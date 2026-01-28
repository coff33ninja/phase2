"""
Ring buffer implementation
Circular buffer for efficient data storage
"""
from typing import Generic, TypeVar, List, Optional
from collections import deque

T = TypeVar('T')


class RingBuffer(Generic[T]):
    """
    Fixed-size circular buffer
    Automatically overwrites oldest data when full
    """
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self._buffer: deque = deque(maxlen=capacity)
    
    def append(self, item: T):
        """Add item to buffer"""
        self._buffer.append(item)
    
    def extend(self, items: List[T]):
        """Add multiple items to buffer"""
        self._buffer.extend(items)
    
    def get(self, index: int) -> Optional[T]:
        """Get item at index (0 = oldest, -1 = newest)"""
        try:
            return self._buffer[index]
        except IndexError:
            return None
    
    def get_all(self) -> List[T]:
        """Get all items in buffer (oldest to newest)"""
        return list(self._buffer)
    
    def get_recent(self, n: int) -> List[T]:
        """Get n most recent items"""
        if n >= len(self._buffer):
            return list(self._buffer)
        return list(self._buffer)[-n:]
    
    def clear(self):
        """Clear all items from buffer"""
        self._buffer.clear()
    
    def is_full(self) -> bool:
        """Check if buffer is at capacity"""
        return len(self._buffer) == self.capacity
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self._buffer) == 0
    
    def __len__(self) -> int:
        """Get current number of items"""
        return len(self._buffer)
    
    def __iter__(self):
        """Iterate over items (oldest to newest)"""
        return iter(self._buffer)
    
    def __repr__(self) -> str:
        return f"RingBuffer(capacity={self.capacity}, size={len(self._buffer)})"
