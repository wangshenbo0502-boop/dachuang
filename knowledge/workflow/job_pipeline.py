"""
文件名称：job_pipeline.py
文件作用：岗位匹配 Pipeline。

流程：
  Receive Query
  → Query Rewriter
  → Retriever（检索岗位知识）
  → Context Builder（组装匹配上下文）
  → Prompt Builder
  → DeepSeek API
  → Output Parser
  → Generate Answer（生成岗位匹配结果）
"""


class JobPipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, user_query: str, user_data: dict) -> dict:
        """TODO: 执行岗位匹配流水线"""
        pass
