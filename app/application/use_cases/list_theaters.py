from dataclasses import dataclass

from app.domain.entities.theater import Theater
from app.domain.ports.theater_repository import TheaterRepository


@dataclass
class ListTheaters:
    repository: TheaterRepository

    def __call__(self) -> list[Theater]:
        return self.repository.list_active()
