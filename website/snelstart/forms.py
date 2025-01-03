from datetime import datetime

import pytz
from django import forms
from django.conf import settings

from snelstart.models import CachedGrootboek, CachedBtwTarief, TaxMapping


class TaxMappingAdminForm(forms.ModelForm):
    """Tax Mapping Admin Form."""

    name = forms.ChoiceField(required=True)
    grootboekcode = forms.ChoiceField(required=True)
    grootboekcode_shipping = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        """Initialize Tax Mapping Admin Form."""
        super(TaxMappingAdminForm, self).__init__(*args, **kwargs)
        if CachedBtwTarief.objects.all().count() == 0:
            self.fields["name"] = forms.IntegerField(
                min_value=1,
                help_text="There are no tax types from Snelstart registered. Please press the"
                " 'Refresh Tax Types' button at the bottom of the screen.",
            )
        else:
            timezone = pytz.timezone(settings.TIME_ZONE)
            now = timezone.localize(datetime.now())
            choices = [
                (x.btw_soort, f"{x.btw_soort} ({x.btw_percentage})")
                for x in CachedBtwTarief.objects.filter(datum_vanaf__lte=now, datum_tot_en_met__gt=now)
            ]
            self.fields["name"].choices = choices
            self.fields["name"].help_text = (
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
            choices = [(x.snelstart_id, f"{x.omschrijving} ({x.nummer})") for x in grootboeken]
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

    def save(self, commit=True) -> TaxMapping:
        """Save a TaxMapping object."""
        obj = super(TaxMappingAdminForm, self).save(commit=False)
        timezone = pytz.timezone(settings.TIME_ZONE)
        now = timezone.localize(datetime.now())
        btw_tarief = CachedBtwTarief.objects.filter(
            datum_vanaf__lte=now, datum_tot_en_met__gt=now, btw_soort=obj.name
        ).first()
        obj.tax_amount = btw_tarief.btw_percentage
        if commit:
            obj.save()

        return obj

    class Meta:
        """Meta class."""

        model = TaxMapping
        fields = (
            "name",
            "grootboekcode",
            "grootboekcode_shipping",
        )
