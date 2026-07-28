"""
文件名称：markdown_loader.py
文件作用：Markdown 文档加载器，负责从 documents/ 目录读取 .md 文件。
当前版本：基础文件读取。
未来版本：支持元数据解析、增量加载。
"""
class MarkdownLoader:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "documents/"

    def load(self, file_path: str) -> str:
        """TODO: 读取单个 Markdown 文件内容"""
        pass

    def load_all(self, category: str = None) -> list[dict]:
        """TODO: 加载指定分类下所有 Markdown 文件，返回 [{path, content, metadata}, ...]"""
        pass
