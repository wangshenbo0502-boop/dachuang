# corpus/ — 原始语料库

## 目录职责
存放原始二进制文件（PDF、Word、Excel、图片等），作为知识库的原始数据来源。

## 当前状态
【预留】当前为空。所有知识已直接整理为 `documents/` 下的 Markdown 文件。

## 未来扩展
- 支持上传 PDF 简历模板、企业招聘简章、行业报告等原始文件
- 通过 `loader/pdf_loader.py` 和 `loader/docx_loader.py` 提取文本
- 通过 `parser/document_parser.py` 统一解析
