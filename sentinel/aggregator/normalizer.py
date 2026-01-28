"""
Data normalization utilities
Normalize and clean collected data
"""
from typing import Any, Dict, Optional
from datetime import datetime


class DataNormalizer:
    """Normalize collected metrics data"""
    
    @staticmethod
    def normalize_percentage(value: float) -> float:
        """Ensure percentage is between 0 and 100"""
        return max(0.0, min(100.0, value))
    
    @staticmethod
    def normalize_bytes_to_gb(bytes_value: float) -> float:
        """Convert bytes to GB"""
        return round(bytes_value / (1024 ** 3), 2)
    
    @staticmethod
    def normalize_bytes_to_mb(bytes_value: float) -> float:
        """Convert bytes to MB"""
        return round(bytes_value / (1024 ** 2), 2)
    
    @staticmethod
    def normalize_timestamp(timestamp: Any) -> datetime:
        """Ensure timestamp is datetime object"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp)
        else:
            return datetime.utcnow()
    
    @staticmethod
    def clean_metric_name(name: str) -> str:
        """Clean and standardize metric names"""
        return name.lower().replace(' ', '_').replace('-', '_')
    
    @staticmethod
    def normalize_cpu_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CPU metrics"""
        normalized = data.copy()
        
        if 'usage_percent' in normalized:
            normalized['usage_percent'] = DataNormalizer.normalize_percentage(
                normalized['usage_percent']
            )
        
        if 'per_core_usage' in normalized:
            normalized['per_core_usage'] = [
                DataNormalizer.normalize_percentage(usage)
                for usage in normalized['per_core_usage']
            ]
        
        return normalized
    
    @staticmethod
    def normalize_ram_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RAM metrics"""
        normalized = data.copy()
        
        if 'usage_percent' in normalized:
            normalized['usage_percent'] = DataNormalizer.normalize_percentage(
                normalized['usage_percent']
            )
        
        return normalized
    
    @staticmethod
    def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from dictionary"""
        return {k: v for k, v in data.items() if v is not None}
    
    @staticmethod
    def ensure_numeric(value: Any, default: float = 0.0) -> float:
        """Ensure value is numeric"""
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
