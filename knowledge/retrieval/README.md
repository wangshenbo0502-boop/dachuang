# retrieval/ — 检索模块

## 目录职责
负责根据用户查询从知识库中检索相关文档，并组装为 LLM 可消费的上下文。

## 检索流程
```
User Query
  → QueryRewriter（改写查询，提取关键词）
  → KeywordRetriever（从索引中检索 TopK 文档）
  → ContextBuilder（组装上下文文本）
  → 输出给 Workflow Pipeline
```

## 模块文件
| 文件 | 状态 | 说明 |
|------|------|------|
| `query_rewriter.py` | 框架已就绪 | 查询改写和关键词提取 |
| `keyword_retriever.py` | 框架已就绪 | 关键词检索器 |
| `search_engine.py` | 框架已就绪 | 检索引擎统一入口 |
| `context_builder.py` | 框架已就绪 | 上下文组装器 |

## 当前实现
- 纯 Python 关键词检索
- 无外部依赖

## 未来升级
- Embedding 向量检索
- 混合检索（关键词 + 向量融合）
- 接入 Reranker 二次精排
