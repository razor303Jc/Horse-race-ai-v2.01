#!/usr/bin/env python3
"""
Simple NTFY Popup Notification Tester
Focus on getting actual popup alerts, not just web app messages
"""

import requests
import time


def send_popup_notification(title, message, priority="high"):
    """Send NTFY notification optimized for popup alerts"""
    try:
        # Clean text - remove all emojis and special characters
        clean_title = "".join(c for c in title if ord(c) < 128)
        clean_message = "".join(c for c in message if ord(c) < 128)

        url = "https://ntfy.sh/horse-racing-alerts"

        # Headers optimized for popup notifications
        headers = {
            "Title": clean_title,
            "Priority": priority,
            "Tags": "alert,popup",
            "Content-Type": "text/plain",
        }

        response = requests.post(url, data=clean_message, headers=headers)
        response.raise_for_status()

        print(f"SUCCESS: Sent '{clean_title}' with {priority} priority")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_popup_notifications():
    """Test notifications that should trigger popups"""

    print("NTFY Popup Notification Test")
    print("=" * 40)
    print()
    print("IMPORTANT: To get popup notifications:")
    print("1. Go to: https://ntfy.sh/horse-racing-alerts")
    print("2. Click the bell icon and ALLOW notifications")
    print("3. Keep the browser tab open (or pin it)")
    print("4. OR install the NTFY mobile app")
    print()
    print("Testing different priority levels...")
    print()

    tests = [
        ("Low Priority Test", "This is a low priority message", "min"),
        ("Normal Test", "This is a normal priority message", "default"),
        ("High Priority Test", "This should popup!", "high"),
        ("Urgent Alert", "URGENT: This should definitely popup!", "urgent"),
    ]

    for i, (title, message, priority) in enumerate(tests, 1):
        print(f"{i}. Testing {priority} priority...")
        success = send_popup_notification(title, message, priority)

        if i < len(tests):
            print("   Waiting 4 seconds...")
            time.sleep(4)
        print()

    print("=" * 40)
    print("Racing Alert Test:")

    # Test a racing alert
    racing_title = "[RACING TIP] Flemington 15:30"
    racing_message = "Top Pick: Thunder Strike (85% confidence)\nRecommended: WIN bet"

    send_popup_notification(racing_title, racing_message, "urgent")

    print()
    print("Test Complete!")
    print()
    print("Did you get popup notifications?")
    print("- YES: Great! Your setup is working")
    print("- NO: Try these solutions:")
    print("  * Check browser notification permissions")
    print("  * Install NTFY mobile app and subscribe to 'horse-racing-alerts'")
    print("  * Try a different browser")
    print("  * Make sure the browser tab stays open")


if __name__ == "__main__":
    test_popup_notifications()
