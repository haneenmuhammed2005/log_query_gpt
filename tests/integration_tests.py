"""
Integration tests for complete ICS-LogQueryGPT system
Tests all components working together
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import unittest
import numpy as np
import pandas as pd
import tempfile
import shutil
from typing import List, Dict

# Import all components to test
try:
    from src.embeddings.log_embedder import LogEmbedder
    from src.embeddings.batch_processor import BatchProcessor
    from src.vector_db.optimized_search import OptimizedVectorDB
    from src.rag_system.cost_optimizer import CostOptimizer
    from src.rag_system.caching_rag import CachingRAG
    from src.evaluation.metrics import RetrievalEvaluator
    from src.evaluation.create_test_set import TestSetCreator
    from src.ui.export_results import ResultsExporter
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all Week 1-4 components are in place")
    sys.exit(1)


class TestEmbeddings(unittest.TestCase):
    """Test embedding components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        print("\n🔧 Setting up embedding tests...")
        cls.embedder = LogEmbedder()
    
    def test_single_embedding(self):
        """Test single log embedding"""
        print("\n🧪 Testing single embedding...")
        
        test_log = "authentication failed for user admin"
        embedding = self.embedder.embed_single_log(test_log)
        
        # Check shape
        self.assertEqual(embedding.shape, (768,), 
                        f"Wrong embedding shape: {embedding.shape}")
        
        # Check no NaN values
        self.assertFalse(np.isnan(embedding).any(), 
                        "Embedding contains NaN values")
        
        # Check values are reasonable
        self.assertTrue(-10 < embedding.mean() < 10,
                       "Embedding values seem unreasonable")
        
        print("  ✅ Single embedding test passed")
    
    def test_batch_embedding(self):
        """Test batch embedding"""
        print("\n🧪 Testing batch embedding...")
        
        test_logs = [
            "authentication failed",
            "connection timeout",
            "system started"
        ]
        
        embeddings = self.embedder.embed_batch(test_logs, batch_size=2)
        
        # Check shape
        self.assertEqual(embeddings.shape[0], len(test_logs),
                        "Wrong number of embeddings")
        self.assertEqual(embeddings.shape[1], 768,
                        "Wrong embedding dimension")
        
        # Check no NaN
        self.assertFalse(np.isnan(embeddings).any(),
                        "Embeddings contain NaN")
        
        print("  ✅ Batch embedding test passed")
    
    def test_batch_processor(self):
        """Test batch processor with checkpointing"""
        print("\n🧪 Testing batch processor...")
        
        # Create temporary directory for checkpoints
        temp_dir = tempfile.mkdtemp()
        
        try:
            processor = BatchProcessor(
                use_gpu=False,
                checkpoint_dir=temp_dir
            )
            
            # Small test dataset
            test_logs = [f"test log {i}" for i in range(50)]
            
            # Process
            embeddings = processor.process_large_dataset(
                test_logs,
                batch_size=10,
                save_interval=20,
                resume_from_checkpoint=False
            )
            
            # Check results
            self.assertEqual(len(embeddings), len(test_logs),
                           "Wrong number of embeddings")
            
            # Check checkpoint was created
            checkpoints = [f for f in os.listdir(temp_dir) if f.startswith('checkpoint_')]
            self.assertGreater(len(checkpoints), 0,
                             "No checkpoints created")
            
            print("  ✅ Batch processor test passed")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)


