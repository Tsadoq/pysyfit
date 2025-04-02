# FIT epoch offset (seconds between Unix epoch and FIT epoch)
from datetime import datetime, UTC

FIT_EPOCH_OFFSET = 631065600  # Seconds from UTC 00:00 Dec 31 1989 to Unix Epoch


def datetime_to_fit_timestamp(dt: datetime) -> int:
    """
    Convert a Python datetime to a FIT timestamp.
    :param dt: The Python datetime to convert
    :return: The equivalent FIT timestamp
    """
    timestamp = int((dt - datetime(1970, 1, 1)).total_seconds())
    return timestamp - FIT_EPOCH_OFFSET


def fit_timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert a FIT timestamp to a Python datetime.
    :param timestamp: The FIT timestamp to convert
    :return: The equivalent Python datetime
    """
    if isinstance(timestamp, datetime):
        return timestamp

    # Otherwise convert from integer timestamp
    return datetime.fromtimestamp(timestamp + FIT_EPOCH_OFFSET, UTC)
