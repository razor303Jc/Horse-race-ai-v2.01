#!/usr/bin/env python3
"""
Simple ML Training on Massive Dataset - Horse Racing AI v2.0
Quick training script with basic features to test our massive dataset
"""

import os
import logging
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import warnings
import joblib

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def quick_ml_training():
    """Quick ML training on massive dataset."""

    logger.info("🚀 QUICK ML TRAINING ON MASSIVE DATASET")
    logger.info("=" * 50)

    # Connect to database
    db_path = "massive_racing_data_with_markets.db"
    conn = sqlite3.connect(db_path)

    logger.info(f"📊 Connected to {db_path}")

    # Simple query with basic features
    query = """
    SELECT 
        r.race_id,
        r.course,
        r.distance,
        r.field_size,
        r.prize_money,
        rp.horse_name,
        rp.horse_age,
        rp.horse_weight_kg,
        rp.draw,
        rp.win_odds,
        rp.form_rating,
        rp.speed_rating,
        rp.class_rating,
        rp.finished_position,
        CASE WHEN rp.finished_position = 1 THEN 1 ELSE 0 END as won_race
    FROM races r
    JOIN race_participants rp ON r.race_id = rp.race_id
    WHERE rp.win_odds IS NOT NULL 
    AND rp.win_odds > 0
    AND rp.finished_position IS NOT NULL
    LIMIT 100000
    """

    logger.info("📊 Loading training data...")
    df = pd.read_sql_query(query, conn)
    conn.close()

    logger.info(f"📈 Loaded {len(df):,} training records")
    logger.info(f"🏇 Unique horses: {df['horse_name'].nunique():,}")
    logger.info(f"🏁 Unique races: {df['race_id'].nunique():,}")
    logger.info(f"🎯 Win rate: {df['won_race'].mean():.3f}")

    # Basic feature engineering
    logger.info("🔧 Engineering basic features...")

    # Numerical features
    df["log_odds"] = np.log(df["win_odds"])
    df["odds_rank"] = df.groupby("race_id")["win_odds"].rank()
    df["is_favorite"] = (df["win_odds"] <= 3.0).astype(int)
    df["is_outsider"] = (df["win_odds"] >= 20.0).astype(int)
    df["log_prize"] = np.log(df["prize_money"] + 1)

    # Encode categorical features
    le_course = LabelEncoder()
    df["course_encoded"] = le_course.fit_transform(df["course"].fillna("Unknown"))

    # Select features for training
    feature_columns = [
        "horse_age",
        "horse_weight_kg",
        "draw",
        "log_odds",
        "odds_rank",
        "is_favorite",
        "is_outsider",
        "form_rating",
        "speed_rating",
        "class_rating",
        "field_size",
        "log_prize",
        "course_encoded",
    ]

    X = df[feature_columns].fillna(0)
    y = df["won_race"]

    logger.info(f"🔢 Features: {len(feature_columns)}")
    logger.info(f"📊 Training samples: {len(X):,}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"📊 Training set: {len(X_train):,}")
    logger.info(f"📊 Test set: {len(X_test):,}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest
    logger.info("🌲 Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    # Evaluate Random Forest
    rf_pred = rf_model.predict(X_test)
    rf_prob = rf_model.predict_proba(X_test)[:, 1]
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_auc = roc_auc_score(y_test, rf_prob)

    logger.info(f"✅ Random Forest - Accuracy: {rf_accuracy:.3f}, AUC: {rf_auc:.3f}")

    # Train Gradient Boosting
    logger.info("🚀 Training Gradient Boosting...")
    gb_model = GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
    )
    gb_model.fit(X_train, y_train)

    # Evaluate Gradient Boosting
    gb_pred = gb_model.predict(X_test)
    gb_prob = gb_model.predict_proba(X_test)[:, 1]
    gb_accuracy = accuracy_score(y_test, gb_pred)
    gb_auc = roc_auc_score(y_test, gb_prob)

    logger.info(
        f"✅ Gradient Boosting - Accuracy: {gb_accuracy:.3f}, AUC: {gb_auc:.3f}"
    )

    # Save models
    models_dir = Path("trained_models")
    models_dir.mkdir(exist_ok=True)

    logger.info("💾 Saving models...")
    joblib.dump(rf_model, models_dir / "random_forest_quick.joblib")
    joblib.dump(gb_model, models_dir / "gradient_boosting_quick.joblib")
    joblib.dump(scaler, models_dir / "scaler_quick.joblib")
    joblib.dump(feature_columns, models_dir / "features_quick.joblib")
    joblib.dump(le_course, models_dir / "course_encoder_quick.joblib")

    # Feature importance
    feature_importance = pd.DataFrame(
        {"feature": feature_columns, "importance": rf_model.feature_importances_}
    ).sort_values("importance", ascending=False)

    logger.info("\n🏆 TOP FEATURE IMPORTANCE:")
    logger.info("-" * 40)
    for _, row in feature_importance.head(10).iterrows():
        logger.info(f"{row['feature']:>20}: {row['importance']:.4f}")

    # Performance summary
    logger.info("\n" + "=" * 50)
    logger.info("🏆 TRAINING COMPLETE!")
    logger.info("=" * 50)
    logger.info(f"📊 Dataset: {len(df):,} records")
    logger.info(f"🌲 Random Forest AUC: {rf_auc:.4f}")
    logger.info(f"🚀 Gradient Boosting AUC: {gb_auc:.4f}")
    logger.info(f"💾 Models saved to: {models_dir}")

    # Quick prediction test
    logger.info("\n🧪 QUICK PREDICTION TEST")
    logger.info("-" * 30)

    # Get a favorite and outsider from test set
    test_df = df.iloc[X_test.index]
    favorite_idx = test_df["win_odds"].idxmin()
    outsider_idx = test_df["win_odds"].idxmax()

    fav_features = X_test.loc[favorite_idx:favorite_idx]
    out_features = X_test.loc[outsider_idx:outsider_idx]

    fav_prob = rf_model.predict_proba(fav_features)[0, 1]
    out_prob = rf_model.predict_proba(out_features)[0, 1]

    logger.info(
        f"🏇 Favorite (odds {test_df.loc[favorite_idx, 'win_odds']:.1f}): {fav_prob:.3f} win prob"
    )
    logger.info(
        f"🐴 Outsider (odds {test_df.loc[outsider_idx, 'win_odds']:.1f}): {out_prob:.3f} win prob"
    )
    logger.info(f"📊 Ratio: {fav_prob/out_prob:.1f}x more likely")


if __name__ == "__main__":
    quick_ml_training()
