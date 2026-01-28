"""
Process information collector
Collects information about running processes
"""
import psutil
from typing import List
from collectors.base import BaseCollector
from models import ProcessInfo


class ProcessCollector(BaseCollector):
    """Collects process information"""
    
    def __init__(self, top_n: int = 10):
        super().__init__("Process")
        self.top_n = top_n
    
    async def collect(self) -> List[ProcessInfo]:
        """Collect top N processes by CPU usage"""
        processes = []
        
        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'num_threads', 'status']):
                try:
                    pinfo = proc.info
                    
                    # Get memory in MB
                    memory_mb = 0.0
                    if pinfo.get('memory_info'):
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    
                    processes.append(ProcessInfo(
                        name=pinfo.get('name', 'Unknown'),
                        pid=pinfo.get('pid', 0),
                        cpu_percent=pinfo.get('cpu_percent', 0.0) or 0.0,
                        memory_mb=round(memory_mb, 2),
                        threads=pinfo.get('num_threads', 0) or 0,
                        status=pinfo.get('status', 'unknown') or 'unknown'
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage and return top N
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
            return processes[:self.top_n]
            
        except Exception:
            return []
