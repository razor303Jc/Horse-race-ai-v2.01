#!/usr/bin/env python3
"""
V2.01 Ensemble Training Script
=============================

Train and test the enhanced ensemble model based on v2.01 analysis.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.ml.v2_01_ensemble_predictor import (
    V201EnsemblePredictor,
    EnsembleResults,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load and prepare training data from current preprocessed data."""
    logger.info("Loading training data...")

    # Load horses data
    horses_file = project_root / "data/preprocessed/cards_data/horses/horses.csv"
    if not horses_file.exists():
        raise FileNotFoundError(f"Horses data not found: {horses_file}")

    horses_df = pd.read_csv(horses_file)
    logger.info(f"Loaded {len(horses_df)} horse records")

    # Prepare features and target
    # Create synthetic target for demonstration (normally would use actual race results)
    # Target: horse won (1) or didn't win (0) based on win percentage
    target = (
        horses_df["Percentage_wins"] > horses_df["Percentage_wins"].median()
    ).astype(int)

    logger.info(f"Target distribution: {target.value_counts().to_dict()}")

    return horses_df, target


def create_race_simulation(horses_df: pd.DataFrame, race_size: int = 8) -> pd.DataFrame:
    """Create a simulated race from available horses."""
    logger.info(f"Creating simulated race with {race_size} horses...")

    # Sample horses for race
    if len(horses_df) < race_size:
        race_horses = horses_df.copy()
    else:
        race_horses = horses_df.sample(n=race_size, random_state=42)

    return race_horses.reset_index(drop=True)


def main():
    """Main training and testing function."""
    logger.info("🏇 Starting V2.01 Ensemble Training...")

    try:
        # Load data
        horses_df, target = load_training_data()

        # Initialize predictor
        predictor = V201EnsemblePredictor(models_dir=str(project_root / "models"))

        # Prepare features
        logger.info("Preparing features...")
        X = predictor.prepare_features(horses_df)
        logger.info(f"Feature matrix shape: {X.shape}")

        # Train ensemble
        logger.info("Training ensemble...")
        training_results = predictor.train_ensemble(X, target)

        if not training_results:
            logger.error("❌ Training failed")
            return

        # Print training results
        logger.info("\n" + "=" * 50)
        logger.info("🎯 TRAINING RESULTS")
        logger.info("=" * 50)

        for model_name, metrics in training_results.items():
            logger.info(f"\n{model_name.upper()}:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.4f}")

        # Save model
        model_path = predictor.save_ensemble()
        logger.info(f"✅ Model saved to: {model_path}")

        # Test on simulated race
        logger.info("\n" + "=" * 50)
        logger.info("🏁 RACE PREDICTION TEST")
        logger.info("=" * 50)

        race_horses = create_race_simulation(horses_df, race_size=8)
        results = predictor.predict_race(race_horses, race_id="TEST_RACE_001")

        # Display race predictions
        logger.info("\nRACE PREDICTIONS:")
        logger.info("-" * 80)
        logger.info(
            f"{'Rank':<4} {'Horse':<20} {'RF':<6} {'GB':<6} {'NN':<6} {'LR':<6} {'Ensemble':<9} {'Conf':<6}"
        )
        logger.info("-" * 80)

        for pred in results.predictions:
            logger.info(
                f"{pred.ml_rank:<4} {pred.horse_name[:20]:<20} "
                f"{pred.rf_prob:<6.3f} {pred.gb_prob:<6.3f} {pred.nn_prob:<6.3f} "
                f"{pred.lr_prob:<6.3f} {pred.ensemble_prob:<9.3f} {pred.confidence:<6.3f}"
            )

        # Display feature importance
        logger.info("\nTOP FEATURE IMPORTANCE:")
        logger.info("-" * 40)
        for feat in results.feature_importance[:10]:
            logger.info(f"{feat.feature_name:<25} {feat.importance_score:.4f}")

        # Display summary stats
        logger.info(f"\nSUMMARY:")
        logger.info(f"Confidence Distribution: {results.confidence_distribution}")
        logger.info(f"Value Bets: {results.value_bets_count}")
        logger.info(f"Model Performance: {len(results.model_performance)} models")

        # Export predictions
        export_path = (
            project_root
            / f"data/v2_01_archive/ml_predictions_test_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        predictor.export_predictions(results, str(export_path))

        # Test model loading
        logger.info("\n" + "=" * 50)
        logger.info("🔄 TESTING MODEL LOADING")
        logger.info("=" * 50)

        new_predictor = V201EnsemblePredictor()
        if new_predictor.load_ensemble(model_path):
            logger.info("✅ Model loaded successfully")

            # Get model summary
            summary = new_predictor.get_model_summary()
            logger.info(f"Model Summary: {summary['status']}")
            logger.info(f"Models: {summary['individual_models']}")
            logger.info(f"Features: {summary['feature_count']}")
        else:
            logger.error("❌ Model loading failed")

        logger.info("\n🎉 Training and testing completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error during training: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
