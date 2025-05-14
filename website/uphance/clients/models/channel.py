from dataclasses import dataclass

from mode_groothandel.clients.utils import get_value_or_error


@dataclass
class Channel:

    channel_id: int
    channel_name: str
    currency: str

    @staticmethod
    def from_data(data: dict) -> "Channel":
        return Channel(
            channel_id=get_value_or_error(data, "channel_ID"),
            channel_name=get_value_or_error(data, "channel_name"),
            currency=get_value_or_error(data, "currency"),
        )
