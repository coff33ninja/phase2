"""Pytest configuration and fixtures for Guardian tests."""
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from config import GuardianConfig
from models import ActionType, RiskLevel


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config = GuardianConfig(
        automation_level="manual",
        enable_rollback=True,
        snapshot_before_action=True,
        log_file=temp_dir / "test.log",
        action_log_db=temp_dir / "actions.db",
        sentinel_db_path=temp_dir / "sentinel.db",
        oracle_db_path=temp_dir / "oracle.db",
        sage_db_path=temp_dir / "sage.db"
    )
    return config


@pytest.fixture
def sample_action_metadata():
    """Create sample action metadata."""
    from models import ActionMetadata
    
    return ActionMetadata(
        action_id="test-action-123",
        action_type=ActionType.CLOSE_PROCESS,
        target="notepad.exe",
        parameters={"force": False},
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        can_rollback=True,
        estimated_impact="Minimal"
    )


@pytest.fixture
def sample_action_result():
    """Create sample action result."""
    from models import ActionResult
    
    return ActionResult(
        success=True,
        message="Process closed successfully",
        data={"pid": 1234, "process": "notepad.exe"},
        execution_time_ms=125.5
    )


@pytest.fixture
def sample_profile():
    """Create sample profile."""
    from models import Profile
    
    return Profile(
        name="test_profile",
        description="Test profile for unit tests",
        actions=[
            {"type": "close_process", "target": "notepad.exe"},
            {"type": "set_priority", "target": "test.exe", "priority": "high"}
        ],
        enabled=True
    )


@pytest.fixture
def mock_process_list():
    """Create mock process list."""
    return [
        {"pid": 1234, "name": "notepad.exe", "cpu_percent": 0.5, "memory_mb": 10},
        {"pid": 5678, "name": "chrome.exe", "cpu_percent": 15.2, "memory_mb": 500},
        {"pid": 9012, "name": "explorer.exe", "cpu_percent": 2.1, "memory_mb": 50}
    ]


@pytest.fixture
def mock_system_metrics():
    """Create mock system metrics."""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": 45.5,
        "ram_usage": 60.2,
        "gpu_usage": 30.0,
        "disk_usage": 75.0,
        "network_usage": 10.5
    }
