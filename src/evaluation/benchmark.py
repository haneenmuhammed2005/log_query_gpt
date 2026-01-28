"""
Performance benchmarking suite for ICS-LogQueryGPT
Tests latency, scalability, and accuracy
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import Dict, List
import numpy as np
import pandas as pd

# Import system components
try:
    from embeddings.log_embedder import LogEmbedder
    from vector_db.optimized_search import OptimizedVectorDB
    from rag_system.caching_rag import CachingRAG
    from evaluation.metrics import RetrievalEvaluator
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure Week 1-3 components exist")
    sys.exit(1)


class PerformanceBenchmark:
    """Benchmark system performance across multiple dimensions"""
    
    def __init__(self):
        self.results = {
            'latency': {},
            'scalability': {},
            'accuracy': {},
            'metadata': {}
        }
        self.embedder = None
        self.vector_db = None
        self.rag = None
        self.evaluator = RetrievalEvaluator()
    
    def initialize_system(self, 
                         embeddings_path: str,
                         metadata_path: str):
        """
        Initialize system components
        
        Args:
            embeddings_path: Path to embeddings .npy file
            metadata_path: Path to metadata .csv file
        """
        print("🚀 Initializing system components...")
        
        try:
            # Load embeddings
            print("  📖 Loading embeddings...")
            embeddings = np.load(embeddings_path)
            
            # Load metadata
            print("  📖 Loading metadata...")
            metadata_df = pd.read_csv(metadata_path)
            
            # Create embedder
            print("  🤖 Loading BERT embedder...")
            self.embedder = LogEmbedder()
            
            # Create vector DB
            print("  🔍 Building vector database...")
            self.vector_db = OptimizedVectorDB()
            self.vector_db.build_index(embeddings, metadata_df)
            
            # Create RAG
            print("  💬 Initializing RAG system...")
            self.rag = CachingRAG()
            
            # Store metadata
            self.metadata_df = metadata_df
            self.embeddings = embeddings
            
            print("✅ System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def benchmark_embedding_latency(self, 
                                   test_queries: List[str],
                                   num_runs: int = 3) -> Dict:
        """
        Measure query embedding latency
        
        Args:
            test_queries: Queries to test
            num_runs: Number of runs for averaging
        
        Returns:
            Latency statistics
        """
        print("\n⏱️ Benchmarking Embedding Latency...")
        print("-" * 60)
        
        latencies = []
        
        for query in test_queries:
            query_times = []
            
            for run in range(num_runs):
                start = time.time()
                _ = self.embedder.embed_single_log(query)
                elapsed = time.time() - start
                query_times.append(elapsed)
            
            avg_time = np.mean(query_times)
            latencies.append(avg_time)
            
            print(f"  ✓ '{query[:40]}...': {avg_time*1000:.1f}ms")
        
        stats = {
            'avg_latency_ms': float(np.mean(latencies) * 1000),
            'min_latency_ms': float(np.min(latencies) * 1000),
            'max_latency_ms': float(np.max(latencies) * 1000),
            'std_latency_ms': float(np.std(latencies) * 1000),
            'num_queries': len(test_queries),
            'num_runs': num_runs
        }
        
        print(f"\n  Average: {stats['avg_latency_ms']:.1f}ms")
        
        return stats
    
    def benchmark_search_latency(self,
                                 test_queries: List[str],
                                 k_values: List[int] = [5],
                                 num_runs: int = 3) -> Dict:
        """
        Measure vector search latency
        
        Args:
            test_queries: Queries to test
            k_values: Different K values to test
            num_runs: Runs for averaging
        
        Returns:
            Search latency statistics
        """
        print("\n🔍 Benchmarking Search Latency...")
        print("-" * 60)
        
        results = {}
        
        for k in k_values:
            print(f"\n  Testing K={k}:")
            latencies = []
            
            for query in test_queries:
                # Embed query first
                query_emb = self.embedder.embed_single_log(query)
                
                # Time search only
                query_times = []
                for run in range(num_runs):
                    start = time.time()
                    _ = self.vector_db.search_with_filter(query_emb, k=k)
                    elapsed = time.time() - start
                    query_times.append(elapsed)
                
                avg_time = np.mean(query_times)
                latencies.append(avg_time)
            
            stats = {
                'avg_latency_ms': float(np.mean(latencies) * 1000),
                'min_latency_ms': float(np.min(latencies) * 1000),
                'max_latency_ms': float(np.max(latencies) * 1000),
                'num_queries': len(test_queries)
            }
            
            results[f'k={k}'] = stats
            print(f"    Average: {stats['avg_latency_ms']:.1f}ms")
        
        return results
    
    def benchmark_end_to_end_latency(self,
                                     test_queries: List[str],
                                     k: int = 5,
                                     num_runs: int = 2) -> Dict:
        """
        Measure complete query pipeline latency
        
        Args:
            test_queries: Test queries
            k: Number of logs to retrieve
            num_runs: Runs for averaging
        
        Returns:
            End-to-end latency statistics
        """
        print("\n🚀 Benchmarking End-to-End Latency...")
        print("-" * 60)
        
        latencies = {
            'embed': [],
            'search': [],
            'generate': [],
            'total': []
        }
        
        for query in test_queries:
            print(f"\n  Testing: '{query[:40]}...'")
            
            for run in range(num_runs):
                # Embedding time
                start = time.time()
                query_emb = self.embedder.embed_single_log(query)
                embed_time = time.time() - start
                
                # Search time
                start = time.time()
                retrieved_logs = self.vector_db.search_with_filter(query_emb, k=k)
                search_time = time.time() - start
                
                # Generation time (cache disabled for benchmarking)
                start = time.time()
                _ = self.rag.generate_with_cache(
                    query, 
                    retrieved_logs,
                    mode='analysis',
                    use_cache=False
                )
                generate_time = time.time() - start
                
                total_time = embed_time + search_time + generate_time
                
                latencies['embed'].append(embed_time)
                latencies['search'].append(search_time)
                latencies['generate'].append(generate_time)
                latencies['total'].append(total_time)
            
            print(f"    Embedding: {np.mean(latencies['embed'][-num_runs:])*1000:.1f}ms")
            print(f"    Search: {np.mean(latencies['search'][-num_runs:])*1000:.1f}ms")
            print(f"    Generation: {np.mean(latencies['generate'][-num_runs:]):.2f}s")
            print(f"    Total: {np.mean(latencies['total'][-num_runs:]):.2f}s")
        
        stats = {
            'avg_embed_ms': float(np.mean(latencies['embed']) * 1000),
            'avg_search_ms': float(np.mean(latencies['search']) * 1000),
            'avg_generate_s': float(np.mean(latencies['generate'])),
            'avg_total_s': float(np.mean(latencies['total'])),
            'num_queries': len(test_queries),
            'k': k
        }
        
        return stats
    
    def benchmark_scalability(self,
                             test_query: str,
                             k_values: List[int] = [1, 5, 10, 20, 50]) -> Dict:
        """
        Test performance with different K values
        
        Args:
            test_query: Single query to test
            k_values: Different K values
        
        Returns:
            Scalability results
        """
        print("\n📈 Benchmarking Scalability...")
        print("-" * 60)
        
        results = {}
        query_emb = self.embedder.embed_single_log(test_query)
        
        for k in k_values:
            start = time.time()
            results_list = self.vector_db.search_with_filter(query_emb, k=k)
            elapsed = time.time() - start
            
            results[f'k={k}'] = {
                'latency_ms': float(elapsed * 1000),
                'num_results': len(results_list)
            }
            
            print(f"  K={k:3d}: {elapsed*1000:6.1f}ms ({len(results_list)} results)")
        
        return results
    
    def benchmark_retrieval_accuracy(self,
                                    test_set: List[Dict],
                                    k_values: List[int] = [1, 5, 10]) -> Dict:
        """
        Measure retrieval accuracy using test set
        
        Args:
            test_set: Test set with ground truth
            k_values: K values to evaluate
        
        Returns:
            Accuracy metrics
        """
        print("\n🎯 Benchmarking Retrieval Accuracy...")
        print("-" * 60)
        
        if not test_set:
            print("  ⚠️ No test set provided, skipping accuracy benchmark")
            return {}
        
        # Collect results for all queries
        all_retrieved = []
        all_ground_truth = []
        test_queries = []
        
        for test_case in test_set:
            query = test_case['query']
            ground_truth = test_case['ground_truth_indices']
            
            # Embed and search
            query_emb = self.embedder.embed_single_log(query)
            retrieved_logs = self.vector_db.search_with_filter(
                query_emb, 
                k=max(k_values)
            )
            
            # Extract indices (we don't have direct indices, so approximate)
            # In a real system, you'd track indices through metadata
            retrieved_indices = list(range(len(retrieved_logs)))
            
            all_retrieved.append(retrieved_indices)
            all_ground_truth.append(ground_truth)
            test_queries.append(query)
            
            print(f"  ✓ {query}")
        
        # Calculate metrics
        metrics = self.evaluator.evaluate_retrieval_system(
            test_queries,
            all_retrieved,
            all_ground_truth,
            k_values=k_values
        )
        
        # Print results
        self.evaluator.print_evaluation_report(metrics)
        
        return metrics
    
    def run_full_benchmark(self,
                          embeddings_path: str,
                          metadata_path: str,
                          test_set_path: str = None,
                          output_file: str = 'data/evaluation/benchmark_results.json') -> Dict:
        """
        Run complete benchmark suite
        
        Args:
            embeddings_path: Path to embeddings
            metadata_path: Path to metadata
            test_set_path: Optional path to test set
            output_file: Where to save results
        
        Returns:
            Complete benchmark results
        """
        print("\n" + "=" * 60)
        print("🚀 RUNNING FULL BENCHMARK SUITE")
        print("=" * 60)
        
        # Initialize system
        if not self.initialize_system(embeddings_path, metadata_path):
            return {'error': 'System initialization failed'}
        
        # Test queries
        test_queries = [
            "Show me authentication failures",
            "What errors occurred?",
            "Find network timeouts",
            "Modbus communication issues",
            "Security events"
        ]
        
        # Run benchmarks
        print("\n" + "=" * 60)
        self.results['latency']['embedding'] = self.benchmark_embedding_latency(
            test_queries, num_runs=3
        )
        
        print("\n" + "=" * 60)
        self.results['latency']['search'] = self.benchmark_search_latency(
            test_queries, k_values=[5, 10], num_runs=3
        )
        
        print("\n" + "=" * 60)
        self.results['latency']['end_to_end'] = self.benchmark_end_to_end_latency(
            test_queries[:2],  # Fewer queries for E2E due to API costs
            k=5,
            num_runs=2
        )
        
        print("\n" + "=" * 60)
        self.results['scalability'] = self.benchmark_scalability(
            test_queries[0],
            k_values=[1, 5, 10, 20, 50]
        )
        
        # Accuracy (if test set available)
        if test_set_path and os.path.exists(test_set_path):
            print("\n" + "=" * 60)
            with open(test_set_path, 'r') as f:
                test_set = json.load(f)
            
            self.results['accuracy'] = self.benchmark_retrieval_accuracy(
                test_set[:5],  # Use subset for speed
                k_values=[1, 5, 10]
            )
        
        # Add metadata
        self.results['metadata'] = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'embeddings_path': embeddings_path,
            'metadata_path': metadata_path,
            'num_logs': len(self.metadata_df),
            'embedding_dim': self.embeddings.shape[1]
        }
        
        # Save results
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        self.print_summary()
        
        print(f"\n💾 Results saved to {output_file}")
        
        return self.results
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        
        if 'latency' in self.results and 'end_to_end' in self.results['latency']:
            e2e = self.results['latency']['end_to_end']
            print(f"Average End-to-End Latency: {e2e['avg_total_s']:.2f}s")
            print(f"  - Embedding: {e2e['avg_embed_ms']:.1f}ms")
            print(f"  - Search: {e2e['avg_search_ms']:.1f}ms")
            print(f"  - Generation: {e2e['avg_generate_s']:.2f}s")
        
        if 'accuracy' in self.results and self.results['accuracy']:
            acc = self.results['accuracy']
            print(f"\nRetrieval Accuracy:")
            print(f"  - MRR: {acc.get('mrr', 0):.3f}")
            print(f"  - Precision@5: {acc.get('precision@5', 0):.3f}")
            print(f"  - Recall@5: {acc.get('recall@5', 0):.3f}")
        
        print("=" * 60)


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Check for required files
    required_files = [
        ('data/embeddings/HDFS_enhanced.npy', 'embeddings'),
        ('data/processed_logs/HDFS_enhanced.csv', 'metadata')
    ]
    
    embeddings_path = None
    metadata_path = None
    
    for filepath, file_type in required_files:
        if os.path.exists(filepath):
            if file_type == 'embeddings':
                embeddings_path = filepath
            elif file_type == 'metadata':
                metadata_path = filepath
            print(f"✓ Found {file_type}: {filepath}")
        else:
            print(f"⚠️ Missing {file_type}: {filepath}")
    
    if not embeddings_path or not metadata_path:
        print("\n❌ Required files not found!")
        print("Please ensure you've completed Week 2 & 3:")
        print("  - Run embedding pipeline")
        print("  - Process logs with protocol detection")
        sys.exit(1)
    
    # Optional test set
    test_set_path = 'data/evaluation/test_set.json'
    if not os.path.exists(test_set_path):
        print(f"\n⚠️ Test set not found: {test_set_path}")
        print("   Accuracy benchmarks will be skipped")
        test_set_path = None
    
    # Run benchmark
    print("\n")
    benchmark = PerformanceBenchmark()
    
    results = benchmark.run_full_benchmark(
        embeddings_path=embeddings_path,
        metadata_path=metadata_path,
        test_set_path=test_set_path,
        output_file='data/evaluation/benchmark_results.json'
    )
    
    print("\n✅ Benchmark complete!")
