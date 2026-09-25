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
    categories = Counter()
    for path in sorted(DOCS.rglob("*.md")):
        if path.name.upper() in {"README.MD", "CHANGELOG.MD"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        meta = front_matter(text)
        reasons = []
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
            reasons.append(f"公开参考来源不足: {references}/5")
        oversized = max((len(part) for part in re.split(r"\n##+ ", text)), default=0)
        if oversized > 3500:
            reasons.append(f"章节过长，不利于 Chunk: {oversized} 字符")
        category = path.relative_to(DOCS).parts[0]
        categories[category] += 1
        if reasons:
            issues.append({"source": path.relative_to(DOCS).as_posix(), "reasons": reasons, "priority": "high" if len(reasons) >= 3 else "medium"})
    report = {"documents": sum(categories.values()), "categories": dict(categories), "needs_improvement": len(issues), "issues": issues}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Knowledge Content Expansion Tasks", "", "由 `scripts/audit_knowledge_content.py` 自动生成。扩写时必须遵循 `documents/扩写要求.txt`，保留原文事实，不虚构数据与来源。", "", "## 执行规则", "", "1. 每次只处理一篇，先查重，再使用至少 3 个公开可靠来源交叉验证。", "2. 补齐 Front Matter、独立语义章节、5 个以上真实链接和 Related Knowledge。", "3. 不覆盖无法核验的数据；不确定内容标注待人工复核。", "4. 完成后运行内容审计、索引入库和 RAG 评测。", "", "## 待处理文件", ""]
    for item in issues:
        lines.append(f"- [{item['priority']}] `{item['source']}`: {'；'.join(item['reasons'])}")
    TASKS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("documents", "categories", "needs_improvement")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
