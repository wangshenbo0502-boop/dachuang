# embedding/ — Embedding 模型接口

## 目录职责
提供生产索引和查询共用的文本向量化接口。

## 当前状态
已接入 `IndexPipeline` 和 `VectorRetriever`。默认使用
`BAAI/bge-small-zh-v1.5`，测试使用确定性的 Mock Provider。

## 支持的模型
| 模型 | 提供方 | 维度 |
|------|--------|------|
| SentenceTransformers | UKP Lab / Hugging Face | 由配置决定 |
| Mock Provider | 项目内置 | 由配置决定 |

## 配置文件
项目根目录 `.env`，对应字段为 `EMBEDDING_PROVIDER`、
`EMBEDDING_MODEL`、`EMBEDDING_DIMENSION`、`EMBEDDING_BATCH_SIZE`。

## 文件
| 文件 | 状态 |
|------|------|
| `base.py` | Embedding 抽象接口 |
| `factory.py` | Provider 工厂和 Mock Provider |
| `local.py` | SentenceTransformers 本地实现 |
