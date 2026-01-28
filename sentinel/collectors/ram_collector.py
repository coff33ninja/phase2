"""
RAM metrics collector
Collects memory usage, available memory, and swap information
"""
import psutil
from collectors.base import BaseCollector
from models import RAMMetrics


class RAMCollector(BaseCollector):
    """Collects RAM metrics"""
    
    def __init__(self):
        super().__init__("RAM")
    
    async def collect(self) -> RAMMetrics:
        """Collect RAM metrics"""
        # Get virtual memory stats
        mem = psutil.virtual_memory()
        
        # Convert bytes to GB
        total_gb = mem.total / (1024 ** 3)
        used_gb = mem.used / (1024 ** 3)
        available_gb = mem.available / (1024 ** 3)
        
        # Get cached memory if available
        cached_gb = None
        if hasattr(mem, 'cached'):
            cached_gb = mem.cached / (1024 ** 3)
        
        return RAMMetrics(
            total_gb=round(total_gb, 2),
            used_gb=round(used_gb, 2),
            available_gb=round(available_gb, 2),
            cached_gb=round(cached_gb, 2) if cached_gb else None,
            usage_percent=mem.percent
        )
