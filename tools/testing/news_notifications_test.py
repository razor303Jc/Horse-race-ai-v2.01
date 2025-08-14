#!/usr/bin/env python3
"""
Test script for racing news notifications
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from horse_racing_ai.notifications.ntfy_client import NotificationMessage, ntfy_client


async def test_notifications():
    """Test different types of racing news notifications"""

    print("🧪 Testing Racing News Notifications...")

    # Test 1: Simple notification
    success1 = await ntfy_client.send_simple(
        "🏇 Racing News Test",
        "Testing notification system for racing news analysis",
        "default",
    )
    print(f"✅ Simple notification: {'Success' if success1 else 'Failed'}")

    # Test 2: High-impact article alert
    article_alert = NotificationMessage(
        title="🚨 Breaking Racing News",
        message="Major story detected with 5 horses mentioned\nSentiment: 0.85",
        priority="high",
        tags=["🏇", "breaking", "high-impact"],
    )
    success2 = await ntfy_client.send_notification(article_alert)
    print(f"✅ Article alert: {'Success' if success2 else 'Failed'}")

    # Test 3: Daily summary
    summary_alert = NotificationMessage(
        title="📊 Daily Racing News Analysis Complete",
        message="Analyzed 8 articles\nAverage Sentiment: Positive (0.72)\nReport available in dashboard",
        priority="default",
        tags=["📰", "daily-summary"],
    )
    success3 = await ntfy_client.send_notification(summary_alert)
    print(f"✅ Daily summary: {'Success' if success3 else 'Failed'}")

    # Test 4: System status
    system_alert = NotificationMessage(
        title="✅ News Analyzer Status",
        message="Status: ONLINE\nLast run: 8 articles analyzed successfully",
        priority="default",
        tags=["system", "online"],
    )
    success4 = await ntfy_client.send_notification(system_alert)
    print(f"✅ System status: {'Success' if success4 else 'Failed'}")

    total_success = sum([success1, success2, success3, success4])
    print(f"\n🎯 Results: {total_success}/4 notifications sent successfully")

    if total_success == 4:
        print("🎉 All notifications working perfectly!")
    else:
        print("⚠️ Some notifications failed - check NTFY service")


if __name__ == "__main__":
    asyncio.run(test_notifications())
