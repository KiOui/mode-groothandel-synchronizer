from datetime import datetime

from uphance.clients.models.invoice import Invoice as UphanceInvoice
from uphance.clients.uphance import Uphance


def setup_invoice_for_synchronisation(uphance_client: Uphance, invoice: UphanceInvoice) -> dict:
    customer = uphance_client.customer_by_id(invoice.company_id)

    # TODO: Set invoice date to correct date
    invoice_date = datetime.now()

    return {
        "factuurnummer": invoice.invoice_number,
        "Klant": {"id": None},
        "boekingsregels": None,
        "factuurbedrag": None,
        "betalingstermijn": None,
        "factuurdatum": invoice_date.strftime("%Y-%m-%d %H:%I:%S"),
        "btw": None,
    }
