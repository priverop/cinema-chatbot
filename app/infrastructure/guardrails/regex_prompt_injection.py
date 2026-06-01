import re

from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.entities.guardrail_result import GuardrailResult
from app.domain.ports.guardrail import _allow

_PATTERNS = re.compile(
    r"ignore\s+(all\s+)?previous\s+instructions"
    r"|disregard.{0,20}instructions"
    r"|you\s+are\s+now\b"
    r"|system\s+prompt"
    r"|roleplay\s+as\b"
    r"|pretend\s+to\s+be\b",
    re.IGNORECASE,
)


class RegexPromptInjection:
    """Blocks common prompt-injection and jailbreak phrases on input."""

    def check_input(self, message: str, history: list[ChatTurn]) -> GuardrailResult:
        m = _PATTERNS.search(message)
        if m:
            return GuardrailResult(
                allowed=False,
                stage="input",
                category="prompt_injection",
                reason=f"matched pattern: {m.group(0)!r}",
            )
        return _allow("input")

    def check_output(self, message: str, response: ChatResponse) -> GuardrailResult:
        return _allow("output")
