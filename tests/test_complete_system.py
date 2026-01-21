import sys
sys.path.append('src')

import numpy as np
import pandas as pd
import requests
import time
from typing import Dict, List

from embeddings.log_embedder import LogEmbedder
from preprocessing.protocol_detector import ProtocolDetector
from vector_db.optimized_search import OptimizedVectorDB
from rag_system.conversational_rag_ollama import ConversationalRAGOllama

class SystemTester:
    """Comprehensive testing suite for ICS-LogQueryGPT"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_results = []
    
    def log_result(self, test_name: str, passed: bool, message: str = "", warning: bool = False):
        """Log test result"""
        status = "PASS" if passed else ("WARN" if warning else "FAIL")
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        
        if passed and not warning:
            self.passed += 1
        elif warning:
            self.warnings += 1
        else:
            self.failed += 1
    
    def test_ollama_connection(self):
        """Test 1: Ollama is running and accessible"""
        print("\n🧪 TEST 1: Ollama Connection")
        print("-" * 70)
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                # Check for Llama 3.1
                llama_models = [m for m in model_names if 'llama3.1' in m]
                
                if llama_models:
                    print(f"✅ Ollama is running")
                    print(f"✅ Found Llama models: {', '.join(llama_models)}")
                    self.log_result("Ollama Connection", True)
                else:
                    print(f"⚠️ Ollama running but no Llama 3.1 models found")
                    print(f"   Available models: {', '.join(model_names)}")
                    self.log_result("Ollama Connection", True, 
                                   "No Llama 3.1 models", warning=True)
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("   Solution: Run 'ollama serve' in terminal")
            self.log_result("Ollama Connection", False, str(e))
    
    def test_protocol_detection(self):
        """Test 2: Protocol detector works correctly"""
        print("\n🧪 TEST 2: Protocol Detection")
        print("-" * 70)
        
        try:
            detector = ProtocolDetector()
            
            # Test cases with expected results
            test_cases = [
                ("modbus read coil failed", ['modbus']),
                ("snmp trap received OID 1.3.6.1", ['snmp']),
                ("ssh authentication failed", ['ssh']),
                ("http get request timeout", ['http']),
                ("unknown error occurred", ['unknown'])
            ]
            
            all_passed = True
            for log_text, expected in test_cases:
                detected = detector.detect_protocol(log_text)
                if set(detected) == set(expected):
                    print(f"✅ '{log_text[:40]}...' → {detected}")
                else:
                    print(f"❌ '{log_text[:40]}...' → Expected {expected}, got {detected}")
                    all_passed = False
            
            if all_passed:
                print("✅ All protocol detection tests passed")
                self.log_result("Protocol Detection", True)
            else:
                self.log_result("Protocol Detection", False, "Some tests failed")
                
        except Exception as e:
            print(f"❌ Protocol detection test failed: {e}")
            self.log_result("Protocol Detection", False, str(e))
    
    def test_embeddings(self):
        """Test 3: BERT embeddings generation"""
        print("\n🧪 TEST 3: Embeddings Generation")
        print("-" * 70)
        
        try:
            embedder = LogEmbedder()
            
            # Test single embedding
            test_log = "authentication failed for user admin"
            start_time = time.time()
            emb = embedder.embed_single_log(test_log)
            embed_time = time.time() - start_time
            
            # Validations
            assert emb.shape == (768,), f"Wrong shape: {emb.shape}"
            assert not np.isnan(emb).any(), "Contains NaN values"
            assert not np.isinf(emb).any(), "Contains Inf values"
            assert np.abs(emb).sum() > 0, "Embedding is all zeros"
            
            print(f"✅ Single embedding: shape {emb.shape}")
            print(f"✅ Time: {embed_time:.3f}s")
            
            # Test batch embedding
            test_logs = [f"test log {i}" for i in range(10)]
            start_time = time.time()
            batch_embs = embedder.embed_batch(test_logs, batch_size=5)
            batch_time = time.time() - start_time
            
            assert len(batch_embs) == 10, f"Wrong batch size: {len(batch_embs)}"
            assert batch_embs.shape[1] == 768, f"Wrong dimension: {batch_embs.shape[1]}"
            
            print(f"✅ Batch embedding: {len(batch_embs)} logs in {batch_time:.3f}s")
            print(f"✅ Speed: {len(batch_embs)/batch_time:.1f} logs/sec")
            
            self.log_result("Embeddings", True)
            
        except Exception as e:
            print(f"❌ Embeddings test failed: {e}")
            self.log_result("Embeddings", False, str(e))
    
    def test_vector_search(self):
        """Test 4: Vector database and search"""
        print("\n🧪 TEST 4: Vector Search")
        print("-" * 70)
        
        try:
            # Create test data
            n_vectors = 100
            test_embeddings = np.random.random((n_vectors, 768)).astype('float32')
            test_df = pd.DataFrame({
                'cleaned': [f'test log {i}' for i in range(n_vectors)],
                'original': [f'original log {i}' for i in range(n_vectors)],
                'protocols': ['modbus' if i % 2 == 0 else 'ssh' for i in range(n_vectors)],
                'severity': ['critical' if i % 3 == 0 else 'low' for i in range(n_vectors)]
            })
            
            # Build index
            db = OptimizedVectorDB()
            start_time = time.time()
            db.build_index(test_embeddings, test_df)
            build_time = time.time() - start_time
            
            print(f"✅ Index built in {build_time:.3f}s")
            print(f"✅ Index type: {db.index_type}")
            
            # Test basic search
            query = test_embeddings[0]
            start_time = time.time()
            results = db.search_with_filter(query, k=5)
            search_time = time.time() - start_time
            
            assert len(results) == 5, f"Expected 5 results, got {len(results)}"
            assert all('log_text' in r for r in results), "Missing log_text in results"
            assert all('similarity_score' in r for r in results), "Missing scores"
            
            print(f"✅ Basic search: {len(results)} results in {search_time*1000:.2f}ms")
            
            # Test filtered search
            modbus_results = db.search_with_filter(query, k=5, protocol_filter='modbus')
            assert all('modbus' in r['protocols'] for r in modbus_results), "Filter failed"
            
            print(f"✅ Filtered search: {len(modbus_results)} Modbus results")
            
            self.log_result("Vector Search", True)
            
        except Exception as e:
            print(f"❌ Vector search test failed: {e}")
            self.log_result("Vector Search", False, str(e))
    
    def test_rag_system(self):
        """Test 5: RAG system with Ollama"""
        print("\n🧪 TEST 5: RAG System")
        print("-" * 70)
        
        try:
            rag = ConversationalRAGOllama(model_name='llama3.1:8b')
            
            test_logs = [{
                'log_text': 'authentication failed for user admin',
                'protocols': 'ssh',
                'severity': 'high',
                'similarity_score': 0.95
            }]
            
            # Test generation
            start_time = time.time()
            result = rag.generate_with_context(
                "What security issue do you see?",
                test_logs,
                mode='analysis'
            )
            gen_time = time.time() - start_time
            
            if result.get('error'):
                print(f"❌ Generation failed: {result['error']}")
                self.log_result("RAG System", False, result['error'])
                return
            
            # Validations
            assert 'answer' in result, "No answer generated"
            assert len(result['answer']) > 0, "Empty answer"
            assert 'generation_time' in result, "No timing info"
            
            print(f"✅ Answer generated ({len(result['answer'])} chars)")
            print(f"✅ Time: {result['generation_time']:.2f}s")
            print(f"✅ Answer preview: {result['answer'][:100]}...")
            
            self.log_result("RAG System", True)
            
        except Exception as e:
            print(f"❌ RAG system test failed: {e}")
            self.log_result("RAG System", False, str(e))
    
    def test_conversation_memory(self):
        """Test 6: Conversation history"""
        print("\n🧪 TEST 6: Conversation Memory")
        print("-" * 70)
        
        try:
            rag = ConversationalRAGOllama(model_name='llama3.1:8b')
            rag.start_conversation()
            
            test_logs = [{
                'log_text': 'test log entry',
                'protocols': 'test',
                'severity': 'info',
                'similarity_score': 0.9
            }]
            
            # First exchange
            result1 = rag.generate_with_context("First question", test_logs)
            
            if result1.get('error'):
                print(f"⚠️ Skipping conversation test (Ollama error)")
                self.log_result("Conversation Memory", True, "Skipped", warning=True)
                return
            
            # Check history
            assert len(rag.conversation_history) == 1, "History not updated"
            assert result1['conversation_length'] == 1, "Wrong conversation length"
            
            # Second exchange
            result2 = rag.generate_with_context("Second question", test_logs)
            assert len(rag.conversation_history) == 2, "History not growing"
            
            print(f"✅ Conversation history working")
            print(f"✅ {len(rag.conversation_history)} exchanges tracked")
            
            # Test export
            rag.export_conversation('test_conversation.json')
            print(f"✅ Conversation export working")
            
            self.log_result("Conversation Memory", True)
            
        except Exception as e:
            print(f"❌ Conversation memory test failed: {e}")
            self.log_result("Conversation Memory", False, str(e))
    
    def test_data_files(self):
        """Test 7: Required data files exist"""
        print("\n🧪 TEST 7: Data Files")
        print("-" * 70)
        
        required_files = [
            'data/embeddings/HDFS_enhanced.npy',
            'data/processed_logs/HDFS_enhanced.csv'
        ]
        
        all_exist = True
        for filepath in required_files:
            try:
                if filepath.endswith('.npy'):
                    data = np.load(filepath)
                    print(f"✅ {filepath} ({data.shape})")
                elif filepath.endswith('.csv'):
                    data = pd.read_csv(filepath)
                    print(f"✅ {filepath} ({len(data)} rows)")
            except FileNotFoundError:
                print(f"❌ {filepath} not found")
                all_exist = False
        
        if all_exist:
            self.log_result("Data Files", True)
        else:
            self.log_result("Data Files", False, "Missing files")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 70)
        print("🚀 ICS-LogQueryGPT COMPLETE SYSTEM TEST")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all tests
        self.test_ollama_connection()
        self.test_protocol_detection()
        self.test_embeddings()
        self.test_vector_search()
        self.test_rag_system()
        self.test_conversation_memory()
        self.test_data_files()
        
        total_time = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed:   {self.passed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"❌ Failed:   {self.failed}")
        print(f"⏱️  Total time: {total_time:.2f}s")
        print("=" * 70)
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            symbol = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[result['status']]
            print(f"{symbol} {result['test']}: {result['status']}")
            if result['message']:
                print(f"   {result['message']}")
        
        print("\n" + "=" * 70)
        
        return self.failed == 0

if __name__ == "__main__":
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("System is ready for deployment!")
    else:
        print("\n⚠️ SOME TESTS FAILED.")
        print("Please review the errors above and fix them before deployment.")
        exit(0 if success else 1)