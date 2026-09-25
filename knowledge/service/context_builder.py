from __future__ import annotations
from config import KnowledgeSettings, get_knowledge_settings


class ContextBuilder:
    def __init__(self, settings: KnowledgeSettings | None = None) -> None:
        self.settings = settings or get_knowledge_settings()

    def build(self, chunks: list[dict]) -> str:
        sections: list[str] = []
        used = 0
        for index, chunk in enumerate(chunks, 1):
            separator = "\n\n" if sections else ""
            remaining = self.settings.context_max_chars - used - len(separator)
            if remaining <= 0:
                break
            section = (
                f"[知识{index}]\n"
                f"标题：{chunk.get('title', '')}\n"
                f"分类：{chunk.get('category', 'general')}\n"
                f"来源：{chunk.get('source', '')}\n"
                f"内容：\n{chunk.get('content', '').strip()}"
            )
            if len(section) > remaining:
                section = section[:remaining].rstrip()
            if not section:
                break
            sections.append(section)
            used += len(separator) + len(section)
        return "\n\n".join(sections)
