"""
文件名称：test_job_match.py
文件作用：岗位匹配模块端到端验证。
覆盖岗位搜索、岗位详情、技能匹配、匹配记录持久化与查询。
使用 SQLite 内存数据库，不依赖外部 MySQL。
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

import app.models  # noqa: F401  确保所有 ORM 模型已注册
from app.database.connection import Base, get_engine
from app.database.session import get_db, get_session_factory
from app.knowledge.knowledge_service import KnowledgeService
from main import app


def run_checks() -> None:
    Base.metadata.create_all(get_engine())
    database_session = get_session_factory()()
    app.dependency_overrides[get_db] = lambda: database_session
    client = TestClient(app, raise_server_exceptions=False)

    # ── 1. 岗位列表搜索 ──
    resp = client.get("/api/jobs?keyword=Java&page_size=3")
    data = resp.json()
    assert resp.status_code == 200 and data["code"] == 0, f"列表失败: {resp.text}"
    print(f"[1] 岗位搜索 'Java' OK, total={data['data']['total']}")

    # ── 2. 岗位详情 ──
    resp = client.get("/api/jobs/AI算法工程师")
    data = resp.json()
    assert resp.status_code == 200 and data["data"]["title"] == "AI算法工程师", f"详情失败: {resp.text}"
    print(f"[2] 岗位详情 OK, category={data['data']['category']}")

    # ── 3. 岗位不存在 → 404 ──
    resp = client.get("/api/jobs/不存在的岗位")
    assert resp.status_code == 404 and resp.json()["code"] == 3001, f"404失败: {resp.text}"
    print("[3] 岗位不存在返回 404 OK")

    # ── 4. 岗位技能匹配 + 记录持久化 ──
    payload = {
        "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Git"],
        "job_category": "后端",
        "top_k": 3,
        "user_id": 1,
    }
    resp = client.post("/api/match", json=payload)
    data = resp.json()
    assert resp.status_code == 200 and data["code"] == 0, f"匹配失败: {resp.text}"
    record_id = data["data"]["record_id"]
    assert record_id is not None, "匹配记录未保存"
    print(f"[4] 岗位匹配 OK, record_id={record_id}, top1={data['data']['matches'][0]['title']}")

    # ── 5. 查询历史匹配记录 ──
    resp = client.get(f"/api/match/{record_id}")
    data = resp.json()
    assert resp.status_code == 200 and data["data"]["id"] == record_id, f"记录查询失败: {resp.text}"
    assert data["data"]["job_title"], "记录缺少主岗位"
    print(f"[5] 历史记录查询 OK, job_title={data['data']['job_title']}")

    # ── 6. 记录不存在 → 404 ──
    resp = client.get("/api/match/99999")
    assert resp.status_code == 404, f"记录404失败: {resp.text}"
    print("[6] 记录不存在返回 404 OK")

    # ── 7. KnowledgeService 通用检索 ──
    ks = KnowledgeService.instance()
    categories = ks.list_categories()
    cats = {c["category"]: c["count"] for c in categories}
    print(f"[7] 知识分类 OK: {cats}")
    assert cats.get("jobs", 0) >= 50, "岗位知识数量不足"
    req_skills = ks.get_skill_requirements("Java后端开发工程师")
    assert req_skills, "技能要求提取失败"
    print(f"[8] 技能要求提取 OK: {req_skills}")

    print("\n✅ 全部 8 项检查通过")

    app.dependency_overrides.clear()
    database_session.close()


if __name__ == "__main__":
    run_checks()
