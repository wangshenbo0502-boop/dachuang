---
title: LangChain
category: skills
tags: [AI, 大模型, 应用开发, 编排框架]
source: [LangChain官方文档, CSDN 2026技术趋势, 腾讯云开发者社区, 猎聘AI岗位JD]
last_update: 2026-07-28
---

# LangChain

> 大模型应用开发最流行的编排框架，连接LLM与外部工具/数据的"胶水层"。LangChain + RAG 已成为大模型应用开发的事实标准，据猎聘 2026 年数据，RAG 工程师/大模型应用工程师岗位同比增长 80%+，LangChain 是该岗位的核心技能要求。

- **就业影响**: 高（AI应用工程师必备）
- **前置技能**: Python, 大模型基础
- **关联系能**: RAG, Agent, 向量数据库, FastAPI

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- LangChain 核心概念：Chain / Agent / Tool / Memory / Retriever
- LCEL（LangChain Expression Language）表达式语言与管道语法
- 基础 Chain 实现：LLMChain、SequentialChain、RouterChain
- Prompt Templates 模板管理：字符串模板、聊天模板、消息模板
- Output Parsers 输出解析器：Pydantic、JSON、CSV、列表解析
- 模型 I/O 模块：Chat Models 与 LLM 的区别与选型
- 消息类型：SystemMessage、HumanMessage、AIMessage、FunctionMessage
- LangChain 生态概览：LangSmith、LangGraph、LangServe

**学习资源：**
- [LangChain 官方文档](https://python.langchain.com/) — 官方文档 · 免费 · 入门 · 英文
- [LangChain 中文教程](https://www.langchain.com.cn/) — 社区文档 · 免费 · 入门 · 中文
- [DeepLearning.AI LangChain 入门课](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) — 在线课程 · 免费 · 入门 · 英文

**练习项目：**
- 使用 LCEL 构建一个简单的翻译 Chain，支持中英互译
- 实现一个带 Few-shot Prompt 模板的文本分类应用（支持 5 个类别）
- 使用 Pydantic Output Parser 将 LLM 输出解析为结构化 JSON 对象
- 搭建一个简单的多轮对话机器人，使用 ConversationBufferMemory

**评估方式：**
- 实操 — 独立完成一个基于 LangChain 的多步骤问答应用
- 代码审查 — 正确使用 Prompt Template 与 Output Parser，代码结构清晰
- 功能验证 — 多轮对话上下文保持正确，结构化输出格式规范

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- RAG 检索链：RetrievalQA、ConversationalRetrievalChain、Map-Reduce 链
- Agent 框架：ReAct 模式、OpenAI Tools Agent、Structured Chat Agent
- Memory 类型：BufferMemory、SummaryMemory、VectorStoreMemory、EntityMemory
- 文档加载器：PDF、Markdown、Web、CSV、Word 等 20+ 种加载器
- 文档切分策略：CharacterSplitter、RecursiveCharacterSplitter、TokenSplitter
- 向量存储集成：Chroma、FAISS、Milvus、Pinecone、Weaviate
- Callback 机制与流式输出：Streaming、StdOutCallbackHandler
- 工具集成：Tavily 搜索、Python REPL、SQL 数据库、API 调用
- 重试与降级策略：模型调用失败处理、超时控制
- LangChain Expression Language 高级用法：自定义 Runnable

**学习资源：**
- [LangChain RAG 指南](https://python.langchain.com/docs/use_cases/question_answering/) — 官方文档 · 免费 · 进阶 · 英文
- [DeepLearning.AI 向量数据库与 RAG 课程](https://www.deeplearning.ai/short-courses/vector-databases-embeddings-applications/) — 在线课程 · 免费 · 进阶 · 英文
- [腾讯云开发者社区 - LangChain 实战专栏](https://cloud.tencent.com/developer) — 技术博客 · 免费 · 进阶 · 中文

**练习项目：**
- 构建一个基于本地 PDF 文档的 RAG 问答系统，支持多文档检索
- 实现一个支持多轮对话的知识库助手（含 ConversationBufferWindowMemory）
- 开发一个具备网络搜索 + 计算器能力的 ReAct Agent
- 实现一个文档摘要系统，使用 Map-Reduce 链处理长文档
- 集成 3 种以上不同的向量数据库并对比检索效果

**评估方式：**
- 项目评审 — RAG 系统回答准确率达标，Agent 能正确调用工具并处理中间结果
- 代码审查 — 模块化设计合理，异常处理完善，文档与注释齐全
- 性能评估 — 流式输出流畅，平均响应时间在合理范围内

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- LangGraph 多 Agent 协作与状态图编排：StateGraph、节点、边、条件边
- 生产级部署：异步支持、并发控制、错误重试、熔断降级
- LangSmith 监控、评估与调试：Tracing、Datasets、Evaluators
- 自定义 Tool / Agent / Retriever / Runnable 开发
- 性能优化：语义缓存、批量处理、Prompt 精简、模型分层
- 企业级 RAG 架构：多路召回、重排序、Query 改写、上下文压缩
- 与 FastAPI 集成构建 API 服务：LangServe、流式接口、鉴权
- 企业级安全：数据脱敏、权限控制、内容审核、Prompt 注入防护
- 多租户架构：数据隔离、模型路由、配额管理
- LangChain 生态整合：LangSmith 评估流水线、LangGraph 持久化

**学习资源：**
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/) — 官方文档 · 免费 · 高级 · 英文
- [LangSmith 官方文档](https://docs.smith.langchain.com/) — 官方文档 · 免费 · 高级 · 英文
- [LangServe 部署指南](https://python.langchain.com/docs/langserve/) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 使用 LangGraph 构建多 Agent 协作系统（规划 + 执行 + 评审三角色）
- 将 RAG 系统部署为 FastAPI 服务并接入 LangSmith 监控与评估
- 设计并实现一个企业级知识库问答系统（含多路召回 + Rerank + Query 改写）
- 开发自定义 Retriever，实现混合检索与重排序逻辑
- 搭建多租户 LLM 应用平台，支持用户数据隔离与权限管控

**评估方式：**
- 架构设计 — 能够独立设计企业级 LLM 应用架构，系统可观测、可扩展、性能达标
- 代码审查 — 生产级代码质量，含完善的错误处理、日志、监控、测试
- 综合答辩 — 能够阐述技术选型理由，应对性能优化、成本控制等架构问题

---

## 学习建议与进阶路径

- **社区参与**：关注 LangChain 官方博客与 GitHub 仓库，跟进版本更新与新特性
- **实战积累**：从真实业务场景出发，持续迭代优化 LLM 应用的效果与性能
- **横向拓展**：结合 RAG、Agent、向量数据库等技能，构建端到端 AI 应用能力
- **纵向深入**：研究 LangGraph 与 LangSmith 的高级用法，向 AI 架构师方向发展
- **生态视野**：关注 LlamaIndex、Haystack 等同类框架，保持技术选型的开阔视野
