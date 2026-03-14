"""
Authentication System Tests
Author: Haneen
Created: Week 5 Day 7
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.user_manager import UserManager
from src.ui.auth.session import SessionManager

class TestUserManager:
    """Test UserManager functionality"""
    
    @pytest.fixture
    def um(self, tmp_path):
        """Create temporary UserManager"""
        db_path = tmp_path / "test_users.db"
        return UserManager(str(db_path))
    
    def test_create_user(self, um):
        """Test user creation"""
        result = um.create_user("testuser", "password123", "analyst")
        assert result == True
        
        # Verify user exists
        user = um.get_user("testuser")
        assert user is not None
        assert user['username'] == "testuser"
        assert user['role'] == "analyst"
    
    def test_create_duplicate_user(self, um):
        """Test duplicate username rejection"""
        um.create_user("testuser", "password123", "analyst")
        result = um.create_user("testuser", "different_pass", "admin")
        assert result == False
    
    def test_authenticate_success(self, um):
        """Test successful authentication"""
        um.create_user("testuser", "password123", "analyst")
        user = um.authenticate("testuser", "password123")
        assert user is not None
        assert user['username'] == "testuser"
    
    def test_authenticate_wrong_password(self, um):
        """Test authentication with wrong password"""
        um.create_user("testuser", "password123", "analyst")
        user = um.authenticate("testuser", "wrongpassword")
        assert user is None
    
    def test_authenticate_nonexistent_user(self, um):
        """Test authentication with nonexistent user"""
        user = um.authenticate("nonexistent", "password123")
        assert user is None
    
    def test_change_password(self, um):
        """Test password change"""
        um.create_user("testuser", "oldpassword", "analyst")
        
        # Change password
        result = um.change_password("testuser", "oldpassword", "newpassword")
        assert result == True
        
        # Verify old password doesn't work
        user = um.authenticate("testuser", "oldpassword")
        assert user is None
        
        # Verify new password works
        user = um.authenticate("testuser", "newpassword")
        assert user is not None
    
    def test_password_validation(self, um):
        """Test password requirements"""
        # Too short
        result = um.create_user("testuser", "short", "analyst")
        assert result == False
    
    def test_username_validation(self, um):
        """Test username requirements"""
        # Too short
        result = um.create_user("ab", "password123", "analyst")
        assert result == False


class TestSessionManager:
    """Test SessionManager functionality"""
    
    @pytest.fixture
    def sm(self, tmp_path):
        """Create temporary SessionManager"""
        db_path = tmp_path / "test_sessions.db"
        return SessionManager(str(db_path), timeout_minutes=1)
    
    @pytest.fixture
    def test_user(self):
        """Test user dict"""
        return {
            'id': 1,
            'username': 'testuser',
            'role': 'analyst'
        }
    
    def test_create_session(self, sm, test_user):
        """Test session creation"""
        token = sm.create_session(test_user)
        assert token is not None
        assert len(token) == 36  # UUID length
    
    def test_validate_session(self, sm, test_user):
        """Test session validation"""
        token = sm.create_session(test_user)
        user = sm.validate_session(token)
        assert user is not None
        assert user['username'] == 'testuser'
    
    def test_validate_invalid_token(self, sm):
        """Test validation with invalid token"""
        user = sm.validate_session("invalid-token-12345")
        assert user is None
    
    def test_destroy_session(self, sm, test_user):
        """Test session destruction"""
        token = sm.create_session(test_user)
        
        # Destroy session
        result = sm.destroy_session(token)
        assert result == True
        
        # Verify session invalid
        user = sm.validate_session(token)
        assert user is None
    
    def test_session_timeout(self, sm, test_user):
        """Test session timeout"""
        import time
        
        token = sm.create_session(test_user)
        
        # Wait for timeout (1 minute + buffer)
        time.sleep(65)
        
        # Session should be expired
        user = sm.validate_session(token)
        assert user is None
    
    def test_extend_session(self, sm, test_user):
        """Test session extension"""
        token = sm.create_session(test_user)
        result = sm.extend_session(token)
        assert result == True
    
    def test_active_sessions_count(self, sm, test_user):
        """Test active session counting"""
        # Create 3 sessions
        sm.create_session(test_user)
        sm.create_session(test_user)
        sm.create_session(test_user)
        
        count = sm.get_active_sessions()
        assert count == 3


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])