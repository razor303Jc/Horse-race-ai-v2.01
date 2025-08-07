#!/usr/bin/env python3

import requests


def send_ntfy_notification(title: str, message: str, priority: str = "default") -> bool:
    """Send a notification via NTFY with emoji handling"""
    try:
        # Remove or replace Unicode emojis for NTFY compatibility
        clean_title = (
            title.replace("🏁", "").replace("🎯", "").replace("⚡", "").strip()
        )
        clean_message = (
            message.replace("🏁", "").replace("🎯", "").replace("⚡", "").strip()
        )

        # Add simple text indicators instead
        if "Racing Analysis" in title:
            clean_title = f"[RACING] {clean_title}"
        elif any(
            venue in title
            for venue in [
                "Carlisle",
                "Worcester",
                "Downpatrick",
                "Wetherby",
                "Fontwell",
            ]
        ):
            clean_title = f"[TIP] {clean_title}"
        elif "Performance" in title:
            clean_title = f"[PERF] {clean_title}"

        url = "https://ntfy.sh/horse-racing-alerts"
        headers = {
            "Title": clean_title,
            "Priority": priority,
            "Tags": "horse,racing,ai",
        }

        response = requests.post(
            url, data=clean_message.encode("utf-8"), headers=headers
        )
        response.raise_for_status()

        print(f"✅ NTFY notification sent: {clean_title}")
        return True

    except Exception as e:
        print(f"❌ NTFY notification error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing fixed NTFY notifications...")

    # Test emoji removal
    success1 = send_ntfy_notification(
        "🏁 Racing Analysis Complete", "🎯 Analyzed 148 races successfully!"
    )

    # Test venue tip
    success2 = send_ntfy_notification(
        "🎯 Carlisle 13:15", "Top pick: Native Trail (22.7%)"
    )

    # Test performance notification
    success3 = send_ntfy_notification(
        "⚡ System Performance", "Pipeline completed in 19.7s"
    )

    if all([success1, success2, success3]):
        print("🎉 All notifications sent successfully!")
    else:
        print("❌ Some notifications failed")
