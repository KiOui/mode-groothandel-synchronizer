from django.db import models


class Customer(models.Model):
    """Customer class."""

    uphance_id = models.IntegerField(unique=True)
    snelstart_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    uphance_name = models.CharField(max_length=255)
    snelstart_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        """Convert this object to string."""
        return f"Customer {self.uphance_name} ({self.uphance_id})"
