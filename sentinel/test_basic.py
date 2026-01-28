"""
Basic functionality test
Run this to verify the system works
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import with proper module structure
from config import Config
from aggregator.pipeline import Pipeline
from collectors import (
    CPUCollector,
    RAMCollector,
    GPUCollector,
    DiskCollector,
    NetworkCollector,
    ProcessCollector,
    ContextCollector
)


async def test_collectors():
    """Test all collectors"""
    print("=" * 60)
    print("Testing Individual Collectors")
    print("=" * 60)
    
    # Test CPU
    print("\n[CPU Collector]")
    cpu = CPUCollector()
    cpu_metrics = await cpu.collect()
    print(f"  Usage: {cpu_metrics.usage_percent:.1f}%")
    print(f"  Frequency: {cpu_metrics.frequency_mhz:.0f} MHz")
    print(f"  Cores: {len(cpu_metrics.per_core_usage)}")
    
    # Test RAM
    print("\n[RAM Collector]")
    ram = RAMCollector()
    ram_metrics = await ram.collect()
    print(f"  Usage: {ram_metrics.usage_percent:.1f}%")
    print(f"  Used: {ram_metrics.used_gb:.2f} GB")
    print(f"  Available: {ram_metrics.available_gb:.2f} GB")
    
    # Test GPU
    print("\n[GPU Collector]")
    gpu = GPUCollector()
    gpu_metrics = await gpu.collect()
    if gpu_metrics:
        for idx, g in enumerate(gpu_metrics):
            print(f"  GPU {idx}: {g.name}")
            print(f"    Usage: {g.usage_percent:.1f}%")
            print(f"    Memory: {g.memory_used_gb:.2f}/{g.memory_total_gb:.2f} GB")
    else:
        print("  No GPU detected or GPU tools not available")
    
    # Test Disk
    print("\n[Disk Collector]")
    disk = DiskCollector()
    disk_metrics = await disk.collect()
    print(f"  Read: {disk_metrics.read_mbps:.2f} MB/s")
    print(f"  Write: {disk_metrics.write_mbps:.2f} MB/s")
    
    # Test Network
    print("\n[Network Collector]")
    network = NetworkCollector()
    network_metrics = await network.collect()
    print(f"  Download: {network_metrics.download_mbps:.2f} MB/s")
    print(f"  Upload: {network_metrics.upload_mbps:.2f} MB/s")
    print(f"  Active Connections: {network_metrics.connections_active}")
    
    # Test Process
    print("\n[Process Collector]")
    process = ProcessCollector(top_n=5)
    processes = await process.collect()
    print(f"  Top {len(processes)} processes by CPU:")
    for p in processes[:5]:
        print(f"    {p.name}: {p.cpu_percent:.1f}% CPU, {p.memory_mb:.1f} MB RAM")
    
    # Test Context
    print("\n[Context Collector]")
    context = ContextCollector()
    context_metrics = await context.collect()
    print(f"  Time of Day: {context_metrics.time_of_day}")
    print(f"  Day of Week: {context_metrics.day_of_week}")
    print(f"  User Active: {context_metrics.user_active}")
    print(f"  User Action: {context_metrics.user_action or 'None detected'}")


async def test_pipeline():
    """Test the full pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline")
    print("=" * 60)
    
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        print("\n✓ Pipeline initialized")
        
        # Collect once
        print("\nCollecting snapshot...")
        snapshot = await pipeline.collect_once()
        print(f"✓ Snapshot collected at {snapshot.timestamp}")
        
        # Store in database
        print("\nStoring in database...")
        snapshot_id = await pipeline.collect_and_store()
        print(f"✓ Stored with ID: {snapshot_id}")
        
        # Get statistics
        print("\nDatabase statistics:")
        stats = await pipeline.get_statistics()
        print(f"  Total snapshots: {stats['total_snapshots']}")
        print(f"  Database size: {stats['database_size_mb']} MB")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    
    finally:
        await pipeline.shutdown()
        print("\n✓ Pipeline shutdown complete")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Phase 2.1 Foundation - Basic Functionality Test")
    print("=" * 60)
    
    try:
        # Test collectors
        await test_collectors()
        
        # Test pipeline
        await test_pipeline()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python main.py collect")
        print("2. Run: python main.py monitor")
        print("3. Run: python main.py status")
        print("4. See USAGE.md for more examples")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
