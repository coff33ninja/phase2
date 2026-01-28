"""
End-to-end integration test
Tests the complete pipeline from collection to storage
"""
import pytest
import asyncio
from pathlib import Path
from config import Config
from aggregator import Pipeline


@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    """Test complete pipeline end-to-end"""
    # Setup test configuration
    config = Config.load()
    config.storage.database_path = Path("./test_data/test_e2e.db")
    
    pipeline = Pipeline(config)
    
    try:
        # Initialize pipeline
        await pipeline.initialize()
        
        # Collect and store multiple snapshots
        snapshot_ids = []
        for i in range(3):
            snapshot_id = await pipeline.collect_and_store()
            snapshot_ids.append(snapshot_id)
            await asyncio.sleep(0.1)
        
        # Verify all snapshots were stored
        assert len(snapshot_ids) == 3
        assert all(sid > 0 for sid in snapshot_ids)
        
        # Get statistics
        stats = await pipeline.get_statistics()
        assert stats['total_snapshots'] >= 3
        
        # Get recent snapshots
        recent = await pipeline.repository.get_recent_snapshots(limit=5)
        assert len(recent) >= 3
        
        # Verify data integrity
        for snapshot in recent:
            assert 'timestamp' in snapshot
            assert 'cpu_usage' in snapshot
            assert 'ram_usage' in snapshot
        
        print("✓ End-to-end test passed!")
    
    finally:
        await pipeline.shutdown()
        
        # Cleanup
        if config.storage.database_path.exists():
            config.storage.database_path.unlink()
        if config.storage.database_path.parent.exists():
            try:
                config.storage.database_path.parent.rmdir()
            except OSError:
                pass
