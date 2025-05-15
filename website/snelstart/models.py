from django.db import models


class CachedBtwTarief(models.Model):

    btw_soort = models.CharField(max_length=100)
    btw_percentage = models.FloatField()
    datum_vanaf = models.DateTimeField()
    datum_tot_en_met = models.DateTimeField()

    def __str__(self):
        return f"{self.btw_soort} - {self.btw_percentage}"

    class Meta:
        unique_together = (("btw_soort", "datum_vanaf"),)


class CachedGrootboek(models.Model):

    modified_on = models.DateTimeField()
    omschrijving = models.CharField(max_length=200)
    kostenplaats_verplicht = models.BooleanField()
    rekening_code = models.CharField(max_length=100)
    nonactief = models.BooleanField()
    nummer = models.IntegerField()
    grootboekfunctie = models.CharField(max_length=100)
    grootboek_rubriek = models.CharField(max_length=100)
    vat_rate_code = models.CharField(max_length=100, blank=True, null=True)
    snelstart_id = models.UUIDField(unique=True)
    uri = models.CharField(max_length=200)


class CachedLand(models.Model):

    naam = models.CharField(max_length=100)
    landcode_iso = models.CharField(max_length=100, null=True, blank=True)
    landcode = models.CharField(max_length=100)
    snelstart_id = models.UUIDField(unique=True)
    uri = models.CharField(max_length=200)

    def __str__(self):
        """Convert this object to string."""
        return self.naam