class TestVectorDatabase(unittest.TestCase):
    """Test vector database components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        print("\n🔧 Setting up vector database tests...")
        
        # Create test data
        cls.test_embeddings = np.random.random((100, 768)).astype('float32')
        cls.test_df = pd.DataFrame({
            'original': [f'original log {i}' for i in range(100)],
            'cleaned': [f'log {i}' for i in range(100)],
            'protocols': ['test'] * 100
        })
    
    def test_index_building(self):
        """Test building vector index"""
        print("\n🧪 Testing index building...")
        
        db = OptimizedVectorDB()
        db.build_index(self.test_embeddings, self.test_df)
        
        # Check index was built
        self.assertIsNotNone(db.index, "Index not created")
        self.assertEqual(db.index.ntotal, len(self.test_embeddings),
                        "Wrong number of vectors in index")
        
        print("  ✅ Index building test passed")
    
    def test_search(self):
        """Test vector search"""
        print("\n🧪 Testing vector search...")
        
        db = OptimizedVectorDB()
        db.build_index(self.test_embeddings, self.test_df)
        
        # Search
        query = self.test_embeddings[0]
        results = db.search_with_filter(query, k=5)
        
        # Check results
        self.assertEqual(len(results), 5, "Wrong number of results")
        self.assertIn('log_text', results[0], "Missing log_text in results")
        self.assertIn('similarity_score', results[0], "Missing similarity_score")
        
        # First result should have highest score
        self.assertGreater(results[0]['similarity_score'], 
                          results[-1]['similarity_score'],
                          "Results not sorted by score")
        
        print("  ✅ Vector search test passed")
    
    def test_protocol_filtering(self):
        """Test search with protocol filter"""
        print("\n🧪 Testing protocol filtering...")
        
        # Create test data with different protocols
        test_df = pd.DataFrame({
            'original': [f'log {i}' for i in range(50)],
            'cleaned': [f'log {i}' for i in range(50)],
            'protocols': ['modbus'] * 25 + ['http'] * 25
        })
        
        test_emb = np.random.random((50, 768)).astype('float32')
        
        db = OptimizedVectorDB()
        db.build_index(test_emb, test_df)
        
        # Search with filter
        results = db.search_with_filter(
            test_emb[0],
            k=10,
            protocol_filter='modbus'
        )
        
        # Check all results have modbus protocol
        for result in results:
            self.assertIn('modbus', result['protocols'],
                         "Filter not working correctly")
        
        print("  ✅ Protocol filtering test passed")


class TestRAGSystem(unittest.TestCase):
    """Test RAG system components"""
    
    def test_cost_optimizer(self):
        """Test cost tracking"""
        print("\n🧪 Testing cost optimizer...")
        
        optimizer = CostOptimizer(model_name='gpt-3.5-turbo')
        
        # Track some usage
        optimizer.track_usage(500, 200, "test query 1")
        optimizer.track_usage(600, 250, "test query 2")
        
        # Get statistics
        stats = optimizer.get_statistics()
        
        # Check statistics
        self.assertEqual(stats['total_queries'], 2)
        self.assertEqual(stats['total_input_tokens'], 1100)
        self.assertEqual(stats['total_output_tokens'], 450)
        self.assertGreater(stats['total_cost'], 0)
        
        # Test context optimization
        test_logs = [
            {'log_text': 'log 1', 'similarity_score': 0.9},
            {'log_text': 'log 2', 'similarity_score': 0.7},
            {'log_text': 'log 3', 'similarity_score': 0.5},
        ]
        
        optimized = optimizer.optimize_context(test_logs, max_logs=2)
        self.assertEqual(len(optimized), 2, "Context optimization failed")
        
        print("  ✅ Cost optimizer test passed")
    
    def test_caching(self):
        """Test response caching"""
        print("\n🧪 Testing caching system...")
        
        # Create temporary cache file
        temp_cache = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_cache.close()
        
        try:
            rag = CachingRAG(cache_file=temp_cache.name)
            
            test_logs = [
                {'log_text': 'test log', 'similarity_score': 0.9, 'protocols': 'test'}
            ]
            
            # First call should be cache miss
            # Note: This will make actual API call, so we skip if no API key
            if os.getenv('OPENAI_API_KEY'):
                result1 = rag.generate_with_cache(
                    "test question",
                    test_logs,
                    mode='analysis'
                )
                
                self.assertFalse(result1['from_cache'], "Should be cache miss")
                
                # Second call should be cache hit
                result2 = rag.generate_with_cache(
                    "test question",
                    test_logs,
                    mode='analysis'
                )
                
                self.assertTrue(result2['from_cache'], "Should be cache hit")
                
                print("  ✅ Caching test passed")
            else:
                print("  ⚠️ Skipping caching test (no API key)")
            
        finally:
            # Cleanup
            os.unlink(temp_cache.name)


class TestEvaluation(unittest.TestCase):
    """Test evaluation components"""
    
    def test_metrics_calculation(self):
        """Test evaluation metrics"""
        print("\n🧪 Testing evaluation metrics...")
        
        evaluator = RetrievalEvaluator()
        
        # Test Precision@K
        retrieved = [0, 1, 2, 3, 4]
        relevant = [1, 2, 5]
        
        precision = evaluator.calculate_precision_at_k(retrieved, relevant, k=5)
        self.assertAlmostEqual(precision, 0.4, places=2)  # 2/5
        
        # Test Recall@K
        recall = evaluator.calculate_recall_at_k(retrieved, relevant, k=5)
        self.assertAlmostEqual(recall, 0.667, places=2)  # 2/3
        
        # Test MRR
        retrieved_list = [[0, 1, 2], [5, 6, 7]]
        ground_truth_list = [[1, 2], [6, 8]]
        
        mrr = evaluator.calculate_mrr(retrieved_list, ground_truth_list)
        self.assertGreater(mrr, 0)
        self.assertLessEqual(mrr, 1)
        
        print("  ✅ Metrics calculation test passed")
    
    def test_test_set_creation(self):
        """Test test set generator"""
        print("\n🧪 Testing test set creation...")
        
        # Create sample log data
        sample_df = pd.DataFrame({
            'original': [
                'authentication failed',
                'modbus timeout',
                'network error',
                'system startup'
            ] * 10,
            'cleaned': [
                'authentication failed',
                'modbus timeout',
                'network error',
                'system startup'
            ] * 10,
            'protocols': ['ssh', 'modbus', 'http', 'unknown'] * 10
        })
        
        creator = TestSetCreator()
        
        # Create temporary output file
        temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_output.close()
        
        try:
            test_set = creator.create_full_test_set(
                sample_df,
                output_file=temp_output.name,
                min_logs_required=1
            )
            
            # Check test set
            self.assertGreater(len(test_set), 0, "No test cases created")
            
            # Validate structure
            for test_case in test_set:
                self.assertIn('query', test_case)
                self.assertIn('ground_truth_indices', test_case)
                self.assertIn('num_relevant', test_case)
            
            # Validate test set
            is_valid = creator.validate_test_set(test_set, sample_df)
            self.assertTrue(is_valid, "Test set validation failed")
            
            print("  ✅ Test set creation test passed")
            
        finally:
            # Cleanup
            os.unlink(temp_output.name)


class TestExport(unittest.TestCase):
    """Test export functionality"""
    
    def test_export_formats(self):
        """Test all export formats"""
        print("\n🧪 Testing export formats...")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            exporter = ResultsExporter(output_dir=temp_dir)
            
            # Test data
            test_results = [
                {
                    'timestamp': '2024-01-01T12:00:00',
                    'question': 'test query',
                    'answer': 'test answer',
                    'cost': 0.002,
                    'tokens_used': 100,
                    'from_cache': False,
                    'mode': 'analysis',
                    'retrieved_logs': [
                        {'log_text': 'test log', 'similarity_score': 0.9}
                    ]
                }
            ]
            
            # Test CSV export
            csv_file = exporter.export_to_csv(test_results)
            self.assertTrue(os.path.exists(csv_file), "CSV not created")
            
            # Test JSON export
            json_file = exporter.export_to_json(test_results)
            self.assertTrue(os.path.exists(json_file), "JSON not created")
            
            # Test Markdown export
            md_file = exporter.export_to_markdown(test_results)
            self.assertTrue(os.path.exists(md_file), "Markdown not created")
            
            # Test all formats at once
            all_exports = exporter.export_all_formats(test_results)
            self.assertEqual(len(all_exports), 4, "Not all formats exported")
            
            print("  ✅ Export formats test passed")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_complete_pipeline(self):
        """Test complete query pipeline"""
        print("\n🧪 Testing complete pipeline...")
        
        # This is a simplified end-to-end test
        # In production, you'd test with real system components
        
        # 1. Create embeddings
        embedder = LogEmbedder()
        test_logs = ["auth failed", "connection timeout", "system error"]
        embeddings = embedder.embed_batch(test_logs)
        
        # 2. Build vector DB
        test_df = pd.DataFrame({
            'original': test_logs,
            'cleaned': test_logs,
            'protocols': ['ssh', 'http', 'unknown']
        })
        
        db = OptimizedVectorDB()
        db.build_index(embeddings.astype('float32'), test_df)
        
        # 3. Search
        query_emb = embedder.embed_single_log("authentication failures")
        results = db.search_with_filter(query_emb, k=3)
        
        # 4. Verify results
        self.assertEqual(len(results), 3, "Pipeline failed")
        self.assertIn('log_text', results[0], "Missing log text")
        
        print("  ✅ Complete pipeline test passed")
    
    def test_error_handling(self):
        """Test system handles errors gracefully"""
        print("\n🧪 Testing error handling...")
        
        # Test empty query
        embedder = LogEmbedder()
        
        try:
            empty_emb = embedder.embed_single_log("")
            # Should not crash, should return valid embedding
            self.assertEqual(empty_emb.shape, (768,))
        except Exception as e:
            self.fail(f"Empty query caused error: {e}")
        
        # Test invalid data
        db = OptimizedVectorDB()
        
        try:
            # Should handle empty dataframe
            empty_df = pd.DataFrame()
            # This should raise an error or handle gracefully
        except Exception:
            pass  # Expected to fail
        
        print("  ✅ Error handling test passed")


def run_all_tests():
    """Run complete test suite"""
    
    print("\n" + "=" * 60)
    print("🚀 RUNNING INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddings))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestExport))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)