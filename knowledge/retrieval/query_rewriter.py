"""Employment-domain query analysis and deterministic rewrite."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class RewriteResult:
    original_query: str
    rewritten_query: str
    intent: str
    keywords: list[str]
    filters: dict

    def as_dict(self) -> dict:
        return asdict(self)


class QueryRewriteService:
    INTENTS = (
        ("resume_optimization", ("简历", "项目经历", "STAR"), ["resume", "jobs", "skills"], "校招简历优化与岗位能力表达"),
        ("interview_preparation", ("面试", "笔试", "八股"), ["interview", "skills"], "校招面试核心知识与准备策略"),
        ("growth_planning", ("学习路线", "成长", "规划", "还差什么", "技能缺口"), ["roadmap", "skills", "jobs"], "目标岗位核心技能要求、技能缺口与成长路线"),
        ("job_matching", ("岗位", "工作", "就业", "求职", "匹配"), ["jobs", "skills", "roadmap"], "目标岗位核心技能要求及就业竞争力"),
    )

    def __init__(self, enabled: bool = True, llm_enabled: bool = False, llm_rewriter=None) -> None:
        self.enabled = enabled
        self.llm_enabled = llm_enabled
        self.llm_rewriter = llm_rewriter

    def analyze(self, query: str) -> RewriteResult:
        original = query.strip()
        intent, categories, template = "employment_qa", [], "大学生就业场景知识与实践建议"
        for name, markers, values, rewrite in self.INTENTS:
            if any(marker.lower() in original.lower() for marker in markers):
                intent, categories, template = name, values, rewrite
                break
        keywords = self.extract_keywords(original)
        rewritten = original if not self.enabled else f"{template} {' '.join(keywords[:8])}".strip()
        if self.llm_enabled and self.llm_rewriter:
            rewritten = str(self.llm_rewriter(original, rewritten)).strip() or rewritten
        return RewriteResult(original, rewritten, intent, keywords, {"categories": categories})

    def rewrite(self, query: str, context: dict | None = None) -> str:
        return self.analyze(query).rewritten_query

    @staticmethod
    def extract_keywords(query: str) -> list[str]:
        terms = re.findall(r"[A-Za-z][A-Za-z0-9_+#.\-]{1,}|[\u4e00-\u9fff]{2,8}", query)
        return list(dict.fromkeys(term for term in terms if term))


QueryRewriter = QueryRewriteService
