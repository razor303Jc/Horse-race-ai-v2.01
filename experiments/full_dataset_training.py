#!/usr/bin/env python3
"""
Full Dataset ML Training - Horse Racing AI v2.0
Train on the complete massive dataset with advanced features
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
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
)

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("full_dataset_training.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def full_dataset_ml_training():
    """Comprehensive ML training on full massive dataset."""

    start_time = datetime.now()

    logger.info("🚀 FULL DATASET ML TRAINING - HORSE RACING AI v2.0")
    logger.info("=" * 60)

    # Connect to database
    db_path = "massive_racing_data_with_markets.db"
    conn = sqlite3.connect(db_path)

    # Get dataset size first
    count_query = "SELECT COUNT(*) FROM race_participants"
    total_records = pd.read_sql_query(count_query, conn).iloc[0, 0]
    logger.info(f"📊 Total records available: {total_records:,}")

    # Enhanced query with all available features
    query = """
    SELECT 
        r.race_id,
        r.course,
        r.race_type,
        r.distance,
        r.field_size,
        r.prize_money,
        r.class_level,
        r.weather_condition,
        r.track_condition,
        rp.horse_name,
        rp.horse_age,
        rp.horse_weight_kg,
        rp.draw,
        rp.win_odds,
        rp.place_odds,
        rp.form_rating,
        rp.speed_rating,
        rp.class_rating,
        rp.market_percentage,
        rp.finished_position,
        CASE WHEN rp.finished_position = 1 THEN 1 ELSE 0 END as won_race,
        CASE WHEN rp.finished_position <= 3 THEN 1 ELSE 0 END as placed
    FROM races r
    JOIN race_participants rp ON r.race_id = rp.race_id
    WHERE rp.win_odds IS NOT NULL 
    AND rp.win_odds > 0
    AND rp.finished_position IS NOT NULL
    """

    logger.info("📊 Loading full massive dataset...")
    df = pd.read_sql_query(query, conn)
    conn.close()

    logger.info(f"📈 Loaded {len(df):,} training records")
    logger.info(f"🏇 Unique horses: {df['horse_name'].nunique():,}")
    logger.info(f"🏁 Unique races: {df['race_id'].nunique():,}")
    logger.info(f"🎯 Win rate: {df['won_race'].mean():.4f}")
    logger.info(f"🥉 Place rate: {df['placed'].mean():.4f}")

    # Advanced feature engineering
    logger.info("🔧 Engineering advanced features...")

    # Odds-based features
    df["log_odds"] = np.log(df["win_odds"])
    df["log_place_odds"] = np.log(df["place_odds"].fillna(df["win_odds"] / 3))
    df["odds_rank"] = df.groupby("race_id")["win_odds"].rank()
    df["odds_percentile"] = df.groupby("race_id")["win_odds"].rank(pct=True)

    # Market features
    df["is_favorite"] = (df["win_odds"] <= 3.0).astype(int)
    df["is_outsider"] = (df["win_odds"] >= 20.0).astype(int)
    df["market_strength"] = 1.0 / df["win_odds"]
    df["market_share"] = df.groupby("race_id")["market_strength"].transform(
        lambda x: x / x.sum()
    )

    # Competition features
    df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
    df["weight_percentile"] = df.groupby("race_id")["horse_weight_kg"].rank(pct=True)
    df["age_percentile"] = df.groupby("race_id")["horse_age"].rank(pct=True)

    # Rating features
    df["rating_rank"] = df.groupby("race_id")["form_rating"].rank(ascending=False)
    df["speed_rank"] = df.groupby("race_id")["speed_rating"].rank(ascending=False)
    df["class_rank"] = df.groupby("race_id")["class_rating"].rank(ascending=False)

    # Composite features
    df["total_rating"] = (
        df["form_rating"] + df["speed_rating"] + df["class_rating"]
    ) / 3
    df["rating_odds_ratio"] = df["total_rating"] / df["win_odds"]
    df["weight_odds_ratio"] = df["horse_weight_kg"] / df["win_odds"]

    # Experience features (simplified historical)
    df["horse_experience"] = df.groupby("horse_name").cumcount() + 1

    # Prize and distance features
    df["log_prize"] = np.log(df["prize_money"] + 1)
    df["prize_per_runner"] = df["prize_money"] / df["field_size"]

    # Distance processing (handle text distances)
    df["distance_numeric"] = pd.to_numeric(
        df["distance"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
    ).fillna(
        1600
    )  # Default to 1 mile
    df["distance_category"] = pd.cut(
        df["distance_numeric"],
        bins=[0, 1200, 1600, 2000, 3200, 10000],
        labels=[1, 2, 3, 4, 5],
    ).astype(float)

    # Encode categorical features
    logger.info("🏷️ Encoding categorical features...")

    encoders = {}
    categorical_features = [
        "course",
        "race_type",
        "class_level",
        "weather_condition",
        "track_condition",
    ]

    for feature in categorical_features:
        le = LabelEncoder()
        df[f"{feature}_encoded"] = le.fit_transform(df[feature].fillna("Unknown"))
        encoders[feature] = le

    # Select features for training
    feature_columns = [
        # Basic horse features
        "horse_age",
        "horse_weight_kg",
        "draw",
        "horse_experience",
        # Odds features
        "log_odds",
        "log_place_odds",
        "odds_rank",
        "odds_percentile",
        "is_favorite",
        "is_outsider",
        "market_strength",
        "market_share",
        # Competition features
        "draw_percentile",
        "weight_percentile",
        "age_percentile",
        # Rating features
        "form_rating",
        "speed_rating",
        "class_rating",
        "total_rating",
        "rating_rank",
        "speed_rank",
        "class_rank",
        # Composite features
        "rating_odds_ratio",
        "weight_odds_ratio",
        # Race features
        "field_size",
        "log_prize",
        "prize_per_runner",
        "distance_category",
        "market_percentage",
        # Encoded categorical features
        "course_encoded",
        "race_type_encoded",
        "class_level_encoded",
        "weather_condition_encoded",
        "track_condition_encoded",
    ]

    # Prepare training data
    X = df[feature_columns].fillna(0)
    y_win = df["won_race"]
    y_place = df["placed"]

    logger.info(f"🔢 Features: {len(feature_columns)}")
    logger.info(f"📊 Training samples: {len(X):,}")
    logger.info(f"🎯 Win rate: {y_win.mean():.4f}")
    logger.info(f"🥉 Place rate: {y_place.mean():.4f}")

    # Split data
    X_train, X_test, y_win_train, y_win_test, y_place_train, y_place_test = (
        train_test_split(
            X, y_win, y_place, test_size=0.2, random_state=42, stratify=y_win
        )
    )

    logger.info(f"📊 Training set: {len(X_train):,}")
    logger.info(f"📊 Test set: {len(X_test):,}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train models
    models = {}
    performance = {}

    # 1. Random Forest for Win Prediction
    logger.info("🌲 Training Random Forest (Win Prediction)...")
    rf_win = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf_win.fit(X_train, y_win_train)

    rf_win_pred = rf_win.predict(X_test)
    rf_win_prob = rf_win.predict_proba(X_test)[:, 1]

    performance["rf_win"] = {
        "accuracy": accuracy_score(y_win_test, rf_win_pred),
        "precision": precision_score(y_win_test, rf_win_pred),
        "recall": recall_score(y_win_test, rf_win_pred),
        "f1": f1_score(y_win_test, rf_win_pred),
        "roc_auc": roc_auc_score(y_win_test, rf_win_prob),
    }
    models["rf_win"] = rf_win

    logger.info(
        f"✅ RF Win - Accuracy: {performance['rf_win']['accuracy']:.3f}, AUC: {performance['rf_win']['roc_auc']:.3f}"
    )

    # 2. Gradient Boosting for Win Prediction
    logger.info("🚀 Training Gradient Boosting (Win Prediction)...")
    gb_win = GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42
    )
    gb_win.fit(X_train, y_win_train)

    gb_win_pred = gb_win.predict(X_test)
    gb_win_prob = gb_win.predict_proba(X_test)[:, 1]

    performance["gb_win"] = {
        "accuracy": accuracy_score(y_win_test, gb_win_pred),
        "precision": precision_score(y_win_test, gb_win_pred),
        "recall": recall_score(y_win_test, gb_win_pred),
        "f1": f1_score(y_win_test, gb_win_pred),
        "roc_auc": roc_auc_score(y_win_test, gb_win_prob),
    }
    models["gb_win"] = gb_win

    logger.info(
        f"✅ GB Win - Accuracy: {performance['gb_win']['accuracy']:.3f}, AUC: {performance['gb_win']['roc_auc']:.3f}"
    )

    # 3. Neural Network for Win Prediction
    logger.info("🧠 Training Neural Network (Win Prediction)...")
    nn_win = MLPClassifier(
        hidden_layer_sizes=(200, 100, 50),
        activation="relu",
        alpha=0.001,
        learning_rate="adaptive",
        max_iter=500,
        random_state=42,
    )
    nn_win.fit(X_train_scaled, y_win_train)

    nn_win_pred = nn_win.predict(X_test_scaled)
    nn_win_prob = nn_win.predict_proba(X_test_scaled)[:, 1]

    performance["nn_win"] = {
        "accuracy": accuracy_score(y_win_test, nn_win_pred),
        "precision": precision_score(y_win_test, nn_win_pred),
        "recall": recall_score(y_win_test, nn_win_pred),
        "f1": f1_score(y_win_test, nn_win_pred),
        "roc_auc": roc_auc_score(y_win_test, nn_win_prob),
    }
    models["nn_win"] = nn_win

    logger.info(
        f"✅ NN Win - Accuracy: {performance['nn_win']['accuracy']:.3f}, AUC: {performance['nn_win']['roc_auc']:.3f}"
    )

    # 4. Ensemble Model
    logger.info("🎭 Creating Ensemble Model...")
    ensemble_win = VotingClassifier(
        estimators=[("rf", rf_win), ("gb", gb_win)], voting="soft"
    )
    ensemble_win.fit(X_train, y_win_train)

    ensemble_win_pred = ensemble_win.predict(X_test)
    ensemble_win_prob = ensemble_win.predict_proba(X_test)[:, 1]

    performance["ensemble_win"] = {
        "accuracy": accuracy_score(y_win_test, ensemble_win_pred),
        "precision": precision_score(y_win_test, ensemble_win_pred),
        "recall": recall_score(y_win_test, ensemble_win_pred),
        "f1": f1_score(y_win_test, ensemble_win_pred),
        "roc_auc": roc_auc_score(y_win_test, ensemble_win_prob),
    }
    models["ensemble_win"] = ensemble_win

    logger.info(
        f"✅ Ensemble Win - Accuracy: {performance['ensemble_win']['accuracy']:.3f}, AUC: {performance['ensemble_win']['roc_auc']:.3f}"
    )

    # 5. Place Prediction Model
    logger.info("🥉 Training Place Prediction Model...")
    rf_place = RandomForestClassifier(
        n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1
    )
    rf_place.fit(X_train, y_place_train)

    rf_place_pred = rf_place.predict(X_test)
    rf_place_prob = rf_place.predict_proba(X_test)[:, 1]

    performance["rf_place"] = {
        "accuracy": accuracy_score(y_place_test, rf_place_pred),
        "precision": precision_score(y_place_test, rf_place_pred),
        "recall": recall_score(y_place_test, rf_place_pred),
        "f1": f1_score(y_place_test, rf_place_pred),
        "roc_auc": roc_auc_score(y_place_test, rf_place_prob),
    }
    models["rf_place"] = rf_place

    logger.info(
        f"✅ RF Place - Accuracy: {performance['rf_place']['accuracy']:.3f}, AUC: {performance['rf_place']['roc_auc']:.3f}"
    )

    # Save all models
    models_dir = Path("trained_models/full_dataset")
    models_dir.mkdir(parents=True, exist_ok=True)

    logger.info("💾 Saving all models...")

    # Save models
    for name, model in models.items():
        joblib.dump(model, models_dir / f"{name}_model.joblib")

    # Save preprocessing components
    joblib.dump(scaler, models_dir / "scaler.joblib")
    joblib.dump(encoders, models_dir / "encoders.joblib")
    joblib.dump(feature_columns, models_dir / "feature_columns.joblib")
    joblib.dump(performance, models_dir / "performance_metrics.joblib")

    # Feature importance analysis
    logger.info("📊 Analyzing feature importance...")
    feature_importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "rf_importance": rf_win.feature_importances_,
            "gb_importance": gb_win.feature_importances_,
        }
    )
    feature_importance["avg_importance"] = (
        feature_importance["rf_importance"] + feature_importance["gb_importance"]
    ) / 2
    feature_importance = feature_importance.sort_values(
        "avg_importance", ascending=False
    )

    # Save feature importance
    feature_importance.to_csv(models_dir / "feature_importance.csv", index=False)

    # Performance summary
    training_time = datetime.now() - start_time

    logger.info("\n" + "=" * 60)
    logger.info("🏆 FULL DATASET TRAINING COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"📊 Total records: {len(df):,}")
    logger.info(f"⏱️ Training time: {training_time}")
    logger.info(f"💾 Models saved to: {models_dir}")

    logger.info("\n🏆 MODEL PERFORMANCE SUMMARY:")
    logger.info("-" * 50)
    for model_name, metrics in performance.items():
        logger.info(f"\n🤖 {model_name.upper()}:")
        for metric, value in metrics.items():
            logger.info(f"  {metric:>12}: {value:.4f}")

    logger.info("\n🔝 TOP 10 FEATURES:")
    logger.info("-" * 40)
    for _, row in feature_importance.head(10).iterrows():
        logger.info(f"  {row['feature']:>25}: {row['avg_importance']:.4f}")

    # Prediction examples
    logger.info("\n🧪 PREDICTION EXAMPLES:")
    logger.info("-" * 30)

    test_df = df.iloc[X_test.index]

    # Best models for examples
    best_model = models["ensemble_win"]

    # Get favorites and outsiders
    favorites = test_df[test_df["is_favorite"] == 1].head(3)
    outsiders = test_df[test_df["is_outsider"] == 1].head(3)

    logger.info("\n🏇 FAVORITES:")
    for idx, row in favorites.iterrows():
        features = X_test.loc[[idx]]
        prob = best_model.predict_proba(features)[0, 1]
        logger.info(f"  Odds {row['win_odds']:.1f}: {prob:.3f} win probability")

    logger.info("\n🐴 OUTSIDERS:")
    for idx, row in outsiders.iterrows():
        features = X_test.loc[[idx]]
        prob = best_model.predict_proba(features)[0, 1]
        logger.info(f"  Odds {row['win_odds']:.1f}: {prob:.3f} win probability")

    logger.info(f"\n✅ Training complete! Check {models_dir} for all saved models.")


if __name__ == "__main__":
    full_dataset_ml_training()
