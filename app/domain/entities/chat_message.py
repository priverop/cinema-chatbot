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
