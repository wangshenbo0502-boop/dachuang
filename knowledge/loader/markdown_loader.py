"""
文件名称：markdown_loader.py
文件作用：Markdown 文档加载器，负责从 documents/ 目录读取 .md 文件。
当前版本：基础文件读取。
未来版本：支持元数据解析、增量加载。
"""
import os


class MarkdownLoader:
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
        self.base_path = base_path

    def load(self, file_path: str) -> str:
        full_path = os.path.join(self.base_path, file_path) if not os.path.isabs(file_path) else file_path
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def load_all(self, category: str = None) -> list[dict]:
        target_dir = os.path.join(self.base_path, category) if category else self.base_path
        documents = []
        if os.path.isdir(target_dir):
            for filename in os.listdir(target_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(target_dir, filename)
                    content = self.load(filepath)
                    documents.append({"path": filepath, "filename": filename, "content": content})
        return documents
