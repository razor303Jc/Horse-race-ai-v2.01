#!/usr/bin/env python3
"""
Working Real AI Selections Generator for Horse Racing
Uses trained ML models with real card data from cards_horse_racing_db
"""

import logging
import sys
import os
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, date, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings

warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkingRealAISelectionsGenerator:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.trained = False

    def connect_results_database(self):
        """Connect to results database for training"""
        return psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def connect_cards_database(self):
        """Connect to cards database for race card data"""
        return psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def load_training_data(self, limit=10000):
        """Load training data with limit to avoid memory issues"""
        logger.info(f"Loading training data (limit: {limit})...")

        conn = self.connect_results_database()

        query = f"""
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
        ORDER BY rec.race_id DESC
        LIMIT {limit}
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(
            f"📊 Loaded {len(df)} training records from {df['race_id'].nunique()} races"
        )
        return df

    def prepare_features(self, df):
        """Prepare features for training"""
        logger.info("Preparing features...")

        features_df = df.copy()
        features_df["is_winner"] = (features_df["position"] == 1).astype(int)

        # Performance features
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
        features_df["odds_value"] = features_df["implied_probability"] - (
            1.0 / features_df["field_size"]
        )

        # Select features for training
        feature_cols = [
            "odds_decimal",
            "implied_probability",
            "log_odds",
            "horse_age",
            "field_size",
            "odds_rank",
            "is_favorite",
            "jockey_performance",
            "trainer_performance",
            "combined_performance",
            "market_position",
            "field_dominance",
            "odds_value",
        ]

        # Remove any rows with NaN values
        features_df = features_df.dropna(subset=feature_cols + ["is_winner"])

        logger.info(f"Features prepared: {len(features_df)} clean records")
        return features_df, feature_cols

    def train_models(self):
        """Train ensemble models"""
        logger.info("🤖 Training ensemble models...")

        # Load training data
        training_data = self.load_training_data(
            limit=50000
        )  # Start with manageable amount
        features_df, feature_cols = self.prepare_features(training_data)

        # Prepare training data
        X = features_df[feature_cols].values
        y = features_df["is_winner"].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(
            f"Training on {len(X_train)} samples, testing on {len(X_test)} samples"
        )

        # Train models
        self.models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boost": GradientBoostingClassifier(
                n_estimators=100, random_state=42
            ),
            "logistic": LogisticRegression(random_state=42, max_iter=1000),
        }

        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)

            logger.info(f"{name}: Accuracy={accuracy:.4f}, AUC={auc:.4f}")

        self.feature_columns = feature_cols
        self.trained = True
        logger.info("✅ Model training completed!")

    def get_todays_races(self):
        """Get today's race cards"""
        logger.info("Loading today's race cards...")

        conn = self.connect_cards_database()
        today = date.today()

        query = """
            SELECT 
                r.race_id,
                r.course,
                r.race_time,
                r.date,
                rd.horse_name,
                rd.jockey,
                rd.trainer,
                rd.number,
                CAST(rd.odds AS FLOAT) as odds_decimal,
                rd.age,
                rd.form
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            WHERE r.date >= %s
            ORDER BY r.date, r.race_time, rd.number
        """

        df = pd.read_sql_query(query, conn, params=(today,))
        conn.close()

        logger.info(f"Found {len(df)} horses in {df['race_id'].nunique()} races")
        return df

    def make_predictions(self, card_data):
        """Make predictions for race card data"""
        if not self.trained:
            raise ValueError("Models must be trained first!")

        logger.info("Making predictions...")

        # Prepare features for prediction (simplified version)
        pred_df = card_data.copy()

        # Add basic features
        pred_df["implied_probability"] = 1.0 / pred_df["odds_decimal"]
        pred_df["log_odds"] = np.log(pred_df["odds_decimal"])
        pred_df["horse_age"] = pred_df["age"].fillna(4)  # Default age
        pred_df["field_size"] = pred_df.groupby("race_id")["race_id"].transform("count")
        pred_df["odds_rank"] = pred_df.groupby("race_id")["odds_decimal"].rank()
        pred_df["is_favorite"] = (pred_df["odds_rank"] == 1).astype(int)

        # Default performance values (would need lookup in real system)
        pred_df["jockey_performance"] = 0.1  # 10% default
        pred_df["trainer_performance"] = 0.1  # 10% default
        pred_df["combined_performance"] = 0.1
        pred_df["market_position"] = 1.0 / pred_df["odds_rank"]
        pred_df["field_dominance"] = pred_df["field_size"] / pred_df["odds_rank"]
        pred_df["odds_value"] = pred_df["implied_probability"] - (
            1.0 / pred_df["field_size"]
        )

        # Select features
        X_pred = pred_df[self.feature_columns].fillna(0).values
        X_pred_scaled = self.scaler.transform(X_pred)

        # Get ensemble predictions
        predictions = {}
        for name, model in self.models.items():
            pred_proba = model.predict_proba(X_pred_scaled)[:, 1]
            predictions[f"{name}_prob"] = pred_proba

        # Ensemble average
        ensemble_prob = np.mean(list(predictions.values()), axis=0)
        predictions["ensemble_prob"] = ensemble_prob

        # Add predictions to dataframe
        for key, values in predictions.items():
            pred_df[key] = values

        return pred_df

    def generate_selections(self):
        """Generate AI selections for today's races"""
        logger.info("🎯 Generating AI selections for today's races...")

        # Train models
        self.train_models()

        # Get today's cards
        card_data = self.get_todays_races()

        if len(card_data) == 0:
            logger.info("No races found for today")
            return

        # Make predictions
        predictions = self.make_predictions(card_data)

        # Generate selections for each race
        logger.info("\n" + "=" * 80)
        logger.info("🏇 AI HORSE RACING SELECTIONS")
        logger.info("=" * 80)

        for race_id in predictions["race_id"].unique():
            race_data = predictions[predictions["race_id"] == race_id].copy()
            race_data = race_data.sort_values("ensemble_prob", ascending=False)

            race_info = race_data.iloc[0]
            logger.info(
                f"\n📍 Race {race_id}: {race_info['course']} - {race_info['race_time']}"
            )
            logger.info(f"Date: {race_info['date']}")
            logger.info("-" * 60)

            # Top 3 selections
            for i, (_, horse) in enumerate(race_data.head(3).iterrows()):
                logger.info(f"{i+1}. {horse['horse_name']} ({horse['jockey']})")
                logger.info(f"   Odds: {horse['odds_decimal']:.1f}/1")
                logger.info(f"   AI Confidence: {horse['ensemble_prob']:.3f}")
                logger.info(f"   Trainer: {horse['trainer']}")
                logger.info("")


if __name__ == "__main__":
    try:
        generator = WorkingRealAISelectionsGenerator()
        generator.generate_selections()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
