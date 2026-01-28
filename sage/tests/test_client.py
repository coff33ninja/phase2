"""Tests for Gemini client."""
import pytest
from gemini_client.rate_limiter import RateLimiter
from gemini_client.token_counter import TokenCounter


class TestRateLimiter:
    """Test rate limiter."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(max_requests_per_minute=60, max_tokens_per_minute=1000000)
        assert limiter.max_requests_per_minute == 60
        assert limiter.max_tokens_per_minute == 1000000
    
    @pytest.mark.asyncio
    async def test_acquire_no_wait(self):
        """Test acquiring without waiting."""
        limiter = RateLimiter(max_requests_per_minute=60)
        await limiter.acquire(100)
        
        requests, tokens = limiter.get_current_usage()
        assert requests == 1
        assert tokens == 100
    
    @pytest.mark.asyncio
    async def test_current_usage(self):
        """Test getting current usage."""
        limiter = RateLimiter()
        
        await limiter.acquire(100)
        await limiter.acquire(200)
        
        requests, tokens = limiter.get_current_usage()
        assert requests == 2
        assert tokens == 300


class TestTokenCounter:
    """Test token counter."""
    
    def test_count_tokens(self):
        """Test token counting."""
        counter = TokenCounter()
        
        text = "This is a test message"
        tokens = counter.count_tokens(text)
        
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_count_tokens_batch(self):
        """Test batch token counting."""
        counter = TokenCounter()
        
        texts = ["Hello world", "Test message", "Another text"]
        counts = counter.count_tokens_batch(texts)
        
        assert len(counts) == 3
        assert all(count > 0 for count in counts)
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        counter = TokenCounter()
        
        cost = counter.estimate_cost(
            input_tokens=1000,
            output_tokens=500,
            input_price_per_million=0.30,
            output_price_per_million=2.50
        )
        
        assert cost > 0
        assert isinstance(cost, float)
        # 1000 * 0.30 / 1M + 500 * 2.50 / 1M = 0.0003 + 0.00125 = 0.00155
        assert abs(cost - 0.00155) < 0.0001
