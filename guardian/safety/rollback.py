"""Rollback manager for failed actions."""
from typing import Dict, Any, Optional
from loguru import logger

from models import ActionResult, SystemSnapshot
from actions.base_action import BaseAction
from safety.snapshot import SnapshotManager


class RollbackManager:
    """Manage action rollbacks."""
    
    def __init__(self, snapshot_manager: SnapshotManager):
        """Initialize rollback manager.
        
        Args:
            snapshot_manager: Snapshot manager instance
        """
        self.snapshot_manager = snapshot_manager
        self.rollback_history: list[Dict[str, Any]] = []
    
    def rollback_action(
        self,
        action: BaseAction,
        snapshot_id: str
    ) -> ActionResult:
        """Rollback an action using snapshot.
        
        Args:
            action: Action to rollback
            snapshot_id: Snapshot to restore
            
        Returns:
            ActionResult with rollback status
        """
        try:
            # Get snapshot
            snapshot = self.snapshot_manager.get_snapshot(snapshot_id)
            if not snapshot:
                logger.error(f"Snapshot {snapshot_id} not found")
                return ActionResult(
                    success=False,
                    message="Snapshot not found",
                    error="SNAPSHOT_NOT_FOUND"
                )
            
            if not snapshot.can_restore:
                logger.error(f"Snapshot {snapshot_id} cannot be restored")
                return ActionResult(
                    success=False,
                    message="Snapshot cannot be restored",
                    error="SNAPSHOT_INVALID"
                )
            
            # Check if action supports rollback
            if not action.can_rollback:
                logger.warning(f"Action {action.action_type} does not support rollback")
                return ActionResult(
                    success=False,
                    message="Action does not support rollback",
                    error="ROLLBACK_NOT_SUPPORTED"
                )
            
            # Perform rollback
            logger.info(f"Rolling back action {action.action_type} using snapshot {snapshot_id}")
            
            snapshot_data = {
                'processes': snapshot.processes,
                'system_state': snapshot.system_state
            }
            
            result = action.rollback(snapshot_data)
            
            # Record rollback
            self.rollback_history.append({
                'action_type': action.action_type.value,
                'snapshot_id': snapshot_id,
                'success': result.success,
                'timestamp': snapshot.timestamp
            })
            
            if result.success:
                logger.info(f"Successfully rolled back action {action.action_type}")
            else:
                logger.error(f"Failed to rollback action {action.action_type}: {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Rollback failed with exception: {e}")
            return ActionResult(
                success=False,
                message="Rollback failed",
                error=str(e)
            )
    
    def get_rollback_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get recent rollback history.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of rollback entries
        """
        return self.rollback_history[-limit:]
    
    def can_rollback(self, action: BaseAction, snapshot_id: str) -> bool:
        """Check if action can be rolled back.
        
        Args:
            action: Action to check
            snapshot_id: Snapshot ID
            
        Returns:
            True if rollback is possible
        """
        if not action.can_rollback:
            return False
        
        snapshot = self.snapshot_manager.get_snapshot(snapshot_id)
        if not snapshot or not snapshot.can_restore:
            return False
        
        return True
