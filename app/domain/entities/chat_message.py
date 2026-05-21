from dataclasses import dataclass


@dataclass(frozen=True)
class ChatResponse:
    reply: str
