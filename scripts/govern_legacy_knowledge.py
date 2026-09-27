"""Conservatively normalize legacy knowledge documents.

The migration preserves the existing body text and only adds metadata,
cross-links, chunk-friendly headings, and a small practice appendix for
short project entries. It deliberately does not invent factual references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "knowledge" / "documents"
SKIP = {"README.md", "CHANGELOG.md"}
REQUIRED = ["id", "title", "category", "tags", "keywords", "summary", "source", "updated_at", "status"]

CATEGORY_LABELS = {
    "companies": "企业",
    "competition": "竞赛",
    "interview": "面试",
    "jobs": "岗位",
    "market": "市场",
    "policies": "政策",
    "projects": "项目",
    "resume": "简历",
    "roadmap": "成长路线",
    "skills": "技能",
    "application": "求职投递",
}


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    raw = text[3:end]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    body = text[end + len("\n---") :].lstrip("\r\n")
    return meta, body


def yaml_value(value: str):
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [x.strip().strip('"\'') for x in value[1:-1].split(",") if x.strip()]
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return value.strip('"\'')


def as_list(value: str | list | None) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    if value is None:
        return []
    parsed = yaml_value(str(value))
    if isinstance(parsed, list):
        return [str(x) for x in parsed if str(x).strip()]
    return [str(parsed)] if str(parsed).strip() else []


def clean_text(value: str) -> str:
    value = re.sub(r"[`*_>#|]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def title_from(path: Path, body: str, meta: dict[str, str]) -> str:
    existing = clean_text(str(yaml_value(meta.get("title", ""))))
    if existing:
        return existing
    for line in body.splitlines():
        if line.startswith("# "):
            return clean_text(line[2:])
    return path.stem.replace("_", " ")


def derive_terms(title: str, body: str, category: str) -> list[str]:
    terms = [title, CATEGORY_LABELS.get(category, category)]
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+.#/-]{1,}|[\u4e00-\u9fff]{2,8}", title):
        terms.append(token)
    for line in body.splitlines():
        if line.startswith("## "):
            heading = clean_text(line[3:])
            if heading:
                terms.append(heading)
    result = []
    for term in terms:
        term = clean_text(term)
        if term and term not in result:
            result.append(term)
    return result[:12]


def summary_from(body: str, title: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body)
    for paragraph in paragraphs:
        text = clean_text(paragraph)
        if text and not text.startswith("#") and len(text) >= 20:
            return text[:156].rstrip("，。；") + "。"
    return f"围绕{title}整理的大学生求职与职业发展知识，包含概念、实践要点和风险提示。"


def existing_sources(body: str, meta: dict[str, str]) -> list[str]:
    sources = as_list(meta.get("source"))
    if sources:
        return sources
    urls = re.findall(r"https?://[^\s)>]+", body)
    return urls[:12]


def render_front(meta: dict[str, str]) -> str:
    lines = ["---"]
    for key in REQUIRED:
        value = meta[key]
        if isinstance(value, list):
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            escaped = str(value).replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
    lines.append("---")
    return "\n".join(lines)


def related_section(path: Path, all_paths: list[Path]) -> str:
    category = path.parent.name
    candidates = [p for p in all_paths if p.parent.name == category and p != path]
    candidates = sorted(candidates, key=lambda p: p.name)[:3]
    if not candidates:
        return "\n## Related Knowledge\n\n暂无同类条目，后续补充。\n"
    lines = ["\n## Related Knowledge\n"]
    for candidate in candidates:
        lines.append(f"- [{candidate.stem}]({candidate.name})")
    return "\n".join(lines) + "\n"


def split_long_sections(body: str, limit: int = 3500) -> tuple[str, int]:
    matches = list(re.finditer(r"(?m)^##+ ", body))
    if not matches:
        return body, 0
    output: list[str] = []
    cursor = 0
    inserted = 0
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        output.append(body[cursor : match.start()])
        section = body[match.start() : end]
        if len(section) <= limit:
            output.append(section)
        else:
            header_end = section.find("\n")
            header = section if header_end < 0 else section[:header_end]
            content = "" if header_end < 0 else section[header_end + 1 :]
            parts = []
            while len(content) > limit:
                cut = content.rfind("\n\n", 0, limit)
                if cut < 600:
                    cut = content.rfind("\n", 0, limit)
                if cut < 300:
                    cut = limit
                parts.append(content[:cut].rstrip())
                content = content[cut:].lstrip("\r\n")
            parts.append(content.rstrip())
            output.append(header + "\n" + parts[0] + "\n")
            for part_no, part in enumerate(parts[1:], 2):
                output.append(f"## {clean_text(header.lstrip('# ').strip())}（续{part_no}）\n\n{part}\n")
                inserted += 1
        cursor = end
    output.append(body[cursor:])
    return "".join(output), inserted


def normalize_heading_levels(body: str) -> str:
    """Keep the first H1 as the document title and make later H1s sections."""
    seen_h1 = False
    lines = []
    for line in body.splitlines():
        if line.startswith("# "):
            if not seen_h1:
                seen_h1 = True
            else:
                line = "## " + line[2:]
        lines.append(line)
    return "\n".join(lines) + ("\n" if body.endswith(("\n", "\r")) else "")


def project_appendix(title: str) -> str:
    return f"""
