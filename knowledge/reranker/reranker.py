"""
文件名称：reranker.py
文件作用：重排序器接口（预留接口）。
当前版本：关闭。仅保留接口框架。
未来版本：对检索结果进行二次精排。

支持的重排序模型（未来）：
  - BGE-Reranker（BAAI）
  - Jina-Reranker（Jina AI）
  - Cohere Rerank API
"""
class Reranker:
    def __init__(self, model_name: str = "bge-reranker"):
        self.model_name = model_name
        self.model = None

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        """TODO: 未来实现重排序"""
        pass
