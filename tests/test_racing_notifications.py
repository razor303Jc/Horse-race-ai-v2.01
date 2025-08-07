#!/usr/bin/env python3
"""
Quick test of racing pipeline notifications
Tests if the updated notification system works for racing alerts
"""

import sys
import os

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from complete_pipeline_runner import send_ntfy_notification


def test_racing_notifications():
    """Test the updated racing notification system"""

    print("🏁 Testing Racing Pipeline Notifications")
    print("=" * 45)
    print()
    print("This will send 3 test notifications using the")
    print("same system as the racing pipeline:")
    print()

    # Test 1: Racing analysis complete
    print("1. Testing racing analysis notification...")
    success1 = send_ntfy_notification(
        "🏁 Racing Analysis Complete",
        "Analyzed 148 races with Monte Carlo predictions. 1680 top picks identified!",
        priority="high",
    )

    if success1:
        print("   ✅ Racing analysis notification sent")
    else:
        print("   ❌ Failed to send racing analysis notification")

    print()

    # Test 2: Racing tip
    print("2. Testing racing tip notification...")
    success2 = send_ntfy_notification(
        "🎯 Carlisle 13:15",
        "Carlisle Selling Stakes - Top pick: Native Trail (22.7%) - James Doyle",
        priority="urgent",
    )

    if success2:
        print("   ✅ Racing tip notification sent")
    else:
        print("   ❌ Failed to send racing tip notification")

    print()

    # Test 3: Performance notification
    print("3. Testing performance notification...")
    success3 = send_ntfy_notification(
        "⚡ System Performance",
        "Complete pipeline executed in 19.7s. All systems optimal.",
        priority="default",
    )

    if success3:
        print("   ✅ Performance notification sent")
    else:
        print("   ❌ Failed to send performance notification")

    print()
    print("=" * 45)

    if all([success1, success2, success3]):
        print("🎉 All racing notifications sent successfully!")
        print()
        print("Check your device for popup notifications:")
        print("📱 Mobile: Check your NTFY app")
        print("🌐 Browser: Check for popup alerts")
        print("🔔 If no popups: See NTFY_NOTIFICATION_SETUP_GUIDE.md")
    else:
        print("❌ Some notifications failed to send")
        print("   Check your internet connection and try again")

    print()
    print("Racing pipeline notifications are now optimized for popups!")


if __name__ == "__main__":
    test_racing_notifications()
