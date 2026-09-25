"""Typed metadata filters shared by every retrieval channel."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from config import normalize_category


@dataclass(slots=True)
class KnowledgeFilter:
    categories: list[str] = field(default_factory=list)
    job_type: str | None = None
    skill: str | None = None
    source: str | None = None
    document_id: int | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_value(cls, value: "KnowledgeFilter | dict[str, Any] | None" = None, *, category: str | None = None) -> "KnowledgeFilter":
        if isinstance(value, cls):
            result = value
        else:
            data = dict(value or {})
            categories = data.pop("categories", data.pop("category", []))
            if isinstance(categories, str):
                categories = [categories]
            result = cls(categories=list(categories or []), **{key: data[key] for key in ("job_type", "skill", "source", "document_id", "tags") if key in data})
        if category:
            result.categories = [category]
        result.categories = [normalize_category(item) for item in result.categories if item]
        if isinstance(result.tags, str):
            result.tags = [result.tags]
        return result


class JobFilter(KnowledgeFilter):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(categories=["jobs", "skills"], **kwargs)


class SkillFilter(KnowledgeFilter):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(categories=["skills"], **kwargs)


class ResumeFilter(KnowledgeFilter):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(categories=["resume", "jobs", "skills"], **kwargs)


class GrowthFilter(KnowledgeFilter):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(categories=["roadmap", "skills", "jobs"], **kwargs)
