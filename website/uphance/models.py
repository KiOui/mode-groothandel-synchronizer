from django.db import models

from sendcloud.models import CachedShippingMethod
from snelstart.models import CachedLand


class Country(models.Model):
    """Available countries in Uphance."""

    country_code = models.CharField(max_length=10, unique=True, help_text="Country code as known in Uphance.")
    mapped_shipping_method_for_pick_tickets = models.ForeignKey(
        to=CachedShippingMethod,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Shipping method for pick tickets going to this country. If this is unset, the pick tickets will use the default shipping method.",
    )
    mapped_country_code_in_snelstart = models.ForeignKey(
        to=CachedLand,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Sometimes, a country code in Snelstart is not the same as a country code in Uphance. This field can be set if that is the case and the synchronisation tool can not map it automatically.",
    )
