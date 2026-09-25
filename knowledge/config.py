"""Environment-driven configuration for the PostgreSQL/pgvector knowledge stack."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


CATEGORY_ALIASES = {
    "job": "jobs",
    "skill": "skills",
    "career": "roadmap",
    "growth": "roadmap",
    "project": "projects",
    "company": "companies",
    "policy": "policies",
}


def normalize_category(category: str | None) -> str:
    value = (category or "general").strip().lower()
    return CATEGORY_ALIASES.get(value, value or "general")


def _as_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class KnowledgeSettings:
    database_url: str
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    embedding_batch_size: int
    embedding_timeout: float
    chunk_size: int
    chunk_overlap: int
    top_k: int
    vector_weight: float
    keyword_weight: float
    reranker_enabled: bool
    context_max_chars: int
    hnsw_m: int = 16
    hnsw_ef_construction: int = 64
    hnsw_ef_search: int = 40
    rrf_k: int = 60
    vector_candidate_k: int = 20
    keyword_candidate_k: int = 20
    fusion_candidate_k: int = 10
    reranker_provider: str = "sentence_transformers"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "auto"
    reranker_batch_size: int = 8
    query_rewrite_enabled: bool = True
    query_rewrite_llm_enabled: bool = False

    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith(("postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://"))


@lru_cache(maxsize=1)
def get_knowledge_settings() -> KnowledgeSettings:
    database_url = os.getenv("KNOWLEDGE_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    vector_weight = float(os.getenv("VECTOR_WEIGHT", "0.7"))
    keyword_weight = float(os.getenv("KEYWORD_WEIGHT", "0.3"))
    total = vector_weight + keyword_weight
    if total <= 0:
        vector_weight, keyword_weight = 0.7, 0.3
    else:
        vector_weight, keyword_weight = vector_weight / total, keyword_weight / total
    chunk_size = max(100, int(os.getenv("CHUNK_SIZE", "800")))
    chunk_overlap = max(0, int(os.getenv("CHUNK_OVERLAP", "120")))
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size // 5)
    return KnowledgeSettings(
        database_url=database_url,
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").strip(),
        embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5").strip(),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "512")),
        embedding_batch_size=max(1, int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))),
        embedding_timeout=float(os.getenv("EMBEDDING_TIMEOUT", "120")),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=max(1, int(os.getenv("TOP_K", "5"))),
        vector_weight=vector_weight,
        keyword_weight=keyword_weight,
        reranker_enabled=_as_bool("RERANKER_ENABLED", False),
        context_max_chars=max(1000, int(os.getenv("RAG_CONTEXT_MAX_CHARS", "12000"))),
        hnsw_m=max(2, int(os.getenv("HNSW_M", "16"))),
        hnsw_ef_construction=max(4, int(os.getenv("HNSW_EF_CONSTRUCTION", "64"))),
        hnsw_ef_search=max(1, int(os.getenv("HNSW_EF_SEARCH", "40"))),
        rrf_k=max(1, int(os.getenv("RRF_K", "60"))),
        vector_candidate_k=max(1, int(os.getenv("VECTOR_CANDIDATE_K", "20"))),
        keyword_candidate_k=max(1, int(os.getenv("KEYWORD_CANDIDATE_K", "20"))),
        fusion_candidate_k=max(1, int(os.getenv("FUSION_CANDIDATE_K", "10"))),
        reranker_provider=os.getenv("RERANKER_PROVIDER", "sentence_transformers").strip(),
        reranker_model=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3").strip(),
        reranker_device=os.getenv("RERANKER_DEVICE", "auto").strip(),
        reranker_batch_size=max(1, int(os.getenv("RERANKER_BATCH_SIZE", "8"))),
        query_rewrite_enabled=_as_bool("QUERY_REWRITE_ENABLED", True),
        query_rewrite_llm_enabled=_as_bool("QUERY_REWRITE_LLM_ENABLED", False),
    )
