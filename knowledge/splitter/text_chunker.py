"""
文件名称：text_chunker.py
文件作用：文本切块器（预留接口）。
当前版本：关闭。仅保留接口框架。
未来版本：采用 Recursive Character Text Splitter 算法实现智能切块。
参考：LangChain RecursiveCharacterTextSplitter。
"""
class TextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        """TODO: 未来实现文本切块"""
        pass

    def split_documents(self, documents: list[dict]) -> list[dict]:
        """TODO: 未来实现批量文档切块"""
        pass
