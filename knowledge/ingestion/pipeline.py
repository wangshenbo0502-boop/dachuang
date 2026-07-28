"""
文件名称：pipeline.py
文件作用：数据摄取流水线，编排 Loader → Parser → Splitter → Indexes 全流程。

当前版本：一次性全量摄取 Markdown 文件。
未来版本：增量更新、变更检测、断点续传。

RAG 数据流位置：
  corpus/（原始文件）
  → IngestionPipeline（本文件）
  → indexes/（索引就绪，等待检索）
"""
class IngestionPipeline:
    def __init__(self, loader=None, parser=None, splitter=None, index=None):
        self.loader = loader
        self.parser = parser
        self.splitter = splitter
        self.index = index
    
    def run(self, source_path: str = None) -> dict:
        """TODO: 执行全量数据摄取，返回 {doc_count, chunk_count, duration}"""
        pass
    
    def run_incremental(self, since_timestamp: str) -> dict:
        """TODO: 增量摄取：只处理变更的文件"""
        pass
    
    def dry_run(self) -> dict:
        """TODO: 预演模式：统计将要处理的文件数量，不实际写入索引"""
        pass
