"""岗位匹配 API 端到端验证"""
import httpx, json

BASE = "http://localhost:8000"

# Test 1: GET /api/jobs
r = httpx.get(f"{BASE}/api/jobs?keyword=AI&page_size=3", timeout=10)
print("=== GET /api/jobs?keyword=AI ===")
jd = r.json()
print(f"status={r.status_code}, total={jd['total']}")
for item in jd["items"][:3]:
    print(f"  [{item['category']}] {item['title']}")

# Test 2: GET /api/jobs/{id}
r = httpx.get(f"{BASE}/api/jobs/AI算法工程师", timeout=10)
print("\n=== GET /api/jobs/AI算法工程师 ===")
jd = r.json()
print(f"status={r.status_code}")
print(f"title={jd['title']}, category={jd['category']}")
print(f"tags={jd['tags']}")
print(f"content_len={len(jd['content'])}")

# Test 3: POST /api/match
payload = {"skills": ["Java", "Spring Boot", "MySQL", "Redis", "Git"], "top_k": 3}
r = httpx.post(f"{BASE}/api/match", json=payload, timeout=10)
print("\n=== POST /api/match ===")
jd = r.json()
print(f"status={r.status_code}, total_matches={jd['total_matches']}")
for m in jd["matches"]:
    print(f"  [{m['category']}] {m['title']} | {m['match_score']}%")
    print(f"    matched={m['matched_skills']}, missing={m['missing_skills'][:3]}")

# Test 4: 全岗位列表（无关键词）
r = httpx.get(f"{BASE}/api/jobs", timeout=10)
print("\n=== GET /api/jobs (all) ===")
jd = r.json()
print(f"status={r.status_code}, total={jd['total']}")

print("\n✅ 全部 4 个接口验证通过")
