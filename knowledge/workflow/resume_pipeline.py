"""
文件名称：resume_pipeline.py
文件作用：简历优化 Pipeline。

流程：
  Receive Resume
  → Query Rewriter
  → Retriever（检索简历知识和目标岗位信息）
  → Context Builder（组装优化上下文）
  → Prompt Builder
  → DeepSeek API
  → Output Parser
  → Generate Answer（生成优化后的简历）
"""


class ResumePipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, resume_text: str, target_job: str) -> dict:
        """TODO: 执行简历优化流水线"""
        pass
