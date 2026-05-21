from datetime import datetime

from sqlmodel import Field, SQLModel


class ShowtimeRow(SQLModel, table=True):
    __tablename__ = "showtimes"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    movie_id: int = Field(foreign_key="movies.id")
    theater_id: int = Field(foreign_key="theaters.id")
    showtime: datetime | None = None
    language: int = 0
