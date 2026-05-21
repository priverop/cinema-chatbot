from dataclasses import dataclass

from app.domain.entities.movie import Movie
from app.domain.ports.movie_repository import MovieRepository


@dataclass
class ListMovies:
    repository: MovieRepository

    def __call__(self) -> list[Movie]:
        return self.repository.list_active()
