# indexing/ — 索引模块

## 目录职责
为知识文档建立检索索引，加速文档查找。

## 模块文件
| 文件 | 状态 | 说明 |
|------|------|------|
| `keyword_index.py` | 框架已就绪 | 关键词倒排索引（内存版） |

## 当前实现
- `KeywordIndex`：基于内存的关键词倒排索引，支持 build/search/add/remove

## 索引升级路线
```
Keyword Index（当前）
→ Embedding Index（BGE-M3/Qwen3-Embedding）
→ FAISS Index（本地向量索引）
→ Hybrid Index（关键词 + 向量混合）
→ Milvus Index（分布式，可选）
```

## 未来扩展
- 支持增量更新索引
- 支持索引持久化到磁盘
