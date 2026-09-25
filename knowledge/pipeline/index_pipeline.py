"""Document -> chunks -> embeddings -> PostgreSQL/pgvector indexing pipeline."""
from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from chunking.recursive_chunker import RecursiveChunker
from config import KnowledgeSettings, get_knowledge_settings
from embedding.base import EmbeddingModel
from embedding.factory import create_embedding_model
from loaders import Document, JsonLoader, MarkdownLoader, TextLoader
from vector_store.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


class IndexPipeline:
    def __init__(
        self,
        settings: KnowledgeSettings | None = None,
        embeddings: EmbeddingModel | None = None,
        store: PgVectorStore | None = None,
        chunker: RecursiveChunker | None = None,
    ) -> None:
        self.settings = settings or get_knowledge_settings()
        self.embeddings = embeddings or create_embedding_model(self.settings)
        self.store = store or PgVectorStore(self.settings)
        self.chunker = chunker or RecursiveChunker(self.settings.chunk_size, self.settings.chunk_overlap)
        self.loaders = {
            ".md": MarkdownLoader(),
            ".markdown": MarkdownLoader(),
            ".txt": TextLoader(),
            ".json": JsonLoader(),
        }

    @staticmethod
    def content_hash(document: Document) -> str:
        payload = f"{document.title}\n{document.category}\n{document.content}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def index_document(self, document: Document, *, force: bool = False) -> dict:
        started = time.perf_counter()
        digest = self.content_hash(document)
        current = self.store.get_document_by_source(document.source)
        if current and current.get("content_hash") == digest and current.get("status") == "completed" and not force:
            return {"document_id": current["id"], "source": document.source, "status": "unchanged", "chunks": 0}
        values = {
            "title": document.title,
            "source": document.source,
            "category": document.category,
            "content": document.content,
            "metadata": document.metadata,
            "content_hash": digest,
        }
        try:
            chunks = self.chunker.split(
                document.content,
                metadata={"source": document.source, "title": document.title, "category": document.category},
            )
            if not chunks:
                raise ValueError("document is empty after parsing and cleaning")
            vectors = self.embeddings.embed_documents([chunk.content for chunk in chunks])
            if len(vectors) != len(chunks):
                raise ValueError(f"embedding count mismatch: chunks={len(chunks)}, vectors={len(vectors)}")
            records = [
                {
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "embedding": vector,
                }
                for chunk, vector in zip(chunks, vectors, strict=True)
            ]
            document_id = self.store.upsert(values, records, force=force)
            result = {"document_id": document_id, "source": document.source, "status": "completed", "chunks": len(records)}
            logger.info(
                "document_indexed source=%s chunks=%s elapsed_ms=%.2f",
                document.source,
                len(records),
                (time.perf_counter() - started) * 1000,
            )
            return result
        except Exception as exc:
            logger.exception("document_index_failed source=%s", document.source)
            try:
                self.store.mark_failed(document.source, values, str(exc))
            except Exception:
                logger.exception("failed_to_record_index_error source=%s", document.source)
            return {"source": document.source, "status": "failed", "chunks": 0, "error": str(exc)}

    def load_path(self, path: str | Path, source_root: str | Path) -> list[Document]:
        file_path = Path(path)
        loader = self.loaders.get(file_path.suffix.lower())
        if loader is None:
            return []
        return loader.load(file_path, source_root=source_root)

    def index_directory(
        self,
        root: str | Path,
        *,
        force: bool = False,
        prune_missing: bool = False,
    ) -> dict:
        root_path = Path(root).resolve()
        if not root_path.is_dir():
            raise FileNotFoundError(f"knowledge source directory not found: {root_path}")
        self.store.initialize()
        results: list[dict] = []
        discovered_sources: set[str] = set()
        for file_path in sorted(path for path in root_path.rglob("*") if path.is_file() and path.suffix.lower() in self.loaders):
            for document in self.load_path(file_path, root_path):
                discovered_sources.add(document.source)
                results.append(self.index_document(document, force=force))
        deleted = 0
        if prune_missing and hasattr(self.store, "list_documents") and hasattr(self.store, "delete_by_source"):
            for existing in self.store.list_documents(limit=100000):
                source = str(existing.get("source", ""))
                if source and source not in discovered_sources:
                    self.store.delete_by_source(source)
                    deleted += 1
        counts: dict[str, int] = {}
        for item in results:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        return {
            "root": str(root_path),
            "documents": len(results),
            "deleted": deleted,
            "status_counts": counts,
            "results": results,
        }
