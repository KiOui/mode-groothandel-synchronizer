# Generated by Django 5.2 on 2025-05-15 11:57
from datetime import datetime

import django.db.models.deletion
import pytz
from django.conf import settings
from django.db import migrations, models

def set_tax_foreign_key(apps, schema_editor):
    TaxMapping = apps.get_model("uphance", "TaxMapping")
    CachedBtwTarief = apps.get_model("snelstart", "CachedBtwTarief")

    timezone = pytz.timezone(settings.TIME_ZONE)
    now = timezone.localize(datetime.now())

    for tax_mapping in TaxMapping.objects.all():
        cached_btw_tarief = CachedBtwTarief.objects.get(
            datum_vanaf__lte=now, datum_tot_en_met__gt=now, btw_naam=tax_mapping.tax_name
        )
        tax_mapping.tax_amount = cached_btw_tarief.id
        tax_mapping.save()


class Migration(migrations.Migration):

    dependencies = [
        ("snelstart", "0004_delete_taxmapping"),
        ("uphance", "0005_alter_taxmapping_tax_name"),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop,
            set_tax_foreign_key,
        ),
        migrations.RemoveField(
            model_name="taxmapping",
            name="tax_name",
        ),
        migrations.AlterField(
            model_name="taxmapping",
            name="tax_amount",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="snelstart.cachedbtwtarief"),
        ),
    ]
