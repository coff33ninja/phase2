"""API endpoints for Nexus."""
from api.metrics import router as metrics_router
from api.patterns import router as patterns_router
from api.chat import router as chat_router
from api.control import router as control_router
from api.training import router as training_router

__all__ = [
    "metrics_router",
    "patterns_router",
    "chat_router",
    "control_router",
    "training_router",
]
