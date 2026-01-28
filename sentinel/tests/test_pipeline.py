"""
Unit tests for pipeline
"""
import pytest
import asyncio
from pathlib import Path
from config import Config
from aggregator import Pipeline


@pytest.fixture
async def test_pipeline():
    """Create a test pipeline"""
    config = Config.load()
    # Use test database
    config.storage.database_path = Path("./test_data/test_pipeline.db")
    
    pipeline = Pipeline(config)
    await pipeline.initialize()
    
    yield pipeline
    
    await pipeline.shutdown()
    
    # Cleanup
    if config.storage.database_path.exists():
        config.storage.database_path.unlink()
    if config.storage.database_path.parent.exists():
        try:
            config.storage.database_path.parent.rmdir()
        except OSError:
            pass


@pytest.mark.asyncio
async def test_pipeline_initialization(test_pipeline):
    """Test pipeline initialization"""
    assert test_pipeline.database is not None
    assert test_pipeline.repository is not None


@pytest.mark.asyncio
async def test_collect_once(test_pipeline):
    """Test single data collection"""
    snapshot = await test_pipeline.collect_once()
    
    assert snapshot is not None
    assert snapshot.cpu is not None
    assert snapshot.ram is not None
    assert snapshot.disk is not None
    assert snapshot.network is not None
    assert snapshot.context is not None


@pytest.mark.asyncio
async def test_collect_and_store(test_pipeline):
    """Test collecting and storing data"""
    snapshot_id = await test_pipeline.collect_and_store()
    
    assert snapshot_id > 0


@pytest.mark.asyncio
async def test_pipeline_statistics(test_pipeline):
    """Test getting pipeline statistics"""
    # Collect some data first
    await test_pipeline.collect_and_store()
    
    stats = await test_pipeline.get_statistics()
    
    assert stats['total_snapshots'] > 0
