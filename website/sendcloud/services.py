from sendcloud.client.sendcloud import Sendcloud
from sendcloud.models import CachedShippingMethod, CachedCountry


def refresh_shipping_methods() -> (int, int, int):
    sendcloud = Sendcloud.get_client()

    shipping_methods = sendcloud.get_shipping_methods()

    shipping_methods_created, shipping_methods_updated = list(), list()
    countries_created, countries_updated = list(), list()

    for shipping_method in shipping_methods:
        countries_needed = list()

        for country in shipping_method.countries:
            try:
                cached_country = CachedCountry.objects.get(sendcloud_id=country.id)
                cached_country.name = country.name
                cached_country.price = country.price
                cached_country.iso_2 = country.iso_2
                cached_country.iso_3 = country.iso_3
                cached_country.save()
                countries_needed.append(cached_country)

                if cached_country not in countries_created:
                    countries_updated.append(cached_country)

            except CachedCountry.DoesNotExist:
                cached_country = CachedCountry.objects.create(
                    sendcloud_id=country.id,
                    price=country.price,
                    name=country.name,
                    iso_2=country.iso_2,
                    iso_3=country.iso_3,
                )
                countries_needed.append(cached_country)
                countries_created.append(cached_country)

        try:
            cached_shipping_method = CachedShippingMethod.objects.get(sendcloud_id=shipping_method.id)
            cached_shipping_method.name = shipping_method.name
            cached_shipping_method.carrier = shipping_method.carrier
            cached_shipping_method.min_weight = shipping_method.min_weight
            cached_shipping_method.max_weight = shipping_method.max_weight
            cached_shipping_method.service_point_input = shipping_method.service_point_input
            cached_shipping_method.price = shipping_method.price
            cached_shipping_method.countries.clear()

            for country in countries_needed:
                cached_shipping_method.countries.add(country)

            cached_shipping_method.save()
            shipping_methods_updated.append(cached_shipping_method)
        except CachedShippingMethod.DoesNotExist:
            cached_shipping_method = CachedShippingMethod.objects.create(
                sendcloud_id=shipping_method.id,
                name=shipping_method.name,
                carrier=shipping_method.carrier,
                min_weight=shipping_method.min_weight,
                max_weight=shipping_method.max_weight,
                service_point_input=shipping_method.service_point_input,
                price=shipping_method.price,
            )
            for country in countries_needed:
                cached_shipping_method.countries.add(country)

            cached_shipping_method.save()
            shipping_methods_created.append(cached_shipping_method)

    created_countries_ids = [x.id for x in countries_created]
    updated_countries_ids = [x.id for x in countries_updated]

    all_ids = created_countries_ids + updated_countries_ids
    countries_untouched = CachedCountry.objects.exclude(id__in=all_ids)
    countries_untouched.delete()

    created_shipping_method_ids = [x.id for x in shipping_methods_created]
    updated_shipping_method_ids = [x.id for x in shipping_methods_updated]

    all_ids = created_shipping_method_ids + updated_shipping_method_ids
    shipping_methods_untouched = CachedShippingMethod.objects.exclude(id__in=all_ids)
    (shipping_methods_deleted_count, _) = shipping_methods_untouched.delete()

    return len(shipping_methods_created), len(shipping_methods_updated), shipping_methods_deleted_count
