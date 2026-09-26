"""
文件名称：user_service.py
文件作用：处理学生资料、技能、项目经历、竞赛经历和实习经历的数据读写与 AI 上下文聚合。
"""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.user import User, UserProject, UserSkill, UserCompetition, UserInternship
from app.schemas.user import (
    StudentContextResponse,
    UserCreate,
    UserProjectsReplace,
    UserSkillsReplace,
    UserCompetitionsReplace,
    UserInternshipsReplace,
    UserUpdate,
)
from app.utils.exceptions import ResourceNotFoundError


class UserService:
    """学生资料领域的业务服务。"""

    def __init__(self, database_session: Session) -> None:
        self.database_session = database_session

    def _eager_load_options(self):
        """返回完整的预先加载选项。"""
        return [
            selectinload(User.skills),
            selectinload(User.projects),
            selectinload(User.competitions),
            selectinload(User.internships),
        ]

    def create_user(self, user_data: UserCreate) -> User:
        """创建学生基本资料。"""
        user = User(**user_data.model_dump())
        self.database_session.add(user)
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    def get_user(self, user_id: int) -> User:
        """获取包含全部关联数据的完整学生资料。"""
        statement = (
            select(User)
            .options(*self._eager_load_options())
            .where(User.id == user_id)
        )
        user = self.database_session.scalar(statement)
        if user is None:
            raise ResourceNotFoundError("学生资料不存在")
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新提供的学生基本资料字段。"""
        user = self.get_user(user_id)
        for field_name, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field_name, value)
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    # ── 技能 ──

    def replace_skills(self, user_id: int, skill_data: UserSkillsReplace) -> User:
        """在单一事务中整组替换学生技能。"""
        user = self.get_user(user_id)
        user.skills[:] = [UserSkill(**skill.model_dump()) for skill in skill_data.skills]
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    # ── 项目经历 ──

    def replace_projects(self, user_id: int, project_data: UserProjectsReplace) -> User:
        """在单一事务中整组替换学生项目经历。"""
        user = self.get_user(user_id)
        user.projects[:] = [UserProject(**p.model_dump()) for p in project_data.projects]
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    # ── 竞赛经历 ──

    def replace_competitions(self, user_id: int, data: UserCompetitionsReplace) -> User:
        """在单一事务中整组替换竞赛经历。"""
        user = self.get_user(user_id)
        user.competitions[:] = [UserCompetition(**c.model_dump()) for c in data.competitions]
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    # ── 实习经历 ──

    def replace_internships(self, user_id: int, data: UserInternshipsReplace) -> User:
        """在单一事务中整组替换实习经历。"""
        user = self.get_user(user_id)
        user.internships[:] = [UserInternship(**i.model_dump()) for i in data.internships]
        self._commit_and_refresh(user)
        return self.get_user(user.id)

    # ── AI 上下文 ──

    def get_user_context(self, user_id: int) -> StudentContextResponse:
        """生成供 AI 业务服务使用的稳定学生上下文。"""
        user = self.get_user(user_id)
        return StudentContextResponse(
            user_id=user.id,
            name=user.name,
            school=user.school,
            major=user.major,
            grade=user.grade,
            bio=user.bio,
            email=user.email,
            phone=user.phone,
            target_city=user.target_city,
            target_salary=user.target_salary,
            skills=user.skills,
            projects=user.projects,
            competitions=user.competitions,
            internships=user.internships,
        )

    def sync_profile_draft(self, user_id: int, profile: dict[str, Any]) -> tuple[User, list[str]]:
        """Atomically merge a user-confirmed AI draft into the profile aggregate.

        Existing records are patched by their natural identity. New records are
        only created when all database-required facts were explicitly supplied.
        """
        user = self.get_user(user_id)
        skipped: list[str] = []
        try:
            basic_limits = {
                "name": 50,
                "school": 100,
                "major": 100,
                "grade": 30,
                "bio": 5000,
                "email": 100,
                "phone": 20,
                "target_city": 50,
                "target_salary": 50,
            }
            for field_name, max_length in basic_limits.items():
                value = self._clean_text(profile.get(field_name), max_length)
                if value:
                    setattr(user, field_name, value)

            self._merge_skills(user, profile.get("skills"), skipped)
            self._merge_projects(user, profile.get("projects"), skipped)
            self._merge_competitions(user, profile.get("competitions"), skipped)
            self._merge_internships(user, profile.get("internships"), skipped)

            self.database_session.commit()
            self.database_session.refresh(user)
        except Exception:
            self.database_session.rollback()
            raise
        return self.get_user(user.id), skipped

    @staticmethod
    def _clean_text(value: Any, max_length: int) -> str:
        return value.strip()[:max_length] if isinstance(value, str) else ""

    @staticmethod
    def _clean_stack(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        result: list[str] = []
        for item in value:
            text = item.strip()[:100] if isinstance(item, str) else ""
            if text and text.casefold() not in {old.casefold() for old in result}:
                result.append(text)
        return result[:50]

    @staticmethod
    def _clean_date(value: Any) -> date | None:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None

    def _merge_skills(self, user: User, values: Any, skipped: list[str]) -> None:
        if not isinstance(values, list):
            return
        levels = {"了解", "熟悉", "掌握", "精通"}
        for raw in values:
            if not isinstance(raw, dict):
                continue
            name = self._clean_text(raw.get("name"), 100)
            if not name:
                continue
            existing = next((item for item in user.skills if item.name.casefold() == name.casefold()), None)
            proficiency = self._clean_text(raw.get("proficiency"), 10)
            description = self._clean_text(raw.get("description"), 2000)
            if existing:
                if proficiency in levels:
                    existing.proficiency = proficiency
                if "description" in raw:
                    existing.description = description
                continue
            if proficiency not in levels:
                skipped.append(f"技能“{name}”缺少明确熟练程度")
                continue
            user.skills.append(UserSkill(name=name, proficiency=proficiency, description=description))

    def _merge_projects(self, user: User, values: Any, skipped: list[str]) -> None:
        if not isinstance(values, list):
            return
        for raw in values:
            if not isinstance(raw, dict):
                continue
            name = self._clean_text(raw.get("name"), 150)
            if not name:
                continue
            existing = next((item for item in user.projects if item.name.casefold() == name.casefold()), None)
            role = self._clean_text(raw.get("role"), 100)
            description = self._clean_text(raw.get("description"), 10000)
            stack = self._clean_stack(raw.get("tech_stack"))
            if existing:
                if role:
                    existing.role = role
                if description:
                    existing.description = description
                if isinstance(raw.get("tech_stack"), list):
                    existing.tech_stack = stack
                start_date = self._clean_date(raw.get("start_date"))
                end_date = self._clean_date(raw.get("end_date"))
                if start_date:
                    existing.start_date = start_date
                if end_date:
                    existing.end_date = end_date
                continue
            if not role or not description:
                skipped.append(f"项目“{name}”缺少明确角色或项目说明")
                continue
            user.projects.append(UserProject(
                name=name,
                role=role,
                description=description,
                tech_stack=stack,
                start_date=self._clean_date(raw.get("start_date")),
                end_date=self._clean_date(raw.get("end_date")),
            ))

    def _merge_competitions(self, user: User, values: Any, skipped: list[str]) -> None:
        if not isinstance(values, list):
            return
        for raw in values:
            if not isinstance(raw, dict):
                continue
            name = self._clean_text(raw.get("name"), 200)
            if not name:
                continue
            existing = next((item for item in user.competitions if item.name.casefold() == name.casefold()), None)
            level = self._clean_text(raw.get("level"), 30)
            award = self._clean_text(raw.get("award"), 100)
            description = self._clean_text(raw.get("description"), 5000)
            if existing:
                if level:
                    existing.level = level
                if award:
                    existing.award = award
                if "description" in raw:
                    existing.description = description
                competition_date = self._clean_date(raw.get("competition_date"))
                if competition_date:
                    existing.competition_date = competition_date
                continue
            if not level or not award:
                skipped.append(f"竞赛“{name}”缺少明确级别或获奖情况")
                continue
            user.competitions.append(UserCompetition(
                name=name,
                level=level,
                award=award,
                description=description,
                competition_date=self._clean_date(raw.get("competition_date")),
            ))

    def _merge_internships(self, user: User, values: Any, skipped: list[str]) -> None:
        if not isinstance(values, list):
            return
        for raw in values:
            if not isinstance(raw, dict):
                continue
            company = self._clean_text(raw.get("company"), 200)
            position = self._clean_text(raw.get("position"), 150)
            if not company or not position:
                label = company or position or "未命名实习"
                skipped.append(f"实习“{label}”缺少公司或岗位")
                continue
            existing = next((
                item for item in user.internships
                if item.company.casefold() == company.casefold()
                and item.position.casefold() == position.casefold()
            ), None)
            description = self._clean_text(raw.get("description"), 10000)
            stack = self._clean_stack(raw.get("tech_stack"))
            if existing:
                if "description" in raw:
                    existing.description = description
                if isinstance(raw.get("tech_stack"), list):
                    existing.tech_stack = stack
                start_date = self._clean_date(raw.get("start_date"))
                end_date = self._clean_date(raw.get("end_date"))
                if start_date:
                    existing.start_date = start_date
                if end_date:
                    existing.end_date = end_date
                continue
            user.internships.append(UserInternship(
                company=company,
                position=position,
                description=description,
                tech_stack=stack,
                start_date=self._clean_date(raw.get("start_date")),
                end_date=self._clean_date(raw.get("end_date")),
            ))

    def _commit_and_refresh(self, user: User) -> None:
        """提交当前事务；发生数据库异常时回滚，避免部分写入。"""
        try:
            self.database_session.commit()
            self.database_session.refresh(user)
        except SQLAlchemyError:
            self.database_session.rollback()
            raise
