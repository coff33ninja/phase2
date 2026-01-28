"""Base action class for all Guardian actions."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time
from loguru import logger

from models import ActionResult, ActionMetadata, RiskLevel, ActionType


class BaseAction(ABC):
    """Abstract base class for all actions."""
    
    def __init__(
        self,
        target: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Initialize action.
        
        Args:
            target: Target of the action (process name, resource, etc.)
            parameters: Additional parameters for the action
        """
        self.target = target
        self.parameters = parameters or {}
        self.metadata: Optional[ActionMetadata] = None
    
    @property
    @abstractmethod
    def action_type(self) -> ActionType:
        """Get action type."""
        pass
    
    @property
    @abstractmethod
    def risk_level(self) -> RiskLevel:
        """Get risk level of this action."""
        pass
    
    @property
    def can_rollback(self) -> bool:
        """Check if action can be rolled back.
        
        Returns:
            True if action supports rollback
        """
        return True
    
    @property
    def estimated_impact(self) -> Optional[str]:
        """Get estimated impact description.
        
        Returns:
            Human-readable impact description
        """
        return None
    
    @abstractmethod
    def validate(self) -> tuple[bool, str]:
        """Validate action before execution.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def execute(self) -> ActionResult:
        """Execute the action.
        
        Returns:
            ActionResult with execution details
        """
        pass
    
    def rollback(self, snapshot_data: Dict[str, Any]) -> ActionResult:
        """Rollback the action.
        
        Args:
            snapshot_data: Snapshot data to restore
            
        Returns:
            ActionResult with rollback details
        """
        return ActionResult(
            success=False,
            message="Rollback not implemented for this action",
            error="NOT_IMPLEMENTED"
        )
    
    def create_metadata(self, action_id: str) -> ActionMetadata:
        """Create metadata for this action.
        
        Args:
            action_id: Unique action identifier
            
        Returns:
            ActionMetadata instance
        """
        requires_approval = self.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        
        self.metadata = ActionMetadata(
            action_id=action_id,
            action_type=self.action_type,
            target=self.target,
            parameters=self.parameters,
            risk_level=self.risk_level,
            requires_approval=requires_approval,
            can_rollback=self.can_rollback,
            estimated_impact=self.estimated_impact
        )
        
        return self.metadata
    
    def run(self) -> ActionResult:
        """Run the action with timing.
        
        Returns:
            ActionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Validate first
            is_valid, error_msg = self.validate()
            if not is_valid:
                return ActionResult(
                    success=False,
                    message="Validation failed",
                    error=error_msg,
                    execution_time_ms=0.0
                )
            
            # Execute
            logger.info(f"Executing {self.action_type.value} on {self.target}")
            result = self.execute()
            
            # Add execution time
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            
            if result.success:
                logger.info(
                    f"Action {self.action_type.value} completed successfully "
                    f"in {execution_time:.2f}ms"
                )
            else:
                logger.warning(
                    f"Action {self.action_type.value} failed: {result.error}"
                )
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Action {self.action_type.value} raised exception: {e}")
            
            return ActionResult(
                success=False,
                message="Action raised exception",
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(target={self.target}, risk={self.risk_level.value})"
