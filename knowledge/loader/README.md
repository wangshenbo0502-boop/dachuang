# loader/ — 文档加载器

## 目录职责
负责从不同来源加载原始文档内容，提供统一的加载接口。

## 模块文件
| 文件 | 类型 | 状态 | 说明 |
|------|------|------|------|
| `markdown_loader.py` | Markdown 加载 | 框架已就绪 | 当前主要使用的加载器 |
| `json_loader.py` | JSON 加载 | 框架已就绪 | 兼容旧数据 |
| `pdf_loader.py` | PDF 加载 | 预留 | 未来集成 PyMuPDF |
| `docx_loader.py` | Word 加载 | 预留 | 未来集成 python-docx |
| `excel_loader.py` | Excel 加载 | 预留 | 未来集成 openpyxl |
| `web_loader.py` | 网页加载 | 预留 | 未来集成 requests+BeautifulSoup |

## 当前实现
- `MarkdownLoader`：读取 `documents/` 下的 .md 文件

## 未来扩展
- 支持更多文档格式的自动识别和加载
- 支持从 `corpus/` 目录加载原始文件
