"""
文件名称：json_loader.py
文件作用：JSON 文档加载器，负责读取 data/ 目录中的 JSON 数据文件。
当前版本：基础 JSON 读取（兼容旧数据）。
未来版本：JSON 到 Markdown 自动转换。
"""
class JsonLoader:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "data/"

    def load(self, file_path: str) -> dict:
        """TODO: 读取单个 JSON 文件"""
        pass

    def load_all(self) -> list[dict]:
        """TODO: 加载所有 JSON 文件"""
        pass
