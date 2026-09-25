from __future__ import annotations
from pathlib import Path
from loaders.base import BaseLoader, Document
from parsers.document_parser import DocumentParser


class MarkdownLoader(BaseLoader):
    extensions = (".md", ".markdown")

    def __init__(self, parser: DocumentParser | None = None) -> None:
        self.parser = parser or DocumentParser()

    def load(self, path: str | Path, *, source_root: str | Path | None = None) -> list[Document]:
        file_path = Path(path)
        root = Path(source_root) if source_root else file_path.parent
        source = file_path.relative_to(root).as_posix() if file_path.is_relative_to(root) else file_path.name
        category = source.split("/", 1)[0] if "/" in source else "general"
        return [self.parser.parse(file_path.read_text(encoding="utf-8-sig"), source=source, category=category)]
