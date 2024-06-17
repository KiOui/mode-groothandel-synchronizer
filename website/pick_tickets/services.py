import logging
import re
from typing import Optional, Tuple, List, Any

from django.conf import settings

from mode_groothandel.clients.api import ApiException
from mode_groothandel.exceptions import SynchronizationError
from mutations.models import Mutation
from pick_tickets.models import PickTicket
from sendcloud.client.sendcloud import Sendcloud
from sendcloud.client.models.shipping_method import ShippingMethod as SendcloudShippingMethod
from uphance.clients.models.pick_ticket import PickTicket as UphancePickTicket


logger = logging.getLogger(__name__)


def get_or_create_pick_ticket_in_database(pick_ticket: UphancePickTicket) -> PickTicket:
    try:
        return PickTicket.objects.get(uphance_id=pick_ticket.id)
    except PickTicket.DoesNotExist:
        return PickTicket.objects.create(
            uphance_id=pick_ticket.id,
            shipment_number=pick_ticket.shipment_number,
            order_id=pick_ticket.order_id,
            sale_id=pick_ticket.sale_id,
        )


def sendcloud_requires_state(iso3166_1_land_code: str) -> bool:
    """Whether a country requires a state to be set in Sendcloud."""
    return iso3166_1_land_code == "US" or iso3166_1_land_code == "IT" or iso3166_1_land_code == "CA"


def convert_dimensions(dimensions_string: str) -> Optional[Tuple[int, int, int]]:
    """Convert a dimensions string into width, length, and height."""
    regex = r"(?P<width>\d*) *x *(?P<length>\d*) *x *(?P<height>\d*)"
    match = re.fullmatch(regex, dimensions_string)
    if match is not None:
        groups = match.groups()
        return int(groups[0]), int(groups[1]), int(groups[2])
    else:
        return None


def convert_weight_to_kg(weight: float, weight_unit: str) -> float:
    if weight_unit == "g":
        return weight / 1000
    elif weight_unit == "oz":
        return weight * 0.02834952
    elif weight_unit == "lb":
        return weight * 0.4535924
    else:
        return weight


def map_parcel_items(pick_ticket: UphancePickTicket) -> List[Any]:
    """Map pick ticket items to sendcloud parcel items."""
    parcel_items = list()
    for line_item in pick_ticket.line_items:
        product_description = line_item.product_name
        product_id = line_item.product_id
        color = line_item.color
        for line_quantity in line_item.line_quantities:
            if line_quantity.quantity > 0:
                sku = line_quantity.sku_id
                size = line_quantity.size
                parcel_items.append(
                    {
                        "description": product_description,
                        "quantity": line_quantity.quantity,
                        "sku": sku,
                        "weight": "0.001",
                        "value": "{:.02f}".format(line_item.unit_price),
                        "product_id": product_id,
                        "properties": {
                            "color": color,
                            "size": size,
                        },
                    }
                )

    return parcel_items


def setup_pick_ticket_for_synchronisation(
    pick_ticket: UphancePickTicket, shipping_method: SendcloudShippingMethod
) -> dict:
    """Setup a pick ticket from Uphance for synchronisation to Sendcloud."""
    address_1 = pick_ticket.address.line_1
    if pick_ticket.address.line_2 != "" and pick_ticket.address.line_3 != "":
        address_2 = f"{pick_ticket.address.line_2} - {pick_ticket.address.line_3}"
    elif pick_ticket.address.line_2 != "":
        address_2 = pick_ticket.address.line_2
    elif pick_ticket.address.line_3 != "":
        address_2 = pick_ticket.address.line_3
    else:
        address_2 = ""

    dimensions = convert_dimensions(pick_ticket.dimensions) if pick_ticket.dimensions is not None else None

    if dimensions is None:
        width, length, height = None, None, None
    else:
        width, length, height = dimensions

    if pick_ticket.gross_weight is not None:
        weight = convert_weight_to_kg(pick_ticket.gross_weight, pick_ticket.gross_weight_unit)
    else:
        weight = 0.001

    # Weight parameter must be greater than 0.001.
    if weight < 0.001:
        weight = 0.001

    return {
        "parcel": {
            "name": pick_ticket.contact_name if pick_ticket.contact_name is not None else pick_ticket.customer_name,
            "company_name": pick_ticket.customer_name,
            "email": pick_ticket.contact_email,
            "telephone": pick_ticket.contact_phone,
            "address": address_1,
            "address_2": address_2,
            "order_number": pick_ticket.order_number,
            "city": pick_ticket.address.city,
            "country": pick_ticket.address.country,
            "postal_code": pick_ticket.address.postcode,
            "country_state": (
                pick_ticket.address.state if sendcloud_requires_state(pick_ticket.address.country) else None
            ),
            "parcel_items": map_parcel_items(pick_ticket),
            "weight": "{:.3f}".format(weight),
            "length": length,
            "width": width,
            "height": height,
            "total_order_value": pick_ticket.grand_total,
            "total_order_value_currency": pick_ticket.currency,
            "customs_shipping_type": 2,  # Commercial goods
            "is_return": False,
            "shipment": {"id": shipping_method.id, "name": shipping_method.name},
            "request_label": False,
        }
    }


