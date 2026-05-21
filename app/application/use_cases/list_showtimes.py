from dataclasses import dataclass
from datetime import date

from app.domain.entities.showtime import Showtime
from app.domain.ports.showtime_repository import ShowtimeRepository


@dataclass
class ListShowtimes:
    repository: ShowtimeRepository

    def __call__(
        self,
        movie_title: str | None = None,
        theater_name: str | None = None,
        on_date: date | None = None,
    ) -> list[Showtime]:
        return self.repository.list_filtered(
            movie_title=movie_title,
            theater_name=theater_name,
            on_date=on_date,
        )
