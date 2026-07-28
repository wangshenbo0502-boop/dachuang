"""
文件名称：keyword_index.py
文件作用：关键词索引器，负责为 Markdown 知识文档建立关键词倒排索引。
当前版本：内存关键词倒排索引（Keyword Index）。
未来版本：Embedding Index（向量化索引）+ Hybrid Index（混合索引）。

升级路线：
  Keyword Index（当前）
  → Embedding Index（BGE-M3/Qwen3-Embedding）
  → FAISS 索引
  → Hybrid Index（关键词 + 向量混合）
  → Milvus 索引（可选）
"""
class KeywordIndex:
    def __init__(self):
        self.inverted_index: dict = {}
        self.documents: dict = {}

    def build(self, documents: list[dict]) -> None:
        """TODO: 构建关键词倒排索引"""
        pass

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """TODO: 关键词搜索"""
        pass

    def add_document(self, doc_id: str, content: str, metadata: dict) -> None:
        """TODO: 增量添加文档到索引"""
        pass

    def remove_document(self, doc_id: str) -> None:
        """TODO: 从索引中移除文档"""
        pass
