"""
Disk I/O metrics collector
Collects disk read/write speeds and queue length
"""
import psutil
import time
from collectors.base import BaseCollector
from models import DiskMetrics


class DiskCollector(BaseCollector):
    """Collects disk I/O metrics"""
    
    def __init__(self):
        super().__init__("Disk")
        self._last_io = None
        self._last_time = None
    
    async def collect(self) -> DiskMetrics:
        """Collect disk I/O metrics"""
        current_io = psutil.disk_io_counters()
        current_time = time.time()
        
        if self._last_io is None or self._last_time is None:
            # First collection, initialize
            self._last_io = current_io
            self._last_time = current_time
            # Return zeros for first collection
            return DiskMetrics(
                read_mbps=0.0,
                write_mbps=0.0,
                queue_length=0,
                usage_percent=None
            )
        
        # Calculate time delta
        time_delta = current_time - self._last_time
        
        if time_delta == 0:
            time_delta = 0.001  # Avoid division by zero
        
        # Calculate read/write speeds in MB/s
        read_bytes = current_io.read_bytes - self._last_io.read_bytes
        write_bytes = current_io.write_bytes - self._last_io.write_bytes
        
        read_mbps = (read_bytes / time_delta) / (1024 * 1024)
        write_mbps = (write_bytes / time_delta) / (1024 * 1024)
        
        # Update last values
        self._last_io = current_io
        self._last_time = current_time
        
        # Get disk usage for system drive
        usage_percent = None
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = disk_usage.percent
        except Exception:
            pass
        
        return DiskMetrics(
            read_mbps=round(read_mbps, 2),
            write_mbps=round(write_mbps, 2),
            queue_length=0,  # psutil doesn't provide queue length directly
            usage_percent=usage_percent
        )
