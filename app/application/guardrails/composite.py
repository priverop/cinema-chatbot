from dataclasses import dataclass, field

from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.entities.guardrail_result import GuardrailResult
from app.domain.ports.guardrail import Guardrail, _allow


@dataclass
class CompositeGuardrail:
    """First-fail composite: iterates guardrails in order, returns first blocked result."""

    guardrails: list[Guardrail] = field(default_factory=list)

    def check_input(self, message: str, history: list[ChatTurn]) -> GuardrailResult:
        for g in self.guardrails:
            result = g.check_input(message, history)
            if not result.allowed:
                return result
        return _allow("input")

    def check_output(self, message: str, response: ChatResponse) -> GuardrailResult:
        for g in self.guardrails:
            result = g.check_output(message, response)
            if not result.allowed:
                return result
        return _allow("output")
