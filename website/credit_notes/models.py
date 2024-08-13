from django.db import models


class CreditNote(models.Model):
    """Credit Note model."""

    uphance_id = models.IntegerField(unique=True)
    snelstart_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    credit_note_number = models.CharField(max_length=100, null=True, blank=True)
    credit_note_total = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Convert this object to String."""
        return f"Credit Note {self.credit_note_number}"
