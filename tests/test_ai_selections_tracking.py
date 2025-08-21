#!/usr/bin/env python3
"""
Test Suite for AI Selections Tracking System
===========================================

Comprehensive tests for AI horse selections tracking with profit/loss ROI
and relationships to race result data.
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from src.horse_racing_ai.analytics.ai_selections_tracker import (
    AISelectionsTracker,
    SelectionAnalytics,
)
from src.horse_racing_ai.integration.ai_selections_integration import (
    AISelectionsIntegrationSystem,
)


class TestAISelectionsTracker(unittest.TestCase):
    """Test cases for AI Selections Tracker."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_ai_selections.db"
        self.tracker = AISelectionsTracker(str(self.db_path))

        # Sample race data
        self.race_data = {
            "race_id": "TEST_2025-08-20_R1",
            "race_date": "2025-08-20T14:30:00Z",
            "course": "Test Course",
            "race_number": 1,
            "distance": 6.0,
            "class": "Class 2",
            "field_size": 8,
            "weather": "Clear",
            "track_condition": "Good",
        }

        # Sample AI selection
        self.selection_data = {
            "horse_name": "Test Horse",
            "horse_id": "TH001",
            "jockey": "Test Jockey",
            "trainer": "Test Trainer",
            "win_probability": 0.35,
            "confidence_score": 0.78,
            "odds_decimal": 3.5,
            "selection_type": "WIN",
            "stake_amount": 10.0,
        }

    def tearDown(self):
        """Clean up test environment."""
        self.tracker.close()
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_record_ai_selection(self):
        """Test recording AI selection."""
        selection_id = self.tracker.record_ai_selection(
            self.race_data, self.selection_data, "consensus", "value_bet"
        )

        self.assertIsInstance(selection_id, str)
        self.assertIn("TEST_2025-08-20_R1", selection_id)
        self.assertIn("Test Horse", selection_id)
        self.assertIn("consensus", selection_id)

    def test_update_selection_result(self):
        """Test updating selection with results."""
        # Record selection first
        selection_id = self.tracker.record_ai_selection(
            self.race_data, self.selection_data, "consensus", "value_bet"
        )

        # Update with result
        result_data = {"position": 2}
        financial_data = {"stake": 10.0, "payout": 17.5}

        success = self.tracker.update_selection_result(
            selection_id, result_data, financial_data
        )

        self.assertTrue(success)

    def test_selection_analytics_empty(self):
        """Test analytics with no selections."""
        analytics = self.tracker.get_selection_analytics()

        self.assertEqual(analytics.total_selections, 0)
        self.assertEqual(analytics.overall_accuracy, 0.0)
        self.assertEqual(analytics.roi_percentage, 0.0)

    def test_selection_analytics_with_data(self):
        """Test analytics with selection data."""
        # Record multiple selections
        for i in range(5):
            selection_data = self.selection_data.copy()
            selection_data["horse_name"] = f"Test Horse {i}"

            selection_id = self.tracker.record_ai_selection(
                self.race_data, selection_data, "consensus", "value_bet"
            )

            # Update with varying results
            position = 1 if i < 2 else 4  # 2 winners, 3 losers
            payout = 35.0 if position == 1 else 0.0

            self.tracker.update_selection_result(
                selection_id, {"position": position}, {"stake": 10.0, "payout": payout}
            )

        analytics = self.tracker.get_selection_analytics()

        self.assertEqual(analytics.total_selections, 5)
        self.assertAlmostEqual(analytics.overall_accuracy, 0.4, places=1)  # 2/5
        self.assertGreater(analytics.roi_percentage, 0)  # Should be profitable

    def test_confidence_calibration(self):
        """Test confidence calibration calculation."""
        # Test with empty data
        calibration = self.tracker._calculate_confidence_calibration([])
        self.assertEqual(calibration, 0.0)

        # Test with mock selection data
        mock_selections = []
        for i in range(10):
            mock_selection = Mock()
            mock_selection.confidence_score = 0.8  # High confidence
            mock_selection.was_correct = i < 8  # 80% accuracy
            mock_selections.append(mock_selection)

        calibration = self.tracker._calculate_confidence_calibration(mock_selections)
        self.assertGreater(calibration, 0.8)  # Should be well calibrated

    def test_strategy_performance_calculation(self):
        """Test strategy performance calculation."""
        mock_selections = []

        # Value bet strategy
        for i in range(5):
            mock_selection = Mock()
            mock_selection.betting_strategy = "value_bet"
            mock_selection.was_correct = i < 3  # 60% accuracy
            mock_selection.stake_placed = 10.0
            mock_selection.payout_received = 15.0 if i < 3 else 0.0
            mock_selections.append(mock_selection)

        # 80/20 strategy
        for i in range(3):
            mock_selection = Mock()
            mock_selection.betting_strategy = "80_20"
            mock_selection.was_correct = i < 2  # 67% accuracy
            mock_selection.stake_placed = 10.0
            mock_selection.payout_received = 20.0 if i < 2 else 0.0
            mock_selections.append(mock_selection)

        performance = self.tracker._calculate_strategy_performance(mock_selections)

        self.assertIn("value_bet", performance)
        self.assertIn("80_20", performance)
        self.assertEqual(performance["value_bet"]["selections"], 5)
        self.assertEqual(performance["80_20"]["selections"], 3)

    def test_risk_metrics_calculation(self):
        """Test risk metrics calculation."""
        mock_selections = []

        # Create selections with varying profit/loss
        profits = [10, -10, 15, -5, -15, 20, -10, 5]

        for i, profit in enumerate(profits):
            mock_selection = Mock()
            mock_selection.race_date = datetime.utcnow() - timedelta(days=i)
            mock_selection.profit_loss = profit
            mock_selections.append(mock_selection)

        risk_metrics = self.tracker._calculate_risk_metrics(mock_selections)

        self.assertIn("max_drawdown", risk_metrics)
        self.assertIn("consecutive_losses", risk_metrics)
        self.assertIn("volatility", risk_metrics)
        self.assertGreater(risk_metrics["volatility"], 0)

    def test_export_selection_data(self):
        """Test data export functionality."""
        # Record a selection
        selection_id = self.tracker.record_ai_selection(
            self.race_data, self.selection_data, "consensus", "value_bet"
        )

        # Update with result
        self.tracker.update_selection_result(
            selection_id, {"position": 1}, {"stake": 10.0, "payout": 35.0}
        )

        # Export data
        file_path = self.tracker.export_selection_data(format_type="csv")

        self.assertTrue(Path(file_path).exists())

        # Verify CSV content
        df = pd.read_csv(file_path)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["horse_name"], "Test Horse")

        # Clean up
        Path(file_path).unlink()

    def test_contextual_analysis(self):
        """Test contextual analysis generation."""
        # Record sufficient selections for analysis
        for i in range(15):
            selection_data = self.selection_data.copy()
            selection_data["horse_name"] = f"Test Horse {i}"

            selection_id = self.tracker.record_ai_selection(
                self.race_data, selection_data, "consensus", "value_bet"
            )

            # Varied results
            position = 1 if i % 3 == 0 else 4
            payout = 35.0 if position == 1 else 0.0

            self.tracker.update_selection_result(
                selection_id, {"position": position}, {"stake": 10.0, "payout": payout}
            )

        analysis = self.tracker.generate_contextual_analysis(period_days=30)

        self.assertIn("performance_summary", analysis)
        self.assertIn("strategy_insights", analysis)
        self.assertIn("recommendations", analysis)
        self.assertEqual(analysis["performance_summary"]["total_selections"], 15)


