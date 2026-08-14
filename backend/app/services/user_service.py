"""
文件名称：user_service.py
文件作用：处理学生资料、技能、项目经历、竞赛经历和实习经历的数据读写与 AI 上下文聚合。
"""

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

    def _commit_and_refresh(self, user: User) -> None:
        """提交当前事务；发生数据库异常时回滚，避免部分写入。"""
        try:
            self.database_session.commit()
            self.database_session.refresh(user)
        except SQLAlchemyError:
            self.database_session.rollback()
            raise