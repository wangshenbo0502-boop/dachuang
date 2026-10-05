"""Validated account requests and public identity responses."""
from datetime import date
import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class QQEmailRequest(BaseModel):
    email: str = Field(min_length=6, max_length=100)
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,31}@qq\.com", value):
            raise ValueError("请输入有效的 QQ 邮箱")
        return value

class SendCodeRequest(QQEmailRequest):
    purpose: Literal["REGISTER", "RESET_PASSWORD"] = "REGISTER"

class RegisterRequest(QQEmailRequest):
    role: Literal["student", "recruiter"] = "student"
    code: str = Field(pattern=r"^\d{6}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str = Field(default="", max_length=20)
    birth_date: date | None = None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        value = value.strip()
        if value and not re.fullmatch(r"1[3-9]\d{9}", value):
            raise ValueError("请输入有效的 11 位手机号")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date | None) -> date | None:
        if value and value > date.today():
            raise ValueError("出生日期不能晚于今天")
        return value

class LoginRequest(QQEmailRequest):
    password: str = Field(min_length=1, max_length=128)
    role: Literal["student", "recruiter"] | None = None

class ResetPasswordRequest(QQEmailRequest):
    code: str = Field(pattern=r"^\d{6}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