class TestAISelectionsIntegration(unittest.TestCase):
    """Test cases for AI Selections Integration System."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Mock the database paths
        selections_db = Path(self.temp_dir) / "test_selections.db"
        performance_db = Path(self.temp_dir) / "test_performance.db"

        with (
            patch(
                "src.horse_racing_ai.integration.ai_selections_integration.AISelectionsTracker"
            ),
            patch(
                "src.horse_racing_ai.integration.ai_selections_integration.EnhancedPerformanceTracker"
            ),
            patch(
                "src.horse_racing_ai.integration.ai_selections_integration.AIBettingIntegrationSystem"
            ),
        ):

            self.integration = AISelectionsIntegrationSystem(
                str(selections_db), str(performance_db)
            )

    def tearDown(self):
        """Clean up test environment."""
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_process_race_predictions(self):
        """Test processing race predictions."""
        race_data = {
            "race_id": "TEST_2025-08-20_R1",
            "race_date": "2025-08-20T14:30:00Z",
            "course": "Test Course",
            "field_size": 8,
        }

        ai_predictions = {
            "consensus": [
                {
                    "horse_name": "Test Horse 1",
                    "win_probability": 0.35,
                    "confidence_score": 0.78,
                    "odds_decimal": 3.5,
                }
            ]
        }

        # Mock the selections tracker
        mock_tracker = Mock()
        mock_tracker.record_ai_selection.return_value = "test_selection_id"
        self.integration.selections_tracker = mock_tracker

        # Mock performance tracker
        mock_performance = Mock()
        self.integration.performance_tracker = mock_performance

        selection_ids = self.integration.process_race_predictions(
            race_data, ai_predictions, ["value_bet"]
        )

        self.assertIsInstance(selection_ids, dict)
        mock_tracker.record_ai_selection.assert_called()
        mock_performance.record_race_prediction.assert_called()

    def test_update_race_results(self):
        """Test updating race results."""
        race_id = "TEST_2025-08-20_R1"
        actual_results = [{"horse_name": "Test Horse 1", "position": 1}]

        # Mock the selections tracker
        mock_tracker = Mock()
        mock_tracker.update_selection_result.return_value = True
        self.integration.selections_tracker = mock_tracker

        # Mock getting race selections
        self.integration._get_race_selections = Mock(
            return_value=[{"selection_id": "test_id", "horse_name": "Test Horse 1"}]
        )

        # Mock other methods
        self.integration._calculate_accuracy_impact = Mock(
            return_value={"overall_change": 0.02}
        )
        self.integration._extract_learning_signals = Mock(return_value=[])
        self.integration._update_contextual_analysis = Mock()

        summary = self.integration.update_race_results(race_id, actual_results)

        self.assertIsInstance(summary, dict)
        self.assertIn("race_id", summary)
        self.assertIn("selections_updated", summary)
        mock_tracker.update_selection_result.assert_called()

    def test_comprehensive_analysis(self):
        """Test comprehensive analysis generation."""
        # Mock analytics
        mock_analytics = Mock()
        mock_analytics.total_selections = 50
        mock_analytics.overall_accuracy = 0.35
        mock_analytics.roi_percentage = 8.5
        mock_analytics.method_performance = {
            "consensus": {"accuracy": 0.4, "roi": 10.0}
        }
        mock_analytics.strategy_performance = {
            "value_bet": {"accuracy": 0.38, "roi": 9.2}
        }

        # Mock tracker methods
        mock_tracker = Mock()
        mock_tracker.get_selection_analytics.return_value = mock_analytics
        mock_tracker.generate_contextual_analysis.return_value = {"status": "success"}
        self.integration.selections_tracker = mock_tracker

        # Mock performance tracker
        mock_performance = Mock()
        mock_performance.get_performance_summary.return_value = {"method_accuracy": {}}
        self.integration.performance_tracker = mock_performance

        # Mock other methods
        self.integration._compare_methods = Mock(return_value={})
        self.integration._assess_overall_risk = Mock(return_value="LOW")
        self.integration._calculate_edge_exploitation = Mock(return_value=0.65)
        self.integration._generate_improvement_recommendations = Mock(return_value=[])
        self.integration._extract_ai_learning_signals = Mock(return_value={})

        analysis = self.integration.generate_comprehensive_analysis(period_days=30)

        self.assertIsInstance(analysis, dict)
        self.assertIn("analysis_period", analysis)
        self.assertIn("selections_performance", analysis)
        self.assertIn("method_comparison", analysis)
        self.assertIn("strategy_effectiveness", analysis)

    def test_real_time_performance(self):
        """Test real-time performance monitoring."""
        # Mock analytics for today and week
        today_analytics = Mock()
        today_analytics.total_selections = 5
        today_analytics.overall_accuracy = 0.4
        today_analytics.roi_percentage = 12.0
        today_analytics.net_profit = 25.0

        week_analytics = Mock()
        week_analytics.total_selections = 30
        week_analytics.overall_accuracy = 0.35
        week_analytics.roi_percentage = 8.5
        week_analytics.net_profit = 125.0

        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_selection_analytics.side_effect = [
            today_analytics,
            week_analytics,
        ]
        self.integration.selections_tracker = mock_tracker

        # Mock status determination
        self.integration._determine_system_status = Mock(return_value="GOOD")

        performance = self.integration.get_real_time_performance()

        self.assertIsInstance(performance, dict)
        self.assertIn("timestamp", performance)
        self.assertIn("today", performance)
        self.assertIn("week", performance)
        self.assertIn("status", performance)
        self.assertEqual(performance["status"], "GOOD")


class TestSelectionAnalytics(unittest.TestCase):
    """Test cases for Selection Analytics data class."""

    def test_selection_analytics_creation(self):
        """Test creating SelectionAnalytics object."""
        analytics = SelectionAnalytics(
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            total_selections=50,
            selections_per_day=7.14,
            win_accuracy=0.35,
            place_accuracy=0.65,
            overall_accuracy=0.42,
            confidence_calibration=0.78,
            total_stakes=500.0,
            total_payouts=550.0,
            net_profit=50.0,
            roi_percentage=10.0,
            profit_factor=1.25,
            strategy_performance={"value_bet": {"roi": 12.0}},
            method_performance={"consensus": {"accuracy": 0.4}},
            max_drawdown=25.0,
            consecutive_losses=3,
            win_loss_ratio=1.5,
            volatility=0.25,
            average_odds=4.2,
            overlay_rate=25.0,
            value_capture_rate=70.0,
            best_conditions={"weather": "clear"},
            worst_conditions={"weather": "rain"},
            improvement_areas=["confidence_calibration"],
        )

        self.assertEqual(analytics.total_selections, 50)
        self.assertAlmostEqual(analytics.selections_per_day, 7.14, places=1)
        self.assertEqual(analytics.net_profit, 50.0)
        self.assertEqual(analytics.roi_percentage, 10.0)


def run_comprehensive_tests():
    """Run comprehensive test suite."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAISelectionsTracker))
    test_suite.addTest(unittest.makeSuite(TestAISelectionsIntegration))
    test_suite.addTest(unittest.makeSuite(TestSelectionAnalytics))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Return results summary
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (
            (
                (result.testsRun - len(result.failures) - len(result.errors))
                / result.testsRun
                * 100
            )
            if result.testsRun > 0
            else 0
        ),
    }


if __name__ == "__main__":
    print("🧪 Running AI Selections Tracking Test Suite")
    print("=" * 50)

    results = run_comprehensive_tests()

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Tests Run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")

    if results["success_rate"] == 100:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed - check output above")
