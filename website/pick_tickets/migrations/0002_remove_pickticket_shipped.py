# Generated by Django 5.0.6 on 2024-06-17 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pick_tickets", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pickticket",
            name="shipped",
        ),
    ]
