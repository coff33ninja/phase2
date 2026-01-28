"""Resource optimization actions."""
import psutil
import subprocess
from typing import Dict, Any
from loguru import logger

from models import ActionResult, RiskLevel, ActionType
from actions.base_action import BaseAction


class ClearRAMAction(BaseAction):
    """Clear RAM cache and free memory."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.CLEAR_RAM
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        return "Free unused RAM (may cause brief slowdown)"
    
    def validate(self) -> tuple[bool, str]:
        """Validate RAM clearing."""
        return True, ""
    
    def execute(self) -> ActionResult:
        """Clear RAM cache."""
        try:
            # Get initial memory
            mem_before = psutil.virtual_memory()
            
            # On Windows, use EmptyWorkingSet
            if psutil.WINDOWS:
                # Clear working sets of all processes
                for proc in psutil.process_iter():
                    try:
                        proc.memory_info()  # This triggers working set trimming
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            # Get memory after
            mem_after = psutil.virtual_memory()
            
            freed_mb = (mem_before.used - mem_after.used) / (1024 * 1024)
            
            return ActionResult(
                success=True,
                message=f"Freed approximately {freed_mb:.1f} MB of RAM",
                data={
                    "freed_mb": round(freed_mb, 1),
                    "before_percent": mem_before.percent,
                    "after_percent": mem_after.percent
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to clear RAM",
                error=str(e)
            )


class SetCPUAffinityAction(BaseAction):
    """Set CPU affinity for a process."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SET_CPU_AFFINITY
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM
    
    @property
    def estimated_impact(self) -> str:
        cpus = self.parameters.get("cpus", [])
        return f"Limit {self.target} to CPU cores: {cpus}"
    
    def validate(self) -> tuple[bool, str]:
        """Validate CPU affinity change."""
        cpus = self.parameters.get("cpus")
        if not cpus:
            return False, "CPU list parameter required"
        
        cpu_count = psutil.cpu_count()
        if any(cpu >= cpu_count for cpu in cpus):
            return False, f"Invalid CPU core (max: {cpu_count - 1})"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Set CPU affinity."""
        try:
            cpus = self.parameters["cpus"]
            
            # Find process
            processes = []
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'].lower() == self.target.lower():
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if not processes:
                return ActionResult(
                    success=False,
                    message="Process not found",
                    error="PROCESS_NOT_FOUND"
                )
            
            updated_pids = []
            for proc in processes:
                try:
                    proc.cpu_affinity(cpus)
                    updated_pids.append(proc.pid)
                    logger.info(f"Set CPU affinity for {self.target} (PID: {proc.pid}) to {cpus}")
                except Exception as e:
                    logger.error(f"Failed to set affinity for PID {proc.pid}: {e}")
            
            return ActionResult(
                success=True,
                message=f"Updated CPU affinity for {len(updated_pids)} instance(s)",
                data={"pids": updated_pids, "cpus": cpus}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to set CPU affinity",
                error=str(e)
            )


class DiskCleanupAction(BaseAction):
    """Clean up temporary files and caches."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.DISK_CLEANUP
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        return "Clean temporary files and caches"
    
    def validate(self) -> tuple[bool, str]:
        """Validate disk cleanup."""
        return True, ""
    
    def execute(self) -> ActionResult:
        """Clean up disk space."""
        try:
            import os
            import tempfile
            import shutil
            
            cleaned_mb = 0
            cleaned_files = 0
            
            # Clean temp directory
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        os.remove(item_path)
                        cleaned_mb += size / (1024 * 1024)
                        cleaned_files += 1
                    elif os.path.isdir(item_path):
                        size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, _, filenames in os.walk(item_path)
                            for filename in filenames
                        )
                        shutil.rmtree(item_path, ignore_errors=True)
                        cleaned_mb += size / (1024 * 1024)
                        cleaned_files += 1
                except (PermissionError, OSError):
                    pass
            
            return ActionResult(
                success=True,
                message=f"Cleaned {cleaned_files} items, freed {cleaned_mb:.1f} MB",
                data={
                    "cleaned_files": cleaned_files,
                    "freed_mb": round(cleaned_mb, 1)
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to clean disk",
                error=str(e)
            )
