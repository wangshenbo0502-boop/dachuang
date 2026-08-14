"""
文件名称：analysis_service.py
文件作用：就业画像分析业务逻辑层。
负责调用AI进行画像分析、保存分析记录、查询历史记录。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import SystemPrompts, ProfileAnalysisPrompts
from app.models.analysis import ProfileAnalysis
from app.models.user import User
from app.schemas.analysis import (
    ProfileAnalysisRequest,
    ProfileAnalysisResult,
    ProfileAnalysisResponse,
    ProfileAnalysisHistoryItem,
    RecommendedDirection,
    SkillAssessment,
)
from app.utils.exceptions import ResourceNotFoundError


class AnalysisService:
    """就业画像分析服务"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.ai_client = DeepSeekClient.instance()

    def analyze_profile(self, request: ProfileAnalysisRequest) -> ProfileAnalysisResponse:
        """执行就业画像分析

        Args:
            request: 分析请求

        Returns:
            分析结果响应
        """
        # 获取用户信息
        user_info = self._resolve_user_info(request)

        # 构建Prompt
        system_prompt = SystemPrompts.profile_analyst()
        user_prompt = ProfileAnalysisPrompts.build_user_prompt(
            name=user_info["name"],
            school=user_info["school"],
            major=user_info["major"],
            grade=user_info["grade"],
            bio=user_info["bio"],
            skills=user_info["skills"],
            projects=user_info["projects"],
            target_job=request.target_job or "",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 调用AI
        ai_result = self.ai_client.chat_json(messages, temperature=0.3)

        # 解析结果
        result = self._parse_ai_result(ai_result)

        # 保存记录
        record = self._save_record(
            user_id=request.user_id,
            user_info=user_info,
            target_job=request.target_job or "",
            result=result,
            raw_result=ai_result,
        )

        return ProfileAnalysisResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=self.ai_client.is_mock_mode,
            created_at=record.created_at,
        )

    def get_analysis(self, analysis_id: int) -> ProfileAnalysisResponse:
        """获取单条分析记录详情

        Args:
            analysis_id: 分析记录ID

        Returns:
            分析结果响应
        """
        record = self.db.get(ProfileAnalysis, analysis_id)
        if not record:
            raise ResourceNotFoundError(f"分析记录 {analysis_id} 不存在")

        result = ProfileAnalysisResult(
            profile_summary=record.profile_summary,
            technical_direction=record.technical_direction,
            core_advantages=record.core_advantages,
            current_level=record.current_level,
            recommended_directions=[
                RecommendedDirection(**d) for d in record.recommended_directions
            ],
            areas_to_improve=record.areas_to_improve,
            comprehensive_score=record.comprehensive_score,
            skill_assessment=SkillAssessment(**record.skill_assessment),
        )

        return ProfileAnalysisResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=False,
            created_at=record.created_at,
        )

    def get_user_analyses(self, user_id: int) -> list[ProfileAnalysisHistoryItem]:
        """获取用户的历史分析记录列表

        Args:
            user_id: 用户ID

        Returns:
            历史记录列表
        """
        stmt = (
            select(ProfileAnalysis)
            .where(ProfileAnalysis.user_id == user_id)
            .order_by(ProfileAnalysis.created_at.desc())
        )
        records = self.db.scalars(stmt).all()

        return [
            ProfileAnalysisHistoryItem(
                id=r.id,
                user_id=r.user_id,
                target_job=r.target_job,
                technical_direction=r.technical_direction,
                comprehensive_score=r.comprehensive_score,
                created_at=r.created_at,
            )
            for r in records
        ]

    def _resolve_user_info(self, request: ProfileAnalysisRequest) -> dict:
        """解析用户信息，优先使用user_id从数据库获取，否则使用请求中直接传入的信息

        Args:
            request: 分析请求

        Returns:
            用户信息字典
        """
        if request.user_id:
            user = self.db.get(User, request.user_id)
            if not user:
                raise ResourceNotFoundError(f"用户 {request.user_id} 不存在")

            return {
                "name": user.name,
                "school": user.school,
                "major": user.major,
                "grade": user.grade,
                "bio": user.bio,
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

        # 使用请求中直接传入的信息
        return {
            "name": request.name or "同学",
            "school": request.school or "未填写",
            "major": request.major or "未填写",
            "grade": request.grade or "未填写",
            "bio": request.bio or "",
            "skills": request.skills or [],
            "projects": request.projects or [],
        }

    def _parse_ai_result(self, ai_result: dict) -> ProfileAnalysisResult:
        """解析AI返回的结果为Pydantic模型

        Args:
            ai_result: AI返回的JSON字典

        Returns:
            解析后的分析结果
        """
        # 设置默认值防止AI返回字段缺失
        skill_assessment_data = ai_result.get("skill_assessment", {})
        skill_assessment = SkillAssessment(
            programming_foundation=skill_assessment_data.get("programming_foundation", 60),
            framework_usage=skill_assessment_data.get("framework_usage", 50),
            database_skill=skill_assessment_data.get("database_skill", 50),
            engineering_practice=skill_assessment_data.get("engineering_practice", 40),
            project_experience=skill_assessment_data.get("project_experience", 40),
        )

        recommended_directions = [
            RecommendedDirection(
                job_title=d.get("job_title", "未知岗位"),
                match_rate=d.get("match_rate", 50),
            )
            for d in ai_result.get("recommended_directions", [])
        ]

        return ProfileAnalysisResult(
            profile_summary=ai_result.get("profile_summary", "暂无分析结果"),
            technical_direction=ai_result.get("technical_direction", "待确定"),
            core_advantages=ai_result.get("core_advantages", [])[:5],
            current_level=ai_result.get("current_level", "入门阶段"),
            recommended_directions=recommended_directions,
            areas_to_improve=ai_result.get("areas_to_improve", [])[:5],
            comprehensive_score=ai_result.get("comprehensive_score", 50),
            skill_assessment=skill_assessment,
        )

    def _save_record(
        self,
        user_id: Optional[int],
        user_info: dict,
        target_job: str,
        result: ProfileAnalysisResult,
        raw_result: dict,
    ) -> ProfileAnalysis:
        """保存分析记录到数据库

        Args:
            user_id: 用户ID
            user_info: 用户信息
            target_job: 目标岗位
            result: 解析后的结果
            raw_result: 原始AI返回

        Returns:
            保存后的记录
        """
        record = ProfileAnalysis(
            user_id=user_id,
            input_name=user_info["name"],
            input_school=user_info["school"],
            input_major=user_info["major"],
            input_grade=user_info["grade"],
            target_job=target_job,
            profile_summary=result.profile_summary,
            technical_direction=result.technical_direction,
            core_advantages=result.core_advantages,
            current_level=result.current_level,
            recommended_directions=[d.model_dump() for d in result.recommended_directions],
            areas_to_improve=result.areas_to_improve,
            comprehensive_score=result.comprehensive_score,
            skill_assessment=result.skill_assessment.model_dump(),
            raw_result=raw_result,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
