"""
Cost optimization and tracking for RAG system
Tracks API usage, costs, and provides optimization recommendations
"""

from typing import List, Dict, Optional
import time
import json
import os
from datetime import datetime


class CostOptimizer:
    """Optimize and track API costs and response times"""
    
    # Update these based on your actual API provider
    # Examples: GPT-3.5-turbo, GPT-4, Claude, etc.
    PRICING_MODELS = {
        'gpt-3.5-turbo': {
            'input': 0.0015,  # per 1K tokens
            'output': 0.002
        },
        'gpt-4': {
            'input': 0.03,
            'output': 0.06
        },
        'gpt-4-turbo': {
            'input': 0.01,
            'output': 0.03
        },
        'claude-3-sonnet': {
            'input': 0.003,
            'output': 0.015
        }
    }
    
    def __init__(self, model_name: str = 'gpt-3.5-turbo', log_file: str = 'data/logs/cost_tracking.json'):
        """
        Initialize cost optimizer
        
        Args:
            model_name: Name of the LLM model being used
            log_file: File to store cost tracking logs
        """
        self.model_name = model_name
        self.log_file = log_file
        
        # Get pricing for model
        if model_name in self.PRICING_MODELS:
            self.price_per_1k_input = self.PRICING_MODELS[model_name]['input']
            self.price_per_1k_output = self.PRICING_MODELS[model_name]['output']
        else:
            print(f"⚠️ Unknown model: {model_name}. Using GPT-3.5-turbo pricing.")
            self.price_per_1k_input = 0.0015
            self.price_per_1k_output = 0.002
        
        # Tracking variables
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.query_count = 0
        self.query_history = []
        
        # Create log directory
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Load existing logs if available
        self._load_history()
        
        print(f"💰 Cost Optimizer initialized")
        print(f"   Model: {model_name}")
        print(f"   Input: ${self.price_per_1k_input}/1K tokens")
        print(f"   Output: ${self.price_per_1k_output}/1K tokens")
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for single query
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Total cost in dollars
        """
        input_cost = (input_tokens / 1000) * self.price_per_1k_input
        output_cost = (output_tokens / 1000) * self.price_per_1k_output
        
        return input_cost + output_cost
    
    def track_usage(self, input_tokens: int, output_tokens: int, query: str = "", metadata: Optional[Dict] = None):
        """
        Track cumulative usage for a query
        
        Args:
            input_tokens: Tokens in the prompt
            output_tokens: Tokens in the response
            query: The query string (for logging)
            metadata: Additional metadata to store
        """
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.query_count += 1
        
        query_cost = self.calculate_cost(input_tokens, output_tokens)
        self.total_cost += query_cost
        
        # Record this query
        query_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query[:100],  # Truncate long queries
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': query_cost,
            'model': self.model_name
        }
        
        if metadata:
            query_record['metadata'] = metadata
        
        self.query_history.append(query_record)
        
        # Save to log file periodically (every 10 queries)
        if self.query_count % 10 == 0:
            self._save_history()
    
    def get_statistics(self) -> Dict:
        """Get comprehensive usage statistics"""
        
        avg_cost = self.total_cost / self.query_count if self.query_count > 0 else 0
        avg_input = self.total_input_tokens / self.query_count if self.query_count > 0 else 0
        avg_output = self.total_output_tokens / self.query_count if self.query_count > 0 else 0
        
        return {
            'total_queries': self.query_count,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'total_cost': self.total_cost,
            'avg_cost_per_query': avg_cost,
            'avg_input_tokens': avg_input,
            'avg_output_tokens': avg_output,
            'model': self.model_name,
            'cost_breakdown': {
                'input_cost': (self.total_input_tokens / 1000) * self.price_per_1k_input,
                'output_cost': (self.total_output_tokens / 1000) * self.price_per_1k_output
            }
        }
    
    def optimize_context(self, logs: List[Dict], max_logs: int = 5, min_score: float = 0.7) -> List[Dict]:
        """
        Optimize number of logs to reduce tokens while maintaining quality
        
        Args:
            logs: List of log dictionaries with 'similarity_score'
            max_logs: Maximum number of logs to keep
            min_score: Minimum similarity score to include
        
        Returns:
            Optimized list of logs
        """
        # Filter by minimum score
        filtered_logs = [log for log in logs if log.get('similarity_score', 0) >= min_score]
        
        # Sort by similarity score (descending)
        sorted_logs = sorted(
            filtered_logs, 
            key=lambda x: x.get('similarity_score', 0), 
            reverse=True
        )
        
        # Take top N
        optimized = sorted_logs[:max_logs]
        
        original_count = len(logs)
        optimized_count = len(optimized)
        
        if optimized_count < original_count:
            print(f"✂️ Optimized context: {original_count} → {optimized_count} logs")
        
        return optimized
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (GPT uses ~4 chars per token)
        This is approximate - actual tokenization may differ
        
        Args:
            text: Text to estimate
        
        Returns:
            Estimated token count
        """
        # Simple heuristic: 1 token ≈ 4 characters
        return len(text) // 4
    
    def estimate_query_cost(self, prompt: str, expected_response_length: int = 200) -> float:
        """
        Estimate cost before making API call
        
        Args:
            prompt: The prompt text
            expected_response_length: Expected tokens in response
        
        Returns:
            Estimated cost
        """
        estimated_input = self.estimate_tokens(prompt)
        estimated_cost = self.calculate_cost(estimated_input, expected_response_length)
        
        return estimated_cost
    
    def get_cost_recommendations(self) -> List[str]:
        """
        Provide cost optimization recommendations based on usage patterns
        
        Returns:
            List of recommendation strings
        """
        stats = self.get_statistics()
        recommendations = []
        
        # High average input tokens
        if stats['avg_input_tokens'] > 2000:
            recommendations.append(
                "⚠️ Average input is large (>2000 tokens). Consider reducing context logs."
            )
        
        # Check if we're using an expensive model unnecessarily
        if self.model_name in ['gpt-4', 'gpt-4-turbo']:
            if stats['avg_cost_per_query'] > 0.05:
                recommendations.append(
                    "💡 Consider using GPT-3.5-turbo for simpler queries to reduce costs."
                )
        
        # Many queries suggest caching could help
        if stats['total_queries'] > 50:
            recommendations.append(
                "💡 With many queries, consider implementing response caching."
            )
        
        # High token usage
        if stats['total_tokens'] > 100000:
            recommendations.append(
                "💡 High token usage detected. Review prompt engineering to reduce verbosity."
            )
        
        if not recommendations:
            recommendations.append("✅ Usage patterns look efficient!")
        
        return recommendations
    
    def print_report(self):
        """Print detailed cost report"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("💰 COST REPORT")
        print("=" * 60)
        print(f"Model: {stats['model']}")
        print(f"Total Queries: {stats['total_queries']}")
        print(f"\nToken Usage:")
        print(f"  Total: {stats['total_tokens']:,}")
        print(f"  Input: {stats['total_input_tokens']:,}")
        print(f"  Output: {stats['total_output_tokens']:,}")
        print(f"\nCosts:")
        print(f"  Total Cost: ${stats['total_cost']:.4f}")
        print(f"  Input Cost: ${stats['cost_breakdown']['input_cost']:.4f}")
        print(f"  Output Cost: ${stats['cost_breakdown']['output_cost']:.4f}")
        print(f"\nAverages (per query):")
        print(f"  Cost: ${stats['avg_cost_per_query']:.4f}")
        print(f"  Input Tokens: {stats['avg_input_tokens']:.0f}")
        print(f"  Output Tokens: {stats['avg_output_tokens']:.0f}")
        
        # Recommendations
        print("\n" + "=" * 60)
        print("💡 RECOMMENDATIONS")
        print("=" * 60)
        for rec in self.get_cost_recommendations():
            print(rec)
        
        print("=" * 60)
    
    def _save_history(self):
        """Save query history to file"""
        try:
            data = {
                'model': self.model_name,
                'total_cost': self.total_cost,
                'total_queries': self.query_count,
                'history': self.query_history
            }
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")
    
    def _load_history(self):
        """Load query history from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.query_history = data.get('history', [])
                    # Don't reload totals - start fresh each session
                    print(f"📂 Loaded {len(self.query_history)} historical queries")
            except Exception as e:
                print(f"⚠️ Could not load history: {e}")
    
    def export_report(self, filepath: str):
        """
        Export detailed cost report to JSON
        
        Args:
            filepath: Path to save report
        """
        stats = self.get_statistics()
        stats['recommendations'] = self.get_cost_recommendations()
        stats['generated_at'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Cost report exported to {filepath}")


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("COST OPTIMIZER TEST")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = CostOptimizer(model_name='gpt-3.5-turbo')
    
    # Simulate some queries
    print("\n📝 Simulating API calls...")
    
    queries = [
        ("Show me authentication failures", 500, 150),
        ("What errors occurred yesterday?", 600, 200),
        ("Find network timeouts", 450, 180),
        ("Analyze modbus communication issues", 700, 250),
        ("Show me all critical errors", 550, 175)
    ]
    
    for query, input_tokens, output_tokens in queries:
        optimizer.track_usage(input_tokens, output_tokens, query)
        print(f"  ✓ Tracked: {query[:40]}...")
    
    # Print report
    print("\n")
    optimizer.print_report()
    
    # Test context optimization
    print("\n" + "=" * 60)
    print("CONTEXT OPTIMIZATION TEST")
    print("=" * 60)
    
    test_logs = [
        {'log_text': 'auth failed for user admin', 'similarity_score': 0.95},
        {'log_text': 'connection timeout on port 502', 'similarity_score': 0.88},
        {'log_text': 'system started successfully', 'similarity_score': 0.75},
        {'log_text': 'warning: disk space low', 'similarity_score': 0.60},
        {'log_text': 'normal operation resumed', 'similarity_score': 0.45},
    ]
    
    print(f"\nOriginal: {len(test_logs)} logs")
    optimized = optimizer.optimize_context(test_logs, max_logs=3, min_score=0.7)
    print(f"Optimized: {len(optimized)} logs")
    print(f"Kept logs with scores: {[f'{log['similarity_score']:.2f}' for log in optimized]}")
    
    # Export report
    print("\n" + "=" * 60)
    export_path = 'data/exports/cost_report_test.json'
    os.makedirs('data/exports', exist_ok=True)
    optimizer.export_report(export_path)
    
    print("\n✅ Cost optimizer test complete!")
