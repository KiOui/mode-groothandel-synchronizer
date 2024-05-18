from django.db import models

from mutations.models import Mutation


class Invoice(models.Model):
    """Invoice model."""

    uphance_id = models.IntegerField(unique=True)
    snelstart_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    invoice_number = models.CharField(max_length=100)
    invoice_total = models.DecimalField(decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Convert this object to String."""
        return f"Invoice {self.invoice_number}"
