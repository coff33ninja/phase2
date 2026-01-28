"""
Base collector class
All collectors inherit from this
"""
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger


class BaseCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        logger.debug(f"Initialized collector: {name}")
    
    @abstractmethod
    async def collect(self) -> Any:
        """
        Collect data from the source
        Must be implemented by subclasses
        """
        pass
    
    def enable(self):
        """Enable this collector"""
        self.enabled = True
        logger.info(f"Enabled collector: {self.name}")
    
    def disable(self):
        """Disable this collector"""
        self.enabled = False
        logger.info(f"Disabled collector: {self.name}")
    
    async def safe_collect(self) -> Any:
        """
        Safely collect data with error handling
        """
        if not self.enabled:
            return None
        
        try:
            return await self.collect()
        except Exception as e:
            logger.error(f"Error in collector {self.name}: {e}")
            return None
