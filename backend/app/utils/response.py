"""
文件名称：response.py
文件作用：统一 API 响应格式封装。
为所有 API 路由和异常处理器生成一致的响应数据结构。
"""

from typing import Any


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    """生成成功响应数据。"""
    return {"code": 0, "message": message, "data": data}


def error(code: int = 1, message: str = "error", data: Any = None) -> dict[str, Any]:
    """生成失败响应数据。"""
    return {"code": code, "message": message, "data": data}
