from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ChatTurn:
    role: Literal["user", "assistant"]
    text: str


@dataclass(frozen=True)
class ChatResponse:
    reply: str
    tools_called: tuple[str, ...] = ()
    tool_outputs: tuple[str, ...] = () # We shouldn't be storing this here (domain), but for the simplicity of the learning project...
