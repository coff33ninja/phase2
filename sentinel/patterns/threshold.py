"""
Threshold-based detection
Simple threshold alerts
"""
from typing import Dict, Optional
from enum import Enum


class Severity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThresholdDetector:
    """Detect when metrics exceed thresholds"""
    
    def __init__(self):
        # Default thresholds for common metrics
        self.thresholds: Dict[str, Dict[str, float]] = {
            'cpu_usage': {
                'medium': 70.0,
                'high': 85.0,
                'critical': 95.0
            },
            'ram_usage': {
                'medium': 70.0,
                'high': 85.0,
                'critical': 95.0
            },
            'disk_usage': {
                'medium': 80.0,
                'high': 90.0,
                'critical': 95.0
            },
            'gpu_usage': {
                'medium': 80.0,
                'high': 90.0,
                'critical': 98.0
            }
        }
    
    def set_threshold(self, metric_name: str, severity: str, value: float):
        """Set a custom threshold"""
        if metric_name not in self.thresholds:
            self.thresholds[metric_name] = {}
        
        self.thresholds[metric_name][severity] = value
    
    def check(self, metric_name: str, value: float) -> Optional[Severity]:
        """
        Check if value exceeds thresholds
        Returns severity level or None
        """
        if metric_name not in self.thresholds:
            return None
        
        thresholds = self.thresholds[metric_name]
        
        if 'critical' in thresholds and value >= thresholds['critical']:
            return Severity.CRITICAL
        elif 'high' in thresholds and value >= thresholds['high']:
            return Severity.HIGH
        elif 'medium' in thresholds and value >= thresholds['medium']:
            return Severity.MEDIUM
        
        return None
    
    def get_all_alerts(self, metrics: Dict[str, float]) -> Dict[str, Severity]:
        """
        Check multiple metrics at once
        Returns dict of metric_name -> severity for alerts
        """
        alerts = {}
        
        for metric_name, value in metrics.items():
            severity = self.check(metric_name, value)
            if severity:
                alerts[metric_name] = severity
        
        return alerts
