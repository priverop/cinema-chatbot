from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.dependencies import get_find_cheapest_session_use_case
from app.application.use_cases.find_cheapest_session import FindCheapestSession
from app.domain.entities.showtime import Showtime

router = APIRouter()


class CheapestSessionResponse(BaseModel):
    session: Showtime
    effective_price: str
    discount_applied: bool


@router.get("/sessions/cheapest", response_model=CheapestSessionResponse)
def get_cheapest_session(
    movie_title: str = Query(...),
    city: str | None = Query(default=None),
    from_datetime: datetime | None = Query(default=None),
    to_datetime: datetime | None = Query(default=None),
    use_case: FindCheapestSession = Depends(get_find_cheapest_session_use_case),
) -> CheapestSessionResponse:
    result = use_case(
        movie_title=movie_title,
        city=city,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No sessions match the filters.")
    return CheapestSessionResponse(
        session=result.showtime,
        effective_price=str(result.effective_price),
        discount_applied=result.discount_applied,
    )
