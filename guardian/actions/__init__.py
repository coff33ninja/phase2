"""Actions module."""
from actions.base_action import BaseAction
from actions.process_actions import (
    CloseProcessAction,
    StartProcessAction,
    SetProcessPriorityAction,
    KillProcessAction
)
from actions.resource_actions import (
    ClearRAMAction,
    SetCPUAffinityAction,
    DiskCleanupAction
)
from actions.system_actions import (
    PowerPlanAction,
    DisplayBrightnessAction,
    SleepAction,
    HibernateAction
)

__all__ = [
    "BaseAction",
    "CloseProcessAction",
    "StartProcessAction",
    "SetProcessPriorityAction",
    "KillProcessAction",
    "ClearRAMAction",
    "SetCPUAffinityAction",
    "DiskCleanupAction",
    "PowerPlanAction",
    "DisplayBrightnessAction",
    "SleepAction",
    "HibernateAction",
]
