"""
文件名称：job_match_service.py
文件作用：岗位匹配业务逻辑层。
负责岗位搜索、详情查询与技能匹配。
知识数据统一通过 KnowledgeService 获取（解耦知识库访问细节）。
当前版本基于 keyword index 实现关键词检索与技能匹配。
"""

import re
from typing import Optional

from sqlalchemy.orm import Session

from app.knowledge.knowledge_service import KnowledgeService
from app.models.job import JobMatchRecord
from app.schemas.job import (
    JobBrief,
    JobDetail,
    JobListResponse,
    JobMatchRequest,
    JobMatchResponse,
    MatchedJob,
)

# ── 岗位标签到业务分类的映射 ──
TAG_CATEGORY_MAP = {
    # 前端
    "html": "前端", "css": "前端", "javascript": "前端", "typescript": "前端",
    "vue": "前端", "react": "前端", "web": "前端", "前端": "前端",
    # 后端
    "java": "后端", "spring": "后端", "go": "后端", "rust": "后端",
    "c++": "后端", "python": "后端", "后端": "后端", "sql": "后端",
    "mysql": "后端", "redis": "后端", "mongodb": "后端",
    # AI/算法
    "ai": "AI", "算法": "AI", "机器学习": "AI", "深度学习": "AI",
    "nlp": "AI", "pytorch": "AI", "tensorflow": "AI",
    # 数据
    "数据分析": "数据", "数据工程": "数据", "数据仓库": "数据",
    # 移动端
    "android": "移动端", "ios": "移动端", "移动端": "移动端",
    # 其他
    "运维": "运维", "测试": "测试", "产品": "产品", "运营": "运营", "安全": "安全",
}


