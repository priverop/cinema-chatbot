from dataclasses import dataclass

from app.domain.entities.chat_message import ChatResponse
from app.domain.ports.llm_client import LLMClient


@dataclass
class Chat:
    llm: LLMClient

    def __call__(self, message: str) -> ChatResponse:
        return ChatResponse(reply=self.llm.generate(message))
