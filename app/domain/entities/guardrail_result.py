from dataclasses import dataclass
from typing import Literal

GuardrailStage = Literal["input", "output"]


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    stage: GuardrailStage
    category: str = ""
    reason: str = ""
