from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlmodel import Session, select

from app.domain.entities.showtime import Showtime, ShowtimeLanguage
from app.infrastructure.db.models.movie_row import MovieRow
from app.infrastructure.db.models.showtime_row import ShowtimeRow
from app.infrastructure.db.models.theater_row import TheaterRow
from app.infrastructure.repositories._text import fold


@dataclass
class SQLModelShowtimeRepository:
    session: Session

    def list_filtered(
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
        statement = (
            select(ShowtimeRow, MovieRow, TheaterRow)
            .join(MovieRow, ShowtimeRow.movie_id == MovieRow.id)
            .join(TheaterRow, ShowtimeRow.theater_id == TheaterRow.id)
        )

        if movie_title is not None:
            statement = statement.where(MovieRow.title.ilike(f"%{movie_title}%"))

        if theater_name is not None:
            statement = statement.where(TheaterRow.name.ilike(f"%{theater_name}%"))

        if on_date is not None:
            start = datetime.combine(on_date, datetime.min.time())
            end = start + timedelta(days=1)
            statement = statement.where(
                ShowtimeRow.showtime >= start, ShowtimeRow.showtime < end
            )

        if from_datetime is not None:
            statement = statement.where(ShowtimeRow.showtime >= from_datetime)

        if to_datetime is not None:
            statement = statement.where(ShowtimeRow.showtime < to_datetime)

        if language is not None:
            statement = statement.where(ShowtimeRow.language == int(language))

        if movie_id is not None:
            statement = statement.where(ShowtimeRow.movie_id == movie_id)

        rows = self.session.exec(statement).all()

        if city is not None:
            city_q = fold(city)
            rows = [r for r in rows if city_q in fold(r[2].location)]

        return [self._to_entity(s, m, t) for s, m, t in rows]

    @staticmethod
    def _to_entity(
        showtime_row: ShowtimeRow, movie_row: MovieRow, theater_row: TheaterRow
    ) -> Showtime:
        try:
            lang = ShowtimeLanguage(showtime_row.language)
        except ValueError:
            lang = None
        return Showtime(
            id=showtime_row.id,
            movie_id=showtime_row.movie_id,
            theater_id=showtime_row.theater_id,
            showtime=showtime_row.showtime,
            language=lang,
            movie_title=movie_row.title,
            theater_name=theater_row.name,
            theater_price=theater_row.price,
            theater_discounted_price=theater_row.discounted_price,
            theater_discounted_days=theater_row.discounted_days,
        )
