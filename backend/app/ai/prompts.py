"""
文件名称：prompts.py
文件作用：AI Prompt 模板管理，统一管理系统提示词和用户提示词模板。
支持从外部Markdown文件加载System Prompt，便于迭代优化。
"""

from app.ai.deepseek_client import DeepSeekClient


def _load_system_prompt(filename: str) -> str:
    """从 knowledge/prompts/ 加载系统Prompt，失败时返回空字符串"""
    return DeepSeekClient.load_prompt(filename)


class SystemPrompts:
    """系统角色提示词，优先从外部文件加载"""

    @staticmethod
    def get(name: str, fallback: str = "") -> str:
        """获取系统提示词

        Args:
            name: 文件名（如 "system_profile_analyst"）
            fallback: 文件不存在时的回退文本
        """
        prompt = _load_system_prompt(f"{name}.md")
        return prompt or fallback

    @staticmethod
    def profile_analyst() -> str:
        return SystemPrompts.get(
            "system_profile_analyst",
            "你是一位资深的IT职业规划专家和技术面试官，请严格按照要求的JSON格式输出。"
        )

    @staticmethod
    def resume_optimizer() -> str:
        return SystemPrompts.get(
            "system_resume_optimizer",
            "你是一位资深的IT行业简历优化专家，请严格按照要求的JSON格式输出。"
        )

    @staticmethod
    def growth_planner() -> str:
        return SystemPrompts.get(
            "system_growth_planner",
            "你是一位资深的程序员成长导师，请严格按照要求的JSON格式输出。"
        )

    @staticmethod
    def job_matcher() -> str:
        return SystemPrompts.get(
            "system_job_matcher",
            "你是一位资深的IT行业招聘技术专家，请严格按照要求的JSON格式输出。"
        )


class ProfileAnalysisPrompts:
    """就业画像分析 Prompt 模板"""

    @staticmethod
    def build_user_prompt(
        name: str,
        school: str,
        major: str,
        grade: str,
        bio: str,
        skills: list[dict],
        projects: list[dict],
        competitions: list[dict] = None,
        internships: list[dict] = None,
        target_job: str = "",
    ) -> str:
        skills_text = _format_skills(skills)
        projects_text = _format_projects(projects)
        competitions_text = _format_competitions(competitions) if competitions else ""
        internships_text = _format_internships(internships) if internships else ""
        target_job_text = f"\n### 意向岗位\n{target_job}\n" if target_job else ""

        return f"""请对以下计算机专业大学生进行就业竞争力画像分析。

### 学生基本信息
- 姓名：{name}
- 学校：{school}
- 专业：{major}
- 年级：{grade}
- 自我评价：{bio or '无'}
{target_job_text}
### 掌握技能
{skills_text}

### 项目经历
{projects_text}
{competitions_text}
{internships_text}
---

请从企业招聘视角进行深度分析，输出以下JSON结构：

```json
{{
  "profile_summary": "一段话总结该学生的整体就业竞争力画像（200字以内）",
  "technical_direction": "最适合的技术方向",
  "core_advantages": ["核心优势1", "核心优势2", "核心优势3"],
  "current_level": "当前水平定位",
  "recommended_directions": [
    {{"job_title": "推荐岗位1", "match_rate": 匹配度0-100}},
    {{"job_title": "推荐岗位2", "match_rate": 匹配度}},
    {{"job_title": "推荐岗位3", "match_rate": 匹配度}}
  ],
  "areas_to_improve": ["需要提升的方面1", "需要提升的方面2"],
  "comprehensive_score": 综合评分0-100,
  "skill_assessment": {{
    "programming_foundation": 评分0-100,
    "framework_usage": 评分0-100,
    "database_skill": 评分0-100,
    "engineering_practice": 评分0-100,
    "project_experience": 评分0-100
  }}
}}
```"""


class ResumeOptimizationPrompts:
    """简历优化 Prompt 模板"""

    @staticmethod
    def build_user_prompt(
        name: str,
        target_job: str,
        skills: list[dict],
        projects: list[dict],
        internships: list[dict] = None,
        original_resume: str = "",
    ) -> str:
        skills_text = _format_skills(skills)
        projects_text = _format_projects(projects)
        internships_text = _format_internships(internships) if internships else ""
        original_text = f"\n### 原始简历内容\n{original_resume}\n" if original_resume else ""

        return f"""请针对目标岗位「{target_job}」，对以下学生的简历进行专业优化。

### 基本信息
姓名：{name}
目标岗位：{target_job}
{original_text}
### 技能清单
{skills_text}

### 项目经历
{projects_text}
{internships_text}
---

请从企业HR和技术面试官的视角进行优化，输出以下JSON结构：

```json
{{
  "optimized_projects": [
    {{
      "project_name": "项目名称",
      "original": "原始描述",
      "optimized": "优化后的描述（STAR法则，50-100字）",
      "highlight_tags": ["标签1", "标签2"]
    }}
  ],
  "optimized_skills": [
    {{"original": "原始技能描述", "optimized": "优化后的技能描述"}}
  ],
  "overall_suggestions": ["整体建议1", "整体建议2"],
  "resume_score": 评分0-100,
  "personal_summary": "优化后的个人简介（3-4句话）"
}}
```

注意：不要虚构经历，只优化表达方式；尽量量化成果。"""


