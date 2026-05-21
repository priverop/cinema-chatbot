from datetime import date
from typing import Protocol

from app.domain.entities.showtime import Showtime


class ShowtimeRepository(Protocol):
    def list_filtered(
        self,
        movie_title: str | None = None,
        theater_name: str | None = None,
        on_date: date | None = None,
    ) -> list[Showtime]: ...
