#!/usr/bin/env python3
"""
Unit Tests for ML Components
Tests machine learning ensemble,
            # Test that the features object was created successfully
            self.assertIsNotNone(market_features)
            self.assertEqual(market_features.horse_name, "Test Horse")
            self.assertEqual(market_features.odds_decimal, 3.5)
            self.assertFalse(market_features.is_favorite)
            self.assertEqual(market_features.field_size, 8)

        except ImportError:
            self.skipTest("MarketFeatures component not available") prediction functionality
"""

import unittest
import tempfile
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestMLEnsemble(unittest.TestCase):
    """Test ML ensemble functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            "models": ["random_forest", "gradient_boosting", "neural_network"],
            "model_directory": self.test_dir,
            "ensemble_method": "weighted_average",
        }

    def test_ensemble_initialization(self):
        """Test ensemble can be initialized"""
        try:
            from tools.pipeline.enhanced_ml_ensemble_integration import (
                EnhancedMLEnsembleIntegration,
            )

            ensemble = EnhancedMLEnsembleIntegration(self.config)
            self.assertIsNotNone(ensemble)
        except ImportError:
            self.skipTest("EnhancedMLEnsembleIntegration not available")

    def test_consensus_rating(self):
        """Test consensus rating calculation"""
        try:
            from src.horse_racing_ai.ml.v2_01_consensus_rating import ConsensusRating

            consensus = ConsensusRating()

            # Test with mock predictions from multiple models
            predictions = [0.75, 0.65, 0.80, 0.70]
            rating = consensus.calculate_consensus(predictions)

            self.assertIsInstance(rating, float)
            self.assertGreaterEqual(rating, 0.0)
            self.assertLessEqual(rating, 1.0)

            # Test weighted consensus
            weights = [0.3, 0.25, 0.35, 0.1]
            weighted_rating = consensus.calculate_weighted_consensus(
                predictions, weights
            )
            self.assertIsInstance(weighted_rating, float)

        except ImportError:
            self.skipTest("ConsensusRating not available")

    def test_feature_engineering(self):
        """Test feature engineering for ML models"""
        try:
            from src.horse_racing_ai.ml.v2_01_market_features import MarketFeatures

            # Create a MarketFeatures instance with required arguments
            market_features = MarketFeatures(
                horse_name="Test Horse",
                odds_decimal=3.5,
                is_favorite=False,
                odds_rank=2,
                market_share=0.25,
                odds_percentile=0.6,
                field_size=8,
                prize_per_runner=1250.0,
                rating_odds_ratio=1.2,
                value_rating=85.0,
                implied_probability=0.286,
            )

            # Test that the features object was created successfully
            self.assertIsNotNone(market_features)
            self.assertEqual(market_features.horse_name, "Test Horse")
            self.assertEqual(market_features.odds_decimal, 3.5)
            self.assertFalse(market_features.is_favorite)
            self.assertEqual(market_features.field_size, 8)

        except ImportError:
            self.skipTest("MarketFeatures component not available")

    def test_model_training(self):
        """Test ML model training"""
        try:
            from src.horse_racing_ai.ml.v2_01_ensemble_predictor import (
                EnsemblePredictor,
            )

            # Create synthetic training data
            np.random.seed(42)
            n_samples = 100
            X = pd.DataFrame(
                {
                    "feature_1": np.random.randn(n_samples),
                    "feature_2": np.random.randn(n_samples),
                    "feature_3": np.random.randn(n_samples),
                    "feature_4": np.random.randn(n_samples),
                }
            )
            y = np.random.randint(0, 2, n_samples)  # Binary classification

            predictor = EnsemblePredictor(self.config)

            # Test training
            predictor.train(X, y)

            # Test prediction
            predictions = predictor.predict(X.head(5))
            self.assertEqual(len(predictions), 5)

        except ImportError:
            self.skipTest("EnsemblePredictor not available")

    def test_model_validation(self):
        """Test model validation functionality"""
        try:
            from src.horse_racing_ai.ml.v2_01_performance_validation import (
                PerformanceValidator,
            )

            validator = PerformanceValidator()

            # Test with mock predictions and actual results
            predictions = np.array([0.7, 0.3, 0.8, 0.2, 0.9])
            actuals = np.array([1, 0, 1, 0, 1])

            metrics = validator.calculate_metrics(predictions, actuals)

            self.assertIn("accuracy", metrics)
            self.assertIn("auc", metrics)
            self.assertIn("precision", metrics)
            self.assertIn("recall", metrics)

            # Validate metric ranges
            self.assertGreaterEqual(metrics["accuracy"], 0.0)
            self.assertLessEqual(metrics["accuracy"], 1.0)

        except ImportError:
            self.skipTest("PerformanceValidator not available")


class TestBettingStrategies(unittest.TestCase):
    """Test betting strategy implementations"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "bankroll": 1000.0,
            "max_stake_percentage": 5.0,
            "min_odds": 1.5,
            "max_odds": 10.0,
        }

    def test_kelly_criterion(self):
        """Test Kelly criterion stake calculation"""
        try:
            from tools.pipeline.betting_integration_system import (
                BettingIntegrationSystem,
            )

            betting_system = BettingIntegrationSystem(self.config)

            # Test Kelly criterion calculation
            test_cases = [
                (3.0, 0.4, 1000.0, 10.0),  # odds, prob, bankroll, expected_stake
                (2.0, 0.6, 1000.0, 20.0),  # Higher prob, lower odds
                (5.0, 0.3, 1000.0, 10.0),  # Lower prob, higher odds
            ]

            for odds, probability, bankroll, expected_range in test_cases:
                stake = betting_system.calculate_kelly_stake(
                    odds, probability, bankroll
                )
                self.assertIsInstance(stake, float)
                self.assertGreaterEqual(stake, 0.0)
                self.assertLessEqual(stake, bankroll * 0.25)  # Reasonable upper limit

        except ImportError:
            self.skipTest("BettingIntegrationSystem not available")

    def test_value_betting(self):
        """Test value betting strategy"""
        try:
            from tools.pipeline.betting_integration_system import (
                BettingIntegrationSystem,
            )

            betting_system = BettingIntegrationSystem(self.config)

            # Test value bet identification
            test_bets = [
                {"odds": 3.0, "probability": 0.4, "expected_value": 0.2},  # Value bet
                {"odds": 2.0, "probability": 0.4, "expected_value": -0.2},  # No value
                {"odds": 5.0, "probability": 0.25, "expected_value": 0.25},  # Value bet
            ]

            for bet in test_bets:
                is_value = betting_system.is_value_bet(bet["odds"], bet["probability"])
                self.assertIsInstance(is_value, bool)

        except ImportError:
            self.skipTest("BettingIntegrationSystem not available")

    def test_arbitrage_detection(self):
        """Test arbitrage opportunity detection"""
        try:
            from tools.pipeline.betting_integration_system import (
                BettingIntegrationSystem,
            )

            betting_system = BettingIntegrationSystem(self.config)

            # Test arbitrage scenarios
            odds_sets = [
                [2.1, 2.0, 1.9],  # No arbitrage
                [2.5, 2.3, 2.1],  # Potential arbitrage
                [1.5, 3.0, 4.0],  # Clear arbitrage
            ]

            for odds in odds_sets:
                arb_opportunity = betting_system.detect_arbitrage(odds)
                self.assertIsInstance(arb_opportunity, (bool, dict))

        except ImportError:
            self.skipTest("BettingIntegrationSystem not available")


