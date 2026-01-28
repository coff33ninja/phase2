"""
Time and date utilities
"""
from datetime import datetime, timedelta
from typing import Optional


def get_time_range(hours: int = 24) -> tuple[datetime, datetime]:
    """
    Get time range for the last N hours
    Returns (start_time, end_time)
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    return start_time, end_time


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string to datetime
    Supports ISO format and common formats
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        pass
    
    # Try common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def get_time_bucket(timestamp: datetime, bucket_size_minutes: int = 5) -> datetime:
    """
    Round timestamp down to nearest time bucket
    Useful for aggregating data
    """
    minutes = (timestamp.minute // bucket_size_minutes) * bucket_size_minutes
    return timestamp.replace(minute=minutes, second=0, microsecond=0)


def is_business_hours(timestamp: datetime) -> bool:
    """Check if timestamp is during business hours (9 AM - 5 PM, Mon-Fri)"""
    if timestamp.weekday() >= 5:  # Saturday or Sunday
        return False
    
    if timestamp.hour < 9 or timestamp.hour >= 17:
        return False
    
    return True


def seconds_until_next_interval(interval_seconds: int) -> float:
    """Calculate seconds until next interval boundary"""
    now = datetime.utcnow()
    seconds_since_epoch = now.timestamp()
    seconds_into_interval = seconds_since_epoch % interval_seconds
    return interval_seconds - seconds_into_interval
