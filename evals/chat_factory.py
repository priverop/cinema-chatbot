"""Builds a Chat instance with real dependencies, without FastAPI DI."""
from pathlib import Path

from sqlmodel import Session, create_engine

from app.api.dependencies import build_chat
from app.application.use_cases.find_cheapest_session import FindCheapestSession
from app.application.use_cases.list_showtimes import ListShowtimes
from app.application.use_cases.search_knowledge import SearchKnowledge
from app.application.use_cases.search_movies import SearchMovies
from app.application.use_cases.search_theaters import SearchTheaters
from app.application.use_cases.chat import Chat
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.gemini_client import GeminiClient
from app.infrastructure.llm.gemini_embedding_client import GeminiEmbeddingClient
from app.infrastructure.rag.chroma_knowledge_repository import ChromaKnowledgeRepository
from app.infrastructure.repositories.sqlmodel_movie_repository import SQLModelMovieRepository
from app.infrastructure.repositories.sqlmodel_showtime_repository import SQLModelShowtimeRepository
from app.infrastructure.repositories.sqlmodel_theater_repository import SQLModelTheaterRepository

_DEFAULT_FIXTURE_DB = Path(__file__).parent / "fixtures" / "test.sqlite3"


def build_chat_for_evals(db_path: Path | None = None, prompt_variant: str = "v1") -> Chat:
    settings = get_settings()
    resolved = db_path or _DEFAULT_FIXTURE_DB
    fixture_engine = create_engine(
        f"sqlite:///{resolved}",
        connect_args={"check_same_thread": False},
    )
    session = Session(fixture_engine)

    llm = GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)
    embedder = GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    knowledge_repo = ChromaKnowledgeRepository(path=settings.chroma_path)

    return build_chat(
        llm=llm,
        search_theaters=SearchTheaters(repository=SQLModelTheaterRepository(session=session)),
        search_movies=SearchMovies(repository=SQLModelMovieRepository(session=session)),
        list_showtimes=ListShowtimes(repository=SQLModelShowtimeRepository(session=session)),
        find_cheapest_session=FindCheapestSession(repository=SQLModelShowtimeRepository(session=session)),
        search_knowledge=SearchKnowledge(embedder=embedder, repository=knowledge_repo),
        prompt_variant=prompt_variant,
    )
