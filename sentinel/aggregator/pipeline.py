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
    DiskCollector, NetworkCollector, ProcessCollector, ContextCollector,
    TemperatureCollector, AIDA64Collector, HWiNFOCollector
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
        self.temperature_collector = TemperatureCollector()
        
        # Initialize AIDA64 collector if enabled
        self.aida64_collector = None
        if config.aida64.enabled:
            self.aida64_collector = AIDA64Collector(
                report_path=config.aida64.report_path
            )
            logger.info("AIDA64 collector enabled")
        
        # Initialize HWiNFO collector if enabled
        self.hwinfo_collector = None
        if config.hwinfo.enabled:
            self.hwinfo_collector = HWiNFOCollector()
            logger.info("HWiNFO64 collector enabled")
        
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
            tasks = [
                self.cpu_collector.safe_collect(),
                self.ram_collector.safe_collect(),
                self.gpu_collector.safe_collect(),
                self.disk_collector.safe_collect(),
                self.network_collector.safe_collect(),
                self.process_collector.safe_collect(),
                self.context_collector.safe_collect(),
                self.temperature_collector.safe_collect()
            ]
            
            # Add AIDA64 collector if enabled
            if self.aida64_collector:
                tasks.append(self.aida64_collector.safe_collect())
            
            # Add HWiNFO collector if enabled
            if self.hwinfo_collector:
                tasks.append(self.hwinfo_collector.safe_collect())
            
            # Wait for all collectors
            results = await asyncio.gather(*tasks)
            
            # Unpack results
            cpu = results[0]
            ram = results[1]
            gpu = results[2]
            disk = results[3]
            network = results[4]
            processes = results[5]
            context = results[6]
            temperatures = results[7]
            
            # Get optional collector results
            result_index = 8
            aida64_data = None
            hwinfo_data = None
            
            if self.aida64_collector:
                aida64_data = results[result_index]
                result_index += 1
            
            if self.hwinfo_collector:
                hwinfo_data = results[result_index]
                result_index += 1
            
            # Merge temperature data from AIDA64 if available
            if aida64_data and 'sensors' in aida64_data:
                if temperatures is None:
                    temperatures = {}
                temperatures['aida64'] = aida64_data['sensors']
                logger.debug(f"AIDA64 sensors: {len(aida64_data['sensors'])} readings")
            
            # Merge temperature data from HWiNFO if available
            if hwinfo_data:
                if temperatures is None:
                    temperatures = {}
                temperatures['hwinfo'] = hwinfo_data
                logger.debug(f"HWiNFO sensors: {len(hwinfo_data.get('temperatures', {}))} temperature readings")
            
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
