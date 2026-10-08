import re
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

Role = Literal["super_admin", "operator", "auditor"]
Version = Annotated[int, Field(strict=True, ge=0)]
Password = Annotated[str, Field(min_length=12, max_length=128)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginBody(StrictModel):
    username: str = Field(max_length=64)
    password: str = Field(max_length=128)

    @field_validator("username")
    @classmethod
    def normalize(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9_.-]{3,64}", value):
            raise ValueError("账号格式不正确")
        return value


class PasswordBody(StrictModel):
    current_password: str = Field(max_length=128)
    new_password: Password

    @field_validator("new_password")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("密码不能全为空白")
        return value


class ReasonBody(StrictModel):
    reason: str = Field(min_length=5, max_length=500)

    @field_validator("reason", mode="before")
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value


class StatusCommand(ReasonBody):
    expected_version: Version
    is_active: StrictBool


class ModerationCommand(ReasonBody):
    expected_version: Version
    moderation_status: Literal["allowed", "blocked"]


class CreateAdmin(LoginBody, ReasonBody):
    password: Password
    role: Role

    @field_validator("password")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("密码不能全为空白")
        return value


class UpdateAdmin(ReasonBody):
    role: Role | None = None
    is_active: StrictBool | None = None
    expected_version: Version
