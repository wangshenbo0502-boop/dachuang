"""
文件名称：career_pipeline.py
文件作用：就业画像分析 Pipeline，编排从用户查询到AI报告生成的完整流程。

流程：
  Receive Query（接收用户请求）
  → Query Rewriter（改写查询）
  → Retriever（检索就业画像相关知识）
  → Context Builder（组装画像上下文）
  → Prompt Builder（构造 Prompt）
  → DeepSeek API（调用大模型）
  → Output Parser（解析输出）
  → Generate Answer（生成就业画像报告）
"""


class CareerPipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, user_query: str, user_data: dict) -> dict:
        """TODO: 执行就业画像分析流水线"""
        pass
