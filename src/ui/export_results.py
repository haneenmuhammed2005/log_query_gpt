"""
Export query results in multiple formats (CSV, JSON, Markdown)
Supports detailed reports with retrieved logs and metadata
"""

import pandas as pd
from datetime import datetime
import json
import os
from typing import Dict, List, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ResultsExporter:
    """Export query results in various formats"""
    
    def __init__(self, output_dir: str = 'data/exports'):
        """
        Initialize exporter
        
        Args:
            output_dir: Directory to save exports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Exports will be saved to: {output_dir}")
    
    def export_to_csv(self, results: List[Dict], 
                     filepath: Optional[str] = None,
                     include_logs: bool = True) -> str:
        """
        Export results to CSV
        
        Args:
            results: List of query result dictionaries
            filepath: Custom filepath (auto-generated if None)
            include_logs: Whether to include retrieved logs
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'results_{timestamp}.csv')
        
        print(f"📊 Exporting to CSV: {filepath}")
        
        # Flatten results for CSV
        export_data = []
        
        for i, result in enumerate(results, 1):
            base_row = {
                'result_id': i,
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'query': result.get('question', ''),
                'answer': result.get('answer', ''),
                'mode': result.get('mode', 'analysis'),
                'tokens_used': result.get('tokens_used', 0),
                'cost': result.get('cost', 0),
                'from_cache': result.get('from_cache', False),
                'num_retrieved_logs': len(result.get('retrieved_logs', []))
            }
            
            if include_logs and 'retrieved_logs' in result:
                # Create one row per retrieved log
                for j, log in enumerate(result['retrieved_logs'], 1):
                    row = base_row.copy()
                    row.update({
                        'log_rank': j,
                        'log_text': log.get('log_text', ''),
                        'log_protocols': log.get('protocols', 'unknown'),
                        'log_similarity_score': log.get('similarity_score', 0)
                    })
                    export_data.append(row)
            else:
                # Single row without log details
                export_data.append(base_row)
        
        # Create DataFrame and save
        df = pd.DataFrame(export_data)
        df.to_csv(filepath, index=False)
        
        print(f"✅ Exported {len(export_data)} rows to CSV")
        return filepath
    
    def export_to_json(self, results: List[Dict], 
                      filepath: Optional[str] = None,
                      pretty: bool = True) -> str:
        """
        Export results to JSON
        
        Args:
            results: List of query results
            filepath: Custom filepath
            pretty: Whether to pretty-print JSON
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'results_{timestamp}.json')
        
        print(f"📄 Exporting to JSON: {filepath}")
        
        # Create export structure
        export_data = {
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_results': len(results),
                'exporter_version': '1.0'
            },
            'results': results
        }
        
        # Save
        with open(filepath, 'w') as f:
            if pretty:
                json.dump(export_data, f, indent=2)
            else:
                json.dump(export_data, f)
        
        print(f"✅ Exported {len(results)} results to JSON")
        return filepath
    
    def export_to_markdown(self, results: List[Dict], 
                          filepath: Optional[str] = None,
                          include_metadata: bool = True) -> str:
        """
        Export results as formatted Markdown report
        
        Args:
            results: List of query results
            filepath: Custom filepath
            include_metadata: Whether to include metadata section
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'results_{timestamp}.md')
        
        print(f"📝 Exporting to Markdown: {filepath}")
        
        # Build markdown content
        md_content = f"""# ICS-LogQueryGPT Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total Queries:** {len(results)}

---

"""
        
        # Add summary statistics if metadata included
        if include_metadata:
            total_cost = sum(r.get('cost', 0) for r in results)
            total_tokens = sum(r.get('tokens_used', 0) for r in results)
            cached_results = sum(1 for r in results if r.get('from_cache', False))
            
            md_content += f"""## 📊 Summary Statistics

- **Total Cost:** ${total_cost:.4f}
- **Total Tokens:** {total_tokens:,}
- **Cached Responses:** {cached_results} ({cached_results/len(results)*100:.1f}%)
- **Average Cost per Query:** ${total_cost/len(results):.4f}

---

"""
        
        # Add each query result
        for i, result in enumerate(results, 1):
            query = result.get('question', 'No question')
            answer = result.get('answer', 'No answer')
            mode = result.get('mode', 'analysis')
            cost = result.get('cost', 0)
            tokens = result.get('tokens_used', 0)
            from_cache = result.get('from_cache', False)
            retrieved_logs = result.get('retrieved_logs', [])
            
            md_content += f"""## Query {i}: {query}

**Analysis Mode:** {mode.title()}  
**From Cache:** {'Yes' if from_cache else 'No'}  
**Cost:** ${cost:.4f} | **Tokens:** {tokens}

### Answer

{answer}

"""
            
            # Add retrieved logs section
            if retrieved_logs:
                md_content += f"""### Retrieved Logs ({len(retrieved_logs)} logs)

"""
                for j, log in enumerate(retrieved_logs[:10], 1):  # Limit to top 10
                    protocols = log.get('protocols', 'unknown')
                    score = log.get('similarity_score', 0)
                    log_text = log.get('log_text', '')
                    
                    md_content += f"""**{j}.** `[{protocols}]` Score: {score:.3f}
```
{log_text}
```

"""
            
            md_content += "---\n\n"
        
        # Save markdown
        with open(filepath, 'w', encoding='utf-8') as f:
         f.write(md_content)

        
        print(f"✅ Exported {len(results)} results to Markdown")
        return filepath
    
    def export_detailed_report(self, results: List[Dict], 
                              filepath: Optional[str] = None) -> str:
        """
        Export comprehensive JSON report with all details
        
        Args:
            results: List of query results
            filepath: Custom filepath
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'detailed_report_{timestamp}.json')
        
        print(f"📋 Exporting detailed report: {filepath}")
        
        # Calculate statistics
        total_cost = sum(r.get('cost', 0) for r in results)
        total_tokens = sum(r.get('tokens_used', 0) for r in results)
        cached_count = sum(1 for r in results if r.get('from_cache', False))
        
        # Build detailed report
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_queries': len(results),
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'cached_responses': cached_count,
                'cache_hit_rate': cached_count / len(results) * 100 if results else 0,
                'avg_cost_per_query': total_cost / len(results) if results else 0,
                'avg_tokens_per_query': total_tokens / len(results) if results else 0
            },
            'results': []
        }
        
        # Add each result with full details
        for i, result in enumerate(results, 1):
            detailed_result = {
                'result_id': i,
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'query': {
                    'question': result.get('question', ''),
                    'mode': result.get('mode', 'analysis')
                },
                'answer': result.get('answer', ''),
                'performance': {
                    'tokens_used': result.get('tokens_used', 0),
                    'cost': result.get('cost', 0),
                    'from_cache': result.get('from_cache', False)
                },
                'retrieved_logs': [
                    {
                        'rank': j,
                        'text': log.get('log_text', ''),
                        'original': log.get('original', ''),
                        'protocols': log.get('protocols', 'unknown'),
                        'similarity_score': log.get('similarity_score', 0),
                        'distance': log.get('distance', 0)
                    }
                    for j, log in enumerate(result.get('retrieved_logs', []), 1)
                ]
            }
            
            report['results'].append(detailed_result)
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Exported detailed report with {len(results)} results")
        return filepath
    
    def export_all_formats(self, results: List[Dict], 
                          base_filename: Optional[str] = None) -> Dict[str, str]:
        """
        Export results in all available formats
        
        Args:
            results: List of query results
            base_filename: Base name for files (timestamp used if None)
        
        Returns:
            Dictionary mapping format to filepath
        """
        if base_filename is None:
            base_filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("=" * 60)
        print("📦 EXPORTING TO ALL FORMATS")
        print("=" * 60)
        
        exports = {}
        
        # CSV
        csv_path = os.path.join(self.output_dir, f"{base_filename}.csv")
        exports['csv'] = self.export_to_csv(results, csv_path)
        
        # JSON
        json_path = os.path.join(self.output_dir, f"{base_filename}.json")
        exports['json'] = self.export_to_json(results, json_path)
        
        # Markdown
        md_path = os.path.join(self.output_dir, f"{base_filename}.md")
        exports['markdown'] = self.export_to_markdown(results, md_path)
        
        # Detailed report
        detailed_path = os.path.join(self.output_dir, f"{base_filename}_detailed.json")
        exports['detailed'] = self.export_detailed_report(results, detailed_path)
        
        print("=" * 60)
        print("✅ ALL EXPORTS COMPLETE")
        print("=" * 60)
        
        for format_name, path in exports.items():
            print(f"  {format_name.upper()}: {path}")
        
        return exports
    
    def export_cost_summary(self, results: List[Dict], 
                           filepath: Optional[str] = None) -> str:
        """
        Export cost analysis summary
        
        Args:
            results: List of query results
            filepath: Custom filepath
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'cost_summary_{timestamp}.json')
        
        print(f"💰 Exporting cost summary: {filepath}")
        
        # Calculate cost breakdown
        total_cost = sum(r.get('cost', 0) for r in results)
        total_tokens = sum(r.get('tokens_used', 0) for r in results)
        
        # Group by mode
        mode_costs = {}
        mode_tokens = {}
        mode_counts = {}
        
        for result in results:
            mode = result.get('mode', 'unknown')
            cost = result.get('cost', 0)
            tokens = result.get('tokens_used', 0)
            
            mode_costs[mode] = mode_costs.get(mode, 0) + cost
            mode_tokens[mode] = mode_tokens.get(mode, 0) + tokens
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        # Build summary
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_queries': len(results),
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'average_cost_per_query': total_cost / len(results) if results else 0,
            'average_tokens_per_query': total_tokens / len(results) if results else 0,
            'by_mode': {
                mode: {
                    'queries': mode_counts[mode],
                    'total_cost': mode_costs[mode],
                    'total_tokens': mode_tokens[mode],
                    'avg_cost': mode_costs[mode] / mode_counts[mode],
                    'avg_tokens': mode_tokens[mode] / mode_counts[mode]
                }
                for mode in mode_costs.keys()
            },
            'recommendations': []
        }
        
        # Add recommendations
        if total_cost > 1.0:
            summary['recommendations'].append(
                "Consider enabling caching to reduce costs"
            )
        
        if total_tokens / len(results) > 1000:
            summary['recommendations'].append(
                "Average token usage is high. Consider reducing context size"
            )
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Cost summary exported")
        return filepath


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("RESULTS EXPORTER TEST")
    print("=" * 60)
    
    # Create test results
    test_results = [
        {
            'timestamp': datetime.now().isoformat(),
            'question': 'Show me authentication failures',
            'answer': 'Found 3 authentication failures in the logs. The failures occurred from IP addresses 192.168.1.100, 192.168.1.101, and 192.168.1.102. All failures were for user "admin" and occurred within a 5-minute window, suggesting a potential brute-force attack.',
            'mode': 'security',
            'cost': 0.0024,
            'tokens_used': 450,
            'from_cache': False,
            'retrieved_logs': [
                {
                    'log_text': 'authentication failed for user admin from ip address',
                    'original': 'AUTH FAILED: user=admin ip=192.168.1.100',
                    'protocols': 'ssh',
                    'similarity_score': 0.95,
                    'distance': 0.05
                },
                {
                    'log_text': 'failed login attempt for user admin',
                    'original': 'LOGIN FAILED: user=admin ip=192.168.1.101',
                    'protocols': 'ssh',
                    'similarity_score': 0.89,
                    'distance': 0.11
                },
                {
                    'log_text': 'authentication error user admin',
                    'original': 'AUTH ERROR: user=admin ip=192.168.1.102',
                    'protocols': 'ssh',
                    'similarity_score': 0.82,
                    'distance': 0.18
                }
            ]
        },
        {
            'timestamp': datetime.now().isoformat(),
            'question': 'What modbus errors occurred?',
            'answer': 'There were 2 Modbus communication errors. Device 5 experienced a timeout on function code 3 (read holding registers), and device 7 had a connection refused error.',
            'mode': 'analysis',
            'cost': 0.0018,
            'tokens_used': 380,
            'from_cache': False,
            'retrieved_logs': [
                {
                    'log_text': 'modbus timeout on device num function code num',
                    'original': 'MODBUS TIMEOUT: device=5 fc=3',
                    'protocols': 'modbus',
                    'similarity_score': 0.92,
                    'distance': 0.08
                },
                {
                    'log_text': 'modbus connection refused device num',
                    'original': 'MODBUS ERROR: device=7 connection refused',
                    'protocols': 'modbus',
                    'similarity_score': 0.87,
                    'distance': 0.13
                }
            ]
        },
        {
            'timestamp': datetime.now().isoformat(),
            'question': 'Show me authentication failures',  # Duplicate for cache test
            'answer': 'Found 3 authentication failures in the logs. The failures occurred from IP addresses 192.168.1.100, 192.168.1.101, and 192.168.1.102. All failures were for user "admin" and occurred within a 5-minute window, suggesting a potential brute-force attack.',
            'mode': 'security',
            'cost': 0,
            'tokens_used': 0,
            'from_cache': True,
            'retrieved_logs': []
        }
    ]
    
    # Initialize exporter
    exporter = ResultsExporter(output_dir='data/exports')
    
    print("\n" + "=" * 60)
    print("TEST 1: Export to CSV")
    print("=" * 60)
    csv_file = exporter.export_to_csv(test_results)
    print(f"✅ CSV exported to: {csv_file}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Export to JSON")
    print("=" * 60)
    json_file = exporter.export_to_json(test_results)
    print(f"✅ JSON exported to: {json_file}")
    
    print("\n" + "=" * 60)
    print("TEST 3: Export to Markdown")
    print("=" * 60)
    md_file = exporter.export_to_markdown(test_results)
    print(f"✅ Markdown exported to: {md_file}")
    
    print("\n" + "=" * 60)
    print("TEST 4: Export Detailed Report")
    print("=" * 60)
    detailed_file = exporter.export_detailed_report(test_results)
    print(f"✅ Detailed report exported to: {detailed_file}")
    
    print("\n" + "=" * 60)
    print("TEST 5: Export Cost Summary")
    print("=" * 60)
    cost_file = exporter.export_cost_summary(test_results)
    print(f"✅ Cost summary exported to: {cost_file}")
    
    print("\n" + "=" * 60)
    print("TEST 6: Export All Formats")
    print("=" * 60)
    all_exports = exporter.export_all_formats(test_results, base_filename='test_export')
    
    print("\n✅ Results exporter test complete!")
    print(f"\n📁 Check {exporter.output_dir} for all exported files")
