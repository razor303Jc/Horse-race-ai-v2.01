#!/usr/bin/env python3
"""
Racing News Notifications Dashboard
Displays recent notifications and system status
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import requests

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from horse_racing_ai.notifications.ntfy_client import ntfy_client

    NTFY_AVAILABLE = True
except ImportError:
    NTFY_AVAILABLE = False
    print("⚠️ NTFY client not available")


def check_ntfy_service():
    """Check if NTFY service is running"""
    try:
        response = requests.get("http://localhost:8081/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_recent_notifications():
    """Get recent notifications from NTFY"""
    try:
        response = requests.get(
            "http://localhost:8081/horse-racing-alerts/json?poll=1", timeout=10
        )
        if response.status_code == 200:
            notifications = []
            for line in response.text.strip().split("\n"):
                if line:
                    try:
                        notifications.append(json.loads(line))
                    except:
                        continue
            return notifications[-10:]  # Last 10 notifications
        return []
    except:
        return []


async def send_test_notification():
    """Send a test notification"""
    if not NTFY_AVAILABLE:
        return False

    try:
        return await ntfy_client.send_simple(
            "🧪 Dashboard Test",
            f"Test notification from dashboard at {datetime.now().strftime('%H:%M:%S')}",
            "min",
        )
    except:
        return False


def display_dashboard():
    """Display the notifications dashboard"""
    print("🏇 Racing News Notifications Dashboard")
    print("=" * 50)

    # Check service status
    service_status = check_ntfy_service()
    print(f"📡 NTFY Service: {'🟢 ONLINE' if service_status else '🔴 OFFLINE'}")

    if NTFY_AVAILABLE:
        print(f"📱 Client Status: 🟢 AVAILABLE")
    else:
        print(f"📱 Client Status: 🔴 UNAVAILABLE")

    print()

    # Get recent notifications
    if service_status:
        print("📊 Recent Notifications (Last 10):")
        print("-" * 50)

        notifications = get_recent_notifications()
        if notifications:
            for i, notif in enumerate(reversed(notifications), 1):
                time_str = datetime.fromtimestamp(notif.get("time", 0)).strftime(
                    "%H:%M:%S"
                )
                title = notif.get("title", "No title")
                message = notif.get("message", "No message")
                priority = notif.get("priority", "default")

                # Truncate long messages
                if len(message) > 60:
                    message = message[:57] + "..."

                priority_emoji = {
                    "min": "🔵",
                    "default": "⚪",
                    "high": "🟡",
                    "max": "🔴",
                }.get(priority, "⚪")

                print(f"{i:2d}. {time_str} {priority_emoji} {title}")
                print(f"    {message}")
                print()
        else:
            print("No recent notifications found")
    else:
        print("❌ Cannot retrieve notifications - service offline")

    print("=" * 50)


async def main():
    """Main dashboard function"""
    display_dashboard()

    # Offer to send test notification
    if NTFY_AVAILABLE:
        print("\n🧪 Send test notification? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response == "y":
                print("Sending test notification...")
                success = await send_test_notification()
                if success:
                    print("✅ Test notification sent successfully!")
                else:
                    print("❌ Failed to send test notification")
        except KeyboardInterrupt:
            print("\nExiting...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")
