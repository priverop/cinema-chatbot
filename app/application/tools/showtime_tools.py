import json
import logging
from datetime import date, datetime
from typing import Any

from opik import track

from app.application.tools.base import Tool
from app.application.use_cases.find_cheapest_session import FindCheapestSession
from app.application.use_cases.list_showtimes import ListShowtimes
from app.domain.entities.showtime import Showtime, ShowtimeLanguage
from app.domain.ports.llm_client import ToolSpec

logger = logging.getLogger(__name__)


_LANGUAGE_MAP = {
    "dubbed": ShowtimeLanguage.DUBBED,
    "doblada": ShowtimeLanguage.DUBBED,
    "vo": ShowtimeLanguage.VO,
    "vose": ShowtimeLanguage.VOSE,
}


def _parse_language(value: str | None) -> ShowtimeLanguage | None:
    if not value:
        return None
    return _LANGUAGE_MAP.get(value.strip().lower())


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _serialize(s: Showtime) -> dict[str, Any]:
    return {
        "id": s.id,
        "movie_id": s.movie_id,
        "movie_title": s.movie_title,
        "theater_id": s.theater_id,
        "theater_name": s.theater_name,
        "showtime": s.showtime.isoformat() if s.showtime else None,
        "language": s.language.name.lower() if s.language is not None else None,
        "theater_price": str(s.theater_price) if s.theater_price is not None else None,
        "theater_discounted_price": (
            str(s.theater_discounted_price)
            if s.theater_discounted_price is not None
            else None
        ),
        "theater_discounted_days": s.theater_discounted_days,
    }


def build_get_showtimes_tool(list_showtimes: ListShowtimes) -> Tool:
    spec = ToolSpec(
        name="get_showtimes",
        description=(
            "Retrieve cinema sessions (showtimes). Filter by movie title, "
            "theater name, city, date (YYYY-MM-DD), datetime range "
            "(from_datetime/to_datetime, ISO 8601), and/or language "
            "('vose' = original with subtitles, 'vo' = original, "
            "'dubbed' = doblada). Each result includes movie title, "
            "theater name, showtime, language, and theater pricing. "
            "Use for any showtime question — what's playing tonight, "
            "tomorrow's sessions, VOSE sessions in Madrid, etc. "
            "Convert relative times ('tonight', 'tomorrow') to ISO "
            "datetimes before calling."
        ),
        parameters={
            "type": "object",
            "properties": {
                "movie_title": {
                    "type": "string",
                    "description": "Movie title substring. Omit if unknown.",
                },
                "theater_name": {
                    "type": "string",
                    "description": "Theater name substring. Omit if unknown.",
                },
                "city": {
                    "type": "string",
                    "description": "City name (e.g. 'Madrid'). Omit if unknown.",
                },
                "date": {
                    "type": "string",
                    "description": "Single day filter, YYYY-MM-DD.",
                },
                "from_datetime": {
                    "type": "string",
                    "description": "Start of window, ISO 8601 (e.g. 2026-05-22T20:00:00).",
                },
                "to_datetime": {
                    "type": "string",
                    "description": "End of window (exclusive), ISO 8601.",
                },
                "language": {
                    "type": "string",
                    "description": "One of 'vose', 'vo', 'dubbed'.",
                },
            },
        },
    )

    @track(name="tool.get_showtimes", project_name="cinema-chatbot")
    def handler(args: dict[str, Any]) -> str:
        movie_title = (args.get("movie_title") or "").strip() or None
        theater_name = (args.get("theater_name") or "").strip() or None
        city = (args.get("city") or "").strip() or None
        on_date = _parse_date(args.get("date"))
        from_dt = _parse_datetime(args.get("from_datetime"))
        to_dt = _parse_datetime(args.get("to_datetime"))
        language = _parse_language(args.get("language"))

        sessions = list_showtimes(
            movie_title=movie_title,
            theater_name=theater_name,
            on_date=on_date,
            from_datetime=from_dt,
            to_datetime=to_dt,
            city=city,
            language=language,
        )
        logger.info(
            "get_showtimes movie=%r theater=%r city=%r date=%r from=%r to=%r lang=%r -> %d",
            movie_title, theater_name, city, on_date, from_dt, to_dt, language, len(sessions),
        )
        return json.dumps({"showtimes": [_serialize(s) for s in sessions]})

    return Tool(spec=spec, handler=handler)


def build_get_cheapest_session_tool(
    find_cheapest_session: FindCheapestSession,
) -> Tool:
    spec = ToolSpec(
        name="get_cheapest_session",
        description=(
            "Find the single cheapest session for a given movie, optionally "
            "filtered by city and datetime range. Computes the effective price "
            "per session using each theater's discount-day rule "
            "(uses discounted_price if the session weekday is in the theater's "
            "discounted_days, else base price). Use when the user asks for "
            "the cheapest session, best price, or where a movie is playing "
            "cheapest in a window of time."
        ),
        parameters={
            "type": "object",
            "properties": {
                "movie_title": {
                    "type": "string",
                    "description": "Movie title substring (required).",
                },
                "city": {
                    "type": "string",
                    "description": "City name (e.g. 'Madrid'). Omit if not specified.",
                },
                "from_datetime": {
                    "type": "string",
                    "description": "Start of window, ISO 8601.",
                },
                "to_datetime": {
                    "type": "string",
                    "description": "End of window (exclusive), ISO 8601.",
                },
            },
            "required": ["movie_title"],
        },
    )

    @track(name="tool.get_cheapest_session", project_name="cinema-chatbot")
    def handler(args: dict[str, Any]) -> str:
        movie_title = (args.get("movie_title") or "").strip()
        city = (args.get("city") or "").strip() or None
        from_dt = _parse_datetime(args.get("from_datetime"))
        to_dt = _parse_datetime(args.get("to_datetime"))

        if not movie_title:
            return json.dumps({"error": "movie_title is required"})

        result = find_cheapest_session(
            movie_title=movie_title,
            city=city,
            from_datetime=from_dt,
            to_datetime=to_dt,
        )
        logger.info(
            "get_cheapest_session movie=%r city=%r from=%r to=%r -> %s",
            movie_title, city, from_dt, to_dt, "hit" if result else "miss",
        )
        if result is None:
            return json.dumps({"cheapest": None})
        return json.dumps({
            "cheapest": {
                "session": _serialize(result.showtime),
                "effective_price": str(result.effective_price),
                "discount_applied": result.discount_applied,
            }
        })

    return Tool(spec=spec, handler=handler)
