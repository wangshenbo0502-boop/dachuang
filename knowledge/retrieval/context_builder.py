"""
文件名称：context_builder.py
文件作用：上下文组装器，负责将检索到的文档片段组装成可供 LLM 消费的上下文。
当前版本：按相关性排序拼接。
未来版本：基于 Token 预算的智能裁剪、引用标注。

组装流程：
  TopK Documents → 排序 → 截断（Token Budget） → 格式化为 Prompt Context
"""


class ContextBuilder:
    def __init__(self, max_tokens: int = 3000):
        self.max_tokens = max_tokens

    def build(self, documents: list[dict], scenario: str = "default") -> str:
        """TODO: 将检索结果组装为 LLM 上下文文本"""
        pass

    def format_as_markdown(self, documents: list[dict]) -> str:
        """TODO: 将文档格式化为 Markdown 引用格式"""
        pass

    def estimate_tokens(self, text: str) -> int:
        """TODO: 估算文本的 Token 数量"""
        pass
