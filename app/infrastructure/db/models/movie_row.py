from datetime import datetime

from sqlmodel import Field, SQLModel


class MovieRow(SQLModel, table=True):
    __tablename__ = "movies"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    data_source: int = 0
    title: str | None = None
    description: str | None = None
    directors: str | None = None
    duration: int | None = None
    genre: str | None = None
    poster: str | None = None
    is_enabled: bool = True
