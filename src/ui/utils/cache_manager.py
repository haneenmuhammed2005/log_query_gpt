"""
Cache Manager - Query result caching for performance
Author: Haneen
Created: Week 5 Day 4
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """Manages query result caching"""
    
    def __init__(
        self,
        db_path: str = "data/cache.db",
        ttl_hours: int = 24
    ):
        """
        Initialize CacheManager
        
        Args:
            db_path: Path to cache database
            ttl_hours: Time to live for cache entries (hours)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self._init_database()
    
    def _init_database(self):
        """Create cache table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                query TEXT NOT NULL,
                protocol TEXT,
                mode TEXT,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                hit_count INTEGER DEFAULT 0,
                last_hit TIMESTAMP
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_key 
            ON query_cache(cache_key)
        """)
        
        # Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_queries INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                cache_misses INTEGER DEFAULT 0,
                hit_rate REAL DEFAULT 0.0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Cache database initialized at {self.db_path}")
    
    def _generate_cache_key(
        self,
        query: str,
        protocol: str = "All",
        mode: str = "Analysis"
    ) -> str:
        """
        Generate unique cache key for query
        
        Args:
            query: User query text
            protocol: Protocol filter
            mode: Analysis mode
        
        Returns:
            MD5 hash as cache key
        """
        # Normalize inputs
        query_lower = query.strip().lower()
        cache_string = f"{query_lower}|{protocol}|{mode}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_response(
        self,
        query: str,
        protocol: str = "All",
        mode: str = "Analysis"
    ) -> Optional[str]:
        """
        Get cached response if available and not expired
        
        Args:
            query: User query
            protocol: Protocol filter
            mode: Analysis mode
        
        Returns:
            Cached response or None
        """
        cache_key = self._generate_cache_key(query, protocol, mode)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT response, expires_at
                FROM query_cache
                WHERE cache_key = ?
            """, (cache_key,))
            
            result = cursor.fetchone()
            
            if not result:
                # Cache miss
                self._record_cache_miss()
                conn.close()
                logger.info("Cache MISS")
                return None
            
            response, expires_at_str = result
            expires_at = datetime.fromisoformat(expires_at_str)
            
            # Check if expired
            if datetime.now() > expires_at:
                # Expired, delete and return None
                logger.info("Cache MISS (expired)")
                cursor.execute("DELETE FROM query_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                self._record_cache_miss()
                conn.close()
                return None
            
            # Cache hit! Update statistics
            cursor.execute("""
                UPDATE query_cache
                SET hit_count = hit_count + 1,
                    last_hit = CURRENT_TIMESTAMP
                WHERE cache_key = ?
            """, (cache_key,))
            
            conn.commit()
            conn.close()
            
            self._record_cache_hit()
            logger.info("Cache HIT ⚡")
            return response
            
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None
    
    def cache_response(
        self,
        query: str,
        response: str,
        protocol: str = "All",
        mode: str = "Analysis"
    ) -> bool:
        """
        Cache query response
        
        Args:
            query: User query
            response: Query response to cache
            protocol: Protocol filter
            mode: Analysis mode
        
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key(query, protocol, mode)
        expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO query_cache
                (cache_key, query, protocol, mode, response, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                query,
                protocol,
                mode,
                response,
                expires_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Response cached (expires in {self.ttl_hours}h)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False
    
    def _record_cache_hit(self):
        """Record cache hit in statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            
            cursor.execute("""
                INSERT INTO cache_stats (date, total_queries, cache_hits, cache_misses)
                VALUES (?, 1, 1, 0)
                ON CONFLICT(date) DO UPDATE SET
                    total_queries = total_queries + 1,
                    cache_hits = cache_hits + 1,
                    hit_rate = CAST(cache_hits AS REAL) / total_queries
            """, (today,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording cache hit: {e}")
    
    def _record_cache_miss(self):
        """Record cache miss in statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            
            cursor.execute("""
                INSERT INTO cache_stats (date, total_queries, cache_hits, cache_misses)
                VALUES (?, 1, 0, 1)
                ON CONFLICT(date) DO UPDATE SET
                    total_queries = total_queries + 1,
                    cache_misses = cache_misses + 1,
                    hit_rate = CAST(cache_hits AS REAL) / total_queries
            """, (today,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording cache miss: {e}")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Today's stats
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT total_queries, cache_hits, cache_misses, hit_rate
                FROM cache_stats
                WHERE date = ?
            """, (today,))
            
            today_stats = cursor.fetchone()
            
            # Total cached entries
            cursor.execute("SELECT COUNT(*) FROM query_cache")
            total_entries = cursor.fetchone()[0]
            
            # Most hit queries
            cursor.execute("""
                SELECT query, hit_count
                FROM query_cache
                ORDER BY hit_count DESC
                LIMIT 5
            """)
            top_queries = cursor.fetchall()
            
            conn.close()
            
            if today_stats:
                total_q, hits, misses, hit_rate = today_stats
            else:
                total_q, hits, misses, hit_rate = 0, 0, 0, 0.0
            
            return {
                'today': {
                    'total_queries': total_q,
                    'cache_hits': hits,
                    'cache_misses': misses,
                    'hit_rate': hit_rate
                },
                'total_cached_entries': total_entries,
                'top_queries': [{'query': q, 'hits': h} for q, h in top_queries]
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            Number of entries deleted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("DELETE FROM query_cache WHERE expires_at < ?", (now,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} expired cache entries")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def clear_all_cache(self) -> bool:
        """Clear all cached entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM query_cache")
            cursor.execute("DELETE FROM cache_stats")
            
            conn.commit()
            conn.close()
            
            logger.info("All cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


# Test the CacheManager
if __name__ == "__main__":
    print("Testing CacheManager...")
    
    cm = CacheManager("data/test_cache.db", ttl_hours=24)
    
    # Test 1: Cache miss (first query)
    print("\n1. First query (should be cache MISS)...")
    response = cm.get_cached_response("show failed logins", "All", "Analysis")
    print(f"   Response: {response}")
    
    # Test 2: Cache a response
    print("\n2. Caching response...")
    result = cm.cache_response(
        "show failed logins",
        "Found 12 failed login attempts...",
        "All",
        "Analysis"
    )
    print(f"   Cached: {result}")
    
    # Test 3: Cache hit (same query)
    print("\n3. Same query (should be cache HIT)...")
    response = cm.get_cached_response("show failed logins", "All", "Analysis")
    print(f"   Response: {response[:50]}...")
    
    # Test 4: Cache stats
    print("\n4. Getting cache statistics...")
    stats = cm.get_cache_stats()
    print(f"   Today's queries: {stats['today']['total_queries']}")
    print(f"   Cache hits: {stats['today']['cache_hits']}")
    print(f"   Hit rate: {stats['today']['hit_rate']:.2%}")
    
    # Test 5: Cleanup
    print("\n5. Cleaning up expired entries...")
    deleted = cm.cleanup_expired_cache()
    print(f"   Deleted: {deleted}")
    
    print("\n✅ All tests completed!")