"""
文件名称：markdown_parser.py
文件作用：Markdown 解析器，负责将 .md 文件内容解析为结构化数据。
当前版本：提取 YAML Front Matter + Markdown Body。
未来版本：支持更多元数据格式、自动标签提取。
"""
import re


class MarkdownParser:
    def parse(self, content: str) -> dict:
        metadata = {}
        body = content
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                front_matter = content[3:end_idx].strip()
                metadata = self._parse_front_matter(front_matter)
                body = content[end_idx + 3:].strip()
        return {"metadata": metadata, "body": body}

    def _parse_front_matter(self, text: str) -> dict:
        result = {}
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value.startswith("[") and value.endswith("]"):
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                result[key] = value
        return result

    def extract_metadata(self, content: str) -> dict:
        return self.parse(content)["metadata"]

    def extract_headings(self, content: str) -> list[str]:
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        return [h.strip() for h in headings]
