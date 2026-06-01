import logging
from dataclasses import dataclass

from opik import track

from app.application.use_cases.chat import Chat
from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.ports.guardrail import Guardrail

logger = logging.getLogger(__name__)

_REFUSAL = (
    "I can only help with cinema questions (movies, showtimes, prices, policies)."
)


@dataclass
class GuardedChat:
    """Wraps Chat with input and output guardrail checks.

    Same __call__ signature as Chat — router requires no changes.
    On block: returns a canned refusal reply, tools_called/tool_outputs preserved
    from the inner response (empty on input block, populated on output block).
    """

    inner: Chat
    guardrail: Guardrail
    refusal_text: str = _REFUSAL

    @track(name="guarded_chat.execute", project_name="cinema-chatbot")
    def __call__(self, message: str, history: list[ChatTurn] | None = None) -> ChatResponse:
        history = history or []

        pre = self.guardrail.check_input(message, history)
        if not pre.allowed:
            logger.info("guardrail blocked input stage=%s category=%s reason=%r", pre.stage, pre.category, pre.reason)
            return ChatResponse(reply=self.refusal_text)

        response = self.inner(message, history)

        post = self.guardrail.check_output(message, response)
        if not post.allowed:
            logger.info("guardrail blocked output stage=%s category=%s reason=%r", post.stage, post.category, post.reason)
            return ChatResponse(
                reply=self.refusal_text,
                tools_called=response.tools_called,
                tool_outputs=response.tool_outputs,
            )

        return response
