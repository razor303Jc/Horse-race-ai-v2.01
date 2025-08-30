#!/usr/bin/env python3
"""
Quick test script to validate Redis health integration in C2 status endpoint
"""

import requests
import json
import time


def test_redis_health_integration():
    """Test Redis health monitoring integrated in C2 status"""
    base_url = "http://c2.horse-racing.local"

    print("🧪 Testing Redis Health Integration in C2 Status")
    print("=" * 60)

    try:
        # Test C2 status endpoint
        print("1. Testing C2 status endpoint...")
        response = requests.get(f"{base_url}/c2/status", timeout=10)

        if response.status_code != 200:
            print(f"❌ C2 status endpoint failed: {response.status_code}")
            return False

        data = response.json()
        print(f"✅ C2 status endpoint responding: {response.status_code}")

        # Check for Redis field
        print("\n2. Checking Redis health in C2 status...")
        if "redis" not in data:
            print("❌ Redis health status not found in C2 response")
            return False

        redis_status = data["redis"]
        print(f"✅ Redis health status found: {redis_status}")

        # Validate Redis status value
        print("\n3. Validating Redis status value...")
        valid_statuses = ["healthy", "unhealthy"]
        if redis_status not in valid_statuses:
            print(f"❌ Invalid Redis status: {redis_status}")
            return False

        print(f"✅ Redis status is valid: {redis_status}")

        # Check database health too
        print("\n4. Checking database health in C2 status...")
        if "database" not in data:
            print("❌ Database health status not found in C2 response")
            return False

        db_status = data["database"]
        print(f"✅ Database health status found: {db_status}")

        # Test response time
        print("\n5. Testing response time...")
        start_time = time.time()
        response = requests.get(f"{base_url}/c2/status", timeout=10)
        response_time = (time.time() - start_time) * 1000
        print(f"✅ Response time: {response_time:.0f}ms")

        if response_time > 5000:  # 5 seconds
            print(f"⚠️  Response time is high: {response_time:.0f}ms")

        # Display full status
        print("\n6. Full C2 status response:")
        print(json.dumps(data, indent=2))

        print("\n" + "=" * 60)
        print("🎉 Redis Health Integration Test PASSED!")
        print("✅ Redis health monitoring is working in C2 status endpoint")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_redis_health_integration()
    exit(0 if success else 1)
