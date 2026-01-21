import re
from typing import Dict, List
import pandas as pd

class ProtocolDetector:
    """Detect ICS/SCADA protocols in log entries with improved accuracy"""
    
    def __init__(self):
        # Extended protocol patterns for ICS environments
        # Patterns are ordered by priority (most specific first)
        self.protocol_patterns = {
            'modbus': [
                r'\bmodbus\b',
                r'function\s*code\s*\d+',
                r'coil\s*(read|write)',
                r'register\s*(holding|input)',
                r'mb\s*tcp',
                r'\bport\s*502\b'  # Modbus TCP port
            ],
            'dnp3': [
                r'\bdnp3\b',
                r'\bdnp\s*3\b',
                r'\boutstation\b',
                r'master\s*station',
                r'integrity\s*poll',
                r'\bport\s*20000\b'  # DNP3 port
            ],
            'snmp': [
                r'\bsnmp\b',
                r'\boid\b',
                r'trap\s*(received|sent)',
                r'community\s*string',
                r'snmp\s*get',  # More specific - requires "snmp" before "get"
                r'\bport\s*16[12]\b'  # SNMP ports 161, 162
            ],
            'http': [
                r'\bhttp[s]?\b',
                r'http\s*(get|post|put|delete)',  # HTTP-specific methods
                r'status\s*code\s*\d+',
                r'rest\s*api',
                r'\bport\s*(80|443|8080)\b'  # HTTP ports
            ],
            'ssh': [
                r'\bssh\b',
                r'authentication\s*(failed|success)',
                r'public\s*key',
                r'login\s*attempt',
                r'\bport\s*22\b'  # SSH port
            ],
            'ftp': [
                r'\bftp\b',
                r'file\s*transfer',
                r'(upload|download)\s*(failed|success)',
                r'\bport\s*21\b'  # FTP port
            ],
            'telnet': [
                r'\btelnet\b',
                r'\bport\s*23\b'  # Telnet port
            ],
            'bacnet': [
                r'\bbacnet\b',
                r'\bbac/ip\b',
                r'\bport\s*47808\b'  # BACnet port
            ]
        }
        
        # Severity keywords for priority detection
        self.severity_keywords = {
            'critical': r'\b(critical|fatal|emergency)\b',
            'high': r'\b(error|failed|failure|denied)\b',
            'medium': r'\b(warning|timeout|retry)\b',
            'low': r'\b(info|debug|notice)\b'
        }
    
    def detect_protocol(self, log_text: str) -> List[str]:
        """
        Detect which protocols are mentioned in a log entry
        Uses priority-based matching to avoid false positives
        
        Args:
            log_text: Raw log string
            
        Returns:
            List of detected protocols (empty list = unknown)
        """
        log_lower = log_text.lower()
        detected = []
        
        # Check for explicit protocol mentions first (high priority)
        explicit_protocols = {
            'modbus': r'\bmodbus\b',
            'dnp3': r'\b(dnp3|dnp\s*3)\b',
            'snmp': r'\bsnmp\b',
            'http': r'\bhttp[s]?\b',
            'ssh': r'\bssh\b',
            'ftp': r'\bftp\b',
            'telnet': r'\btelnet\b',
            'bacnet': r'\bbacnet\b'
        }
        
        # First pass: look for explicit protocol names
        for protocol, pattern in explicit_protocols.items():
            if re.search(pattern, log_lower):
                detected.append(protocol)
        
        # If explicit protocols found, return them
        if detected:
            return detected
        
        # Second pass: look for protocol-specific patterns (only if no explicit match)
        for protocol, patterns in self.protocol_patterns.items():
            for pattern in patterns:
                if re.search(pattern, log_lower):
                    # Avoid ambiguous matches
                    # Skip generic patterns like "get" or "post" without context
                    if protocol == 'http' and re.search(r'\b(get|post|put|delete)\b', pattern):
                        # Only match HTTP methods if no other protocol detected
                        if not detected:
                            detected.append(protocol)
                            break
                    else:
                        detected.append(protocol)
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_detected = []
        for p in detected:
            if p not in seen:
                seen.add(p)
                unique_detected.append(p)
        
        return unique_detected if unique_detected else ['unknown']
    
    def detect_severity(self, log_text: str) -> str:
        """Detect log severity level"""
        log_lower = log_text.lower()
        
        # Check in order of priority (critical -> high -> medium -> low)
        for level in ['critical', 'high', 'medium', 'low']:
            pattern = self.severity_keywords[level]
            if re.search(pattern, log_lower):
                return level
        
        return 'info'
    
    def add_protocol_tags(self, log_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add protocol and severity columns to dataframe
        
        Args:
            log_df: DataFrame with 'original' column
            
        Returns:
            Enhanced DataFrame with 'protocols' and 'severity' columns
        """
        print("🏷️ Detecting protocols in logs...")
        
        # Detect protocols
        log_df['protocols'] = log_df['original'].apply(
            lambda x: ','.join(self.detect_protocol(x))
        )
        
        # Detect severity
        log_df['severity'] = log_df['original'].apply(
            self.detect_severity
        )
        
        # Count detections
        protocol_counts = {}
        for protocols in log_df['protocols']:
            for p in protocols.split(','):
                protocol_counts[p] = protocol_counts.get(p, 0) + 1
        
        print("\n📊 Protocol Distribution:")
        for protocol, count in sorted(protocol_counts.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True):
            percentage = (count / len(log_df)) * 100
            print(f"  {protocol:15} {count:6} ({percentage:.1f}%)")
        
        return log_df
    
    def get_protocol_stats(self, log_df: pd.DataFrame) -> Dict:
        """Get comprehensive protocol statistics"""
        stats = {
            'total_logs': len(log_df),
            'protocols': {},
            'severity': log_df['severity'].value_counts().to_dict()
        }
        
        for protocols in log_df['protocols']:
            for p in protocols.split(','):
                if p not in stats['protocols']:
                    stats['protocols'][p] = 0
                stats['protocols'][p] += 1
        
        return stats

# Test and demonstrate
if __name__ == "__main__":
    detector = ProtocolDetector()
    
    # Test cases
    test_logs = [
        "modbus read coil failed on device 5 at register 100",
        "snmp trap received from 192.168.1.10 with OID 1.3.6.1",
        "http get request timeout after 30 seconds",
        "dnp3 outstation integrity poll completed",
        "ssh authentication failed for user admin from 10.0.0.5",
        "unknown error occurred in system component",
        "critical bacnet device offline on network 47808",
        "get request completed successfully",  # Should not match anything specific
        "snmp get request from monitoring system"  # Should match SNMP only
    ]
    
    print("🧪 Testing Protocol Detection:\n")
    for log in test_logs:
        protocols = detector.detect_protocol(log)
        severity = detector.detect_severity(log)
        print(f"Log: {log[:60]}...")
        print(f"  ├─ Protocols: {protocols}")
        print(f"  └─ Severity: {severity}\n")
    
    # Test with DataFrame
    print("\n" + "="*70)
    print("Testing with DataFrame:")
    print("="*70)
    
    test_df = pd.DataFrame({
        'original': test_logs,
        'cleaned': [log.lower() for log in test_logs]
    })
    
    enhanced_df = detector.add_protocol_tags(test_df)
    print("\n✅ Enhanced DataFrame Preview:")
    print(enhanced_df[['original', 'protocols', 'severity']].head())