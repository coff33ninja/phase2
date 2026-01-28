"""Tests for pattern storage."""
import pytest
from pathlib import Path

from patterns.behavior_profiles import BehaviorProfileManager
from patterns.usage_patterns import UsagePatternStore
from patterns.correlation_matrix import CorrelationTracker
from patterns.baseline_manager import BaselineManager


class TestBehaviorProfileManager:
    """Test behavior profile management."""
    
    def test_create_profile(self, temp_dir):
        """Test creating a profile."""
        db_path = temp_dir / "patterns.db"
        manager = BehaviorProfileManager(db_path)
        
        profile_data = {
            "work_hours": {"start": "09:00", "end": "17:00"},
            "apps": ["vscode", "chrome"]
        }
        
        profile_id = manager.create_profile("developer", profile_data)
        assert profile_id > 0
    
    def test_get_profile(self, temp_dir):
        """Test retrieving a profile."""
        db_path = temp_dir / "patterns.db"
        manager = BehaviorProfileManager(db_path)
        
        profile_data = {"test": "data"}
        manager.create_profile("test_profile", profile_data)
        
        retrieved = manager.get_profile("test_profile")
        assert retrieved is not None
        assert retrieved["data"]["test"] == "data"
    
    def test_update_profile(self, temp_dir):
        """Test updating a profile."""
        db_path = temp_dir / "patterns.db"
        manager = BehaviorProfileManager(db_path)
        
        manager.create_profile("test", {"value": 1})
        manager.update_profile("test", {"value": 2})
        
        profile = manager.get_profile("test")
        assert profile["data"]["value"] == 2


class TestUsagePatternStore:
    """Test usage pattern storage."""
    
    def test_store_pattern(self, temp_dir):
        """Test storing a pattern."""
        db_path = temp_dir / "patterns.db"
        store = UsagePatternStore(db_path)
        
        pattern_data = {"cpu_mean": 45.0, "ram_mean": 60.0}
        pattern_id = store.store_pattern(
            "cpu_usage",
            "weekday_morning",
            pattern_data,
            confidence=0.85
        )
        
        assert pattern_id > 0
    
    def test_get_pattern(self, temp_dir):
        """Test retrieving a pattern."""
        db_path = temp_dir / "patterns.db"
        store = UsagePatternStore(db_path)
        
        pattern_data = {"cpu_mean": 45.0}
        store.store_pattern("cpu_usage", "morning", pattern_data, 0.8)
        
        retrieved = store.get_pattern("cpu_usage", "morning")
        assert retrieved is not None
        assert retrieved["confidence"] == 0.8
    
    def test_get_patterns_by_type(self, temp_dir):
        """Test getting patterns by type."""
        db_path = temp_dir / "patterns.db"
        store = UsagePatternStore(db_path)
        
        store.store_pattern("cpu_usage", "morning", {"val": 1}, 0.8)
        store.store_pattern("cpu_usage", "evening", {"val": 2}, 0.9)
        
        patterns = store.get_patterns_by_type("cpu_usage")
        assert len(patterns) == 2


class TestCorrelationTracker:
    """Test correlation tracking."""
    
    def test_update_process_correlation(self, temp_dir):
        """Test updating process correlation."""
        db_path = temp_dir / "patterns.db"
        tracker = CorrelationTracker(db_path)
        
        tracker.update_process_correlation("chrome", "vscode", 0.75)
        
        correlations = tracker.get_process_correlations("chrome", min_score=0.5)
        assert len(correlations) > 0
    
    def test_update_metric_correlation(self, temp_dir):
        """Test updating metric correlation."""
        db_path = temp_dir / "patterns.db"
        tracker = CorrelationTracker(db_path)
        
        tracker.update_metric_correlation("cpu_percent", "ram_percent", 0.65)
        
        correlations = tracker.get_metric_correlations("cpu_percent", min_score=0.5)
        assert len(correlations) > 0


class TestBaselineManager:
    """Test baseline management."""
    
    def test_update_baseline(self, temp_dir):
        """Test updating a baseline."""
        db_path = temp_dir / "patterns.db"
        manager = BaselineManager(db_path)
        
        values = [45.0, 50.0, 48.0, 52.0, 47.0]
        manager.update_baseline("cpu_percent", "weekday_morning", values)
        
        baseline = manager.get_baseline("cpu_percent", "weekday_morning")
        assert baseline is not None
        assert 45.0 <= baseline["baseline"] <= 52.0
    
    def test_is_anomaly(self, temp_dir):
        """Test anomaly detection."""
        db_path = temp_dir / "patterns.db"
        manager = BaselineManager(db_path)
        
        # Use 1000+ values to get confidence >= 0.5 (confidence = sample_count / 1000)
        # Add variation to get non-zero std deviation
        values = [50.0 + (i % 20) for i in range(1000)]  # Values between 50-69
        manager.update_baseline("cpu_percent", "morning", values)
        
        # Normal value (within range)
        assert not manager.is_anomaly("cpu_percent", "morning", 60.0)
        
        # Anomalous value (far outside range)
        assert manager.is_anomaly("cpu_percent", "morning", 200.0)
    
    def test_get_expected_range(self, temp_dir):
        """Test getting expected range."""
        db_path = temp_dir / "patterns.db"
        manager = BaselineManager(db_path)
        
        values = [50.0] * 100
        manager.update_baseline("cpu_percent", "morning", values)
        
        range_val = manager.get_expected_range("cpu_percent", "morning")
        assert range_val is not None
        assert len(range_val) == 2
    
    def test_get_time_context(self, temp_dir):
        """Test time context generation."""
        db_path = temp_dir / "patterns.db"
        manager = BaselineManager(db_path)
        
        context = manager.get_time_context()
        assert "_" in context
        assert any(day in context for day in ["weekday", "weekend"])
