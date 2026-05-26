from datetime import datetime

_WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def weekday_name(dt: datetime) -> str:
    return _WEEKDAYS[dt.weekday()]