class GrowthPlanningPrompts:
    """成长规划 Prompt 模板"""

    @staticmethod
    def build_user_prompt(
        name: str,
        major: str,
        grade: str,
        target_job: str,
        skills: list[dict],
        projects: list[dict],
        profile_analysis: dict = None,
    ) -> str:
        skills_text = _format_skills(skills)
        projects_text = _format_projects(projects)
        analysis_text = ""
        if profile_analysis:
            analysis_text = f"""
### 当前画像分析结果
- 综合评分：{profile_analysis.get('comprehensive_score', 'N/A')}
- 核心优势：{'、'.join(profile_analysis.get('core_advantages', []))}
- 待提升：{'、'.join(profile_analysis.get('areas_to_improve', []))}
"""

        return f"""请为以下计算机专业大学生制定针对「{target_job}」岗位的个性化成长提升规划。

### 学生基本信息
- 姓名：{name}
- 专业：{major}
- 年级：{grade}
- 目标岗位：{target_job}
{analysis_text}
### 当前技能
{skills_text}

### 已有项目经历
{projects_text}

---

请制定一份3-6个月的可执行学习成长计划，输出以下JSON结构：

```json
{{
  "current_situation": "当前能力现状分析（100字以内）",
  "ability_gaps": [
    {{"skill": "技能名称", "importance": "必须/加分", "difficulty": "低/中/高", "description": "说明"}}
  ],
  "learning_roadmap": [
    {{
      "stage": "第一阶段（X-X个月）",
      "focus": "核心目标",
      "tasks": ["任务1", "任务2"],
      "milestone": "里程碑"
    }}
  ],
  "recommended_projects": [
    {{"name": "项目名称", "description": "描述", "tech_stack": ["技术"], "difficulty": "入门/中级/进阶"}}
  ],
  "recommended_resources": ["资源1", "资源2"],
  "interview_prep_tips": ["建议1", "建议2"],
  "expected_timeline": "预计达标时间"
}}
```"""


class JobMatchPrompts:
    """岗位匹配 Prompt 模板"""

    @staticmethod
    def build_user_prompt(
        name: str,
        user_skills: list[dict],
        user_projects: list[dict],
        job_title: str,
        job_description: str,
        job_requirements: str,
    ) -> str:
        skills_text = _format_skills(user_skills)
        projects_text = _format_projects(user_projects)

        return f"""请对以下学生的技能与岗位要求进行AI匹配分析。

### 学生信息
- 姓名：{name}
- 技能：{skills_text}
- 项目经历：{projects_text}

### 目标岗位
- 岗位名称：{job_title}
- 岗位描述：{job_description}
- 岗位要求：{job_requirements}

---

请分析匹配度并给出建议，输出以下JSON结构：

```json
{{
  "match_score": 匹配度0-100,
  "match_reason": "匹配理由（100字以内）",
  "matched_skills": ["已匹配的技能1", "已匹配的技能2"],
  "missing_skills": ["缺失的技能1", "缺失的技能2"],
  "learning_suggestions": [
    "学习建议1（具体可执行）",
    "学习建议2"
  ],
  "interview_focus": ["面试重点准备方向1", "面试重点准备方向2"]
}}
```"""


# ── 格式化辅助函数 ──

def _format_skills(skills: list[dict]) -> str:
    if not skills:
        return "（暂无填写技能）"
    lines = []
    for i, skill in enumerate(skills, 1):
        desc = f" - {skill.get('description', '')}" if skill.get('description') else ""
        lines.append(f"{i}. {skill['name']}（{skill['proficiency']}）{desc}")
    return "\n".join(lines)


def _format_projects(projects: list[dict]) -> str:
    if not projects:
        return "（暂无填写项目经历）"
    lines = []
    for i, proj in enumerate(projects, 1):
        tech = "、".join(proj.get('tech_stack', [])) if proj.get('tech_stack') else "未注明"
        lines.append(f"""项目{i}：{proj['name']}
- 担任角色：{proj['role']}
- 技术栈：{tech}
- 项目描述：{proj['description']}""")
    return "\n\n".join(lines)


def _format_competitions(competitions: list[dict]) -> str:
    if not competitions:
        return ""
    lines = ["\n### 竞赛经历"]
    for i, comp in enumerate(competitions, 1):
        lines.append(f"{i}. {comp['name']}（{comp.get('level', '')} - {comp.get('award', '')}）")
        if comp.get('description'):
            lines.append(f"   描述：{comp['description']}")
    return "\n".join(lines)


def _format_internships(internships: list[dict]) -> str:
    if not internships:
        return ""
    lines = ["\n### 实习经历"]
    for i, intern in enumerate(internships, 1):
        lines.append(f"{i}. {intern['company']} - {intern['position']}")
        if intern.get('description'):
            lines.append(f"   描述：{intern['description']}")
        tech = "、".join(intern.get('tech_stack', []))
        if tech:
            lines.append(f"   技术栈：{tech}")
    return "\n".join(lines)