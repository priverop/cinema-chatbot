from dataclasses import dataclass

from sqlmodel import Session, select

from app.domain.entities.theater import Theater
from app.infrastructure.db.models.theater_row import TheaterRow


@dataclass
class SQLModelTheaterRepository:
    session: Session

    def list_active(self) -> list[Theater]:
        rows = self.session.exec(
            select(TheaterRow).where(TheaterRow.is_enabled == True)  # noqa: E712
        ).all()
        return [self._to_entity(row) for row in rows]

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
