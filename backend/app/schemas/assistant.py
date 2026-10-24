"""Payloads for persisting AI career assistant conversations."""
import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

SESSION_ID_PATTERN = r"^[A-Za-z0-9-]{1,64}$"
MAX_DRAFT_BYTES = 100_000
MAX_SESSION_BYTES = 2_000_000


class StoredMessage(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    role: Literal["user", "assistant"]
    content: str = Field(max_length=20000)
    createdAt: str = Field(default="", max_length=40)
    failed: bool = False


class AssistantSessionPayload(BaseModel):
    title: str = Field(default="新对话", max_length=60)
    mode: Literal["consult", "profile"] = "consult"
    target: str = Field(default="", max_length=100)
    consultMessages: list[StoredMessage] = Field(default_factory=list, max_length=1000)
    profileMessages: list[StoredMessage] = Field(default_factory=list, max_length=1000)
    draft: dict[str, Any] = Field(default_factory=dict)
    suggestedAction: Optional[Literal["profile", "resume", "analysis", "growth", "jobs"]] = None

    @field_validator("title")
    @classmethod
    def _title(cls, value: str) -> str:
        return value.strip() or "新对话"

    @field_validator("draft")
    @classmethod
    def _draft_size(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > MAX_DRAFT_BYTES:
            raise ValueError("档案草稿过大")
        return value

    @model_validator(mode="after")
    def _total_size(self) -> "AssistantSessionPayload":
        if len(self.model_dump_json().encode("utf-8")) > MAX_SESSION_BYTES:
            raise ValueError("对话内容过长，请新建一个对话继续")
        return self
