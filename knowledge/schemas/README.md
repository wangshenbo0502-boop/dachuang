# schemas/ — 数据模型定义

## 目录职责
定义整个 RAG 系统中所有模块共享的核心数据结构（Document / Chunk / SearchResult）。

## 为什么需要
- 统一数据契约，避免各模块自定义 ad-hoc dict
- 支持 IDE 类型提示和静态检查
- 方便未来迁移到 Pydantic v2 以支持 JSON Schema 导出和自动校验

## 模块文件
| 文件 | 说明 |
|------|------|
| `document.py` | 文档标准模型 |
| `chunk.py` | 切块模型【预留】 |
| `search_result.py` | 检索结果模型 |

## 未来迁移计划
当需要更强的校验和序列化能力时，可将 dataclass 迁移为 Pydantic v2 BaseModel。
