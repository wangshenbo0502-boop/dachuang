# embedding/ — Embedding 模型接口

## 目录职责
提供文本向量化（Embedding）的统一接口。

## 当前状态
【预留】当前关闭。仅保留接口框架。

## 支持的模型候选（未来）
| 模型 | 提供方 | 维度 |
|------|--------|------|
| BGE-M3 | BAAI | 1024 |
| Qwen3-Embedding | 阿里 | 2048 |
| Jina Embedding | Jina AI | 1024 |
| SentenceTransformer | UKP Lab | 可变 |

## 配置文件
`config/embedding_config.json`

## 文件
| 文件 | 状态 |
|------|------|
| `embedding_model.py` | 预留接口 |
