"""
文件名称：embedding_model.py
文件作用：Embedding 模型接口（预留接口）。
当前版本：关闭。仅保留接口框架。
未来版本：支持多种 Embedding 模型。

支持的模型（未来）：
  - BGE-M3（BAAI）
  - Qwen3-Embedding（阿里）
  - Jina Embedding（Jina AI）
  - SentenceTransformer（通用 Python 库）
  - OpenAI Embedding API
"""
class EmbeddingModel:
    def __init__(self, model_name: str = "bge-m3"):
        self.model_name = model_name
        self.model = None

    def encode(self, texts: list[str]) -> list[list[float]]:
        """TODO: 未来实现文本向量化"""
        pass

    def encode_query(self, query: str) -> list[float]:
        """TODO: 未来实现查询向量化"""
        pass
