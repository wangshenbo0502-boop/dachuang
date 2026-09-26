"""Validated account requests and public identity responses."""
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
    code: str = Field(pattern=r"^\d{6}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=1, max_length=50)

class LoginRequest(QQEmailRequest):
    password: str = Field(min_length=1, max_length=128)

class ResetPasswordRequest(QQEmailRequest):
    code: str = Field(pattern=r"^\d{6}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
