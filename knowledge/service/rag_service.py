"""Retrieval-augmented generation service with traceable sources."""
from __future__ import annotations

import logging
from typing import Any, Callable

from service.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, knowledge: KnowledgeService | None = None) -> None:
        self.knowledge = knowledge or KnowledgeService()

    def augment_prompt(self, query: str, prompt: str, *, category: str | None = None, top_k: int | None = None) -> tuple[str, list[dict]]:
        try:
            payload = self.knowledge.retrieve_context(query, top_k=top_k, category=category)
        except Exception:
            logger.exception("rag_retrieval_failed category=%s; continuing without knowledge context", category)
            return prompt, []
        context = payload["context"]
        if not context:
            return prompt, []
        augmented = f"{prompt}\n\n### 检索到的知识库上下文\n请将以下内容作为参考依据，不要照抄，也不要编造上下文中不存在的事实。\n\n{context}"
        return augmented, payload["sources"]

    def answer(
        self,
        query: str,
        llm: Callable[[list[dict[str, str]]], str],
        *,
        system_prompt: str = "请基于提供的知识库上下文准确回答问题。",
        category: str | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        base_prompt = f"用户问题：{query}"
        prompt, sources = self.augment_prompt(query, base_prompt, category=category, top_k=top_k)
        answer = llm([{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}])
        return {"answer": answer, "sources": sources}
