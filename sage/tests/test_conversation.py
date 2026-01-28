"""Tests for conversation management."""
import pytest
from conversation.session_manager import SessionManager


class TestSessionManager:
    """Test session manager."""
    
    def test_initialization(self, temp_dir):
        """Test session manager initialization."""
        db_path = temp_dir / "conversations.db"
        manager = SessionManager()
        manager.db_path = db_path
        manager._initialize_db()
        
        assert db_path.exists()
    
    def test_create_session(self, temp_dir):
        """Test creating a session."""
        db_path = temp_dir / "conversations.db"
        manager = SessionManager()
        manager.db_path = db_path
        manager._initialize_db()
        
        result = manager.create_session("test_session_1")
        assert result is True
        
        # Try creating duplicate
        result = manager.create_session("test_session_1")
        assert result is False
    
    def test_add_message(self, temp_dir):
        """Test adding a message."""
        db_path = temp_dir / "conversations.db"
        manager = SessionManager()
        manager.db_path = db_path
        manager._initialize_db()
        
        manager.create_session("test_session")
        manager.add_message(
            "test_session",
            "user",
            "Hello Sage",
            context={"test": "data"},
            tokens_used=10
        )
        
        history = manager.get_session_history("test_session")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello Sage"
        assert history[0]["tokens_used"] == 10
    
    def test_get_session_history(self, temp_dir):
        """Test getting session history."""
        db_path = temp_dir / "conversations.db"
        manager = SessionManager()
        manager.db_path = db_path
        manager._initialize_db()
        
        manager.create_session("test_session")
        manager.add_message("test_session", "user", "Message 1")
        manager.add_message("test_session", "assistant", "Response 1")
        manager.add_message("test_session", "user", "Message 2")
        
        history = manager.get_session_history("test_session")
        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[2]["role"] == "user"
    
    def test_get_recent_sessions(self, temp_dir):
        """Test getting recent sessions."""
        db_path = temp_dir / "conversations.db"
        manager = SessionManager()
        manager.db_path = db_path
        manager._initialize_db()
        
        manager.create_session("session_1")
        manager.create_session("session_2")
        manager.add_message("session_1", "user", "Test")
        
        sessions = manager.get_recent_sessions()
        assert len(sessions) >= 2
        assert any(s["session_id"] == "session_1" for s in sessions)
        assert any(s["session_id"] == "session_2" for s in sessions)
