# parser/ — 文档解析器

## 目录职责
将加载的文档内容解析为结构化数据（提取元数据、标题、正文）。

## 模块文件
| 文件 | 状态 | 说明 |
|------|------|------|
| `markdown_parser.py` | 框架已就绪 | 解析 YAML Front Matter + Markdown Body |
| `document_parser.py` | 框架已就绪 | 通用解析器，按文件类型分发 |
| `text_cleaner.py` | 框架已就绪 | 文本清洗、格式化、去噪 |

## 当前实现
- `MarkdownParser`：提取 YAML 元数据 + 正文内容

## 未来扩展
- 支持 PDF 解析（表格/图片提取）
- 支持 Word 段落和样式解析
- 支持中文分词和关键词自动提取
