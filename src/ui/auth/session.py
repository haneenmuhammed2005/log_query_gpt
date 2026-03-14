"""
Session Manager - Handles user session lifecycle
Author: Haneen
Created: Week 5 Day 2
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with timeout support"""
    
    def __init__(
        self,
        db_path: str = "data/sessions.db",
        timeout_minutes: int = 30
    ):
        """
        Initialize SessionManager
        
        Args:
            db_path: Path to session database
            timeout_minutes: Session timeout in minutes (default 30)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.timeout_minutes = timeout_minutes
        self._init_database()
    
    def _init_database(self):
        """Create sessions table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                user_role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_token 
            ON sessions(session_token)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Session database initialized at {self.db_path}")
    
    def create_session(self, user: Dict) -> str:
        """
        Create new session for authenticated user
        
        Args:
            user: User dict from UserManager.authenticate()
                  {'id': 1, 'username': 'admin', 'role': 'admin'}
        
        Returns:
            Session token (UUID)
        """
        try:
            # Generate unique session token
            session_token = str(uuid.uuid4())
            
            # Calculate expiration time
            now = datetime.now()
            expires_at = now + timedelta(minutes=self.timeout_minutes)
            
            # Insert session
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions 
                (session_token, user_id, username, user_role, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_token,
                user['id'],
                user['username'],
                user['role'],
                expires_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session created for user '{user['username']}' (expires in {self.timeout_minutes} min)")
            return session_token
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate session token and return user info
        
        Args:
            session_token: Session token to validate
        
        Returns:
            User dict if session valid, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, user_role, expires_at, active
                FROM sessions
                WHERE session_token = ?
            """, (session_token,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.warning("Session validation failed: Token not found")
                conn.close()
                return None
            
            user_id, username, user_role, expires_at_str, active = result
            
            # Check if session is active
            if not active:
                logger.warning(f"Session validation failed: Session inactive for '{username}'")
                conn.close()
                return None
            
            # Check if session expired
            expires_at = datetime.fromisoformat(expires_at_str)
            now = datetime.now()
            
            if now > expires_at:
                logger.warning(f"Session expired for '{username}'")
                # Mark session as inactive
                self._deactivate_session(session_token)
                conn.close()
                return None
            
            # Update last activity
            cursor.execute("""
                UPDATE sessions
                SET last_activity = CURRENT_TIMESTAMP
                WHERE session_token = ?
            """, (session_token,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session validated for '{username}'")
            
            return {
                'id': user_id,
                'username': username,
                'role': user_role
            }
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def _deactivate_session(self, session_token: str):
        """Mark session as inactive"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions
                SET active = 0
                WHERE session_token = ?
            """, (session_token,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error deactivating session: {e}")
    
    def destroy_session(self, session_token: str) -> bool:
        """
        Destroy session (logout)
        
        Args:
            session_token: Session token to destroy
        
        Returns:
            True if session destroyed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions
                SET active = 0
                WHERE session_token = ?
            """, (session_token,))
            
            conn.commit()
            conn.close()
            
            logger.info("Session destroyed")
            return True
            
        except Exception as e:
            logger.error(f"Error destroying session: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                DELETE FROM sessions
                WHERE expires_at < ? OR active = 0
            """, (now,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} expired/inactive sessions")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0
    
    def get_active_sessions(self) -> int:
        """Get count of active sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                SELECT COUNT(*) FROM sessions
                WHERE active = 1 AND expires_at > ?
            """, (now,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return 0
    
    def extend_session(self, session_token: str) -> bool:
        """
        Extend session timeout (renew)
        
        Args:
            session_token: Session to extend
        
        Returns:
            True if extended successfully
        """
        try:
            # First validate session
            user = self.validate_session(session_token)
            if not user:
                return False
            
            # Extend expiration
            new_expires_at = datetime.now() + timedelta(minutes=self.timeout_minutes)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions
                SET expires_at = ?
                WHERE session_token = ?
            """, (new_expires_at.isoformat(), session_token))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session extended for '{user['username']}'")
            return True
            
        except Exception as e:
            logger.error(f"Error extending session: {e}")
            return False


# Test the SessionManager
if __name__ == "__main__":
    print("Testing SessionManager...")
    
    # Initialize
    sm = SessionManager("data/test_sessions.db", timeout_minutes=1)  # 1 min for testing
    
    # Mock user (would come from UserManager.authenticate())
    test_user = {
        'id': 1,
        'username': 'testuser',
        'role': 'analyst'
    }
    
    # Test 1: Create session
    print("\n1. Creating session...")
    token = sm.create_session(test_user)
    print(f"   Token: {token}")
    
    # Test 2: Validate session immediately
    print("\n2. Validating session (should succeed)...")
    user = sm.validate_session(token)
    print(f"   User: {user}")
    
    # Test 3: Check active sessions
    print("\n3. Checking active sessions...")
    count = sm.get_active_sessions()
    print(f"   Active sessions: {count}")
    
    # Test 4: Extend session
    print("\n4. Extending session...")
    result = sm.extend_session(token)
    print(f"   Extended: {result}")
    
    # Test 5: Destroy session
    print("\n5. Destroying session...")
    result = sm.destroy_session(token)
    print(f"   Destroyed: {result}")
    
    # Test 6: Validate after destroy (should fail)
    print("\n6. Validating destroyed session (should fail)...")
    user = sm.validate_session(token)
    print(f"   User: {user}")
    
    # Test 7: Cleanup
    print("\n7. Cleaning up expired sessions...")
    deleted = sm.cleanup_expired_sessions()
    print(f"   Deleted: {deleted}")
    
    print("\n✅ All tests completed!")