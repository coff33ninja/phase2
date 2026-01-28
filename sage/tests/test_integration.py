"""Integration tests for Sage."""
import pytest
from pathlib import Path
from conversation.session_manager import SessionManager
from context.context_aggregator import ContextAggregator
from prompts.prompt_builder import PromptBuilder
from feedback.feedback_collector import FeedbackCollector


class TestEndToEndFlow:
    """Test complete end-to-end workflows."""
    
    def test_conversation_flow(self, temp_dir):
        """Test complete conversation flow."""
        # Setup
        session_mgr = SessionManager()
        session_mgr.db_path = temp_dir / "conversations.db"
        session_mgr._initialize_db()
        
        # Create session
        session_id = "test_session_integration"
        assert session_mgr.create_session(session_id)
        
        # Add user message
        session_mgr.add_message(
            session_id,
            "user",
            "Why is my system slow?",
            tokens_used=10
        )
        
        # Add assistant response
        session_mgr.add_message(
            session_id,
            "assistant",
            "Your system is slow because...",
            tokens_used=50
        )
        
        # Verify history
        history = session_mgr.get_session_history(session_id)
        assert len(history) == 2
        # Verify roles exist (order may vary)
        roles = [msg["role"] for msg in history]
        assert "user" in roles
        assert "assistant" in roles
    
    def test_feedback_flow(self, temp_dir):
        """Test feedback collection flow."""
        # Setup
        feedback_collector = FeedbackCollector()
        feedback_collector.db_path = temp_dir / "feedback.db"
        feedback_collector._initialize_db()
        
        # Record feedback
        feedback_id = feedback_collector.record_feedback(
            session_id="test_session",
            query="Test query",
            response="Test response",
            user_action="accepted",
            rating=5,
            comment="Great response!"
        )
        
        assert feedback_id > 0
        
        # Get stats
        stats = feedback_collector.get_feedback_stats()
        assert stats["total_feedback"] == 1
        assert stats["actions"]["accepted"] == 1
        assert stats["avg_rating"] == 5.0
        assert stats["acceptance_rate"] == 100.0
    
    def test_context_and_prompt_flow(self, sample_context):
        """Test context aggregation and prompt building."""
        # Build prompt with context
        prompt = PromptBuilder.build_analysis_prompt(
            query="Analyze my system performance",
            system_state=sample_context["system_state"],
            patterns=sample_context["patterns"],
            anomalies=sample_context["anomalies"],
            predictions=sample_context["predictions"]
        )
        
        # Verify prompt contains all components
        assert "Analyze my system performance" in prompt
        assert "Current System State" in prompt
        assert "CPU: 45.2%" in prompt
        assert "Learned Patterns" in prompt
        assert "Recent Anomalies" in prompt
        assert "Predictions" in prompt
    
    def test_complete_query_workflow(self, temp_dir, sample_context):
        """Test complete query workflow without API call."""
        # Setup all components
        session_mgr = SessionManager()
        session_mgr.db_path = temp_dir / "conversations.db"
        session_mgr._initialize_db()
        
        feedback_collector = FeedbackCollector()
        feedback_collector.db_path = temp_dir / "feedback.db"
        feedback_collector._initialize_db()
        
        # Create session
        session_id = "workflow_test"
        session_mgr.create_session(session_id)
        
        # User query
        query = "Why is my CPU usage high?"
        
        # Build prompt
        prompt = PromptBuilder.build_analysis_prompt(
            query=query,
            system_state=sample_context["system_state"],
            patterns=sample_context["patterns"]
        )
        
        # Simulate response (without actual API call)
        response = "Your CPU usage is high because..."
        tokens_used = 100
        
        # Save to session
        session_mgr.add_message(session_id, "user", query, tokens_used=10)
        session_mgr.add_message(
            session_id,
            "assistant",
            response,
            context=sample_context,
            tokens_used=tokens_used
        )
        
        # Record feedback
        feedback_collector.record_feedback(
            session_id=session_id,
            query=query,
            response=response,
            user_action="accepted",
            rating=4
        )
        
        # Verify everything was saved
        history = session_mgr.get_session_history(session_id)
        assert len(history) == 2
        
        stats = feedback_collector.get_feedback_stats()
        assert stats["total_feedback"] == 1
        assert stats["acceptance_rate"] == 100.0


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_multiple_sessions(self, temp_dir):
        """Test managing multiple sessions."""
        session_mgr = SessionManager()
        session_mgr.db_path = temp_dir / "conversations.db"
        session_mgr._initialize_db()
        
        # Create multiple sessions
        for i in range(5):
            session_id = f"session_{i}"
            session_mgr.create_session(session_id)
            session_mgr.add_message(session_id, "user", f"Message {i}")
        
        # Get recent sessions
        sessions = session_mgr.get_recent_sessions(limit=10)
        assert len(sessions) == 5
    
    def test_feedback_statistics(self, temp_dir):
        """Test feedback statistics calculation."""
        feedback_collector = FeedbackCollector()
        feedback_collector.db_path = temp_dir / "feedback.db"
        feedback_collector._initialize_db()
        
        # Record various feedback
        feedback_collector.record_feedback(
            "s1", "q1", "r1", "accepted", rating=5
        )
        feedback_collector.record_feedback(
            "s2", "q2", "r2", "accepted", rating=4
        )
        feedback_collector.record_feedback(
            "s3", "q3", "r3", "rejected", rating=2
        )
        feedback_collector.record_feedback(
            "s4", "q4", "r4", "modified", rating=3
        )
        
        stats = feedback_collector.get_feedback_stats()
        assert stats["total_feedback"] == 4
        assert stats["actions"]["accepted"] == 2
        assert stats["actions"]["rejected"] == 1
        assert stats["actions"]["modified"] == 1
        assert stats["avg_rating"] == 3.5
        assert stats["acceptance_rate"] == 50.0
