from decimal import Decimal

from pydantic import BaseModel


class Theater(BaseModel):
    id: int
    name: str | None = None
    location: str | None = None
    price: Decimal | None = None
    discounted_price: Decimal | None = None
    discounted_days: str | None = None
    website: str | None = None
