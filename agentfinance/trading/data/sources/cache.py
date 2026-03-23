"""
Market Data Caching Layer
==========================
Multi-tier caching for OHLCV and market data:

1. Redis (primary) — TTL-based key/value store
2. Filesystem (fallback) — JSON files with TTL checks

Cache TTLs by timeframe:
- M15:  2 minutes
- M5:   2 minutes
- H1:   10 minutes
- H4:   10 minutes
- D:    1 hour
- W:    6 hours
"""

import hashlib
import json
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# TTL Configuration
# ─────────────────────────────────────────────


TTL_SECONDS = {
    "M5": 120,  # 2 minutes
    "M15": 120,  # 2 minutes
    "M30": 300,  # 5 minutes
    "H1": 600,  # 10 minutes
    "H4": 600,  # 10 minutes
    "D": 3600,  # 1 hour
    "W": 21600,  # 6 hours
}

DEFAULT_TTL = 300  # 5 minutes


def get_ttl(timeframe: str) -> int:
    """Get TTL in seconds for a given timeframe."""
    return TTL_SECONDS.get(timeframe.upper(), DEFAULT_TTL)


# ─────────────────────────────────────────────
# Cache Key Builder
# ─────────────────────────────────────────────


def build_cache_key(
    source: str,
    symbol: str,
    timeframe: str,
    params: Optional[Dict] = None,
) -> str:
    """
    Build a deterministic cache key from source, symbol, timeframe, and params.

    Example: "oanda:EURUSD:H1:{'count':500}"
    """
    param_str = ""
    if params:
        # Sort keys for determinism
        sorted_params = sorted(params.items())
        param_str = str(sorted_params)
    raw = f"{source}:{symbol}:{timeframe}:{param_str}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


# ─────────────────────────────────────────────
# Redis Cache Backend
# ─────────────────────────────────────────────


class RedisCache:
    """Redis-backed cache with TTL support."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._client = None
        self._host = host
        self._port = port
        self._db = db
        self._available = None

    @property
    def available(self) -> bool:
        """Check if Redis is available (lazy)."""
        if self._available is None:
            try:
                import redis

                self._client = redis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                    decode_responses=False,  # We use pickle
                )
                self._client.ping()
                self._available = True
                logger.info(f"Redis cache connected at {self._host}:{self._port}")
            except Exception as e:
                self._available = False
                self._client = None
                logger.debug(f"Redis not available: {e}")
        return self._available

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.available:
            return None
        try:
            data = self._client.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Redis get failed for {key}: {e}")
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in Redis cache with TTL."""
        if not self.available:
            return False
        try:
            data = pickle.dumps(value)
            if ttl:
                self._client.setex(key, ttl, data)
            else:
                self._client.set(key, data)
            return True
        except Exception as e:
            logger.warning(f"Redis set failed for {key}: {e}")
        return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not self.available:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception:
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self.available:
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis clear_pattern failed: {e}")
        return 0


# ─────────────────────────────────────────────
# Filesystem Cache Backend
# ─────────────────────────────────────────────


