from dataclasses import dataclass

from app.domain.entities.movie import Movie
from app.domain.ports.movie_repository import MovieRepository


@dataclass
class SearchMovies:
    repository: MovieRepository

    def __call__(
        self,
        title: str | None = None,
        director: str | None = None,
        genre: str | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
    ) -> list[Movie]:
        return self.repository.search(
            title=title,
            director=director,
            genre=genre,
            min_duration=min_duration,
            max_duration=max_duration,
        )
