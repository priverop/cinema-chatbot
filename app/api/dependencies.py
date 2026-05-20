from fastapi import Depends
from sqlmodel import Session

from app.application.use_cases.list_theaters import ListTheaters
from app.domain.ports.theater_repository import TheaterRepository
from app.infrastructure.db.engine import get_session
from app.infrastructure.repositories.sqlmodel_theater_repository import (
    SQLModelTheaterRepository,
)


def get_theater_repository(
    session: Session = Depends(get_session),
) -> TheaterRepository:
    return SQLModelTheaterRepository(session=session)


def get_list_theaters_use_case(
    repository: TheaterRepository = Depends(get_theater_repository),
) -> ListTheaters:
    return ListTheaters(repository=repository)
