"""
文件名称：keyword_retriever.py
文件作用：关键词检索器，负责根据用户输入的问题进行关键词检索。
扫描 Markdown 知识文档，返回 TopK 相关知识。

当前版本：Keyword Retrieval（关键词匹配）。
未来版本：Embedding Retrieval → Hybrid Retrieval → Reranker。

检索流程：
  1. 接收改写后的 Query
  2. 从 KeywordIndex 中检索匹配文档
  3. 返回 TopK 结果及其相似度分数
"""


class KeywordRetriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query: str, top_k: int = 10, category: str = None) -> list[dict]:
        """TODO: 执行关键词检索，返回 [{doc_id, content, metadata, score}, ...]"""
        pass

    def search_by_tags(self, tags: list[str], top_k: int = 10) -> list[dict]:
        """TODO: 按标签检索文档"""
        pass
