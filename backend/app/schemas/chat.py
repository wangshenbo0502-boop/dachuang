"""对话式就业助手的数据结构。"""

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatTurnRequest(BaseModel):
    user_id: int = Field(ge=1)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=80)
    target_job: str = Field(default="", max_length=100)


class ChatConversationRequest(BaseModel):
    user_id: int = Field(ge=1)
    messages: list[ChatMessage] = Field(default_factory=list, max_length=60)
    target_job: str = Field(default="", max_length=100)


class ChatConversationResponse(BaseModel):
    reply: str


class ChatTurnResponse(BaseModel):
    reply: str
    # 保留该字段兼容旧客户端；新版界面不展示轮次，也不限制访谈轮数。
    question_number: int = Field(ge=0)
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
