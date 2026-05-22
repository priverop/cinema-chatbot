import logging
from dataclasses import dataclass, field

from app.application.tools.base import Tool
from app.domain.entities.chat_message import ChatResponse
from app.domain.errors import LLMToolLoopExceeded
from app.domain.ports.llm_client import LLMClient, Message

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = (
    "You are a helpful cinema assistant. You can answer questions about movies, "
    "showtimes, theaters, and the app itself. When the user asks about cinemas, "
    "theaters, or where movies play, use the get_theaters tool. When the user "
    "asks about movies (by title, director, genre, or duration), use the "
    "get_movies tool. Pass specific filters (name, title, genre, etc.) instead "
    "of fetching the full list whenever possible. Genres in the catalog are in "
    "Spanish — translate user terms before filtering. For general or FAQ "
    "questions about the app, answer directly without calling tools. "
    "Reply concisely in the same language as the user.\n\n"
    "STRICT DATA POLICY: Only use information returned by the provided tools "
    "or present in this conversation. Do NOT use your own prior knowledge "
    "about movies, directors, theaters, showtimes, or cinema listings. "
    "Never invent movie titles, theater names, showtimes, prices, durations, "
    "or movie-theater relationships. If a tool returns no results or the "
    "needed data is unavailable, say so explicitly — do not fill gaps with "
    "guesses or external knowledge. If the user asks for something the tools "
    "cannot answer (e.g. showtimes, movie-theater mapping), state that the "
    "app does not have that information."
)


@dataclass
class Chat:
    llm: LLMClient
    tools: list[Tool] = field(default_factory=list)

    def __call__(self, message: str) -> ChatResponse:
        tool_index = {t.spec.name: t for t in self.tools}
        tool_specs = [t.spec for t in self.tools]
        history: list[Message] = [Message(role="user", content=message)]

        for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
            response = self.llm.generate_with_tools(
                messages=history,
                tools=tool_specs,
                system_prompt=SYSTEM_PROMPT,
            )

            if not response.tool_calls:
                return ChatResponse(reply=response.text)

            history.append(Message(role="model", content="", tool_calls=list(response.tool_calls)))
            for call in response.tool_calls:
                tool = tool_index.get(call.name)
                if tool is None:
                    result = f'{{"error": "unknown tool {call.name}"}}'
                    logger.warning("LLM requested unknown tool: %s", call.name)
                else:
                    logger.info("tool call iter=%d name=%s args=%s", iteration, call.name, call.args)
                    result = tool.handler(call.args)
                history.append(Message(role="tool", content=result, tool_name=call.name))

        raise LLMToolLoopExceeded(
            f"tool-call loop exceeded {MAX_TOOL_ITERATIONS} iterations"
        )
