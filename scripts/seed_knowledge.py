"""Idempotently migrate existing Markdown/JSON/TXT knowledge files into pgvector."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
sys.path.insert(0, str(KNOWLEDGE_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from pipeline.index_pipeline import IndexPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=KNOWLEDGE_ROOT / "documents")
    parser.add_argument("--force", action="store_true", help="rebuild documents even when content hash is unchanged")
    parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="delete indexed file sources that no longer exist under --source",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    result = IndexPipeline().index_directory(
        args.source,
        force=args.force,
        prune_missing=args.prune_missing,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "results"}, ensure_ascii=False, indent=2))
    failed = result["status_counts"].get("failed", 0)
    if failed:
        print(json.dumps([item for item in result["results"] if item["status"] == "failed"][:20], ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
