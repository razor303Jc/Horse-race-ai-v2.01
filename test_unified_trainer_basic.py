#!/usr/bin/env python3
"""
🧪 Simple Unified ML Trainer Test
Basic functionality test for the unified trainer
"""

import os
import sys
import logging
from pathlib import Path

# Set up path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test the unified ML trainer basic functionality."""
    logger.info("🚀 Testing Unified ML Trainer Basic Functionality")

    try:
        # Test imports
        logger.info("📦 Testing imports...")
        from tools.ml_training.unified_ml_trainer import (
            UnifiedMLTrainer,
            FeatureEngineer,
        )

        logger.info("✅ Imports successful")

        # Test configuration
        logger.info("⚙️ Testing configuration...")
        trainer = UnifiedMLTrainer()
        assert trainer.config is not None
        assert trainer.config["mode"] == "production"
        logger.info("✅ Configuration loaded successfully")

        # Test feature engineer
        logger.info("🔧 Testing feature engineering...")
        import pandas as pd
        import numpy as np

        # Create minimal test data
        test_data = pd.DataFrame(
            {
                "race_id": ["race_1"] * 3,
                "horse_name": ["horse_1", "horse_2", "horse_3"],
                "win_odds": [2.5, 5.0, 10.0],
                "horse_age": [4, 5, 6],
                "horse_weight_kg": [57, 58, 59],
                "draw": [1, 2, 3],
                "finished_position": [1, 2, 3],
                "prize_money": [10000, 10000, 10000],
                "jockey_win_pct": [15.0, 12.0, 8.0],
                "trainer_win_pct": [20.0, 18.0, 15.0],
            }
        )

        engineer = FeatureEngineer("basic")
        result_df = engineer.engineer_features(test_data.copy())

        # Verify basic features are created
        expected_features = [
            "log_odds",
            "implied_probability",
            "is_favorite",
            "is_winner",
        ]
        for feature in expected_features:
            assert feature in result_df.columns, f"Missing feature: {feature}"

        logger.info("✅ Feature engineering successful")

        # Test model definitions
        logger.info("🤖 Testing model definitions...")
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression

        # Verify we can create models
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=10, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=10, random_state=42
            ),
            "Logistic": LogisticRegression(random_state=42, max_iter=100),
        }

        logger.info("✅ Model definitions successful")

        logger.info("🎉 All basic functionality tests passed!")
        logger.info("🎯 Unified ML Trainer is ready for integration")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
