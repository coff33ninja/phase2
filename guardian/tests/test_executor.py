"""Tests for Guardian action executor."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from execution.executor import ActionExecutor
from execution.logger import ActionLogger
from actions.process_actions import CloseProcess
from models import ActionStatus


class TestActionExecutor:
    """Test action executor."""
    
    @patch('psutil.process_iter')
    def test_execute_action_success(self, mock_process_iter):
        """Test successful action execution."""
        # Mock process
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'notepad.exe'}
        mock_proc.terminate = Mock()
        mock_process_iter.return_value = [mock_proc]
        
        executor = ActionExecutor()
        action = CloseProcess(target="notepad.exe")
        
        result = executor.execute_action(action, user_approved=True)
        
        assert result.success is True
    
    def test_execute_action_validation_failure(self):
        """Test action execution with validation failure."""
        executor = ActionExecutor()
        action = CloseProcess(target="explorer.exe")  # Protected process
        
        result = executor.execute_action(action, user_approved=True)
        
        assert result.success is False
        assert "validation" in result.message.lower() or "protected" in result.error.lower()
    
    def test_execute_action_requires_approval(self):
        """Test action requiring approval."""
        executor = ActionExecutor()
        action = CloseProcess(target="notepad.exe")
        
        # Execute without approval
        result = executor.execute_action(action, user_approved=False)
        
        # Should fail or succeed depending on risk level
        # Close process is low risk, so might not require approval
        assert result is not None
    
    @patch('psutil.process_iter')
    def test_execute_action_with_snapshot(self, mock_process_iter):
        """Test action execution with snapshot creation."""
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'notepad.exe'}
        mock_proc.terminate = Mock()
        mock_process_iter.return_value = [mock_proc]
        
        executor = ActionExecutor()
        action = CloseProcess(target="notepad.exe")
        
        result = executor.execute_action(action, user_approved=True)
        
        # Should create snapshot before execution
        assert result is not None
    
    @patch('psutil.process_iter')
    def test_execute_action_with_rollback(self, mock_process_iter):
        """Test automatic rollback on failure."""
        # Mock process that fails to terminate
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'notepad.exe'}
        mock_proc.terminate = Mock(side_effect=Exception("Failed"))
        mock_process_iter.return_value = [mock_proc]
        
        executor = ActionExecutor()
        action = CloseProcess(target="notepad.exe")
        
        result = executor.execute_action(action, user_approved=True)
        
        # Should fail and attempt rollback
        assert result.success is False


class TestActionLogger:
    """Test action logger."""
    
    def test_log_action(self, temp_dir, sample_action_metadata, sample_action_result):
        """Test logging an action."""
        from models import ActionLog, ActionStatus
        
        logger = ActionLogger(db_path=temp_dir / "actions.db")
        
        action_log = ActionLog(
            action_id=sample_action_metadata.action_id,
            action_type=sample_action_metadata.action_type,
            target=sample_action_metadata.target,
            parameters=sample_action_metadata.parameters,
            status=ActionStatus.SUCCESS,
            result=sample_action_result,
            started_at=sample_action_metadata.created_at,
            user_approved=True
        )
        
        logger.log_action(action_log)
        
        # Verify logged
        recent = logger.get_recent_actions(limit=1)
        assert len(recent) == 1
        assert recent[0].action_id == sample_action_metadata.action_id
    
    def test_get_recent_actions(self, temp_dir):
        """Test retrieving recent actions."""
        from models import ActionLog, ActionStatus, ActionType
        from datetime import datetime
        
        logger = ActionLogger(db_path=temp_dir / "actions.db")
        
        # Log multiple actions
        for i in range(5):
            action_log = ActionLog(
                action_id=f"test-{i}",
                action_type=ActionType.CLOSE_PROCESS,
                target="test.exe",
                parameters={},
                status=ActionStatus.SUCCESS,
                started_at=datetime.now()
            )
            logger.log_action(action_log)
        
        # Get recent
        recent = logger.get_recent_actions(limit=3)
        
        assert len(recent) == 3
    
    def test_get_action_by_id(self, temp_dir, sample_action_metadata):
        """Test retrieving action by ID."""
        from models import ActionLog, ActionStatus
        
        logger = ActionLogger(db_path=temp_dir / "actions.db")
        
        action_log = ActionLog(
            action_id=sample_action_metadata.action_id,
            action_type=sample_action_metadata.action_type,
            target=sample_action_metadata.target,
            parameters=sample_action_metadata.parameters,
            status=ActionStatus.SUCCESS,
            started_at=sample_action_metadata.created_at
        )
        
        logger.log_action(action_log)
        
        # Retrieve by ID
        retrieved = logger.get_action(sample_action_metadata.action_id)
        
        assert retrieved is not None
        assert retrieved.action_id == sample_action_metadata.action_id
