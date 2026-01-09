"""
CardForge Base API Client
Async HTTP client with rate limiting and caching
"""

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TypeVar, Generic
import aiohttp
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type
)

T = TypeVar('T')


class RateLimiter:
    """Token bucket rate limiter for API requests."""
    
    def __init__(
        self, 
        requests_per_second: float = 10.0,
        burst_size: int = 10
    ):
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class CacheEntry:
    """Cache entry with TTL."""
    
    def __init__(self, data: Any, ttl: timedelta):
        self.data = data
        self.expires_at = datetime.now() + ttl
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class InMemoryCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
    
    def _make_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from URL and params."""
        key_data = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached value if not expired."""
        key = self._make_key(url, params)
        entry = self._cache.get(key)
        
        if entry and not entry.is_expired:
            return entry.data
        elif entry:
            del self._cache[key]
        
        return None
    
    def set(
        self, 
        url: str, 
        data: Any, 
        ttl: timedelta = timedelta(hours=1),
        params: Optional[Dict] = None
    ):
        """Cache a value."""
        # Evict if at capacity
        if len(self._cache) >= self._max_size:
            # Remove expired entries first
            expired = [k for k, v in self._cache.items() if v.is_expired]
            for k in expired:
                del self._cache[k]
            
            # If still at capacity, remove oldest
            if len(self._cache) >= self._max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].expires_at
                )
                del self._cache[oldest_key]
        
        key = self._make_key(url, params)
        self._cache[key] = CacheEntry(data, ttl)
    
    def invalidate(self, url: str, params: Optional[Dict] = None):
        """Remove a cached value."""
        key = self._make_key(url, params)
        self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cached values."""
        self._cache.clear()


class BaseAPIClient(ABC):
    """
    Base async API client with rate limiting and caching.
    
    All CardForge API clients inherit from this.
    """
    
    base_url: str
    rate_limit: float = 10.0  # requests per second
    cache_ttl: timedelta = timedelta(hours=1)
    
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        cache: Optional[InMemoryCache] = None,
    ):
        self._session = session
        self._own_session = session is None
        self._cache = cache or InMemoryCache()
        self._rate_limiter = RateLimiter(self.rate_limit)
        self._headers = {
            'User-Agent': 'CardForge/1.0 (MTG Collection Manager)',
            'Accept': 'application/json',
        }
    
    async def __aenter__(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self._session:
            await self._session.close()
            self._session = None
    
    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._session
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_cache: bool = True,
        cache_ttl: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with rate limiting and caching."""
        url = f"{self.base_url}{endpoint}"
        
        # Check cache for GET requests
        if method.upper() == 'GET' and use_cache:
            cached = self._cache.get(url, params)
            if cached is not None:
                return cached
        
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        # Make request
        request_headers = {**self._headers, **(headers or {})}
        
        async with self.session.request(
            method,
            url,
            params=params,
            json=data,
            headers=request_headers,
        ) as response:
            response.raise_for_status()
            result = await response.json()
        
        # Cache GET responses
        if method.upper() == 'GET' and use_cache:
            self._cache.set(
                url, 
                result, 
                ttl=cache_ttl or self.cache_ttl,
                params=params
            )
        
        return result
    
    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        use_cache: bool = True,
        cache_ttl: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request(
            'GET', endpoint, params=params, 
            use_cache=use_cache, cache_ttl=cache_ttl
        )
    
    async def post(
        self, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request(
            'POST', endpoint, params=params, data=data, use_cache=False
        )
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if API is reachable."""
        pass
