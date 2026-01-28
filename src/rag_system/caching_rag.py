"""
Response caching system for RAG to reduce API costs
Integrates with EnhancedRAG from Week 3
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_system.enhanced_rag_ollama import EnhancedRAGOllama as EnhancedRAG
# Line 11 - Make it optional:
try:
    from rag_system.cost_optimizer import CostOptimizer
except ImportError:
    CostOptimizer = None  # Ollama doesn't need cost tracking
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime


class CachingRAG(EnhancedRAG):
    """RAG with response caching to reduce costs"""
    
    def __init__(self, cache_file: str = 'data/cache/response_cache.json'):
        """
        Initialize caching RAG
        
        Args:
            cache_file: Path to cache file
        """
        super().__init__()
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.optimizer = CostOptimizer()  if CostOptimizer else None
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        
        print(f"💾 Caching RAG initialized")
        print(f"   Cache file: {cache_file}")
        print(f"   Cached responses: {len(self.cache)}")
    
    def load_cache(self) -> Dict:
        """Load cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    print(f"📂 Loaded {len(cache_data)} cached responses")
                    return cache_data
            except Exception as e:
                print(f"⚠️ Could not load cache: {e}")
                return {}
        return {}
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    def create_cache_key(self, question: str, 
                        log_texts: List[str],
                        mode: str,
                        max_logs_for_key: int = 3) -> str:
        """
        Create unique cache key based on query and context
        
        Args:
            question: The user's question
            log_texts: List of log text strings
            mode: Analysis mode
            max_logs_for_key: Max logs to include in key (to prevent huge keys)
        
        Returns:
            MD5 hash string
        """
        # Combine question, mode, and top N logs
        logs_sample = log_texts[:max_logs_for_key] if log_texts else []
        content = f"{question.lower().strip()}|{mode}|{'|'.join(logs_sample)}"
        
        # Hash to create key
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate_with_cache(self, question: str,
                           retrieved_logs: List[Dict],
                           mode: str = 'analysis',
                           use_cache: bool = True) -> Dict:
        """
        Generate answer with caching
        
        Args:
            question: User's question
            retrieved_logs: Retrieved log entries
            mode: Analysis mode
            use_cache: Whether to use cache (can disable for testing)
        
        Returns:
            Result dictionary with answer and metadata
        """
        # Create cache key
        log_texts = [log['log_text'] for log in retrieved_logs]
        cache_key = self.create_cache_key(question, log_texts, mode)
        
        # Check cache if enabled
        if use_cache and cache_key in self.cache:
            print("✅ Cache hit! Using cached response")
            self.cache_hits += 1
            
            cached_result = self.cache[cache_key].copy()
            cached_result['from_cache'] = True
            cached_result['cache_key'] = cache_key
            cached_result['timestamp'] = datetime.now().isoformat()
            
            return cached_result
        
        # Cache miss - generate new response
        print(f"🤖 Cache miss. Generating new response... (mode: {mode})")
        self.cache_misses += 1
        
        try:
            # Use parent class method to generate answer
            result = self.generate_answer(question, retrieved_logs, mode)
            
            # Track cost if tokens were used
            if 'tokens_used' in result and not result.get('error'):
                # Estimate input/output split (approximation)
                # Typically input is ~60% of total tokens
                total_tokens = result['tokens_used']
                input_tokens = int(total_tokens * 0.6)
                output_tokens = int(total_tokens * 0.4)
                
                self.optimizer.track_usage(
                    input_tokens, 
                    output_tokens, 
                    question,
                    metadata={'mode': mode, 'cached': False}
                )
            
            # Add cache metadata
            result['from_cache'] = False
            result['cache_key'] = cache_key
            result['timestamp'] = datetime.now().isoformat()
            
            # Cache the result (only if no error)
            if not result.get('error'):
                self.cache[cache_key] = result
                self.save_cache()
                print(f"💾 Response cached (key: {cache_key[:8]}...)")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return {
                'question': question,
                'answer': f"Error generating response: {str(e)}",
                'error': True,
                'from_cache': False
            }
    
    def clear_cache(self, confirm: bool = False):
        """
        Clear all cached responses
        
        Args:
            confirm: Safety flag to prevent accidental clearing
        """
        if not confirm:
            print("⚠️ Use clear_cache(confirm=True) to actually clear the cache")
            return
        
        self.cache = {}
        self.save_cache()
        self.cache_hits = 0
        self.cache_misses = 0
        print("🗑️ Cache cleared")
    
    def remove_old_entries(self, days_old: int = 7):
        """
        Remove cache entries older than specified days
        
        Args:
            days_old: Remove entries older than this many days
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        original_size = len(self.cache)
        
        # Filter out old entries
        new_cache = {}
        for key, value in self.cache.items():
            try:
                entry_date = datetime.fromisoformat(value.get('timestamp', ''))
                if entry_date > cutoff_date:
                    new_cache[key] = value
            except:
                # Keep entries without valid timestamps
                new_cache[key] = value
        
        removed = original_size - len(new_cache)
        self.cache = new_cache
        self.save_cache()
        
        print(f"🗑️ Removed {removed} old cache entries")
        print(f"   Remaining: {len(self.cache)}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_queries = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_queries * 100) if total_queries > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'cache_file': self.cache_file,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_queries': total_queries,
            'hit_rate_percent': hit_rate,
            'cost_stats': self.optimizer.get_statistics()
        }
    
    def print_cache_report(self):
        """Print detailed cache report"""
        stats = self.get_cache_stats()
        
        print("\n" + "=" * 60)
        print("💾 CACHE REPORT")
        print("=" * 60)
        print(f"Cache Size: {stats['cache_size']} entries")
        print(f"Cache File: {stats['cache_file']}")
        print(f"\nSession Statistics:")
        print(f"  Cache Hits: {stats['cache_hits']}")
        print(f"  Cache Misses: {stats['cache_misses']}")
        print(f"  Total Queries: {stats['total_queries']}")
        print(f"  Hit Rate: {stats['hit_rate_percent']:.1f}%")
        
        if stats['cache_hits'] > 0:
            cost_stats = stats['cost_stats']
            # Estimate savings (cache hits save ~average cost per query)
            if cost_stats['total_queries'] > 0:
                avg_cost = cost_stats['avg_cost_per_query']
                estimated_savings = stats['cache_hits'] * avg_cost
                print(f"\nEstimated Savings: ${estimated_savings:.4f}")
        
        print("=" * 60)
    
    def export_cache_report(self, filepath: str):
        """
        Export cache statistics to JSON
        
        Args:
            filepath: Path to save report
        """
        stats = self.get_cache_stats()
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Cache report exported to {filepath}")


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("CACHING RAG TEST")
    print("=" * 60)
    
    # Initialize caching RAG
    rag = CachingRAG(cache_file='data/cache/test_cache.json')
    
    # Test logs
    test_logs = [
        {
            'log_text': 'authentication failed for user admin',
            'protocols': 'ssh',
            'similarity_score': 0.95
        },
        {
            'log_text': 'connection timeout on port 502',
            'protocols': 'modbus',
            'similarity_score': 0.82
        }
    ]
    
    print("\n" + "=" * 60)
    print("TEST 1: First Query (Cache Miss Expected)")
    print("=" * 60)
    
    result1 = rag.generate_with_cache(
        "What security issues do you see?",
        test_logs,
        mode='security'
    )
    
    print(f"From cache: {result1['from_cache']}")
    print(f"Answer length: {len(result1.get('answer', ''))}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Same Query (Cache Hit Expected)")
    print("=" * 60)
    
    result2 = rag.generate_with_cache(
        "What security issues do you see?",
        test_logs,
        mode='security'
    )
    
    print(f"From cache: {result2['from_cache']}")
    print(f"Same answer: {result1.get('answer') == result2.get('answer')}")
    
    print("\n" + "=" * 60)
    print("TEST 3: Different Query (Cache Miss Expected)")
    print("=" * 60)
    
    result3 = rag.generate_with_cache(
        "Summarize these events",
        test_logs,
        mode='summary'
    )
    
    print(f"From cache: {result3['from_cache']}")
    
    # Print reports
    print("\n")
    rag.print_cache_report()
    
    print("\n")
    rag.optimizer.print_report()
    
    # Export report
    print("\n" + "=" * 60)
    os.makedirs('data/exports', exist_ok=True)
    rag.export_cache_report('data/exports/cache_report_test.json')
    
    # Print cache stats
    stats = rag.get_cache_stats()
    print(f"\n📊 Final Cache Stats:")
    print(f"   Size: {stats['cache_size']}")
    print(f"   Hit Rate: {stats['hit_rate_percent']:.1f}%")
    
    print("\n✅ Caching RAG test complete!")
