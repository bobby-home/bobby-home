import datetime
from typing import Optional


def is_time_lapsed(last_time: Optional[datetime.datetime], seconds: float) -> bool:
    return (last_time is not None) and (
        datetime.datetime.now() - last_time).seconds >= seconds
