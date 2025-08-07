"""NTFY-based notification system for Horse Racing AI."""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
import structlog

from ..core.config import config

logger = structlog.get_logger(__name__)


@dataclass
class NotificationMessage:
    """Data structure for notification messages."""

    title: str
    message: str
    priority: str = "default"  # min, low, default, high, max
    tags: Optional[List[str]] = None
    click_url: Optional[str] = None
    attach_url: Optional[str] = None
    email: Optional[str] = None
    icon_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {"title": self.title, "message": self.message, "priority": self.priority}

        if self.tags:
            data["tags"] = ",".join(self.tags)
        if self.click_url:
            data["click"] = self.click_url
        if self.attach_url:
            data["attach"] = self.attach_url
        if self.email:
            data["email"] = self.email
        if self.icon_url:
            data["icon"] = self.icon_url

        return data


class NTFYClient:
    """NTFY notification client for horse racing alerts."""

    def __init__(
        self, topic: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize NTFY client.

        Args:
            topic: NTFY topic name
            base_url: NTFY server URL
        """
        self.topic = topic or config.notifications.topic
        self.base_url = base_url or config.notifications.ntfy_url
        self.enabled = config.notifications.enabled

        if not self.topic:
            logger.warning("No NTFY topic configured - notifications will be disabled")
            self.enabled = False

    async def send_notification(self, notification: NotificationMessage) -> bool:
        """Send a notification via NTFY.

        Args:
            notification: The notification message to send

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Notifications disabled, skipping")
            return False

        if not self.topic:
            logger.error("No NTFY topic configured")
            return False

        try:
            url = f"{self.base_url}/{self.topic}"
            headers = {"Content-Type": "application/json"}
            data = notification.to_dict()

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data, headers=headers)

                if response.status_code == 200:
                    logger.info(f"Notification sent successfully: {notification.title}")
                    return True
                else:
                    logger.error(
                        f"Failed to send notification: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    async def send_simple(
        self, title: str, message: str, priority: str = "default"
    ) -> bool:
        """Send a simple notification.

        Args:
            title: Notification title
            message: Notification message
            priority: Notification priority

        Returns:
            True if successful, False otherwise
        """
        notification = NotificationMessage(
            title=title, message=message, priority=priority
        )
        return await self.send_notification(notification)

    async def send_race_alert(
        self, race_data: Dict[str, Any], message_type: str = "info"
    ) -> bool:
        """Send a race-specific alert.

        Args:
            race_data: Dictionary containing race information
            message_type: Type of alert (info, warning, success, error)

        Returns:
            True if successful, False otherwise
        """
        priority_map = {
            "info": "default",
            "warning": "high",
            "success": "default",
            "error": "max",
        }

        tag_map = {
            "info": ["🏇", "info"],
            "warning": ["⚠️", "warning"],
            "success": ["✅", "success"],
            "error": ["❌", "error"],
        }

        title = f"Race Alert: {race_data.get('track', 'Unknown Track')}"

        # Build message content
        message_parts = []
        if race_number := race_data.get("race_number"):
            message_parts.append(f"Race {race_number}")
        if race_time := race_data.get("race_time"):
            if isinstance(race_time, datetime):
                message_parts.append(f"Time: {race_time.strftime('%H:%M')}")
            else:
                message_parts.append(f"Time: {race_time}")
        if distance := race_data.get("distance"):
            message_parts.append(f"Distance: {distance}")
        if num_horses := len(race_data.get("horses", [])):
            message_parts.append(f"Horses: {num_horses}")

        message = " | ".join(message_parts)

        notification = NotificationMessage(
            title=title,
            message=message,
            priority=priority_map.get(message_type, "default"),
            tags=tag_map.get(message_type, ["🏇"]),
        )

        return await self.send_notification(notification)

    async def send_prediction_alert(
        self, predictions: List[Dict[str, Any]], confidence: float
    ) -> bool:
        """Send a prediction alert with AI recommendations.

        Args:
            predictions: List of horse predictions
            confidence: Overall confidence score

        Returns:
            True if successful, False otherwise
        """
        if not predictions:
            return False

        # Get top prediction
        top_prediction = predictions[0]
        horse_name = top_prediction.get("horse_name", "Unknown")
        probability = top_prediction.get("probability", 0.0)

        title = "🎯 AI Prediction Alert"
        message = (
            f"Top Pick: {horse_name} ({probability:.1%})\nConfidence: {confidence:.1%}"
        )

        # Add additional context if available
        if len(predictions) > 1:
            second_pick = predictions[1]
            message += f"\n2nd: {second_pick.get('horse_name', 'Unknown')} ({second_pick.get('probability', 0.0):.1%})"

        priority = "high" if confidence > 0.8 else "default"
        tags = ["🎯", "prediction", "ai"]

        notification = NotificationMessage(
            title=title, message=message, priority=priority, tags=tags
        )

        return await self.send_notification(notification)

    async def send_system_alert(
        self, system: str, status: str, details: str = ""
    ) -> bool:
        """Send a system status alert.

        Args:
            system: Name of the system component
            status: Status (online, offline, error, warning)
            details: Additional details

        Returns:
            True if successful, False otherwise
        """
        status_icons = {
            "online": "✅",
            "offline": "❌",
            "error": "🚨",
            "warning": "⚠️",
            "maintenance": "🔧",
        }

        status_priorities = {
            "online": "default",
            "offline": "high",
            "error": "max",
            "warning": "high",
            "maintenance": "default",
        }

        icon = status_icons.get(status, "ℹ️")
        title = f"{icon} {system} Status"
        message = f"Status: {status.upper()}"

        if details:
            message += f"\n{details}"

        notification = NotificationMessage(
            title=title,
            message=message,
            priority=status_priorities.get(status, "default"),
            tags=["system", status],
        )

        return await self.send_notification(notification)

    async def send_batch_notifications(
        self, notifications: List[NotificationMessage], delay: float = 0.5
    ) -> List[bool]:
        """Send multiple notifications with optional delay between sends.

        Args:
            notifications: List of notifications to send
            delay: Delay in seconds between notifications

        Returns:
            List of success status for each notification
        """
        results = []

        for i, notification in enumerate(notifications):
            if i > 0 and delay > 0:
                await asyncio.sleep(delay)

            result = await self.send_notification(notification)
            results.append(result)

        success_count = sum(results)
        logger.info(
            f"Sent {success_count}/{len(notifications)} notifications successfully"
        )

        return results

    def test_connection(self) -> bool:
        """Test NTFY connection synchronously.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            return asyncio.run(
                self.send_simple(
                    "Test Notification", "Horse Racing AI system test", "min"
                )
            )
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global NTFY client instance
ntfy_client = NTFYClient()
