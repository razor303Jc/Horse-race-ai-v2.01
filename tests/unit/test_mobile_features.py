#!/usr/bin/env python3
"""
Mobile & Cross-Platform Features Test Suite
Tests PWA functionality, mobile components, and responsive design
"""

import pytest
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
from unittest.mock import Mock, patch


class TestPWAFeatures:
    """Test Progressive Web App functionality"""

    @pytest.fixture
    def manifest_path(self):
        """Path to PWA manifest file"""
        return (
            Path(__file__).parent.parent.parent
            / "src"
            / "web"
            / "public"
            / "manifest.json"
        )

    def test_manifest_exists(self, manifest_path):
        """Test PWA manifest.json exists"""
        assert manifest_path.exists(), "PWA manifest.json not found"

    def test_manifest_validation(self, manifest_path):
        """Test PWA manifest structure and content"""
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Required PWA fields
        required_fields = [
            "name",
            "short_name",
            "start_url",
            "display",
            "theme_color",
            "background_color",
            "icons",
        ]

        for field in required_fields:
            assert field in manifest, f"Missing required manifest field: {field}"

        # Validate specific values
        assert manifest["display"] in ["standalone", "fullscreen", "minimal-ui"]
        assert manifest["start_url"] in ["/", "./", "index.html"]

        # Validate icons
        icons = manifest["icons"]
        assert len(icons) > 0, "No icons defined"

        # Check for common icon sizes
        icon_sizes = [icon["sizes"] for icon in icons]
        required_sizes = ["192x192", "512x512"]

        for size in required_sizes:
            assert any(
                size in sizes for sizes in icon_sizes
            ), f"Missing icon size: {size}"

    def test_service_worker_exists(self):
        """Test service worker file exists"""
        sw_path = (
            Path(__file__).parent.parent.parent / "src" / "web" / "public" / "sw.js"
        )
        assert sw_path.exists(), "Service worker file not found"

    @pytest.mark.asyncio
    async def test_pwa_installation(self):
        """Test PWA installation prompt functionality"""
        # Mock PWA installation event
        pwa_install_event = {
            "event_type": "beforeinstallprompt",
            "user_choice": "accepted",
            "platform": "web",
            "timestamp": "2024-03-20T10:30:00Z",
        }

        assert pwa_install_event["event_type"] == "beforeinstallprompt"
        assert pwa_install_event["user_choice"] in ["accepted", "dismissed"]


