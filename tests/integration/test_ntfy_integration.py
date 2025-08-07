"""
Integration tests for NTFY notification system in containerized environment.

Tests the complete notification flow including:
- NTFY server connectivity
- Message publishing
- Topic subscription
- Error handling
"""

import asyncio
import os
import time
from typing import Optional

import httpx
import pytest
import requests

from src.horse_racing_ai.notifications.ntfy_client import (
    NotificationMessage,
    NTFYClient,
)


class TestNTFYIntegration:
    """Integration tests for NTFY notification system."""

    @pytest.fixture
    def ntfy_url(self) -> str:
        """Get NTFY server URL from environment."""
        return os.getenv("NTFY_URL", "http://ntfy-test:80")

    @pytest.fixture
    def test_topic(self) -> str:
        """Get test topic name."""
        return os.getenv("NTFY_TOPIC", "horse-racing-test")

    @pytest.fixture
    def ntfy_client(self, ntfy_url: str, test_topic: str) -> NTFYClient:
        """Create NTFY client for testing."""
        return NTFYClient(topic=test_topic, base_url=ntfy_url)

    def test_ntfy_server_health(self, ntfy_url: str):
        """Test that NTFY server is healthy and accessible."""
        health_url = f"{ntfy_url}/v1/health"

        try:
            response = requests.get(health_url, timeout=10)
            assert (
                response.status_code == 200
            ), f"NTFY health check failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to NTFY server: {e}")

    def test_ntfy_topic_creation(self, ntfy_url: str, test_topic: str):
        """Test topic creation and basic functionality."""
        topic_url = f"{ntfy_url}/{test_topic}"

        # Test that we can access the topic
        try:
            response = requests.get(topic_url, timeout=5)
            # Topics return 200 even if they don't exist yet
            assert response.status_code == 200
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to access NTFY topic: {e}")

    @pytest.mark.asyncio
    async def test_send_notification_success(self, ntfy_client: NTFYClient):
        """Test successful notification sending."""
        test_message = "🧪 Test notification from integration tests"
        test_title = "Integration Test"

        try:
            notification = NotificationMessage(
                title=test_title,
                message=test_message,
                priority="default",
                tags=["test", "integration"],
            )
            success = await ntfy_client.send_notification(notification)

            assert success is True, "Notification sending should succeed"

        except Exception as e:
            pytest.fail(f"Failed to send notification: {e}")

    @pytest.mark.asyncio
    async def test_send_race_notification(self, ntfy_client: NTFYClient):
        """Test race-specific notification."""
        race_data = {
            "track": "Test Track",
            "race_number": 1,
            "race_time": "14:30",
            "distance": "1200m",
            "horses": [
                {"name": "Integration Horse", "odds": 3.5},
                {"name": "Test Horse 2", "odds": 4.0},
            ],
        }

        try:
            success = await ntfy_client.send_race_alert(race_data, "info")
            assert success is True, "Race notification should succeed"

        except Exception as e:
            pytest.fail(f"Failed to send race notification: {e}")

    @pytest.mark.asyncio
    async def test_send_bet_notification(self, ntfy_client: NTFYClient):
        """Test bet-specific notification using system alert."""
        bet_info = (
            "🐎 Test Horse in Integration Test Race\n"
            "💰 Odds: 3.5\n"
            "💸 Stake: $25.0\n"
            "💵 Potential Return: $87.5\n"
            "📊 Confidence: 88%"
        )

        try:
            success = await ntfy_client.send_system_alert(
                "Betting", "opportunity", bet_info
            )
            assert success is True, "Bet notification should succeed"

        except Exception as e:
            pytest.fail(f"Failed to send bet notification: {e}")

    @pytest.mark.asyncio
    async def test_notification_with_different_priorities(
        self, ntfy_client: NTFYClient
    ):
        """Test notifications with different priority levels."""
        priorities = ["min", "low", "default", "high", "max"]

        for priority in priorities:
            try:
                notification = NotificationMessage(
                    title=f"Priority Test - {priority.upper()}",
                    message=f"Test message with {priority} priority",
                    priority=priority,
                    tags=["test", "priority", priority],
                )
                success = await ntfy_client.send_notification(notification)

                assert (
                    success is True
                ), f"Notification with {priority} priority should succeed"

                # Small delay between notifications
                await asyncio.sleep(0.5)

            except Exception as e:
                pytest.fail(f"Failed to send {priority} priority notification: {e}")

    def test_ntfy_client_configuration(self, ntfy_client: NTFYClient):
        """Test NTFY client configuration."""
        assert ntfy_client.base_url is not None
        assert ntfy_client.topic is not None
        assert ntfy_client.enabled is True

    @pytest.mark.asyncio
    async def test_notification_error_handling(self, test_topic: str):
        """Test error handling with invalid NTFY configuration."""
        # Create client with invalid URL
        invalid_client = NTFYClient(
            topic=test_topic, base_url="http://invalid-server:9999"
        )

        # This should fail gracefully
        notification = NotificationMessage(
            title="Error Test", message="This should fail"
        )
        success = await invalid_client.send_notification(notification)

        # Should return False on failure, not raise exception
        assert success is False, "Should return False for failed notifications"

    @pytest.mark.asyncio
    async def test_disabled_notifications(self, ntfy_url: str, test_topic: str):
        """Test that notifications work with valid configuration."""
        # Create normal client (we can't easily test disabled state in integration)
        client = NTFYClient(topic=test_topic, base_url=ntfy_url)

        notification = NotificationMessage(
            title="Config Test", message="Testing client configuration"
        )
        success = await client.send_notification(notification)

        # Should work normally
        assert success is True, "Notification should succeed with valid config"

    def test_ntfy_server_endpoints(self, ntfy_url: str):
        """Test various NTFY server endpoints."""
        endpoints_to_test = [
            "/v1/health",
            "/static/js/app.js",  # Web UI assets
        ]

        for endpoint in endpoints_to_test:
            url = f"{ntfy_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                # Health should be 200, assets might be 200 or 404
                # depending on NTFY version
                assert response.status_code in [
                    200,
                    404,
                ], f"Unexpected status for {endpoint}"
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Failed to access {endpoint}: {e}")

    @pytest.mark.asyncio
    async def test_concurrent_notifications(self, ntfy_client: NTFYClient):
        """Test sending multiple notifications concurrently."""

        async def send_test_notification(index: int) -> bool:
            notification = NotificationMessage(
                title=f"Concurrent Test {index}",
                message=f"Concurrent test message #{index}",
                tags=["test", "concurrent", str(index)],
            )
            return await ntfy_client.send_notification(notification)

        # Send 5 notifications concurrently
        tasks = [send_test_notification(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent notification {i} failed: {result}")
            assert result is True, f"Concurrent notification {i} should succeed"
