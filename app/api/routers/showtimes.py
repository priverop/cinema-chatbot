from datetime import date, datetime

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_list_showtimes_use_case
from app.application.use_cases.list_showtimes import ListShowtimes
from app.domain.entities.showtime import Showtime, ShowtimeLanguage

router = APIRouter()


_LANGUAGE_MAP = {
    "dubbed": ShowtimeLanguage.DUBBED,
    "doblada": ShowtimeLanguage.DUBBED,
    "vo": ShowtimeLanguage.VO,
    "vose": ShowtimeLanguage.VOSE,
}


@router.get("/showtimes", response_model=list[Showtime])
def get_showtimes(
    movie_title: str | None = Query(default=None),
    theater_name: str | None = Query(default=None),
    on_date: date | None = Query(default=None, alias="date"),
    from_datetime: datetime | None = Query(default=None),
    to_datetime: datetime | None = Query(default=None),
    city: str | None = Query(default=None),
    language: str | None = Query(default=None),
    movie_id: int | None = Query(default=None),
    use_case: ListShowtimes = Depends(get_list_showtimes_use_case),
) -> list[Showtime]:
    lang_enum = _LANGUAGE_MAP.get(language.lower()) if language else None
    return use_case(
        movie_title=movie_title,
        theater_name=theater_name,
        on_date=on_date,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        city=city,
        language=lang_enum,
        movie_id=movie_id,
    )