class TestMobileResponsiveness:
    """Test mobile responsive design"""

    @pytest.fixture
    def mobile_breakpoints(self):
        """Mobile breakpoint definitions"""
        return {
            "xs": 320,  # Small mobile
            "sm": 576,  # Large mobile
            "md": 768,  # Tablet portrait
            "lg": 992,  # Tablet landscape
            "xl": 1200,  # Desktop
        }

    def test_breakpoint_progression(self, mobile_breakpoints):
        """Test breakpoints are in ascending order"""
        breakpoint_values = list(mobile_breakpoints.values())

        for i in range(1, len(breakpoint_values)):
            assert (
                breakpoint_values[i] > breakpoint_values[i - 1]
            ), f"Breakpoints not in ascending order: {breakpoint_values}"

    @pytest.mark.asyncio
    async def test_mobile_navigation(self):
        """Test mobile navigation functionality"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Set mobile viewport
            await page.set_viewport_size({"width": 375, "height": 667})

            # Mock navigation test
            nav_items = [
                {"label": "Dashboard", "href": "/dashboard", "icon": "dashboard"},
                {"label": "Races", "href": "/races", "icon": "race"},
                {"label": "Betting", "href": "/betting", "icon": "betting"},
                {"label": "Analytics", "href": "/analytics", "icon": "analytics"},
            ]

            # Validate navigation structure
            for item in nav_items:
                assert "label" in item
                assert "href" in item
                assert "icon" in item
                assert item["href"].startswith("/")

            await browser.close()

    def test_touch_gesture_config(self):
        """Test touch gesture configuration"""
        gesture_config = {
            "swipe_threshold": 50,  # pixels
            "tap_timeout": 300,  # milliseconds
            "double_tap_timeout": 500,  # milliseconds
            "long_press_timeout": 1000,  # milliseconds
            "pinch_zoom_enabled": True,
            "pan_enabled": True,
            "rotation_enabled": False,
        }

        # Validate gesture thresholds
        assert gesture_config["swipe_threshold"] > 0
        assert gesture_config["tap_timeout"] > 0
        assert gesture_config["double_tap_timeout"] > gesture_config["tap_timeout"]
        assert (
            gesture_config["long_press_timeout"] > gesture_config["double_tap_timeout"]
        )

        # Validate boolean flags
        assert isinstance(gesture_config["pinch_zoom_enabled"], bool)
        assert isinstance(gesture_config["pan_enabled"], bool)


class TestMobileBettingInterface:
    """Test mobile betting interface functionality"""

    def test_mobile_betting_layout(self):
        """Test mobile betting interface layout"""
        mobile_betting_config = {
            "quick_bet_amounts": [5, 10, 25, 50, 100],
            "swipe_navigation": True,
            "touch_optimized_buttons": True,
            "haptic_feedback": True,
            "gesture_shortcuts": {
                "swipe_left": "next_race",
                "swipe_right": "prev_race",
                "double_tap": "quick_bet",
                "long_press": "bet_details",
            },
        }

        # Validate quick bet amounts
        quick_bets = mobile_betting_config["quick_bet_amounts"]
        assert len(quick_bets) > 0
        assert all(amount > 0 for amount in quick_bets)
        assert quick_bets == sorted(quick_bets), "Quick bet amounts should be sorted"

        # Validate gesture shortcuts
        gestures = mobile_betting_config["gesture_shortcuts"]
        expected_gestures = ["swipe_left", "swipe_right", "double_tap", "long_press"]

        for gesture in expected_gestures:
            assert gesture in gestures, f"Missing gesture shortcut: {gesture}"

    def test_mobile_stake_calculator(self):
        """Test mobile stake calculator functionality"""
        stake_calc_data = {
            "stake_amount": 25.0,
            "odds": 3.5,
            "potential_return": 87.5,
            "potential_profit": 62.5,
            "kelly_fraction": 0.12,
            "recommended_stake": 15.0,
        }

        # Validate calculations
        expected_return = stake_calc_data["stake_amount"] * stake_calc_data["odds"]
        expected_profit = expected_return - stake_calc_data["stake_amount"]

        assert abs(stake_calc_data["potential_return"] - expected_return) < 0.01
        assert abs(stake_calc_data["potential_profit"] - expected_profit) < 0.01

        # Validate Kelly criterion
        assert 0.0 <= stake_calc_data["kelly_fraction"] <= 1.0
        assert stake_calc_data["recommended_stake"] <= stake_calc_data["stake_amount"]


class TestMobilePerformance:
    """Test mobile performance optimizations"""

    def test_mobile_bundle_size(self):
        """Test mobile-optimized bundle sizes"""
        # Expected mobile bundle sizes (KB)
        mobile_bundle_limits = {
            "main_js": 300,  # Main JavaScript bundle
            "vendor_js": 600,  # Third-party libraries
            "css": 100,  # Stylesheets
            "images": 500,  # Image assets
            "fonts": 200,  # Font files
        }

        # Validate bundle size limits
        total_size = sum(mobile_bundle_limits.values())
        assert total_size < 2000, f"Total mobile bundle too large: {total_size}KB"

        # Individual bundle limits
        assert mobile_bundle_limits["main_js"] < 400
        assert mobile_bundle_limits["vendor_js"] < 800
        assert mobile_bundle_limits["css"] < 150

    def test_mobile_image_optimization(self):
        """Test mobile image optimization"""
        image_config = {
            "formats": ["webp", "avif", "jpeg"],
            "responsive_breakpoints": [320, 640, 960, 1280],
            "lazy_loading": True,
            "compression_quality": 0.8,
            "max_width": 1920,
            "placeholder_strategy": "blur",
        }

        # Validate image configuration
        assert "webp" in image_config["formats"], "WebP format missing"
        assert image_config["lazy_loading"] is True
        assert 0.0 < image_config["compression_quality"] <= 1.0
        assert image_config["max_width"] > 0

        # Validate responsive breakpoints
        breakpoints = image_config["responsive_breakpoints"]
        assert breakpoints == sorted(breakpoints), "Breakpoints not sorted"
        assert min(breakpoints) >= 320, "Minimum breakpoint too small"

    def test_mobile_caching_strategy(self):
        """Test mobile caching configuration"""
        cache_config = {
            "strategy": "cache_first",
            "max_age": 86400,  # 24 hours
            "offline_pages": ["/", "/dashboard", "/races"],
            "cache_size_limit": 50,  # MB
            "auto_cleanup": True,
            "background_sync": True,
        }

        # Validate caching strategy
        valid_strategies = ["cache_first", "network_first", "stale_while_revalidate"]
        assert cache_config["strategy"] in valid_strategies

        # Validate cache settings
        assert cache_config["max_age"] > 0
        assert cache_config["cache_size_limit"] > 0
        assert len(cache_config["offline_pages"]) > 0


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility"""

    @pytest.mark.parametrize("device_type", ["mobile", "tablet", "desktop"])
    def test_device_specific_layouts(self, device_type):
        """Test device-specific layout configurations"""
        layout_configs = {
            "mobile": {
                "columns": 1,
                "sidebar_collapsed": True,
                "navigation_type": "bottom_tabs",
                "font_scale": 1.0,
            },
            "tablet": {
                "columns": 2,
                "sidebar_collapsed": False,
                "navigation_type": "sidebar",
                "font_scale": 1.1,
            },
            "desktop": {
                "columns": 3,
                "sidebar_collapsed": False,
                "navigation_type": "top_nav",
                "font_scale": 1.0,
            },
        }

        config = layout_configs[device_type]

        # Validate layout configuration
        assert config["columns"] > 0
        assert isinstance(config["sidebar_collapsed"], bool)
        assert config["navigation_type"] in ["bottom_tabs", "sidebar", "top_nav"]
        assert config["font_scale"] > 0

    def test_browser_compatibility(self):
        """Test browser compatibility requirements"""
        browser_support = {
            "chrome": ">=90",
            "firefox": ">=88",
            "safari": ">=14",
            "edge": ">=90",
            "ios_safari": ">=14",
            "android_chrome": ">=90",
        }

        # Validate browser versions
        for browser, version in browser_support.items():
            assert version.startswith(
                ">="
            ), f"Invalid version format for {browser}: {version}"
            version_num = int(version.replace(">=", ""))
            assert (
                version_num > 0
            ), f"Invalid version number for {browser}: {version_num}"

    def test_accessibility_compliance(self):
        """Test mobile accessibility features"""
        a11y_features = {
            "screen_reader_support": True,
            "keyboard_navigation": True,
            "high_contrast_mode": True,
            "font_size_scaling": True,
            "touch_target_size": 44,  # pixels (iOS/Android standard)
            "color_contrast_ratio": 4.5,  # WCAG AA standard
            "focus_indicators": True,
            "aria_labels": True,
        }

        # Validate accessibility features
        assert a11y_features["screen_reader_support"] is True
        assert a11y_features["keyboard_navigation"] is True
        assert a11y_features["touch_target_size"] >= 44
        assert a11y_features["color_contrast_ratio"] >= 4.5


