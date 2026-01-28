"""Rate limiting for Gemini API calls."""
import asyncio
from datetime import datetime, timedelta
from collections import deque
from typing import Tuple
from loguru import logger


class RateLimiter:
    """Rate limiter for API requests and tokens."""
    
    def __init__(
        self,
        max_requests_per_minute: int = 60,
        max_tokens_per_minute: int = 1000000
    ):
        """Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum requests per minute
            max_tokens_per_minute: Maximum tokens per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        
        self.request_times: deque = deque()
        self.token_usage: deque = deque()  # (timestamp, token_count)
        
        self._lock = asyncio.Lock()
    
    async def acquire(self, token_count: int = 0):
        """Acquire permission to make a request.
        
        Args:
            token_count: Number of tokens for this request
        """
        async with self._lock:
            now = datetime.now()
            
            # Clean old entries
            self._clean_old_entries(now)
            
            # Check if we need to wait
            wait_time = self._calculate_wait_time(now, token_count)
            
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                now = datetime.now()
                self._clean_old_entries(now)
            
            # Record this request
            self.request_times.append(now)
            if token_count > 0:
                self.token_usage.append((now, token_count))
    
    def _clean_old_entries(self, now: datetime):
        """Remove entries older than 1 minute.
        
        Args:
            now: Current timestamp
        """
        cutoff = now - timedelta(minutes=1)
        
        # Clean request times
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()
        
        # Clean token usage
        while self.token_usage and self.token_usage[0][0] < cutoff:
            self.token_usage.popleft()
    
    def _calculate_wait_time(self, now: datetime, token_count: int) -> float:
        """Calculate how long to wait before making request.
        
        Args:
            now: Current timestamp
            token_count: Tokens for this request
            
        Returns:
            Wait time in seconds
        """
        wait_times = []
        
        # Check request rate
        if len(self.request_times) >= self.max_requests_per_minute:
            oldest_request = self.request_times[0]
            time_since_oldest = (now - oldest_request).total_seconds()
            wait_times.append(60 - time_since_oldest)
        
        # Check token rate
        if token_count > 0:
            current_tokens = sum(count for _, count in self.token_usage)
            if current_tokens + token_count > self.max_tokens_per_minute:
                # Need to wait for oldest tokens to expire
                if self.token_usage:
                    oldest_token_time = self.token_usage[0][0]
                    time_since_oldest = (now - oldest_token_time).total_seconds()
                    wait_times.append(60 - time_since_oldest)
        
        return max(wait_times) if wait_times else 0
    
    def get_current_usage(self) -> Tuple[int, int]:
        """Get current usage statistics.
        
        Returns:
            Tuple of (requests_in_last_minute, tokens_in_last_minute)
        """
        now = datetime.now()
        self._clean_old_entries(now)
        
        requests = len(self.request_times)
        tokens = sum(count for _, count in self.token_usage)
        
        return requests, tokens
