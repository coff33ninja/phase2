"""Process management actions."""
import psutil
import time
from typing import Dict, Any, Optional
from loguru import logger

from models import ActionResult, RiskLevel, ActionType
from actions.base_action import BaseAction
from config import config


class CloseProcessAction(BaseAction):
    """Close a process gracefully."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CLOSE_PROCESS
    
    @property
    def risk_level(self) -> RiskLevel:
        # Protected processes are high risk
        if config.is_process_protected(self.target):
            return RiskLevel.HIGH
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        return f"Close {self.target} (can be restarted)"
    
    def validate(self) -> tuple[bool, str]:
        """Validate process can be closed."""
        # Check if protected
        if config.is_process_protected(self.target):
            return False, f"Process {self.target} is protected"
        
        # Check if process exists
        if not self._find_process():
            return False, f"Process {self.target} not found"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Close the process."""
        try:
            processes = self._find_process()
            if not processes:
                return ActionResult(
                    success=False,
                    message="Process not found",
                    error="PROCESS_NOT_FOUND"
                )
            
            closed_pids = []
            for proc in processes:
                try:
                    proc.terminate()
                    # Wait up to 5 seconds for graceful termination
                    proc.wait(timeout=5)
                    closed_pids.append(proc.pid)
                    logger.info(f"Closed process {self.target} (PID: {proc.pid})")
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    proc.kill()
                    closed_pids.append(proc.pid)
                    logger.warning(f"Force killed process {self.target} (PID: {proc.pid})")
                except Exception as e:
                    logger.error(f"Failed to close process {proc.pid}: {e}")
            
            return ActionResult(
                success=True,
                message=f"Closed {len(closed_pids)} instance(s) of {self.target}",
                data={"pids": closed_pids, "count": len(closed_pids)}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to close process",
                error=str(e)
            )
    
    def rollback(self, snapshot_data: Dict[str, Any]) -> ActionResult:
        """Restart the closed process."""
        # Would need to store process path and arguments in snapshot
        return ActionResult(
            success=False,
            message="Process restart not implemented",
            error="NOT_IMPLEMENTED"
        )
    
    def _find_process(self) -> list:
        """Find process by name."""
        processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == self.target.lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes


class StartProcessAction(BaseAction):
    """Start a process."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.START_PROCESS
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        return f"Start {self.target}"
    
    def validate(self) -> tuple[bool, str]:
        """Validate process can be started."""
        # Check if process path exists
        import os
        if not os.path.exists(self.target):
            return False, f"Process path {self.target} not found"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Start the process."""
        try:
            import subprocess
            
            # Start process
            process = subprocess.Popen(
                self.target,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait a moment to ensure it started
            time.sleep(0.5)
            
            if process.poll() is None:
                return ActionResult(
                    success=True,
                    message=f"Started {self.target}",
                    data={"pid": process.pid}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Process exited immediately",
                    error="PROCESS_EXITED"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to start process",
                error=str(e)
            )


class SetProcessPriorityAction(BaseAction):
    """Set process priority."""
    
    PRIORITY_MAP = {
        "low": psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 0,
        "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 1,
        "normal": psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 2,
        "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'ABOVE_NORMAL_PRIORITY_CLASS') else 3,
        "high": psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else 4,
        "realtime": psutil.REALTIME_PRIORITY_CLASS if hasattr(psutil, 'REALTIME_PRIORITY_CLASS') else 5,
    }
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SET_PRIORITY
    
    @property
    def risk_level(self) -> RiskLevel:
        priority = self.parameters.get("priority", "normal")
        if priority in ["high", "realtime"]:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        priority = self.parameters.get("priority", "normal")
        return f"Set {self.target} priority to {priority}"
    
    def validate(self) -> tuple[bool, str]:
        """Validate priority change."""
        priority = self.parameters.get("priority")
        if not priority:
            return False, "Priority parameter required"
        
        if priority not in self.PRIORITY_MAP:
            return False, f"Invalid priority: {priority}"
        
        # Check if process exists
        processes = self._find_process()
        if not processes:
            return False, f"Process {self.target} not found"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Set process priority."""
        try:
            priority = self.parameters["priority"]
            priority_value = self.PRIORITY_MAP[priority]
            
            processes = self._find_process()
            if not processes:
                return ActionResult(
                    success=False,
                    message="Process not found",
                    error="PROCESS_NOT_FOUND"
                )
            
            updated_pids = []
            for proc in processes:
                try:
                    proc.nice(priority_value)
                    updated_pids.append(proc.pid)
                    logger.info(f"Set priority of {self.target} (PID: {proc.pid}) to {priority}")
                except Exception as e:
                    logger.error(f"Failed to set priority for PID {proc.pid}: {e}")
            
            return ActionResult(
                success=True,
                message=f"Updated priority for {len(updated_pids)} instance(s)",
                data={"pids": updated_pids, "priority": priority}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to set priority",
                error=str(e)
            )
    
    def _find_process(self) -> list:
        """Find process by name."""
        processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == self.target.lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes


class KillProcessAction(BaseAction):
    """Force kill a process (high risk)."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.KILL_PROCESS
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.HIGH
    
    @property
    def can_rollback(self) -> bool:
        return False
    
    @property
    def estimated_impact(self) -> str:
        return f"Force kill {self.target} (may lose unsaved data)"
    
    def validate(self) -> tuple[bool, str]:
        """Validate process can be killed."""
        if config.is_process_protected(self.target):
            return False, f"Process {self.target} is protected"
        
        processes = self._find_process()
        if not processes:
            return False, f"Process {self.target} not found"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Force kill the process."""
        try:
            processes = self._find_process()
            if not processes:
                return ActionResult(
                    success=False,
                    message="Process not found",
                    error="PROCESS_NOT_FOUND"
                )
            
            killed_pids = []
            for proc in processes:
                try:
                    proc.kill()
                    killed_pids.append(proc.pid)
                    logger.warning(f"Force killed process {self.target} (PID: {proc.pid})")
                except Exception as e:
                    logger.error(f"Failed to kill process {proc.pid}: {e}")
            
            return ActionResult(
                success=True,
                message=f"Killed {len(killed_pids)} instance(s) of {self.target}",
                data={"pids": killed_pids}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to kill process",
                error=str(e)
            )
    
    def _find_process(self) -> list:
        """Find process by name."""
        processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == self.target.lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
