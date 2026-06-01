from fastapi import Depends
from sqlmodel import Session

from app.application.guardrails.composite import CompositeGuardrail
from app.application.tools.knowledge_tools import build_search_knowledge_tool
from app.application.tools.movie_tools import build_get_movies_tool
from app.application.tools.showtime_tools import (
    build_get_cheapest_session_tool,
    build_get_showtimes_tool,
)
from app.application.tools.theater_tools import build_get_theaters_tool
from app.application.use_cases.chat import Chat
from app.application.use_cases.find_cheapest_session import FindCheapestSession
from app.application.use_cases.guarded_chat import GuardedChat
from app.application.use_cases.list_movies import ListMovies
from app.application.use_cases.list_showtimes import ListShowtimes
from app.application.use_cases.list_theaters import ListTheaters
from app.application.use_cases.search_knowledge import SearchKnowledge
from app.application.use_cases.search_movies import SearchMovies
from app.application.use_cases.search_theaters import SearchTheaters
from app.domain.ports.embedding_client import EmbeddingClient
from app.domain.ports.knowledge_repository import KnowledgeRepository
from app.domain.ports.llm_client import LLMClient
from app.domain.ports.movie_repository import MovieRepository
from app.domain.ports.showtime_repository import ShowtimeRepository
from app.domain.ports.theater_repository import TheaterRepository
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.db.engine import get_session
from app.infrastructure.guardrails.regex_prompt_injection import RegexPromptInjection
from app.infrastructure.guardrails.title_leak import TitleLeakGuardrail
from app.infrastructure.llm.gemini_client import GeminiClient
from app.infrastructure.llm.gemini_embedding_client import GeminiEmbeddingClient
from app.infrastructure.rag.chroma_knowledge_repository import ChromaKnowledgeRepository
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


def get_search_theaters_use_case(
    repository: TheaterRepository = Depends(get_theater_repository),
) -> SearchTheaters:
    return SearchTheaters(repository=repository)


def get_movie_repository(
    session: Session = Depends(get_session),
) -> MovieRepository:
    return SQLModelMovieRepository(session=session)


def get_list_movies_use_case(
    repository: MovieRepository = Depends(get_movie_repository),
) -> ListMovies:
    return ListMovies(repository=repository)


def get_search_movies_use_case(
    repository: MovieRepository = Depends(get_movie_repository),
) -> SearchMovies:
    return SearchMovies(repository=repository)


def get_showtime_repository(
    session: Session = Depends(get_session),
) -> ShowtimeRepository:
    return SQLModelShowtimeRepository(session=session)


def get_list_showtimes_use_case(
    repository: ShowtimeRepository = Depends(get_showtime_repository),
) -> ListShowtimes:
    return ListShowtimes(repository=repository)


def get_find_cheapest_session_use_case(
    repository: ShowtimeRepository = Depends(get_showtime_repository),
) -> FindCheapestSession:
    return FindCheapestSession(repository=repository)


def get_llm_client(
    settings: Settings = Depends(get_settings),
) -> LLMClient:
    return GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)


def get_embedding_client(
    settings: Settings = Depends(get_settings),
) -> EmbeddingClient:
    return GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )


def get_knowledge_repository(
    settings: Settings = Depends(get_settings),
) -> KnowledgeRepository:
    return ChromaKnowledgeRepository(path=settings.chroma_path)


def get_search_knowledge_use_case(
    embedder: EmbeddingClient = Depends(get_embedding_client),
    repository: KnowledgeRepository = Depends(get_knowledge_repository),
) -> SearchKnowledge:
    return SearchKnowledge(embedder=embedder, repository=repository)


def build_chat(
    llm: LLMClient,
    search_theaters: SearchTheaters,
    search_movies: SearchMovies,
    list_showtimes: ListShowtimes,
    find_cheapest_session: FindCheapestSession,
    search_knowledge: SearchKnowledge,
    movie_repository: MovieRepository,
    prompt_variant: str = "v1",
) -> GuardedChat:
    tools = [
        build_get_theaters_tool(search_theaters),
        build_get_movies_tool(search_movies),
        build_get_showtimes_tool(list_showtimes),
        build_get_cheapest_session_tool(find_cheapest_session),
        build_search_knowledge_tool(search_knowledge),
    ]
    inner = Chat(llm=llm, tools=tools, prompt_variant=prompt_variant)
    guardrail = CompositeGuardrail(guardrails=[
        RegexPromptInjection(),
        TitleLeakGuardrail(movie_repository=movie_repository),
    ])
    return GuardedChat(inner=inner, guardrail=guardrail)


def get_chat_use_case(
    llm: LLMClient = Depends(get_llm_client),
    search_theaters: SearchTheaters = Depends(get_search_theaters_use_case),
    search_movies: SearchMovies = Depends(get_search_movies_use_case),
    list_showtimes: ListShowtimes = Depends(get_list_showtimes_use_case),
    find_cheapest_session: FindCheapestSession = Depends(
        get_find_cheapest_session_use_case
    ),
    search_knowledge: SearchKnowledge = Depends(get_search_knowledge_use_case),
    movie_repository: MovieRepository = Depends(get_movie_repository),
) -> GuardedChat:
    return build_chat(
        llm=llm,
        search_theaters=search_theaters,
        search_movies=search_movies,
        list_showtimes=list_showtimes,
        find_cheapest_session=find_cheapest_session,
        search_knowledge=search_knowledge,
        movie_repository=movie_repository,
    )
