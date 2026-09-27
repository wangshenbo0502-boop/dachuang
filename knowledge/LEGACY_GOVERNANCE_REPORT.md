# 知识库历史文档治理报告

更新时间：2026-09-27

## 治理范围

本轮处理 `knowledge/documents/` 下原有的 244 篇历史 Markdown 文档，新增的 `application` 类 8 篇文档保持不变。

## 已完成

- 所有历史文档补齐 `id`、`title`、`category`、`tags`、`keywords`、`summary`、`source`、`updated_at`、`status`。
- 为中文文件名生成稳定的路径哈希 ID，避免同名或同前缀条目在索引中冲突。
- 统一标题层级：文档保留一个一级标题，后续内容使用二级标题，便于分块检索。
- 对过长章节按段落边界拆分，避免单个语义块过大。
- 对过短项目文档补充实践验证、展示材料和求职证据规范。
- 为没有关联章节的文档补充 `Related Knowledge`。
- 对缺少公开链接的文档标记 `status: "needs_source_review"`，没有虚构来源。
- 重新生成 `knowledge/evaluation/reports/content_audit.json` 和 `knowledge/CONTENT_EXPANSION_TASKS.md`。

## 当前结果

| 指标 | 结果 |
|---|---:|
| 知识文档总数 | 252 |
| 本轮治理历史文档 | 244 |
| 结构性问题 | 0 |
| Front Matter 缺失 | 0 |
| 重复 ID | 0 |
| 来源待人工复核 | 135 |

“来源待人工复核”不等于文档内容一定错误，而是表示当前正文中可识别的公开链接少于 5 个，或者只有来源名称没有可访问 URL。企业、市场、政策和技术事实需要逐篇补充能够直接支撑正文的官方或一手来源，不能用无关链接凑数。

## 可重复执行

```powershell
python scripts/govern_legacy_knowledge.py
python scripts/audit_knowledge_content.py
```

治理脚本只处理历史分类目录，不改写 `application` 类新增知识；重复运行不会追加重复的关联章节。

## 后续来源治理顺序

1. `companies/`：优先补企业官网、招聘官网、年报或交易所公告。
2. `market/`：优先补国家统计部门、行业主管部门、上市公司公告和研究机构原始报告。
3. `policies/`：优先补中国政府网、部委官网和法律法规数据库，并记录访问日期。
4. `jobs/`、`skills/`、`interview/`：优先补官方技术文档、职业分类和教育机构资料。
5. `projects/`、`resume/`、`roadmap/`：区分通用方法和项目自拟内容，只有外部事实才要求外部来源。

