#!/usr/bin/env python3
"""
Simple AI Selections using trained models with real card data
Focuses on working with the actual database structure we have
"""

import logging
import os
import pandas as pd
import numpy as np
import psycopg2
from datetime import date
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class SimpleAISelections:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False

    def connect_results_db(self):
        return psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def connect_cards_db(self):
        return psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def train_simple_model(self):
        """Train a simple model on available historical data"""
        logger.info("🤖 Training simple AI model...")

        with self.connect_results_db() as conn:
            # Simple query to get basic training data
            query = """
                SELECT 
                    rec.race_id,
                    rec.position,
                    CAST(rec.starting_price AS FLOAT) as odds,
                    rec.age,
                    COUNT(*) OVER (PARTITION BY rec.race_id) as field_size,
                    ROW_NUMBER() OVER (PARTITION BY rec.race_id ORDER BY CAST(rec.starting_price AS FLOAT)) as market_rank
                FROM records rec
                WHERE rec.position IS NOT NULL 
                  AND rec.starting_price IS NOT NULL
                  AND CAST(rec.starting_price AS FLOAT) > 0
                  AND rec.age IS NOT NULL
                LIMIT 300
            """

            df = pd.read_sql_query(query, conn)

        logger.info(
            f"📊 Training on {len(df)} records from {df['race_id'].nunique()} races"
        )

        # Create features
        df["log_odds"] = np.log(df["odds"])
        df["implied_prob"] = 1.0 / df["odds"]
        df["is_favorite"] = (df["market_rank"] == 1).astype(int)
        df["field_dominance"] = df["field_size"] / df["market_rank"]
        df["is_winner"] = (df["position"] == 1).astype(int)

        # Features for training
        feature_cols = [
            "odds",
            "log_odds",
            "implied_prob",
            "age",
            "field_size",
            "market_rank",
            "is_favorite",
            "field_dominance",
        ]

        X = df[feature_cols].fillna(0).values
        y = df["is_winner"].values

        # Scale and train
        X_scaled = self.scaler.fit_transform(X)

        self.model = LogisticRegression(random_state=42)
        self.model.fit(X_scaled, y)

        accuracy = self.model.score(X_scaled, y)
        logger.info(f"✅ Model trained - Training accuracy: {accuracy:.3f}")
        self.trained = True

        return feature_cols

    def get_race_cards(self):
        """Get available race cards"""
        logger.info("📋 Loading race cards...")

        with self.connect_cards_db() as conn:
            today = date.today()

            # Check what dates we have
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT date FROM races ORDER BY date DESC LIMIT 5")
            available_dates = [row[0] for row in cursor.fetchall()]
            logger.info(f"Available race dates: {available_dates}")

            if not available_dates:
                logger.info("No race data found")
                return pd.DataFrame()

            # Use the most recent date
            target_date = available_dates[0]
            logger.info(f"Using races from: {target_date}")

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
                    COALESCE(CAST(rd.odds AS FLOAT), 5.0) as odds,
                    COALESCE(rd.age, 4) as age
                FROM races r
                JOIN racecard_details rd ON r.race_id = rd.race_id
                WHERE r.date = %s
                ORDER BY r.race_time, rd.number
            """

            df = pd.read_sql_query(query, conn, params=(target_date,))

        logger.info(f"📋 Found {len(df)} horses in {df['race_id'].nunique()} races")
        return df

    def make_selections(self, cards_df, feature_cols):
        """Make AI selections for the race cards"""
        if not self.trained:
            raise ValueError("Model must be trained first!")

        logger.info("🎯 Making AI selections...")

        # Prepare features
        pred_df = cards_df.copy()
        pred_df["log_odds"] = np.log(pred_df["odds"])
        pred_df["implied_prob"] = 1.0 / pred_df["odds"]
        pred_df["field_size"] = pred_df.groupby("race_id")["race_id"].transform("count")
        pred_df["market_rank"] = pred_df.groupby("race_id")["odds"].rank()
        pred_df["is_favorite"] = (pred_df["market_rank"] == 1).astype(int)
        pred_df["field_dominance"] = pred_df["field_size"] / pred_df["market_rank"]

        # Make predictions
        X = pred_df[feature_cols].fillna(0).values
        X_scaled = self.scaler.transform(X)

        win_probs = self.model.predict_proba(X_scaled)[:, 1]
        pred_df["ai_win_prob"] = win_probs

        return pred_df

    def run_full_analysis(self):
        """Run complete analysis - train model and make selections"""
        logger.info("🚀 Starting AI Horse Racing Analysis")
        logger.info("=" * 60)

        # Train model
        feature_cols = self.train_simple_model()

        # Get race cards
        cards_df = self.get_race_cards()

        if len(cards_df) == 0:
            logger.info("❌ No race cards available")
            return

        # Make selections
        selections_df = self.make_selections(cards_df, feature_cols)

        # Display results
        logger.info("\\n" + "=" * 60)
        logger.info("🏇 AI HORSE RACING SELECTIONS")
        logger.info("=" * 60)

        for race_id in selections_df["race_id"].unique():
            race_data = selections_df[selections_df["race_id"] == race_id].copy()
            race_data = race_data.sort_values("ai_win_prob", ascending=False)

            race_info = race_data.iloc[0]
            logger.info(f"\\n📍 Race {race_id}: {race_info['course']}")
            logger.info(
                f"🕐 Time: {race_info['race_time']} | Date: {race_info['date']}"
            )
            logger.info("-" * 50)

            # Top 3 AI selections
            for i, (_, horse) in enumerate(race_data.head(3).iterrows()):
                confidence_pct = horse["ai_win_prob"] * 100
                logger.info(f"{i+1}. {horse['horse_name']}")
                logger.info(f"   🏃 Jockey: {horse['jockey']}")
                logger.info(f"   💰 Odds: {horse['odds']:.1f}/1")
                logger.info(f"   🤖 AI Confidence: {confidence_pct:.1f}%")
                logger.info("")

        logger.info("✅ AI Analysis Complete!")


if __name__ == "__main__":
    try:
        ai = SimpleAISelections()
        ai.run_full_analysis()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
