"""
文件名称：search_engine.py
文件作用：检索引擎统一入口，协调 QueryRewriter + Retriever 完成检索。
当前版本：关键词检索。
未来版本：Hybrid Search（关键词 + 向量混合检索）。

检索流程：
  User Query
  → QueryRewriter (改写)
  → KeywordRetriever (关键词检索)
  → ContextBuilder (组装上下文)
  → Prompt (注入 LLM)
"""


class SearchEngine:
    def __init__(self, retriever, query_rewriter=None):
        self.retriever = retriever
        self.query_rewriter = query_rewriter

    def search(self, query: str, top_k: int = 10, category: str = None) -> list[dict]:
        """TODO: 统一检索入口：改写 → 检索 → 返回"""
        pass
