from dataclasses import dataclass

from app.domain.entities.theater import Theater
from app.domain.ports.theater_repository import TheaterRepository


@dataclass
class SearchTheaters:
    repository: TheaterRepository

    def __call__(
        self, name: str | None = None, city: str | None = None
    ) -> list[Theater]:
        return self.repository.search(name=name, city=city)
