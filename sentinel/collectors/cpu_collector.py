"""
CPU metrics collector
Collects CPU usage, frequency, temperature, and load
"""
import psutil
from typing import Optional
from collectors.base import BaseCollector
from models import CPUMetrics


class CPUCollector(BaseCollector):
    """Collects CPU metrics"""
    
    def __init__(self):
        super().__init__("CPU")
        self._last_cpu_percent = None
    
    async def collect(self) -> CPUMetrics:
        """Collect CPU metrics"""
        # Get overall CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get per-core usage
        per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Get CPU frequency
        freq = psutil.cpu_freq()
        current_freq = freq.current if freq else 0.0
        
        # Get load average (Unix-like systems only)
        load_avg = None
        try:
            load_avg = list(psutil.getloadavg())
        except (AttributeError, OSError):
            pass
        
        # Temperature (requires additional setup on Windows)
        temperature = self._get_temperature()
        
        return CPUMetrics(
            usage_percent=cpu_percent,
            per_core_usage=per_core,
            frequency_mhz=current_freq,
            temperature_celsius=temperature,
            load_average=load_avg
        )
    
    def _get_temperature(self) -> Optional[float]:
        """
        Get CPU temperature
        Note: Requires additional setup on Windows (e.g., OpenHardwareMonitor)
        """
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to find CPU temperature
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        if entries:
                            return entries[0].current
        except (AttributeError, OSError):
            pass
        return None
