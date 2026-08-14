"""
文件名称：growth_service.py
文件作用：成长规划业务逻辑层。
负责调用AI生成成长规划、保存规划记录、查询历史记录。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import SystemPrompts, GrowthPlanningPrompts
from app.models.growth import GrowthPlan
from app.models.user import User
from app.schemas.growth import (
    GrowthPlanRequest,
    GrowthPlanResponse,
    GrowthPlanResult,
    GrowthPlanHistoryItem,
    AbilityGap,
    LearningStage,
    RecommendedProject,
)
from app.utils.exceptions import ResourceNotFoundError


class GrowthService:
    """成长规划服务"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.ai_client = DeepSeekClient.instance()

    def generate_plan(self, request: GrowthPlanRequest) -> GrowthPlanResponse:
        """生成成长规划

        Args:
            request: 规划请求

        Returns:
            规划结果响应
        """
        # 获取用户信息
        user_info = self._resolve_user_info(request)

        # 构建Prompt
        system_prompt = SystemPrompts.growth_planner()
        user_prompt = GrowthPlanningPrompts.build_user_prompt(
            name=user_info["name"],
            major=user_info["major"],
            grade=user_info["grade"],
            target_job=request.target_job,
            skills=user_info["skills"],
            projects=user_info["projects"],
            profile_analysis=request.profile_analysis,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 调用AI
        ai_result = self.ai_client.chat_json(messages, temperature=0.4)

        # 解析结果
        result = self._parse_ai_result(ai_result)

        # 保存记录
        record = self._save_record(
            user_id=request.user_id,
            user_info=user_info,
            target_job=request.target_job,
            result=result,
            raw_result=ai_result,
        )

        return GrowthPlanResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=self.ai_client.is_mock_mode,
            created_at=record.created_at,
        )

    def get_plan(self, plan_id: int) -> GrowthPlanResponse:
        """获取单条规划记录详情

        Args:
            plan_id: 规划记录ID

        Returns:
            规划结果响应
        """
        record = self.db.get(GrowthPlan, plan_id)
        if not record:
            raise ResourceNotFoundError(f"规划记录 {plan_id} 不存在")

        result = GrowthPlanResult(
            current_situation=record.current_situation,
            ability_gaps=[AbilityGap(**g) for g in record.ability_gaps],
            learning_roadmap=[LearningStage(**s) for s in record.learning_roadmap],
            recommended_projects=[RecommendedProject(**p) for p in record.recommended_projects],
            recommended_resources=record.recommended_resources,
            interview_prep_tips=record.interview_prep_tips,
            expected_timeline=record.expected_timeline,
        )

        return GrowthPlanResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=False,
            created_at=record.created_at,
        )

    def get_user_plans(self, user_id: int) -> list[GrowthPlanHistoryItem]:
        """获取用户的历史规划记录列表

        Args:
            user_id: 用户ID

        Returns:
            历史记录列表
        """
        stmt = (
            select(GrowthPlan)
            .where(GrowthPlan.user_id == user_id)
            .order_by(GrowthPlan.created_at.desc())
        )
        records = self.db.scalars(stmt).all()

        return [
            GrowthPlanHistoryItem(
                id=r.id,
                user_id=r.user_id,
                target_job=r.target_job,
                expected_timeline=r.expected_timeline,
                created_at=r.created_at,
            )
            for r in records
        ]

    def _resolve_user_info(self, request: GrowthPlanRequest) -> dict:
        """解析用户信息

        Args:
            request: 规划请求

        Returns:
            用户信息字典
        """
        if request.user_id:
            user = self.db.get(User, request.user_id)
            if not user:
                raise ResourceNotFoundError(f"用户 {request.user_id} 不存在")

            return {
                "name": user.name,
                "major": user.major,
                "grade": user.grade,
                "skills": [
                    {"name": s.name, "proficiency": s.proficiency, "description": s.description}
                    for s in user.skills
                ],
                "projects": [
                    {
                        "name": p.name,
                        "role": p.role,
                        "description": p.description,
                        "tech_stack": p.tech_stack or [],
                    }
                    for p in user.projects
                ],
            }

        return {
            "name": request.name or "同学",
            "major": request.major or "计算机相关专业",
            "grade": request.grade or "未填写",
            "skills": request.skills or [],
            "projects": request.projects or [],
        }

    def _parse_ai_result(self, ai_result: dict) -> GrowthPlanResult:
        """解析AI返回的结果

        Args:
            ai_result: AI返回的JSON字典

        Returns:
            解析后的规划结果
        """
        ability_gaps = [
            AbilityGap(
                skill=g.get("skill", "未知技能"),
                importance=g.get("importance", "加分"),
                difficulty=g.get("difficulty", "中"),
                description=g.get("description", ""),
            )
            for g in ai_result.get("ability_gaps", [])
        ]

        learning_roadmap = [
            LearningStage(
                stage=s.get("stage", f"阶段{i+1}"),
                focus=s.get("focus", ""),
                tasks=s.get("tasks", [])[:5],
                milestone=s.get("milestone", ""),
            )
            for i, s in enumerate(ai_result.get("learning_roadmap", []))
        ]

        recommended_projects = [
            RecommendedProject(
                name=p.get("name", "实战项目"),
                description=p.get("description", ""),
                tech_stack=p.get("tech_stack", []),
                difficulty=p.get("difficulty", "中级"),
            )
            for p in ai_result.get("recommended_projects", [])
        ]

        return GrowthPlanResult(
            current_situation=ai_result.get("current_situation", "请继续完善技能和项目经历"),
            ability_gaps=ability_gaps,
            learning_roadmap=learning_roadmap,
            recommended_projects=recommended_projects,
            recommended_resources=ai_result.get("recommended_resources", [])[:5],
            interview_prep_tips=ai_result.get("interview_prep_tips", [])[:5],
            expected_timeline=ai_result.get("expected_timeline", "3-6个月"),
        )

    def _save_record(
        self,
        user_id: Optional[int],
        user_info: dict,
        target_job: str,
        result: GrowthPlanResult,
        raw_result: dict,
    ) -> GrowthPlan:
        """保存规划记录到数据库

        Args:
            user_id: 用户ID
            user_info: 用户信息
            target_job: 目标岗位
            result: 解析后的结果
            raw_result: 原始AI返回

        Returns:
            保存后的记录
        """
        record = GrowthPlan(
            user_id=user_id,
            input_name=user_info["name"],
            input_major=user_info["major"],
            input_grade=user_info["grade"],
            target_job=target_job,
            current_situation=result.current_situation,
            ability_gaps=[g.model_dump() for g in result.ability_gaps],
            learning_roadmap=[s.model_dump() for s in result.learning_roadmap],
            recommended_projects=[p.model_dump() for p in result.recommended_projects],
            recommended_resources=result.recommended_resources,
            interview_prep_tips=result.interview_prep_tips,
            expected_timeline=result.expected_timeline,
            raw_result=raw_result,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
