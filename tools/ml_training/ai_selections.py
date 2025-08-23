#!/usr/bin/env python3
"""
AI Selections Generator for Horse Racing
Uses trained ML models to generate race predictions and selections
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

warnings.filterwarnings("ignore")

sys.path.append("/app")
from tools.ml_training.standalone_course_mapper import StandaloneCourseMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AISelectionsGenerator:
    def __init__(self):
        self.course_mapper = StandaloneCourseMapper()
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.trained = False

    def connect_database(self):
        """Establish database connection"""
        return psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def train_ensemble_models(self):
        """Train the ensemble models on all available data"""
        logger.info("🤖 Training ensemble models for AI selections...")

        conn = self.connect_database()

        # Load all training data
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

        logger.info(f"📊 Loaded {len(df)} records from {df['race_id'].nunique()} races")

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
        features_df["field_competitive"] = (
            features_df["field_size"] * features_df["market_position"]
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
            "field_competitive",
        ]

        X = features_df[self.feature_columns].fillna(0)
        y = features_df["is_winner"]

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train ensemble models
        logger.info("  Training RandomForest...")
        self.models["RandomForest"] = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=1
        )
        self.models["RandomForest"].fit(X, y)

        logger.info("  Training GradientBoosting...")
        self.models["GradientBoosting"] = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
        )
        self.models["GradientBoosting"].fit(X, y)

        logger.info("  Training LogisticRegression...")
        self.models["LogisticRegression"] = LogisticRegression(
            C=1.5, random_state=42, max_iter=1000
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

    def generate_mock_race_data(self):
        """Generate mock upcoming race data for AI selections"""
        logger.info("🏇 Generating mock upcoming race data...")

        # Create realistic mock race data
        mock_races = []

        # Race 1: 2:30 PM - Newmarket
        race1_horses = [
            {
                "horse_name": "Thunder Strike",
                "jockey": "W A Carson",
                "trainer": "B Ellison",
                "age": 4,
                "odds": 3.5,
            },
            {
                "horse_name": "Lightning Flash",
                "jockey": "T E Whelan",
                "trainer": "Tom Dascombe",
                "age": 3,
                "odds": 4.2,
            },
            {
                "horse_name": "Storm Chaser",
                "jockey": "S Foley",
                "trainer": "Miss Gay Kelleway",
                "age": 5,
                "odds": 6.0,
            },
            {
                "horse_name": "Wind Runner",
                "jockey": "Joey Haynes",
                "trainer": "C Hills",
                "age": 4,
                "odds": 7.5,
            },
            {
                "horse_name": "Rain Dancer",
                "jockey": "K Shoemark",
                "trainer": "S Dixon",
                "age": 3,
                "odds": 9.0,
            },
            {
                "horse_name": "Cloud Walker",
                "jockey": "Saffie Osborne",
                "trainer": "Mrs J Harrington",
                "age": 6,
                "odds": 12.0,
            },
        ]

        # Race 2: 3:15 PM - York
        race2_horses = [
            {
                "horse_name": "Golden Arrow",
                "jockey": "W A Carson",
                "trainer": "Tom Dascombe",
                "age": 4,
                "odds": 2.8,
            },
            {
                "horse_name": "Silver Bullet",
                "jockey": "T E Whelan",
                "trainer": "B Ellison",
                "age": 5,
                "odds": 3.2,
            },
            {
                "horse_name": "Bronze Medal",
                "jockey": "S Foley",
                "trainer": "C Hills",
                "age": 3,
                "odds": 5.5,
            },
            {
                "horse_name": "Copper Coin",
                "jockey": "Joey Haynes",
                "trainer": "Miss Gay Kelleway",
                "age": 4,
                "odds": 8.0,
            },
            {
                "horse_name": "Iron Will",
                "jockey": "K Shoemark",
                "trainer": "S Dixon",
                "age": 6,
                "odds": 11.0,
            },
            {
                "horse_name": "Steel Magnolia",
                "jockey": "Callum Hutchinson",
                "trainer": "Mrs J Harrington",
                "age": 4,
                "odds": 15.0,
            },
            {
                "horse_name": "Platinum Star",
                "jockey": "Saffie Osborne",
                "trainer": "Miss J Feilden",
                "age": 5,
                "odds": 20.0,
            },
        ]

        races = [
            {
                "race_id": 999001,
                "course": "Newmarket",
                "time": "14:30",
                "horses": race1_horses,
            },
            {
                "race_id": 999002,
                "course": "York",
                "time": "15:15",
                "horses": race2_horses,
            },
        ]

        return races

    def get_jockey_trainer_stats(self, jockey_name, trainer_name):
        """Get jockey and trainer statistics from database"""
        conn = self.connect_database()
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

    def generate_race_predictions(self, race_data):
        """Generate predictions for a single race"""
        if not self.trained:
            raise Exception("Models not trained. Call train_ensemble_models() first.")

        horses_data = []

        for i, horse in enumerate(race_data["horses"]):
            # Get jockey/trainer stats
            jockey_win_rate, trainer_win_rate = self.get_jockey_trainer_stats(
                horse["jockey"], horse["trainer"]
            )

            # Create features
            odds_decimal = float(horse["odds"])
            implied_probability = 1.0 / odds_decimal
            log_odds = np.log(odds_decimal)
            horse_age = horse["age"]
            field_size = len(race_data["horses"])
            odds_rank = i + 1  # Assuming horses are ordered by odds
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
            field_competitive = field_size * market_position

            horse_features = {
                "horse_name": horse["horse_name"],
                "jockey": horse["jockey"],
                "trainer": horse["trainer"],
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
                "field_competitive": field_competitive,
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

        # Ensemble prediction (weighted average)
        ensemble_proba = (
            predictions["RandomForest"] * 0.3
            + predictions["GradientBoosting"] * 0.3
            + predictions["LogisticRegression"]
            * 0.4  # Best performing model gets higher weight
        )
        predictions["Ensemble"] = ensemble_proba

        # Add predictions to DataFrame
        for model_name, proba in predictions.items():
            df[f"{model_name}_win_prob"] = proba * 100  # Convert to percentage

        # Sort by ensemble probability
        df = df.sort_values("Ensemble_win_prob", ascending=False)

        return df

    def generate_ai_selections(self):
        """Generate AI selections for upcoming races"""
        logger.info("🎯 Generating AI Selections...")

        # Train models
        training_stats = self.train_ensemble_models()
        logger.info(f"📊 Training completed: {training_stats}")

        # Get upcoming races (mock data)
        upcoming_races = self.generate_mock_race_data()

        all_selections = []

        for race in upcoming_races:
            logger.info(
                f"🏇 Analyzing Race {race['race_id']} - {race['course']} {race['time']}"
            )

            # Generate predictions
            predictions_df = self.generate_race_predictions(race)

            # Create race summary
            race_summary = {
                "race_id": race["race_id"],
                "course": race["course"],
                "time": race["time"],
                "field_size": len(race["horses"]),
                "selections": [],
            }

            # Top 3 selections
            for i, (_, horse) in enumerate(predictions_df.head(3).iterrows()):
                selection = {
                    "position": i + 1,
                    "horse_name": horse["horse_name"],
                    "jockey": horse["jockey"],
                    "trainer": horse["trainer"],
                    "odds": f"{horse['odds_decimal']:.1f}",
                    "ai_win_probability": f"{horse['Ensemble_win_prob']:.1f}%",
                    "confidence": (
                        "High"
                        if horse["Ensemble_win_prob"] > 25
                        else "Medium" if horse["Ensemble_win_prob"] > 15 else "Low"
                    ),
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
                f"  🥇 Top Selection: {race_summary['selections'][0]['horse_name']} ({race_summary['selections'][0]['ai_win_probability']})"
            )
            logger.info(
                f"  🥈 Second Choice: {race_summary['selections'][1]['horse_name']} ({race_summary['selections'][1]['ai_win_probability']})"
            )
            logger.info(
                f"  🥉 Third Choice: {race_summary['selections'][2]['horse_name']} ({race_summary['selections'][2]['ai_win_probability']})"
            )

        return all_selections

    def display_selections(self, selections):
        """Display AI selections in a formatted way"""
        logger.info("🎯 AI RACING SELECTIONS")
        logger.info("=" * 60)
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"🤖 AI Model: Ensemble (RF + GB + LR)")
        logger.info("=" * 60)

        for race in selections:
            logger.info(
                f"\n🏇 RACE {race['race_id']} - {race['course']} {race['time']}"
            )
            logger.info(f"   Field Size: {race['field_size']} runners")
            logger.info("-" * 50)

            for selection in race["selections"]:
                confidence_emoji = (
                    "🔥"
                    if selection["confidence"] == "High"
                    else "⚡" if selection["confidence"] == "Medium" else "💡"
                )
                logger.info(
                    f"   {selection['position']}. {confidence_emoji} {selection['horse_name']}"
                )
                logger.info(f"      Jockey: {selection['jockey']}")
                logger.info(f"      Trainer: {selection['trainer']}")
                logger.info(f"      Odds: {selection['odds']}")
                logger.info(
                    f"      AI Win Probability: {selection['ai_win_probability']}"
                )
                logger.info(f"      Confidence: {selection['confidence']}")
                logger.info("")

        logger.info("🎯 AI SELECTIONS COMPLETE!")


def main():
    """Main AI selections generator"""
    ai_selector = AISelectionsGenerator()

    try:
        # Generate AI selections
        selections = ai_selector.generate_ai_selections()

        # Display results
        ai_selector.display_selections(selections)

        logger.info("✅ AI Selections generated successfully!")

    except Exception as e:
        logger.error(f"❌ AI Selections failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
