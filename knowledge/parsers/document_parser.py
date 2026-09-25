"""Normalize source text and metadata into the canonical Document shape."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from loaders.base import Document
from parsers.metadata_parser import parse_front_matter
from config import normalize_category


class DocumentParser:
    def parse(self, content: str, *, source: str, category: str = "general", title: str = "", metadata: dict[str, Any] | None = None) -> Document:
        raw = content.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
        parsed_metadata = dict(metadata or {})
        body = raw
        if raw.startswith("---\n"):
            end = raw.find("\n---", 4)
            if end >= 0:
                parsed_metadata = {**parse_front_matter(raw[4:end]), **parsed_metadata}
                body = raw[end + 4 :].lstrip("\n")
        body = re.sub(r"[ \t]+\n", "\n", body)
        body = re.sub(r"\n{4,}", "\n\n\n", body).strip()
        resolved_title = str(parsed_metadata.get("title") or title or Path(source).stem)
        resolved_category = normalize_category(str(parsed_metadata.get("category") or category or "general"))
        return Document(
            title=resolved_title,
            source=source.replace("\\", "/"),
            content=body,
            category=resolved_category,
            metadata=parsed_metadata,
        )
