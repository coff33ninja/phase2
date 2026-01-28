"""System-level actions."""
import subprocess
import platform
from typing import Dict, Any
from loguru import logger

from models import ActionResult, RiskLevel, ActionType
from actions.base_action import BaseAction


class PowerPlanAction(BaseAction):
    """Switch Windows power plan."""
    
    POWER_PLANS = {
        "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    }
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.POWER_PLAN
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        mode = self.parameters.get("mode", "balanced")
        return f"Switch to {mode} power plan"
    
    def validate(self) -> tuple[bool, str]:
        """Validate power plan change."""
        if platform.system() != "Windows":
            return False, "Power plan switching only supported on Windows"
        
        mode = self.parameters.get("mode")
        if not mode:
            return False, "Mode parameter required"
        
        if mode not in self.POWER_PLANS:
            return False, f"Invalid mode: {mode}"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Switch power plan."""
        try:
            mode = self.parameters["mode"]
            plan_guid = self.POWER_PLANS[mode]
            
            # Use powercfg to set active power plan
            result = subprocess.run(
                ["powercfg", "/setactive", plan_guid],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Switched to {mode} power plan")
                return ActionResult(
                    success=True,
                    message=f"Switched to {mode} power plan",
                    data={"mode": mode, "guid": plan_guid}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Failed to switch power plan",
                    error=result.stderr
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to switch power plan",
                error=str(e)
            )
    
    def rollback(self, snapshot_data: Dict[str, Any]) -> ActionResult:
        """Restore previous power plan."""
        previous_mode = snapshot_data.get("power_plan")
        if previous_mode and previous_mode in self.POWER_PLANS:
            self.parameters["mode"] = previous_mode
            return self.execute()
        
        return ActionResult(
            success=False,
            message="Cannot restore power plan",
            error="NO_SNAPSHOT_DATA"
        )


class DisplayBrightnessAction(BaseAction):
    """Adjust display brightness."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.DISPLAY_BRIGHTNESS
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def estimated_impact(self) -> str:
        level = self.parameters.get("level", 50)
        return f"Set brightness to {level}%"
    
    def validate(self) -> tuple[bool, str]:
        """Validate brightness change."""
        level = self.parameters.get("level")
        if level is None:
            return False, "Level parameter required"
        
        if not 0 <= level <= 100:
            return False, "Level must be between 0 and 100"
        
        return True, ""
    
    def execute(self) -> ActionResult:
        """Set display brightness."""
        try:
            level = self.parameters["level"]
            
            if platform.system() == "Windows":
                # Use WMI to set brightness
                import wmi
                c = wmi.WMI(namespace='wmi')
                methods = c.WmiMonitorBrightnessMethods()[0]
                methods.WmiSetBrightness(level, 0)
                
                logger.info(f"Set brightness to {level}%")
                return ActionResult(
                    success=True,
                    message=f"Set brightness to {level}%",
                    data={"level": level}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Brightness control not supported on this platform",
                    error="UNSUPPORTED_PLATFORM"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to set brightness",
                error=str(e)
            )


class SleepAction(BaseAction):
    """Put system to sleep."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.SLEEP
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM
    
    @property
    def can_rollback(self) -> bool:
        return False
    
    @property
    def estimated_impact(self) -> str:
        return "Put system to sleep"
    
    def validate(self) -> tuple[bool, str]:
        """Validate sleep action."""
        return True, ""
    
    def execute(self) -> ActionResult:
        """Put system to sleep."""
        try:
            if platform.system() == "Windows":
                # Use rundll32 to sleep
                subprocess.run(
                    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                    check=True
                )
                
                return ActionResult(
                    success=True,
                    message="System going to sleep"
                )
            else:
                return ActionResult(
                    success=False,
                    message="Sleep not supported on this platform",
                    error="UNSUPPORTED_PLATFORM"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to sleep system",
                error=str(e)
            )


class HibernateAction(BaseAction):
    """Hibernate the system."""
    
    @property
    def action_type(self) -> ActionType:
        return ActionType.HIBERNATE
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM
    
    @property
    def can_rollback(self) -> bool:
        return False
    
    @property
    def estimated_impact(self) -> str:
        return "Hibernate system (save state to disk)"
    
    def validate(self) -> tuple[bool, str]:
        """Validate hibernate action."""
        return True, ""
    
    def execute(self) -> ActionResult:
        """Hibernate the system."""
        try:
            if platform.system() == "Windows":
                # Use shutdown command to hibernate
                subprocess.run(
                    ["shutdown", "/h"],
                    check=True
                )
                
                return ActionResult(
                    success=True,
                    message="System hibernating"
                )
            else:
                return ActionResult(
                    success=False,
                    message="Hibernate not supported on this platform",
                    error="UNSUPPORTED_PLATFORM"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to hibernate system",
                error=str(e)
            )
