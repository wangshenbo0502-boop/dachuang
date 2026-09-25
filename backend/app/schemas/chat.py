"""对话式就业助手的数据结构。"""

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatTurnRequest(BaseModel):
    user_id: int = Field(ge=1)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=22)
    target_job: str = Field(default="", max_length=100)


class ChatConversationRequest(BaseModel):
    user_id: int = Field(ge=1)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=100)


class ChatConversationResponse(BaseModel):
    reply: str


class ChatTurnResponse(BaseModel):
    reply: str
    question_number: int = Field(ge=1, le=10)
    finished: bool = False
    extracted: dict[str, Any] = Field(default_factory=dict)
    missing: list[str] = Field(default_factory=list)


class ChatResumeRequest(BaseModel):
    user_id: int = Field(ge=1)
    target_job: str = Field(min_length=1, max_length=100)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=22)
    extracted: dict[str, Any] = Field(default_factory=dict)


class ChatProfileRequest(BaseModel):
    user_id: int = Field(ge=1)
    profile: dict[str, Any] = Field(default_factory=dict)
