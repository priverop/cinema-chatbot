import logging
from dataclasses import dataclass, field
from datetime import datetime

from app.application.tools.base import Tool
from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.errors import LLMToolLoopExceeded
from app.domain.ports.llm_client import LLMClient, Message

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT_TEMPLATE = (
    "You are a helpful cinema assistant. Today is {today} ({weekday}). "
    "You can answer questions about movies, showtimes, theaters, and the app "
    "itself. Tools available:\n"
    "- get_theaters: cinemas, locations, base/discount prices.\n"
    "- get_movies: titles, directors, genres, durations.\n"
    "- get_showtimes: sessions filtered by movie, theater, city, date, "
    "datetime range, or language ('vose', 'vo', 'dubbed').\n"
    "- get_cheapest_session: single cheapest session for a movie, with "
    "theater discount-day pricing applied.\n\n"
    "Push filters into the tool call instead of asking for the full list and "
    "filtering yourself. Convert relative times ('tonight', 'tomorrow', "
    "'this week') to ISO 8601 datetimes using today's date before calling. "
    "Genres in the catalog are in Spanish — translate user terms before "
    "filtering. For general/FAQ questions about the app, answer directly. "
    "Reply concisely in the same language as the user.\n\n"
    "STRICT DATA POLICY: Only use information returned by the provided tools "
    "or present in this conversation. Do NOT use your own prior knowledge "
    "about movies, directors, theaters, showtimes, or cinema listings. "
    "Never invent movie titles, theater names, showtimes, prices, durations, "
    "or movie-theater relationships. If a tool returns no results or the "
    "needed data is unavailable, say so explicitly."
)


def _build_system_prompt() -> str:
    now = datetime.now()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return SYSTEM_PROMPT_TEMPLATE.format(
        today=now.date().isoformat(),
        weekday=weekdays[now.weekday()],
    )


@dataclass
class Chat:
    llm: LLMClient
    tools: list[Tool] = field(default_factory=list)

    def __call__(self, message: str, history: list[ChatTurn] | None = None) -> ChatResponse:
        tool_index = {t.spec.name: t for t in self.tools}
        tool_specs = [t.spec for t in self.tools]
        prior: list[Message] = [
            Message(role="user" if t.role == "user" else "model", content=t.text)
            for t in (history or [])
        ]
        history_: list[Message] = [*prior, Message(role="user", content=message)]

        for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
            response = self.llm.generate_with_tools(
                messages=history_,
                tools=tool_specs,
                system_prompt=_build_system_prompt(),
            )

            if not response.tool_calls:
                return ChatResponse(reply=response.text)

            history_.append(Message(role="model", content="", tool_calls=list(response.tool_calls)))
            for call in response.tool_calls:
                tool = tool_index.get(call.name)
                if tool is None:
                    result = f'{{"error": "unknown tool {call.name}"}}'
                    logger.warning("LLM requested unknown tool: %s", call.name)
                else:
                    logger.info("tool call iter=%d name=%s args=%s", iteration, call.name, call.args)
                    result = tool.handler(call.args)
                history_.append(Message(role="tool", content=result, tool_name=call.name))

        raise LLMToolLoopExceeded(
            f"tool-call loop exceeded {MAX_TOOL_ITERATIONS} iterations"
        )
