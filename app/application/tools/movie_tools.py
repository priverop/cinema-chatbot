import json
import logging
from typing import Any

from opik import track

from app.application.tools.base import Tool
from app.application.use_cases.search_movies import SearchMovies
from app.domain.ports.llm_client import ToolSpec

logger = logging.getLogger(__name__)


def build_get_movies_tool(search_movies: SearchMovies) -> Tool:
    spec = ToolSpec(
        name="get_movies",
        description=(
            "Retrieve movies. Optionally filter by title, director, genre, "
            "and/or duration range (in minutes). All filters are substring, "
            "case-insensitive matches except duration. "
            "Genre values are in Spanish (e.g. 'Terror', 'Comedia', 'Drama', "
            "'Acción', 'Animación', 'Documental', 'Ciencia Ficción'). "
            "Translate user genre terms to Spanish before calling. "
            "Use when the user asks about movies, titles, directors, genres, "
            "or wants movies of a certain length. "
            "Do NOT use to check whether a movie has showtimes — use get_showtimes for that."
        ),
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title substring (e.g. 'Dune'). Omit if unknown.",
                },
                "director": {
                    "type": "string",
                    "description": "Director name substring (e.g. 'Nolan'). Omit if unknown.",
                },
                "genre": {
                    "type": "string",
                    "description": "Genre in Spanish (e.g. 'Terror', 'Comedia'). Omit if unknown.",
                },
                "min_duration": {
                    "type": "integer",
                    "description": "Minimum duration in minutes. Omit if no lower bound.",
                },
                "max_duration": {
                    "type": "integer",
                    "description": "Maximum duration in minutes. Omit if no upper bound.",
                },
            },
        },
    )

    @track(name="tool.get_movies", project_name="cinema-chatbot")
    def handler(args: dict[str, Any]) -> str:
        title = (args.get("title") or "").strip() or None
        director = (args.get("director") or "").strip() or None
        genre = (args.get("genre") or "").strip() or None
        min_duration = args.get("min_duration")
        max_duration = args.get("max_duration")
        movies = search_movies(
            title=title,
            director=director,
            genre=genre,
            min_duration=min_duration,
            max_duration=max_duration,
        )
        logger.info(
            "get_movies called title=%r director=%r genre=%r min=%r max=%r -> %d results",
            title, director, genre, min_duration, max_duration, len(movies),
        )
        payload = [
            {
                "id": m.id,
                "title": m.title,
                "directors": m.directors,
                "duration": m.duration,
                "genre": m.genre,
                "description": m.description,
                "poster": m.poster,
            }
            for m in movies
        ]
        return json.dumps({"movies": payload})

    return Tool(spec=spec, handler=handler)
