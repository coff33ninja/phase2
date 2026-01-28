"""
Data formatting utilities
"""
from datetime import datetime
from typing import Any, Dict


def format_bytes(bytes_value: float) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_percentage(value: float) -> str:
    """Format percentage with color coding"""
    if value < 50:
        return f"[green]{value:.1f}%[/green]"
    elif value < 80:
        return f"[yellow]{value:.1f}%[/yellow]"
    else:
        return f"[red]{value:.1f}%[/red]"


def format_timestamp(dt: datetime) -> str:
    """Format timestamp for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_metric_value(metric_name: str, value: float) -> str:
    """Format metric value based on metric type"""
    if 'percent' in metric_name.lower() or 'usage' in metric_name.lower():
        return f"{value:.1f}%"
    elif 'mbps' in metric_name.lower() or 'mb/s' in metric_name.lower():
        return f"{value:.2f} MB/s"
    elif 'gb' in metric_name.lower():
        return f"{value:.2f} GB"
    elif 'mhz' in metric_name.lower():
        return f"{value:.0f} MHz"
    elif 'celsius' in metric_name.lower():
        return f"{value:.1f}°C"
    elif 'watts' in metric_name.lower():
        return f"{value:.1f}W"
    else:
        return f"{value:.2f}"
