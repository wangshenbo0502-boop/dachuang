"""Audit corpus quality and create a task list for external writing models."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "knowledge" / "documents"
REPORT = ROOT / "knowledge" / "evaluation" / "reports" / "content_audit.json"
TASKS = ROOT / "knowledge" / "CONTENT_EXPANSION_TASKS.md"
REQUIRED = {"id", "title", "category", "tags", "keywords", "summary", "source", "updated_at", "status"}


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    values = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    issues = []
    source_review = []
    categories = Counter()
    for path in sorted(DOCS.rglob("*.md")):
        if path.name.upper() in {"README.MD", "CHANGELOG.MD"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        meta = front_matter(text)
        reasons = []
        source_reasons = []
        if not meta:
            reasons.append("缺少 YAML Front Matter")
        else:
            missing = sorted(REQUIRED - set(meta))
            if missing:
                reasons.append("缺少字段: " + ", ".join(missing))
        if len(text) < 1800:
            reasons.append(f"正文偏短: {len(text)} 字符")
        references = len(re.findall(r"https?://", text))
        if references < 5:
            source_reasons.append(f"公开参考来源不足: {references}/5")
        oversized = max((len(part) for part in re.split(r"\n##+ ", text)), default=0)
        if oversized > 3500:
            reasons.append(f"章节过长，不利于 Chunk: {oversized} 字符")
        category = path.relative_to(DOCS).parts[0]
        categories[category] += 1
        if reasons:
            issues.append({"source": path.relative_to(DOCS).as_posix(), "reasons": reasons, "priority": "high" if len(reasons) >= 3 else "medium"})
        if source_reasons:
            source_review.append({"source": path.relative_to(DOCS).as_posix(), "reasons": source_reasons, "references": references, "status": meta.get("status", "")})
    report = {
        "documents": sum(categories.values()),
        "categories": dict(categories),
        "needs_improvement": len(issues),
        "issues": issues,
        "source_review": len(source_review),
        "source_review_items": source_review,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Knowledge Content Governance Tasks", "", "由 `scripts/audit_knowledge_content.py` 自动生成。结构治理与来源治理分开统计；不得为了满足链接数量虚构来源。", "", "## 执行规则", "", "1. 先完成 Front Matter、关键词、Related Knowledge、篇幅和标题层级治理。", "2. 对企业、市场、政策和技术条目逐篇补充能够支撑正文事实的公开来源。", "3. 不覆盖无法核验的数据；不确定内容标注待人工复核。", "4. 完成后运行内容审计、索引入库和 RAG 评测。", "", "## 结构问题", ""]
    for item in issues:
        lines.append(f"- [{item['priority']}] `{item['source']}`: {'；'.join(item['reasons'])}")
    lines.extend(["", "## 来源复核清单", ""])
    for item in source_review:
        lines.append(f"- `{item['source']}`: {'；'.join(item['reasons'])}；当前状态: {item['status'] or '未标记'}")
    TASKS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("documents", "categories", "needs_improvement")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