class JobMatchService:
    """岗位匹配服务：提供岗位搜索、详情与技能匹配能力。

    知识数据通过 KnowledgeService 统一获取，
    本服务只负责岗位相关的业务组装与匹配算法。
    """

    _instance: Optional["JobMatchService"] = None

    def __init__(self) -> None:
        self._knowledge = KnowledgeService.instance()
        self._all_jobs: dict[str, dict] = {}  # doc_id → job doc
        self._loaded = False

    # ── 单例懒加载 ──

    @classmethod
    def instance(cls) -> "JobMatchService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self) -> None:
        """首次调用时从 KnowledgeService 拉取全部岗位文档。"""
        if self._loaded:
            return
        self._all_jobs = {doc["doc_id"]: doc for doc in self._knowledge.list_documents("jobs")}
        self._loaded = True

    # ── 岗位列表搜索 ──

    def search_jobs(
        self, keyword: str = "", category: str = None, page: int = 1, page_size: int = 20
    ) -> JobListResponse:
        """搜索岗位列表（支持关键词、业务分类过滤与分页）。"""
        self._ensure_loaded()
        if keyword:
            results = self._knowledge.search(keyword, category="jobs", top_k=50)
        else:
            # 无关键词时返回全部岗位
            results = [
                {"doc_id": j["doc_id"], "content": j["content"], "metadata": j["metadata"], "score": 0}
                for j in self._all_jobs.values()
            ]
        # 按业务分类过滤
        if category:
            results = [r for r in results if self._classify_job(r) == category]
        # 分页
        total = len(results)
        start = (page - 1) * page_size
        page_results = results[start : start + page_size]
        items = [self._to_job_brief(r) for r in page_results]
        return JobListResponse(total=total, items=items, keyword=keyword or None)

    # ── 岗位详情 ──

    def get_job_detail(self, job_id: str) -> Optional[JobDetail]:
        """获取单个岗位详情。"""
        self._ensure_loaded()
        doc = self._all_jobs.get(job_id)
        if not doc:
            return None
        metadata = doc["metadata"]
        return JobDetail(
            job_id=job_id,
            title=metadata.get("title", job_id),
            category=self._classify_job(doc),
            tags=list(metadata.get("tags", [])),
            content=doc["content"],
            metadata=metadata,
        )

    # ── 岗位智能匹配 ──

    def match_jobs(self, request: JobMatchRequest) -> JobMatchResponse:
        """根据用户技能列表做岗位匹配，返回匹配度评分与技能差距。"""
        self._ensure_loaded()
        user_skills_lower = [s.strip().lower() for s in request.skills]

        # 用用户技能拼接查询关键词
        query = " ".join(request.skills)
        results = self._knowledge.search(query, category="jobs", top_k=50)

        matches: list[MatchedJob] = []
        for r in results:
            doc_id = r["doc_id"]
            doc = self._all_jobs.get(doc_id)
            if not doc:
                continue
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            tags = list(metadata.get("tags", []))

            # 岗位需求技能（来自知识库）
            required_skills = self._knowledge.get_skill_requirements(doc_id) or [
                t.lower() if isinstance(t, str) else "" for t in tags if t
            ]

            # 匹配计算：支持技能子串匹配（如 "Spring Boot" 命中 "spring"）
            matched, missing = [], []
            for skill in required_skills:
                if any(skill == us or skill in us or us in skill for us in user_skills_lower):
                    matched.append(skill)
                else:
                    missing.append(skill)
            if not required_skills:
                continue
            score = round(len(matched) / len(required_skills) * 100, 1)

            # 按业务分类过滤
            if request.job_category:
                if self._classify_job(r) != request.job_category:
                    continue

            matches.append(
                MatchedJob(
                    job_id=doc_id,
                    title=metadata.get("title", doc_id),
                    category=self._classify_job(r),
                    tags=tags,
                    match_score=score,
                    matched_skills=matched,
                    missing_skills=missing,
                    snippet=self._make_snippet(content),
                )
            )

        # 按得分降序，截取 top_k
        matches.sort(key=lambda m: m.match_score, reverse=True)
        matches = matches[: request.top_k]
        return JobMatchResponse(
            user_skills=request.skills,
            total_matches=len(matches),
            matches=matches,
        )

    # ── 匹配记录持久化 ──

    def save_match_record(self, db: Session, request: JobMatchRequest, response: JobMatchResponse) -> JobMatchRecord:
        """将一次匹配结果持久化为历史记录。"""
        top_match = response.matches[0] if response.matches else None
        record = JobMatchRecord(
            user_id=request.user_id,
            skills=request.skills,
            job_id=top_match.job_id if top_match else "",
            job_title=top_match.title if top_match else "",
            match_score=top_match.match_score if top_match else 0.0,
            matched_skills=top_match.matched_skills if top_match else [],
            missing_skills=top_match.missing_skills if top_match else [],
            result=[m.model_dump() for m in response.matches],
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    # ── 辅助方法 ──

    def _to_job_brief(self, result: dict) -> JobBrief:
        """将内部文档结果转为 JobBrief Pydantic 模型。"""
        metadata = result.get("metadata", {})
        return JobBrief(
            job_id=result.get("doc_id", ""),
            title=metadata.get("title", result.get("doc_id", "")),
            category=self._classify_job(result),
            tags=list(metadata.get("tags", [])),
            snippet=self._make_snippet(result.get("content", "")),
        )

    @staticmethod
    def _make_snippet(content: str, max_len: int = 200) -> str:
        """截取内容前 N 字作为摘要。"""
        text = re.sub(r"[#*\-\[\]|`]", "", content[: max_len * 2])
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_len] + ("…" if len(text) > max_len else "")

    @classmethod
    def _classify_job(cls, result: dict) -> str:
        """根据标签或标题推断岗位的业务分类。"""
        metadata = result.get("metadata", {})
        tags = metadata.get("tags", [])

        # 按标签推断
        for tag in tags:
            tag_lower = tag.lower() if isinstance(tag, str) else ""
            if tag_lower in TAG_CATEGORY_MAP:
                return TAG_CATEGORY_MAP[tag_lower]
        # 按标题关键词推断
        title = metadata.get("title", "").lower() or result.get("filename", "").lower()
        if any(k in title for k in ["前端", "web"]):
            return "前端"
        if any(k in title for k in ["后端", "java", "go", "python"]):
            return "后端"
        if any(k in title for k in ["ai", "算法", "机器学习", "深度学习", "nlp"]):
            return "AI"
        if any(k in title for k in ["数据"]):
            return "数据"
        if any(k in title for k in ["运维", "sre"]):
            return "运维"
        if any(k in title for k in ["测试"]):
            return "测试"
        if any(k in title for k in ["产品"]):
            return "产品"
        if any(k in title for k in ["运营"]):
            return "运营"
        if any(k in title for k in ["安全", "渗透"]):
            return "安全"
        return "其他"
