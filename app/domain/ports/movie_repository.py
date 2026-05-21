from typing import Protocol

from app.domain.entities.movie import Movie


class MovieRepository(Protocol):
    def list_active(self) -> list[Movie]: ...
