from dataclasses import dataclass

from sqlmodel import Session, select

from app.domain.entities.theater import Theater
from app.infrastructure.db.models.theater_row import TheaterRow
from app.infrastructure.repositories._text import fold


@dataclass
class SQLModelTheaterRepository:
    session: Session

    def list_active(self) -> list[Theater]:
        rows = self.session.exec(
            select(TheaterRow).where(TheaterRow.is_enabled == True)  # noqa: E712
        ).all()
        return [self._to_entity(row) for row in rows]

    def search(
        self, name: str | None = None, city: str | None = None
    ) -> list[Theater]:
        stmt = select(TheaterRow).where(TheaterRow.is_enabled == True)  # noqa: E712
        rows = self.session.exec(stmt).all()
        name_q = fold(name)
        city_q = fold(city)
        filtered = [
            row for row in rows
            if (not name_q or name_q in fold(row.name))
            and (not city_q or city_q in fold(row.location))
        ]
        return [self._to_entity(row) for row in filtered]

    @staticmethod
    def _to_entity(row: TheaterRow) -> Theater:
        return Theater(
            id=row.id,
            name=row.name,
            location=row.location,
            price=row.price,
            discounted_price=row.discounted_price,
            discounted_days=row.discounted_days,
            website=row.website,
        )
