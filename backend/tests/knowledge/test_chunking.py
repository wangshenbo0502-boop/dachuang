from chunking.recursive_chunker import RecursiveChunker


def test_chunking_keeps_bounds_and_overlap() -> None:
    text = "## 技能要求\n" + "掌握Python和SQL。" * 40 + "\n\n## 项目经验\n" + "完成真实项目。" * 40
    chunks = RecursiveChunker(chunk_size=160, chunk_overlap=30).split(text)
    assert len(chunks) > 2
    assert all(0 < len(chunk.content) <= 160 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_empty_content_produces_no_chunk() -> None:
    assert RecursiveChunker().split("   \n") == []
