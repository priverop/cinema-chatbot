from typing import Protocol

from app.domain.entities.theater import Theater


class TheaterRepository(Protocol):
    def list_active(self) -> list[Theater]: ...
