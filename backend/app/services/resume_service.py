"""
文件名称：resume_service.py
文件作用：简历优化业务逻辑层。
负责调用AI进行简历优化、保存优化记录、查询历史记录。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import SystemPrompts, ResumeOptimizationPrompts
from app.models.resume import ResumeOptimization
from app.models.user import User
from app.schemas.resume import (
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    ResumeOptimizationResult,
    ResumeOptimizationHistoryItem,
    OptimizedProject,
    OptimizedSkill,
)
from app.utils.exceptions import ResourceNotFoundError


class ResumeService:
    """简历优化服务"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.ai_client = DeepSeekClient.instance()

    def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """执行简历优化

        Args:
            request: 优化请求

        Returns:
            优化结果响应
        """
        # 获取用户信息
        user_info = self._resolve_user_info(request)

        # 构建Prompt
        system_prompt = SystemPrompts.resume_optimizer()
        user_prompt = ResumeOptimizationPrompts.build_user_prompt(
            name=user_info["name"],
            target_job=request.target_job,
            skills=user_info["skills"],
            projects=user_info["projects"],
            original_resume=request.original_resume or "",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 调用AI
        ai_result = self.ai_client.chat_json(messages, temperature=0.4)

        # 解析结果
        result = self._parse_ai_result(ai_result, user_info)

        # 保存记录
        record = self._save_record(
            user_id=request.user_id,
            name=user_info["name"],
            target_job=request.target_job,
            original_resume=request.original_resume or "",
            result=result,
            raw_result=ai_result,
        )

        return ResumeOptimizationResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=self.ai_client.is_mock_mode,
            created_at=record.created_at,
        )

    def get_optimization(self, optimization_id: int) -> ResumeOptimizationResponse:
        """获取单条优化记录详情

        Args:
            optimization_id: 优化记录ID

        Returns:
            优化结果响应
        """
        record = self.db.get(ResumeOptimization, optimization_id)
        if not record:
            raise ResourceNotFoundError(f"优化记录 {optimization_id} 不存在")

        result = ResumeOptimizationResult(
            optimized_projects=[OptimizedProject(**p) for p in record.optimized_projects],
            optimized_skills=[OptimizedSkill(**s) for s in record.optimized_skills],
            overall_suggestions=record.overall_suggestions,
            personal_summary=record.personal_summary,
            resume_score=record.resume_score,
        )

        return ResumeOptimizationResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=False,
            created_at=record.created_at,
        )

    def get_user_optimizations(self, user_id: int) -> list[ResumeOptimizationHistoryItem]:
        """获取用户的历史优化记录列表

        Args:
            user_id: 用户ID

        Returns:
            历史记录列表
        """
        stmt = (
            select(ResumeOptimization)
            .where(ResumeOptimization.user_id == user_id)
            .order_by(ResumeOptimization.created_at.desc())
        )
        records = self.db.scalars(stmt).all()

        return [
            ResumeOptimizationHistoryItem(
                id=r.id,
                user_id=r.user_id,
                target_job=r.target_job,
                resume_score=r.resume_score,
                created_at=r.created_at,
            )
            for r in records
        ]

    def _resolve_user_info(self, request: ResumeOptimizationRequest) -> dict:
        """解析用户信息

        Args:
            request: 优化请求

        Returns:
            用户信息字典
        """
        if request.user_id:
            user = self.db.get(User, request.user_id)
            if not user:
                raise ResourceNotFoundError(f"用户 {request.user_id} 不存在")

            return {
                "name": user.name,
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
            "skills": request.skills or [],
            "projects": request.projects or [],
        }

    def _parse_ai_result(self, ai_result: dict, user_info: dict) -> ResumeOptimizationResult:
        """解析AI返回的结果

        Args:
            ai_result: AI返回的JSON字典
            user_info: 用户信息

        Returns:
            解析后的优化结果
        """
        # 处理优化后的项目
        optimized_projects = []
        ai_projects = ai_result.get("optimized_projects", [])
        user_projects = user_info.get("projects", [])

        # 确保每个项目都有结果
        for i, proj in enumerate(user_projects):
            if i < len(ai_projects):
                ai_proj = ai_projects[i]
                optimized_projects.append(OptimizedProject(
                    project_name=ai_proj.get("project_name", proj.get("name", f"项目{i+1}")),
                    original=ai_proj.get("original", proj.get("description", "")),
                    optimized=ai_proj.get("optimized", proj.get("description", "")),
                    highlight_tags=ai_proj.get("highlight_tags", []),
                ))
            else:
                optimized_projects.append(OptimizedProject(
                    project_name=proj.get("name", f"项目{i+1}"),
                    original=proj.get("description", ""),
                    optimized=proj.get("description", ""),
                    highlight_tags=proj.get("tech_stack", []),
                ))

        # 处理优化后的技能
        optimized_skills = []
        ai_skills = ai_result.get("optimized_skills", [])
        user_skills = user_info.get("skills", [])

        for i, skill in enumerate(user_skills):
            if i < len(ai_skills):
                ai_skill = ai_skills[i]
                optimized_skills.append(OptimizedSkill(
                    original=ai_skill.get("original", skill.get("name", "")),
                    optimized=ai_skill.get("optimized", skill.get("name", "")),
                ))
            else:
                optimized_skills.append(OptimizedSkill(
                    original=skill.get("name", ""),
                    optimized=f"{skill.get('name', '')}（{skill.get('proficiency', '掌握')}）",
                ))

        return ResumeOptimizationResult(
            optimized_projects=optimized_projects,
            optimized_skills=optimized_skills,
            overall_suggestions=ai_result.get("overall_suggestions", [])[:5],
            personal_summary=ai_result.get("personal_summary", ""),
            resume_score=ai_result.get("resume_score", 60),
        )

    def _save_record(
        self,
        user_id: Optional[int],
        name: str,
        target_job: str,
        original_resume: str,
        result: ResumeOptimizationResult,
        raw_result: dict,
    ) -> ResumeOptimization:
        """保存优化记录到数据库

        Args:
            user_id: 用户ID
            name: 用户姓名
            target_job: 目标岗位
            original_resume: 原始简历
            result: 解析后的结果
            raw_result: 原始AI返回

        Returns:
            保存后的记录
        """
        record = ResumeOptimization(
            user_id=user_id,
            input_name=name,
            target_job=target_job,
            original_resume=original_resume,
            optimized_projects=[p.model_dump() for p in result.optimized_projects],
            optimized_skills=[s.model_dump() for s in result.optimized_skills],
            overall_suggestions=result.overall_suggestions,
            personal_summary=result.personal_summary,
            resume_score=result.resume_score,
            raw_result=raw_result,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
