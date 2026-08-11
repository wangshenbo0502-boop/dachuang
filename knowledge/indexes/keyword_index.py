"""
文件名称：keyword_index.py
文件作用：关键词索引器，负责为 Markdown 知识文档建立关键词倒排索引。
当前版本：内存关键词倒排索引（Keyword Index）。
未来版本：Embedding Index（向量化索引）+ Hybrid Index（混合索引）。

升级路线：
  Keyword Index（当前）
  → Embedding Index（BGE-M3/Qwen3-Embedding）
  → FAISS 索引
  → Hybrid Index（关键词 + 向量混合）
  → Milvus 索引（可选）
"""
import re


class KeywordIndex:
    def __init__(self):
        self.inverted_index: dict = {}
        self.documents: dict = {}

    def _tokenize(self, text: str) -> list[str]:
        tokens = []
        en_tokens = re.findall(r'[a-zA-Z0-9_+#.\-]+', text)
        tokens.extend([t.lower() for t in en_tokens if len(t) > 1])
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        for i in range(len(chinese_chars)):
            tokens.append(chinese_chars[i])
            if i + 1 < len(chinese_chars):
                tokens.append(chinese_chars[i] + chinese_chars[i + 1])
        return tokens

    def build(self, documents: list[dict]) -> None:
        self.inverted_index.clear()
        self.documents.clear()
        for doc in documents:
            doc_id = doc.get("doc_id") or doc.get("filename") or doc.get("path", "")
            self.documents[doc_id] = doc
            text = doc.get("content", "")
            tokens = self._tokenize(text)
            token_counts = {}
            for token in tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
            for token, count in token_counts.items():
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append((doc_id, count))

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        query_tokens = self._tokenize(query)
        doc_scores = {}
        for token in query_tokens:
            if token in self.inverted_index:
                for doc_id, count in self.inverted_index[token]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + count
        ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score in ranked[:top_k]:
            doc = self.documents.get(doc_id, {})
            results.append({
                "doc_id": doc_id,
                "content": doc.get("content", ""),
                "score": score,
                "metadata": doc.get("metadata", {}),
                "filename": doc.get("filename", ""),
            })
        return results

    def add_document(self, doc_id: str, content: str, metadata: dict) -> None:
        doc = {"doc_id": doc_id, "content": content, "metadata": metadata}
        self.documents[doc_id] = doc
        tokens = self._tokenize(content)
        for token in set(tokens):
            if token not in self.inverted_index:
                self.inverted_index[token] = []
            self.inverted_index[token].append((doc_id, 1))

    def remove_document(self, doc_id: str) -> None:
        self.documents.pop(doc_id, None)
        for token in list(self.inverted_index.keys()):
            self.inverted_index[token] = [(did, c) for did, c in self.inverted_index[token] if did != doc_id]
            if not self.inverted_index[token]:
                del self.inverted_index[token]
