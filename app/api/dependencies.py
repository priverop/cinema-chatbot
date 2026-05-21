from fastapi import Depends
from sqlmodel import Session

from app.application.use_cases.chat import Chat
from app.application.use_cases.list_movies import ListMovies
from app.application.use_cases.list_showtimes import ListShowtimes
from app.application.use_cases.list_theaters import ListTheaters
from app.domain.ports.llm_client import LLMClient
from app.domain.ports.movie_repository import MovieRepository
from app.domain.ports.showtime_repository import ShowtimeRepository
from app.domain.ports.theater_repository import TheaterRepository
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.db.engine import get_session
from app.infrastructure.llm.gemini_client import GeminiClient
from app.infrastructure.repositories.sqlmodel_movie_repository import (
    SQLModelMovieRepository,
)
from app.infrastructure.repositories.sqlmodel_showtime_repository import (
    SQLModelShowtimeRepository,
)
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


def get_movie_repository(
    session: Session = Depends(get_session),
) -> MovieRepository:
    return SQLModelMovieRepository(session=session)


def get_list_movies_use_case(
    repository: MovieRepository = Depends(get_movie_repository),
) -> ListMovies:
    return ListMovies(repository=repository)


def get_showtime_repository(
    session: Session = Depends(get_session),
) -> ShowtimeRepository:
    return SQLModelShowtimeRepository(session=session)


def get_list_showtimes_use_case(
    repository: ShowtimeRepository = Depends(get_showtime_repository),
) -> ListShowtimes:
    return ListShowtimes(repository=repository)


def get_llm_client(
    settings: Settings = Depends(get_settings),
) -> LLMClient:
    return GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)


def get_chat_use_case(
    llm: LLMClient = Depends(get_llm_client),
) -> Chat:
    return Chat(llm=llm)
