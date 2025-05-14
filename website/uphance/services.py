from uphance.clients.uphance import Uphance
from uphance.models import CachedChannel


def refresh_cached_channels() -> (int, int, int):
    uphance = Uphance.get_client()

    channels = uphance.channels()

    channels_created, channels_updated = list(), list()

    for channel in channels:
        try:
            cached_channel = CachedChannel.objects.get(channel_id=channel.channel_id)
            cached_channel.name = channel.channel_name
            cached_channel.currency = channel.currency
            cached_channel.save()
            channels_updated.append(cached_channel)
        except CachedChannel.DoesNotExist:
            created_channel = CachedChannel.objects.create(
                channel_id=channel.channel_id,
                name=channel.channel_name,
                currency=channel.currency,
            )
            channels_created.append(created_channel)

    # Remove all non-updated channels
    created_channel_ids = [x.id for x in channels_created]
    updated_channel_ids = [x.id for x in channels_updated]

    all_ids = created_channel_ids + updated_channel_ids

    channels_untouched = CachedChannel.objects.exclude(id__in=all_ids)
    (channels_deleted_count, _) = channels_untouched.delete()

    return len(channels_created), len(channels_updated), channels_deleted_count
