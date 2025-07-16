"""Unit tests for rate limiter implementation."""

import asyncio
import time
import pytest
from app.services.rate_limiter import TokenBucket, PolygonRateLimiter, ExponentialBackoff


class TestTokenBucket:
    """Test TokenBucket rate limiting algorithm."""
    
    @pytest.mark.asyncio
    async def test_token_bucket_basic(self):
        """Test basic token bucket functionality."""
        # Create bucket with 5 tokens, refill 2 per second
        bucket = TokenBucket(capacity=5, refill_rate=2)
        
        # Should be able to consume 5 tokens immediately
        for i in range(5):
            assert await bucket.consume(1) is True
            
        # 6th request should fail (no tokens left)
        assert await bucket.consume(1) is False
        
        # Wait for refill
        await asyncio.sleep(1)
        
        # Should have ~2 tokens now
        assert await bucket.consume(1) is True
        assert await bucket.consume(1) is True
        assert await bucket.consume(1) is False
    
    @pytest.mark.asyncio
    async def test_token_bucket_wait(self):
        """Test waiting for tokens."""
        bucket = TokenBucket(capacity=2, refill_rate=1)
        
        # Consume all tokens
        assert await bucket.consume(2) is True
        
        # Measure wait time for next token
        start = time.time()
        assert await bucket.consume(1, wait=True) is True
        elapsed = time.time() - start
        
        # Should have waited ~1 second for refill
        assert 0.9 < elapsed < 1.2
    
    def test_token_bucket_stats(self):
        """Test token bucket statistics."""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        
        stats = bucket.stats
        assert stats['capacity'] == 10
        assert stats['refill_rate'] == 5
        assert stats['current_tokens'] == 10
        assert stats['total_requests'] == 0
        assert stats['average_rate'] == 0


class TestPolygonRateLimiter:
    """Test Polygon-specific rate limiter."""
    
    @pytest.mark.asyncio
    async def test_polygon_free_tier_limits(self):
        """Test Polygon free tier rate limits (5 req/min)."""
        limiter = PolygonRateLimiter()
        
        # Should allow 5 requests
        for i in range(5):
            await limiter.acquire()
        
        # 6th request should wait
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start
        
        # Should have waited for token refill
        assert elapsed > 0.1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_with_429_error(self):
        """Test handling 429 rate limit errors."""
        limiter = PolygonRateLimiter()
        
        # Simulate 429 error
        limiter.handle_429_error()
        
        # Should wait longer on next acquire
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start
        
        # Should have extra delay
        assert elapsed > 0.5


class TestExponentialBackoff:
    """Test exponential backoff for retries."""
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_sequence(self):
        """Test exponential backoff delay sequence."""
        backoff = ExponentialBackoff(base_delay=1, max_delay=10)
        
        # Test delay sequence: 1, 2, 4, 8, 10 (capped)
        expected_delays = [1, 2, 4, 8, 10]
        
        for i, expected in enumerate(expected_delays):
            delay = backoff.get_delay(i + 1)
            assert delay == expected
    
    @pytest.mark.asyncio
    async def test_backoff_with_jitter(self):
        """Test backoff with jitter."""
        backoff = ExponentialBackoff(base_delay=1, max_delay=10, jitter=True)
        
        # With jitter, delays should vary
        delays = [backoff.get_delay(3) for _ in range(10)]
        
        # All should be around 4 seconds (2^2) but with variation
        assert all(3 < d < 5 for d in delays)
        assert len(set(delays)) > 1  # Should have variation
    
    @pytest.mark.asyncio
    async def test_backoff_wait(self):
        """Test actual waiting with backoff."""
        backoff = ExponentialBackoff(base_delay=0.1, max_delay=1)
        
        start = time.time()
        await backoff.wait(attempt=2)
        elapsed = time.time() - start
        
        # Should wait ~0.2 seconds (0.1 * 2^1)
        assert 0.15 < elapsed < 0.25


@pytest.mark.asyncio
async def test_rate_limiter_integration():
    """Integration test for rate limiting in practice."""
    limiter = PolygonRateLimiter()
    backoff = ExponentialBackoff(base_delay=0.1)
    
    async def make_api_call(call_id: int):
        """Simulate an API call with rate limiting."""
        await limiter.acquire()
        return f"Response {call_id}"
    
    # Make 10 concurrent requests
    tasks = [make_api_call(i) for i in range(10)]
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    # Should have rate limited the requests
    assert len(results) == 10
    assert elapsed > 1.0  # Should take time due to rate limiting
    
    # Check stats
    stats = limiter.stats
    assert stats['total_requests'] == 10
    assert stats['average_rate'] < 5  # Should be under limit
