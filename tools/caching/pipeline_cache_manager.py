#!/usr/bin/env python3
"""
🏇 Pipeline Cache Manager - Phase 1C Intelligent Caching System

Implements Redis-based caching for expensive computations:
- Feature engineering results
- Database query results
- ML model predictions
- Race analysis aggregations

Author: AI Assistant
Date: August 15, 2025
Part of: Phase 1C - Intelligent Caching System
"""

import redis
import json
import pickle
import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    total_time_saved_ms: float = 0.0
    cache_size_mb: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage."""
        return 100.0 - self.hit_rate


class PipelineCacheManager:
    """
    🚀 Intelligent caching system for horse racing pipeline computations.
    
    Features:
    - Redis-based storage with automatic expiration
    - Feature engineering result caching
    - Database query result caching
    - ML prediction caching
    - Cache analytics and monitoring
    - Automatic cache invalidation strategies
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 3600  # 1 hour default TTL
    ):
        """
        Initialize the cache manager.
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            default_ttl: Default time-to-live in seconds
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.default_ttl = default_ttl
        
        # Cache key prefixes for different data types
        self.prefixes = {
            'features': 'cache:features:',
            'queries': 'cache:queries:',
            'predictions': 'cache:predictions:',
            'aggregations': 'cache:aggregations:',
            'race_data': 'cache:race_data:',
            'stats': 'cache:stats'
        }
        
        # Initialize Redis connection
        self._connect_redis()
        
        # Initialize cache statistics
        self.stats = CacheStats()
        self._load_stats()
        
        logger.info("🚀 Pipeline Cache Manager initialized")
        logger.info(f"📊 Current cache stats: {self.stats.hit_rate:.1f}% hit rate")
    
    def _connect_redis(self) -> None:
        """Establish Redis connection with error handling."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=False,  # Keep binary for pickle
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
            
        except redis.ConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("🔄 Falling back to in-memory cache (limited functionality)")
            self.redis_client = None
            self._fallback_cache = {}
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """
        Generate a unique cache key from arguments.
        
        Args:
            prefix: Cache key prefix
            *args: Arguments to include in key generation
            
        Returns:
            Unique cache key string
        """
        # Create a string representation of all arguments
        key_data = str(args)
        
        # Generate MD5 hash for consistent key length
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"{prefix}{key_hash}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage in Redis."""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"❌ Serialization error: {e}")
            return pickle.dumps(str(data))
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis storage."""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"❌ Deserialization error: {e}")
            return None
    
    def _load_stats(self) -> None:
        """Load cache statistics from Redis."""
        try:
            if self.redis_client:
                stats_data = self.redis_client.get(self.prefixes['stats'])
                if stats_data:
                    stats_dict = json.loads(stats_data.decode())
                    self.stats = CacheStats(**stats_dict)
        except Exception as e:
            logger.warning(f"⚠️ Could not load cache stats: {e}")
    
    def _save_stats(self) -> None:
        """Save cache statistics to Redis."""
        try:
            if self.redis_client:
                stats_dict = {
                    'hits': self.stats.hits,
                    'misses': self.stats.misses,
                    'total_requests': self.stats.total_requests,
                    'total_time_saved_ms': self.stats.total_time_saved_ms,
                    'cache_size_mb': self.stats.cache_size_mb
                }
                self.redis_client.set(
                    self.prefixes['stats'], 
                    json.dumps(stats_dict),
                    ex=86400  # Save stats for 24 hours
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not save cache stats: {e}")
    
    @contextmanager
    def cache_timing(self):
        """Context manager to measure cache operation timing."""
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        self.stats.total_time_saved_ms += elapsed_ms
    
    def get(
        self, 
        cache_type: str, 
        key_args: tuple, 
        default: Any = None
    ) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            cache_type: Type of cache ('features', 'queries', 'predictions', etc.)
            key_args: Arguments to generate cache key
            default: Default value if not found
            
        Returns:
            Cached data or default value
        """
        if cache_type not in self.prefixes:
            logger.error(f"❌ Invalid cache type: {cache_type}")
            return default
        
        cache_key = self._generate_cache_key(self.prefixes[cache_type], *key_args)
        
        try:
            if self.redis_client:
                with self.cache_timing():
                    data = self.redis_client.get(cache_key)
                    
                if data:
                    self.stats.hits += 1
                    self.stats.total_requests += 1
                    result = self._deserialize_data(data)
                    logger.debug(f"✅ Cache HIT: {cache_type} - {cache_key[:20]}...")
                    return result
                else:
                    self.stats.misses += 1
                    self.stats.total_requests += 1
                    logger.debug(f"❌ Cache MISS: {cache_type} - {cache_key[:20]}...")
                    return default
            else:
                # Fallback to in-memory cache
                if cache_key in self._fallback_cache:
                    self.stats.hits += 1
                    self.stats.total_requests += 1
                    return self._fallback_cache[cache_key]
                else:
                    self.stats.misses += 1
                    self.stats.total_requests += 1
                    return default
                    
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            self.stats.misses += 1
            self.stats.total_requests += 1
            return default
    
    def set(
        self, 
        cache_type: str, 
        key_args: tuple, 
        data: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store data in cache.
        
        Args:
            cache_type: Type of cache ('features', 'queries', 'predictions', etc.)
            key_args: Arguments to generate cache key
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if cache_type not in self.prefixes:
            logger.error(f"❌ Invalid cache type: {cache_type}")
            return False
        
        cache_key = self._generate_cache_key(self.prefixes[cache_type], *key_args)
        ttl = ttl or self.default_ttl
        
        try:
            if self.redis_client:
                serialized_data = self._serialize_data(data)
                success = self.redis_client.set(cache_key, serialized_data, ex=ttl)
                
                if success:
                    logger.debug(f"💾 Cache SET: {cache_type} - {cache_key[:20]}... (TTL: {ttl}s)")
                    return True
                else:
                    logger.error(f"❌ Failed to set cache: {cache_key[:20]}...")
                    return False
            else:
                # Fallback to in-memory cache
                self._fallback_cache[cache_key] = data
                logger.debug(f"💾 Fallback cache SET: {cache_type} - {cache_key[:20]}...")
                return True
                
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            return False
    
    def delete(self, cache_type: str, key_args: tuple) -> bool:
        """Delete specific cache entry."""
        if cache_type not in self.prefixes:
            logger.error(f"❌ Invalid cache type: {cache_type}")
            return False
        
        cache_key = self._generate_cache_key(self.prefixes[cache_type], *key_args)
        
        try:
            if self.redis_client:
                result = self.redis_client.delete(cache_key)
                logger.debug(f"🗑️  Cache DELETE: {cache_type} - {cache_key[:20]}...")
                return bool(result)
            else:
                if cache_key in self._fallback_cache:
                    del self._fallback_cache[cache_key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ Cache delete error: {e}")
            return False
    
    def invalidate_pattern(self, cache_type: str, pattern: str = "*") -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            cache_type: Type of cache to invalidate
            pattern: Redis pattern for key matching
            
        Returns:
            Number of keys deleted
        """
        if cache_type not in self.prefixes:
            logger.error(f"❌ Invalid cache type: {cache_type}")
            return 0
        
        try:
            if self.redis_client:
                search_pattern = f"{self.prefixes[cache_type]}{pattern}"
                keys = self.redis_client.keys(search_pattern)
                
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"🗑️  Invalidated {deleted} cache entries for {cache_type}")
                    return deleted
                return 0
            else:
                # Fallback cache invalidation
                prefix = self.prefixes[cache_type]
                keys_to_delete = [
                    k for k in self._fallback_cache.keys() 
                    if k.startswith(prefix)
                ]
                
                for key in keys_to_delete:
                    del self._fallback_cache[key]
                
                logger.info(f"🗑️  Invalidated {len(keys_to_delete)} fallback cache entries")
                return len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {e}")
            return 0
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information and statistics."""
        try:
            # Update stats
            self._save_stats()
            
            cache_info = {
                'connection_status': 'connected' if self.redis_client else 'fallback',
                'hit_rate_percent': round(self.stats.hit_rate, 2),
                'miss_rate_percent': round(self.stats.miss_rate, 2),
                'total_hits': self.stats.hits,
                'total_misses': self.stats.misses,
                'total_requests': self.stats.total_requests,
                'time_saved_ms': round(self.stats.total_time_saved_ms, 2),
                'default_ttl_seconds': self.default_ttl,
                'cache_types': list(self.prefixes.keys())
            }
            
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    cache_info.update({
                        'redis_version': info.get('redis_version', 'unknown'),
                        'used_memory_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
                        'connected_clients': info.get('connected_clients', 0),
                        'total_commands_processed': info.get('total_commands_processed', 0)
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Could not get Redis info: {e}")
            
            return cache_info
            
        except Exception as e:
            logger.error(f"❌ Error getting cache info: {e}")
            return {'error': str(e)}
    
    def clear_all_cache(self) -> bool:
        """Clear all pipeline cache data."""
        try:
            total_deleted = 0
            
            for cache_type in self.prefixes.keys():
                if cache_type != 'stats':  # Don't delete stats
                    deleted = self.invalidate_pattern(cache_type, "*")
                    total_deleted += deleted
            
            logger.info(f"🗑️  Cleared all cache data: {total_deleted} entries deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False


# Cache decorators for easy integration
def cached_feature_engineering(
    cache_manager: PipelineCacheManager,
    ttl: int = 3600
):
    """Decorator for caching feature engineering results."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_args = (func.__name__, args, tuple(sorted(kwargs.items())))
            
            # Try to get from cache first
            cached_result = cache_manager.get('features', cache_key_args)
            if cached_result is not None:
                logger.debug(f"🎯 Using cached features for {func.__name__}")
                return cached_result
            
            # Compute result and cache it
            logger.debug(f"🔧 Computing features for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set('features', cache_key_args, result, ttl)
            
            return result
        return wrapper
    return decorator


def cached_database_query(
    cache_manager: PipelineCacheManager,
    ttl: int = 1800  # 30 minutes for database queries
):
    """Decorator for caching database query results."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            cache_key_args = (func.__name__, args, tuple(sorted(kwargs.items())))
            
            cached_result = cache_manager.get('queries', cache_key_args)
            if cached_result is not None:
                logger.debug(f"🎯 Using cached query result for {func.__name__}")
                return cached_result
            
            logger.debug(f"🔍 Executing database query: {func.__name__}")
            result = func(*args, **kwargs)
            
            cache_manager.set('queries', cache_key_args, result, ttl)
            
            return result
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    print("🏇 Pipeline Cache Manager - Testing Mode")
    print("=" * 50)
    
    # Initialize cache manager
    cache_manager = PipelineCacheManager()
    
    # Test basic cache operations
    print("\n🧪 Testing basic cache operations...")
    
    # Test feature caching
    test_features = {
        'race_id': 'R123456',
        'features': [1.2, 3.4, 5.6, 7.8],
        'feature_names': ['speed', 'form', 'weight', 'odds']
    }
    
    # Cache some test data
    success = cache_manager.set('features', ('R123456', 'basic_features'), test_features)
    print(f"✅ Cache set successful: {success}")
    
    # Retrieve from cache
    cached_features = cache_manager.get('features', ('R123456', 'basic_features'))
    print(f"🎯 Cache retrieval successful: {cached_features is not None}")
    
    # Test cache miss
    missing_data = cache_manager.get('features', ('R999999', 'missing_features'))
    print(f"❌ Cache miss handled correctly: {missing_data is None}")
    
    # Display cache statistics
    print("\n📊 Cache Statistics:")
    cache_info = cache_manager.get_cache_info()
    for key, value in cache_info.items():
        print(f"  • {key}: {value}")
    
    print("\n🎉 Cache Manager testing complete!")
