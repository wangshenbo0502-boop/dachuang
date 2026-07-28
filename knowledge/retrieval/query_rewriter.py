"""
文件名称：query_rewriter.py
文件作用：Query 改写器，负责对用户原始问题进行优化和扩展。
当前版本：基础同义词扩展 + 关键词提取。
未来版本：基于 LLM 的 Query 改写、多轮对话上下文融合。

流程位置：
  User Query → Query Rewrite → Keyword Search → TopK Docs → Context Builder → LLM
"""


class QueryRewriter:
    def rewrite(self, query: str, context: dict = None) -> str:
        """TODO: 改写用户查询，扩展关键词"""
        pass

    def extract_keywords(self, query: str) -> list[str]:
        """TODO: 提取查询中的关键词"""
        pass
