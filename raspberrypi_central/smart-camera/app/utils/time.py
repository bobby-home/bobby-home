import datetime
from typing import Optional


def is_time_lapsed(last_time: Optional[datetime.datetime], seconds: float, first_true: bool = False) -> bool:
    if first_true is True and last_time is None:
        return True

    return (last_time is not None) and (
        datetime.datetime.now() - last_time).seconds >= seconds
