from datetime import date, datetime
from typing import Protocol

from app.domain.entities.showtime import Showtime, ShowtimeLanguage


class ShowtimeRepository(Protocol):
    def list_filtered(
        self,
        movie_title: str | None = None,
        theater_name: str | None = None,
        on_date: date | None = None,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
        city: str | None = None,
        language: ShowtimeLanguage | None = None,
        movie_id: int | None = None,
    ) -> list[Showtime]: ...
