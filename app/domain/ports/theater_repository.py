from typing import Protocol

from app.domain.entities.theater import Theater


class TheaterRepository(Protocol):
    def list_active(self) -> list[Theater]: ...

    def search(
        self, name: str | None = None, city: str | None = None
    ) -> list[Theater]: ...
