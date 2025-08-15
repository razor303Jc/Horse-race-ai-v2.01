#!/usr/bin/env python3
"""
Integration tests for the Intelligent Caching System - Phase 1C
"""

import pytest
import sys
import os
import time
import redis
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from tools.caching.pipeline_cache_manager import PipelineCacheManager
    from tools.caching.cached_feature_engineering import CachedFeatureEngineering
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestIntelligentCaching:
    """Test suite for intelligent caching system."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing."""
        return PipelineCacheManager()
    
    @pytest.fixture
    def cached_fe(self):
        """Create cached feature engineering for testing."""
        return CachedFeatureEngineering()
    
    def test_redis_connection(self, cache_manager):
        """Test Redis connection and basic operations."""
        print("🔧 Testing Redis connection...")
        
        # Test basic set/get
        test_key = "test:connection"
        test_value = {"timestamp": time.time(), "status": "ok"}
        
        # Set value
        success = cache_manager.set(test_key, test_value, ttl=60)
        assert success, "Failed to set cache value"
        print("✅ Cache SET operation successful")
        
        # Get value
        retrieved = cache_manager.get(test_key)
        assert retrieved is not None, "Failed to retrieve cache value"
        assert retrieved["status"] == "ok", "Retrieved value mismatch"
        print("✅ Cache GET operation successful")
        
        # Test TTL
        ttl = cache_manager.redis.ttl(test_key)
        assert 0 < ttl <= 60, f"TTL not set correctly: {ttl}"
        print(f"✅ TTL set correctly: {ttl} seconds")
        
        # Clean up
        cache_manager.delete(test_key)
    
    def test_cache_performance_tracking(self, cache_manager):
        """Test cache hit/miss performance tracking."""
        print("📊 Testing cache performance tracking...")
        
        # Reset metrics
        cache_manager.reset_metrics()
        
        # Test cache miss
        result = cache_manager.get("nonexistent:key")
        assert result is None
        
        metrics = cache_manager.get_metrics()
        assert metrics["cache_misses"] == 1
        assert metrics["cache_hits"] == 0
        print("✅ Cache miss tracking works")
        
        # Test cache hit
        cache_manager.set("test:hit", {"data": "test"}, ttl=60)
        result = cache_manager.get("test:hit")
        assert result is not None
        
        metrics = cache_manager.get_metrics()
        assert metrics["cache_hits"] == 1
        assert metrics["cache_misses"] == 1
        
        hit_rate = metrics["hit_rate"]
        assert hit_rate == 50.0, f"Hit rate should be 50%, got {hit_rate}%"
        print(f"✅ Cache hit rate: {hit_rate}%")
        
        # Clean up
        cache_manager.delete("test:hit")
    
    def test_race_feature_caching(self, cached_fe):
        """Test race feature engineering caching."""
        print("🏇 Testing race feature caching...")
        
        # Mock race ID for testing
        test_race_id = "test_race_001"
        
        # First call should compute and cache
        print("🔧 First call - should compute and cache...")
        start_time = time.time()
        features_1 = cached_fe.get_race_features(test_race_id)
        first_duration = time.time() - start_time
        
        assert features_1 is not None, "Feature computation failed"
        print(f"✅ Features computed in {first_duration:.3f}s")
        print(f"📊 Feature count: {len(features_1)} features")
        
        # Second call should use cache
        print("⚡ Second call - should use cache...")
        start_time = time.time()
        features_2 = cached_fe.get_race_features(test_race_id)
        second_duration = time.time() - start_time
        
        assert features_2 == features_1, "Cached features don't match"
        assert second_duration < first_duration, "Cache didn't improve performance"
        
        speedup = first_duration / second_duration if second_duration > 0 else float('inf')
        print(f"✅ Cache hit in {second_duration:.3f}s")
        print(f"🚀 Performance improvement: {speedup:.1f}x faster")
        
        # Test cache invalidation
        print("🔄 Testing cache invalidation...")
        cached_fe.invalidate_race_cache(test_race_id)
        
        # Third call should recompute
        start_time = time.time()
        features_3 = cached_fe.get_race_features(test_race_id)
        third_duration = time.time() - start_time
        
        assert features_3 == features_1, "Recomputed features don't match"
        assert third_duration > second_duration, "Cache invalidation didn't work"
        print("✅ Cache invalidation successful")
    
    def test_feature_engineering_performance(self, cached_fe):
        """Test overall feature engineering performance with caching."""
        print("🎯 Testing feature engineering performance...")
        
        # Test multiple races to see cache benefits
        test_races = ["race_001", "race_002", "race_001", "race_003", "race_002"]
        
        total_start = time.time()
        cache_hits = 0
        cache_misses = 0
        
        for i, race_id in enumerate(test_races, 1):
            start_time = time.time()
            features = cached_fe.get_race_features(race_id)
            duration = time.time() - start_time
            
            # Check if this was likely a cache hit (very fast)
            is_cache_hit = duration < 0.01  # Less than 10ms is likely cached
            if is_cache_hit:
                cache_hits += 1
            else:
                cache_misses += 1
            
            status = "HIT" if is_cache_hit else "MISS"
            print(f"  Race {i}: {race_id} - {duration:.3f}s ({status})")
        
        total_duration = time.time() - total_start
        
        print(f"\n📊 Performance Summary:")
        print(f"   Total time: {total_duration:.3f}s")
        print(f"   Cache hits: {cache_hits}")
        print(f"   Cache misses: {cache_misses}")
        print(f"   Hit rate: {cache_hits/(cache_hits+cache_misses)*100:.1f}%")
        
        # Should have some cache hits on repeated races
        assert cache_hits > 0, "No cache hits detected"
        print("✅ Cache performance optimization working")
    
    def test_cache_memory_usage(self, cache_manager):
        """Test cache memory usage and cleanup."""
        print("💾 Testing cache memory usage...")
        
        # Get initial memory info
        info = cache_manager.redis.info('memory')
        initial_memory = info['used_memory']
        print(f"🔧 Initial Redis memory: {initial_memory:,} bytes")
        
        # Store multiple large objects
        large_data = {"data": "x" * 10000, "features": list(range(1000))}
        stored_keys = []
        
        for i in range(10):
            key = f"test:large_data:{i}"
            cache_manager.set(key, large_data, ttl=300)
            stored_keys.append(key)
        
        # Check memory usage
        info = cache_manager.redis.info('memory')
        after_memory = info['used_memory']
        memory_increase = after_memory - initial_memory
        
        print(f"📊 Memory after storing data: {after_memory:,} bytes")
        print(f"📈 Memory increase: {memory_increase:,} bytes")
        
        assert memory_increase > 0, "Memory didn't increase as expected"
        
        # Clean up and check memory decrease
        for key in stored_keys:
            cache_manager.delete(key)
        
        # Force garbage collection in Redis
        cache_manager.redis.flushdb()
        
        info = cache_manager.redis.info('memory')
        final_memory = info['used_memory']
        print(f"🧹 Final memory after cleanup: {final_memory:,} bytes")
        
        assert final_memory <= initial_memory + 1000, "Memory not properly cleaned up"
        print("✅ Cache memory management working")


