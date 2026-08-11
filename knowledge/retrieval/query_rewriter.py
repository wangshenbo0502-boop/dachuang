"""
文件名称：query_rewriter.py
文件作用：Query 改写器，负责对用户原始问题进行优化和扩展。
当前版本：基础同义词扩展 + 关键词提取。
未来版本：基于 LLM 的 Query 改写、多轮对话上下文融合。

流程位置：
  User Query → Query Rewrite → Keyword Search → TopK Docs → Context Builder → LLM
"""


import re


class QueryRewriter:
    def rewrite(self, query: str, context: dict = None) -> str:
        return query.strip()

    def extract_keywords(self, query: str) -> list[str]:
        keywords = []
        en_keywords = re.findall(r'[a-zA-Z0-9_+#.]+', query)
        keywords.extend([k.lower() for k in en_keywords if len(k) >= 2])
        chinese = re.findall(r'[\u4e00-\u9fff]+', query)
        keywords.extend(chinese)
        return keywords
