"""Action executor with safety checks."""
import uuid
from typing import Optional
from loguru import logger

from models import ActionResult, ActionLog, ActionStatus
from actions.base_action import BaseAction
from safety import ActionValidator, SnapshotManager, RollbackManager
from execution.logger import ActionLogger
from config import config


class ActionExecutor:
    """Execute actions with safety checks."""
    
    def __init__(self):
        """Initialize executor."""
        self.validator = ActionValidator()
        self.snapshot_manager = SnapshotManager()
        self.rollback_manager = RollbackManager(self.snapshot_manager)
        self.action_logger = ActionLogger()
    
    def execute_action(
        self,
        action: BaseAction,
        user_approved: bool = False
    ) -> ActionResult:
        """Execute an action with full safety checks.
        
        Args:
            action: Action to execute
            user_approved: Whether user has approved this action
            
        Returns:
            ActionResult with execution details
        """
        action_id = str(uuid.uuid4())
        snapshot_id = None
        
        try:
            # Create metadata
            metadata = action.create_metadata(action_id)
            
            # Log action start
            action_log = ActionLog(
                action_id=action_id,
                action_type=action.action_type,
                target=action.target,
                parameters=action.parameters,
                status=ActionStatus.PENDING,
                started_at=metadata.created_at,
                user_approved=user_approved
            )
            
            # Validate action
            is_valid, error_msg = self.validator.validate_action(action)
            if not is_valid:
                logger.warning(f"Action validation failed: {error_msg}")
                action_log.status = ActionStatus.FAILED
                result = ActionResult(
                    success=False,
                    message="Validation failed",
                    error=error_msg
                )
                action_log.result = result
                self.action_logger.log_action(action_log)
                return result
            
            # Check if approval required
            if self.validator.requires_approval(action) and not user_approved:
                logger.info(f"Action requires approval: {action}")
                action_log.status = ActionStatus.PENDING
                result = ActionResult(
                    success=False,
                    message="Action requires user approval",
                    error="APPROVAL_REQUIRED"
                )
                action_log.result = result
                self.action_logger.log_action(action_log)
                return result
            
            # Create snapshot if enabled
            if config.snapshot_before_action:
                snapshot = self.snapshot_manager.create_snapshot(action_id)
                snapshot_id = snapshot.snapshot_id
                action_log.snapshot_id = snapshot_id
                logger.info(f"Created snapshot {snapshot_id}")
            
            # Execute action
            logger.info(f"Executing action: {action}")
            action_log.status = ActionStatus.RUNNING
            
            result = action.run()
            
            # Update log
            if result.success:
                action_log.status = ActionStatus.SUCCESS
                logger.info(f"Action completed successfully: {action}")
            else:
                action_log.status = ActionStatus.FAILED
                logger.error(f"Action failed: {result.error}")
                
                # Attempt rollback if enabled and possible
                if config.enable_rollback and snapshot_id:
                    logger.info("Attempting automatic rollback")
                    rollback_result = self.rollback_manager.rollback_action(
                        action,
                        snapshot_id
                    )
                    if rollback_result.success:
                        action_log.rolled_back = True
                        action_log.status = ActionStatus.ROLLED_BACK
                        logger.info("Automatic rollback successful")
            
            action_log.result = result
            self.action_logger.log_action(action_log)
            
            return result
            
        except Exception as e:
            logger.error(f"Action execution failed with exception: {e}")
            
            # Log failure
            if 'action_log' in locals():
                action_log.status = ActionStatus.FAILED
                action_log.result = ActionResult(
                    success=False,
                    message="Execution failed",
                    error=str(e)
                )
                self.action_logger.log_action(action_log)
            
            return ActionResult(
                success=False,
                message="Execution failed",
                error=str(e)
            )
    
    def rollback_last_action(self) -> ActionResult:
        """Rollback the last executed action.
        
        Returns:
            ActionResult with rollback status
        """
        # Get last action from log
        last_action = self.action_logger.get_recent_actions(limit=1)
        if not last_action:
            return ActionResult(
                success=False,
                message="No actions to rollback",
                error="NO_ACTIONS"
            )
        
        action_log = last_action[0]
        
        if not action_log.snapshot_id:
            return ActionResult(
                success=False,
                message="No snapshot available for rollback",
                error="NO_SNAPSHOT"
            )
        
        # Would need to recreate action instance here
        # For now, return not implemented
        return ActionResult(
            success=False,
            message="Manual rollback not yet implemented",
            error="NOT_IMPLEMENTED"
        )
