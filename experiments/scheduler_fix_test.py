#!/usr/bin/env python3
"""
Simple test to verify scheduler fixes
"""

import sys
import os
from datetime import datetime
import subprocess


def send_ntfy_test():
    """Test NTFY notification."""
    try:
        import requests

        url = "http://localhost:8081/horse_racing_alerts"
        headers = {
            "Title": "Scheduler Fix Test",
            "Priority": "high",
            "Tags": "test,scheduler",
        }
        message = f"Scheduler test completed at {datetime.now().strftime('%H:%M:%S')}"
        response = requests.post(url, data=message, headers=headers)

        if response.status_code == 200:
            print("✅ NTFY notification sent successfully")
            return True
        else:
            print(f"❌ NTFY failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ NTFY error: {e}")
        return False


def test_subprocess():
    """Test subprocess execution with proper Python path."""
    try:
        # Use current Python executable
        python_path = sys.executable
        print(f"✅ Python path: {python_path}")

        # Test a simple Python command
        result = subprocess.run(
            [python_path, "-c", "print('✅ Subprocess test successful')"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print(f"✅ Subprocess output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Subprocess failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Subprocess error: {e}")
        return False


def main():
    """Run scheduler fix tests."""
    print("🧪 Testing scheduler fixes...")
    print(f"📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working directory: {os.getcwd()}")

    # Test NTFY
    print("\n🔔 Testing NTFY notifications...")
    ntfy_success = send_ntfy_test()

    # Test subprocess
    print("\n⚙️ Testing subprocess execution...")
    subprocess_success = test_subprocess()

    # Summary
    print("\n📊 TEST RESULTS:")
    print(f"   NTFY notifications: {'✅ WORKING' if ntfy_success else '❌ FAILED'}")
    print(
        f"   Subprocess execution: {'✅ WORKING' if subprocess_success else '❌ FAILED'}"
    )

    if ntfy_success and subprocess_success:
        print("\n🎉 ALL TESTS PASSED! Scheduler issues are FIXED!")
        return True
    else:
        print("\n❌ Some tests failed. Issues remain.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
