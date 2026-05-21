from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_list_showtimes_use_case
from app.application.use_cases.list_showtimes import ListShowtimes
from app.domain.entities.showtime import Showtime

router = APIRouter()


@router.get("/showtimes", response_model=list[Showtime])
def get_showtimes(
    movie_title: str | None = Query(default=None),
    theater_name: str | None = Query(default=None),
    on_date: date | None = Query(default=None, alias="date"),
    use_case: ListShowtimes = Depends(get_list_showtimes_use_case),
) -> list[Showtime]:
    return use_case(
        movie_title=movie_title,
        theater_name=theater_name,
        on_date=on_date,
    )
