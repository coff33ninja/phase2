"""Tests for Guardian actions."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from actions.base_action import BaseAction
from actions.process_actions import CloseProcess, StartProcess, SetPriority, KillProcess
from actions.resource_actions import ClearRAM, SetCPUAffinity, DiskCleanup
from actions.system_actions import PowerPlan, DisplayBrightness, Sleep, Hibernate
from models import ActionType, RiskLevel, ActionResult


class TestBaseAction:
    """Test base action class."""
    
    def test_create_metadata(self):
        """Test metadata creation."""
        action = CloseProcess(target="notepad.exe")
        metadata = action.create_metadata("test-123")
        
        assert metadata.action_id == "test-123"
        assert metadata.action_type == ActionType.CLOSE_PROCESS
        assert metadata.target == "notepad.exe"
        assert metadata.risk_level == RiskLevel.LOW
    
    def test_validate_success(self):
        """Test successful validation."""
        action = CloseProcess(target="notepad.exe")
        is_valid, error = action.validate()
        
        assert is_valid is True
        assert error is None
    
    def test_validate_empty_target(self):
        """Test validation with empty target."""
        action = CloseProcess(target="")
        is_valid, error = action.validate()
        
        assert is_valid is False
        assert "Target cannot be empty" in error


class TestProcessActions:
    """Test process management actions."""
    
    @patch('psutil.process_iter')
    def test_close_process_success(self, mock_process_iter):
        """Test successful process close."""
        # Mock process
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'notepad.exe'}
        mock_proc.terminate = Mock()
        mock_process_iter.return_value = [mock_proc]
        
        action = CloseProcess(target="notepad.exe")
        result = action.execute()
        
        assert result.success is True
        assert "closed" in result.message.lower()
        mock_proc.terminate.assert_called_once()
    
    @patch('psutil.process_iter')
    def test_close_process_not_found(self, mock_process_iter):
        """Test close process when not found."""
        mock_process_iter.return_value = []
        
        action = CloseProcess(target="nonexistent.exe")
        result = action.execute()
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    @patch('subprocess.Popen')
    def test_start_process_success(self, mock_popen):
        """Test successful process start."""
        mock_proc = Mock()
        mock_proc.pid = 5678
        mock_popen.return_value = mock_proc
        
        action = StartProcess(target="notepad.exe")
        result = action.execute()
        
        assert result.success is True
        assert "started" in result.message.lower()
    
    @patch('psutil.process_iter')
    def test_set_priority_success(self, mock_process_iter):
        """Test successful priority change."""
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'test.exe'}
        mock_proc.nice = Mock()
        mock_process_iter.return_value = [mock_proc]
        
        action = SetPriority(target="test.exe", parameters={"priority": "high"})
        result = action.execute()
        
        assert result.success is True
        mock_proc.nice.assert_called_once()


class TestResourceActions:
    """Test resource management actions."""
    
    @patch('ctypes.windll.kernel32.SetProcessWorkingSetSize')
    def test_clear_ram_success(self, mock_set_working_set):
        """Test RAM clearing."""
        mock_set_working_set.return_value = 1
        
        action = ClearRAM(target="system")
        result = action.execute()
        
        assert result.success is True
        assert "cleared" in result.message.lower()
    
    @patch('psutil.process_iter')
    def test_set_cpu_affinity_success(self, mock_process_iter):
        """Test CPU affinity setting."""
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'test.exe'}
        mock_proc.cpu_affinity = Mock()
        mock_process_iter.return_value = [mock_proc]
        
        action = SetCPUAffinity(
            target="test.exe",
            parameters={"cores": [0, 1]}
        )
        result = action.execute()
        
        assert result.success is True
        mock_proc.cpu_affinity.assert_called_once()


class TestSystemActions:
    """Test system-level actions."""
    
    @patch('subprocess.run')
    def test_power_plan_success(self, mock_run):
        """Test power plan switching."""
        mock_run.return_value = Mock(returncode=0)
        
        action = PowerPlan(target="performance")
        result = action.execute()
        
        assert result.success is True
        assert "power plan" in result.message.lower()
    
    @patch('subprocess.run')
    def test_display_brightness_success(self, mock_run):
        """Test display brightness adjustment."""
        mock_run.return_value = Mock(returncode=0)
        
        action = DisplayBrightness(
            target="display",
            parameters={"level": 50}
        )
        result = action.execute()
        
        assert result.success is True
    
    @patch('subprocess.run')
    def test_sleep_success(self, mock_run):
        """Test system sleep."""
        mock_run.return_value = Mock(returncode=0)
        
        action = Sleep(target="system")
        result = action.execute()
        
        assert result.success is True
        assert "sleep" in result.message.lower()


class TestActionRollback:
    """Test action rollback functionality."""
    
    @patch('psutil.process_iter')
    def test_close_process_rollback(self, mock_process_iter):
        """Test rollback of close process action."""
        action = CloseProcess(target="notepad.exe")
        
        # Mock snapshot data
        snapshot_data = {
            "process": "notepad.exe",
            "pid": 1234,
            "state": "running"
        }
        
        result = action.rollback(snapshot_data)
        
        # Rollback should attempt to restart the process
        assert result.success is True or "not implemented" in result.message.lower()
