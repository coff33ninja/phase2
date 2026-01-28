"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock Gemini API key."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_12345")


@pytest.fixture
def sample_context():
    """Sample system context."""
    return {
        "system_state": {
            "cpu": 45.2,
            "ram": 16.5,
            "gpu": 12.0,
            "disk": {"read_mb": 125.0, "write_mb": 45.0},
            "network": {"sent_mb": 15.2, "recv_mb": 8.1}
        },
        "patterns": {
            "typical_usage": "moderate",
            "work_hours": "9:00-17:00",
            "common_apps": ["chrome", "vscode", "discord"]
        },
        "anomalies": [
            {
                "type": "high_cpu",
                "description": "CPU usage 3x normal",
                "severity": "medium"
            }
        ],
        "predictions": {
            "next_hour": "60-70% CPU",
            "confidence": 0.85
        }
    }
