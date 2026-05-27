"""Creates evals/fixtures/test.sqlite3 with stable fixture data.

Run with: python -m evals.fixtures.seed
"""
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.infrastructure.db.models.movie_row import MovieRow
from app.infrastructure.db.models.showtime_row import ShowtimeRow
from app.infrastructure.db.models.theater_row import TheaterRow

FIXTURE_DB = Path(__file__).parent / "test.sqlite3"

# Stable anchor for created_at/updated_at — never changes.
_TS = datetime(2026, 1, 1, 0, 0, 0)

# Showtimes in 2099 so they are always "future" regardless of when evals run.
# The tool-selection eval only checks which tools are called, not what they return.
_BASE = datetime(2099, 6, 1, 10, 0, 0)


def _dt(day_offset: int, hour: int = 10) -> datetime:
    from datetime import timedelta

    return _BASE.replace(day=1) + timedelta(days=day_offset, hours=hour - 10)


def seed() -> None:
    FIXTURE_DB.unlink(missing_ok=True)

    engine = create_engine(
        f"sqlite:///{FIXTURE_DB}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    movies = [
        MovieRow(id=1, created_at=_TS, updated_at=_TS, title="FixtureFilm Alpha", directors="John Fixture", duration=120, genre="Action", is_enabled=True),
        MovieRow(id=2, created_at=_TS, updated_at=_TS, title="FixtureFilm Beta", directors="Jane Fixture", duration=95, genre="Drama", is_enabled=True),
        MovieRow(id=3, created_at=_TS, updated_at=_TS, title="FixtureFilm Gamma", directors="Bob Fixture", duration=100, genre="Comedy", is_enabled=True),
        MovieRow(id=4, created_at=_TS, updated_at=_TS, title="FixtureFilm Delta", directors="Alice Fixture", duration=110, genre="Thriller", is_enabled=True),
        MovieRow(id=5, created_at=_TS, updated_at=_TS, title="FixtureFilm Epsilon", directors="Charlie Fixture", duration=85, genre="Animation", is_enabled=True),
    ]

    theaters = [
        TheaterRow(id=1, created_at=_TS, updated_at=_TS, name="Fixture Cinema Norte", location="Madrid", price=Decimal("10.00"), discounted_price=Decimal("7.00"), discounted_days="Monday,Wednesday", is_enabled=True),
        TheaterRow(id=2, created_at=_TS, updated_at=_TS, name="Fixture Cinema Sur", location="Barcelona", price=Decimal("11.00"), discounted_price=Decimal("8.00"), discounted_days="Tuesday,Thursday", is_enabled=True),
    ]

    # 10 showtimes: mix of movies, theaters, days, languages
    # language: 0=dubbed, 1=vo, 2=vose
    showtimes = [
        ShowtimeRow(id=1,  created_at=_TS, updated_at=_TS, movie_id=1, theater_id=1, showtime=_dt(0, 10), language=0),
        ShowtimeRow(id=2,  created_at=_TS, updated_at=_TS, movie_id=1, theater_id=2, showtime=_dt(0, 17), language=2),
        ShowtimeRow(id=3,  created_at=_TS, updated_at=_TS, movie_id=2, theater_id=1, showtime=_dt(1, 11), language=0),
        ShowtimeRow(id=4,  created_at=_TS, updated_at=_TS, movie_id=2, theater_id=2, showtime=_dt(1, 18), language=1),
        ShowtimeRow(id=5,  created_at=_TS, updated_at=_TS, movie_id=3, theater_id=1, showtime=_dt(2, 16), language=0),
        ShowtimeRow(id=6,  created_at=_TS, updated_at=_TS, movie_id=3, theater_id=2, showtime=_dt(3, 20), language=2),
        ShowtimeRow(id=7,  created_at=_TS, updated_at=_TS, movie_id=4, theater_id=1, showtime=_dt(4, 19), language=0),
        ShowtimeRow(id=8,  created_at=_TS, updated_at=_TS, movie_id=4, theater_id=2, showtime=_dt(5, 15), language=1),
        ShowtimeRow(id=9,  created_at=_TS, updated_at=_TS, movie_id=5, theater_id=1, showtime=_dt(6, 12), language=2),
        ShowtimeRow(id=10, created_at=_TS, updated_at=_TS, movie_id=5, theater_id=2, showtime=_dt(7, 21), language=0),
    ]

    with Session(engine) as session:
        for obj in [*movies, *theaters, *showtimes]:
            session.add(obj)
        session.commit()

    print(f"Seeded {FIXTURE_DB}")
    print(f"  {len(movies)} movies, {len(theaters)} theaters, {len(showtimes)} showtimes")


if __name__ == "__main__":
    seed()
