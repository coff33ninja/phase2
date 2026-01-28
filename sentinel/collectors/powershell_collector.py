"""
PowerShell integration collector
Executes PowerShell commands to collect system data
"""
import subprocess
import json
from typing import Dict, Any, Optional
from .base import BaseCollector


class PowerShellCollector(BaseCollector):
    """Collects data via PowerShell commands"""
    
    def __init__(self):
        super().__init__("PowerShell")
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Collect data from PowerShell"""
        data = {}
        
        # Collect system info
        system_info = await self._get_system_info()
        if system_info:
            data['system_info'] = system_info
        
        # Collect BIOS info
        bios_info = await self._get_bios_info()
        if bios_info:
            data['bios'] = bios_info
        
        # Collect motherboard info
        mb_info = await self._get_motherboard_info()
        if mb_info:
            data['motherboard'] = mb_info
        
        # Collect Windows updates
        updates = await self._get_windows_updates()
        if updates:
            data['windows_updates'] = updates
        
        return data if data else None
    
    async def _execute_powershell(self, command: str) -> Optional[str]:
        """Execute PowerShell command and return output"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    async def _get_system_info(self) -> Optional[Dict[str, str]]:
        """Get system information"""
        command = """
        Get-ComputerInfo | Select-Object CsName, CsManufacturer, CsModel, 
        OsName, OsVersion, OsArchitecture | ConvertTo-Json
        """
        
        output = await self._execute_powershell(command)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass
        return None
    
    async def _get_bios_info(self) -> Optional[Dict[str, str]]:
        """Get BIOS information"""
        command = """
        Get-WmiObject Win32_BIOS | Select-Object Manufacturer, Version, 
        ReleaseDate | ConvertTo-Json
        """
        
        output = await self._execute_powershell(command)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass
        return None
    
    async def _get_motherboard_info(self) -> Optional[Dict[str, str]]:
        """Get motherboard information"""
        command = """
        Get-WmiObject Win32_BaseBoard | Select-Object Manufacturer, Product, 
        Version | ConvertTo-Json
        """
        
        output = await self._execute_powershell(command)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass
        return None
    
    async def _get_windows_updates(self) -> Optional[Dict[str, Any]]:
        """Get Windows update information"""
        command = """
        $Session = New-Object -ComObject Microsoft.Update.Session
        $Searcher = $Session.CreateUpdateSearcher()
        $HistoryCount = $Searcher.GetTotalHistoryCount()
        $Updates = $Searcher.QueryHistory(0, [Math]::Min($HistoryCount, 10))
        $Updates | Select-Object Title, Date, @{Name='Result';Expression={
            switch($_.ResultCode) {
                0 {'NotStarted'}
                1 {'InProgress'}
                2 {'Succeeded'}
                3 {'SucceededWithErrors'}
                4 {'Failed'}
                5 {'Aborted'}
            }
        }} | ConvertTo-Json
        """
        
        output = await self._execute_powershell(command)
        if output:
            try:
                updates = json.loads(output)
                return {
                    'recent_updates': updates if isinstance(updates, list) else [updates],
                    'count': len(updates) if isinstance(updates, list) else 1
                }
            except json.JSONDecodeError:
                pass
        return None
