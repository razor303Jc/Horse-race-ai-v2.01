#!/usr/bin/env python3
"""
Container-Optimized AI Selections Generator
Generates AI selections for specified dates using trained ML models in container environment
"""

import json
import logging
import sys
import argparse
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import psycopg2
from sklearn.preprocessing import StandardScaler

# Setup logging for container environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class ContainerAISelections:
    """Container-optimized AI selections generator"""

    def __init__(self):
        # Database configurations for container environment
        self.results_db_config = {
            "host": "postgres",
            "port": "5432",
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        self.cards_db_config = {
            "host": "postgres",
            "port": "5432",
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # For container environment, we'll use the trained models from our last training session
        # In production, these would be loaded from persistent storage
        self.trained_model = None
        self.scaler = None
        self.feature_names = [
            "win_odds",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "odds_rank",
            "is_favorite",
            "implied_probability",
            "log_odds",
            "field_size",
            "jockey_performance_ratio",
            "trainer_performance_ratio",
            "prize_money",
            "distance",
            "prize_per_meter",
            "jockey_wins",
            "trainer_wins",
            "jockey_runs",
        ]

    def get_training_data_for_model(self):
        """Get training data to rebuild the model (since we can't persist in container)"""
        logger.info("🔄 Rebuilding model from training data...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    r.*,
                    js.wins as jockey_wins,
                    js.runs as jockey_runs,
                    js.win_rate as jockey_win_pct,
                    ts.wins as trainer_wins,
                    ts.runs as trainer_runs,
                    ts.win_rate as trainer_win_pct,
                    ra.course,
                    ra.distance,
                    ra.date as race_date,
                    ra.prize as prize_money
                FROM records r
                LEFT JOIN jockeys_stats js ON r.jockey = js.jockey_name
                LEFT JOIN trainers_stats ts ON r.trainer = ts.trainer_name
                LEFT JOIN races ra ON r.race_id = ra.race_id
                WHERE r.jockey != 'none' 
                AND r.trainer != 'none'
                AND r.position IS NOT NULL
                AND r.starting_price > 0
                ORDER BY r.record_id DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            # Engineer features (same as training)
            df["win_odds"] = pd.to_numeric(df["starting_price"], errors="coerce")
            df["horse_age"] = pd.to_numeric(df["age"], errors="coerce")
            df["horse_weight_kg"] = pd.to_numeric(df["weight"], errors="coerce").fillna(
                60
            )
            if "draw" not in df.columns:
                df["draw"] = 1
            df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(1)
            df["finished_position"] = pd.to_numeric(df["position"], errors="coerce")

            # Clean missing values
            df = df.dropna(subset=["win_odds", "horse_age", "finished_position"])
            df = df[df["win_odds"] > 0]

            # Fill missing stats
            df["jockey_wins"] = df["jockey_wins"].fillna(0)
            df["jockey_runs"] = df["jockey_runs"].fillna(1)
            df["jockey_win_pct"] = df["jockey_win_pct"].fillna(5.0)
            df["trainer_wins"] = df["trainer_wins"].fillna(0)
            df["trainer_runs"] = df["trainer_runs"].fillna(1)
            df["trainer_win_pct"] = df["trainer_win_pct"].fillna(5.0)

            # Additional features
            df["odds_rank"] = df.groupby("race_id")["win_odds"].rank()
            df["is_favorite"] = (df["odds_rank"] == 1).astype(int)
            df["implied_probability"] = 1.0 / df["win_odds"]
            df["log_odds"] = np.log(df["win_odds"])
            df["field_size"] = df.groupby("race_id")["race_id"].transform("count")
            df["jockey_performance_ratio"] = df["jockey_win_pct"] / 100.0
            df["trainer_performance_ratio"] = df["trainer_win_pct"] / 100.0
            df["prize_money"] = pd.to_numeric(
                df["prize_money"], errors="coerce"
            ).fillna(1000)
            df["distance"] = pd.to_numeric(df["distance"], errors="coerce").fillna(1600)
            df["prize_per_meter"] = df["prize_money"] / df["distance"]

            # Create target and features
            df["is_winner"] = (df["finished_position"] == 1).astype(int)

            # Select features
            X = df[self.feature_names].values
            y = df["is_winner"].values

            # Handle NaN values
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

            logger.info(f"✅ Loaded {len(df)} training records")
            return X, y

        except Exception as e:
            logger.error(f"❌ Failed to load training data: {e}")
            raise

    def train_model(self):
        """Train the model for predictions (since we can't persist in container)"""
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        logger.info("🤖 Training prediction model...")

        # Get training data
        X, y = self.get_training_data_for_model()

        # Train scaler and model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Use LogisticRegression (best performer from our training)
        self.trained_model = LogisticRegression(
            random_state=42, max_iter=1000, solver="liblinear"
        )
        self.trained_model.fit(X_scaled, y)

        logger.info("✅ Model trained successfully")

    def get_race_cards_for_date(self, target_date: str) -> pd.DataFrame:
        """Get race card data for the specified date"""
        logger.info(f"📅 Loading race cards for {target_date}...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)

            query = """
                SELECT 
                    r.race_id,
                    r.race_number,
                    r.course,
                    r.race_time,
                    r.race_name,
                    r.class,
                    r.distance,
                    r.prize as prize_money,
                    rd.detail_id,
                    rd.horse_name,
                    rd.jockey,
                    rd.trainer,
                    rd.number as draw,
                    rd.weight,
                    rd.age,
                    rd.odds,
                    rd.form,
                    js.wins as jockey_wins,
                    js.runs as jockey_runs,
                    js.win_rate as jockey_win_pct,
                    ts.wins as trainer_wins,
                    ts.runs as trainer_runs,
                    ts.win_rate as trainer_win_pct
                FROM races r
                JOIN racecard_details rd ON r.race_id = rd.race_id
                LEFT JOIN jockeys_stats js ON rd.jockey = js.jockey_name
                LEFT JOIN trainers_stats ts ON rd.trainer = ts.trainer_name
                WHERE r.date = %s
                ORDER BY r.course, r.race_time, rd.number
            """

            df = pd.read_sql_query(query, conn, params=[target_date])
            conn.close()

            logger.info(
                f"✅ Loaded {len(df)} runners from {df['race_id'].nunique()} races"
            )
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load race cards: {e}")
            raise

    def engineer_prediction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for prediction (same as training)"""
        logger.info("⚙️ Engineering prediction features...")

        df_features = df.copy()

        # Convert and clean data
        df_features["win_odds"] = pd.to_numeric(
            df_features["odds"], errors="coerce"
        ).fillna(5.0)
        df_features["horse_age"] = pd.to_numeric(
            df_features["age"], errors="coerce"
        ).fillna(4)
        df_features["horse_weight_kg"] = pd.to_numeric(
            df_features["weight"], errors="coerce"
        ).fillna(60)
        df_features["draw"] = pd.to_numeric(
            df_features["draw"], errors="coerce"
        ).fillna(1)

        # Fill missing stats
        df_features["jockey_wins"] = df_features["jockey_wins"].fillna(0)
        df_features["jockey_runs"] = df_features["jockey_runs"].fillna(1)
        df_features["jockey_win_pct"] = df_features["jockey_win_pct"].fillna(5.0)
        df_features["trainer_wins"] = df_features["trainer_wins"].fillna(0)
        df_features["trainer_runs"] = df_features["trainer_runs"].fillna(1)
        df_features["trainer_win_pct"] = df_features["trainer_win_pct"].fillna(5.0)

        # Race-level features
        df_features["odds_rank"] = df_features.groupby("race_id")["win_odds"].rank()
        df_features["is_favorite"] = (df_features["odds_rank"] == 1).astype(int)
        df_features["implied_probability"] = 1.0 / df_features["win_odds"]
        df_features["log_odds"] = np.log(df_features["win_odds"])
        df_features["field_size"] = df_features.groupby("race_id")["race_id"].transform(
            "count"
        )

        # Performance features
        df_features["jockey_performance_ratio"] = df_features["jockey_win_pct"] / 100.0
        df_features["trainer_performance_ratio"] = (
            df_features["trainer_win_pct"] / 100.0
        )

        # Distance and prize features
        df_features["prize_money"] = pd.to_numeric(
            df_features["prize_money"], errors="coerce"
        ).fillna(1000)
        df_features["distance"] = pd.to_numeric(
            df_features["distance"], errors="coerce"
        ).fillna(1600)
        df_features["prize_per_meter"] = (
            df_features["prize_money"] / df_features["distance"]
        )

        logger.info(f"✅ Features engineered for {len(df_features)} runners")
        return df_features

    def generate_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate AI predictions for the race cards"""
        logger.info("🎯 Generating AI predictions...")

        # Prepare features
        X = df[self.feature_names].values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Get predictions
        win_probabilities = self.trained_model.predict_proba(X_scaled)[:, 1]

        # Add predictions to dataframe
        df_predictions = df.copy()
        df_predictions["ai_win_probability"] = win_probabilities
        df_predictions["ai_confidence"] = np.where(
            win_probabilities > 0.5,
            "High",
            np.where(win_probabilities > 0.3, "Medium", "Low"),
        )

        # Rank by race
        df_predictions["ai_ranking"] = df_predictions.groupby("race_id")[
            "ai_win_probability"
        ].rank(ascending=False)

        logger.info(f"✅ Generated predictions for {len(df_predictions)} runners")
        return df_predictions

    def save_selections_to_database(self, df: pd.DataFrame, target_date: str):
        """Save AI selections to the cards database"""
        logger.info("💾 Saving AI selections to database...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)
            cursor = conn.cursor()

            # Clear existing selections for this date
            cursor.execute(
                "DELETE FROM ai_selections WHERE race_date = %s", [target_date]
            )

            # Insert new selections
            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO ai_selections (
                        race_id, detail_id, horse_name, win_probability, confidence_score,
                        model_name, model_version, ai_selection_type, race_date, course,
                        race_number, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    [
                        row["race_id"],
                        row["detail_id"],
                        row["horse_name"],
                        float(row["ai_win_probability"]),
                        float(row["ai_win_probability"]),
                        "LogisticRegression",
                        "v1.0",
                        "win",
                        target_date,
                        row["course"],
                        row["race_number"],
                        datetime.now(),
                    ],
                )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Saved {len(df)} AI selections to database")

        except Exception as e:
            logger.error(f"❌ Failed to save selections: {e}")
            raise

    def generate_selections_for_date(self, target_date: str):
        """Complete pipeline to generate AI selections for a date"""
        logger.info(f"🎯 Starting AI selections generation for {target_date}")

        try:
            # Train model (since we can't persist in container)
            self.train_model()

            # Get race cards
            race_cards = self.get_race_cards_for_date(target_date)

            if len(race_cards) == 0:
                logger.warning(f"❌ No race cards found for {target_date}")
                return

            # Engineer features
            race_cards_features = self.engineer_prediction_features(race_cards)

            # Generate predictions
            predictions = self.generate_predictions(race_cards_features)

            # Save to database
            self.save_selections_to_database(predictions, target_date)

            # Show summary
            summary = (
                predictions.groupby(["race_id", "course", "race_time"])
                .agg({"horse_name": "count", "ai_win_probability": "max"})
                .rename(
                    columns={
                        "horse_name": "runners",
                        "ai_win_probability": "top_probability",
                    }
                )
            )

            logger.info("📊 AI Selections Summary:")
            print(summary)

            # Show top selections
            top_selections = predictions[predictions["ai_ranking"] <= 3].sort_values(
                ["race_id", "ai_ranking"]
            )[
                [
                    "race_id",
                    "course",
                    "race_time",
                    "horse_name",
                    "jockey",
                    "ai_win_probability",
                    "ai_confidence",
                ]
            ]

            logger.info("🏆 Top 3 AI Selections per race:")
            print(top_selections)

            logger.info(f"🎉 AI selections generation completed for {target_date}")

        except Exception as e:
            logger.error(f"❌ Failed to generate selections: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI selections for horse racing"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="2025-08-22",
        help="Date for selections (YYYY-MM-DD)",
    )

    args = parser.parse_args()

    generator = ContainerAISelections()
    generator.generate_selections_for_date(args.date)


if __name__ == "__main__":
    main()
