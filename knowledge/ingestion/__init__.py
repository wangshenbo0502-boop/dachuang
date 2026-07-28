"""
文件名称：__init__.py
文件作用：数据摄取（Ingestion）模块统一入口。

Ingestion 是 RAG 的数据预处理流水线协调层，负责：
  corpus/（原始文件）
  → Loader（加载）
  → Parser（解析）
  → Splitter（切块）
  → Indexes（索引构建）

当前版本：协调 Markdown 文件的加载→解析→索引流程。
未来版本：支持增量摄取、定时更新、多来源并发摄取。
"""
from .pipeline import IngestionPipeline
