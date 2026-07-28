"""
文件名称：interview_pipeline.py
文件作用：面试辅导 Pipeline。

流程：
  Receive Query
  → Query Rewriter
  → Retriever（检索面试题库、公司面试风格）
  → Context Builder（组装面试辅导上下文）
  → Prompt Builder
  → DeepSeek API
  → Output Parser
  → Generate Answer（生成面试辅导内容）
"""


class InterviewPipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, user_query: str, target_role: str = None) -> dict:
        """TODO: 执行面试辅导流水线"""
        pass
