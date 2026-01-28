"""
Data validation utilities
Validate collected metrics before storage
"""
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Raised when data validation fails"""
    pass


class DataValidator:
    """Validate collected metrics data"""
    
    @staticmethod
    def validate_percentage(value: float, field_name: str = "value") -> None:
        """Validate percentage is between 0 and 100"""
        if not 0 <= value <= 100:
            raise ValidationError(f"{field_name} must be between 0 and 100, got {value}")
    
    @staticmethod
    def validate_positive(value: float, field_name: str = "value") -> None:
        """Validate value is positive"""
        if value < 0:
            raise ValidationError(f"{field_name} must be positive, got {value}")
    
    @staticmethod
    def validate_cpu_metrics(data: Dict[str, Any]) -> List[str]:
        """
        Validate CPU metrics
        Returns list of validation errors (empty if valid)
        """
        errors = []
        
        try:
            if 'usage_percent' in data:
                DataValidator.validate_percentage(data['usage_percent'], 'CPU usage')
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            if 'frequency_mhz' in data:
                DataValidator.validate_positive(data['frequency_mhz'], 'CPU frequency')
        except ValidationError as e:
            errors.append(str(e))
        
        if 'per_core_usage' in data:
            for idx, usage in enumerate(data['per_core_usage']):
                try:
                    DataValidator.validate_percentage(usage, f"Core {idx} usage")
                except ValidationError as e:
                    errors.append(str(e))
        
        return errors
    
    @staticmethod
    def validate_ram_metrics(data: Dict[str, Any]) -> List[str]:
        """Validate RAM metrics"""
        errors = []
        
        try:
            if 'usage_percent' in data:
                DataValidator.validate_percentage(data['usage_percent'], 'RAM usage')
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            if 'total_gb' in data:
                DataValidator.validate_positive(data['total_gb'], 'Total RAM')
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            if 'used_gb' in data and 'total_gb' in data:
                if data['used_gb'] > data['total_gb']:
                    errors.append(f"Used RAM ({data['used_gb']} GB) cannot exceed total RAM ({data['total_gb']} GB)")
        except Exception as e:
            errors.append(str(e))
        
        return errors
    
    @staticmethod
    def validate_disk_metrics(data: Dict[str, Any]) -> List[str]:
        """Validate disk metrics"""
        errors = []
        
        try:
            if 'read_mbps' in data:
                DataValidator.validate_positive(data['read_mbps'], 'Disk read speed')
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            if 'write_mbps' in data:
                DataValidator.validate_positive(data['write_mbps'], 'Disk write speed')
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @staticmethod
    def validate_network_metrics(data: Dict[str, Any]) -> List[str]:
        """Validate network metrics"""
        errors = []
        
        try:
            if 'download_mbps' in data:
                DataValidator.validate_positive(data['download_mbps'], 'Download speed')
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            if 'upload_mbps' in data:
                DataValidator.validate_positive(data['upload_mbps'], 'Upload speed')
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @staticmethod
    def is_valid_snapshot(snapshot: Any) -> bool:
        """
        Check if a snapshot is valid
        Returns True if valid, False otherwise
        """
        if not hasattr(snapshot, 'cpu') or snapshot.cpu is None:
            return False
        
        if not hasattr(snapshot, 'ram') or snapshot.ram is None:
            return False
        
        if not hasattr(snapshot, 'disk') or snapshot.disk is None:
            return False
        
        if not hasattr(snapshot, 'network') or snapshot.network is None:
            return False
        
        if not hasattr(snapshot, 'context') or snapshot.context is None:
            return False
        
        return True
