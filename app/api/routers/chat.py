from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_chat_use_case
from app.application.use_cases.guarded_chat import GuardedChat
from app.domain.entities.chat_message import ChatTurn

router = APIRouter()


class ChatTurnSchema(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatTurnSchema] = []


class ChatReply(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatReply)
def post_chat(
    request: ChatRequest,
    use_case: GuardedChat = Depends(get_chat_use_case),
) -> ChatReply:
    turns = [ChatTurn(role=t.role, text=t.text) for t in request.history]
    result = use_case(request.message, history=turns)
    return ChatReply(reply=result.reply)
