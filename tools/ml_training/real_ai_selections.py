#!/usr/bin/env python3
"""
Real AI Selections Generator for Horse Racing
Uses trained ML models with actual race card data from the database
"""

import logging
import sys
import os
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, date
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings
import re

warnings.filterwarnings("ignore")

sys.path.append("/app")
from tools.ml_training.standalone_course_mapper import StandaloneCourseMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealAISelectionsGenerator:
    def __init__(self):
        self.course_mapper = StandaloneCourseMapper()
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

    def connect_card_database(self):
        """Connect to card database for live data"""
        return psycopg2.connect(
            host="postgres",
            database="horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def train_ensemble_models(self):
        """Train the ensemble models on results data"""
        logger.info("🤖 Training ensemble models on historical results...")

        conn = self.connect_results_database()

        # Load training data from results database
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

        logger.info(
            f"📊 Loaded {len(df)} training records from {df['race_id'].nunique()} races"
        )

        # Feature engineering
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

        # Advanced features
        features_df["odds_value"] = features_df["implied_probability"] - (
            1.0 / features_df["field_size"]
        )
        features_df["favorite_advantage"] = (
            features_df["is_favorite"] * features_df["combined_performance"]
        )
        features_df["age_performance"] = (
            features_df["horse_age"] * features_df["combined_performance"]
        )

        # Select features
        self.feature_columns = [
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
            "odds_value",
            "favorite_advantage",
            "age_performance",
        ]

        X = features_df[self.feature_columns].fillna(0)
        y = features_df["is_winner"]

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train models with optimized parameters
        logger.info("  Training RandomForest...")
        self.models["RandomForest"] = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=3,
            random_state=42,
            n_jobs=1,
        )
        self.models["RandomForest"].fit(X, y)

        logger.info("  Training GradientBoosting...")
        self.models["GradientBoosting"] = GradientBoostingClassifier(
            n_estimators=120, learning_rate=0.08, max_depth=8, random_state=42
        )
        self.models["GradientBoosting"].fit(X, y)

        logger.info("  Training LogisticRegression...")
        self.models["LogisticRegression"] = LogisticRegression(
            C=2.0, random_state=42, max_iter=1000
        )
        self.models["LogisticRegression"].fit(X_scaled, y)

        self.trained = True
        logger.info("✅ Ensemble models trained successfully")

        return {
            "total_records": len(df),
            "total_races": df["race_id"].nunique(),
            "win_rate": y.mean(),
            "features_used": len(self.feature_columns),
        }

    def get_jockey_trainer_stats(self, jockey_name, trainer_name):
        """Get jockey and trainer statistics from results database"""
        conn = self.connect_results_database()
        cursor = conn.cursor()

        # Get jockey stats
        cursor.execute(
            "SELECT win_rate FROM jockeys_stats WHERE jockey_name = %s", (jockey_name,)
        )
        jockey_result = cursor.fetchone()
        jockey_win_rate = (
            float(jockey_result[0]) if jockey_result and jockey_result[0] else 8.0
        )

        # Get trainer stats
        cursor.execute(
            "SELECT win_rate FROM trainers_stats WHERE trainer_name = %s",
            (trainer_name,),
        )
        trainer_result = cursor.fetchone()
        trainer_win_rate = (
            float(trainer_result[0]) if trainer_result and trainer_result[0] else 12.0
        )

        conn.close()
        return jockey_win_rate, trainer_win_rate

    def parse_odds(self, odds_text):
        """Parse odds text to decimal format"""
        if not odds_text or odds_text == "N/A":
            return 10.0  # Default odds

        # Handle different odds formats
        odds_text = str(odds_text).strip()

        # Decimal odds (e.g., "3.5", "2.00")
        if re.match(r"^\d+\.?\d*$", odds_text):
            return float(odds_text)

        # Fractional odds (e.g., "7/2", "5/1")
        if "/" in odds_text:
            try:
                numerator, denominator = odds_text.split("/")
                return (float(numerator) / float(denominator)) + 1.0
            except:
                return 10.0

        # Handle special cases
        if odds_text.lower() == "evens" or odds_text == "1/1":
            return 2.0

        return 10.0  # Default fallback

    def get_live_race_cards(self):
        """Get today's race cards from the card database"""
        logger.info("🏇 Loading today's race cards...")

        conn = self.connect_card_database()

        # Get today's races
        today = date.today()

        race_query = """
        SELECT race_id, course, race_time, race_name, runners_racecard
        FROM races 
        WHERE date = %s
        ORDER BY race_time
        """

        races_df = pd.read_sql_query(race_query, conn, params=(today,))

        if races_df.empty:
            logger.warning("No races found for today, using recent races...")
            # Get most recent races if no races today
            race_query = """
            SELECT race_id, course, race_time, race_name, runners_racecard
            FROM races 
            ORDER BY date DESC, race_time DESC
            LIMIT 5
            """
            races_df = pd.read_sql_query(race_query, conn)

        logger.info(f"📅 Found {len(races_df)} races")

        # Get race card details for each race
        all_race_cards = []

        for _, race in races_df.iterrows():
            race_id = race["race_id"]

            card_query = """
            SELECT horse_name, jockey, trainer, number, weight, age, form, odds
            FROM racecard_details
            WHERE race_id = %s
            ORDER BY number
            """

            card_df = pd.read_sql_query(card_query, conn, params=(race_id,))

            if not card_df.empty:
                race_card = {
                    "race_id": race_id,
                    "course": race["course"],
                    "time": race["race_time"],
                    "race_name": race["race_name"],
                    "runners": len(card_df),
                    "horses": card_df.to_dict("records"),
                }
                all_race_cards.append(race_card)
                logger.info(
                    f"  📋 {race['course']} {race['race_time']}: {len(card_df)} runners"
                )

        conn.close()
        return all_race_cards

    def generate_race_predictions(self, race_data):
        """Generate predictions for a live race"""
        if not self.trained:
            raise Exception("Models not trained. Call train_ensemble_models() first.")

        horses_data = []
        field_size = len(race_data["horses"])

        # Sort horses by odds for ranking
        horses_with_odds = []
        for horse in race_data["horses"]:
            odds_decimal = self.parse_odds(horse["odds"])
            horses_with_odds.append({**horse, "odds_decimal": odds_decimal})

        # Sort by odds (lowest = favorite)
        horses_with_odds.sort(key=lambda x: x["odds_decimal"])

        for i, horse in enumerate(horses_with_odds):
            # Get jockey/trainer stats
            jockey_win_rate, trainer_win_rate = self.get_jockey_trainer_stats(
                horse["jockey"], horse["trainer"]
            )

            # Create features
            odds_decimal = horse["odds_decimal"]
            implied_probability = 1.0 / odds_decimal
            log_odds = np.log(odds_decimal) if odds_decimal > 0 else 0
            horse_age = horse.get("age", 5)
            odds_rank = i + 1
            is_favorite = 1 if i == 0 else 0

            # Performance features
            jockey_performance = jockey_win_rate / 100.0
            trainer_performance = trainer_win_rate / 100.0
            combined_performance = jockey_performance * 0.6 + trainer_performance * 0.4

            # Market features
            market_position = 1.0 / odds_rank
            field_dominance = field_size / odds_rank

            # Advanced features
            odds_value = implied_probability - (1.0 / field_size)
            favorite_advantage = is_favorite * combined_performance
            age_performance = horse_age * combined_performance

            horse_features = {
                "horse_name": horse["horse_name"],
                "jockey": horse["jockey"],
                "trainer": horse["trainer"],
                "number": horse.get("number", i + 1),
                "form": horse.get("form", ""),
                "odds_text": horse["odds"],
                "odds_decimal": odds_decimal,
                "implied_probability": implied_probability,
                "log_odds": log_odds,
                "horse_weight_kg": 10.0,
                "horse_age": horse_age,
                "field_size": field_size,
                "odds_rank": odds_rank,
                "is_favorite": is_favorite,
                "jockey_performance": jockey_performance,
                "trainer_performance": trainer_performance,
                "combined_performance": combined_performance,
                "market_position": market_position,
                "field_dominance": field_dominance,
                "odds_value": odds_value,
                "favorite_advantage": favorite_advantage,
                "age_performance": age_performance,
                "jockey_win_rate": jockey_win_rate,
                "trainer_win_rate": trainer_win_rate,
            }

            horses_data.append(horse_features)

        # Convert to DataFrame
        df = pd.DataFrame(horses_data)
        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)

        # Generate predictions from all models
        predictions = {}

        # RandomForest predictions
        rf_proba = self.models["RandomForest"].predict_proba(X)[:, 1]
        predictions["RandomForest"] = rf_proba

        # GradientBoosting predictions
        gb_proba = self.models["GradientBoosting"].predict_proba(X)[:, 1]
        predictions["GradientBoosting"] = gb_proba

        # LogisticRegression predictions
        lr_proba = self.models["LogisticRegression"].predict_proba(X_scaled)[:, 1]
        predictions["LogisticRegression"] = lr_proba

        # Ensemble prediction (weighted average based on historical performance)
        ensemble_proba = (
            predictions["RandomForest"] * 0.25
            + predictions["GradientBoosting"] * 0.35
            + predictions["LogisticRegression"] * 0.40  # Best performing model
        )
        predictions["Ensemble"] = ensemble_proba

        # Add predictions to DataFrame
        for model_name, proba in predictions.items():
            df[f"{model_name}_win_prob"] = proba * 100

        # Sort by ensemble probability
        df = df.sort_values("Ensemble_win_prob", ascending=False)

        return df

    def generate_real_ai_selections(self):
        """Generate AI selections for today's races"""
        logger.info("🎯 Generating REAL AI Selections from Live Race Cards...")

        # Train models
        training_stats = self.train_ensemble_models()
        logger.info(f"📊 Training completed: {training_stats}")

        # Get live race cards
        race_cards = self.get_live_race_cards()

        if not race_cards:
            logger.error("❌ No race cards found!")
            return []

        all_selections = []

        for race in race_cards:
            logger.info(
                f"🏇 Analyzing Race {race['race_id']} - {race['course']} {race['time']}"
            )
            logger.info(f"   📝 {race['race_name']}")

            # Generate predictions
            predictions_df = self.generate_race_predictions(race)

            # Create race summary
            race_summary = {
                "race_id": race["race_id"],
                "course": race["course"],
                "time": race["time"],
                "race_name": race["race_name"],
                "field_size": race["runners"],
                "selections": [],
            }

            # Top 5 selections
            for i, (_, horse) in enumerate(predictions_df.head(5).iterrows()):
                confidence_level = (
                    "Very High"
                    if horse["Ensemble_win_prob"] > 30
                    else (
                        "High"
                        if horse["Ensemble_win_prob"] > 20
                        else "Medium" if horse["Ensemble_win_prob"] > 12 else "Low"
                    )
                )

                selection = {
                    "position": i + 1,
                    "number": horse["number"],
                    "horse_name": horse["horse_name"],
                    "jockey": horse["jockey"],
                    "trainer": horse["trainer"],
                    "form": horse["form"],
                    "odds": horse["odds_text"],
                    "odds_decimal": f"{horse['odds_decimal']:.1f}",
                    "ai_win_probability": f"{horse['Ensemble_win_prob']:.1f}%",
                    "confidence": confidence_level,
                    "jockey_win_rate": f"{horse['jockey_win_rate']:.1f}%",
                    "trainer_win_rate": f"{horse['trainer_win_rate']:.1f}%",
                    "model_predictions": {
                        "RandomForest": f"{horse['RandomForest_win_prob']:.1f}%",
                        "GradientBoosting": f"{horse['GradientBoosting_win_prob']:.1f}%",
                        "LogisticRegression": f"{horse['LogisticRegression_win_prob']:.1f}%",
                    },
                }
                race_summary["selections"].append(selection)

            all_selections.append(race_summary)

            # Log race analysis
            logger.info(
                f"  🥇 Top Selection: #{race_summary['selections'][0]['number']} {race_summary['selections'][0]['horse_name']} ({race_summary['selections'][0]['ai_win_probability']})"
            )
            if len(race_summary["selections"]) > 1:
                logger.info(
                    f"  🥈 Second Choice: #{race_summary['selections'][1]['number']} {race_summary['selections'][1]['horse_name']} ({race_summary['selections'][1]['ai_win_probability']})"
                )
            if len(race_summary["selections"]) > 2:
                logger.info(
                    f"  🥉 Third Choice: #{race_summary['selections'][2]['number']} {race_summary['selections'][2]['horse_name']} ({race_summary['selections'][2]['ai_win_probability']})"
                )

        return all_selections

    def display_real_selections(self, selections):
        """Display real AI selections in a formatted way"""
        logger.info("🎯 REAL AI RACING SELECTIONS")
        logger.info("=" * 70)
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        logger.info(f"🤖 AI Model: Trained Ensemble (RF + GB + LR)")
        logger.info(f"📊 Data Source: Live Race Cards + Historical Results")
        logger.info("=" * 70)

        for race in selections:
            logger.info(
                f"\n🏇 RACE {race['race_id']} - {race['course']} {race['time']}"
            )
            logger.info(f"   📝 {race['race_name']}")
            logger.info(f"   👥 Field Size: {race['field_size']} runners")
            logger.info("-" * 60)

            for selection in race["selections"]:
                confidence_emoji = (
                    "🔥🔥"
                    if selection["confidence"] == "Very High"
                    else (
                        "🔥"
                        if selection["confidence"] == "High"
                        else "⚡" if selection["confidence"] == "Medium" else "💡"
                    )
                )

                logger.info(
                    f"   {selection['position']}. {confidence_emoji} #{selection['number']} {selection['horse_name']}"
                )
                logger.info(
                    f"      Jockey: {selection['jockey']} ({selection['jockey_win_rate']} SR)"
                )
                logger.info(
                    f"      Trainer: {selection['trainer']} ({selection['trainer_win_rate']} SR)"
                )
                logger.info(f"      Form: {selection['form']}")
                logger.info(f"      Odds: {selection['odds']}")
                logger.info(
                    f"      🤖 AI Win Probability: {selection['ai_win_probability']}"
                )
                logger.info(f"      📊 Confidence: {selection['confidence']}")
                logger.info("")

        logger.info("🎯 REAL AI SELECTIONS COMPLETE!")
        logger.info("📈 Good luck with your selections!")


def main():
    """Main real AI selections generator"""
    ai_selector = RealAISelectionsGenerator()

    try:
        # Generate real AI selections
        selections = ai_selector.generate_real_ai_selections()

        if selections:
            # Display results
            ai_selector.display_real_selections(selections)
            logger.info("✅ Real AI Selections generated successfully!")
        else:
            logger.warning("⚠️ No selections generated - check race card data")

    except Exception as e:
        logger.error(f"❌ Real AI Selections failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
