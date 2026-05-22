from typing import Protocol

from app.domain.entities.movie import Movie


class MovieRepository(Protocol):
    def list_active(self) -> list[Movie]: ...

    def search(
        self,
        title: str | None = None,
        director: str | None = None,
        genre: str | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
    ) -> list[Movie]: ...
