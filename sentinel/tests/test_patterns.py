"""
Unit tests for pattern detection
"""
import pytest
from patterns import BaselineCalculator, ThresholdDetector, SpikeDetector
from patterns.threshold import Severity


def test_threshold_detector():
    """Test threshold detection"""
    detector = ThresholdDetector()
    
    # Test CPU usage thresholds
    assert detector.check('cpu_usage', 50.0) is None  # Normal
    assert detector.check('cpu_usage', 75.0) == Severity.MEDIUM
    assert detector.check('cpu_usage', 90.0) == Severity.HIGH
    assert detector.check('cpu_usage', 98.0) == Severity.CRITICAL
    
    # Test custom threshold
    detector.set_threshold('custom_metric', 'high', 80.0)
    assert detector.check('custom_metric', 85.0) == Severity.HIGH


def test_threshold_detector_multiple():
    """Test checking multiple metrics"""
    detector = ThresholdDetector()
    
    metrics = {
        'cpu_usage': 90.0,  # HIGH
        'ram_usage': 60.0,  # None
        'disk_usage': 96.0  # CRITICAL
    }
    
    alerts = detector.get_all_alerts(metrics)
    
    assert 'cpu_usage' in alerts
    assert alerts['cpu_usage'] == Severity.HIGH
    assert 'ram_usage' not in alerts
    assert 'disk_usage' in alerts
    assert alerts['disk_usage'] == Severity.CRITICAL


def test_baseline_calculator():
    """Test baseline calculation"""
    calc = BaselineCalculator(window_size=10)
    
    # Add some values
    for i in range(10):
        calc.add_value('cpu', 50.0 + i)
    
    baseline = calc.get_baseline('cpu')
    
    assert baseline['count'] == 10
    assert 50.0 <= baseline['mean'] <= 60.0
    assert baseline['std'] > 0
    assert baseline['min'] == 50.0
    assert baseline['max'] == 59.0


def test_baseline_anomaly_detection():
    """Test anomaly detection"""
    calc = BaselineCalculator()
    
    # Add normal values with some variation
    for i in range(20):
        calc.add_value('cpu', 50.0 + (i % 5))  # Values: 50, 51, 52, 53, 54, repeating
    
    # Normal value should not be anomaly
    assert not calc.is_anomaly('cpu', 52.0)
    
    # Very different value should be anomaly
    assert calc.is_anomaly('cpu', 150.0, std_threshold=3.0)


def test_spike_detector():
    """Test spike detection"""
    detector = SpikeDetector(window_size=5, spike_threshold=1.5)
    
    # Add normal values
    for i in range(5):
        detector.add_value('cpu', 50.0)
    
    # Detect spike
    spike = detector.detect_spike('cpu', 150.0)
    
    assert spike is not None
    assert spike['spike_type'] == 'increase'
    assert spike['current_value'] == 150.0
    
    # No spike for normal value
    spike = detector.detect_spike('cpu', 52.0)
    assert spike is None


def test_spike_detector_trend():
    """Test trend detection"""
    detector = SpikeDetector(window_size=10)
    
    # Add increasing values
    for i in range(10):
        detector.add_value('cpu', 50.0 + i * 5)
    
    trend = detector.get_trend('cpu')
    assert trend == "increasing"
    
    # Add decreasing values
    detector2 = SpikeDetector(window_size=10)
    for i in range(10):
        detector2.add_value('ram', 100.0 - i * 5)
    
    trend = detector2.get_trend('ram')
    assert trend == "decreasing"