class FilesystemCache:
    """
    Filesystem-backed cache as fallback when Redis is unavailable.
    Stores JSON files in a cache directory with TTL metadata.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.dirname(__file__),
                "../../../.cache/market_data",
            )
        self.cache_dir = Path(cache_dir).expanduser().resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Filesystem cache directory: {self.cache_dir}")

    def _key_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def _meta_path(self, key: str) -> Path:
        """Get the metadata path for a cache key."""
        return self.cache_dir / f"{key}.meta"

    def get(self, key: str) -> Optional[Any]:
        """Get value from filesystem cache if not expired."""
        data_path = self._key_path(key)
        meta_path = self._meta_path(key)

        if not data_path.exists() or not meta_path.exists():
            return None

        try:
            # Check TTL
            meta = json.loads(meta_path.read_text())
            expires_at = meta.get("expires_at", 0)
            if datetime.now().timestamp() > expires_at:
                # Expired — clean up
                data_path.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return None

            # Load data
            data = json.loads(data_path.read_text())
            return data

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"FilesystemCache get failed for {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in filesystem cache with TTL."""
        if ttl is None:
            ttl = DEFAULT_TTL

        try:
            data_path = self._key_path(key)
            meta_path = self._meta_path(key)

            # Write data
            data_path.write_text(json.dumps(value))

            # Write metadata
            meta = {
                "created_at": datetime.now().isoformat(),
                "expires_at": datetime.now().timestamp() + ttl,
                "ttl": ttl,
            }
            meta_path.write_text(json.dumps(meta))

            return True

        except OSError as e:
            logger.warning(f"FilesystemCache set failed for {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from filesystem cache."""
        data_path = self._key_path(key)
        meta_path = self._meta_path(key)
        removed = False
        if data_path.exists():
            data_path.unlink()
            removed = True
        if meta_path.exists():
            meta_path.unlink()
        return removed

    def clear_expired(self) -> int:
        """Remove all expired cache entries. Returns count of removed files."""
        removed = 0
        now = datetime.now().timestamp()
        for meta_file in self.cache_dir.glob("*.meta"):
            try:
                meta = json.loads(meta_file.read_text())
                if now > meta.get("expires_at", 0):
                    key = meta_file.stem
                    data_file = self.cache_dir / f"{key}.json"
                    data_file.unlink(missing_ok=True)
                    meta_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, OSError):
                continue
        return removed


# ─────────────────────────────────────────────
# Unified Cache Layer
# ─────────────────────────────────────────────


