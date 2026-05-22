from dataclasses import dataclass

from sqlmodel import Session, select

from app.domain.entities.movie import Movie
from app.infrastructure.db.models.movie_row import MovieRow
from app.infrastructure.repositories._text import fold


@dataclass
class SQLModelMovieRepository:
    session: Session

    def list_active(self) -> list[Movie]:
        rows = self.session.exec(
            select(MovieRow).where(MovieRow.is_enabled == True)  # noqa: E712
        ).all()
        return [self._to_entity(row) for row in rows]

    def search(
        self,
        title: str | None = None,
        director: str | None = None,
        genre: str | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
    ) -> list[Movie]:
        stmt = select(MovieRow).where(MovieRow.is_enabled == True)  # noqa: E712
        if min_duration is not None:
            stmt = stmt.where(MovieRow.duration >= min_duration)
        if max_duration is not None:
            stmt = stmt.where(MovieRow.duration <= max_duration)
        rows = self.session.exec(stmt).all()

        title_q = fold(title)
        director_q = fold(director)
        genre_q = fold(genre)
        filtered = [
            row for row in rows
            if (not title_q or title_q in fold(row.title))
            and (not director_q or director_q in fold(row.directors))
            and (not genre_q or genre_q in fold(row.genre))
        ]
        return [self._to_entity(row) for row in filtered]

    @staticmethod
    def _to_entity(row: MovieRow) -> Movie:
        return Movie(
            id=row.id,
            title=row.title,
            description=row.description,
            directors=row.directors,
            duration=row.duration,
            genre=row.genre,
            poster=row.poster,
        )
