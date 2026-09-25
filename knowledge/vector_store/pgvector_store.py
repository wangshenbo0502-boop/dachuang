"""All PostgreSQL and pgvector persistence/query logic for the knowledge subsystem."""
from __future__ import annotations

import logging
import re
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from sqlalchemy import cast, create_engine, delete, func, or_, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config import KnowledgeSettings, get_knowledge_settings, normalize_category
from retrieval.filters import KnowledgeFilter
from vector_store.base import BaseVectorStore, VectorStoreError
from vector_store.models import KnowledgeBase, KnowledgeChunk, KnowledgeDocument

logger = logging.getLogger(__name__)


class PgVectorStore(BaseVectorStore):
    def __init__(self, settings: KnowledgeSettings | None = None, engine: Engine | None = None) -> None:
        self.settings = settings or get_knowledge_settings()
        if engine is None:
            if not self.settings.database_url:
                raise VectorStoreError("KNOWLEDGE_DATABASE_URL or DATABASE_URL is required")
            if not self.settings.is_postgresql:
                raise VectorStoreError("knowledge vector store requires PostgreSQL with pgvector")
            try:
                engine = create_engine(
                    self.settings.database_url,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10,
                    pool_recycle=3600,
                )
            except SQLAlchemyError as exc:
                raise VectorStoreError(f"failed to create knowledge database engine: {exc}") from exc
        self.engine = engine
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, autoflush=False)

    def initialize(self) -> None:
        started = time.perf_counter()
        try:
            with self.engine.begin() as connection:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                connection.execute(text("ALTER TABLE IF EXISTS knowledge_chunks ADD COLUMN IF NOT EXISTS search_text TEXT NOT NULL DEFAULT ''"))
            KnowledgeBase.metadata.create_all(self.engine)
            with self.engine.begin() as connection:
                connection.execute(text("UPDATE knowledge_chunks c SET search_text = d.title || ' ' || c.content FROM knowledge_documents d WHERE c.document_id = d.id AND c.search_text = ''"))
                connection.execute(text("ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(search_text, ''))) STORED"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_search_vector_gin ON knowledge_chunks USING gin (search_vector)"))
                connection.execute(text("DROP INDEX IF EXISTS ix_knowledge_chunks_embedding_hnsw"))
                connection.execute(text(f"CREATE INDEX ix_knowledge_chunks_embedding_hnsw ON knowledge_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = {self.settings.hnsw_m}, ef_construction = {self.settings.hnsw_ef_construction})"))
        except SQLAlchemyError as exc:
            raise VectorStoreError(f"failed to initialize pgvector schema: {exc}") from exc
        logger.info("vector_store_initialized elapsed_ms=%.2f", (time.perf_counter() - started) * 1000)

    @contextmanager
    def session(self) -> Iterator[Session]:
        db = self.session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _document_values(document: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": str(document["title"]),
            "source": str(document["source"]),
            "category": normalize_category(str(document.get("category") or "general")),
            "content": str(document["content"]),
            "metadata_json": dict(document.get("metadata") or {}),
            "content_hash": str(document["content_hash"]),
        }

    def add(self, document: dict[str, Any], chunks: list[dict[str, Any]]) -> int:
        values = self._document_values(document)
        with self.session() as db:
            existing = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.source == values["source"]))
            if existing:
                raise VectorStoreError(f"document source already exists: {values['source']}")
            row = KnowledgeDocument(**values, status="processing")
            db.add(row)
            db.flush()
            self._replace_chunks(db, row, chunks)
            row.status = "completed"
            row.indexed_at = datetime.now(timezone.utc)
            return row.id

    def upsert(self, document: dict[str, Any], chunks: list[dict[str, Any]], *, force: bool = False) -> int:
        values = self._document_values(document)
        with self.session() as db:
            row = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.source == values["source"]))
            if row and row.content_hash == values["content_hash"] and row.status == "completed" and not force:
                return row.id
            if row is None:
                row = KnowledgeDocument(**values, status="processing")
                db.add(row)
                db.flush()
            else:
                for key, value in values.items():
                    setattr(row, key, value)
                row.status = "processing"
                row.error_message = None
                db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == row.id))
                db.flush()
            self._replace_chunks(db, row, chunks)
            row.status = "completed"
            row.indexed_at = datetime.now(timezone.utc)
            return row.id

    @staticmethod
    def _replace_chunks(db: Session, document: KnowledgeDocument, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            raise VectorStoreError("document produced no chunks")
        for item in chunks:
            vector = item.get("embedding")
            db.add(
                KnowledgeChunk(
                    document_id=document.id,
                    chunk_index=int(item["chunk_index"]),
                    content=str(item["content"]),
                    search_text=PgVectorStore._fts_document(document.title, str(item["content"])),
                    metadata_json=dict(item.get("metadata") or {}),
                    embedding=vector,
                    embedding_status="completed" if vector else "failed",
                    error_message=None if vector else "embedding missing",
                )
            )

    def mark_failed(self, source: str, document: dict[str, Any], message: str) -> int:
        values = self._document_values(document)
        with self.session() as db:
            row = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.source == source))
            if row is None:
                row = KnowledgeDocument(**values)
                db.add(row)
                db.flush()
            row.status = "failed"
            row.error_message = message[:4000]
            for key, value in values.items():
                setattr(row, key, value)
            return row.id

    @staticmethod
    def _apply_filters(stmt, filters: KnowledgeFilter):
        if filters.categories:
            stmt = stmt.where(KnowledgeDocument.category.in_(filters.categories))
        if filters.document_id:
            stmt = stmt.where(KnowledgeDocument.id == filters.document_id)
        if filters.source:
            stmt = stmt.where(KnowledgeDocument.source == filters.source)
        metadata = cast(KnowledgeDocument.metadata_json, JSONB)
        if filters.job_type:
            stmt = stmt.where(metadata["job_type"].as_string() == filters.job_type)
        if filters.skill:
            stmt = stmt.where(or_(metadata["skills"].contains([filters.skill]), metadata["tags"].contains([filters.skill]), metadata["keywords"].contains([filters.skill])))
        if filters.tags:
            stmt = stmt.where(metadata["tags"].contains(filters.tags))
        return stmt

    def search(self, query_vector: list[float], top_k: int = 5, category: str | None = None, filters: KnowledgeFilter | dict | None = None, *, use_hnsw: bool = True) -> list[dict[str, Any]]:
        if len(query_vector) != self.settings.embedding_dimension:
            raise VectorStoreError(
                f"query vector dimension mismatch: expected {self.settings.embedding_dimension}, got {len(query_vector)}"
            )
        distance = KnowledgeChunk.embedding.cosine_distance(query_vector).label("distance")
        stmt = (
            select(KnowledgeChunk, KnowledgeDocument, distance)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(
                KnowledgeChunk.embedding_status == "completed",
                KnowledgeChunk.embedding.is_not(None),
                KnowledgeDocument.status == "completed",
            )
            .order_by(distance.asc())
            .limit(max(1, top_k))
        )
        stmt = self._apply_filters(stmt, KnowledgeFilter.from_value(filters, category=category))
        started = time.perf_counter()
        try:
            with self.session() as db:
                if use_hnsw:
                    db.execute(text("SELECT set_config('hnsw.ef_search', :value, true)"), {"value": str(self.settings.hnsw_ef_search)})
                else:
                    db.execute(text("SET LOCAL enable_indexscan = off"))
                rows = db.execute(stmt).all()
        except SQLAlchemyError as exc:
            raise VectorStoreError(f"vector search failed: {exc}") from exc
        logger.info("vector_search count=%s elapsed_ms=%.2f", len(rows), (time.perf_counter() - started) * 1000)
        return [self._result(chunk, document, max(0.0, min(1.0, 1.0 - float(value))), "vector") for chunk, document, value in rows]

    def keyword_search(self, query: str, top_k: int = 5, category: str | None = None, filters: KnowledgeFilter | dict | None = None) -> list[dict[str, Any]]:
        tokens = self._keyword_tokens(query)
        if not tokens:
            return []
        safe_tokens = []
        for token in tokens[:32]:
            safe_tokens.extend(value for value in re.split(r"[^a-z0-9_\u4e00-\u9fff]+", token.lower()) if value)
        tsquery = " | ".join(dict.fromkeys(safe_tokens))
        if not tsquery:
            return []
        query_expr = func.to_tsquery("simple", tsquery)
        rank = func.ts_rank_cd(KnowledgeChunk.search_vector, query_expr).label("keyword_score")
        stmt = (
            select(KnowledgeChunk, KnowledgeDocument, rank)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(KnowledgeChunk.search_vector.op("@@")(query_expr), KnowledgeDocument.status == "completed")
            .order_by(rank.desc())
            .limit(max(1, top_k))
        )
        stmt = self._apply_filters(stmt, KnowledgeFilter.from_value(filters, category=category))
        started = time.perf_counter()
        try:
            with self.session() as db:
                rows = db.execute(stmt).all()
        except SQLAlchemyError as exc:
            raise VectorStoreError(f"keyword search failed: {exc}") from exc
        logger.info("keyword_search count=%s elapsed_ms=%.2f", len(rows), (time.perf_counter() - started) * 1000)
        return [self._result(chunk, document, float(score), "keyword") for chunk, document, score in rows]

    @staticmethod
    def _keyword_tokens(query: str) -> list[str]:
        """Extract exact technical terms plus useful Chinese 2-4 character n-grams."""
        lowered = query.lower().strip()
        values: list[str] = re.findall(r"[a-z0-9_+#.\-]{2,}", lowered)
        for sequence in re.findall(r"[\u4e00-\u9fff]+", lowered):
            if 2 <= len(sequence) <= 8:
                values.append(sequence)
            for size in (4, 3, 2):
                if len(sequence) < size:
                    continue
                values.extend(sequence[index : index + size] for index in range(len(sequence) - size + 1))
        return list(dict.fromkeys(value for value in values if value))[:24]

    @classmethod
    def _fts_document(cls, title: str, content: str) -> str:
        original = f"{title} {content}"
        tokens: list[str] = re.findall(r"[a-z0-9_+#.\-]{2,}", original.lower())
        for sequence in re.findall(r"[\u4e00-\u9fff]+", original):
            for size in (4, 3, 2):
                if len(sequence) >= size:
                    tokens.extend(sequence[index : index + size] for index in range(len(sequence) - size + 1))
        tokens = list(dict.fromkeys(tokens))[:1000]
        return f"{original} {' '.join(tokens)}"

    @staticmethod
    def _result(chunk: KnowledgeChunk, document: KnowledgeDocument, score: float, mode: str) -> dict[str, Any]:
        return {
            "chunk_id": chunk.id,
            "document_id": document.id,
            "content": chunk.content,
            "score": round(float(score), 6),
            "title": document.title,
            "category": document.category,
            "source": document.source,
            "metadata": {**(document.metadata_json or {}), **(chunk.metadata_json or {})},
            "retrieval_mode": mode,
            "retrieval_source": mode,
            f"{mode}_score": round(float(score), 6),
        }

    def health(self) -> dict[str, Any]:
        checks: dict[str, Any] = {}
        try:
            with self.engine.connect() as connection:
                checks["postgresql"] = bool(connection.scalar(text("SELECT 1")))
                checks["pgvector"] = bool(connection.scalar(text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector')")))
                indexes = set(connection.scalars(text("SELECT indexname FROM pg_indexes WHERE tablename='knowledge_chunks'")).all())
                columns = set(connection.scalars(text("SELECT column_name FROM information_schema.columns WHERE table_name='knowledge_chunks'")).all())
            checks["hnsw"] = "ix_knowledge_chunks_embedding_hnsw" in indexes
            checks["fts"] = "search_vector" in columns
            checks["gin"] = "ix_knowledge_chunks_search_vector_gin" in indexes
            checks["embedding_dimension"] = self.settings.embedding_dimension
        except Exception as exc:
            checks["postgresql"] = False
            checks["error"] = str(exc)
        checks["status"] = "healthy" if all(checks.get(key) for key in ("postgresql", "pgvector", "hnsw", "fts", "gin")) else "failed" if not checks.get("postgresql") else "degraded"
        return checks

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        with self.session() as db:
            row = db.get(KnowledgeDocument, document_id)
            if row is None:
                return None
            return self._serialize_document(row)

    def get_document_by_source(self, source: str) -> dict[str, Any] | None:
        with self.session() as db:
            row = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.source == source))
            return self._serialize_document(row) if row else None

    def list_documents(self, category: str | None = None, limit: int = 500, offset: int = 0) -> list[dict[str, Any]]:
        stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.id).offset(offset).limit(limit)
        if category:
            stmt = stmt.where(KnowledgeDocument.category == normalize_category(category))
        with self.session() as db:
            return [self._serialize_document(row) for row in db.scalars(stmt).all()]

    @staticmethod
    def _serialize_document(row: KnowledgeDocument) -> dict[str, Any]:
        return {
            "id": row.id,
            "doc_id": row.source.rsplit("/", 1)[-1].rsplit(".", 1)[0],
            "title": row.title,
            "source": row.source,
            "filename": row.source.rsplit("/", 1)[-1],
            "category": row.category,
            "content": row.content,
            "metadata": row.metadata_json or {},
            "status": row.status,
            "content_hash": row.content_hash,
            "error_message": row.error_message,
            "indexed_at": row.indexed_at.isoformat() if row.indexed_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    def create_document(self, document: dict[str, Any]) -> int:
        values = self._document_values(document)
        with self.session() as db:
            row = KnowledgeDocument(**values, status="pending")
            db.add(row)
            db.flush()
            return row.id

    def update(self, document_id: int, values: dict[str, Any]) -> bool:
        allowed = {"title", "source", "category", "content", "metadata_json", "content_hash", "status", "error_message"}
        with self.session() as db:
            row = db.get(KnowledgeDocument, document_id)
            if row is None:
                return False
            for key, value in values.items():
                if key in allowed:
                    setattr(row, key, value)
            return True

    def delete(self, chunk_id: int) -> bool:
        with self.session() as db:
            result = db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id == chunk_id))
            return bool(result.rowcount)

    def delete_document(self, document_id: int) -> bool:
        with self.session() as db:
            result = db.execute(delete(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
            return bool(result.rowcount)

    def delete_by_source(self, source: str) -> bool:
        """Delete one indexed source and its chunks by its stable source key."""
        with self.session() as db:
            result = db.execute(delete(KnowledgeDocument).where(KnowledgeDocument.source == source))
            return bool(result.rowcount)

    def delete_by_document(self, document_id: int) -> int:
        with self.session() as db:
            result = db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id))
            return int(result.rowcount or 0)

    def count(self) -> dict[str, int]:
        with self.session() as db:
            documents = db.scalar(select(func.count()).select_from(KnowledgeDocument)) or 0
            chunks = db.scalar(select(func.count()).select_from(KnowledgeChunk)) or 0
            embedded = db.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.embedding_status == "completed")) or 0
            failed = db.scalar(select(func.count()).select_from(KnowledgeDocument).where(KnowledgeDocument.status == "failed")) or 0
            return {"documents_count": documents, "chunks_count": chunks, "embedded_count": embedded, "failed_count": failed}

    def stats(self) -> dict[str, Any]:
        values = self.count()
        with self.session() as db:
            categories = dict(db.execute(select(KnowledgeDocument.category, func.count()).group_by(KnowledgeDocument.category)).all())
            last_index = db.scalar(select(func.max(KnowledgeDocument.indexed_at)))
        return {**values, "categories": categories, "last_index_time": last_index.isoformat() if last_index else None}
