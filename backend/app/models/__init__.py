"""
文件名称：__init__.py
文件作用：models 数据模型层包初始化文件。
"""

from app.models.user import User, UserProject, UserSkill, UserCompetition, UserInternship
from app.models.job import JobMatchRecord
from app.models.analysis import ProfileAnalysis
from app.models.resume import Resume, ResumeOptimization
from app.models.growth import GrowthPlan
from app.models.application import JobApplication
from app.models.recruitment import RecruiterProfile, RecruitmentJob, RecruitmentApplication
from app.models.admin_receipt import BusinessAdminReceipt
from app.models.activity import GrowthTask, ResourceEvent

__all__ = [
    "User",
    "UserProject",
    "UserSkill",
    "UserCompetition",
    "UserInternship",
    "JobMatchRecord",
    "ProfileAnalysis",
    "ResumeOptimization",
    "Resume",
    "GrowthPlan",
    "JobApplication",
    "Account",
    "EmailCode",
    "RecruiterProfile",
    "RecruitmentJob",
    "RecruitmentApplication",
    "BusinessAdminReceipt",
]

from app.models.account import Account, EmailCode
