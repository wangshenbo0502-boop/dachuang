"""
文件名称：deepseek_client.py
文件作用：DeepSeek API 调用客户端，封装 API 请求与响应处理。
使用 OpenAI 兼容 SDK 调用 DeepSeek API。
支持重试机制、外部Prompt加载、动态Mock数据。
"""

import json
import os
import re
import time
import random
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, APIConnectionError

load_dotenv()

# 知识库Prompt目录
PROMPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "prompts"


class DeepSeekClient:
    """DeepSeek API 客户端（单例模式）

    特性：
    - 支持外部Markdown Prompt文件加载
    - 3次指数退避重试
    - 区分不同错误类型
    - 动态Mock数据生成
    """

    _instance: Optional["DeepSeekClient"] = None

    def __init__(self) -> None:
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.timeout = float(os.getenv("AI_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("AI_MAX_RETRIES", "3"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))

        if not api_key or api_key == "your_deepseek_api_key_here":
            self._client = None
            self._mock_mode = True
        else:
            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.timeout,
            )
            self._mock_mode = False

    @classmethod
    def instance(cls) -> "DeepSeekClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（用于测试或配置变更后重连）"""
        cls._instance = None

    @property
    def is_mock_mode(self) -> bool:
        return self._mock_mode

    # ─── Prompt 加载 ───

    @staticmethod
    def load_prompt(filename: str) -> str:
        """从 knowledge/prompts/ 目录加载Prompt文件

        Args:
            filename: 文件名（如 "system_profile_analyst.md"）

        Returns:
            文件内容，如果文件不存在则返回空字符串
        """
        prompt_path = PROMPT_DIR / filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8").strip()
        return ""

    # ─── 核心调用 ───

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = None,
        max_tokens: int = 4000,
        response_format: Optional[dict[str, str]] = None,
    ) -> str:
        """发送对话请求并返回响应文本（带重试）

        Args:
            messages: 消息列表
            temperature: 温度参数（None则用默认值）
            max_tokens: 最大生成token数
            response_format: 响应格式

        Returns:
            AI 响应的文本内容
        """
        if self._mock_mode:
            return self._mock_response(messages)

        if temperature is None:
            temperature = self.temperature

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if response_format:
            kwargs["response_format"] = response_format

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.chat.completions.create(**kwargs)
                return response.choices[0].message.content or ""
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait = (2 ** attempt) * 2 + random.uniform(0, 1)
                    time.sleep(wait)
            except (APITimeoutError, APIConnectionError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(1 + attempt)
            except APIError as e:
                # 非重试型错误（如401鉴权失败、400参数错误）直接抛出
                raise AIServiceError(
                    f"AI API错误: {e.status_code or '?'} - {str(e)}",
                    error_type=AIServiceError.TYPE_API_ERROR,
                ) from e
            except Exception as e:
                raise AIServiceError(f"AI 服务调用失败: {str(e)}") from e

        raise AIServiceError(
            f"AI调用重试{self.max_retries}次后仍失败: {str(last_error)}",
            error_type=AIServiceError.TYPE_RETRY_EXHAUSTED,
        )

    def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> dict:
        """发送对话请求并解析为JSON"""
        json_instruction = {
            "role": "system",
            "content": "你必须严格以JSON格式返回结果，不要包含任何markdown格式标记（如```json），直接返回纯JSON字符串。",
        }
        enhanced_messages = [json_instruction] + messages

        response_text = self.chat(
            enhanced_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        return self._parse_json(response_text)

    def _parse_json(self, text: str) -> dict:
        """解析AI返回的JSON文本，增强容错"""
        text = re.sub(r"^```json\s*", "", text.strip())
        text = re.sub(r"\s*```$", "", text.strip())

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试修复常见问题：截取第一个{到最后一个}
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
            raise AIServiceError(
                f"AI 响应JSON解析失败，响应内容: {text[:300]}",
                error_type=AIServiceError.TYPE_PARSE_ERROR,
            )

    # ─── 动态Mock数据 ───

    def _mock_response(self, messages: list[dict[str, str]]) -> str:
        """模拟模式响应，根据用户输入动态生成更贴切的演示数据"""
        last_user_msg = ""
        skills_in_msg: list[str] = []
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        # 提取用户消息中的技能名
        skill_pattern = re.findall(r'"name":\s*"([^"]+)"|技能[：:]\s*(.+)|- (\w+)', last_user_msg)
        for match in skill_pattern:
            for g in match:
                if g and len(g) > 1:
                    skills_in_msg.append(g)

        if "就业画像" in last_user_msg or "profile" in last_user_msg.lower():
            return json.dumps(self._mock_profile_result(skills_in_msg), ensure_ascii=False)
        elif "简历" in last_user_msg or "resume" in last_user_msg.lower():
            return json.dumps(self._mock_resume_result(skills_in_msg), ensure_ascii=False)
        elif "成长" in last_user_msg or "growth" in last_user_msg.lower() or "学习路线" in last_user_msg or "学习计划" in last_user_msg:
            return json.dumps(self._mock_growth_result(skills_in_msg), ensure_ascii=False)
        elif "岗位" in last_user_msg or "匹配" in last_user_msg or "job" in last_user_msg.lower():
            return json.dumps(self._mock_job_match_result(skills_in_msg), ensure_ascii=False)
        else:
            return json.dumps({"message": "模拟模式响应，请配置DEEPSEEK_API_KEY以获得真实AI分析"}, ensure_ascii=False)

    def _mock_profile_result(self, skills: list[str] = None) -> dict:
        sk = skills or ["Java", "SpringBoot", "MySQL"]
        return {
            "profile_summary": f"该学生具备{'、'.join(sk[:3])}等技术基础，有项目实践经验，但在企业级技术和工程经验方面仍有提升空间。",
            "technical_direction": "后端开发" if any("java" in s.lower() for s in sk) else "全栈开发",
            "core_advantages": [
                f"掌握{'、'.join(sk[:2])}，具备开发基础能力",
                "有数据库设计和项目开发经验",
                "学习态度积极，有项目实践经历"
            ],
            "current_level": "初级开发工程师（校招入门水平）",
            "recommended_directions": [
                {"job_title": "Java后端开发工程师", "match_rate": 75},
                {"job_title": "全栈开发工程师", "match_rate": 60},
                {"job_title": "大数据开发工程师", "match_rate": 45}
            ],
            "areas_to_improve": [
                "Redis缓存、消息队列等中间件使用经验",
                "微服务架构和分布式系统知识",
                "企业级项目经验和代码规范"
            ],
            "comprehensive_score": 68,
            "skill_assessment": {
                "programming_foundation": 75,
                "framework_usage": 70,
                "database_skill": 65,
                "engineering_practice": 50,
                "project_experience": 55
            }
        }

    def _mock_resume_result(self, skills: list[str] = None) -> dict:
        sk = skills or ["Java", "SpringBoot"]
        return {
            "optimized_projects": [
                {
                    "project_name": "校园管理系统",
                    "original": "负责后端接口开发，使用SpringBoot框架",
                    "optimized": f"基于SpringBoot + MySQL构建校园管理系统，独立设计并开发用户管理、课程管理等核心RESTful API接口，实现数据校验与异常处理，接口响应时间<200ms。",
                    "highlight_tags": ["SpringBoot", "MySQL", "RESTful API", "后端开发"]
                }
            ],
            "optimized_skills": [
                {"original": sk[0] if sk else "Java", "optimized": f"熟练掌握{sk[0] if sk else 'Java'}编程语言，熟悉集合框架、多线程、JVM基础"},
                {"original": sk[1] if len(sk) > 1 else "SpringBoot", "optimized": f"熟悉{sk[1] if len(sk) > 1 else 'SpringBoot'}框架，能够快速搭建RESTful API服务"}
            ],
            "overall_suggestions": [
                "项目描述建议使用STAR法则，突出个人贡献和技术难点",
                "技能描述建议区分精通/熟悉/了解三个层次",
                "建议添加量化成果，如系统QPS、数据量等"
            ],
            "personal_summary": f"计算机专业学生，具备{'、'.join(sk[:2])}等技能基础，有实际项目开发经验，对后端开发有浓厚兴趣，期望在软件开发领域持续成长。",
            "resume_score": 72
        }

    def _mock_growth_result(self, skills: list[str] = None) -> dict:
        sk = skills or ["Java"]
        return {
            "current_situation": f"具备{'、'.join(sk)}基础，能够完成简单项目开发",
            "ability_gaps": [
                {"skill": "Redis", "importance": "必须", "difficulty": "低", "description": "缓存中间件，企业必备技能"},
                {"skill": "Spring Cloud", "importance": "加分", "difficulty": "中", "description": "微服务框架，中高级岗位要求"},
                {"skill": "消息队列", "importance": "加分", "difficulty": "中", "description": "Kafka/RabbitMQ，异步处理必备"}
            ],
            "learning_roadmap": [
                {
                    "stage": "第一阶段（1-2个月）",
                    "focus": "夯实基础 + 中间件入门",
                    "tasks": [
                        "深入学习Java并发编程和JVM",
                        "掌握Redis常用数据结构和应用场景",
                        "学习MySQL索引优化和SQL调优"
                    ],
                    "milestone": "能够独立完成一个带缓存的后端项目"
                },
                {
                    "stage": "第二阶段（2-3个月）",
                    "focus": "微服务与工程实践",
                    "tasks": [
                        "学习Spring Cloud Alibaba微服务栈",
                        "了解消息队列（RabbitMQ/Kafka）使用",
                        "学习Git协作和代码规范"
                    ],
                    "milestone": "完成一个微服务架构的实战项目"
                },
                {
                    "stage": "第三阶段（持续）",
                    "focus": "面试准备与项目打磨",
                    "tasks": [
                        "刷LeetCode算法题（200道+）",
                        "准备项目亮点和技术难点",
                        "模拟面试练习"
                    ],
                    "milestone": "通过校招拿到满意offer"
                }
            ],
            "recommended_projects": [
                {
                    "name": "在线面试题库系统",
                    "description": "构建一个支持题目管理、在线答题、自动评分的面试题库平台",
                    "tech_stack": ["SpringBoot", "Redis", "MySQL", "Vue"],
                    "difficulty": "中级"
                }
            ],
            "recommended_resources": [
                "《Java并发编程实战》",
                "《Redis设计与实现》",
                "Spring官方文档",
                "牛客网/LeetCode刷题"
            ],
            "interview_prep_tips": [
                "准备2-3个项目的深度介绍",
                "整理常见面试题的回答思路",
                "模拟面试练习"
            ],
            "expected_timeline": "3-6个月可达到校招中级水平"
        }

    def _mock_job_match_result(self, skills: list[str] = None) -> dict:
        sk = skills or ["Java"]
        return {
            "match_analysis": f"基于用户的{'、'.join(sk)}技能，最适合的方向是后端开发。建议优先投递Java后端相关的校招岗位。",
            "competitiveness_level": "中等偏上",
            "detailed_matches": [
                {
                    "job_id": "java-backend",
                    "job_title": "Java后端开发工程师",
                    "match_score": 75,
                    "match_reason": f"用户掌握{sk[0] if sk else 'Java'}等核心技能，与岗位要求高度匹配",
                    "matched_skills": sk[:2] if len(sk) >= 2 else sk,
                    "missing_skills": ["Redis", "Spring Cloud", "消息队列"],
                    "learning_suggestions": [
                        "优先学习Redis，掌握常用数据结构和缓存策略",
                        "了解Spring Cloud微服务基础概念",
                        "学习一种消息队列（推荐RabbitMQ入门）"
                    ]
                }
            ]
        }


class AIServiceError(Exception):
    """AI 服务异常，区分不同错误类型"""

    TYPE_API_ERROR = "api_error"
    TYPE_RETRY_EXHAUSTED = "retry_exhausted"
    TYPE_PARSE_ERROR = "parse_error"
    TYPE_UNKNOWN = "unknown"

    def __init__(
        self,
        message: str = "AI服务调用失败",
        error_type: str = TYPE_UNKNOWN,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type