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
    "theaters, or where movies play, use the get_theaters tool. For general or "
    "FAQ questions about the app, answer directly without calling tools. "
    "Reply concisely in the same language as the user."
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
