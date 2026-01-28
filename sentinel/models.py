"""
Data models for system metrics
Using Pydantic for validation and serialization
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CPUMetrics(BaseModel):
    """CPU metrics snapshot"""
    usage_percent: float = Field(description="Overall CPU usage percentage")
    per_core_usage: List[float] = Field(default_factory=list, description="Per-core usage")
    frequency_mhz: float = Field(description="Current CPU frequency in MHz")
    temperature_celsius: Optional[float] = Field(default=None, description="CPU temperature")
    load_average: Optional[List[float]] = Field(default=None, description="Load average (1, 5, 15 min)")


class RAMMetrics(BaseModel):
    """RAM metrics snapshot"""
    total_gb: float = Field(description="Total RAM in GB")
    used_gb: float = Field(description="Used RAM in GB")
    available_gb: float = Field(description="Available RAM in GB")
    cached_gb: Optional[float] = Field(default=None, description="Cached RAM in GB")
    usage_percent: float = Field(description="RAM usage percentage")


class GPUMetrics(BaseModel):
    """GPU metrics snapshot"""
    name: str = Field(description="GPU name/model")
    usage_percent: float = Field(description="GPU usage percentage")
    memory_used_gb: float = Field(description="GPU memory used in GB")
    memory_total_gb: float = Field(description="Total GPU memory in GB")
    temperature_celsius: Optional[float] = Field(default=None, description="GPU temperature")
    power_draw_watts: Optional[float] = Field(default=None, description="Power draw in watts")


class DiskMetrics(BaseModel):
    """Disk I/O metrics snapshot"""
    read_mbps: float = Field(description="Read speed in MB/s")
    write_mbps: float = Field(description="Write speed in MB/s")
    queue_length: int = Field(description="Disk queue length")
    usage_percent: Optional[float] = Field(default=None, description="Disk usage percentage")


class NetworkMetrics(BaseModel):
    """Network metrics snapshot"""
    download_mbps: float = Field(description="Download speed in MB/s")
    upload_mbps: float = Field(description="Upload speed in MB/s")
    connections_active: int = Field(description="Active network connections")


class ProcessInfo(BaseModel):
    """Individual process information"""
    name: str = Field(description="Process name")
    pid: int = Field(description="Process ID")
    cpu_percent: float = Field(description="CPU usage percentage")
    memory_mb: float = Field(description="Memory usage in MB")
    threads: int = Field(description="Number of threads")
    status: str = Field(description="Process status")


class SystemContext(BaseModel):
    """System context information"""
    user_active: bool = Field(description="Is user actively using the system")
    time_of_day: str = Field(description="Time of day category (morning, afternoon, evening, night)")
    day_of_week: str = Field(description="Day of the week")
    user_action: Optional[str] = Field(default=None, description="Detected user action/activity")


class SystemSnapshot(BaseModel):
    """Complete system metrics snapshot"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu: CPUMetrics
    ram: RAMMetrics
    gpu: Optional[List[GPUMetrics]] = Field(default=None)
    disk: DiskMetrics
    network: NetworkMetrics
    processes: List[ProcessInfo] = Field(default_factory=list)
    context: SystemContext
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataPoint(BaseModel):
    """Generic time-series data point"""
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnomalyDetection(BaseModel):
    """Anomaly detection result"""
    timestamp: datetime
    metric_name: str
    current_value: float
    expected_value: float
    deviation_std: float
    severity: str = Field(description="low, medium, high, critical")
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