def get_shipping_method(sendcloud_client: Sendcloud) -> SendcloudShippingMethod:
    selected_shipping_method_name = settings.SENDCLOUD_SHIPPING_METHOD
    if selected_shipping_method_name is None:
        raise SynchronizationError("No shipping method indicated in Django settings")

    try:
        shipping_methods = sendcloud_client.get_shipping_methods()
    except ApiException as e:
        raise SynchronizationError(f"An error occurred while retrieving the shipping methods from Sendcloud: {e}")

    for shipping_method in shipping_methods:
        if shipping_method.name == selected_shipping_method_name:
            return shipping_method

    raise SynchronizationError(
        f"Shipping method '{selected_shipping_method_name}' could not be found in the shipping methods retrieved from Sendcloud"
    )


def try_delete_pick_ticket(sendcloud_client: Sendcloud, pick_ticket: UphancePickTicket, trigger: int) -> None:
    pick_ticket_in_database = get_or_create_pick_ticket_in_database(pick_ticket)
    if pick_ticket_in_database.sendcloud_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=False,
            message=f"Unable to delete pick ticket {pick_ticket.id} because no Sendcloud ID was found in the database",
        )

    try:
        sendcloud_client.cancel_parcel(pick_ticket_in_database.sendcloud_id)
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=True,
            message=None,
        )
    except ApiException as e:
        Mutation.objects.create(
            method=Mutation.METHOD_DELETE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=False,
            message=f"An API error occurred while deleting pick ticket {pick_ticket.id}: {e}",
        )


def try_update_pick_ticket(sendcloud_client: Sendcloud, pick_ticket: UphancePickTicket, trigger: int) -> None:
    pick_ticket_in_database = get_or_create_pick_ticket_in_database(pick_ticket)

    pick_ticket_in_database.shipment_number = pick_ticket.shipment_number
    pick_ticket_in_database.order_id = pick_ticket.order_id
    pick_ticket_in_database.sale_id = pick_ticket.sale_id
    pick_ticket_in_database.save()

    if pick_ticket_in_database.sendcloud_id is None:
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=False,
            message=f"Unable to update pick ticket {pick_ticket.id} because no Sendcloud ID was found in the database",
        )
        return

    try:
        shipping_method = get_shipping_method(sendcloud_client)
        pick_ticket_converted = setup_pick_ticket_for_synchronisation(pick_ticket, shipping_method)
        try:
            pick_ticket_converted["parcel"]["id"] = pick_ticket_in_database.sendcloud_id
            sendcloud_client.update_parcel(pick_ticket_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while updating a parcel for pick ticket {pick_ticket.id} to Sendcloud: {e}"
            )
        logger.info(f"Successfully updated pick ticket {pick_ticket.id}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred while updating pick ticket {pick_ticket.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_UPDATE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=False,
            message=f"A Synchronization error occurred while updating pick ticket {pick_ticket.id}: {e}",
        )


def try_create_pick_ticket(sendcloud_client: Sendcloud, pick_ticket: UphancePickTicket, trigger: int) -> None:
    pick_ticket_in_database = get_or_create_pick_ticket_in_database(pick_ticket)

    try:
        shipping_method = get_shipping_method(sendcloud_client)
        pick_ticket_converted = setup_pick_ticket_for_synchronisation(pick_ticket, shipping_method)
        try:
            parcel = sendcloud_client.create_parcel(pick_ticket_converted)
        except ApiException as e:
            raise SynchronizationError(
                f"An error occurred while adding a parcel for pick ticket {pick_ticket.id} to Sendcloud: {e}"
            )
        logger.info(f"Successfully synchronized pick ticket {pick_ticket.id}")
        pick_ticket_in_database.sendcloud_id = parcel["parcel"]["id"]
        pick_ticket_in_database.save()
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=True,
            message=None,
        )
    except SynchronizationError as e:
        logger.error(f"A Synchronization error occurred for pick ticket {pick_ticket.id}: {e}")
        Mutation.objects.create(
            method=Mutation.METHOD_CREATE,
            trigger=trigger,
            on=pick_ticket_in_database,
            success=False,
            message=f"A Synchronization error occurred for pick ticket {pick_ticket.id}: {e}",
        )