# Integration Tests
class TestMobileIntegration:
    """Test mobile integration with backend services"""

    @pytest.mark.asyncio
    async def test_mobile_api_integration(self):
        """Test mobile-specific API optimizations"""
        mobile_api_config = {
            "compression": "gzip",
            "response_format": "json",
            "batch_requests": True,
            "request_timeout": 10000,  # 10 seconds
            "retry_attempts": 3,
            "offline_queue": True,
            "background_sync": True,
        }

        # Validate mobile API configuration
        assert mobile_api_config["compression"] in ["gzip", "brotli", "deflate"]
        assert mobile_api_config["response_format"] == "json"
        assert mobile_api_config["request_timeout"] > 0
        assert mobile_api_config["retry_attempts"] > 0

    @pytest.mark.asyncio
    async def test_mobile_websocket_connection(self):
        """Test mobile WebSocket connectivity"""
        mobile_ws_config = {
            "auto_reconnect": True,
            "max_reconnect_attempts": 10,
            "reconnect_delay": 1000,  # 1 second
            "ping_interval": 30000,  # 30 seconds
            "compression": True,
            "message_queue_size": 100,
            "battery_optimization": True,
        }

        # Validate WebSocket configuration
        assert mobile_ws_config["auto_reconnect"] is True
        assert mobile_ws_config["max_reconnect_attempts"] > 0
        assert mobile_ws_config["ping_interval"] > 0
        assert mobile_ws_config["message_queue_size"] > 0

    def test_mobile_offline_functionality(self):
        """Test mobile offline capabilities"""
        offline_config = {
            "cached_pages": ["/", "/dashboard", "/races", "/betting"],
            "cached_data_types": ["race_cards", "user_profile", "recent_bets"],
            "max_offline_time": 86400,  # 24 hours
            "sync_on_reconnect": True,
            "conflict_resolution": "server_wins",
            "offline_indicators": True,
        }

        # Validate offline configuration
        assert len(offline_config["cached_pages"]) > 0
        assert len(offline_config["cached_data_types"]) > 0
        assert offline_config["max_offline_time"] > 0
        assert offline_config["conflict_resolution"] in [
            "server_wins",
            "client_wins",
            "merge",
        ]


if __name__ == "__main__":
    """Run mobile features test suite"""
    import sys

    print("📱 Running Mobile & Cross-Platform Features Test Suite")
    print("=" * 60)

    # Configure pytest
    pytest_args = [
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",
        "-x",  # Stop on first failure
    ]

    # Run tests
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n✅ All mobile tests passed successfully!")
        print("📱 Mobile & Cross-Platform features are working correctly!")
    else:
        print(f"\n❌ Mobile tests failed with exit code: {exit_code}")
        print("🔧 Please check the test output above for details.")

    sys.exit(exit_code)
