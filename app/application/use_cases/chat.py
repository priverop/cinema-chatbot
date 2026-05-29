import logging
from dataclasses import dataclass, field
from datetime import datetime

from opik import track

from app.application.tools.base import Tool
from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.errors import LLMToolLoopExceeded
from app.domain.ports.llm_client import LLMClient, Message

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT_TEMPLATE_V1 = (
    "You are a helpful cinema assistant. Today is {today} ({weekday}). "
    "You can answer questions about movies, showtimes, theaters, and the app "
    "itself. Tools available:\n"
    "- get_theaters: cinemas, locations, base/discount prices.\n"
    "- get_movies: movie catalog — titles, directors, genres, durations. "
    "Use when the user asks about movies or 'qué hay en cartelera'. "
    "Do NOT use to check whether a movie has showtimes. "
    "When presenting movie results always include title, director, and duration.\n"
    "- get_showtimes: sessions filtered by movie, theater, city, date, "
    "datetime range, or language ('vose', 'vo', 'dubbed'). "
    "Call directly even if unsure the movie exists — returns empty if not found.\n"
    "- get_cheapest_session: single cheapest session for a movie, with "
    "theater discount-day pricing applied. "
    "movie_title is required; if unspecified, ask the user.\n"
    "- search_knowledge: search Cinemapi's internal documentation (FAQ, legal "
    "disclaimer, policies). Call this when the user asks about how Cinemapi "
    "works, data accuracy, ticket purchasing, error reporting, pricing "
    "disclaimers, legal responsibility, or any question about the service "
    "itself rather than specific movies or showtimes.\n\n"
    "Never call get_movies to verify a movie exists before calling "
    "get_showtimes or get_cheapest_session — call the target tool directly. "
    "Push filters into the tool call instead of asking for the full list and "
    "filtering yourself. Convert relative times ('tonight', 'tomorrow', "
    "'this week') to ISO 8601 datetimes using today's date before calling. "
    "Genres in the catalog are in Spanish — translate user terms before "
    "filtering. Reply concisely in the same language as the user.\n\n"
    "STRICT DATA POLICY: Only use information returned by the provided tools "
    "or present in this conversation. Do NOT use your own prior knowledge "
    "about movies, directors, theaters, showtimes, or cinema listings. "
    "Never invent movie titles, theater names, showtimes, prices, durations, "
    "or movie-theater relationships. If a tool returns no results or the "
    "needed data is unavailable, say so explicitly. After giving information "
    "of prices or showtimes, add a note at the end stating that they can be "
    "wrong and always double-check with the theater website."
)

SYSTEM_PROMPT_TEMPLATE_V2 = (
    "You are a cinema assistant. Today is {today} ({weekday}). "
    "Answer questions about movies, showtimes, theaters, and the app. "
    "Use the provided tools when needed. Reply in the user's language."
)

_PROMPT_TEMPLATES = {
    "v1": SYSTEM_PROMPT_TEMPLATE_V1,
    "v2": SYSTEM_PROMPT_TEMPLATE_V2,
}


def _build_system_prompt(variant: str = "v1") -> str:
    template = _PROMPT_TEMPLATES.get(variant)
    if template is None:
        raise ValueError(f"Unknown prompt variant: {variant!r}. Valid: {list(_PROMPT_TEMPLATES)}")
    now = datetime.now()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return template.format(
        today=now.date().isoformat(),
        weekday=weekdays[now.weekday()],
    )


@dataclass
class Chat:
    llm: LLMClient
    tools: list[Tool] = field(default_factory=list)
    prompt_variant: str = "v1"

    @track(name="chat.execute", project_name="cinema-chatbot")
    def __call__(self, message: str, history: list[ChatTurn] | None = None) -> ChatResponse:
        tool_index = {t.spec.name: t for t in self.tools}
        tool_specs = [t.spec for t in self.tools]
        prior: list[Message] = [
            Message(role="user" if t.role == "user" else "model", content=t.text)
            for t in (history or [])
        ]
        history_: list[Message] = [*prior, Message(role="user", content=message)]
        tools_called: list[str] = []
        tool_outputs: list[str] = []

        for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
            response = self.llm.generate_with_tools(
                messages=history_,
                tools=tool_specs,
                system_prompt=_build_system_prompt(self.prompt_variant),
            )

            if not response.tool_calls:
                return ChatResponse(
                    reply=response.text,
                    tools_called=tuple(tools_called),
                    tool_outputs=tuple(tool_outputs),
                )

            history_.append(Message(role="model", content="", tool_calls=list(response.tool_calls)))
            for call in response.tool_calls:
                tools_called.append(call.name)
                tool = tool_index.get(call.name)
                if tool is None:
                    result = f'{{"error": "unknown tool {call.name}"}}'
                    logger.warning("LLM requested unknown tool: %s", call.name)
                else:
                    logger.info("tool call iter=%d name=%s args=%s", iteration, call.name, call.args)
                    result = tool.handler(call.args)
                tool_outputs.append(result)
                history_.append(Message(role="tool", content=result, tool_name=call.name))

        raise LLMToolLoopExceeded(
            f"tool-call loop exceeded {MAX_TOOL_ITERATIONS} iterations"
        )
