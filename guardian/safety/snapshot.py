"""System snapshot for rollback capability."""
import psutil
import uuid
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from models import SystemSnapshot


class SnapshotManager:
    """Manage system snapshots for rollback."""
    
    def __init__(self):
        """Initialize snapshot manager."""
        self.snapshots: Dict[str, SystemSnapshot] = {}
    
    def create_snapshot(self, action_id: str) -> SystemSnapshot:
        """Create a snapshot of current system state.
        
        Args:
            action_id: ID of action being performed
            
        Returns:
            SystemSnapshot instance
        """
        snapshot_id = str(uuid.uuid4())
        
        try:
            # Capture process list
            processes = self._capture_processes()
            
            # Capture system state
            system_state = self._capture_system_state()
            
            snapshot = SystemSnapshot(
                snapshot_id=snapshot_id,
                action_id=action_id,
                processes=processes,
                system_state=system_state,
                can_restore=True
            )
            
            # Store snapshot
            self.snapshots[snapshot_id] = snapshot
            
            logger.info(f"Created snapshot {snapshot_id} for action {action_id}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            # Return empty snapshot
            return SystemSnapshot(
                snapshot_id=snapshot_id,
                action_id=action_id,
                can_restore=False
            )
    
    def get_snapshot(self, snapshot_id: str) -> SystemSnapshot:
        """Get a snapshot by ID.
        
        Args:
            snapshot_id: Snapshot identifier
            
        Returns:
            SystemSnapshot or None
        """
        return self.snapshots.get(snapshot_id)
    
    def delete_snapshot(self, snapshot_id: str):
        """Delete a snapshot.
        
        Args:
            snapshot_id: Snapshot identifier
        """
        if snapshot_id in self.snapshots:
            del self.snapshots[snapshot_id]
            logger.info(f"Deleted snapshot {snapshot_id}")
    
    def _capture_processes(self) -> List[Dict[str, Any]]:
        """Capture current process list.
        
        Returns:
            List of process information
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'status': info['status'],
                    'cpu_percent': info['cpu_percent'],
                    'memory_percent': info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return processes
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state.
        
        Returns:
            Dictionary of system metrics
        """
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Try to get power plan on Windows
            power_plan = None
            try:
                import subprocess
                result = subprocess.run(
                    ['powercfg', '/getactivescheme'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Parse power plan from output
                    power_plan = result.stdout.strip()
            except:
                pass
            
            return {
                'cpu_percent': cpu,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': disk.percent,
                'power_plan': power_plan,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to capture system state: {e}")
            return {}
