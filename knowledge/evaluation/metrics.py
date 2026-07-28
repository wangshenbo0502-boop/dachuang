"""
文件名称：metrics.py
文件作用：RAG 评估指标定义（预留接口）。
当前版本：关闭。仅保留接口框架。
未来版本：实现 RAGAS 兼容的评估指标。

参考：RAGAS (https://github.com/explodinggradients/ragas)
"""
class RAGEvaluator:
    def evaluate_retrieval(self, queries: list, ground_truth: list) -> dict:
        """TODO: 评估检索质量（MRR/NDCG/Recall@K）"""
        pass
    
    def evaluate_generation(self, answers: list, contexts: list) -> dict:
        """TODO: 评估生成质量（Faithfulness/Relevance）"""
        pass
    
    def evaluate_end_to_end(self, test_cases: list) -> dict:
        """TODO: 端到端评估"""
        pass
