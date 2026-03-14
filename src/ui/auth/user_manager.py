"""
User Manager - Handles all user database operations
Author: Haneen
"""

import sqlite3
import bcrypt
from pathlib import Path
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    """Manages user accounts and authentication"""

    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._create_default_admin()

    def _init_database(self):
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

    def _create_default_admin(self):
        if self.get_user_count() == 0:
            self.create_user("admin", "admin123", role="admin", skip_password_check=True)
            logger.warning("Default admin created: admin / admin123")

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def user_exists(self, username: str) -> bool:
        """Check if a username already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return False

    def create_user(self, username: str, password: str, role: str = "analyst", skip_password_check: bool = False) -> bool:
        """Create new user account"""
        try:
            if len(username) < 3:
                logger.error("Username must be at least 3 characters")
                return False

            if not skip_password_check and len(password) < 6:
                logger.error("Password must be at least 6 characters")
                return False

            if role not in ['admin', 'analyst', 'viewer']:
                role = 'analyst'

            password_hash = self._hash_password(password)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            conn.close()

            logger.info(f"User '{username}' created with role '{role}'")
            return True

        except sqlite3.IntegrityError:
            logger.error(f"Username '{username}' already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
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
                return None

            user_id, uname, password_hash, role, active = result

            if not active:
                return None

            if not self._verify_password(password, password_hash):
                return None

            self._update_last_login(user_id)

            return {'id': user_id, 'username': uname, 'role': role}

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def _update_last_login(self, user_id: int):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")

    def get_user(self, username: str) -> Optional[Dict]:
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
            return {'id': result[0], 'username': result[1], 'role': result[2],
                    'created_at': result[3], 'last_login': result[4], 'active': result[5]}
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def get_user_count(self) -> int:
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
        user = self.authenticate(username, old_password)
        if not user:
            return False
        if len(new_password) < 6:
            return False
        try:
            new_hash = self._hash_password(new_password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def list_users(self) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, created_at, last_login, active FROM users ORDER BY username")
            users = []
            for row in cursor.fetchall():
                users.append({'id': row[0], 'username': row[1], 'role': row[2],
                               'created_at': row[3], 'last_login': row[4], 'active': row[5]})
            conn.close()
            return users
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
