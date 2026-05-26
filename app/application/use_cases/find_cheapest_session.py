from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.application._weekdays import weekday_name
from app.domain.entities.showtime import Showtime
from app.domain.ports.showtime_repository import ShowtimeRepository
from app.infrastructure.repositories._text import fold


@dataclass
class CheapestSession:
    showtime: Showtime
    effective_price: Decimal
    discount_applied: bool


@dataclass
class FindCheapestSession:
    repository: ShowtimeRepository

    def __call__(
        self,
        movie_title: str,
        city: str | None = None,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
    ) -> CheapestSession | None:
        sessions = self.repository.list_filtered(
            movie_title=movie_title,
            city=city,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

        best: CheapestSession | None = None
        for s in sessions:
            price, discounted = _effective_price(s)
            if price is None:
                continue
            if best is None or price < best.effective_price:
                best = CheapestSession(
                    showtime=s, effective_price=price, discount_applied=discounted
                )
        return best


def _effective_price(s: Showtime) -> tuple[Decimal | None, bool]:
    base = s.theater_price
    discounted = s.theater_discounted_price
    days = s.theater_discounted_days
    if (
        s.showtime is not None
        and discounted is not None
        and days
        and weekday_name(s.showtime) in fold(days)
    ):
        return discounted, True
    return base, False
