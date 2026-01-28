"""
Temperature sensor collector
Collects temperature data from various sensors
"""
import subprocess
from typing import Dict, Optional, List
from .base import BaseCollector


class TemperatureCollector(BaseCollector):
    """Collects temperature data from system sensors"""
    
    def __init__(self):
        super().__init__("Temperature")
        self._openhardwaremonitor_available = self._check_ohm()
    
    def _check_ohm(self) -> bool:
        """Check if OpenHardwareMonitor is available"""
        try:
            # Check if OHM WMI interface is available
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            return True
        except Exception:
            return False
    
    async def collect(self) -> Optional[Dict[str, float]]:
        """Collect temperature data"""
        temperatures = {}
        
        # Try OpenHardwareMonitor first (Windows)
        if self._openhardwaremonitor_available:
            ohm_temps = await self._collect_from_ohm()
            if ohm_temps:
                temperatures.update(ohm_temps)
        
        # Try psutil sensors (Linux/some systems)
        psutil_temps = await self._collect_from_psutil()
        if psutil_temps:
            temperatures.update(psutil_temps)
        
        # Try WMI thermal zone (Windows fallback)
        wmi_temps = await self._collect_from_wmi()
        if wmi_temps:
            temperatures.update(wmi_temps)
        
        return temperatures if temperatures else None
    
    async def _collect_from_ohm(self) -> Dict[str, float]:
        """Collect from OpenHardwareMonitor"""
        temps = {}
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            
            for sensor in sensors:
                if sensor.SensorType == 'Temperature':
                    name = f"{sensor.Parent}_{sensor.Name}".replace(' ', '_')
                    temps[name] = float(sensor.Value)
        except Exception:
            pass
        
        return temps
    
    async def _collect_from_psutil(self) -> Dict[str, float]:
        """Collect from psutil sensors"""
        temps = {}
        try:
            import psutil
            if hasattr(psutil, 'sensors_temperatures'):
                sensor_temps = psutil.sensors_temperatures()
                for name, entries in sensor_temps.items():
                    for i, entry in enumerate(entries):
                        key = f"{name}_{i}" if len(entries) > 1 else name
                        temps[key] = entry.current
        except (AttributeError, Exception):
            pass
        
        return temps
    
    async def _collect_from_wmi(self) -> Dict[str, float]:
        """Collect from WMI thermal zone (Windows)"""
        temps = {}
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            thermal_zones = w.MSAcpi_ThermalZoneTemperature()
            
            for i, zone in enumerate(thermal_zones):
                # Convert from tenths of Kelvin to Celsius
                temp_celsius = (zone.CurrentTemperature / 10.0) - 273.15
                temps[f"ThermalZone_{i}"] = round(temp_celsius, 1)
        except Exception:
            pass
        
        return temps
