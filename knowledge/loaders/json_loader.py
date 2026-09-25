from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from loaders.base import BaseLoader, Document
from parsers.document_parser import DocumentParser


class JsonLoader(BaseLoader):
    extensions = (".json",)

    def __init__(self, parser: DocumentParser | None = None) -> None:
        self.parser = parser or DocumentParser()

    def load(self, path: str | Path, *, source_root: str | Path | None = None) -> list[Document]:
        file_path = Path(path)
        root = Path(source_root) if source_root else file_path.parent
        source = file_path.relative_to(root).as_posix() if file_path.is_relative_to(root) else file_path.name
        category = source.split("/", 1)[0] if "/" in source else "general"
        payload: Any = json.loads(file_path.read_text(encoding="utf-8-sig"))
        items = payload if isinstance(payload, list) else [payload]
        documents: list[Document] = []
        for index, item in enumerate(items):
            if isinstance(item, dict):
                content = item.get("content") or item.get("body") or item.get("text") or json.dumps(item, ensure_ascii=False, indent=2)
                title = str(item.get("title") or item.get("name") or f"{file_path.stem}-{index + 1}")
                item_category = str(item.get("category") or category)
                metadata = {k: v for k, v in item.items() if k not in {"content", "body", "text"}}
            else:
                content, title, item_category, metadata = str(item), f"{file_path.stem}-{index + 1}", category, {}
            item_source = source if len(items) == 1 else f"{source}#{index + 1}"
            documents.append(self.parser.parse(str(content), source=item_source, category=item_category, title=title, metadata=metadata))
        return documents
