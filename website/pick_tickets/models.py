from django.db import models

from mutations.models import Mutation


class PickTicket(models.Model):
    """Pick Ticket model."""

    uphance_id = models.IntegerField(unique=True)
    sendcloud_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    shipment_number = models.IntegerField()
    order_id = models.IntegerField()
    sale_id = models.IntegerField()
    shipped = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Convert this object to String."""
        return f"Pick Ticket {self.uphance_id}"