# workflow/ — RAG Pipeline 工作流

## 目录职责
编排完整的 RAG 流程，每个 Pipeline 对应一个业务场景。

## Pipeline 清单
| 文件 | 业务场景 | 说明 |
|------|---------|------|
| `career_pipeline.py` | 就业画像分析 | 评估用户技术能力和竞争力 |
| `job_pipeline.py` | 岗位匹配 | 智能匹配最适合的岗位 |
| `resume_pipeline.py` | 简历优化 | 根据目标岗位优化简历 |
| `planner_pipeline.py` | 成长规划 | 生成个性化学习路线 |
| `interview_pipeline.py` | 面试辅导 | 提供面试问题解答和策略 |
| `market_pipeline.py` | 市场分析 | 分析就业市场和薪资行情 |

## 每个 Pipeline 的标准流程
```
Receive Query
→ Query Rewriter（改写查询）
→ Retriever（检索知识）
→ Context Builder（组装上下文）
→ Prompt Builder（构造 Prompt）
→ DeepSeek API（调用 LLM）
→ Output Parser（解析输出）
→ Generate Answer（返回结果）
```

## 当前状态
所有 Pipeline 均为框架代码，仅声明类和方法，具体业务逻辑待实现。
