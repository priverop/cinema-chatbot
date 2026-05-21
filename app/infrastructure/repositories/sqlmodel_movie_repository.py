from dataclasses import dataclass

from sqlmodel import Session, select

from app.domain.entities.movie import Movie
from app.infrastructure.db.models.movie_row import MovieRow


@dataclass
class SQLModelMovieRepository:
    session: Session

    def list_active(self) -> list[Movie]:
        rows = self.session.exec(
            select(MovieRow).where(MovieRow.is_enabled == True)  # noqa: E712
        ).all()
        return [self._to_entity(row) for row in rows]

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
