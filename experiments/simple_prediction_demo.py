#!/usr/bin/env python3
"""
Simple ML Prediction Demo
Demonstrates the trained race card models
"""

import sqlite3
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_race_card_models():
    """Load the trained race card models."""

    models_dir = Path("trained_models/race_card_models")

    try:
        # Load models
        rf_model = joblib.load(models_dir / "random_forest_race_card.joblib")
        gb_model = joblib.load(models_dir / "gradient_boosting_race_card.joblib")

        # Load components
        scalers = joblib.load(models_dir / "scalers_race_card.joblib")
        encoders = joblib.load(models_dir / "encoders_race_card.joblib")
        features = joblib.load(models_dir / "features_race_card.joblib")
        performance = joblib.load(models_dir / "performance_race_card.joblib")

        logger.info("✅ Race card models loaded successfully")

        return {
            "rf_model": rf_model,
            "gb_model": gb_model,
            "scalers": scalers,
            "encoders": encoders,
            "features": features,
            "performance": performance,
        }

    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        return None


def load_sample_race_data():
    """Load a sample race for prediction."""

    conn = sqlite3.connect("race_cards_prediction_data.db")

    query = """
    SELECT 
        rc.race_id,
        rc.course,
        rc.field_size,
        
        rce.horse_name,
        rce.morning_line_odds,
        rce.recent_form_rating,
        rce.speed_rating,
        rce.class_rating
        
    FROM race_cards rc
    JOIN race_card_entries rce ON rc.race_id = rce.race_id
    WHERE rce.morning_line_odds IS NOT NULL
    LIMIT 20
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def simple_prediction_demo():
    """Run a simple prediction demonstration."""

    logger.info("🚀 SIMPLE PREDICTION DEMO")
    logger.info("=" * 40)

    # Load models
    components = load_race_card_models()
    if not components:
        return

    # Show model performance
    logger.info("\n📊 Model Performance:")
    performance = components["performance"]
    for model_name, metrics in performance.items():
        logger.info(f"{model_name}: AUC = {metrics['roc_auc']:.4f}")

    # Load sample data
    df = load_sample_race_data()
    logger.info(f"\n🏁 Sample race data loaded: {len(df)} entries")

    # Simple odds analysis
    df["implied_prob"] = 1.0 / df["morning_line_odds"]
    df["market_share"] = df["implied_prob"] / df["implied_prob"].sum()
    df["odds_rank"] = df["morning_line_odds"].rank()

    # Display sample predictions
    logger.info("\n🏆 SAMPLE RACE ANALYSIS")
    logger.info("-" * 40)

    for idx, row in df.head(10).iterrows():
        logger.info(
            f"{int(row['odds_rank']):2d}. {row['horse_name']:<20} "
            f"Odds: {row['morning_line_odds']:5.1f} "
            f"Prob: {row['market_share']:.3f}"
        )

    logger.info("\n✅ Demo complete!")


if __name__ == "__main__":
    simple_prediction_demo()
