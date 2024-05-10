import pytz
from django.conf import settings

from snelstart.clients.snelstart import Snelstart
from snelstart.models import CachedGrootboek, CachedBtwTarief, CachedLand


def refresh_cached_grootboeken() -> (int, int, int):
    timezone = pytz.timezone(settings.TIME_ZONE)

    snelstart = Snelstart.get_client()

    grootboeken = snelstart.get_grootboeken()

    grootboeken_created, grootboeken_updated = list(), list()

    for grootboek in grootboeken:
        try:
            cached_grootboek = CachedGrootboek.objects.get(snelstart_id=grootboek.id)
            cached_grootboek.modified_on = timezone.localize(grootboek.modified_on)
            cached_grootboek.omschrijving = grootboek.omschrijving
            cached_grootboek.kostenplaats_verplicht = grootboek.kostenplaats_verplicht
            cached_grootboek.rekening_code = grootboek.rekening_code
            cached_grootboek.nonactief = grootboek.nonactief
            cached_grootboek.nummer = grootboek.nummer
            cached_grootboek.grootboekfunctie = grootboek.grootboekfunctie
            cached_grootboek.vat_rate_code = grootboek.vat_rate_code
            cached_grootboek.uri = grootboek.uri
            cached_grootboek.save()
            grootboeken_updated.append(cached_grootboek)
        except CachedGrootboek.DoesNotExist:
            created_grootboek = CachedGrootboek.objects.create(
                modified_on=timezone.localize(grootboek.modified_on),
                omschrijving=grootboek.omschrijving,
                kostenplaats_verplicht=grootboek.kostenplaats_verplicht,
                rekening_code=grootboek.rekening_code,
                nonactief=grootboek.nonactief,
                nummer=grootboek.nummer,
                grootboekfunctie=grootboek.grootboekfunctie,
                grootboek_rubriek=grootboek.grootboek_rubriek,
                vat_rate_code=grootboek.vat_rate_code,
                snelstart_id=grootboek.id,
                uri=grootboek.uri,
            )
            grootboeken_created.append(created_grootboek)

    # Remove all non-updated grootboeken
    created_grootboeken_ids = [x.id for x in grootboeken_created]
    updated_grootboeken_ids = [x.id for x in grootboeken_updated]

    all_ids = created_grootboeken_ids + updated_grootboeken_ids

    grootboeken_untouched = CachedGrootboek.objects.exclude(id__in=all_ids)
    (grootboeken_deleted_count, _) = grootboeken_untouched.delete()

    return len(grootboeken_created), len(grootboeken_updated), grootboeken_deleted_count


def refresh_cached_tax_types() -> (int, int, int):
    timezone = pytz.timezone(settings.TIME_ZONE)

    snelstart = Snelstart.get_client()

    tax_types = snelstart.get_btwtarieven()

    tax_types_created, tax_types_updated = list(), list()

    for tax_type in tax_types:
        try:
            cached_tax_type = CachedBtwTarief.objects.get(btw_soort=tax_type.btw_soort, datum_vanaf=timezone.localize(tax_type.datum_vanaf))
            cached_tax_type.btw_percentage = tax_type.btw_percentage
            cached_tax_type.datum_tot_en_met = timezone.localize(tax_type.datum_tot_en_met)
            cached_tax_type.save()
            tax_types_updated.append(cached_tax_type)
        except CachedBtwTarief.DoesNotExist:
            created_tax_type = CachedBtwTarief.objects.create(
                btw_soort=tax_type.btw_soort,
                btw_percentage=tax_type.btw_percentage,
                datum_vanaf=timezone.localize(tax_type.datum_vanaf),
                datum_tot_en_met=timezone.localize(tax_type.datum_tot_en_met),
            )
            tax_types_created.append(created_tax_type)

    # Remove all non-updated tax types
    created_tax_type_ids = [x.id for x in tax_types_created]
    updated_tax_type_ids = [x.id for x in tax_types_updated]

    all_ids = created_tax_type_ids + updated_tax_type_ids

    tax_types_untouched = CachedBtwTarief.objects.exclude(id__in=all_ids)
    (grootboeken_deleted_count, _) = tax_types_untouched.delete()

    return len(tax_types_created), len(tax_types_updated), grootboeken_deleted_count


def refresh_landen() -> (int, int, int):
    snelstart = Snelstart.get_client()

    landen = snelstart.get_landen()

    landen_created, landen_updated = list(), list()

    for land in landen:
        try:
            cached_land = CachedLand.objects.get(snelstart_id=land.id)
            cached_land.naam = land.naam
            cached_land.landcode_iso = land.landcode_iso
            cached_land.landcode = land.landcode
            cached_land.uri = land.uri
            cached_land.save()
            landen_updated.append(cached_land)
        except CachedLand.DoesNotExist:
            created_land = CachedLand.objects.create(
                naam=land.naam,
                landcode_iso=land.landcode_iso,
                landcode=land.landcode,
                snelstart_id=land.id,
                uri=land.uri,
            )
            landen_created.append(created_land)

    # Remove all non-updated tax types
    created_landen_ids = [x.id for x in landen_created]
    updated_landen_ids = [x.id for x in landen_updated]

    all_ids = created_landen_ids + updated_landen_ids

    landen_untouched = CachedLand.objects.exclude(id__in=all_ids)
    (landen_deleted_count, _) = landen_untouched.delete()

    return len(landen_created), len(landen_updated), landen_deleted_count