# RAG Evaluation Report

## 当前状态

评测框架与 30 条就业领域数据集已完成，覆盖岗位技能、技能定义、岗位匹配、简历、项目表达、成长规划、面试、政策和就业市场。指标包括 Recall@5、Recall@10、MRR、Hit Rate@5、NDCG@5 和平均检索延迟。

截至 2026-09-25，本机没有可用 Docker/PostgreSQL 知识库实例，索引检查返回数据库配置缺失或连接失败，因此**尚未生成检索效果数值**。本文不填写估算或虚构结果。

## 实验方法

真实运行器 `scripts/run_rag_evaluation.py` 对照：

1. PostgreSQL FTS Keyword
2. 精确 Vector（关闭索引扫描）
3. pgvector HNSW
4. HNSW + FTS 加权融合基线
5. HNSW + FTS + RRF
6. HNSW + FTS + RRF + Cross-Encoder

相关文档以稳定 `source` 标识判定。运行器成功后会生成 `knowledge/evaluation/reports/evaluation_report.json` 和 `.md`，其中全部数值来自该次真实执行。

## 执行前置条件

```powershell
docker compose up -d knowledge-db
python scripts/seed_knowledge.py
python scripts/check_rag_indexes.py
python scripts/run_rag_evaluation.py
```

正式比较 Reranker 前应设置 `RERANKER_ENABLED=true` 并预先下载配置的模型；否则第六组代表 NoOp 降级结果，报告应明确标注。

## 生成层评估

核心生产检索不依赖 Ragas。后续在具备固定 DeepSeek 模型版本、温度和参考答案后，可在评测层增加 Context Precision、Context Recall、Faithfulness 和 Answer Relevancy。缺少参考答案或评审模型时不得宣称已完成生成质量评估。
