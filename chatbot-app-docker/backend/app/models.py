from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None


class Message(BaseModel):
    id: str
    conversation_id: str
    role: str
    message_text: str
    created_at: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str


class ConversationDetail(BaseModel):
    conversation_id: str
    title: Optional[str]
    messages: List[Message]
