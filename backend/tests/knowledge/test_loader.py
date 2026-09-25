from pathlib import Path

from loaders.json_loader import JsonLoader
from loaders.markdown_loader import MarkdownLoader
from loaders.text_loader import TextLoader


def test_markdown_front_matter_and_category(tmp_path: Path) -> None:
    root = tmp_path / "documents"
    path = root / "jobs" / "frontend.md"
    path.parent.mkdir(parents=True)
    path.write_text('---\ntitle: 前端工程师\ntags: ["Vue", "React"]\n---\n# 岗位要求\n掌握 JavaScript。', encoding="utf-8")
    document = MarkdownLoader().load(path, source_root=root)[0]
    assert document.title == "前端工程师"
    assert document.category == "jobs"
    assert document.source == "jobs/frontend.md"
    assert document.metadata["tags"] == ["Vue", "React"]


def test_text_and_json_loaders(tmp_path: Path) -> None:
    root = tmp_path / "documents"
    text_path = root / "skills" / "python.txt"
    text_path.parent.mkdir(parents=True)
    text_path.write_text("Python 技能说明", encoding="utf-8")
    assert TextLoader().load(text_path, source_root=root)[0].category == "skills"

    json_path = root / "resume" / "tips.json"
    json_path.parent.mkdir(parents=True)
    json_path.write_text('[{"title":"STAR","content":"使用 STAR 法则"}]', encoding="utf-8")
    documents = JsonLoader().load(json_path, source_root=root)
    assert documents[0].title == "STAR"
    assert documents[0].source == "resume/tips.json"
