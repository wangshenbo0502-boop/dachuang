# chunk/ — 文本切块器

## 目录职责
将长文档切分为适合 Embedding 模型的文本块。

## 当前状态
【预留】当前关键词检索阶段无需切块。启用 Embedding 后激活。

## 未来实现
- 采用 Recursive Character Text Splitter 算法
- 参考 LangChain `RecursiveCharacterTextSplitter`
- 按 `config/chunk_config.json` 配置切块参数
- 支持按文档类型定制切块策略

## 文件
| 文件 | 状态 |
|------|------|
| `text_chunker.py` | 预留接口 |
