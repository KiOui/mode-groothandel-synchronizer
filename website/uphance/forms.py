from datetime import datetime

import pytz
from django import forms
from django.conf import settings

from snelstart.models import CachedBtwTarief, CachedGrootboek
from uphance.models import TaxMapping


class TaxMappingAdminForm(forms.ModelForm):
    """Tax Mapping Admin Form."""

    tax_amount = forms.ChoiceField(required=True)
    grootboekcode = forms.ChoiceField(required=True)
    grootboekcode_shipping = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        """Initialize Tax Mapping Admin Form."""
        super(TaxMappingAdminForm, self).__init__(*args, **kwargs)
        if CachedBtwTarief.objects.all().count() == 0:
            self.fields["tax_amount"] = forms.IntegerField(
                min_value=1,
                help_text="There are no tax types from Snelstart registered. Please press the"
                " 'Refresh Tax Types' button at the bottom of the screen.",
            )
        else:
            timezone = pytz.timezone(settings.TIME_ZONE)
            now = timezone.localize(datetime.now())
            choices = [
                (x.btw_percentage, f"{x.btw_soort} ({x.btw_percentage})")
                for x in CachedBtwTarief.objects.filter(datum_vanaf__lte=now, datum_tot_en_met__gt=now)
            ]
            self.fields["tax_amount"].choices = choices
            self.fields["tax_amount"].help_text = (
                "The tax types displayed here are cached. If you want to refresh these tax types, "
                "please press the 'Refresh Tax Types' button at the "
                "bottom of the screen."
            )

        if CachedGrootboek.objects.all().count() == 0:
            self.fields["grootboekcode"] = forms.IntegerField(
                min_value=1,
                help_text="There are no grootboeken from Snelstart registered. Please press the"
                " 'Refresh Grootboekcodes' button at the bottom of the screen.",
            )
            self.fields["grootboekcode_shipping"] = forms.IntegerField(
                min_value=1,
                help_text="There are no grootboeken from Snelstart registered. Please press the"
                " 'Refresh Grootboekcodes' button at the bottom of the screen.",
            )
        else:
            grootboeken = list(CachedGrootboek.objects.all())
            grootboeken.sort(key=lambda x: x.nummer)
            choices = [(x.snelstart_id, f"{x.nummer} - {x.omschrijving}") for x in grootboeken]
            self.fields["grootboekcode"].choices = choices
            self.fields["grootboekcode"].help_text = (
                "The grootboekcodes displayed here are cached. If you want to refresh these grootboekcodes, "
                "please press the 'Refresh Grootboekcodes' button at the "
                "bottom of the screen."
            )
            self.fields["grootboekcode_shipping"].choices = choices
            self.fields["grootboekcode_shipping"].help_text = (
                "The grootboekcodes displayed here are cached. If you want to refresh these grootboekcodes, "
                "please press the 'Refresh Grootboekcodes' button at the "
                "bottom of the screen."
            )

    class Meta:
        """Meta class."""

        model = TaxMapping
        fields = (
            "tax_amount",
            "grootboekcode",
            "grootboekcode_shipping",
        )
