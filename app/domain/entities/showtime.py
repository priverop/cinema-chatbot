from datetime import datetime

from pydantic import BaseModel


class Showtime(BaseModel):
    id: int
    movie_id: int
    theater_id: int
    showtime: datetime | None = None
