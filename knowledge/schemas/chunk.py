"""
文件名称：chunk.py
文件作用：Chunk 数据模型，定义切块后的文本片段。

当前版本：不启用（Keyword Retrieval 阶段无需切块）。
未来版本：启用 Embedding 后，长文档将被切分为多个 Chunk。
"""
from dataclasses import dataclass, field

@dataclass
class Chunk:
    """文本切块数据模型【预留】"""
    chunk_id: str                       # Chunk 唯一标识
    doc_id: str                         # 所属文档 ID
    content: str                        # Chunk 文本内容
    chunk_index: int                    # Chunk 在文档中的序号
    metadata: dict = field(default_factory=dict)
    embedding: list[float] = None       # Chunk 向量【未来】
