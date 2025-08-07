#!/usr/bin/env python3
"""
Test Trends & Performance Database Integration for Horse Racing AI v2.0
=====================================================================

Test script demonstrating the complete integration of race trends analysis,
AI betting performance tracking, and database storage.

Features:
- Test race trends analysis integration
- Test AI prediction tracking
- Test betting strategy performance monitoring
- Generate comprehensive performance reports
"""

import logging
import sys
from datetime import datetime, date
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import after path setup
from database.trends_performance_integration_manager import (
    TrendsPerformanceIntegrationManager,
)
from database.trends_performance_database_manager import (
    RaceTrend,
    RaceAnalysisTrends,
    HorseTrendScore,
    AIPrediction,
    BettingStrategy,
    MethodPerformance,
    StrategyPerformance,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockRaceTrendsAnalyzer:
    """Mock RaceTrendsAnalyzer for testing"""

    def analyze_race_trends(self, race_data):
        """Mock race trends analysis"""

        class MockTrend:
            def __init__(self, category, trend_type, confidence, edge):
                self.category = category
                self.trend_type = trend_type
                self.description = f"{category} trend: {trend_type}"
                self.confidence = confidence
                self.edge = edge
                self.sample_size = 50

        class MockTrendsAnalysis:
            def __init__(self):
                self.trends = [
                    MockTrend("age_trends", "young_horses_advantage", 0.8, 0.15),
                    MockTrend("weight_trends", "light_weight_bias", 0.7, 0.12),
                    MockTrend("draw_trends", "inside_draw_favored", 0.6, 0.08),
                    MockTrend("form_trends", "recent_form_important", 0.9, 0.20),
                    MockTrend("price_trends", "value_in_midrange", 0.5, 0.05),
                ]
                self.age_trends = self.trends[:1]
                self.weight_trends = self.trends[1:2]
                self.draw_trends = self.trends[2:3]
                self.form_trends = self.trends[3:4]
                self.price_trends = self.trends[4:5]
                self.seasonal_trends = []
                self.course_form_trends = []
                self.distance_form_trends = []

                self.horse_scores = {
                    "Thunder Bolt": {
                        "overall_score": 78.5,
                        "rank": 1,
                        "confidence": 0.85,
                        "age_score": 12.5,
                        "weight_score": 10.2,
                        "draw_score": 8.8,
                        "form_score": 25.0,
                        "price_score": 22.0,
                        "positive_trends": 4,
                        "negative_trends": 1,
                        "neutral_trends": 0,
                    },
                    "Lightning Strike": {
                        "overall_score": 72.3,
                        "rank": 2,
                        "confidence": 0.78,
                        "age_score": 10.8,
                        "weight_score": 12.5,
                        "draw_score": 6.5,
                        "form_score": 20.5,
                        "price_score": 22.0,
                        "positive_trends": 3,
                        "negative_trends": 2,
                        "neutral_trends": 0,
                    },
                    "Storm Chaser": {
                        "overall_score": 65.7,
                        "rank": 3,
                        "confidence": 0.65,
                        "age_score": 8.2,
                        "weight_score": 8.5,
                        "draw_score": 9.5,
                        "form_score": 18.5,
                        "price_score": 21.0,
                        "positive_trends": 2,
                        "negative_trends": 2,
                        "neutral_trends": 1,
                    },
                }

        return MockTrendsAnalysis()


def test_database_creation():
    """Test database creation and basic functionality"""
    logger.info("=== Testing Database Creation ===")

    try:
        # Initialize integration manager (creates database)
        integration_manager = TrendsPerformanceIntegrationManager(
            "data/test_trends_performance.db"
        )

        logger.info("✓ Database created successfully")
        logger.info("✓ Integration manager initialized")
        return integration_manager

    except Exception as e:
        logger.error(f"✗ Database creation failed: {e}")
        return None


def test_race_trends_integration(integration_manager):
    """Test race trends analysis integration"""
    logger.info("\n=== Testing Race Trends Integration ===")

    try:
        # Create mock race data
        race_data = {
            "race_id": "TEST_RACE_20240101_001",
            "track": "Belmont Park",
            "distance": 8.0,
            "surface": "dirt",
            "race_class": "STAKES",
            "field_size": 8,
        }

        # Create mock horses data
        horses_data = [
            {"horse_name": "Thunder Bolt", "age": 4, "weight": 118, "draw": 3},
            {"horse_name": "Lightning Strike", "age": 5, "weight": 120, "draw": 7},
            {"horse_name": "Storm Chaser", "age": 3, "weight": 115, "draw": 1},
        ]

        # Initialize mock analyzer
        trends_analyzer = MockRaceTrendsAnalyzer()

        # Test race trends analysis
        trends_result = integration_manager.process_race_trends_analysis(
            trends_analyzer, race_data
        )

        if trends_result["success"]:
            trends_count = trends_result["trends_identified"]
            edge_rating = trends_result["overall_edge_rating"]
            logger.info(f"✓ Race trends analysis: {trends_count} trends identified")
            logger.info(f"✓ Overall edge rating: {edge_rating:.3f}")
            logger.info(f"✓ Trend strength: {trends_result['trend_strength']}")
        else:
            error_msg = trends_result.get("error")
            logger.error(f"✗ Race trends analysis failed: {error_msg}")
            return False

        # Test horse scoring with trends
        scoring_result = integration_manager.score_horses_with_trends(
            trends_analyzer, race_data, horses_data
        )

        if scoring_result["success"]:
            logger.info("✓ Horse trend scoring completed:")
            for horse in scoring_result["scored_horses"]:
                name = horse["horse_name"]
                score = horse["trend_score"]
                rank = horse["trend_rank"]
                logger.info(f"  - {name}: Score {score:.1f} (Rank {rank})")
        else:
            logger.error(f"✗ Horse trend scoring failed: {scoring_result.get('error')}")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ Race trends integration test failed: {e}")
        return False


def test_ai_predictions_tracking(integration_manager):
    """Test AI predictions tracking"""
    logger.info("\n=== Testing AI Predictions Tracking ===")

    try:
        race_data = {
            "race_id": "TEST_RACE_20240101_002",
            "track": "Churchill Downs",
            "distance": 10.0,
        }

        # Mock AI predictions data
        predictions = {
            "Thunder Bolt": {
                "raw_rating": 85.2,
                "monte_carlo_rating": 82.7,
                "ai_ml_rating": 88.1,
                "consensus_rating": 85.3,
                "raw_win_probability": 0.35,
                "monte_carlo_win_probability": 0.32,
                "ai_ml_win_probability": 0.38,
                "consensus_win_probability": 0.35,
                "prediction_confidence": 0.85,
                "method_agreement_score": 0.78,
                "prediction_consistency": 0.82,
                "betting_odds": 3.2,
                "implied_probability": 0.31,
                "value_rating": 12.5,
            },
            "Lightning Strike": {
                "raw_rating": 78.9,
                "monte_carlo_rating": 80.1,
                "ai_ml_rating": 76.8,
                "consensus_rating": 78.6,
                "raw_win_probability": 0.28,
                "monte_carlo_win_probability": 0.30,
                "ai_ml_win_probability": 0.26,
                "consensus_win_probability": 0.28,
                "prediction_confidence": 0.72,
                "method_agreement_score": 0.68,
                "prediction_consistency": 0.71,
                "betting_odds": 4.5,
                "implied_probability": 0.22,
                "value_rating": 27.3,
            },
            "Storm Chaser": {
                "raw_rating": 71.5,
                "monte_carlo_rating": 73.2,
                "ai_ml_rating": 69.8,
                "consensus_rating": 71.5,
                "raw_win_probability": 0.20,
                "monte_carlo_win_probability": 0.22,
                "ai_ml_win_probability": 0.18,
                "consensus_win_probability": 0.20,
                "prediction_confidence": 0.65,
                "method_agreement_score": 0.61,
                "prediction_consistency": 0.63,
                "betting_odds": 6.8,
                "implied_probability": 0.15,
                "value_rating": 33.3,
            },
        }

        # Track AI predictions
        tracking_result = integration_manager.track_ai_predictions(
            race_data, predictions
        )

        if tracking_result["success"]:
            count = tracking_result["predictions_stored"]
            logger.info(f"✓ AI predictions tracked: {count} horses")
            for pred in tracking_result["predictions"]:
                name = pred["horse_name"]
                conf = pred["confidence"]
                value = pred["value_rating"]
                logger.info(f"  - {name}: Confidence {conf:.2f}, Value {value:.1f}")
        else:
            error_msg = tracking_result.get("error")
            logger.error(f"✗ AI predictions tracking failed: {error_msg}")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ AI predictions tracking test failed: {e}")
        return False


def test_betting_strategies_tracking(integration_manager):
    """Test betting strategies tracking"""
    logger.info("\n=== Testing Betting Strategies Tracking ===")

    try:
        race_data = {
            "race_id": "TEST_RACE_20240101_003",
            "track": "Santa Anita",
            "distance": 8.5,
        }

        # Mock betting strategies data
        strategies = [
            {
                "horse_name": "Thunder Bolt",
                "strategy_type": "value_bet",
                "bet_type": "win",
                "recommended_stake": 25.0,
                "recommended_odds": 3.2,
                "expected_value": 0.125,
                "kelly_fraction": 0.08,
                "confidence_score": 0.85,
                "risk_rating": "LOW",
                "staking_method": "kelly",
            },
            {
                "horse_name": "Lightning Strike",
                "strategy_type": "each_way",
                "bet_type": "each_way",
                "recommended_stake": 20.0,
                "recommended_odds": 4.5,
                "expected_value": 0.185,
                "kelly_fraction": 0.12,
                "confidence_score": 0.72,
                "risk_rating": "MEDIUM",
                "staking_method": "kelly",
            },
            {
                "horse_name": "Storm Chaser",
                "strategy_type": "value_bet",
                "bet_type": "place",
                "recommended_stake": 15.0,
                "recommended_odds": 2.8,
                "expected_value": 0.095,
                "kelly_fraction": 0.05,
                "confidence_score": 0.65,
                "risk_rating": "MEDIUM",
                "staking_method": "percentage",
            },
        ]

        # Track betting strategies
        tracking_result = integration_manager.track_betting_strategies(
            race_data, strategies
        )

        if tracking_result["success"]:
            count = tracking_result["strategies_stored"]
            logger.info(f"✓ Betting strategies tracked: {count} strategies")
            for strategy in tracking_result["strategies"]:
                name = strategy["horse_name"]
                s_type = strategy["strategy_type"]
                ev = strategy["expected_value"]
                risk = strategy["risk_rating"]
                logger.info(f"  - {name}: {s_type} EV {ev:.3f} Risk {risk}")
        else:
            error_msg = tracking_result.get("error")
            logger.error(f"✗ Betting strategies tracking failed: {error_msg}")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ Betting strategies tracking test failed: {e}")
        return False


def test_performance_reporting(integration_manager):
    """Test performance reporting functionality"""
    logger.info("\n=== Testing Performance Reporting ===")

    try:
        # Generate comprehensive performance report
        report = integration_manager.generate_comprehensive_report(days=30)

        logger.info("✓ Comprehensive Performance Report Generated:")
        logger.info(f"  Period: {report['period_days']} days")

        # Overall statistics
        overall = report["overall_statistics"]
        logger.info(f"  Total Races: {overall['total_races']}")
        logger.info(f"  Total Predictions: {overall['total_predictions']}")
        accuracy = overall["avg_prediction_accuracy"]
        logger.info(f"  Avg Prediction Accuracy: {accuracy:.1%}")

        # Betting statistics
        betting = report["betting_statistics"]
        logger.info(f"  Total Bets: {betting['total_bets']}")
        stakes = betting["total_stakes"] or 0.0
        profit = betting["total_profit"] or 0.0
        roi = betting["avg_roi"] or 0.0
        win_rate = betting["win_rate"] or 0.0
        logger.info(f"  Total Stakes: ${stakes:.2f}")
        logger.info(f"  Total Profit: ${profit:.2f}")
        logger.info(f"  Avg ROI: {roi:.1f}%")
        logger.info(f"  Win Rate: {win_rate:.1f}%")

        # Trends statistics
        trends = report["trends_statistics"]
        logger.info(f"  Races with Trends: {trends['races_with_trends']}")
        avg_trends = trends["avg_trends_per_race"] or 0.0
        avg_edge = trends["avg_edge_rating"] or 0.0
        logger.info(f"  Avg Trends per Race: {avg_trends:.1f}")
        logger.info(f"  Avg Edge Rating: {avg_edge:.3f}")
        logger.info(f"  Strong Trend Races: {trends['strong_trend_races']}")

        # Method performance
        if report["method_performance"]:
            logger.info("  Method Performance:")
            for method, perf in report["method_performance"].items():
                acc = perf["avg_accuracy"]
                roi = perf["avg_roi"]
                logger.info(f"    {method}: Accuracy {acc:.1%}, ROI {roi:.1f}%")

        # Strategy effectiveness
        if report["strategy_effectiveness"]:
            logger.info("  Strategy Effectiveness:")
            for strategy, eff in report["strategy_effectiveness"].items():
                roi = eff["avg_roi"]
                usage = eff["avg_usage_rate"]
                logger.info(f"    {strategy}: ROI {roi:.1f}%, Usage {usage:.1%}")

        return True

    except Exception as e:
        logger.error(f"✗ Performance reporting test failed: {e}")
        return False


def test_data_export(integration_manager):
    """Test data export functionality"""
    logger.info("\n=== Testing Data Export ===")

    try:
        # Export performance data
        export_path = integration_manager.db_manager.export_performance_data(
            "data/test_performance_export.csv"
        )

        logger.info(f"✓ Performance data exported to: {export_path}")

        # Check if file exists and has content
        export_file = Path(export_path)
        if export_file.exists():
            file_size = export_file.stat().st_size
            logger.info(f"✓ Export file size: {file_size} bytes")
        else:
            logger.error("✗ Export file was not created")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ Data export test failed: {e}")
        return False


def main():
    """Run comprehensive integration tests"""
    logger.info("🏇 Starting Trends & Performance Database Integration Tests")
    logger.info("=" * 70)

    # Test database creation
    integration_manager = test_database_creation()
    if not integration_manager:
        logger.error("❌ Database creation failed - aborting tests")
        return False

    # Run all tests
    tests = [
        ("Race Trends Integration", test_race_trends_integration),
        ("AI Predictions Tracking", test_ai_predictions_tracking),
        ("Betting Strategies Tracking", test_betting_strategies_tracking),
        ("Performance Reporting", test_performance_reporting),
        ("Data Export", test_data_export),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_function in tests:
        logger.info(f"\n🧪 Running {test_name} Test...")
        if test_function(integration_manager):
            logger.info(f"✅ {test_name} Test PASSED")
            passed_tests += 1
        else:
            logger.error(f"❌ {test_name} Test FAILED")

    # Final results
    logger.info("\n" + "=" * 70)
    logger.info(f"🏁 Test Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        msg = (
            "🎉 All tests passed! Trends & Performance integration "
            "is working correctly."
        )
        logger.info(msg)
        return True
    else:
        failed = total_tests - passed_tests
        logger.error(f"💥 {failed} test(s) failed. Check the logs above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
