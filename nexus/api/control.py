"""Control API endpoints for Guardian integration."""
import sqlite3
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from config import config

router = APIRouter(prefix="/api/control", tags=["control"])


class ActionRequest(BaseModel):
    """Action execution request."""
    action_type: str
    target: str
    parameters: Dict[str, Any] = {}


class ProfileRequest(BaseModel):
    """Profile activation request."""
    profile_name: str


def get_guardian_connection():
    """Get connection to Guardian database."""
    if not config.guardian_db_path.exists():
        raise HTTPException(status_code=503, detail="Guardian database not found")
    
    conn = sqlite3.connect(config.guardian_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/profiles")
async def list_profiles() -> List[Dict[str, Any]]:
    """List all available Guardian profiles.
    
    Returns:
        List of profile dictionaries
    """
    try:
        # In a real implementation, this would call Guardian's profile manager
        # For now, return placeholder data
        
        return [
            {
                "name": "gaming",
                "description": "Optimize system for gaming performance",
                "enabled": True,
                "actions": 5
            },
            {
                "name": "work",
                "description": "Optimize system for work productivity",
                "enabled": True,
                "actions": 3
            },
            {
                "name": "power_saver",
                "description": "Conserve battery power",
                "enabled": True,
                "actions": 4
            }
        ]
        
    except Exception as e:
        logger.error(f"Failed to list profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/activate")
async def activate_profile(request: ProfileRequest) -> Dict[str, Any]:
    """Activate a Guardian profile.
    
    Args:
        request: Profile activation request
        
    Returns:
        Activation result
    """
    try:
        # In a real implementation, this would call Guardian's API
        # For now, return placeholder response
        
        return {
            "success": True,
            "message": f"Profile {request.profile_name} activated",
            "profile": request.profile_name
        }
        
    except Exception as e:
        logger.error(f"Failed to activate profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions/execute")
async def execute_action(request: ActionRequest) -> Dict[str, Any]:
    """Execute a Guardian action.
    
    Args:
        request: Action execution request
        
    Returns:
        Execution result
    """
    try:
        # In a real implementation, this would call Guardian's executor
        # For now, return placeholder response
        
        return {
            "success": True,
            "message": f"Action {request.action_type} executed",
            "action_id": "placeholder-id"
        }
        
    except Exception as e:
        logger.error(f"Failed to execute action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/history")
async def get_action_history(
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get Guardian action history.
    
    Args:
        limit: Maximum number of actions to return
        
    Returns:
        List of action log entries
    """
    try:
        conn = get_guardian_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM action_logs
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get action history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions/rollback")
async def rollback_action(action_id: str = None) -> Dict[str, Any]:
    """Rollback a Guardian action.
    
    Args:
        action_id: Action ID to rollback (optional, defaults to last)
        
    Returns:
        Rollback result
    """
    try:
        # In a real implementation, this would call Guardian's rollback
        # For now, return placeholder response
        
        return {
            "success": True,
            "message": "Action rolled back successfully",
            "action_id": action_id or "last"
        }
        
    except Exception as e:
        logger.error(f"Failed to rollback action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_guardian_status() -> Dict[str, Any]:
    """Get Guardian status.
    
    Returns:
        Guardian status dictionary
    """
    try:
        # In a real implementation, this would call Guardian's status API
        # For now, return placeholder data
        
        return {
            "automation_level": "semi_auto",
            "active_profile": None,
            "rollback_enabled": True,
            "protected_processes": ["explorer.exe", "System", "Registry", "csrss.exe"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get Guardian status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
