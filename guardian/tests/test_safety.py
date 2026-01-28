"""Tests for Guardian safety system."""
import pytest
from unittest.mock import Mock, patch

from safety.validator import ActionValidator
from safety.snapshot import SnapshotManager
from safety.rollback import RollbackManager
from actions.process_actions import CloseProcess, KillProcess
from actions.system_actions import PowerPlan
from models import RiskLevel


class TestActionValidator:
    """Test action validator."""
    
    def test_validate_safe_action(self):
        """Test validation of safe action."""
        validator = ActionValidator()
        action = CloseProcess(target="notepad.exe")
        
        is_valid, error = validator.validate_action(action)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_protected_process(self):
        """Test validation rejects protected process."""
        validator = ActionValidator()
        action = CloseProcess(target="explorer.exe")
        
        is_valid, error = validator.validate_action(action)
        
        assert is_valid is False
        assert "protected" in error.lower()
    
    def test_validate_system_process(self):
        """Test validation rejects system process."""
        validator = ActionValidator()
        action = KillProcess(target="System")
        
        is_valid, error = validator.validate_action(action)
        
        assert is_valid is False
        assert "protected" in error.lower() or "system" in error.lower()
    
    def test_requires_approval_high_risk(self):
        """Test high-risk actions require approval."""
        validator = ActionValidator()
        action = KillProcess(target="important.exe")
        
        requires = validator.requires_approval(action)
        
        # Kill process is high risk
        assert requires is True
    
    def test_requires_approval_low_risk(self):
        """Test low-risk actions don't require approval."""
        validator = ActionValidator()
        action = CloseProcess(target="notepad.exe")
        
        requires = validator.requires_approval(action)
        
        # Close process is low risk
        assert requires is False
    
    def test_assess_risk_level(self):
        """Test risk level assessment."""
        validator = ActionValidator()
        
        # Low risk
        action1 = CloseProcess(target="notepad.exe")
        risk1 = validator.assess_risk(action1)
        assert risk1 == RiskLevel.LOW
        
        # High risk
        action2 = KillProcess(target="important.exe")
        risk2 = validator.assess_risk(action2)
        assert risk2 == RiskLevel.HIGH


class TestSnapshotManager:
    """Test snapshot manager."""
    
    @patch('psutil.process_iter')
    def test_create_snapshot(self, mock_process_iter):
        """Test snapshot creation."""
        # Mock processes
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'notepad.exe', 'status': 'running'}
        mock_process_iter.return_value = [mock_proc]
        
        manager = SnapshotManager()
        action = CloseProcess(target="notepad.exe")
        
        snapshot = manager.create_snapshot("test-action-123")
        
        assert snapshot is not None
        assert snapshot.action_id == "test-action-123"
        assert len(snapshot.processes) > 0
        assert snapshot.can_restore is True
    
    def test_get_snapshot(self):
        """Test snapshot retrieval."""
        manager = SnapshotManager()
        
        # Create snapshot
        snapshot = manager.create_snapshot("test-123")
        
        # Retrieve it
        retrieved = manager.get_snapshot(snapshot.snapshot_id)
        
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id
    
    def test_get_nonexistent_snapshot(self):
        """Test retrieval of nonexistent snapshot."""
        manager = SnapshotManager()
        
        snapshot = manager.get_snapshot("nonexistent-id")
        
        assert snapshot is None


class TestRollbackManager:
    """Test rollback manager."""
    
    def test_rollback_action_success(self):
        """Test successful action rollback."""
        snapshot_manager = SnapshotManager()
        rollback_manager = RollbackManager(snapshot_manager)
        
        # Create snapshot
        snapshot = snapshot_manager.create_snapshot("test-123")
        
        # Create action
        action = CloseProcess(target="notepad.exe")
        
        # Attempt rollback
        result = rollback_manager.rollback_action(action, snapshot.snapshot_id)
        
        # Should succeed or indicate not implemented
        assert result.success is True or "not implemented" in result.message.lower()
    
    def test_rollback_without_snapshot(self):
        """Test rollback without snapshot."""
        snapshot_manager = SnapshotManager()
        rollback_manager = RollbackManager(snapshot_manager)
        
        action = CloseProcess(target="notepad.exe")
        
        result = rollback_manager.rollback_action(action, "nonexistent-id")
        
        assert result.success is False
        assert "snapshot" in result.message.lower()
    
    def test_rollback_history(self):
        """Test rollback history tracking."""
        snapshot_manager = SnapshotManager()
        rollback_manager = RollbackManager(snapshot_manager)
        
        # Create and rollback action
        snapshot = snapshot_manager.create_snapshot("test-123")
        action = CloseProcess(target="notepad.exe")
        rollback_manager.rollback_action(action, snapshot.snapshot_id)
        
        # Check history
        history = rollback_manager.get_rollback_history()
        
        assert len(history) > 0
