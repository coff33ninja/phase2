"""
AIDA64 integration collector
Collects data from AIDA64 if available
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseCollector


class AIDA64Collector(BaseCollector):
    """Collects data from AIDA64 reports"""
    
    def __init__(self, report_path: Optional[Path] = None):
        super().__init__("AIDA64")
        self.report_path = report_path or self._find_aida64_report()
    
    def _find_aida64_report(self) -> Optional[Path]:
        """Try to find AIDA64 report file"""
        # Common AIDA64 report locations
        possible_paths = [
            Path("C:/Program Files/AIDA64/report.xml"),
            Path("C:/Program Files (x86)/AIDA64/report.xml"),
            Path.home() / "Documents" / "AIDA64" / "report.xml",
            Path("./aida64_report.xml")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Collect data from AIDA64 report"""
        if not self.report_path or not self.report_path.exists():
            return None
        
        try:
            tree = ET.parse(self.report_path)
            root = tree.getroot()
            
            data = {}
            
            # Parse different sections
            data['computer'] = self._parse_section(root, 'Computer')
            data['motherboard'] = self._parse_section(root, 'Motherboard')
            data['processor'] = self._parse_section(root, 'Processor')
            data['memory'] = self._parse_section(root, 'Memory')
            data['display'] = self._parse_section(root, 'Display')
            data['storage'] = self._parse_section(root, 'Storage')
            data['sensors'] = self._parse_sensors(root)
            
            return data
        
        except Exception:
            return None
    
    def _parse_section(self, root: ET.Element, section_name: str) -> Dict[str, str]:
        """Parse a specific section from AIDA64 report"""
        section_data = {}
        
        for section in root.findall(f".//{section_name}"):
            for item in section:
                if item.tag and item.text:
                    section_data[item.tag] = item.text
        
        return section_data
    
    def _parse_sensors(self, root: ET.Element) -> Dict[str, float]:
        """Parse sensor data from AIDA64 report"""
        sensors = {}
        
        # Look for sensor readings
        for sensor in root.findall(".//Sensor"):
            name = sensor.get('name')
            value = sensor.get('value')
            
            if name and value:
                try:
                    # Try to extract numeric value
                    numeric_value = float(''.join(c for c in value if c.isdigit() or c == '.'))
                    sensors[name] = numeric_value
                except ValueError:
                    sensors[name] = value
        
        return sensors
    
    def set_report_path(self, path: Path):
        """Set custom AIDA64 report path"""
        self.report_path = path
    
    async def generate_report(self, aida64_exe: Path, output_path: Path) -> bool:
        """
        Generate AIDA64 report (requires AIDA64 to be installed)
        Returns True if successful
        """
        try:
            import subprocess
            
            # AIDA64 command line to generate report
            result = subprocess.run(
                [str(aida64_exe), "/R", str(output_path), "/XML"],
                timeout=30,
                check=False
            )
            
            if result.returncode == 0 and output_path.exists():
                self.report_path = output_path
                return True
        
        except Exception:
            pass
        
        return False
