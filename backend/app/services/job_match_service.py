"""
文件名称：job_match_service.py
文件作用：岗位匹配业务逻辑层。
负责岗位搜索、详情查询与技能匹配（含AI智能匹配）。
"""

import re
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.ai.prompts import SystemPrompts, JobMatchPrompts
from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.skill_synonyms import normalize_skill, is_skill_match
from app.models.job import JobMatchRecord
from app.models.user import User
from app.utils.exceptions import ResourceNotFoundError
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
    "html": "前端", "css": "前端", "javascript": "前端", "typescript": "前端",
    "vue": "前端", "react": "前端", "web": "前端", "前端": "前端",
    "java": "后端", "spring": "后端", "go": "后端", "rust": "后端",
    "c++": "后端", "python": "后端", "后端": "后端", "sql": "后端",
    "mysql": "后端", "redis": "后端", "mongodb": "后端",
    "ai": "AI", "算法": "AI", "机器学习": "AI", "深度学习": "AI",
    "nlp": "AI", "pytorch": "AI", "tensorflow": "AI",
    "数据分析": "数据", "数据工程": "数据", "数据仓库": "数据",
    "android": "移动端", "ios": "移动端", "移动端": "移动端",
    "运维": "运维", "测试": "测试", "产品": "产品", "运营": "运营", "安全": "安全",
}


class JobMatchService:
    """岗位匹配服务：提供岗位搜索、详情与AI增强匹配能力。"""

    _instance: Optional["JobMatchService"] = None

    def __init__(self) -> None:
        self._knowledge = KnowledgeService.instance()
        self._all_jobs: dict[str, dict] = {}
        self._loaded = False
        self._ai_client = DeepSeekClient.instance()

    @classmethod
    def instance(cls) -> "JobMatchService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._all_jobs = {doc["doc_id"]: doc for doc in self._knowledge.list_documents("jobs")}
        self._loaded = True

    # ── 岗位列表搜索 ──

    def search_jobs(
        self, keyword: str = "", category: str = None, page: int = 1, page_size: int = 20
    ) -> JobListResponse:
        self._ensure_loaded()
        if keyword:
            results = self._knowledge.search(keyword, category="jobs", top_k=50)
        else:
            results = [
                {"doc_id": j["doc_id"], "content": j["content"], "metadata": j["metadata"], "score": 0}
                for j in self._all_jobs.values()
            ]
        if category:
            results = [r for r in results if self._classify_job(r) == category]
        total = len(results)
        start = (page - 1) * page_size
        page_results = results[start : start + page_size]
        items = [self._to_job_brief(r) for r in page_results]
        return JobListResponse(total=total, items=items, keyword=keyword or None)

    # ── 岗位详情 ──

    def get_job_detail(self, job_id: str) -> Optional[JobDetail]:
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

    # ── 岗位匹配（AI增强版） ──

    def match_jobs(self, request: JobMatchRequest) -> JobMatchResponse:
        """根据用户技能列表做岗位匹配。

        分两步：
        1. 关键词快速筛选（粗排）
        2. AI深度匹配分析（精排，Top-K）
        """
        self._ensure_loaded()
        # 标准化用户技能（使用同义词映射）
        user_skills_lower = [s.strip().lower() for s in request.skills]
        user_skills_normalized = set()
        for s in user_skills_lower:
            user_skills_normalized.add(normalize_skill(s))

        # 步骤1：关键词粗排
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

            required_skills = self._knowledge.get_skill_requirements(doc_id) or [
                t.lower() if isinstance(t, str) else "" for t in tags if t
            ]

            matched, missing = [], []
            for skill in required_skills:
                skill_normalized = normalize_skill(skill)
                # 使用同义词感知的匹配
                if skill_normalized in user_skills_normalized:
                    matched.append(skill)
                else:
                    # 回退：模糊匹配（子串匹配）
                    if any(
                        skill_normalized in us or us in skill_normalized
                        for us in user_skills_normalized
                    ):
                        matched.append(skill)
                    else:
                        missing.append(skill)
            if not required_skills:
                continue
            score = round(len(matched) / len(required_skills) * 100, 1)

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

        matches.sort(key=lambda m: m.match_score, reverse=True)
        top_k = request.top_k

        # 步骤2：对Top-K岗位进行AI深度匹配分析
        if not self._ai_client.is_mock_mode and matches:
            ai_top_k = min(top_k, len(matches))
            ai_matches = self._ai_enhance_matches(
                user_skills=request.skills,
                matches=matches[:ai_top_k],
            )
            matches[:ai_top_k] = ai_matches

        matches = matches[:top_k]
        return JobMatchResponse(
            user_skills=request.skills,
            total_matches=len(matches),
            matches=matches,
        )

    def _ai_enhance_matches(
        self, user_skills: list[str], matches: list[MatchedJob]
    ) -> list[MatchedJob]:
        """对匹配结果进行AI深度分析，更新匹配分数和理由"""
        enhanced = []
        for match in matches:
            job = self._all_jobs.get(match.job_id)
            if not job:
                enhanced.append(match)
                continue

            metadata = job.get("metadata", {})
            content = job.get("content", "")
            job_title = metadata.get("title", match.job_id)
            required_skills = self._knowledge.get_skill_requirements(match.job_id) or []

            try:
                system_prompt = SystemPrompts.job_matcher() or "你是一位资深的IT行业招聘技术专家。"
                user_prompt = JobMatchPrompts.build_user_prompt(
                    name="学生",
                    user_skills=[{"name": s, "proficiency": "掌握"} for s in user_skills],
                    user_projects=[],
                    job_title=job_title,
                    job_description=content[:500],
                    job_requirements="、".join(required_skills),
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                ai_result = self._ai_client.chat_json(messages, temperature=0.3)

                ai_match_score = ai_result.get("match_score", match.match_score)
                match_reason = ai_result.get("match_reason", "")

                # 更新匹配结果
                match.match_score = min(ai_match_score, match.match_score + 20)
                match.match_reason = match_reason
                match.missing_skills = ai_result.get("missing_skills", match.missing_skills)
                match.learning_suggestions = ai_result.get("learning_suggestions", [])
                match.interview_focus = ai_result.get("interview_focus", [])
            except Exception:
                # AI增强失败，保持原始匹配结果
                pass

            enhanced.append(match)

        return enhanced

    # ── 匹配记录持久化 ──

    def save_match_record(self, db: Session, request: JobMatchRequest, response: JobMatchResponse) -> JobMatchRecord:
        if request.user_id is not None and db.get(User, request.user_id) is None:
            raise ResourceNotFoundError(f"用户 {request.user_id} 不存在")
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
        text = re.sub(r"[#*\-\[\]|`]", "", content[: max_len * 2])
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_len] + ("…" if len(text) > max_len else "")

    @classmethod
    def _classify_job(cls, result: dict) -> str:
        metadata = result.get("metadata", {})
        tags = metadata.get("tags", [])
        for tag in tags:
            tag_lower = tag.lower() if isinstance(tag, str) else ""
            if tag_lower in TAG_CATEGORY_MAP:
                return TAG_CATEGORY_MAP[tag_lower]
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
