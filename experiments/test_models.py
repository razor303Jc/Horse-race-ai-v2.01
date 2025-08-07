#!/usr/bin/env python3
"""
Test Trained Models - Quick validation of our ML models
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_quick_models():
    """Test the quick trained models."""

    logger.info("🧪 TESTING QUICK TRAINED MODELS")
    logger.info("=" * 40)

    models_dir = Path("trained_models")

    try:
        # Load models
        rf_model = joblib.load(models_dir / "random_forest_quick.joblib")
        gb_model = joblib.load(models_dir / "gradient_boosting_quick.joblib")
        scaler = joblib.load(models_dir / "scaler_quick.joblib")
        features = joblib.load(models_dir / "features_quick.joblib")
        course_encoder = joblib.load(models_dir / "course_encoder_quick.joblib")

        logger.info("✅ All models loaded successfully")
        logger.info(f"🔢 Features: {len(features)}")

        # Create test cases
        test_scenarios = [
            {
                "name": "Strong Favorite",
                "horse_age": 4,
                "horse_weight_kg": 57.0,
                "draw": 1,
                "log_odds": np.log(2.0),  # 2.0 odds
                "odds_rank": 1,
                "is_favorite": 1,
                "is_outsider": 0,
                "form_rating": 85,
                "speed_rating": 80,
                "class_rating": 75,
                "field_size": 8,
                "log_prize": np.log(50000),
                "course_encoded": 0,  # Will use first course
            },
            {
                "name": "Mid-range Runner",
                "horse_age": 5,
                "horse_weight_kg": 56.0,
                "draw": 4,
                "log_odds": np.log(8.0),  # 8.0 odds
                "odds_rank": 4,
                "is_favorite": 0,
                "is_outsider": 0,
                "form_rating": 65,
                "speed_rating": 60,
                "class_rating": 55,
                "field_size": 8,
                "log_prize": np.log(50000),
                "course_encoded": 0,
            },
            {
                "name": "Long Shot",
                "horse_age": 7,
                "horse_weight_kg": 54.0,
                "draw": 8,
                "log_odds": np.log(25.0),  # 25.0 odds
                "odds_rank": 8,
                "is_favorite": 0,
                "is_outsider": 1,
                "form_rating": 45,
                "speed_rating": 40,
                "class_rating": 35,
                "field_size": 8,
                "log_prize": np.log(50000),
                "course_encoded": 0,
            },
        ]

        logger.info("\n🏇 PREDICTION SCENARIOS:")
        logger.info("-" * 50)

        for scenario in test_scenarios:
            # Create feature vector
            feature_data = pd.DataFrame([scenario])[features]

            # Make predictions
            rf_prob = rf_model.predict_proba(feature_data)[0, 1]
            gb_prob = gb_model.predict_proba(feature_data)[0, 1]
            avg_prob = (rf_prob + gb_prob) / 2

            # Convert to approximate odds
            implied_odds = 1.0 / avg_prob if avg_prob > 0 else 999

            logger.info(f"\n🐴 {scenario['name']}:")
            logger.info(f"   Market Odds: {np.exp(scenario['log_odds']):.1f}")
            logger.info(f"   RF Prediction: {rf_prob:.3f}")
            logger.info(f"   GB Prediction: {gb_prob:.3f}")
            logger.info(f"   Average: {avg_prob:.3f}")
            logger.info(f"   Implied Odds: {implied_odds:.1f}")

        logger.info("\n✅ Model testing complete!")

        # Model comparison
        logger.info(f"\n📊 MODEL COMPARISON:")
        logger.info(f"Random Forest trees: {rf_model.n_estimators}")
        logger.info(f"Gradient Boosting trees: {gb_model.n_estimators}")
        logger.info(f"Feature scaling: {'Enabled' if scaler else 'Disabled'}")

    except Exception as e:
        logger.error(f"❌ Model testing failed: {e}")
        return False

    return True


def check_model_files():
    """Check what model files we have."""

    logger.info("\n📁 CHECKING MODEL FILES:")
    logger.info("-" * 30)

    models_dir = Path("trained_models")

    if not models_dir.exists():
        logger.warning("❌ No trained_models directory found")
        return

    for file in models_dir.glob("*.joblib"):
        size_mb = file.stat().st_size / (1024 * 1024)
        logger.info(f"📄 {file.name}: {size_mb:.1f}MB")

    # Check for full dataset models
    full_dir = models_dir / "full_dataset"
    if full_dir.exists():
        logger.info(f"\n📁 Full Dataset Models:")
        for file in full_dir.glob("*.joblib"):
            size_mb = file.stat().st_size / (1024 * 1024)
            logger.info(f"📄 {file.name}: {size_mb:.1f}MB")


if __name__ == "__main__":
    check_model_files()
    test_quick_models()
