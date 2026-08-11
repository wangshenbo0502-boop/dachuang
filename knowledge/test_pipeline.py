"""测试检索管线是否正常工作"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from loader.markdown_loader import MarkdownLoader
from parser.markdown_parser import MarkdownParser
from indexes.keyword_index import KeywordIndex
from retrieval.query_rewriter import QueryRewriter
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.search_engine import SearchEngine
from retrieval.context_builder import ContextBuilder

# 1. 加载
loader = MarkdownLoader()
docs = loader.load_all(category="jobs")
print(f"加载了 {len(docs)} 个岗位文档")

# 2. 解析
parser = MarkdownParser()
for doc in docs:
    parsed = parser.parse(doc["content"])
    doc["metadata"] = parsed["metadata"]
    doc["content"] = parsed["body"]

# 3. 构建索引
index = KeywordIndex()
index.build(docs)
print(f"索引词数: {len(index.inverted_index)}")

# 4. 检索
rewriter = QueryRewriter()
retriever = KeywordRetriever(index)
engine = SearchEngine(retriever, rewriter)

print("\n--- 搜索: 'Java' ---")
results = engine.search("Java", top_k=3)
for r in results:
    title = r.get("metadata", {}).get("title", "N/A")
    print(f"  [{r['score']}] {title} ({r['doc_id']})")

print("\n--- 搜索: '前端 HTML CSS' ---")
results = engine.search("前端 HTML CSS", top_k=3)
for r in results:
    title = r.get("metadata", {}).get("title", "N/A")
    print(f"  [{r['score']}] {title} ({r['doc_id']})")
