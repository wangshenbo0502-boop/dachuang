"""
文件名称：market_pipeline.py
文件作用：市场分析 Pipeline。

流程：
  Receive Query
  → Query Rewriter
  → Retriever（检索市场数据、薪资行情、企业信息）
  → Context Builder（组装市场分析上下文）
  → Prompt Builder
  → DeepSeek API
  → Output Parser
  → Generate Answer（生成市场分析报告）
"""


class MarketPipeline:
    def __init__(self, search_engine, context_builder):
        self.search_engine = search_engine
        self.context_builder = context_builder

    def run(self, user_query: str) -> dict:
        """TODO: 执行市场分析流水线"""
        pass
