from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlmodel import Session, select

from app.domain.entities.showtime import Showtime
from app.infrastructure.db.models.movie_row import MovieRow
from app.infrastructure.db.models.showtime_row import ShowtimeRow
from app.infrastructure.db.models.theater_row import TheaterRow


@dataclass
class SQLModelShowtimeRepository:
    session: Session

    def list_filtered(
        self,
        movie_title: str | None = None,
        theater_name: str | None = None,
        on_date: date | None = None,
    ) -> list[Showtime]:
        statement = select(ShowtimeRow)

        if movie_title is not None:
            statement = statement.join(
                MovieRow, ShowtimeRow.movie_id == MovieRow.id
            ).where(MovieRow.title.ilike(f"%{movie_title}%"))

        if theater_name is not None:
            statement = statement.join(
                TheaterRow, ShowtimeRow.theater_id == TheaterRow.id
            ).where(TheaterRow.name.ilike(f"%{theater_name}%"))

        if on_date is not None:
            start = datetime.combine(on_date, datetime.min.time())
            end = start + timedelta(days=1)
            statement = statement.where(
                ShowtimeRow.showtime >= start, ShowtimeRow.showtime < end
            )

        rows = self.session.exec(statement).all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: ShowtimeRow) -> Showtime:
        return Showtime(
            id=row.id,
            movie_id=row.movie_id,
            theater_id=row.theater_id,
            showtime=row.showtime,
        )
