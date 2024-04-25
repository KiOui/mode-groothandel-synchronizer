from django.db import models


class Invoice(models.Model):
    uphance_id = models.IntegerField(unique=True)
    snelstart_id = models.IntegerField(unique=True)
    invoice_number = models.CharField(max_length=100)
    invoice_total = models.DecimalField(decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
