from house.models import House
import pytz


def format_utc_datetime(fmt: str, utc_dt) -> str:
    """Convert aware datetime (utc tz) to localtime to be read by humans. Using the Home timezone.


    Parameters
    ----------
    fmt : string describing the expected output format.
    utc_dt : datetime aware (UTC) object.

    Returns
    -------
    str
    """
    tz = House.objects.get_system_house()
    home_timezone = pytz.timezone(tz.timezone)
    loc_dt = utc_dt.astimezone(home_timezone)

    return loc_dt.strftime(fmt)
