"""
Network metrics collector
Collects network bandwidth usage and connection count
"""
import psutil
import time
from collectors.base import BaseCollector
from models import NetworkMetrics


class NetworkCollector(BaseCollector):
    """Collects network metrics"""
    
    def __init__(self):
        super().__init__("Network")
        self._last_io = None
        self._last_time = None
    
    async def collect(self) -> NetworkMetrics:
        """Collect network metrics"""
        current_io = psutil.net_io_counters()
        current_time = time.time()
        
        if self._last_io is None or self._last_time is None:
            # First collection, initialize
            self._last_io = current_io
            self._last_time = current_time
            # Return zeros for first collection
            return NetworkMetrics(
                download_mbps=0.0,
                upload_mbps=0.0,
                connections_active=self._count_connections()
            )
        
        # Calculate time delta
        time_delta = current_time - self._last_time
        
        if time_delta == 0:
            time_delta = 0.001  # Avoid division by zero
        
        # Calculate download/upload speeds in MB/s
        bytes_recv = current_io.bytes_recv - self._last_io.bytes_recv
        bytes_sent = current_io.bytes_sent - self._last_io.bytes_sent
        
        download_mbps = (bytes_recv / time_delta) / (1024 * 1024)
        upload_mbps = (bytes_sent / time_delta) / (1024 * 1024)
        
        # Update last values
        self._last_io = current_io
        self._last_time = current_time
        
        return NetworkMetrics(
            download_mbps=round(download_mbps, 2),
            upload_mbps=round(upload_mbps, 2),
            connections_active=self._count_connections()
        )
    
    def _count_connections(self) -> int:
        """Count active network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            # Count established connections
            active = sum(1 for conn in connections if conn.status == 'ESTABLISHED')
            return active
        except (psutil.AccessDenied, Exception):
            return 0
