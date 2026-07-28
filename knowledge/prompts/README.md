# prompts/ — Prompt 模板

## 目录职责
存放各业务场景的 LLM Prompt 模板（SYSTEM/CONTEXT/INSTRUCTION/OUTPUT 四段式）。

## 模板清单
| 文件 | 场景 | 目标模型 |
|------|------|---------|
| `profile_prompt.md` | 就业画像分析 | DeepSeek |
| `job_prompt.md` | 岗位匹配 | DeepSeek |
| `resume_prompt.md` | 简历优化 | DeepSeek |
| `growth_prompt.md` | 成长规划 | DeepSeek |

## 模板结构
每个模板遵循标准四段式：
- `[SYSTEM]`：模型角色 + 行为约束
- `[CONTEXT]`：上下文占位（由 Context Builder 动态填充）
- `[INSTRUCTION]`：分步指令 + 思考链
- `[OUTPUT]`：JSON Schema 输出格式

## 数据来源
从 v0.2 的 `01-prompt-engineering/templates/` 迁移而来，格式从 .txt 转为 .md（带 YAML Front Matter）。
