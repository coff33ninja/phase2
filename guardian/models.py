"""Data models for Guardian."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk levels for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionStatus(str, Enum):
    """Action execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionType(str, Enum):
    """Types of actions."""
    CLOSE_PROCESS = "close_process"
    START_PROCESS = "start_process"
    SET_PRIORITY = "set_priority"
    KILL_PROCESS = "kill_process"
    SUSPEND_PROCESS = "suspend_process"
    RESUME_PROCESS = "resume_process"
    CLEAR_RAM = "clear_ram"
    SET_CPU_AFFINITY = "set_cpu_affinity"
    GPU_POWER_MODE = "gpu_power_mode"
    DISK_CLEANUP = "disk_cleanup"
    POWER_PLAN = "power_plan"
    DISPLAY_BRIGHTNESS = "display_brightness"
    VOLUME_CONTROL = "volume_control"
    NOTIFICATION_MODE = "notification_mode"
    SLEEP = "sleep"
    HIBERNATE = "hibernate"


class ActionResult(BaseModel):
    """Result of an action execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Process closed successfully",
                "data": {"process": "chrome.exe", "pid": 1234},
                "execution_time_ms": 125.5
            }
        }


class ActionMetadata(BaseModel):
    """Metadata for an action."""
    action_id: str
    action_type: ActionType
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel
    requires_approval: bool = False
    can_rollback: bool = True
    estimated_impact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ActionLog(BaseModel):
    """Log entry for an executed action."""
    action_id: str
    action_type: ActionType
    target: str
    parameters: Dict[str, Any]
    status: ActionStatus
    result: Optional[ActionResult] = None
    snapshot_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    user_approved: bool = False
    rolled_back: bool = False


class SystemSnapshot(BaseModel):
    """Snapshot of system state before action."""
    snapshot_id: str
    action_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    processes: list[Dict[str, Any]] = Field(default_factory=list)
    system_state: Dict[str, Any] = Field(default_factory=dict)
    can_restore: bool = True


class Profile(BaseModel):
    """Automation profile."""
    name: str
    description: str
    trigger: Optional[str] = None
    actions: list[Dict[str, Any]] = Field(default_factory=list)
    schedule: Optional[str] = None
    rollback_on_exit: bool = False
    enabled: bool = True
