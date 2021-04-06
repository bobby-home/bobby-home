import datetime
import datetime as dt
import pytz
from django.utils import timezone

UTC = pytz.utc


def utcnow() -> dt.datetime:
    """Get now in UTC time."""
    return dt.datetime.utcnow().replace(tzinfo=UTC)


def is_time_newer_than(ttime: datetime.datetime, past_seconds: int) -> bool:
    """

    Parameters
    ----------
    ttime : datetime.datetime
    past_seconds : int

    Returns
    -------
    bool
        True if ttime is newer than now - past_seconds.
        False otherwise.
    """
    min_date = timezone.now() - datetime.timedelta(seconds=past_seconds)

    return min_date < ttime
