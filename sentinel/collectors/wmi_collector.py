"""
WMI (Windows Management Instrumentation) collector
Collects detailed Windows system information
"""
from typing import Dict, Any, Optional, List
from .base import BaseCollector


class WMICollector(BaseCollector):
    """Collects data via WMI queries"""
    
    def __init__(self):
        super().__init__("WMI")
        self._wmi_available = self._check_wmi()
    
    def _check_wmi(self) -> bool:
        """Check if WMI is available"""
        try:
            import wmi
            return True
        except ImportError:
            return False
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Collect WMI data"""
        if not self._wmi_available:
            return None
        
        data = {}
        
        # Collect various WMI data
        data['processor'] = await self._get_processor_info()
        data['memory'] = await self._get_memory_info()
        data['disk'] = await self._get_disk_info()
        data['network_adapters'] = await self._get_network_adapters()
        data['video_controller'] = await self._get_video_controller()
        data['operating_system'] = await self._get_os_info()
        
        return data
    
    async def _get_processor_info(self) -> Optional[Dict[str, Any]]:
        """Get processor information"""
        try:
            import wmi
            w = wmi.WMI()
            processors = w.Win32_Processor()
            
            if processors:
                proc = processors[0]
                return {
                    'name': proc.Name,
                    'manufacturer': proc.Manufacturer,
                    'cores': proc.NumberOfCores,
                    'logical_processors': proc.NumberOfLogicalProcessors,
                    'max_clock_speed': proc.MaxClockSpeed,
                    'architecture': proc.Architecture,
                    'l2_cache_size': proc.L2CacheSize,
                    'l3_cache_size': proc.L3CacheSize
                }
        except Exception:
            pass
        return None
    
    async def _get_memory_info(self) -> Optional[List[Dict[str, Any]]]:
        """Get memory module information"""
        try:
            import wmi
            w = wmi.WMI()
            memory_modules = w.Win32_PhysicalMemory()
            
            modules = []
            for mem in memory_modules:
                modules.append({
                    'capacity_gb': int(mem.Capacity) / (1024**3) if mem.Capacity else 0,
                    'speed_mhz': mem.Speed,
                    'manufacturer': mem.Manufacturer,
                    'part_number': mem.PartNumber,
                    'serial_number': mem.SerialNumber
                })
            
            return modules if modules else None
        except Exception:
            pass
        return None
    
    async def _get_disk_info(self) -> Optional[List[Dict[str, Any]]]:
        """Get disk drive information"""
        try:
            import wmi
            w = wmi.WMI()
            disks = w.Win32_DiskDrive()
            
            disk_list = []
            for disk in disks:
                disk_list.append({
                    'model': disk.Model,
                    'size_gb': int(disk.Size) / (1024**3) if disk.Size else 0,
                    'interface_type': disk.InterfaceType,
                    'media_type': disk.MediaType,
                    'serial_number': disk.SerialNumber
                })
            
            return disk_list if disk_list else None
        except Exception:
            pass
        return None
    
    async def _get_network_adapters(self) -> Optional[List[Dict[str, Any]]]:
        """Get network adapter information"""
        try:
            import wmi
            w = wmi.WMI()
            adapters = w.Win32_NetworkAdapter(PhysicalAdapter=True)
            
            adapter_list = []
            for adapter in adapters:
                adapter_list.append({
                    'name': adapter.Name,
                    'manufacturer': adapter.Manufacturer,
                    'mac_address': adapter.MACAddress,
                    'speed_mbps': int(adapter.Speed) / 1000000 if adapter.Speed else 0,
                    'adapter_type': adapter.AdapterType
                })
            
            return adapter_list if adapter_list else None
        except Exception:
            pass
        return None
    
    async def _get_video_controller(self) -> Optional[Dict[str, Any]]:
        """Get video controller information"""
        try:
            import wmi
            w = wmi.WMI()
            controllers = w.Win32_VideoController()
            
            if controllers:
                ctrl = controllers[0]
                return {
                    'name': ctrl.Name,
                    'adapter_ram_mb': int(ctrl.AdapterRAM) / (1024**2) if ctrl.AdapterRAM else 0,
                    'driver_version': ctrl.DriverVersion,
                    'video_processor': ctrl.VideoProcessor,
                    'current_refresh_rate': ctrl.CurrentRefreshRate,
                    'max_refresh_rate': ctrl.MaxRefreshRate
                }
        except Exception:
            pass
        return None
    
    async def _get_os_info(self) -> Optional[Dict[str, Any]]:
        """Get operating system information"""
        try:
            import wmi
            w = wmi.WMI()
            os_list = w.Win32_OperatingSystem()
            
            if os_list:
                os = os_list[0]
                return {
                    'name': os.Caption,
                    'version': os.Version,
                    'build_number': os.BuildNumber,
                    'architecture': os.OSArchitecture,
                    'install_date': str(os.InstallDate),
                    'last_boot_time': str(os.LastBootUpTime),
                    'system_directory': os.SystemDirectory
                }
        except Exception:
            pass
        return None
