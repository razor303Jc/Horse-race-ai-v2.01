#!/usr/bin/env python3
"""
NTFY Test Script - Tests notification system without shell quoting issues
"""

import requests
import json
from datetime import datetime


def send_ntfy_notification(title, message, priority="default"):
    """Send notification to NTFY server."""
    try:
        url = "http://localhost:8081/horse-racing-alerts"

        # Use requests instead of curl to avoid shell issues
        headers = {"Title": title, "Priority": priority, "Tags": "horse,racing,test"}

        response = requests.post(url, data=message, headers=headers)

        if response.status_code == 200:
            print(f"✅ Notification sent successfully!")
            print(f"📱 Title: {title}")
            print(f"💬 Message: {message}")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False


def test_notifications():
    """Test different types of notifications."""
    print("🧪 Testing NTFY Notification System")
    print("=" * 40)

    # Test 1: Simple notification
    print("\n📱 Test 1: Simple notification")
    send_ntfy_notification(
        "Horse Racing System Test",
        "This is a test notification from the horse racing pipeline.",
    )

    # Test 2: High priority alert
    print("\n🚨 Test 2: High priority alert")
    send_ntfy_notification(
        "Data Download Alert",
        f"Fresh race data downloaded at {datetime.now().strftime('%H:%M:%S')}",
        priority="high",
    )

    # Test 3: System status
    print("\n📊 Test 3: System status")
    send_ntfy_notification(
        "Pipeline Status",
        "ML models trained successfully with 91% accuracy!",
        priority="default",
    )


if __name__ == "__main__":
    test_notifications()
