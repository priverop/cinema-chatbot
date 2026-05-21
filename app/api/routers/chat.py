from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_chat_use_case
from app.application.use_cases.chat import Chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatReply(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatReply)
def post_chat(
    request: ChatRequest,
    use_case: Chat = Depends(get_chat_use_case),
) -> ChatReply:
    result = use_case(request.message)
    return ChatReply(reply=result.reply)
