"""
Data collectors package
Each collector is responsible for gathering specific system metrics
"""
from .base import BaseCollector
from .cpu_collector import CPUCollector
from .ram_collector import RAMCollector
from .gpu_collector import GPUCollector
from .disk_collector import DiskCollector
from .network_collector import NetworkCollector
from .process_collector import ProcessCollector
from .context_collector import ContextCollector
from .temperature_collector import TemperatureCollector
from .powershell_collector import PowerShellCollector
from .wmi_collector import WMICollector
from .aida64_collector import AIDA64Collector
from .hwinfo_collector import HWiNFOCollector

__all__ = [
    "BaseCollector",
    "CPUCollector",
    "RAMCollector",
    "GPUCollector",
    "DiskCollector",
    "NetworkCollector",
    "ProcessCollector",
    "ContextCollector",
    "TemperatureCollector",
    "PowerShellCollector",
    "WMICollector",
    "AIDA64Collector",
    "HWiNFOCollector",
]
