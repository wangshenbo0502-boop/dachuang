from config import KnowledgeSettings
from vector_store.pgvector_store import PgVectorStore


def _store_without_init() -> PgVectorStore:
    store = object.__new__(PgVectorStore)
    store.settings = KnowledgeSettings("", "mock", "test", 8, 4, 5.0, 100, 20, 5, 0.7, 0.3, False, 2000)
    return store


def test_keyword_tokenization_supports_chinese_and_tech_terms() -> None:
    tokens = _store_without_init()._keyword_tokens("前端开发工程师需要 Vue.js 和 Python 技能")
    assert "vue.js" in tokens
    assert "python" in tokens
    assert "前端" in tokens
    assert "开发" in tokens
