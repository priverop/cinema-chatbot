from typing import Protocol

from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.entities.guardrail_result import GuardrailResult, GuardrailStage


def _allow(stage: GuardrailStage) -> GuardrailResult:
    return GuardrailResult(allowed=True, stage=stage)


class Guardrail(Protocol):
    def check_input(self, message: str, history: list[ChatTurn]) -> GuardrailResult: ...
    def check_output(self, message: str, response: ChatResponse) -> GuardrailResult: ...
