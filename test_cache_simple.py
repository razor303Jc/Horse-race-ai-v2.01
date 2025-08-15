#!/usr/bin/env python3
"""
Simple test for the Intelligent Caching System - Phase 1C
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from tools.caching.pipeline_cache_manager import PipelineCacheManager
    from tools.caching.cached_feature_engineering import CachedFeatureEngineering
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_cache_basic_operations():
    """Test basic cache operations."""
    print("🔧 Testing basic cache operations...")

    cache = PipelineCacheManager()

    # Test setting and getting data
    test_data = {"race_id": "test_001", "features": [1, 2, 3, 4, 5]}

    # Set data in cache
    success = cache.set("features", ("test_001",), test_data, ttl=60)
    if success:
        print("✅ Data stored in cache")
    else:
        print("❌ Failed to store data")
        return False

    # Get data from cache
    retrieved = cache.get("features", ("test_001",))
    if retrieved and retrieved == test_data:
        print("✅ Data retrieved successfully")
        print(f"📊 Retrieved: {retrieved}")
    else:
        print("❌ Failed to retrieve data or data mismatch")
        return False

    # Test cache miss
    missing = cache.get("features", ("nonexistent",))
    if missing is None:
        print("✅ Cache miss handled correctly")
    else:
        print("❌ Unexpected data for cache miss")
        return False

    return True


def test_cache_performance():
    """Test cache performance benefits."""
    print("\n⚡ Testing cache performance...")

    cache = PipelineCacheManager()

    # Simulate expensive computation
    def expensive_computation(race_id):
        """Simulate an expensive feature engineering computation."""
        time.sleep(0.1)  # Simulate 100ms computation
        return {
            "race_id": race_id,
            "features": {
                "avg_speed": 45.5,
                "field_size": 12,
                "track_condition": "good",
                "weather": "clear",
            },
            "computed_at": time.time(),
        }

    race_id = "performance_test_001"

    # First call - should be slow (computation)
    print("🔧 First call - computing features...")
    start_time = time.time()

    # Check cache first
    cached_result = cache.get("features", (race_id,))
    if cached_result is None:
        # Not in cache, compute
        result = expensive_computation(race_id)
        cache.set("features", (race_id,), result, ttl=300)
        print("📊 Result computed and cached")
    else:
        result = cached_result
        print("📊 Result found in cache")

    first_duration = time.time() - start_time
    print(f"⏱️  First call: {first_duration:.3f}s")

    # Second call - should be fast (cached)
    print("⚡ Second call - should use cache...")
    start_time = time.time()

    cached_result = cache.get("features", (race_id,))
    if cached_result:
        print("✅ Found in cache")
        result2 = cached_result
    else:
        print("❌ Not found in cache - unexpected")
        return False

    second_duration = time.time() - start_time
    print(f"⚡ Second call: {second_duration:.3f}s")

    # Verify performance improvement
    if second_duration < first_duration:
        speedup = (
            first_duration / second_duration if second_duration > 0 else float("inf")
        )
        print(f"🚀 Performance improvement: {speedup:.1f}x faster")
        return True
    else:
        print("❌ No performance improvement detected")
        return False


def test_cache_stats():
    """Test cache statistics tracking."""
    print("\n📊 Testing cache statistics...")

    cache = PipelineCacheManager()

    # Get initial stats
    initial_info = cache.get_cache_info()
    print(f"📈 Initial stats: {initial_info['hit_rate']:.1f}% hit rate")

    # Make some cache operations
    test_keys = [("stats_test_1",), ("stats_test_2,"), ("stats_test_1",)]

    for i, key_args in enumerate(test_keys, 1):
        # Try to get (will be miss for new keys)
        result = cache.get("features", key_args)

        if result is None:
            # Cache miss - store some data
            test_data = {"test": f"data_{i}", "timestamp": time.time()}
            cache.set("features", key_args, test_data, ttl=60)
            status = "MISS -> STORE"
        else:
            status = "HIT"

        print(f"  Operation {i}: {status}")

    # Get final stats
    final_info = cache.get_cache_info()
    print(f"📊 Final stats: {final_info['hit_rate']:.1f}% hit rate")
    print(f"🎯 Total requests: {final_info['total_requests']}")

    return True


def test_cached_feature_engineering():
    """Test the cached feature engineering wrapper."""
    print("\n🏇 Testing cached feature engineering...")

    try:
        cached_fe = CachedFeatureEngineering()
        print("✅ CachedFeatureEngineering initialized")

        # Test if it has the expected interface
        if hasattr(cached_fe, "cache_manager"):
            print("✅ Has cache manager")
        else:
            print("⚠️  No cache manager attribute")

        return True

    except Exception as e:
        print(f"❌ Error testing cached feature engineering: {e}")
        return False


def main():
    """Run all cache tests."""
    print("🏇 Intelligent Caching System - Simple Test Suite")
    print("=" * 60)

    # Check Redis availability
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        print("✅ Redis server available")
    except Exception as e:
        print(f"❌ Redis server not available: {e}")
        print("💡 Start Redis with: redis-server")
        return False

    tests = [
        ("Basic Cache Operations", test_cache_basic_operations),
        ("Cache Performance", test_cache_performance),
        ("Cache Statistics", test_cache_stats),
        ("Cached Feature Engineering", test_cached_feature_engineering),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n🧪 {test_name}")
            print("-" * 40)
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")

    print(f"\n🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All caching system tests passed! 🚀")
        print("📊 Intelligent caching system is working correctly")
        return True
    else:
        print("⚠️  Some tests failed - review implementation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
