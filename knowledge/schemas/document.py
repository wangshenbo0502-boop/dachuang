"""
文件名称：document.py
文件作用：Document 数据模型，定义知识文档的标准结构。

Document 是 RAG 管道中流转的最基本数据单元。
从 Loader 产出，经 Parser 加工，最终被 Indexer 消费。
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Document:
    """知识文档标准数据模型"""
    doc_id: str                                    # 文档唯一标识
    content: str                                   # 文档正文内容
    metadata: dict = field(default_factory=dict)   # 元数据（title/tags/category/source等）
    source_path: Optional[str] = None              # 源文件路径
    created_at: Optional[str] = None               # 创建时间
    updated_at: Optional[str] = None               # 更新时间
