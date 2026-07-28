"""
文件名称：__init__.py
文件作用：数据模型定义（Schemas）模块统一入口。

定义整个 RAG 系统中的核心数据结构，所有模块共享使用。
使用 Python dataclass 定义，方便类型检查和序列化。
未来可迁移为 Pydantic v2 BaseModel 以获得更强的校验能力。
"""
from .document import Document
from .chunk import Chunk
from .search_result import SearchResult
