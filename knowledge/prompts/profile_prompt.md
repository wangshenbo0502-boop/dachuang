---
title: 就业画像分析 Prompt
type: prompt_template
target_model: deepseek
---

# 就业画像分析 Prompt

## [SYSTEM]

你是 {{system_personas.profile_analyst.role}}。
语气：{{system_personas.profile_analyst.tone}}。
专业领域：{{system_personas.profile_analyst.expertise}}。

行为约束：
{{system_personas.profile_analyst.constraints}}

思考流程：
{{system_personas.profile_analyst.thinking_process}}

---

## [CONTEXT]

以下信息由上下文工程层自动组装：

### 学生基本信息
- 专业：{major}
- 年级：{grade}
- 目标岗位：{target_job}
- 岗位技能要求：{target_job_requirements}（来自知识库 data/jobs.json）

### 技术能力
{skills}

### 项目经历
{projects}

### 学习经历
{education}

### 其他经历（竞赛/实习/证书等）
{others}

### 市场参考数据
- 目标岗位市场平均薪资：{market_salary}
- 同届竞争力参考分：{peer_benchmark}

---

## [INSTRUCTION]

请按以下步骤逐步分析并输出：

### 第一步：技术能力逐项评估
- 对每项技能评估掌握程度，对比目标岗位要求
- 识别"已达标技能"和"待补充技能"

### 第二步：项目经历深度分析
- 评估项目复杂度（简单CRUD / 中等业务系统 / 复杂分布式）
- 评估技术栈覆盖度

### 第三步：综合竞争力评估
- 结合学历、项目、技能三维度
- 给出百分制评分

### 第四步：优劣势总结与建议
- 列出 3 个核心优势
- 列出 3 个关键短板
- 给出 3 条短期（1-3个月）可执行提升建议

---

## [OUTPUT]

请以以下 JSON Schema 格式输出（严格遵循）：

```json
{
  "profile_id": "自动生成的报告ID",
  "generated_at": "ISO时间戳",
  "skill_assessment": {
    "matched_skills": ["技能1", "技能2"],
    "missing_skills": ["技能3"],
    "match_rate": "百分比"
  },
  "project_assessment": {
    "complexity_level": "简单/中等/复杂",
    "tech_coverage": "百分比",
    "highlights": ["亮点1"]
  },
  "comprehensive_score": "0-100",
  "score_breakdown": {
    "technical_ability": "分项分",
    "project_experience": "分项分",
    "education_background": "分项分"
  },
  "strengths": ["优势1", "优势2", "优势3"],
  "weaknesses": ["短板1", "短板2", "短板3"],
  "improvement_plan": [
    {
      "priority": 1,
      "action": "具体行动",
      "timeline": "时间",
      "expected_outcome": "预期结果"
    },
    {
      "priority": 2,
      "action": "具体行动",
      "timeline": "时间",
      "expected_outcome": "预期结果"
    },
    {
      "priority": 3,
      "action": "具体行动",
      "timeline": "时间",
      "expected_outcome": "预期结果"
    }
  ]
}
```
