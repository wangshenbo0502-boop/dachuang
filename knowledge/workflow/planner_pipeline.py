"""
文件名称：planner_pipeline.py
文件作用：成长规划 Pipeline。

流程：
  Receive Query
  → Query Rewriter
  → Retriever（检索学习路线、项目案例、技能提升方法）
  → Context Builder（组装规划上下文）
  → Prompt Builder
  → DeepSeek API
  → Output Parser
  → Generate Answer（生成个性化学习路线）
"""


class PlannerPipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, user_query: str, user_data: dict) -> dict:
        """TODO: 执行成长规划流水线"""
        pass
