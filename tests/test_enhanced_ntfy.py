#!/usr/bin/env python3
"""
Enhanced NTFY Notification System
Tests different notification methods to ensure popup alerts work
"""

import requests
import time
import json
from datetime import datetime


class EnhancedNTFYNotifier:
    def __init__(self, topic="horse-racing-alerts"):
        self.topic = topic
        self.base_url = f"https://ntfy.sh/{topic}"

    def send_notification(
        self,
        title: str,
        message: str,
        priority: str = "default",
        tags: str = "horse,racing,ai",
        actions: list = None,
    ) -> bool:
        """Send enhanced NTFY notification with popup-friendly settings"""
        try:
            # Clean emojis for better compatibility
            clean_title = self._clean_text(title)
            clean_message = self._clean_text(message)

            headers = {
                "Title": clean_title,
                "Priority": priority,
                "Tags": tags,
                "Content-Type": "text/plain; charset=utf-8",
            }

            # Add actions for interactive notifications
            if actions:
                headers["Actions"] = json.dumps(actions)

            # For high priority notifications, add extra headers
            if priority == "urgent":
                headers["Call"] = "yes"  # Make phone ring/vibrate
                headers["Email"] = "auto"  # Send email backup

            response = requests.post(
                self.base_url,
                data=clean_message.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()

            print(f"✅ Enhanced notification sent: {clean_title}")
            return True

        except Exception as e:
            print(f"❌ Notification error: {e}")
            return False

    def _clean_text(self, text: str) -> str:
        """Remove problematic characters for better notification display"""
        # Remove emojis and replace with text indicators
        replacements = {
            "🏁": "[RACE]",
            "🎯": "[TIP]",
            "⚡": "[PERF]",
            "🔥": "[HOT]",
            "💰": "[WIN]",
            "📊": "[DATA]",
            "🚨": "[ALERT]",
        }

        clean_text = text
        for emoji, replacement in replacements.items():
            clean_text = clean_text.replace(emoji, replacement)

        return clean_text.strip()

    def test_notification_levels(self):
        """Test different notification priority levels"""
        print("🧪 Testing NTFY notification levels...")

        test_cases = [
            {
                "title": "🔧 Low Priority Test",
                "message": "This is a low priority test message",
                "priority": "min",
            },
            {
                "title": "📋 Normal Priority Test",
                "message": "This is a normal priority test message",
                "priority": "default",
            },
            {
                "title": "⚠️ High Priority Test",
                "message": "This is a high priority test - should popup!",
                "priority": "high",
            },
            {
                "title": "🚨 URGENT Test",
                "message": "URGENT: This should definitely create a popup alert!",
                "priority": "urgent",
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. Sending {test['priority']} priority notification...")
            success = self.send_notification(
                test["title"], test["message"], priority=test["priority"]
            )

            if success:
                print(f"   ✅ Sent successfully")
            else:
                print(f"   ❌ Failed to send")

            # Wait between notifications
            if i < len(test_cases):
                print("   ⏳ Waiting 3 seconds...")
                time.sleep(3)

    def send_racing_alert(self, race_name: str, tip: str, confidence: float):
        """Send a racing-specific alert with high priority if confidence is high"""
        priority = (
            "urgent" if confidence > 0.8 else "high" if confidence > 0.6 else "default"
        )

        actions = [
            {
                "action": "view",
                "label": "View Details",
                "url": "https://ntfy.sh/horse-racing-alerts",
            }
        ]

        title = f"[TIP] {race_name}"
        message = f"Top Pick: {tip}\nConfidence: {confidence:.1%}\nTime: {datetime.now().strftime('%H:%M')}"

        return self.send_notification(
            title=title,
            message=message,
            priority=priority,
            tags="horse,racing,tip,alert",
            actions=actions,
        )


def main():
    """Main test function"""
    print("🔔 NTFY Enhanced Notification Tester")
    print("=" * 50)

    notifier = EnhancedNTFYNotifier()

    # Test different notification levels
    notifier.test_notification_levels()

    print("\n" + "=" * 50)
    print("🏁 Testing Racing-Specific Alert...")

    # Test a high-confidence racing alert
    notifier.send_racing_alert(
        race_name="Flemington 15:30", tip="Thunder Strike", confidence=0.85
    )

    print("\n" + "=" * 50)
    print("✅ Testing Complete!")
    print("\nIf you received popup notifications:")
    print("   🎉 Your NTFY setup is working correctly!")
    print("\nIf you only saw messages in the web app:")
    print("   📱 Try the mobile app or enable browser notifications")
    print("   🔔 Check browser notification permissions")
    print("   📋 See NTFY_NOTIFICATION_SETUP_GUIDE.md for help")


if __name__ == "__main__":
    main()
