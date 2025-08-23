#!/usr/bin/env python3
"""
Simplified ML Training Script for Results Database
Debug version to identify and fix any hanging issues
"""

import logging
import sys
import os
import pandas as pd
import numpy as np
import psycopg2
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import warnings

warnings.filterwarnings("ignore")

sys.path.append("/app")
from tools.ml_training.standalone_course_mapper import StandaloneCourseMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 Starting Simplified ML Training Pipeline")

    try:
        # 1. Database connection
        logger.info("📊 Connecting to database...")
        conn = psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

        # 2. Load course mapper
        logger.info("🗺️ Loading course mapper...")
        course_mapper = StandaloneCourseMapper()

        # 3. Load data
        logger.info("📈 Loading race data...")
        query = """
        SELECT 
            rec.race_id,
            rec.horse_name,
            rec.jockey,
            rec.trainer,
            rec.position,
            rec.horse_id,
            rec.jockey_id,
            rec.trainer_id,
            CAST(rec.starting_price AS FLOAT) as odds_decimal,
            1.0 / CAST(rec.starting_price AS FLOAT) as implied_probability,
            LN(CAST(rec.starting_price AS FLOAT)) as log_odds,
            10.0 as horse_weight_kg,
            CAST(rec.age AS INT) as horse_age,
            COUNT(*) OVER (PARTITION BY rec.race_id) as field_size,
            ROW_NUMBER() OVER (PARTITION BY rec.race_id ORDER BY CAST(rec.starting_price AS FLOAT)) as odds_rank,
            CASE WHEN ROW_NUMBER() OVER (PARTITION BY rec.race_id ORDER BY CAST(rec.starting_price AS FLOAT)) = 1 THEN 1 ELSE 0 END as is_favorite,
            COALESCE(js.win_rate, 0.0) as jockey_win_pct,
            COALESCE(js.place_rate, 0.0) as jockey_place_pct,
            COALESCE(ts.win_rate, 0.0) as trainer_win_pct,
            COALESCE(ts.place_rate, 0.0) as trainer_place_pct
        FROM records rec
        LEFT JOIN jockeys_stats js ON rec.jockey_id = js.jockey_id
        LEFT JOIN trainers_stats ts ON rec.trainer_id = ts.trainer_id
        WHERE rec.position IS NOT NULL
          AND rec.starting_price IS NOT NULL
          AND CAST(rec.starting_price AS FLOAT) > 0
          AND rec.jockey_id IS NOT NULL
          AND rec.trainer_id IS NOT NULL
        ORDER BY rec.race_id, CAST(rec.starting_price AS FLOAT)
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(f"✅ Loaded {len(df)} records from {df['race_id'].nunique()} races")

        # 4. Create target variable
        logger.info("🎯 Creating target variable...")
        df["is_winner"] = (df["position"] == 1).astype(int)
        win_rate = df["is_winner"].mean()
        logger.info(f"✅ Win rate: {win_rate:.2%} ({df['is_winner'].sum()} winners)")

        # 5. Feature engineering
        logger.info("⚙️ Creating features...")
        features_df = df.copy()

        # Performance features (already in percentage format)
        features_df["jockey_performance"] = features_df["jockey_win_pct"] / 100.0
        features_df["trainer_performance"] = features_df["trainer_win_pct"] / 100.0
        features_df["combined_performance"] = (
            features_df["jockey_performance"] * 0.6
            + features_df["trainer_performance"] * 0.4
        )

        # Market features
        features_df["market_position"] = 1.0 / features_df["odds_rank"]
        features_df["field_dominance"] = (
            features_df["field_size"] / features_df["odds_rank"]
        )

        # Select feature columns
        feature_columns = [
            "odds_decimal",
            "implied_probability",
            "log_odds",
            "horse_weight_kg",
            "horse_age",
            "field_size",
            "odds_rank",
            "is_favorite",
            "jockey_performance",
            "trainer_performance",
            "combined_performance",
            "market_position",
            "field_dominance",
        ]

        # Prepare data
        X = features_df[feature_columns]
        y = features_df["is_winner"]

        logger.info(f"✅ Created {len(feature_columns)} features for {len(X)} records")

        # 6. Handle missing values
        logger.info("🧹 Handling missing values...")
        X = X.fillna(0)

        # 7. Split data
        logger.info("✂️ Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"✅ Training set: {len(X_train)} records")
        logger.info(f"✅ Test set: {len(X_test)} records")

        # 8. Scale features
        logger.info("📏 Scaling features...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 9. Train models
        logger.info("🤖 Training models...")

        models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=100, random_state=42, n_jobs=1
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=100, random_state=42
            ),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000),
        }

        results = {}
        for name, model in models.items():
            logger.info(f"  Training {name}...")

            if name == "LogisticRegression":
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

            # Calculate metrics
            report = classification_report(y_test, y_pred, output_dict=True)

            results[name] = {
                "auc": auc,
                "accuracy": report["accuracy"],
                "precision": report["1"]["precision"],
                "recall": report["1"]["recall"],
                "f1": report["1"]["f1-score"],
            }

            logger.info(
                f"  ✅ {name} - AUC: {auc:.4f}, Accuracy: {report['accuracy']:.4f}"
            )

        # 10. Results summary
        logger.info("📊 TRAINING RESULTS SUMMARY")
        logger.info("=" * 50)
        for name, metrics in results.items():
            logger.info(f"{name}:")
            logger.info(f"  AUC: {metrics['auc']:.4f}")
            logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall: {metrics['recall']:.4f}")
            logger.info(f"  F1-Score: {metrics['f1']:.4f}")
            logger.info("-" * 30)

        # Find best model
        best_model = max(results.keys(), key=lambda x: results[x]["auc"])
        logger.info(
            f"🏆 Best Model: {best_model} (AUC: {results[best_model]['auc']:.4f})"
        )

        logger.info("✅ ML Training Pipeline Completed Successfully!")

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
