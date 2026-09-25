"""Safe RAG integration for existing AI business services."""
from __future__ import annotations

import logging
from typing import Any

from app.knowledge.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


def augment_prompt(query: str, prompt: str, *, category: str | None = None, top_k: int = 5) -> tuple[str, list[dict[str, Any]]]:
    try:
        payload = KnowledgeService.instance().retrieve_context(query, category=category, top_k=top_k)
    except Exception:
        logger.exception("rag_context_unavailable category=%s", category)
        return prompt, []
    context = payload.get("context", "")
    sources = payload.get("sources", [])
    if not context:
        return prompt, sources
    return (
        f"{prompt}\n\n### 知识库参考上下文\n"
        "以下内容仅作为分析依据。请优先结合用户真实信息，不得编造经历、项目或技能。\n\n"
        f"{context}",
        sources,
    )
