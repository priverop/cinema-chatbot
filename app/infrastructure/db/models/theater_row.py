from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class TheaterRow(SQLModel, table=True):
    __tablename__ = "theaters"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    name: str | None = None
    location: str | None = None
    price: Decimal | None = None
    discounted_price: Decimal | None = None
    discounted_days: str | None = None
    is_enabled: bool = True
    website: str | None = None
    scraper_external_id: str | None = None
    scraper_key: int | None = None
