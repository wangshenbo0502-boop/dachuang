---
title: RAG检索增强生成
category: skills
tags: [AI, 大模型, 检索增强, 知识库]
source: [腾讯云开发者社区, DeepSeek RAG实战, CSDN 2026技术趋势, LangChain官方博客]
last_update: 2026-07-28
---

# RAG检索增强生成

> 企业级AI应用的标准架构，通过外部知识库检索增强大模型回答，有效解决幻觉和知识时效性问题。2026年超过75%的企业AI落地采用RAG架构，RAG工程师岗位同比增长80%以上，是AI应用开发的核心技术方向。

- **就业影响**: 高（AI应用核心技术，75%企业AI落地采用RAG）
- **前置技能**: Python, 大模型基础, 向量数据库
- **关联系能**: LangChain, LlamaIndex, Milvus, Embedding

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- RAG 基本原理与架构：检索 + 生成两阶段核心流程
- RAG 的价值与适用场景：知识问答、文档搜索、客服助手
- 文档加载：PDF、Word、Markdown、网页、PPT 等多格式处理
- 文档切分策略：固定大小分块、按段落分块、按句子分块
- Embedding 模型原理与选型：OpenAI Embedding、BGE、M3E、GTE
- 向量检索基础：相似度计算（余弦/欧氏距离/内积）、Top-K 检索
- 简单 RAG 系统端到端实现：加载 -> 切分 -> 向量化 -> 检索 -> 生成
- RAG 效果的初步评估方法：人工评估、简单指标对比

**学习资源：**
- [LangChain RAG 官方教程](https://python.langchain.com/docs/use_cases/question_answering/) — 官方文档 · 免费 · 入门 · 英文
- [腾讯云 RAG 技术专栏](https://cloud.tencent.com/developer/column) — 技术博客 · 免费 · 入门 · 中文
- [DeepSeek RAG 入门指南](https://platform.deepseek.com/docs/guides/rag) — 官方文档 · 免费 · 入门 · 中文

**练习项目：**
- 使用 LangChain + Chroma 构建一个基于本地文档的简单问答系统
- 对比 3 种不同 Embedding 模型（BGE / M3E / OpenAI）的检索效果差异
- 实现一个命令行版的本地知识库问答工具，支持 PDF 和 Markdown 文档
- 构建一个小型测试集（20 个问答对），初步评估 RAG 系统的回答准确率

**评估方式：**
- 实操 — 独立完成端到端 RAG 系统，能正确检索并基于上下文回答问题
- 功能验证 — 支持至少 2 种文档格式，检索结果与问题相关度达标
- 报告输出 — 完成不同 Embedding 模型的对比实验报告

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- 分块策略优化：语义分块（Semantic Chunking）、递归分块、父子分块
- 混合检索：关键词检索（BM25 / Elasticsearch）+ 向量检索融合
- 重排序（Rerank）：Cross-Encoder、Cohere Rerank、BGE-Reranker、ColBERT
- 多模态 RAG：图片、表格、公式的检索与多模态 Embedding
- RAG 评估指标与框架：RAGAS（忠实度/相关性/答案相关性）、TruLens
- 查询改写（Query Transformation）：多查询生成、HyDE、Step-Back Prompting
- 上下文压缩与精选（Context Compression）：LLM 提炼、Embedding 重过滤
- 对话式 RAG：历史上下文整合、追问识别、会话状态管理
- RAG 流水线设计：数据预处理 -> 索引构建 -> 查询处理 -> 回答生成

**学习资源：**
- [RAGAS 官方文档](https://docs.ragas.io/) — 官方文档 · 免费 · 进阶 · 英文
- [DeepSeek RAG 实战指南](https://platform.deepseek.com/) — 技术文档 · 免费 · 进阶 · 中文
- [CSDN - 2026 RAG 技术趋势报告](https://www.csdn.net/) — 技术报告 · 免费 · 进阶 · 中文

**练习项目：**
- 构建一个带 BM25 + 向量混合检索的 RAG 系统，实现 RRF 融合
- 集成 BGE-Reranker 优化检索结果，对比前后准确率提升并量化
- 使用 RAGAS 对 RAG 系统进行全面评估，输出包含 5 项指标的评估报告
- 实现一个支持多轮对话的 RAG 系统，能正确处理指代消解与上下文追问
- 设计并实现一个语义分块策略，对比固定分块的检索效果差异

**评估方式：**
- 项目评审 — RAG 系统在 100 条测试集上的回答准确率与引用准确率均达到预期指标
- 性能评估 — 检索 + 生成端到端延迟控制在合理范围内
- 代码审查 — 模块划分清晰，配置化程度高，便于迭代优化

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- Agentic RAG：Agent 驱动的自适应检索、多步推理、工具调用
- Graph RAG：知识图谱构建、实体关系抽取、图检索与向量检索融合
- Query 改写进阶：查询分解、子问题回答、多跳推理 RAG
- 多轮对话 RAG：会话感知检索、记忆增强、用户画像结合
- 生产级 RAG 架构：数据流水线、增量更新、版本管理、索引回滚
- 性能调优：检索延迟优化、批量 Embedding、缓存策略、冷热分层
- 成本优化：模型选型分层、Embedding 分层、检索降级、Token 优化
- 企业级 RAG 落地：权限控制、多租户、数据安全、合规审计
- 多路召回与融合策略设计：向量 + 关键词 + 知识图谱 + 数据库
- RAG 前沿技术：Self-RAG、Corrective RAG、Adaptive RAG、Modular RAG

**学习资源：**
- [Graph RAG 微软官方论文](https://microsoft.github.io/graphrag/) — 研究论文 · 免费 · 高级 · 英文
- [LangChain 高级 RAG 模式](https://python.langchain.com/docs/use_cases/question_answering/advanced/) — 官方文档 · 免费 · 高级 · 英文
- [LlamaIndex 高级 RAG 教程](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 设计并实现一个 Agentic RAG 系统，支持多步推理、工具调用与自适应检索
- 构建 Graph RAG 原型系统，对比传统向量 RAG 在复杂推理问题上的效果差异
- 搭建生产级 RAG 服务，含数据更新流水线、监控告警、性能指标面板
- 设计并实现企业级多租户 RAG 平台，支持文档权限隔离与检索权限控制
- 完成 RAG 系统的全面性能优化，在保持准确率的前提下将成本降低 30% 以上

**评估方式：**
- 架构设计 — 能够独立设计企业级 RAG 架构方案，综合考虑效果、性能、成本与可维护性
- 方案评审 — 针对给定业务场景，能输出完整的 RAG 技术选型与架构设计文档
- 综合答辩 — 能够深入阐述 RAG 各模块的技术原理、选型依据与优化方向

---

## 学习建议与进阶路径

- **持续实践**：RAG 是工程性极强的技术，需在真实数据与业务场景中反复迭代优化
- **评估驱动**：建立完善的评估体系，用数据驱动优化，避免凭感觉调参
- **关注前沿**：跟踪 Graph RAG、Agentic RAG、Self-RAG 等新兴技术方向
- **全栈能力**：结合向量数据库、Embedding 模型、推理引擎，构建端到端优化能力
- **业务理解**：深入理解业务场景与知识结构，设计与业务匹配的 RAG 架构方案