class MarketDataCache:
    """
    Unified caching layer with Redis primary and filesystem fallback.

    Usage:
        cache = MarketDataCache()

        # Try to get cached data
        data = cache.get("oanda", "EURUSD", "H1", {"count": 500})
        if data is None:
            data = fetch_from_api()
            cache.set("oanda", "EURUSD", "H1", {"count": 500}, data)

        # Also supports direct key access:
        key = cache.build_key("oanda", "EURUSD", "H1")
        cache.set_direct(key, data, ttl=600)
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        cache_dir: Optional[str] = None,
    ):
        self.redis = RedisCache(host=redis_host, port=redis_port, db=redis_db)
        self.fs = FilesystemCache(cache_dir=cache_dir)
        self._backend = None

    @property
    def backend(self) -> str:
        """Which backend is currently active."""
        if self._backend is None:
            self._backend = "redis" if self.redis.available else "filesystem"
        return self._backend

    def build_key(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        params: Optional[Dict] = None,
    ) -> str:
        """Build a cache key."""
        return build_cache_key(source, symbol, timeframe, params)

    def get(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        params: Optional[Dict] = None,
    ) -> Optional[Any]:
        """Get cached data for a market data request."""
        key = self.build_key(source, symbol, timeframe, params)
        return self.get_direct(key)

    def set(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        params: Optional[Dict],
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache market data with appropriate TTL."""
        if ttl is None:
            ttl = get_ttl(timeframe)
        key = self.build_key(source, symbol, timeframe, params)
        return self.set_direct(key, value, ttl)

    def get_direct(self, key: str) -> Optional[Any]:
        """Get value by direct key access."""
        # Try Redis first
        if self.redis.available:
            result = self.redis.get(key)
            if result is not None:
                logger.debug(f"CACHE HIT (redis): {key}")
                return result

        # Fall back to filesystem
        result = self.fs.get(key)
        if result is not None:
            logger.debug(f"CACHE HIT (fs): {key}")
        return result

    def set_direct(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value with direct key access."""
        # Always write to filesystem as backup
        fs_ok = self.fs.set(key, value, ttl)

        # Try Redis as primary
        if self.redis.available:
            redis_ok = self.redis.set(key, value, ttl)
            if redis_ok:
                logger.debug(f"CACHE SET (redis): {key} TTL={ttl}s")
                return True
            else:
                # Redis set failed but FS worked
                logger.debug(f"CACHE SET (fs only): {key} TTL={ttl}s")
                return fs_ok

        logger.debug(f"CACHE SET (fs fallback): {key} TTL={ttl}s")
        return fs_ok

    def delete(self, key: str) -> bool:
        """Delete a cache key from both backends."""
        redis_ok = self.redis.delete(key)
        fs_ok = self.fs.delete(key)
        return redis_ok or fs_ok

    def clear_source(self, source: str) -> int:
        """Clear all cached entries for a source."""
        pattern = f"*{source}*"
        redis_count = self.redis.clear_pattern(pattern)

        # For filesystem, clear by scanning
        fs_count = 0
        for meta_file in self.fs.cache_dir.glob("*.meta"):
            if source in meta_file.stem:
                key = meta_file.stem
                data_file = self.fs.cache_dir / f"{key}.json"
                data_file.unlink(missing_ok=True)
                meta_file.unlink()
                fs_count += 1

        total = redis_count + fs_count
        logger.info(f"Cleared {total} cache entries for source '{source}'")
        return total

    def clear_all(self) -> int:
        """Clear all cached entries."""
        redis_count = self.redis.clear_pattern("*")
        fs_count = 0
        for f in self.fs.cache_dir.glob("*"):
            if f.suffix in (".json", ".meta"):
                f.unlink()
                fs_count += 1
        total = redis_count + fs_count
        logger.info(f"Cleared {total} total cache entries")
        return total

    def cleanup_expired(self) -> int:
        """Remove expired entries from filesystem cache."""
        return self.fs.clear_expired()

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        stats = {
            "backend": self.backend,
            "redis_available": self.redis.available,
            "fs_cache_dir": str(self.fs.cache_dir),
            "fs_entries": 0,
        }

        # Count filesystem entries
        if self.fs.cache_dir.exists():
            stats["fs_entries"] = len(list(self.fs.cache_dir.glob("*.meta")))

        return stats


# ─────────────────────────────────────────────
# Convenience decorators
# ─────────────────────────────────────────────


def cached(
    source: str,
    timeframe: str,
    ttl: Optional[int] = None,
    params_key: Optional[str] = None,
):
    """
    Decorator to cache function results based on source/timeframe.

    Usage:
        @cached("oanda", "H1", ttl=600)
        def fetch_ohlcv(symbol, timeframe, count):
            ...
    """
    if ttl is None:
        ttl = get_ttl(timeframe)

    def decorator(func):
        cache = MarketDataCache()

        def wrapper(*args, **kwargs):
            # Build params from kwargs
            params = kwargs.copy()
            if params_key and len(args) > 0:
                params[params_key] = args[0]

            key = cache.build_key(
                source, str(args[0]) if args else "default", timeframe, params
            )

            # Try cache
            result = cache.get_direct(key)
            if result is not None:
                return result

            # Fetch fresh
            result = func(*args, **kwargs)
            if result is not None:
                cache.set_direct(key, result, ttl)
            return result

        return wrapper

    return decorator


# ─────────────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────────────

# Global cache instance — lazy initialization
_cache_instance: Optional[MarketDataCache] = None


def get_cache() -> MarketDataCache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MarketDataCache()
    return _cache_instance


if __name__ == "__main__":
    # Quick test
    cache = MarketDataCache()
    print(f"Cache backend: {cache.backend}")
    print(f"Cache stats: {cache.get_stats()}")

    # Test basic set/get
    test_key = cache.build_key("oanda", "EURUSD", "H1", {"count": 100})
    cache.set_direct(test_key, {"candles": 100, "test": True}, ttl=60)
    result = cache.get_direct(test_key)
    print(f"Test get: {result}")
    print(f"Cache stats after test: {cache.get_stats()}")
