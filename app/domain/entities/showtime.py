from datetime import datetime
from decimal import Decimal
from enum import IntEnum

from pydantic import BaseModel


class ShowtimeLanguage(IntEnum):
    DUBBED = 0
    VO = 1
    VOSE = 2


class Showtime(BaseModel):
    id: int
    movie_id: int
    theater_id: int
    showtime: datetime | None = None
    language: ShowtimeLanguage | None = None
    movie_title: str | None = None
    theater_name: str | None = None
    theater_price: Decimal | None = None
    theater_discounted_price: Decimal | None = None
    theater_discounted_days: str | None = None
