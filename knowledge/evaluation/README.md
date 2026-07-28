# evaluation/ — RAG 评估模块

## 目录职责
评估 RAG 系统的检索质量（找到了吗？）和生成质量（答对了吗？）。

## 当前状态
【预留】当前关闭。仅保留接口框架。

## 未来实现的评估维度

### 检索评估
| 指标 | 含义 |
|------|------|
| MRR | Mean Reciprocal Rank |
| NDCG@K | Normalized Discounted Cumulative Gain |
| Recall@K | TopK 召回率 |
| Precision@K | TopK 精确率 |

### 生成评估
| 指标 | 含义 |
|------|------|
| Faithfulness | 生成内容是否忠于检索上下文 |
| Answer Relevance | 回答是否与问题相关 |
| Context Relevance | 检索上下文是否与问题相关 |

## 参考框架
- RAGAS (https://github.com/explodinggradients/ragas)
- TruLens
- DeepEval

## 模块文件
| 文件 | 状态 |
|------|------|
| `metrics.py` | 预留接口 |
| `test_cases.json` | 空测试集 |
