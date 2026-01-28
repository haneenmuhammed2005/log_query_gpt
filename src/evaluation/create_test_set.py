"""
Create evaluation test dataset with ground truth mappings
Uses actual log data from Week 2 preprocessing
"""

import pandas as pd
import json
import os
from typing import List, Dict, Set
import re


class TestSetCreator:
    """Create test dataset with ground truth for evaluation"""
    
    def __init__(self):
        self.test_cases = []
    
    def create_test_queries(self) -> List[Dict]:
        """
        Create diverse test queries covering different scenarios
        
        Returns:
            List of test query configurations
        """
        
        test_queries = [
            {
                'query': 'authentication failures',
                'expected_keywords': ['auth', 'failed', 'login', 'denied', 'unauthorized'],
                'expected_protocols': ['ssh', 'http'],
                'category': 'security',
                'min_relevance': 2  # Minimum number of expected relevant logs
            },
            {
                'query': 'modbus communication errors',
                'expected_keywords': ['modbus', 'timeout', 'connection', 'failed', 'error'],
                'expected_protocols': ['modbus'],
                'category': 'protocol',
                'min_relevance': 1
            },
            {
                'query': 'system startup events',
                'expected_keywords': ['startup', 'boot', 'initialized', 'started', 'begin'],
                'expected_protocols': ['unknown', 'http', 'ssh'],
                'category': 'system',
                'min_relevance': 1
            },
            {
                'query': 'network timeouts',
                'expected_keywords': ['timeout', 'connection', 'network', 'unreachable', 'failed'],
                'expected_protocols': ['http', 'modbus', 'snmp', 'ssh'],
                'category': 'network',
                'min_relevance': 2
            },
            {
                'query': 'sensor reading errors',
                'expected_keywords': ['sensor', 'reading', 'error', 'failed', 'invalid'],
                'expected_protocols': ['modbus', 'snmp'],
                'category': 'hardware',
                'min_relevance': 1
            },
            {
                'query': 'connection refused',
                'expected_keywords': ['refused', 'rejected', 'denied', 'connection'],
                'expected_protocols': ['http', 'ssh', 'modbus'],
                'category': 'network',
                'min_relevance': 1
            },
            {
                'query': 'configuration changes',
                'expected_keywords': ['config', 'configuration', 'changed', 'modified', 'updated'],
                'expected_protocols': ['unknown', 'http', 'ssh'],
                'category': 'system',
                'min_relevance': 1
            },
            {
                'query': 'critical errors',
                'expected_keywords': ['critical', 'fatal', 'emergency', 'severe', 'error'],
                'expected_protocols': ['unknown', 'modbus', 'http', 'ssh', 'snmp'],
                'category': 'security',
                'min_relevance': 1
            },
            {
                'query': 'snmp trap messages',
                'expected_keywords': ['snmp', 'trap', 'alert', 'notification'],
                'expected_protocols': ['snmp'],
                'category': 'protocol',
                'min_relevance': 1
            },
            {
                'query': 'database connection issues',
                'expected_keywords': ['database', 'db', 'sql', 'connection', 'query', 'failed'],
                'expected_protocols': ['http', 'unknown'],
                'category': 'system',
                'min_relevance': 1
            }
        ]
        
        return test_queries
    
    def calculate_relevance_score(self, log_text: str, 
                                  expected_keywords: List[str]) -> float:
        """
        Calculate how relevant a log is based on keyword matching
        
        Args:
            log_text: Cleaned log text
            expected_keywords: Keywords that indicate relevance
        
        Returns:
            Score from 0-1
        """
        log_lower = log_text.lower()
        matches = 0
        
        for keyword in expected_keywords:
            if keyword in log_lower:
                matches += 1
        
        # Normalize by number of keywords
        return matches / len(expected_keywords) if expected_keywords else 0
    
    def generate_ground_truth(self, logs_df: pd.DataFrame,
                            test_query: Dict,
                            top_n: int = 20) -> List[int]:
        """
        Find relevant logs for a test query
        
        Args:
            logs_df: DataFrame with processed logs
            test_query: Test query configuration
            top_n: Maximum number of relevant logs to include
        
        Returns:
            List of relevant log indices
        """
        
        relevant_indices = []
        relevance_scores = []
        
        for idx, row in logs_df.iterrows():
            # Get log text (use cleaned version)
            log_text = row.get('cleaned', row.get('original', '')).lower()
            
            # Calculate relevance score based on keywords
            keyword_score = self.calculate_relevance_score(
                log_text, 
                test_query['expected_keywords']
            )
            
            # Check protocol match if protocols column exists
            protocol_score = 0
            if 'protocols' in row:
                protocols = str(row['protocols']).lower()
                for expected_protocol in test_query['expected_protocols']:
                    if expected_protocol in protocols:
                        protocol_score = 0.3  # Bonus for protocol match
                        break
            
            # Combined score
            total_score = keyword_score + protocol_score
            
            # Consider relevant if score is above threshold
            if total_score > 0.3:  # At least 30% match
                relevant_indices.append(idx)
                relevance_scores.append(total_score)
        
        # Sort by relevance score and take top N
        if relevant_indices:
            sorted_pairs = sorted(
                zip(relevant_indices, relevance_scores),
                key=lambda x: x[1],
                reverse=True
            )
            relevant_indices = [idx for idx, score in sorted_pairs[:top_n]]
        
        return relevant_indices
    
    def create_full_test_set(self, logs_df: pd.DataFrame,
                            output_file: str = 'data/evaluation/test_set.json',
                            min_logs_required: int = 1) -> List[Dict]:
        """
        Create complete test set with ground truth
        
        Args:
            logs_df: DataFrame with processed logs
            output_file: Where to save test set
            min_logs_required: Minimum relevant logs required to include query
        
        Returns:
            List of test cases
        """
        
        print("=" * 60)
        print("📝 CREATING TEST SET")
        print("=" * 60)
        print(f"Total logs in dataset: {len(logs_df)}")
        
        test_queries = self.create_test_queries()
        test_set = []
        
        for query_info in test_queries:
            print(f"\n🔍 Processing: {query_info['query']}")
            
            ground_truth = self.generate_ground_truth(logs_df, query_info)
            
            # Only include if we found enough relevant logs
            if len(ground_truth) >= min_logs_required:
                test_case = {
                    'query': query_info['query'],
                    'category': query_info['category'],
                    'expected_keywords': query_info['expected_keywords'],
                    'expected_protocols': query_info['expected_protocols'],
                    'ground_truth_indices': ground_truth,
                    'num_relevant': len(ground_truth)
                }
                
                test_set.append(test_case)
                
                print(f"   ✅ Found {len(ground_truth)} relevant logs")
                
                # Show sample logs
                if len(ground_truth) > 0:
                    sample_idx = ground_truth[0]
                    sample_log = logs_df.iloc[sample_idx]['cleaned']
                    print(f"   📋 Sample: {sample_log[:60]}...")
            else:
                print(f"   ⚠️ Skipped: Only {len(ground_truth)} relevant logs found (min: {min_logs_required})")
        
        # Save to JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(test_set, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 TEST SET SUMMARY")
        print("=" * 60)
        print(f"Total queries: {len(test_set)}")
        print(f"Output file: {output_file}")
        
        # Category breakdown
        categories = {}
        total_relevant = 0
        for test_case in test_set:
            cat = test_case['category']
            categories[cat] = categories.get(cat, 0) + 1
            total_relevant += test_case['num_relevant']
        
        print(f"\nQueries by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
        
        print(f"\nTotal relevant logs: {total_relevant}")
        print(f"Average relevant per query: {total_relevant / len(test_set):.1f}")
        
        print("=" * 60)
        
        return test_set
    
    def validate_test_set(self, test_set: List[Dict], logs_df: pd.DataFrame):
        """
        Validate that test set is well-formed
        
        Args:
            test_set: Test set to validate
            logs_df: DataFrame with logs
        """
        print("\n🔍 VALIDATING TEST SET")
        print("-" * 60)
        
        issues = []
        
        for i, test_case in enumerate(test_set):
            # Check required fields
            required_fields = ['query', 'category', 'ground_truth_indices', 'num_relevant']
            for field in required_fields:
                if field not in test_case:
                    issues.append(f"Query {i}: Missing field '{field}'")
            
            # Check indices are valid
            for idx in test_case['ground_truth_indices']:
                if idx < 0 or idx >= len(logs_df):
                    issues.append(f"Query {i}: Invalid index {idx}")
            
            # Check count matches
            if len(test_case['ground_truth_indices']) != test_case['num_relevant']:
                issues.append(f"Query {i}: Count mismatch")
        
        if issues:
            print("❌ Validation failed:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Test set is valid!")
        
        return len(issues) == 0


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("TEST SET CREATOR")
    print("=" * 60)
    
    # Try to load enhanced logs (from Week 3)
    log_files = [
        'data/processed_logs/HDFS_enhanced.csv',
        'data/processed_logs/HDFS_cleaned.csv',
        'data/processed_logs/BGL_enhanced.csv',
        'data/processed_logs/BGL_cleaned.csv'
    ]
    
    logs_df = None
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📖 Loading {log_file}...")
            logs_df = pd.read_csv(log_file)
            print(f"   Loaded {len(logs_df)} logs")
            break
    
    if logs_df is None:
        print("\n⚠️ No log files found! Creating sample data for testing...")
        # Create sample data for testing
        logs_df = pd.DataFrame({
            'original': [
                'authentication failed for user admin',
                'modbus timeout on device 5',
                'system startup completed',
                'network connection timeout',
                'sensor reading error on channel 3',
                'http connection refused',
                'configuration file updated',
                'critical error in module X',
                'snmp trap received',
                'database connection failed'
            ] * 10,  # Repeat to have 100 logs
            'cleaned': [
                'authentication failed for user admin',
                'modbus timeout on device num',
                'system startup completed',
                'network connection timeout',
                'sensor reading error on channel num',
                'http connection refused',
                'configuration file updated',
                'critical error in module x',
                'snmp trap received',
                'database connection failed'
            ] * 10,
            'protocols': [
                'ssh',
                'modbus',
                'unknown',
                'http',
                'modbus',
                'http',
                'unknown',
                'unknown',
                'snmp',
                'unknown'
            ] * 10
        })
        print(f"   Created {len(logs_df)} sample logs")
    
    # Create test set
    print("\n")
    creator = TestSetCreator()
    test_set = creator.create_full_test_set(
        logs_df,
        output_file='data/evaluation/test_set.json',
        min_logs_required=1
    )
    
    # Validate
    creator.validate_test_set(test_set, logs_df)
    
    # Show sample test case
    if test_set:
        print("\n" + "=" * 60)
        print("SAMPLE TEST CASE")
        print("=" * 60)
        sample = test_set[0]
        print(f"Query: {sample['query']}")
        print(f"Category: {sample['category']}")
        print(f"Keywords: {', '.join(sample['expected_keywords'])}")
        print(f"Protocols: {', '.join(sample['expected_protocols'])}")
        print(f"Relevant logs: {sample['num_relevant']}")
        
        # Show first few ground truth logs
        print(f"\nFirst 3 relevant logs:")
        for i, idx in enumerate(sample['ground_truth_indices'][:3], 1):
            log = logs_df.iloc[idx]['cleaned']
            print(f"  {i}. {log[:70]}...")
    
    print("\n✅ Test set creation complete!")
