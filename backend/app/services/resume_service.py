"""
文件名称：resume_service.py
文件作用：简历优化业务逻辑层。
负责调用AI进行简历优化、保存优化记录、查询历史记录。
"""

from typing import Optional
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import SystemPrompts, ResumeOptimizationPrompts
from app.models.resume import Resume, ResumeOptimization
from app.models.user import User
from app.knowledge.rag_integration import augment_prompt
from app.schemas.resume import (
    ResumeOptimizationRequest,
    ResumeOptimizationResponse,
    ResumeOptimizationResult,
    ResumeOptimizationHistoryItem,
    ResumeVersionCreate, ResumeVersionUpdate, ResumeVersionResponse,
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
        system_prompt += "\n只能改写输入事实，不得新增数字、技术、职责或获奖；缺少结果应提示补充。外部知识不是用户经历。"
        user_prompt = ResumeOptimizationPrompts.build_user_prompt(
            name=user_info["name"],
            target_job=request.target_job,
            skills=user_info["skills"],
            projects=user_info["projects"],
            original_resume=request.original_resume or "",
        )
        skill_names = [str(item.get("name", "")) for item in user_info["skills"] if isinstance(item, dict)]
        project_names = [str(item.get("name", "")) for item in user_info["projects"] if isinstance(item, dict)]
        rag_query = " ".join(
            value for value in [
                request.target_job,
                *skill_names,
                *project_names,
                "简历 项目经历 技能关键词 STAR",
            ] if value
        )
        user_prompt, sources = augment_prompt(rag_query, user_prompt, top_k=5)
        if request.job_id:
            from app.services.job_match_service import JobMatchService
            job = JobMatchService.instance().get_job_detail(request.job_id)
            if job:
                user_prompt += f"\n### 目标岗位要求（仅用于对照，不得写成用户已有经历）\n{job.content[:6000]}"

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
            raw_result={"answer": ai_result, "sources": sources},
        )

        return ResumeOptimizationResponse(
            id=record.id,
            user_id=record.user_id,
            target_job=record.target_job,
            result=result,
            is_mock=self.ai_client.is_mock_mode,
            created_at=record.created_at,
        )

    def create_version(self, request: ResumeVersionCreate) -> ResumeVersionResponse:
        user = self.db.get(User, request.user_id)
        if not user:
            raise ResourceNotFoundError(f"用户 {request.user_id} 不存在")
        record = Resume(profile_id=user.id, user_id=user.id, **request.model_dump(exclude={"user_id"}))
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._version_response(record, user)

    def list_versions(self, user_id: int) -> list[ResumeVersionResponse]:
        user = self.db.get(User, user_id)
        if not user:
            raise ResourceNotFoundError(f"用户 {user_id} 不存在")
        records = self.db.scalars(select(Resume).where(Resume.user_id == user_id).order_by(Resume.updated_at.desc())).all()
        return [self._version_response(record, user) for record in records]

    def get_version(self, version_id: int) -> ResumeVersionResponse:
        record = self.db.get(Resume, version_id)
        if not record:
            raise ResourceNotFoundError(f"简历版本 {version_id} 不存在")
        user = self.db.get(User, record.profile_id)
        return self._version_response(record, user)

    def update_version(self, version_id: int, request: ResumeVersionUpdate) -> ResumeVersionResponse:
        record = self.db.get(Resume, version_id)
        if not record:
            raise ResourceNotFoundError(f"简历版本 {version_id} 不存在")
        for field, value in request.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return self._version_response(record, self.db.get(User, record.profile_id))

    def _version_response(self, record: Resume, user: User) -> ResumeVersionResponse:
        """按引用 ID 从就业档案实时组装，确保档案更新后简历不会产生副本。"""
        project_ids = set(record.selected_projects or [])
        skill_ids = set(record.selected_skills or [])
        experience_ids = {key: set(value or []) for key, value in (record.selected_experiences or {}).items()}
        profile = {
            "name": user.name, "school": user.school, "major": user.major, "grade": user.grade,
            "bio": user.bio, "email": user.email, "phone": user.phone,
            "skills": [self._model_dict(item) for item in user.skills if item.id in skill_ids],
            "projects": [self._model_dict(item) for item in user.projects if item.id in project_ids],
            "competitions": [self._model_dict(item) for item in user.competitions if item.id in experience_ids.get("competitions", set())],
            "internships": [self._model_dict(item) for item in user.internships if item.id in experience_ids.get("internships", set())],
        }
        return ResumeVersionResponse(
            id=record.id, user_id=record.user_id, name=record.name, target_job=record.target_job,
            profile_id=record.profile_id, selected_projects=record.selected_projects or [],
            selected_skills=record.selected_skills or [], selected_experiences=record.selected_experiences or {},
            personal_summary=record.personal_summary, optimized_content=record.optimized_content or {}, template=record.template, status=record.status,
            profile=profile, created_at=record.created_at, updated_at=record.updated_at,
        )

    @staticmethod
    def _model_dict(item) -> dict:
        return {column.name: getattr(item, column.name) for column in item.__table__.columns}

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

            selected_project_ids = set(request.selected_project_ids) if request.selected_project_ids is not None else None
            selected_skill_ids = set(request.selected_skill_ids) if request.selected_skill_ids is not None else None
            return {
                "name": user.name,
                "skills": [
                    {"name": s.name, "proficiency": s.proficiency, "description": s.description}
                    for s in user.skills if selected_skill_ids is None or s.id in selected_skill_ids
                ],
                "projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "role": p.role,
                        "description": p.description,
                        "tech_stack": p.tech_stack or [],
                    }
                    for p in user.projects if selected_project_ids is None or p.id in selected_project_ids
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
        ai_projects = self._dict_list(ai_result.get("optimized_projects"))
        user_projects = user_info.get("projects", [])

        # 确保每个项目都有结果
        for i, proj in enumerate(user_projects):
            name = proj.get("name", f"项目{i+1}")
            candidates = [item for item in ai_projects if item.get("project_name") == name]
            ai_proj = candidates[0] if len(candidates) == 1 else {}
            original = proj.get("description", "")
            optimized = self._text(ai_proj.get("optimized"), original)
            facts = " ".join([name, original, str(proj.get("role", "")), *proj.get("tech_stack", [])])
            warnings = []
            if self._new_numbers(optimized, facts):
                optimized = original
                warnings.append("检测到原始经历中不存在的数字，已保留原文")
            if not re.search(r"\d", original):
                warnings.append("结果数据待补充：实际规模、测试结果或使用反馈")
            if not ai_proj:
                warnings.append("未找到唯一对应的项目改写，已保留原文")
            optimized_projects.append(OptimizedProject(
                project_name=name, original=original, optimized=optimized,
                source_experience_id=proj.get("id"),
                highlight_tags=proj.get("tech_stack", []),
                fact_warnings=warnings,
            ))

        # 处理优化后的技能
        optimized_skills = []
        ai_skills = self._dict_list(ai_result.get("optimized_skills"))
        user_skills = user_info.get("skills", [])

        for i, skill in enumerate(user_skills):
            if i < len(ai_skills):
                ai_skill = ai_skills[i]
                optimized_skills.append(OptimizedSkill(
                    original=skill.get("name", ""),
                    optimized=self._text(ai_skill.get("optimized"), skill.get("name", "")),
                ))
            else:
                optimized_skills.append(OptimizedSkill(
                    original=skill.get("name", ""),
                    optimized=f"{skill.get('name', '')}（{skill.get('proficiency', '掌握')}）",
                ))

        summary = self._text(ai_result.get("personal_summary"))
        source_facts = str(user_info)
        if self._new_numbers(summary, source_facts):
            summary = ""
        return ResumeOptimizationResult(
            optimized_projects=optimized_projects,
            optimized_skills=optimized_skills,
            overall_suggestions=self._string_list(ai_result.get("overall_suggestions"))[:5],
            personal_summary=summary,
            resume_score=self._score(ai_result.get("resume_score"), 60),
        )

    @staticmethod
    def _new_numbers(text: str, facts: str) -> set[str]:
        pattern = r"\d+(?:\.\d+)?(?:%|％|万|亿)?"
        return set(re.findall(pattern, text)) - set(re.findall(pattern, facts))

    @staticmethod
    def _dict_list(value: object) -> list[dict]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    @staticmethod
    def _string_list(value: object) -> list[str]:
        return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []

    @staticmethod
    def _text(value: object, fallback: str = "") -> str:
        return value.strip() if isinstance(value, str) else fallback

    @staticmethod
    def _score(value: object, fallback: int) -> int:
        try:
            score = int(float(value))
        except (TypeError, ValueError):
            return fallback
        return max(0, min(100, score))

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
