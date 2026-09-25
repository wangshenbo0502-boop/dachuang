from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    category: str | None = Field(default=None, max_length=100)
    filters: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=1000)
    category: str = Field(default="general", min_length=1, max_length=100)
    content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
