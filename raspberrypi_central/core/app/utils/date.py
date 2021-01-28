import datetime as dt
import pytz


UTC = pytz.utc


def utcnow() -> dt.datetime:
    """Get now in UTC time."""
    return dt.datetime.utcnow().replace(tzinfo=UTC)