def run_caching_tests():
    """Run all caching system tests."""
    print("🏇 Intelligent Caching System - Integration Tests")
    print("=" * 60)
    
    try:
        # Test Redis availability
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis server available")
    except Exception as e:
        print(f"❌ Redis server not available: {e}")
        print("💡 Start Redis with: redis-server")
        return False
    
    # Create test instances
    test_suite = TestIntelligentCaching()
    cache_manager = PipelineCacheManager()
    cached_fe = CachedFeatureEngineering()
    
    tests = [
        ("Redis Connection", lambda: test_suite.test_redis_connection(cache_manager)),
        ("Performance Tracking", lambda: test_suite.test_cache_performance_tracking(cache_manager)),
        ("Race Feature Caching", lambda: test_suite.test_race_feature_caching(cached_fe)),
        ("FE Performance", lambda: test_suite.test_feature_engineering_performance(cached_fe)),
        ("Memory Management", lambda: test_suite.test_cache_memory_usage(cache_manager)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        try:
            test_func()
            print(f"✅ {test_name} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All caching system tests passed! 🚀")
        print("📊 Intelligent caching system ready for integration")
        return True
    else:
        print("⚠️  Some tests failed - review implementation")
        return False


if __name__ == "__main__":
    success = run_caching_tests()
    sys.exit(0 if success else 1)
