"""
System utilities
Helper functions for system operations
"""
import platform
import os
from pathlib import Path
from typing import Dict, Optional


def get_system_info() -> Dict[str, str]:
    """Get basic system information"""
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == 'Windows'


def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system() == 'Linux'


def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system() == 'Darwin'


def get_hostname() -> str:
    """Get system hostname"""
    return platform.node()


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if needed"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(path: Path) -> float:
    """Get file size in MB"""
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def is_admin() -> bool:
    """Check if running with admin/root privileges"""
    try:
        if is_windows():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def get_cpu_count() -> int:
    """Get number of CPU cores"""
    return os.cpu_count() or 1


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with default"""
    return os.getenv(name, default)


def format_path_for_platform(path: str) -> str:
    """Format path for current platform"""
    if is_windows():
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')
