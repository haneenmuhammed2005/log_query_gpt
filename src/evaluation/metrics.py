"""
Evaluation metrics for retrieval system
Implements Precision@K, Recall@K, MRR, and NDCG with real matching
"""

import numpy as np
from typing import List, Dict, Tuple, Set
from sklearn.metrics.pairwise import cosine_similarity


class RetrievalEvaluator:
    """Evaluate retrieval system performance with multiple metrics"""
    
    def __init__(self):
        pass
    
    def calculate_mrr(self, retrieved_indices: List[List[int]], 
                     ground_truth_per_query: List[List[int]]) -> float:
        """
        Mean Reciprocal Rank
        Measures where the first relevant document appears
        
        Args:
            retrieved_indices: List of retrieved document indices for each query
            ground_truth_per_query: List of relevant document indices for each query
        
        Returns:
            MRR score (0-1), higher is better
        
        Example:
            retrieved_indices = [[5, 1, 3, 7], [2, 4, 6]]
            ground_truth = [[1, 3], [6, 8]]
            MRR considers first match: 1 appears at position 2 (score=1/2)
                                       6 appears at position 3 (score=1/3)
            MRR = (0.5 + 0.333) / 2 = 0.417
        """
        reciprocal_ranks = []
        
        for retrieved, ground_truth in zip(retrieved_indices, ground_truth_per_query):
            ground_truth_set = set(ground_truth)
            
            # Find position of first relevant item
            for rank, idx in enumerate(retrieved, 1):
                if idx in ground_truth_set:
                    reciprocal_ranks.append(1.0 / rank)
                    break
            else:
                # No relevant item found
                reciprocal_ranks.append(0.0)
        
        if not reciprocal_ranks:
            return 0.0
        
        return float(np.mean(reciprocal_ranks))
    
    def calculate_precision_at_k(self, retrieved: List[int], 
                                 relevant: List[int], 
                                 k: int = 5) -> float:
        """
        Precision@K: Fraction of top-K results that are relevant
        
        Args:
            retrieved: List of retrieved document indices (ordered by relevance)
            relevant: List of relevant document indices (ground truth)
            k: Number of top results to consider
        
        Returns:
            Precision score (0-1)
        
        Example:
            retrieved = [1, 2, 3, 4, 5]
            relevant = [1, 3, 7]
            k = 5
            Relevant in top-5: [1, 3] = 2 items
            P@5 = 2/5 = 0.4
        """
        if k <= 0:
            return 0.0
        
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        
        relevant_retrieved = len([idx for idx in retrieved_k if idx in relevant_set])
        
        return relevant_retrieved / k
    
    def calculate_recall_at_k(self, retrieved: List[int], 
                             relevant: List[int], 
                             k: int = 5) -> float:
        """
        Recall@K: Fraction of relevant items found in top-K
        
        Args:
            retrieved: List of retrieved document indices
            relevant: List of relevant document indices
            k: Number of top results to consider
        
        Returns:
            Recall score (0-1)
        
        Example:
            retrieved = [1, 2, 3, 4, 5]
            relevant = [1, 3, 7, 9]  # 4 relevant items total
            k = 5
            Found in top-5: [1, 3] = 2 items
            R@5 = 2/4 = 0.5
        """
        if len(relevant) == 0:
            return 0.0
        
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        
        relevant_retrieved = len([idx for idx in retrieved_k if idx in relevant_set])
        
        return relevant_retrieved / len(relevant)
    
    def calculate_f1_at_k(self, retrieved: List[int],
                          relevant: List[int],
                          k: int = 5) -> float:
        """
        F1 score at K: Harmonic mean of Precision@K and Recall@K
        
        Returns:
            F1 score (0-1)
        """
        precision = self.calculate_precision_at_k(retrieved, relevant, k)
        recall = self.calculate_recall_at_k(retrieved, relevant, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_ndcg(self, retrieved_indices: List[int],
                      relevance_scores: Dict[int, float],
                      k: int = 5) -> float:
        """
        Normalized Discounted Cumulative Gain
        Measures ranking quality considering position and relevance
        
        Args:
            retrieved_indices: Ordered list of retrieved document indices
            relevance_scores: Dict mapping doc_id -> relevance score (0-1 or binary)
            k: Number of top results to consider
        
        Returns:
            NDCG score (0-1)
        
        Example:
            retrieved_indices = [5, 1, 3, 7, 2]
            relevance_scores = {1: 1.0, 3: 0.8, 7: 0.3, others: 0}
            NDCG considers both presence and position
        """
        def dcg(scores, k):
            """Calculate DCG for given scores"""
            scores_k = scores[:k]
            if len(scores_k) == 0:
                return 0.0
            
            # DCG = sum(rel_i / log2(i+2)) for i in positions
            dcg_value = sum([
                score / np.log2(i + 2)  # i+2 because i starts at 0
                for i, score in enumerate(scores_k)
            ])
            return dcg_value
        
        # Get relevance scores for retrieved documents
        retrieved_scores = [
            relevance_scores.get(idx, 0.0) 
            for idx in retrieved_indices
        ]
        
        # Calculate DCG of retrieved results
        dcg_score = dcg(retrieved_scores, k)
        
        # Calculate ideal DCG (sorted by relevance)
        all_scores = sorted(relevance_scores.values(), reverse=True)
        ideal_dcg = dcg(all_scores, k)
        
        if ideal_dcg == 0:
            return 0.0
        
        return dcg_score / ideal_dcg
    
    def calculate_map(self, retrieved_indices_list: List[List[int]],
                     ground_truth_list: List[List[int]]) -> float:
        """
        Mean Average Precision (MAP)
        Average of precision values at each relevant document position
        
        Args:
            retrieved_indices_list: Retrieved docs for each query
            ground_truth_list: Relevant docs for each query
        
        Returns:
            MAP score (0-1)
        """
        average_precisions = []
        
        for retrieved, relevant in zip(retrieved_indices_list, ground_truth_list):
            if len(relevant) == 0:
                continue
            
            relevant_set = set(relevant)
            precisions = []
            num_relevant_found = 0
            
            # Calculate precision at each position where we find a relevant doc
            for i, doc_id in enumerate(retrieved, 1):
                if doc_id in relevant_set:
                    num_relevant_found += 1
                    precision_at_i = num_relevant_found / i
                    precisions.append(precision_at_i)
            
            if precisions:
                average_precisions.append(np.mean(precisions))
            else:
                average_precisions.append(0.0)
        
        if not average_precisions:
            return 0.0
        
        return float(np.mean(average_precisions))
    
    def evaluate_retrieval_system(self, 
                                 test_queries: List[str],
                                 retrieved_results: List[List[int]],
                                 ground_truth: List[List[int]],
                                 k_values: List[int] = [1, 5, 10]) -> Dict:
        """
        Comprehensive evaluation across multiple queries
        
        Args:
            test_queries: List of query strings (for reference)
            retrieved_results: Retrieved doc indices for each query
            ground_truth: Relevant doc indices for each query
            k_values: K values to evaluate
        
        Returns:
            Dictionary with all metrics
        """
        
        if len(retrieved_results) != len(ground_truth):
            raise ValueError("Mismatch between retrieved results and ground truth")
        
        metrics = {
            'num_queries': len(test_queries),
            'mrr': self.calculate_mrr(retrieved_results, ground_truth),
            'map': self.calculate_map(retrieved_results, ground_truth)
        }
        
        # Calculate metrics for each K value
        for k in k_values:
            precision_scores = []
            recall_scores = []
            f1_scores = []
            
            for retrieved, relevant in zip(retrieved_results, ground_truth):
                precision_scores.append(
                    self.calculate_precision_at_k(retrieved, relevant, k=k)
                )
                recall_scores.append(
                    self.calculate_recall_at_k(retrieved, relevant, k=k)
                )
                f1_scores.append(
                    self.calculate_f1_at_k(retrieved, relevant, k=k)
                )
            
            metrics[f'precision@{k}'] = float(np.mean(precision_scores))
            metrics[f'recall@{k}'] = float(np.mean(recall_scores))
            metrics[f'f1@{k}'] = float(np.mean(f1_scores))
        
        return metrics
    
    def print_evaluation_report(self, metrics: Dict):
        """Print formatted evaluation report"""
        print("\n" + "=" * 60)
        print("📊 RETRIEVAL EVALUATION REPORT")
        print("=" * 60)
        print(f"Number of Queries: {metrics['num_queries']}")
        print(f"\nOverall Metrics:")
        print(f"  MRR (Mean Reciprocal Rank): {metrics['mrr']:.3f}")
        print(f"  MAP (Mean Average Precision): {metrics['map']:.3f}")
        
        # Print metrics for each K
        print(f"\nMetrics by K:")
        k_values = sorted([int(k.split('@')[1]) for k in metrics.keys() if 'precision@' in k])
        
        for k in k_values:
            print(f"\n  K = {k}:")
            print(f"    Precision@{k}: {metrics[f'precision@{k}']:.3f}")
            print(f"    Recall@{k}: {metrics[f'recall@{k}']:.3f}")
            print(f"    F1@{k}: {metrics[f'f1@{k}']:.3f}")
        
        print("=" * 60)


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("EVALUATION METRICS TEST")
    print("=" * 60)
    
    evaluator = RetrievalEvaluator()
    
    # Test individual metrics
    print("\n1. Testing Precision@K and Recall@K")
    print("-" * 60)
    
    retrieved = [0, 1, 2, 3, 4]  # Retrieved document IDs
    relevant = [1, 3, 7]  # Relevant document IDs
    
    p5 = evaluator.calculate_precision_at_k(retrieved, relevant, k=5)
    r5 = evaluator.calculate_recall_at_k(retrieved, relevant, k=5)
    f1 = evaluator.calculate_f1_at_k(retrieved, relevant, k=5)
    
    print(f"Retrieved: {retrieved}")
    print(f"Relevant: {relevant}")
    print(f"Precision@5: {p5:.3f} (2 relevant out of 5 retrieved)")
    print(f"Recall@5: {r5:.3f} (2 found out of 3 relevant total)")
    print(f"F1@5: {f1:.3f}")
    
    # Test MRR
    print("\n2. Testing Mean Reciprocal Rank (MRR)")
    print("-" * 60)
    
    retrieved_list = [
        [5, 1, 3, 7],  # First relevant (1) at position 2
        [2, 4, 6, 8],  # First relevant (6) at position 3
        [9, 10, 11, 12]  # No relevant items
    ]
    ground_truth_list = [
        [1, 3],
        [6, 8],
        [15, 16]
    ]
    
    mrr = evaluator.calculate_mrr(retrieved_list, ground_truth_list)
    print(f"Query 1: First relevant at position 2 → RR = 1/2 = 0.500")
    print(f"Query 2: First relevant at position 3 → RR = 1/3 = 0.333")
    print(f"Query 3: No relevant found → RR = 0.000")
    print(f"MRR = (0.500 + 0.333 + 0.000) / 3 = {mrr:.3f}")
    
    # Test NDCG
    print("\n3. Testing NDCG")
    print("-" * 60)
    
    retrieved_indices = [5, 1, 3, 7, 2]
    relevance_scores = {1: 3, 3: 2, 7: 1, 2: 0, 5: 0}  # Graded relevance
    
    ndcg = evaluator.calculate_ndcg(retrieved_indices, relevance_scores, k=5)
    print(f"Retrieved: {retrieved_indices}")
    print(f"Relevance: {relevance_scores}")
    print(f"NDCG@5: {ndcg:.3f}")
    
    # Full system evaluation
    print("\n4. Full System Evaluation")
    print("-" * 60)
    
    test_queries = ["query1", "query2", "query3"]
    test_results = [
        [0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9],
        [10, 11, 12, 13, 14]
    ]
    ground_truth = [
        [1, 2],
        [6, 8],
        [12, 15]
    ]
    
    results = evaluator.evaluate_retrieval_system(
        test_queries,
        test_results,
        ground_truth,
        k_values=[1, 3, 5]
    )
    
    evaluator.print_evaluation_report(results)
    
    print("\n✅ Evaluation metrics test complete!")
