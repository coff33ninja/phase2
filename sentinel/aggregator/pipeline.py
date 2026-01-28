"""
Main data collection pipeline
Orchestrates all collectors and stores data
"""
import asyncio
from datetime import datetime
from typing import List, Optional
from loguru import logger

from collectors import (
    CPUCollector, RAMCollector, GPUCollector,
    DiskCollector, NetworkCollector, ProcessCollector, ContextCollector
)
from storage import Database, Repository
from models import SystemSnapshot
from config import Config


class Pipeline:
    """Main data collection and aggregation pipeline"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize collectors
        self.cpu_collector = CPUCollector()
        self.ram_collector = RAMCollector()
        self.gpu_collector = GPUCollector()
        self.disk_collector = DiskCollector()
        self.network_collector = NetworkCollector()
        self.process_collector = ProcessCollector(top_n=10)
        self.context_collector = ContextCollector()
        
        # Initialize storage
        self.database = Database(config.storage.database_path)
        self.repository = Repository(self.database)
        
        # Pipeline state
        self.running = False
        self._collection_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the pipeline"""
        await self.database.connect()
        logger.info("Pipeline initialized")
    
    async def shutdown(self):
        """Shutdown the pipeline"""
        self.running = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        await self.database.disconnect()
        logger.info("Pipeline shutdown complete")
    
    async def collect_once(self) -> SystemSnapshot:
        """Collect data once from all collectors"""
        try:
            # Collect from all sources concurrently
            cpu_task = self.cpu_collector.safe_collect()
            ram_task = self.ram_collector.safe_collect()
            gpu_task = self.gpu_collector.safe_collect()
            disk_task = self.disk_collector.safe_collect()
            network_task = self.network_collector.safe_collect()
            process_task = self.process_collector.safe_collect()
            context_task = self.context_collector.safe_collect()
            
            # Wait for all collectors
            results = await asyncio.gather(
                cpu_task, ram_task, gpu_task, disk_task,
                network_task, process_task, context_task
            )
            
            cpu, ram, gpu, disk, network, processes, context = results
            
            # Create snapshot
            snapshot = SystemSnapshot(
                timestamp=datetime.utcnow(),
                cpu=cpu,
                ram=ram,
                gpu=gpu,
                disk=disk,
                network=network,
                processes=processes or [],
                context=context
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            raise
    
    async def collect_and_store(self) -> int:
        """Collect data and store in database"""
        snapshot = await self.collect_once()
        snapshot_id = await self.repository.save_snapshot(snapshot)
        return snapshot_id
    
    async def start_continuous_collection(self, interval_seconds: int = 1):
        """Start continuous data collection"""
        self.running = True
        logger.info(f"Starting continuous collection (interval: {interval_seconds}s)")
        
        while self.running:
            try:
                await self.collect_and_store()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def start(self):
        """Start the pipeline in background"""
        await self.initialize()
        
        interval = self.config.intervals.high_frequency
        self._collection_task = asyncio.create_task(
            self.start_continuous_collection(interval)
        )
        
        logger.info("Pipeline started")
    
    async def get_statistics(self):
        """Get pipeline statistics"""
        return await self.repository.get_statistics()
