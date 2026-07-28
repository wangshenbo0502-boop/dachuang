"""
文件名称：search_result.py
文件作用：SearchResult 数据模型，定义检索结果的标准结构。

Retriever 返回 SearchResult 列表，ContextBuilder 据此组装 LLM 上下文。
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SearchResult:
    """检索结果标准数据模型"""
    doc_id: str                             # 文档/Chunk ID
    content: str                            # 匹配内容
    score: float                            # 相关性得分
    metadata: dict = field(default_factory=dict)
    rank: Optional[int] = None              # 排序位置（经 Reranker 后）
    source_type: str = "keyword"            # 检索来源：keyword / embedding / hybrid
