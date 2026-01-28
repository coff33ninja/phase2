"""
Sample test data fixtures
"""
from datetime import datetime
from models import (
    CPUMetrics, RAMMetrics, GPUMetrics, DiskMetrics,
    NetworkMetrics, ProcessInfo, SystemContext, SystemSnapshot
)


def create_sample_cpu_metrics() -> CPUMetrics:
    """Create sample CPU metrics"""
    return CPUMetrics(
        usage_percent=50.5,
        per_core_usage=[45.0, 55.0, 50.0, 52.0],
        frequency_mhz=3600.0,
        temperature_celsius=65.0
    )


def create_sample_ram_metrics() -> RAMMetrics:
    """Create sample RAM metrics"""
    return RAMMetrics(
        total_gb=16.0,
        used_gb=8.5,
        available_gb=7.5,
        cached_gb=2.0,
        usage_percent=53.1
    )


def create_sample_gpu_metrics() -> GPUMetrics:
    """Create sample GPU metrics"""
    return GPUMetrics(
        name="NVIDIA RTX 3080",
        usage_percent=75.0,
        memory_used_gb=6.5,
        memory_total_gb=10.0,
        temperature_celsius=72.0,
        power_draw_watts=250.0
    )


def create_sample_disk_metrics() -> DiskMetrics:
    """Create sample disk metrics"""
    return DiskMetrics(
        read_mbps=100.5,
        write_mbps=50.2,
        queue_length=2,
        usage_percent=65.0
    )


def create_sample_network_metrics() -> NetworkMetrics:
    """Create sample network metrics"""
    return NetworkMetrics(
        download_mbps=10.5,
        upload_mbps=5.2,
        connections_active=25
    )


def create_sample_process_info() -> ProcessInfo:
    """Create sample process info"""
    return ProcessInfo(
        name="python.exe",
        pid=1234,
        cpu_percent=5.5,
        memory_mb=150.0,
        threads=8,
        status="running"
    )


def create_sample_context() -> SystemContext:
    """Create sample system context"""
    return SystemContext(
        user_active=True,
        time_of_day="afternoon",
        day_of_week="Monday",
        user_action="coding"
    )


def create_sample_snapshot() -> SystemSnapshot:
    """Create complete sample snapshot"""
    return SystemSnapshot(
        timestamp=datetime.utcnow(),
        cpu=create_sample_cpu_metrics(),
        ram=create_sample_ram_metrics(),
        gpu=[create_sample_gpu_metrics()],
        disk=create_sample_disk_metrics(),
        network=create_sample_network_metrics(),
        processes=[create_sample_process_info()],
        context=create_sample_context()
    )
