import pandas as pd
import re
import os
from typing import List

class LogCleaner:
    """Clean and preprocess log messages"""
    
    def clean_single_log(self, log: str) -> str:
        """Clean one log message"""
        # Lowercase
        log = log.lower()
        
        # Remove timestamps
        log = re.sub(r'\d{4}-\d{2}-\d{2}', '', log)
        log = re.sub(r'\d{2}:\d{2}:\d{2}', '', log)
        
        # Remove IP addresses
        log = re.sub(r'\d{1,3}(\.\d{1,3}){3}', ' ipaddr ', log)
        
        # Remove hex addresses
        log = re.sub(r'0x[0-9a-fA-F]+', ' hexaddr ', log)
        
        # Remove standalone numbers
        log = re.sub(r'\b\d+\b', ' num ', log)

        
        # Remove special characters
        log = re.sub(r'[^a-z\s]', ' ', log)
        
        # Remove extra spaces
        log = ' '.join(log.split())
        
        return log.strip()
    
    def clean_batch(self, logs: List[str]) -> List[str]:
        """Clean multiple logs"""
        print(f"🧹 Cleaning {len(logs)} logs...")
        return [self.clean_single_log(log) for log in logs]
    
    def save_to_csv(self, original_logs: List[str], 
                    cleaned_logs: List[str], filepath: str):
        """Save to CSV"""
        df = pd.DataFrame({
            'original': original_logs,
            'cleaned': cleaned_logs
        })
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"💾 Saved to {filepath}")

# Test
if __name__ == "__main__":
    cleaner = LogCleaner()
    
    test_logs = [
        "2024-01-15 10:30:45 ERROR: Auth failed from 192.168.1.100",
        "Connection timeout 0x7fff on port 8080"
    ]
    
    cleaned = cleaner.clean_batch(test_logs)
    
    for orig, clean in zip(test_logs, cleaned):
        print(f"Original: {orig}")
        print(f"Cleaned:  {clean}\n")