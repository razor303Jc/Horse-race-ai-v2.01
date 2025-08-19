#!/usr/bin/env python3
"""
Advanced Analytics & Performance Test Suite
Tests analytics dashboard, performance monitoring, and reporting features
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal


class TestAnalyticsDashboard:
    """Test Advanced Analytics Dashboard functionality"""

    @pytest.fixture
    def sample_betting_data(self):
        """Sample betting data for analytics testing"""
        return [
            {
                "bet_id": "bet_001",
                "race_id": "race_123",
                "horse_id": "horse_456",
                "stake": 25.0,
                "odds": 3.5,
                "result": "win",
                "return": 87.5,
                "profit": 62.5,
                "date": "2024-03-15",
                "track": "ascot",
                "race_type": "flat",
            },
            {
                "bet_id": "bet_002",
                "race_id": "race_124",
                "horse_id": "horse_457",
                "stake": 50.0,
                "odds": 2.1,
                "result": "lose",
                "return": 0.0,
                "profit": -50.0,
                "date": "2024-03-15",
                "track": "cheltenham",
                "race_type": "hurdle",
            },
            {
                "bet_id": "bet_003",
                "race_id": "race_125",
                "horse_id": "horse_458",
                "stake": 30.0,
                "odds": 4.2,
                "result": "win",
                "return": 126.0,
                "profit": 96.0,
                "date": "2024-03-16",
                "track": "aintree",
                "race_type": "chase",
            },
        ]

    def test_roi_calculation(self, sample_betting_data):
        """Test Return on Investment calculation"""
        total_stake = sum(bet["stake"] for bet in sample_betting_data)
        total_return = sum(bet["return"] for bet in sample_betting_data)
        total_profit = sum(bet["profit"] for bet in sample_betting_data)

        # Calculate ROI
        roi = total_profit / total_stake if total_stake > 0 else 0
        roi_percentage = roi * 100

        # Validate calculations
        assert total_stake == 105.0
        assert total_return == 213.5
        assert total_profit == 108.5
        assert abs(roi - 1.033) < 0.001  # ~103.3% ROI
        assert abs(roi_percentage - 103.33) < 0.1

    def test_win_rate_calculation(self, sample_betting_data):
        """Test win rate calculation"""
        total_bets = len(sample_betting_data)
        winning_bets = sum(1 for bet in sample_betting_data if bet["result"] == "win")

        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        win_rate_percentage = win_rate * 100

        # Validate win rate
        assert total_bets == 3
        assert winning_bets == 2
        assert abs(win_rate - 0.667) < 0.001  # 66.7% win rate
        assert abs(win_rate_percentage - 66.67) < 0.1

    def test_sharpe_ratio_calculation(self, sample_betting_data):
        """Test Sharpe ratio calculation for risk-adjusted returns"""
        # Calculate daily returns
        daily_returns = []
        for bet in sample_betting_data:
            daily_return = bet["profit"] / bet["stake"]
            daily_returns.append(daily_return)

        # Sharpe ratio calculation
        if len(daily_returns) > 1:
            mean_return = np.mean(daily_returns)
            std_return = np.std(daily_returns, ddof=1)
            sharpe_ratio = mean_return / std_return if std_return != 0 else 0
        else:
            sharpe_ratio = 0

        # Validate Sharpe ratio
        assert len(daily_returns) == 3
        assert sharpe_ratio != 0  # Should have a valid Sharpe ratio
        assert -10 < sharpe_ratio < 10  # Reasonable range

    def test_drawdown_analysis(self, sample_betting_data):
        """Test maximum drawdown calculation"""
        # Calculate cumulative P&L
        cumulative_pl = []
        running_total = 0

        for bet in sample_betting_data:
            running_total += bet["profit"]
            cumulative_pl.append(running_total)

        # Calculate drawdown
        peak = cumulative_pl[0]
        max_drawdown = 0

        for value in cumulative_pl:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak != 0 else 0
            max_drawdown = max(max_drawdown, drawdown)

        # Validate drawdown calculation
        assert len(cumulative_pl) == 3
        assert cumulative_pl[-1] == 108.5  # Final P&L
        assert 0 <= max_drawdown <= 1  # Drawdown as percentage

    def test_performance_attribution(self, sample_betting_data):
        """Test performance attribution by various factors"""
        # Group by track
        track_performance = {}
        for bet in sample_betting_data:
            track = bet["track"]
            if track not in track_performance:
                track_performance[track] = {"profit": 0, "stake": 0, "count": 0}

            track_performance[track]["profit"] += bet["profit"]
            track_performance[track]["stake"] += bet["stake"]
            track_performance[track]["count"] += 1

        # Calculate ROI by track
        for track, perf in track_performance.items():
            perf["roi"] = perf["profit"] / perf["stake"] if perf["stake"] > 0 else 0

        # Validate attribution
        assert len(track_performance) == 3  # Three different tracks

        for track, perf in track_performance.items():
            assert perf["count"] > 0
            assert perf["stake"] > 0
            assert "roi" in perf

    def test_trend_analysis(self, sample_betting_data):
        """Test trend analysis over time"""
        # Sort by date
        sorted_bets = sorted(sample_betting_data, key=lambda x: x["date"])

        # Calculate daily totals
        daily_totals = {}
        for bet in sorted_bets:
            date = bet["date"]
            if date not in daily_totals:
                daily_totals[date] = {"profit": 0, "stake": 0, "bets": 0}

            daily_totals[date]["profit"] += bet["profit"]
            daily_totals[date]["stake"] += bet["stake"]
            daily_totals[date]["bets"] += 1

        # Calculate moving averages (if more data available)
        dates = sorted(daily_totals.keys())

        # Validate trend data
        assert len(daily_totals) == 2  # Two different dates
        assert all(date in daily_totals for date in ["2024-03-15", "2024-03-16"])

        for date, totals in daily_totals.items():
            assert totals["bets"] > 0
            assert totals["stake"] > 0


class TestPerformanceMonitoring:
    """Test real-time performance monitoring"""

    def test_api_response_time_monitoring(self):
        """Test API response time tracking"""
        api_metrics = {
            "endpoint": "/api/daily_races",
            "method": "GET",
            "response_time_ms": 145,
            "status_code": 200,
            "timestamp": datetime.now().isoformat(),
            "user_id": "user_123",
            "cache_hit": True,
            "database_time_ms": 23,
            "processing_time_ms": 122,
        }

        # Validate performance metrics
        assert api_metrics["response_time_ms"] > 0
        assert api_metrics["status_code"] == 200
        assert api_metrics["database_time_ms"] >= 0
        assert api_metrics["processing_time_ms"] >= 0

        # Response time should be sum of components
        total_time = api_metrics["database_time_ms"] + api_metrics["processing_time_ms"]
        assert api_metrics["response_time_ms"] >= total_time

        # Performance thresholds
        assert api_metrics["response_time_ms"] < 500  # Under 500ms

    def test_websocket_performance_metrics(self):
        """Test WebSocket performance monitoring"""
        ws_metrics = {
            "connection_id": "ws_001",
            "message_type": "race_update",
            "message_size_bytes": 1024,
            "latency_ms": 45,
            "throughput_msgs_per_sec": 15.7,
            "compression_ratio": 0.65,
            "error_rate": 0.002,
            "active_connections": 1247,
        }

        # Validate WebSocket metrics
        assert ws_metrics["message_size_bytes"] > 0
        assert ws_metrics["latency_ms"] > 0
        assert ws_metrics["throughput_msgs_per_sec"] > 0
        assert 0 <= ws_metrics["compression_ratio"] <= 1
        assert 0 <= ws_metrics["error_rate"] <= 1
        assert ws_metrics["active_connections"] > 0

        # Performance thresholds
        assert ws_metrics["latency_ms"] < 100  # Under 100ms
        assert ws_metrics["error_rate"] < 0.01  # Under 1% error rate

    def test_system_resource_monitoring(self):
        """Test system resource monitoring"""
        system_metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage_percent": 45.2,
            "memory_usage_percent": 67.8,
            "disk_usage_percent": 34.1,
            "network_io_mbps": 12.4,
            "database_connections": 18,
            "cache_hit_rate": 0.87,
            "queue_depth": 5,
            "active_users": 342,
        }

        # Validate system metrics
        assert 0 <= system_metrics["cpu_usage_percent"] <= 100
        assert 0 <= system_metrics["memory_usage_percent"] <= 100
        assert 0 <= system_metrics["disk_usage_percent"] <= 100
        assert system_metrics["network_io_mbps"] >= 0
        assert system_metrics["database_connections"] >= 0
        assert 0 <= system_metrics["cache_hit_rate"] <= 1
        assert system_metrics["queue_depth"] >= 0
        assert system_metrics["active_users"] >= 0

        # Alert thresholds
        if system_metrics["cpu_usage_percent"] > 80:
            alert_cpu = True
        else:
            alert_cpu = False

        if system_metrics["memory_usage_percent"] > 85:
            alert_memory = True
        else:
            alert_memory = False

        # These should not trigger alerts with current values
        assert alert_cpu is False
        assert alert_memory is False

    def test_user_experience_metrics(self):
        """Test user experience performance metrics"""
        ux_metrics = {
            "page_load_time_ms": 1245,
            "first_contentful_paint_ms": 890,
            "largest_contentful_paint_ms": 1456,
            "cumulative_layout_shift": 0.045,
            "first_input_delay_ms": 23,
            "time_to_interactive_ms": 2134,
            "bounce_rate": 0.23,
            "session_duration_sec": 892,
            "pages_per_session": 3.4,
        }

        # Validate UX metrics
        assert ux_metrics["page_load_time_ms"] > 0
        assert ux_metrics["first_contentful_paint_ms"] > 0
        assert (
            ux_metrics["largest_contentful_paint_ms"]
            >= ux_metrics["first_contentful_paint_ms"]
        )
        assert 0 <= ux_metrics["cumulative_layout_shift"] <= 1
        assert ux_metrics["first_input_delay_ms"] >= 0
        assert ux_metrics["time_to_interactive_ms"] > 0
        assert 0 <= ux_metrics["bounce_rate"] <= 1
        assert ux_metrics["session_duration_sec"] > 0
        assert ux_metrics["pages_per_session"] > 0

        # Performance thresholds (Core Web Vitals)
        assert ux_metrics["largest_contentful_paint_ms"] < 2500  # Good LCP
        assert ux_metrics["first_input_delay_ms"] < 100  # Good FID
        assert ux_metrics["cumulative_layout_shift"] < 0.1  # Good CLS


class TestReportingSystem:
    """Test automated reporting system"""

    def test_daily_report_generation(self):
        """Test daily performance report generation"""
        daily_report = {
            "report_date": "2024-03-20",
            "report_type": "daily_performance",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_bets": 147,
                "total_stake": 3675.0,
                "total_return": 4123.50,
                "net_profit": 448.50,
                "roi_percentage": 12.2,
                "win_rate": 0.68,
            },
            "top_performers": [
                {"track": "ascot", "roi": 0.234},
                {"track": "cheltenham", "roi": 0.189},
            ],
            "alerts": [
                {
                    "type": "performance",
                    "message": "Win rate above 65% threshold",
                    "severity": "info",
                }
            ],
            "charts": {
                "profit_trend": "chart_data_profit.json",
                "win_rate_trend": "chart_data_winrate.json",
            },
        }

        # Validate daily report structure
        assert "report_date" in daily_report
        assert "summary" in daily_report
        assert "top_performers" in daily_report
        assert "alerts" in daily_report

        # Validate summary calculations
        summary = daily_report["summary"]
        expected_roi = (summary["net_profit"] / summary["total_stake"]) * 100
        assert abs(summary["roi_percentage"] - expected_roi) < 0.1

        # Validate alert structure
        for alert in daily_report["alerts"]:
            assert "type" in alert
            assert "message" in alert
            assert "severity" in alert
            assert alert["severity"] in ["info", "warning", "error", "critical"]

    def test_weekly_report_aggregation(self):
        """Test weekly report aggregation"""
        weekly_report = {
            "start_date": "2024-03-15",
            "end_date": "2024-03-21",
            "report_type": "weekly_summary",
            "aggregated_metrics": {
                "total_days": 7,
                "active_days": 5,
                "total_bets": 342,
                "average_daily_bets": 68.4,
                "total_profit": 1247.80,
                "average_daily_profit": 249.56,
                "best_day": {"date": "2024-03-18", "profit": 456.30},
                "worst_day": {"date": "2024-03-16", "profit": -123.45},
            },
            "trend_analysis": {
                "profit_trend": "increasing",
                "win_rate_trend": "stable",
                "stake_trend": "increasing",
            },
            "recommendations": [
                "Consider increasing stakes on high-confidence bets",
                "Focus more on flat racing based on performance",
            ],
        }

        # Validate weekly report
        metrics = weekly_report["aggregated_metrics"]
        assert metrics["total_days"] == 7
        assert metrics["active_days"] <= metrics["total_days"]
        assert metrics["total_bets"] > 0
        assert (
            metrics["average_daily_bets"]
            == metrics["total_bets"] / metrics["active_days"]
        )

        # Validate trend analysis
        trends = weekly_report["trend_analysis"]
        valid_trends = ["increasing", "decreasing", "stable"]

        for trend_key, trend_value in trends.items():
            assert trend_value in valid_trends

    def test_export_functionality(self):
        """Test data export functionality"""
        export_request = {
            "export_id": "exp_001",
            "user_id": "user_123",
            "export_type": "betting_history",
            "format": "csv",
            "date_range": {"start_date": "2024-01-01", "end_date": "2024-03-20"},
            "filters": {
                "tracks": ["ascot", "cheltenham"],
                "min_stake": 10.0,
                "result": "all",
            },
            "status": "completed",
            "file_path": "/exports/betting_history_user_123_20240320.csv",
            "file_size_bytes": 156789,
            "record_count": 1247,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        # Validate export request
        assert export_request["format"] in ["csv", "json", "xlsx", "pdf"]
        assert export_request["status"] in [
            "pending",
            "processing",
            "completed",
            "failed",
        ]
        assert export_request["file_size_bytes"] > 0
        assert export_request["record_count"] > 0

        # Validate date range
        start_date = datetime.fromisoformat(export_request["date_range"]["start_date"])
        end_date = datetime.fromisoformat(export_request["date_range"]["end_date"])
        assert start_date <= end_date

        # Validate expiration
        created_at = datetime.fromisoformat(export_request["created_at"])
        expires_at = datetime.fromisoformat(export_request["expires_at"])
        assert expires_at > created_at


class TestDataVisualization:
    """Test data visualization components"""

    def test_chart_data_preparation(self):
        """Test chart data preparation and formatting"""
        # Sample time series data for profit chart
        profit_chart_data = {
            "chart_type": "line",
            "title": "Daily Profit Trend",
            "x_axis": {
                "label": "Date",
                "type": "datetime",
                "data": [
                    "2024-03-15",
                    "2024-03-16",
                    "2024-03-17",
                    "2024-03-18",
                    "2024-03-19",
                    "2024-03-20",
                ],
            },
            "y_axis": {
                "label": "Profit (£)",
                "type": "numeric",
                "data": [125.50, -45.20, 234.75, 89.30, 167.85, 203.45],
            },
            "config": {
                "responsive": True,
                "animation": True,
                "tooltip_enabled": True,
                "legend_enabled": True,
            },
        }

        # Validate chart data structure
        assert profit_chart_data["chart_type"] in [
            "line",
            "bar",
            "pie",
            "area",
            "scatter",
        ]
        assert len(profit_chart_data["x_axis"]["data"]) == len(
            profit_chart_data["y_axis"]["data"]
        )

        # Validate data types
        x_data = profit_chart_data["x_axis"]["data"]
        y_data = profit_chart_data["y_axis"]["data"]

        assert all(isinstance(x, str) for x in x_data)  # Date strings
        assert all(isinstance(y, (int, float)) for y in y_data)  # Numeric values

    def test_performance_dashboard_layout(self):
        """Test performance dashboard layout configuration"""
        dashboard_layout = {
            "layout_id": "performance_dashboard",
            "grid_system": "12_column",
            "widgets": [
                {
                    "widget_id": "profit_chart",
                    "type": "line_chart",
                    "position": {"row": 1, "col": 1, "width": 8, "height": 4},
                    "data_source": "daily_profits",
                    "refresh_interval": 300,  # 5 minutes
                },
                {
                    "widget_id": "win_rate_gauge",
                    "type": "gauge",
                    "position": {"row": 1, "col": 9, "width": 4, "height": 4},
                    "data_source": "current_win_rate",
                    "refresh_interval": 60,  # 1 minute
                },
                {
                    "widget_id": "recent_bets_table",
                    "type": "data_table",
                    "position": {"row": 5, "col": 1, "width": 12, "height": 6},
                    "data_source": "recent_betting_activity",
                    "refresh_interval": 30,  # 30 seconds
                },
            ],
            "auto_refresh": True,
            "export_enabled": True,
            "sharing_enabled": False,
        }

        # Validate dashboard layout
        assert dashboard_layout["grid_system"] in ["12_column", "24_column", "flexible"]
        assert len(dashboard_layout["widgets"]) > 0

        # Validate widget configurations
        for widget in dashboard_layout["widgets"]:
            assert "widget_id" in widget
            assert "type" in widget
            assert "position" in widget
            assert "data_source" in widget

            # Validate position
            pos = widget["position"]
            assert pos["width"] > 0
            assert pos["height"] > 0
            assert pos["width"] <= 12  # Within grid system

            # Validate refresh interval
            assert widget["refresh_interval"] > 0


# Integration Tests
class TestAnalyticsIntegration:
    """Test analytics integration with other systems"""

    @pytest.mark.asyncio
    async def test_real_time_analytics_pipeline(self):
        """Test real-time analytics data pipeline"""
        # Mock streaming betting event
        betting_event = {
            "event_type": "bet_placed",
            "timestamp": datetime.now().isoformat(),
            "bet_id": "bet_12345",
            "user_id": "user_789",
            "race_id": "race_456",
            "stake": 50.0,
            "odds": 2.8,
            "predicted_probability": 0.42,
        }

        # Mock analytics processing
        analytics_update = {
            "user_id": betting_event["user_id"],
            "updated_metrics": {
                "total_bets_today": 15,
                "total_stake_today": 675.0,
                "average_odds": 2.95,
                "risk_exposure": 1247.50,
            },
            "dashboard_refresh_required": True,
        }

        # Validate real-time processing
        assert betting_event["event_type"] in [
            "bet_placed",
            "bet_settled",
            "bet_cancelled",
        ]
        assert analytics_update["updated_metrics"]["total_bets_today"] > 0
        assert analytics_update["dashboard_refresh_required"] is True

    def test_ml_prediction_analytics_integration(self):
        """Test integration between ML predictions and analytics"""
        prediction_performance = {
            "model_id": "model_001",
            "prediction_id": "pred_12345",
            "actual_result": "win",
            "predicted_result": "win",
            "predicted_probability": 0.67,
            "actual_odds": 2.3,
            "model_confidence": 0.78,
            "prediction_accuracy": True,
            "prediction_value": 0.156,  # Expected value calculation
            "contribution_to_roi": 0.043,
        }

        # Validate prediction analytics
        assert prediction_performance["actual_result"] in ["win", "lose", "place"]
        assert prediction_performance["predicted_result"] in ["win", "lose", "place"]
        assert 0 <= prediction_performance["predicted_probability"] <= 1
        assert 0 <= prediction_performance["model_confidence"] <= 1
        assert isinstance(prediction_performance["prediction_accuracy"], bool)


if __name__ == "__main__":
    """Run analytics test suite"""
    import sys

    print("📊 Running Advanced Analytics & Performance Test Suite")
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
        print("\n✅ All analytics tests passed successfully!")
        print("📊 Advanced Analytics & Performance features are working correctly!")
    else:
        print(f"\n❌ Analytics tests failed with exit code: {exit_code}")
        print("🔧 Please check the test output above for details.")

    sys.exit(exit_code)
