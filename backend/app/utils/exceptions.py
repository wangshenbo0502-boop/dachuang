"""
文件名称：exceptions.py
文件作用：自定义异常类定义，统一项目异常处理。
由业务层抛出，并由 FastAPI 全局异常处理器转换为标准响应。
"""


class AppException(Exception):
    """项目业务异常基类。"""

    def __init__(self, message: str, code: int = 1, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ResourceNotFoundError(AppException):
    """请求的资源不存在。"""

    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message=message, code=3001, status_code=404)


class DatabaseConfigurationError(AppException):
    """数据库环境变量或连接参数配置错误。"""

    def __init__(self, message: str = "数据库配置错误") -> None:
        super().__init__(message=message, code=1005, status_code=500)
