# Generated by Django 5.0.4 on 2024-05-11 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="snelstart_id",
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
