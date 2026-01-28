"""
Queue management for async data processing
Manages queues for data collection and storage
"""
import asyncio
from typing import Any, Optional, Callable
from loguru import logger


class QueueManager:
    """Manage async queues for data processing"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._workers: list[asyncio.Task] = []
        self._running = False
    
    async def put(self, item: Any):
        """Add item to queue"""
        try:
            await self.queue.put(item)
        except asyncio.QueueFull:
            logger.warning("Queue is full, dropping item")
    
    async def get(self) -> Any:
        """Get item from queue"""
        return await self.queue.get()
    
    def task_done(self):
        """Mark task as done"""
        self.queue.task_done()
    
    async def start_workers(
        self,
        worker_func: Callable,
        num_workers: int = 3
    ):
        """Start worker tasks to process queue"""
        self._running = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(
                self._worker(worker_func, i)
            )
            self._workers.append(worker)
        
        logger.info(f"Started {num_workers} queue workers")
    
    async def _worker(self, worker_func: Callable, worker_id: int):
        """Worker task that processes queue items"""
        logger.debug(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Get item with timeout
                item = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                
                # Process item
                try:
                    await worker_func(item)
                except Exception as e:
                    logger.error(f"Worker {worker_id} error processing item: {e}")
                finally:
                    self.queue.task_done()
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.debug(f"Worker {worker_id} stopped")
    
    async def stop_workers(self):
        """Stop all worker tasks"""
        self._running = False
        
        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        
        logger.info("All queue workers stopped")
    
    async def wait_empty(self):
        """Wait for queue to be empty"""
        await self.queue.join()
    
    def qsize(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()
    
    def is_full(self) -> bool:
        """Check if queue is full"""
        return self.queue.full()
