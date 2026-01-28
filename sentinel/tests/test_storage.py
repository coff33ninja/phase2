"""
Unit tests for storage layer
"""
import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from storage import Database, Repository
from models import (
    CPUMetrics, RAMMetrics, DiskMetrics, NetworkMetrics,
    SystemContext, SystemSnapshot
)


@pytest.fixture
async def test_db():
    """Create a test database"""
    db_path = Path("./test_data/test.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    db = Database(db_path)
    await db.connect()
    
    yield db
    
    await db.disconnect()
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    if db_path.parent.exists():
        db_path.parent.rmdir()


@pytest.mark.asyncio
async def test_database_connection(test_db):
    """Test database connection"""
    assert test_db._connection is not None


@pytest.mark.asyncio
async def test_save_snapshot(test_db):
    """Test saving a snapshot"""
    repo = Repository(test_db)
    
    # Create test snapshot
    snapshot = SystemSnapshot(
        timestamp=datetime.utcnow(),
        cpu=CPUMetrics(
            usage_percent=50.0,
            per_core_usage=[50.0, 55.0],
            frequency_mhz=3000.0
        ),
        ram=RAMMetrics(
            total_gb=16.0,
            used_gb=8.0,
            available_gb=8.0,
            usage_percent=50.0
        ),
        disk=DiskMetrics(
            read_mbps=100.0,
            write_mbps=50.0,
            queue_length=0
        ),
        network=NetworkMetrics(
            download_mbps=10.0,
            upload_mbps=5.0,
            connections_active=25
        ),
        context=SystemContext(
            user_active=True,
            time_of_day="afternoon",
            day_of_week="Monday"
        )
    )
    
    # Save snapshot
    snapshot_id = await repo.save_snapshot(snapshot)
    
    assert snapshot_id > 0


@pytest.mark.asyncio
async def test_get_recent_snapshots(test_db):
    """Test retrieving recent snapshots"""
    repo = Repository(test_db)
    
    # Save a snapshot first
    snapshot = SystemSnapshot(
        timestamp=datetime.utcnow(),
        cpu=CPUMetrics(usage_percent=50.0, per_core_usage=[], frequency_mhz=3000.0),
        ram=RAMMetrics(total_gb=16.0, used_gb=8.0, available_gb=8.0, usage_percent=50.0),
        disk=DiskMetrics(read_mbps=100.0, write_mbps=50.0, queue_length=0),
        network=NetworkMetrics(download_mbps=10.0, upload_mbps=5.0, connections_active=25),
        context=SystemContext(user_active=True, time_of_day="afternoon", day_of_week="Monday")
    )
    
    await repo.save_snapshot(snapshot)
    
    # Retrieve snapshots
    snapshots = await repo.get_recent_snapshots(limit=10)
    
    assert len(snapshots) > 0
    assert 'cpu_usage' in snapshots[0]


@pytest.mark.asyncio
async def test_database_statistics(test_db):
    """Test database statistics"""
    repo = Repository(test_db)
    
    stats = await repo.get_statistics()
    
    assert 'total_snapshots' in stats
    assert 'database_size_mb' in stats
    assert isinstance(stats['total_snapshots'], int)
