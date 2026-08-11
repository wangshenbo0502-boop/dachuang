"""
文件名称：knowledge_loader.py
文件作用：知识库数据加载器（backend 适配层）。
负责对接项目 knowledge/ 模块的 Markdown 知识库，读取并解析各类知识文档。
当前版本：支持 Markdown 文档（jobs/companies/skills/interview 等分类）。
未来版本：支持 PDF/Word/Excel/网页等更多来源。
"""

import os
import sys

# 引入独立 knowledge 模块（位于项目根目录）
_knowledge_root = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "knowledge",
)
if _knowledge_root not in sys.path:
    sys.path.insert(0, _knowledge_root)

from loader.markdown_loader import MarkdownLoader  # noqa: E402
from parser.markdown_parser import MarkdownParser  # noqa: E402


class KnowledgeLoader:
    """知识库数据加载器：加载并解析 knowledge/documents/ 下的 Markdown 文档。

    所有 backend 模块（岗位匹配、就业画像等）通过本类访问知识文档，
    内部复用 knowledge 模块的 MarkdownLoader 与 MarkdownParser。
    """

    def __init__(self) -> None:
        self._markdown_loader = MarkdownLoader()
        self._parser = MarkdownParser()

    def get_categories(self) -> list[str]:
        """获取知识库中实际存在的分类（documents/ 下的子目录名）。"""
        documents_dir = self._markdown_loader.base_path
        if not os.path.isdir(documents_dir):
            return []
        return sorted(
            name
            for name in os.listdir(documents_dir)
            if os.path.isdir(os.path.join(documents_dir, name))
        )

    def load_category(self, category: str) -> list[dict]:
        """加载指定分类下的全部文档。

        返回格式：[{"doc_id", "filename", "metadata", "content"}, ...]
        doc_id 为去掉 .md 后缀的文件名（如 "Java后端开发工程师"）。
        """
        raw_docs = self._markdown_loader.load_all(category=category)
        documents: list[dict] = []
        for doc in raw_docs:
            parsed = self._parser.parse(doc["content"])
            documents.append(
                {
                    "doc_id": doc["filename"].replace(".md", ""),
                    "filename": doc["filename"],
                    "metadata": parsed["metadata"],
                    "content": parsed["body"],
                }
            )
        return documents

    def load_all(self) -> dict[str, list[dict]]:
        """加载全部分类的文档，返回 {category: [documents]}。"""
        return {category: self.load_category(category) for category in self.get_categories()}
