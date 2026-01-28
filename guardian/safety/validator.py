"""Action validator for safety checks."""
from typing import Tuple
from loguru import logger

from models import RiskLevel
from actions.base_action import BaseAction
from config import config


class ActionValidator:
    """Validate actions before execution."""
    
    def __init__(self):
        """Initialize validator."""
        self.automation_level = config.automation_level
    
    def validate_action(self, action: BaseAction) -> Tuple[bool, str]:
        """Validate an action for execution.
        
        Args:
            action: Action to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # 1. Check action's own validation
        is_valid, error_msg = action.validate()
        if not is_valid:
            logger.warning(f"Action validation failed: {error_msg}")
            return False, error_msg
        
        # 2. Check protected processes
        if hasattr(action, 'target'):
            if config.is_process_protected(action.target):
                logger.warning(f"Action targets protected process: {action.target}")
                return False, f"Process {action.target} is protected"
        
        # 3. Check risk level vs automation level
        if not self._check_risk_level(action):
            return False, "Action risk level requires manual approval"
        
        # 4. Check system state
        if not self._check_system_state():
            return False, "System state not suitable for action"
        
        logger.info(f"Action validated: {action}")
        return True, ""
    
    def _check_risk_level(self, action: BaseAction) -> bool:
        """Check if action risk level is acceptable.
        
        Args:
            action: Action to check
            
        Returns:
            True if risk level is acceptable
        """
        risk = action.risk_level
        
        # Manual mode: all actions require approval
        if self.automation_level == "manual":
            return False
        
        # Semi-auto mode: medium and high risk require approval
        if self.automation_level == "semi_auto":
            if risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
                return False
        
        # Fully-auto mode: only high risk requires approval
        if self.automation_level == "fully_auto":
            if risk == RiskLevel.HIGH:
                return False
        
        return True
    
    def _check_system_state(self) -> bool:
        """Check if system state is suitable for actions.
        
        Returns:
            True if system state is OK
        """
        # Could check:
        # - CPU usage not too high
        # - Disk not full
        # - No critical processes running
        # For now, always return True
        return True
    
    def requires_approval(self, action: BaseAction) -> bool:
        """Check if action requires user approval.
        
        Args:
            action: Action to check
            
        Returns:
            True if approval required
        """
        # Check automation level
        if self.automation_level == "manual":
            return True
        
        risk = action.risk_level
        
        if self.automation_level == "semi_auto":
            return risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        
        if self.automation_level == "fully_auto":
            return risk == RiskLevel.HIGH
        
        return False
