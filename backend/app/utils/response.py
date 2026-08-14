"""
文件名称：response.py
文件作用：统一 API 响应格式封装 + 错误码枚举 + 分页模型。
"""

from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


# ── 错误码枚举 ──

class ErrorCode(Enum):
    """统一错误码定义"""
    SUCCESS = 0
    # 通用错误 1-99
    INTERNAL_ERROR = 1
    PARAM_VALIDATION_ERROR = 1001
    # 资源错误 2000-2999
    NOT_FOUND = 2001
    ALREADY_EXISTS = 2002
    # AI服务错误 3000-3999
    AI_SERVICE_ERROR = 3001
    AI_API_ERROR = 3002
    AI_RETRY_EXHAUSTED = 3003
    AI_PARSE_ERROR = 3004
    # 认证授权 4000-4999
    UNAUTHORIZED = 4001
    FORBIDDEN = 4002


# ── 响应函数 ──

def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": ErrorCode.SUCCESS.value, "message": message, "data": data}


def error(code: int = 1, message: str = "error", data: Any = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


# ── 分页模型 ──

T = TypeVar("T")


class PaginatedData(BaseModel, Generic[T]):
    """通用分页数据模型"""
    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")


class PaginatedResponse(BaseModel):
    """通用分页响应模型"""
    items: list[Any] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    total_pages: int = Field(default=0)

    @classmethod
    def from_data(cls, items: list[Any], total: int, page: int, page_size: int) -> "PaginatedResponse":
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0,
        )