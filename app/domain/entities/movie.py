from pydantic import BaseModel


class Movie(BaseModel):
    id: int
    title: str | None = None
    description: str | None = None
    directors: str | None = None
    duration: int | None = None
    genre: str | None = None
    poster: str | None = None