## {title}的实践与求职证据

使用本项目知识时，建议把项目目标、使用者、核心流程、个人负责范围、技术选择、异常处理、测试结果和可展示材料分别记录。描述项目经历时，优先写清楚本人完成了什么、解决了什么问题、产出了什么结果；没有可靠数据时不要补写用户量、性能提升或商业收益。

实践验证可以从最小可运行版本开始：准备一组正常输入、一组边界输入和一组错误输入，记录系统行为、预期结果和待改进点。展示材料可包括架构图、接口文档、测试记录、部署截图、演示地址、代码仓库或复盘文档，但涉及个人信息、企业数据和商业秘密时应脱敏。

面向求职时，可将本项目整理为一张能力证据卡，注明项目时间、团队规模、个人职责、关键决策和证据链接。AI 只能帮助压缩表达和匹配岗位关键词，不能新增不存在的角色、奖项、数字或技术成果。
""".strip() + "\n"


def migrate(path: Path, all_paths: list[Path], today: str) -> dict[str, int | str]:
    text = path.read_text(encoding="utf-8-sig")
    original = text
    old_meta, body = split_front_matter(text)
    category = path.parent.name
    title = title_from(path, body, old_meta)
    sources = existing_sources(body, old_meta)
    urls = len(re.findall(r"https?://", body))
    status = str(yaml_value(old_meta.get("status", ""))).strip()
    if not status:
        status = "needs_source_review" if urls < 5 else "migrated_pending_review"
    slug = re.sub(r"[^a-z0-9]+", "-", f"{category}-{path.stem.lower()}").strip("-")
    path_hash = hashlib.sha1(path.as_posix().encode("utf-8")).hexdigest()[:10]
    if not slug or slug == category:
        slug = category
    slug = f"{slug}-{path_hash}"
    meta = {
        "id": slug[:120],
        "title": title,
        "category": category,
        "tags": as_list(old_meta.get("tags")) or [CATEGORY_LABELS.get(category, category), title],
        "keywords": as_list(old_meta.get("keywords")) or derive_terms(title, body, category),
        "summary": str(yaml_value(old_meta.get("summary", ""))).strip() or summary_from(body, title),
        "source": sources or ["待人工核验：原文未提供公开来源"],
        "updated_at": str(yaml_value(old_meta.get("updated_at", old_meta.get("last_update", "")))).strip() or today,
        "status": status,
    }
    # Preserve any existing metadata values that the simple parser can read.
    for key in REQUIRED:
        if key in old_meta and key not in {"id", "title", "category", "source", "updated_at", "last_update"}:
            parsed = yaml_value(old_meta[key])
            meta[key] = parsed if parsed not in ("", []) else meta[key]
    body = normalize_heading_levels(body)
    body, split_count = split_long_sections(body)
    was_short_project = category == "projects" and len(body) < 1800
    if was_short_project:
        body = body.rstrip() + "\n\n" + project_appendix(title)
    if "## Related Knowledge" not in body:
        body = body.rstrip() + related_section(path, all_paths)
    migrated = render_front(meta) + "\n\n" + body.lstrip()
    if migrated != original:
        path.write_text(migrated.rstrip() + "\n", encoding="utf-8")
    return {"changed": int(migrated != original), "split": split_count, "source_review": int(urls < 5), "short_project": int(was_short_project)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    paths = sorted(p for p in DOCS.rglob("*.md") if p.name not in SKIP and p.parent.name != "application")
    today = date.today().isoformat()
    totals = {"documents": len(paths), "changed": 0, "split": 0, "source_review": 0, "short_project": 0}
    for path in paths:
        if args.dry_run:
            continue
        result = migrate(path, paths, today)
        for key in totals:
            if key != "documents":
                totals[key] += int(result.get(key, 0))
    print(json.dumps(totals, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
