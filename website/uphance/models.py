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
        help_text="Shipping method for pick tickets going to this country. If this is unset, the pick tickets will use"
        " the default shipping method.",
    )
    mapped_country_code_in_snelstart = models.ForeignKey(
        to=CachedLand,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Sometimes, a country code in Snelstart is not the same as a country code in Uphance. This field can"
        " be set if that is the case and the synchronisation tool can not map it automatically.",
    )


class CachedChannel(models.Model):
    """Cached available channels in Uphance."""

    channel_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.channel_id}:- {self.name}"


class ChannelMapping(models.Model):

    channel = models.OneToOneField(to=CachedChannel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.channel.name} ({self.channel.channel_id})"


class TaxMapping(models.Model):

    channel_mapping = models.ForeignKey(to=ChannelMapping, on_delete=models.CASCADE)
    tax_amount = models.FloatField()
    grootboekcode = models.UUIDField()
    grootboekcode_shipping = models.UUIDField()

    def __str__(self):
        return f"{self.channel_mapping.channel.name} ({self.tax_amount})"

    class Meta:
        unique_together = ("channel_mapping", "tax_amount")
