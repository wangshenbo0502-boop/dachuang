"""
文件名称：context_builder.py
文件作用：上下文组装器，负责将检索到的文档片段组装成可供 LLM 消费的上下文。
当前版本：按相关性排序拼接。
未来版本：基于 Token 预算的智能裁剪、引用标注。

组装流程：
  TopK Documents → 排序 → 截断（Token Budget） → 格式化为 Prompt Context
"""


import re


class ContextBuilder:
    def __init__(self, max_tokens: int = 3000):
        self.max_tokens = max_tokens

    def build(self, documents: list[dict], scenario: str = "default") -> str:
        parts = []
        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            title = doc.get("metadata", {}).get("title", "") or doc.get("filename", "")
            parts.append(f"## 文档 {i+1}: {title}\n\n{content}")

        context = "\n\n---\n\n".join(parts)
        estimated = self.estimate_tokens(context)
        if estimated > self.max_tokens:
            ratio = self.max_tokens / estimated * 0.8
            context = context[:int(len(context) * ratio)] + "\n\n...(内容已截断)"
        return context

    def format_as_markdown(self, documents: list[dict]) -> str:
        return self.build(documents)

    def estimate_tokens(self, text: str) -> int:
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 0.5 + other_chars * 0.25)
