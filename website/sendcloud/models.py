from django.db import models


class CachedCountry(models.Model):
    """Available countries in Sendcloud."""

    sendcloud_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    iso_2 = models.CharField(max_length=2)
    iso_3 = models.CharField(max_length=3)

    def __str__(self):
        """Convert this object to string."""
        return self.name


class CachedShippingMethod(models.Model):
    """Available shipping methods in Sendcloud."""

    sendcloud_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    carrier = models.CharField(max_length=255)
    min_weight = models.DecimalField(max_digits=10, decimal_places=3)
    max_weight = models.DecimalField(max_digits=10, decimal_places=3)
    service_point_input = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    countries = models.ManyToManyField(to=CachedCountry)

    def __str__(self):
        """Convert this object to string."""
        return self.name
