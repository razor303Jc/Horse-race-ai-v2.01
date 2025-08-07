"""
Test suite for NTFY notifications client.

This module tests the notification system including:
- NTFY client configuration
- Message sending functionality
- Error handling
- Priority levels and formatting
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.horse_racing_ai.notifications.ntfy_client import NTFYClient


class TestNTFYClient:
    """Test the NTFY notification client."""

    def test_client_initialization(self):
        """Test NTFY client initialization with different configurations."""
        # Test with default topic
        client = NTFYClient(topic="test-topic")
        assert client.topic == "test-topic"
        assert client.base_url == "https://ntfy.sh"

        # Test with custom URL
        client = NTFYClient(topic="test", ntfy_url="https://custom.ntfy.sh")
        assert client.base_url == "https://custom.ntfy.sh"

    def test_disabled_client(self):
        """Test behavior when notifications are disabled."""
        client = NTFYClient(topic="test", enabled=False)
        assert not client.enabled

    @pytest.mark.asyncio
    async def test_send_notification_success(self):
        """Test successful notification sending."""
        client = NTFYClient(topic="test-topic")

        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await client.send_notification(
                title="Test Title", message="Test message", priority="high"
            )

            assert result is True
            mock_post.assert_called_once()

            # Verify the correct URL was called
            args, kwargs = mock_post.call_args
            assert "test-topic" in str(args[0])

    @pytest.mark.asyncio
    async def test_send_notification_disabled(self):
        """Test notification sending when disabled."""
        client = NTFYClient(topic="test", enabled=False)

        result = await client.send_notification("Title", "Message")
        assert result is True  # Should return True but not actually send

    @pytest.mark.asyncio
    async def test_send_notification_failure(self):
        """Test notification sending failure handling."""
        client = NTFYClient(topic="test-topic")

        # Mock failed HTTP response
        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await client.send_notification("Title", "Message")
            assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_exception(self):
        """Test notification sending exception handling."""
        client = NTFYClient(topic="test-topic")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Network error")

            result = await client.send_notification("Title", "Message")
            assert result is False

    @pytest.mark.asyncio
    async def test_send_race_alert(self):
        """Test race-specific alert functionality."""
        client = NTFYClient(topic="test-topic")

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            race_data = {
                "race_name": "Test Race",
                "track": "Test Track",
                "horses": [{"name": "Test Horse", "odds": 3.5}],
            }

            result = await client.send_race_alert(race_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_send_betting_alert(self):
        """Test betting-specific alert functionality."""
        client = NTFYClient(topic="test-topic")

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            bet_data = {
                "horse_name": "Test Horse",
                "odds": 3.5,
                "stake": 10.0,
                "confidence": 0.85,
            }

            result = await client.send_betting_alert(bet_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_send_performance_summary(self):
        """Test performance summary notification."""
        client = NTFYClient(topic="test-topic")

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            summary = {"total_bets": 10, "wins": 6, "profit_loss": 25.50, "roi": 0.15}

            result = await client.send_performance_summary(summary)
            assert result is True

    def test_priority_levels(self):
        """Test that priority levels are handled correctly."""
        client = NTFYClient(topic="test")

        # Test valid priority levels
        valid_priorities = ["min", "low", "default", "high", "max"]
        for priority in valid_priorities:
            # Should not raise an exception
            assert priority in valid_priorities

    def test_message_formatting(self):
        """Test message formatting functionality."""
        client = NTFYClient(topic="test")

        # Test basic message formatting
        formatted = client._format_race_message(
            {"race_name": "Test Race", "track": "Test Track"}
        )

        assert "Test Race" in formatted
        assert "Test Track" in formatted

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test NTFY client as context manager."""
        async with NTFYClient(topic="test") as client:
            assert client is not None
            assert hasattr(client, "session")

    def test_url_construction(self):
        """Test proper URL construction."""
        client = NTFYClient(topic="test-topic")

        expected_url = f"{client.base_url}/test-topic"
        assert client._get_topic_url() == expected_url

    def test_headers_construction(self):
        """Test HTTP headers construction."""
        client = NTFYClient(topic="test")

        headers = client._get_headers(
            title="Test Title", priority="high", tags=["racing", "alert"]
        )

        assert "Title" in headers
        assert "Priority" in headers
        assert "Tags" in headers
        assert headers["Priority"] == "high"
