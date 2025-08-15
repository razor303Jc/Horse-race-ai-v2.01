#!/usr/bin/env python3
"""
🧪 Unified ML Trainer Integration Test
Quick integration test to verify the unified trainer works correctly

This script tests the basic functionality of the UnifiedMLTrainer
without requiring the full dataset or long training times.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.ml_training.unified_ml_trainer import FeatureEngineer, UnifiedMLTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_data() -> pd.DataFrame:
    """Create synthetic test data for testing."""
    np.random.seed(42)
    n_races = 50
    horses_per_race = 8

    data = []
    for race_id in range(n_races):
        for horse_pos in range(horses_per_race):
            data.append(
                {
                    "race_id": f"race_{race_id}",
                    "horse_name": f"horse_{race_id}_{horse_pos}",
                    "win_odds": np.random.uniform(2.0, 50.0),
                    "horse_age": np.random.randint(3, 8),
                    "horse_weight_kg": np.random.uniform(55, 65),
                    "draw": horse_pos + 1,
                    "finished_position": (
                        horse_pos + 1
                        if horse_pos == 0
                        else np.random.randint(2, horses_per_race + 1)
                    ),
                    "prize_money": np.random.uniform(5000, 50000),
                    "jockey_name": f"jockey_{np.random.randint(1, 20)}",
                    "trainer_name": f"trainer_{np.random.randint(1, 15)}",
                    "jockey_win_pct": np.random.uniform(5, 25),
                    "trainer_win_pct": np.random.uniform(8, 30),
                    "course": f"course_{np.random.randint(1, 5)}",
                    "race_date": "2025-08-15",
                }
            )

    return pd.DataFrame(data)


def test_feature_engineering():
    """Test the FeatureEngineer class."""
    logger.info("🧪 Testing FeatureEngineer...")

    # Create test data
    df = create_test_data()

    # Test each feature set
    feature_sets = ["basic", "standard", "advanced", "experimental"]

    for feature_set in feature_sets:
        logger.info(f"  Testing {feature_set} features...")
        engineer = FeatureEngineer(feature_set)
        result_df = engineer.engineer_features(df.copy())

        # Verify target variable is created
        assert (
            "is_winner" in result_df.columns
        ), f"Target variable missing in {feature_set}"

        # Verify we have winners (one per race)
        winners_per_race = result_df.groupby("race_id")["is_winner"].sum()
        assert all(
            winners_per_race == 1
        ), f"Incorrect winners per race in {feature_set}"

        logger.info(
            f"    ✅ {feature_set}: {len(result_df.columns)} features, {len(result_df)} records"
        )

    logger.info("✅ FeatureEngineer tests passed!")


def test_unified_trainer():
    """Test the UnifiedMLTrainer class."""
    logger.info("🧪 Testing UnifiedMLTrainer...")

    class MockTrainer(UnifiedMLTrainer):
        """Mock trainer that uses synthetic data instead of database."""

        def load_data(self):
            return create_test_data()

    # Test with fast strategy (minimal training time)
    trainer = MockTrainer()

    logger.info("  Testing fast training strategy...")
    results = trainer.train_models(strategy="fast")

    # Verify results structure
    assert "models" in results, "Missing models in results"
    assert "best_model" in results, "Missing best_model in results"
    assert "training_time_minutes" in results, "Missing training time in results"

    # Verify we have trained models
    assert len(results["models"]) > 0, "No models trained"

    # Verify performance metrics
    for model_name, metrics in results["models"].items():
        assert "accuracy" in metrics, f"Missing accuracy for {model_name}"
        assert "roc_auc" in metrics, f"Missing ROC AUC for {model_name}"
        assert 0 <= metrics["accuracy"] <= 1, f"Invalid accuracy for {model_name}"

        logger.info(
            f"    {model_name}: Accuracy={metrics['accuracy']:.3f}, ROC AUC={metrics['roc_auc']:.3f}"
        )

    logger.info(
        f"  ✅ Training completed in {results['training_time_minutes']:.1f} minutes"
    )
    logger.info(f"  🏆 Best model: {results['best_model']}")

    logger.info("✅ UnifiedMLTrainer tests passed!")


def test_configuration_loading():
    """Test configuration loading."""
    logger.info("🧪 Testing configuration loading...")

    # Test default configuration
    trainer = UnifiedMLTrainer()
    assert trainer.config is not None, "Failed to load default configuration"
    assert trainer.config["mode"] == "production", "Incorrect default mode"

    # Test custom configuration file
    config_path = project_root / "config" / "ml_training_config.yaml"
    if config_path.exists():
        trainer_custom = UnifiedMLTrainer(config_path=str(config_path))
        assert trainer_custom.config is not None, "Failed to load custom configuration"
        logger.info("  ✅ Custom configuration loaded successfully")

    logger.info("✅ Configuration tests passed!")


def main():
    """Run all integration tests."""
    logger.info("🚀 Starting Unified ML Trainer Integration Tests")
    logger.info("=" * 60)

    try:
        # Run tests
        test_feature_engineering()
        test_configuration_loading()
        test_unified_trainer()

        logger.info("=" * 60)
        logger.info("🎉 All integration tests passed!")
        logger.info("🎯 Unified ML Trainer is ready for production use")

        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
