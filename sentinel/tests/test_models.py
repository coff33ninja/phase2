"""
Unit tests for data models
"""
import pytest
from datetime import datetime
from models import (
    CPUMetrics, RAMMetrics, GPUMetrics, DiskMetrics,
    NetworkMetrics, ProcessInfo, SystemContext, SystemSnapshot
)


def test_cpu_metrics():
    """Test CPU metrics model"""
    cpu = CPUMetrics(
        usage_percent=50.5,
        per_core_usage=[45.0, 55.0, 50.0, 52.0],
        frequency_mhz=3600.0,
        temperature_celsius=65.0
    )
    
    assert cpu.usage_percent == 50.5
    assert len(cpu.per_core_usage) == 4
    assert cpu.frequency_mhz == 3600.0


def test_ram_metrics():
    """Test RAM metrics model"""
    ram = RAMMetrics(
        total_gb=16.0,
        used_gb=8.5,
        available_gb=7.5,
        usage_percent=53.1
    )
    
    assert ram.total_gb == 16.0
    assert ram.used_gb == 8.5
    assert ram.usage_percent == 53.1


def test_gpu_metrics():
    """Test GPU metrics model"""
    gpu = GPUMetrics(
        name="NVIDIA RTX 3080",
        usage_percent=75.0,
        memory_used_gb=6.5,
        memory_total_gb=10.0,
        temperature_celsius=72.0,
        power_draw_watts=250.0
    )
    
    assert gpu.name == "NVIDIA RTX 3080"
    assert gpu.usage_percent == 75.0
    assert gpu.memory_used_gb == 6.5


def test_process_info():
    """Test process info model"""
    proc = ProcessInfo(
        name="python.exe",
        pid=1234,
        cpu_percent=5.5,
        memory_mb=150.0,
        threads=8,
        status="running"
    )
    
    assert proc.name == "python.exe"
    assert proc.pid == 1234
    assert proc.cpu_percent == 5.5


def test_system_context():
    """Test system context model"""
    context = SystemContext(
        user_active=True,
        time_of_day="afternoon",
        day_of_week="Monday",
        user_action="coding"
    )
    
    assert context.user_active is True
    assert context.time_of_day == "afternoon"
    assert context.user_action == "coding"


def test_system_snapshot():
    """Test complete system snapshot"""
    cpu = CPUMetrics(
        usage_percent=50.0,
        per_core_usage=[50.0],
        frequency_mhz=3000.0
    )
    
    ram = RAMMetrics(
        total_gb=16.0,
        used_gb=8.0,
        available_gb=8.0,
        usage_percent=50.0
    )
    
    disk = DiskMetrics(
        read_mbps=100.0,
        write_mbps=50.0,
        queue_length=0
    )
    
    network = NetworkMetrics(
        download_mbps=10.0,
        upload_mbps=5.0,
        connections_active=25
    )
    
    context = SystemContext(
        user_active=True,
        time_of_day="afternoon",
        day_of_week="Monday"
    )
    
    snapshot = SystemSnapshot(
        cpu=cpu,
        ram=ram,
        disk=disk,
        network=network,
        context=context
    )
    
    assert snapshot.cpu.usage_percent == 50.0
    assert snapshot.ram.total_gb == 16.0
    assert snapshot.disk.read_mbps == 100.0
    assert snapshot.network.connections_active == 25
    assert isinstance(snapshot.timestamp, datetime)
