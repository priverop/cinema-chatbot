from dataclasses import dataclass
from datetime import date, datetime

from app.domain.entities.showtime import Showtime, ShowtimeLanguage
from app.domain.ports.showtime_repository import ShowtimeRepository


@dataclass
class ListShowtimes:
    repository: ShowtimeRepository

    def __call__(
        self,
        movie_title: str | None = None,
        theater_name: str | None = None,
        on_date: date | None = None,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
        city: str | None = None,
        language: ShowtimeLanguage | None = None,
        movie_id: int | None = None,
    ) -> list[Showtime]:
        return self.repository.list_filtered(
            movie_title=movie_title,
            theater_name=theater_name,
            on_date=on_date,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            city=city,
            language=language,
            movie_id=movie_id,
        )
