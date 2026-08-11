"""
文件名称：knowledge_service.py
文件作用：知识库查询服务，提供统一的 RAG 知识检索能力。
负责构建知识索引，提供知识搜索、文档查询、技能要求提取等通用能力，
供岗位匹配、就业画像、简历优化等各业务模块复用。

当前版本：基于 keyword index 关键词检索。
未来版本：升级 Embedding + Hybrid Retrieval + Reranker。
"""

import os
import re
import sys
from typing import Optional

# 引入独立 knowledge 模块（位于项目根目录）
_knowledge_root = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "knowledge",
)
if _knowledge_root not in sys.path:
    sys.path.insert(0, _knowledge_root)

from app.knowledge.knowledge_loader import KnowledgeLoader  # noqa: E402

from indexes.keyword_index import KeywordIndex  # noqa: E402
from retrieval.query_rewriter import QueryRewriter  # noqa: E402
from retrieval.keyword_retriever import KeywordRetriever  # noqa: E402
from retrieval.search_engine import SearchEngine  # noqa: E402


class KnowledgeService:
    """知识库查询服务（单例）：加载全部知识文档并构建检索索引。

    职责：
        - 构建并维护 keyword 索引
        - 提供跨分类的知识检索入口
        - 提供单篇文档查询与技能要求提取
    其他业务服务（如 JobMatchService）依赖本服务获取知识数据。
    """

    _instance: Optional["KnowledgeService"] = None

    def __init__(self) -> None:
        self._loader = KnowledgeLoader()
        self._index = KeywordIndex()
        self._engine: Optional[SearchEngine] = None
        # (category, doc_id) -> doc
        self._documents: dict[tuple[str, str], dict] = {}
        # category -> [doc_id]
        self._by_category: dict[str, list[str]] = {}
        self._loaded = False

    # ── 单例懒加载 ──

    @classmethod
    def instance(cls) -> "KnowledgeService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self) -> None:
        """首次调用时加载全部知识文档并构建索引（延迟加载）。"""
        if self._loaded:
            return
        for category in self._loader.get_categories():
            docs = self._loader.load_category(category)
            ids: list[str] = []
            for doc in docs:
                key = (category, doc["doc_id"])
                self._documents[key] = doc
                ids.append(doc["doc_id"])
            self._by_category[category] = ids
        self._index.build(list(self._documents.values()))
        self._engine = SearchEngine(
            retriever=KeywordRetriever(self._index),
            query_rewriter=QueryRewriter(),
        )
        self._loaded = True

    # ── 知识检索 ──

    def search(self, query: str, category: Optional[str] = None, top_k: int = 10) -> list[dict]:
        """在知识库中检索与 query 相关的文档。

        Args:
            query: 检索关键词
            category: 限定知识分类（如 "jobs"、"skills"），None 表示全库检索
            top_k: 返回结果数量

        Returns:
            检索结果列表 [{"doc_id", "content", "score", "metadata", "filename"}, ...]
        """
        self._ensure_loaded()
        return self._engine.search(query, top_k=top_k, category=category)

    def get_document(self, category: str, doc_id: str) -> Optional[dict]:
        """获取指定分类下的单篇知识文档。"""
        self._ensure_loaded()
        return self._documents.get((category, doc_id))

    def list_documents(self, category: str) -> list[dict]:
        """获取指定分类下的全部文档列表。"""
        self._ensure_loaded()
        return [self._documents[(category, doc_id)] for doc_id in self._by_category.get(category, [])]

    def list_categories(self) -> list[dict]:
        """列出知识库中的分类及文档数量。"""
        self._ensure_loaded()
        return [
            {"category": category, "count": len(doc_ids)}
            for category, doc_ids in sorted(self._by_category.items())
        ]

    # ── 技能要求提取 ──

    def get_skill_requirements(self, job_id: str) -> list[str]:
        """获取岗位文档中的核心技能要求。

        优先使用 YAML 元数据中的 tags，
        缺失时从正文「核心技能要求」小节中提取。
        """
        doc = self.get_document("jobs", job_id)
        if not doc:
            return []
        tags = doc["metadata"].get("tags", [])
        if tags:
            return [str(tag).lower() for tag in tags if tag]
        # 回退：从正文提取技能列表
        content = doc.get("content", "")
        match = re.search(r"核心技能要求.*?\n((?:\s*[-*]\s*.+\n?)+)", content, re.IGNORECASE)
        if not match:
            return []
        skills = re.findall(r"[-*]\s*(.+)", match.group(1))
        return [s.strip().lower() for s in skills if s.strip()]

    # ── 重置（供测试使用） ──

    @classmethod
    def reset(cls) -> None:
        """清除单例，供测试或知识库变更后重新初始化。"""
        cls._instance = None
