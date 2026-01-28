"""
Spike detection
Detects sudden changes in metrics
"""
from typing import Dict, Optional, List
from collections import deque


class SpikeDetector:
    """Detect sudden spikes or drops in metrics"""
    
    def __init__(self, window_size: int = 10, spike_threshold: float = 2.0):
        self.window_size = window_size
        self.spike_threshold = spike_threshold
        self.history: Dict[str, deque] = {}
    
    def add_value(self, metric_name: str, value: float):
        """Add a value to the history"""
        if metric_name not in self.history:
            self.history[metric_name] = deque(maxlen=self.window_size)
        
        self.history[metric_name].append(value)
    
    def detect_spike(self, metric_name: str, current_value: float) -> Optional[Dict]:
        """
        Detect if current value is a spike
        Returns spike info or None
        """
        if metric_name not in self.history:
            return None
        
        history = list(self.history[metric_name])
        
        if len(history) < 3:  # Need some history
            return None
        
        # Calculate average of recent history (excluding current)
        avg = sum(history) / len(history)
        
        # Calculate change ratio
        if avg == 0:
            return None
        
        change_ratio = abs(current_value - avg) / avg
        
        # Check if it's a spike
        if change_ratio > self.spike_threshold:
            return {
                'metric': metric_name,
                'current_value': current_value,
                'average': avg,
                'change_ratio': change_ratio,
                'spike_type': 'increase' if current_value > avg else 'decrease'
            }
        
        return None
    
    def get_trend(self, metric_name: str) -> Optional[str]:
        """
        Get trend direction (increasing, decreasing, stable)
        """
        if metric_name not in self.history:
            return None
        
        history = list(self.history[metric_name])
        
        if len(history) < 3:
            return None
        
        # Simple trend: compare first half to second half
        mid = len(history) // 2
        first_half_avg = sum(history[:mid]) / mid
        second_half_avg = sum(history[mid:]) / (len(history) - mid)
        
        if second_half_avg > first_half_avg * 1.1:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
