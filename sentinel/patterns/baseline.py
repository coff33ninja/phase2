"""
Baseline calculation for metrics
Calculates normal operating ranges
"""
from typing import List, Dict
from statistics import mean, stdev


class BaselineCalculator:
    """Calculate baseline metrics from historical data"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data: Dict[str, List[float]] = {}
    
    def add_value(self, metric_name: str, value: float):
        """Add a value to the baseline calculation"""
        if metric_name not in self.data:
            self.data[metric_name] = []
        
        self.data[metric_name].append(value)
        
        # Keep only the last window_size values
        if len(self.data[metric_name]) > self.window_size:
            self.data[metric_name] = self.data[metric_name][-self.window_size:]
    
    def get_baseline(self, metric_name: str) -> Dict[str, float]:
        """
        Get baseline statistics for a metric
        Returns mean, std, min, max
        """
        if metric_name not in self.data or len(self.data[metric_name]) < 2:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'count': 0
            }
        
        values = self.data[metric_name]
        
        return {
            'mean': mean(values),
            'std': stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }
    
    def is_anomaly(self, metric_name: str, value: float, std_threshold: float = 3.0) -> bool:
        """
        Check if a value is an anomaly (beyond std_threshold standard deviations)
        """
        baseline = self.get_baseline(metric_name)
        
        if baseline['count'] < 10:  # Need enough data
            return False
        
        if baseline['std'] == 0:  # No variation
            return False
        
        deviation = abs(value - baseline['mean']) / baseline['std']
        return deviation > std_threshold
