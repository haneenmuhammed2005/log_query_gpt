"""
User Manager - Handles all user database operations
Author: Haneen
Created: Week 5 Day 1
"""

import sqlite3
import bcrypt
from pathlib import Path
from typing import Optional, Dict, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, db_path: str = "data/users.db"):
        """
        Initialize UserManager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._create_default_admin()
    
    def _init_database(self):
        """Create users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _create_default_admin(self):
        """Create default admin account if no users exist"""
        if self.get_user_count() == 0:
            self.create_user(
                username="admin",
                password="admin123",  # TODO: Change on first login
                role="admin"
            )
            logger.warning("Default admin account created! Username: admin, Password: admin123")
            logger.warning("CHANGE THIS PASSWORD IMMEDIATELY!")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Stored hash
            
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def create_user(
        self,
        username: str,
        password: str,
        role: str = "analyst"
    ) -> bool:
        """
        Create new user account
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            role: User role (admin, analyst, viewer)
            
        Returns:
            True if user created successfully
        """
        try:
            # Validate inputs
            if len(username) < 3:
                logger.error("Username must be at least 3 characters")
                return False
            
            if len(password) < 8:
                logger.error("Password must be at least 8 characters")
                return False
            
            if role not in ['admin', 'analyst', 'viewer']:
                logger.error(f"Invalid role: {role}")
                return False
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"User '{username}' created successfully with role '{role}'")
            return True
            
        except sqlite3.IntegrityError:
            logger.error(f"Username '{username}' already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User dict if authentication successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, password_hash, role, active FROM users WHERE username = ?",
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                logger.warning(f"Authentication failed: User '{username}' not found")
                return None
            
            user_id, username, password_hash, role, active = result
            
            # Check if account is active
            if not active:
                logger.warning(f"Authentication failed: User '{username}' is disabled")
                return None
            
            # Verify password
            if not self._verify_password(password, password_hash):
                logger.warning(f"Authentication failed: Invalid password for '{username}'")
                return None
            
            # Update last login
            self._update_last_login(user_id)
            
            logger.info(f"User '{username}' authenticated successfully")
            
            return {
                'id': user_id,
                'username': username,
                'role': role
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def _update_last_login(self, user_id: int):
        """Update last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user information
        
        Args:
            username: Username to lookup
            
        Returns:
            User dict or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, role, created_at, last_login, active FROM users WHERE username = ?",
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            return {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'created_at': result[3],
                'last_login': result[4],
                'active': result[5]
            }
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        # First verify old password
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        # Validate new password
        if len(new_password) < 8:
            logger.error("New password must be at least 8 characters")
            return False
        
        try:
            # Hash new password
            new_hash = self._hash_password(new_password)
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (new_hash, username)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Password changed for user '{username}'")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """
        Delete user (admin only - check in UI)
        
        Args:
            username: Username to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User '{username}' deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def list_users(self) -> List[Dict]:
        """
        Get list of all users (admin only - check in UI)
        
        Returns:
            List of user dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, role, created_at, last_login, active FROM users ORDER BY username"
            )
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'created_at': row[3],
                    'last_login': row[4],
                    'active': row[5]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []


# Test the UserManager
if __name__ == "__main__":
    print("Testing UserManager...")
    
    # Initialize
    um = UserManager("data/test_users.db")
    
    # Test user creation
    print("\n1. Creating test user...")
    result = um.create_user("testuser", "password123", "analyst")
    print(f"   Result: {result}")
    
    # Test authentication - correct password
    print("\n2. Testing authentication (correct password)...")
    user = um.authenticate("testuser", "password123")
    print(f"   Result: {user}")
    
    # Test authentication - wrong password
    print("\n3. Testing authentication (wrong password)...")
    user = um.authenticate("testuser", "wrongpass")
    print(f"   Result: {user}")
    
    # Test get user
    print("\n4. Getting user info...")
    user_info = um.get_user("testuser")
    print(f"   Result: {user_info}")
    
    # Test password change
    print("\n5. Changing password...")
    result = um.change_password("testuser", "password123", "newpassword456")
    print(f"   Result: {result}")
    
    # Test authentication with new password
    print("\n6. Testing authentication with new password...")
    user = um.authenticate("testuser", "newpassword456")
    print(f"   Result: {user}")
    
    # List all users
    print("\n7. Listing all users...")
    users = um.list_users()
    for u in users:
        print(f"   - {u['username']} ({u['role']})")
    
    print("\n✅ All tests completed!")