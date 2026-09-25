"""Verify the production PostgreSQL/pgvector retrieval schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "knowledge"))

from config import get_knowledge_settings
from vector_store.pgvector_store import PgVectorStore


def main() -> int:
    try:
        report = PgVectorStore(get_knowledge_settings()).health()
    except Exception as exc:
        report = {"status": "failed", "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
