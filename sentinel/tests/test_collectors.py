"""
Unit tests for collectors
"""
import pytest
import asyncio
from collectors import (
    CPUCollector, RAMCollector, GPUCollector,
    DiskCollector, NetworkCollector, ProcessCollector, ContextCollector
)


@pytest.mark.asyncio
async def test_cpu_collector():
    """Test CPU collector"""
    collector = CPUCollector()
    metrics = await collector.collect()
    
    assert metrics is not None
    assert 0 <= metrics.usage_percent <= 100
    assert metrics.frequency_mhz > 0
    assert len(metrics.per_core_usage) > 0


@pytest.mark.asyncio
async def test_ram_collector():
    """Test RAM collector"""
    collector = RAMCollector()
    metrics = await collector.collect()
    
    assert metrics is not None
    assert metrics.total_gb > 0
    assert 0 <= metrics.usage_percent <= 100
    assert metrics.used_gb <= metrics.total_gb


@pytest.mark.asyncio
async def test_disk_collector():
    """Test Disk collector"""
    collector = DiskCollector()
    
    # First collection initializes
    metrics1 = await collector.collect()
    assert metrics1 is not None
    
    # Second collection should have real data
    await asyncio.sleep(0.1)
    metrics2 = await collector.collect()
    assert metrics2.read_mbps >= 0
    assert metrics2.write_mbps >= 0


@pytest.mark.asyncio
async def test_network_collector():
    """Test Network collector"""
    collector = NetworkCollector()
    
    # First collection initializes
    metrics1 = await collector.collect()
    assert metrics1 is not None
    
    # Second collection should have real data
    await asyncio.sleep(0.1)
    metrics2 = await collector.collect()
    assert metrics2.download_mbps >= 0
    assert metrics2.upload_mbps >= 0
    assert metrics2.connections_active >= 0


@pytest.mark.asyncio
async def test_process_collector():
    """Test Process collector"""
    collector = ProcessCollector(top_n=5)
    processes = await collector.collect()
    
    assert processes is not None
    assert len(processes) <= 5
    
    if processes:
        proc = processes[0]
        assert proc.name
        assert proc.pid >= 0  # PID 0 is valid on Windows (System Idle Process)
        assert proc.cpu_percent >= 0


@pytest.mark.asyncio
async def test_context_collector():
    """Test Context collector"""
    collector = ContextCollector()
    context = await collector.collect()
    
    assert context is not None
    assert context.time_of_day in ['morning', 'afternoon', 'evening', 'night']
    assert context.day_of_week
    assert isinstance(context.user_active, bool)


@pytest.mark.asyncio
async def test_collector_enable_disable():
    """Test collector enable/disable"""
    collector = CPUCollector()
    
    # Should be enabled by default
    assert collector.enabled
    
    # Disable
    collector.disable()
    assert not collector.enabled
    
    # Safe collect should return None when disabled
    result = await collector.safe_collect()
    assert result is None
    
    # Re-enable
    collector.enable()
    assert collector.enabled
    
    # Should work again
    result = await collector.safe_collect()
    assert result is not None