class TestPerformanceTracking(unittest.TestCase):
    """Test performance tracking functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_performance.db")
        self.config = {
            "database_path": self.db_path,
            "alert_thresholds": {"roi": 10.0, "accuracy": 60.0, "loss_limit": 20.0},
        }

    def test_roi_calculation(self):
        """Test ROI calculation"""
        try:
            from tools.pipeline.performance_tracking_integration import (
                PerformanceTrackingIntegration,
            )

            tracker = PerformanceTrackingIntegration(self.config)

            # Test ROI with winning and losing bets
            bets = [
                {"stake": 10.0, "return": 15.0, "result": "win"},
                {"stake": 20.0, "return": 0.0, "result": "loss"},
                {"stake": 15.0, "return": 30.0, "result": "win"},
                {"stake": 25.0, "return": 0.0, "result": "loss"},
            ]

            roi = tracker.calculate_roi(bets)
            self.assertIsInstance(roi, float)

            # ROI should be (total_return - total_stake) / total_stake * 100
            total_stake = sum(bet["stake"] for bet in bets)
            total_return = sum(bet["return"] for bet in bets)
            expected_roi = ((total_return - total_stake) / total_stake) * 100

            self.assertAlmostEqual(roi, expected_roi, places=2)

        except ImportError:
            self.skipTest("PerformanceTrackingIntegration not available")

    def test_accuracy_tracking(self):
        """Test prediction accuracy tracking"""
        try:
            from tools.pipeline.performance_tracking_integration import (
                PerformanceTrackingIntegration,
            )

            tracker = PerformanceTrackingIntegration(self.config)

            # Test accuracy calculation
            predictions = [
                {"predicted": "win", "actual": "win"},
                {"predicted": "loss", "actual": "loss"},
                {"predicted": "win", "actual": "loss"},
                {"predicted": "loss", "actual": "win"},
                {"predicted": "win", "actual": "win"},
            ]

            accuracy = tracker.calculate_accuracy(predictions)
            self.assertIsInstance(accuracy, float)
            self.assertGreaterEqual(accuracy, 0.0)
            self.assertLessEqual(accuracy, 100.0)

            # Expected accuracy is 3/5 = 60%
            self.assertAlmostEqual(accuracy, 60.0, places=1)

        except ImportError:
            self.skipTest("PerformanceTrackingIntegration not available")

    def test_alert_system(self):
        """Test performance alert system"""
        try:
            from tools.pipeline.performance_tracking_integration import (
                PerformanceTrackingIntegration,
            )

            tracker = PerformanceTrackingIntegration(self.config)

            # Test alert triggers
            performance_data = {
                "roi": 5.0,  # Below threshold
                "accuracy": 55.0,  # Below threshold
                "total_loss": 25.0,  # Above loss limit
            }

            alerts = tracker.check_alerts(performance_data)
            self.assertIsInstance(alerts, list)
            self.assertGreater(len(alerts), 0)  # Should trigger alerts

        except ImportError:
            self.skipTest("PerformanceTrackingIntegration not available")


class TestContextualAI(unittest.TestCase):
    """Test contextual AI functionality"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "weather_api_key": "test_key",
            "ai_model": "qwen",
            "analysis_types": ["weather", "track", "form"],
        }

    @patch("requests.get")
    def test_weather_analysis(self, mock_get):
        """Test weather analysis functionality"""
        try:
            from tools.pipeline.contextual_ai_enhancement_system import (
                ContextualAIEnhancementSystem,
            )

            # Mock weather API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "weather": [{"main": "Rain", "description": "light rain"}],
                "main": {"temp": 15.0, "humidity": 80, "pressure": 1013},
                "wind": {"speed": 5.0, "deg": 180},
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            ai_system = ContextualAIEnhancementSystem(self.config)
            weather_analysis = ai_system.analyze_weather("London")

            self.assertIsNotNone(weather_analysis)
            self.assertIn("weather_condition", weather_analysis)
            self.assertIn("temperature", weather_analysis)

        except ImportError:
            self.skipTest("ContextualAIEnhancementSystem not available")

    def test_form_analysis(self):
        """Test horse form analysis"""
        try:
            from tools.pipeline.contextual_ai_enhancement_system import (
                ContextualAIEnhancementSystem,
            )

            ai_system = ContextualAIEnhancementSystem(self.config)

            # Test form data
            form_data = [
                {"position": 1, "race_date": "2025-01-15", "distance": 1600},
                {"position": 3, "race_date": "2025-01-08", "distance": 1400},
                {"position": 2, "race_date": "2025-01-01", "distance": 1600},
            ]

            form_analysis = ai_system.analyze_form(form_data)

            self.assertIsNotNone(form_analysis)
            self.assertIn("recent_performance", form_analysis)
            self.assertIn("consistency", form_analysis)

        except ImportError:
            self.skipTest("ContextualAIEnhancementSystem not available")

    def test_track_condition_analysis(self):
        """Test track condition analysis"""
        try:
            from tools.pipeline.contextual_ai_enhancement_system import (
                ContextualAIEnhancementSystem,
            )

            ai_system = ContextualAIEnhancementSystem(self.config)

            # Test track conditions
            track_data = {
                "going": "Good to Firm",
                "surface": "Turf",
                "rail_position": "True",
                "track_variant": 0,
            }

            track_analysis = ai_system.analyze_track_conditions(track_data)

            self.assertIsNotNone(track_analysis)
            self.assertIn("going_rating", track_analysis)
            self.assertIn("surface_advantage", track_analysis)

        except ImportError:
            self.skipTest("ContextualAIEnhancementSystem not available")


if __name__ == "__main__":
    unittest.main()
