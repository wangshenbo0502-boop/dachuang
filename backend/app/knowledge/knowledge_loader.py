"""Compatibility adapter over the canonical knowledge loaders and parser."""
from __future__ import annotations

import sys
from pathlib import Path

_knowledge_root = Path(__file__).resolve().parents[3] / "knowledge"
if str(_knowledge_root) not in sys.path:
    sys.path.insert(0, str(_knowledge_root))

from loaders.markdown_loader import MarkdownLoader


class KnowledgeLoader:
    """知识库数据加载器：加载并解析 knowledge/documents/ 下的 Markdown 文档。

    所有 backend 模块（岗位匹配、就业画像等）通过本类访问知识文档，
    内部复用 knowledge 模块的 MarkdownLoader 与 DocumentParser。
    """

    def __init__(self) -> None:
        self._documents_dir = _knowledge_root / "documents"
        self._markdown_loader = MarkdownLoader()

    def get_categories(self) -> list[str]:
        """获取知识库中实际存在的分类（documents/ 下的子目录名）。"""
        if not self._documents_dir.is_dir():
            return []
        return sorted(path.name for path in self._documents_dir.iterdir() if path.is_dir())

    def load_category(self, category: str) -> list[dict]:
        """加载指定分类下的全部文档。

        返回格式：[{"doc_id", "filename", "metadata", "content"}, ...]
        doc_id 为去掉 .md 后缀的文件名（如 "Java后端开发工程师"）。
        """
        documents: list[dict] = []
        category_dir = self._documents_dir / category
        if not category_dir.is_dir():
            return documents
        for path in sorted(category_dir.glob("*.md")):
            doc = self._markdown_loader.load(path, source_root=self._documents_dir)[0]
            documents.append(
                {
                    "doc_id": path.stem,
                    "filename": path.name,
                    "metadata": doc.metadata,
                    "content": doc.content,
                }
            )
        return documents

    def load_all(self) -> dict[str, list[dict]]:
        """加载全部分类的文档，返回 {category: [documents]}。"""
        return {category: self.load_category(category) for category in self.get_categories()}
