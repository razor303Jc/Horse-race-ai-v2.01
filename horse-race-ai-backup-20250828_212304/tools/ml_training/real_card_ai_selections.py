#!/usr/bin/env python3
"""
Real AI Selections Generator for Horse Racing
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
import warnings

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

    def connect_cards_database(self):
        """Connect to cards database for race card data"""
        return psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )

    def train_ensemble_models(self):
        """Train the ensemble models on historical results data"""
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
            f"📊 Loaded {len(df)} historical records from {df['race_id'].nunique()} races"
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
        features_df["field_competitive"] = (
            features_df["field_size"] * features_df["market_position"]
        )

        # Define features
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

        # Train models
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

    def get_upcoming_races(self, days_ahead=1):
        """Get upcoming races from cards database"""
        logger.info(f"🏇 Loading upcoming races for next {days_ahead} days...")

        conn = self.connect_cards_database()

        # Get target date (today + days_ahead)
        target_date = date.today() + timedelta(days=days_ahead)

        # First try today's races if no future races
        query = """
        SELECT r.race_id, r.course, r.race_time, r.date, r.race_name, r.distance, r.runners
        FROM races r
        WHERE r.date >= CURRENT_DATE
        ORDER BY r.date, r.race_time
        LIMIT 10
        """

        df = pd.read_sql_query(query, conn)

        if len(df) == 0:
            # If no future races, get recent past races for demo
            logger.info(
                "No upcoming races found, using recent races for demonstration..."
            )
            query = """
            SELECT r.race_id, r.course, r.race_time, r.date, r.race_name, r.distance, r.runners
            FROM races r
            WHERE r.date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY r.date DESC, r.race_time DESC
            LIMIT 5
            """
            df = pd.read_sql_query(query, conn)

        conn.close()

        logger.info(f"📅 Found {len(df)} upcoming races")
        return df.to_dict("records")

    def get_race_horses(self, race_id):
        """Get horses for a specific race"""
        conn = self.connect_cards_database()

        query = """
        SELECT 
            rd.horse_name,
            rd.jockey,
            rd.trainer,
            rd.number,
            COALESCE(CAST(rd.odds AS FLOAT), 5.0) as odds,
            rd.age,
            rd.form,
            rd.weight
        FROM racecard_details rd
        WHERE rd.race_id = %s
        ORDER BY rd.number
        """

        cursor = conn.cursor()
        cursor.execute(query, (race_id,))
        horses = cursor.fetchall()

        conn.close()

        # Convert to list of dictionaries
        horse_list = []
        for horse in horses:
            horse_dict = {
                "horse_name": horse[0],
                "jockey": horse[1] or "Unknown",
                "trainer": horse[2] or "Unknown",
                "number": horse[3] or 1,
                "odds": max(horse[4], 1.5),  # Ensure minimum odds
                "age": horse[5] or 4,
                "form": horse[6] or "",
                "weight": horse[7] or "9-0",
            }
            horse_list.append(horse_dict)

        return horse_list

    def get_jockey_trainer_stats_from_results(self, jockey_name, trainer_name):
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

    def generate_race_predictions(self, race_data, horses):
        """Generate predictions for a race using real card data"""
        if not self.trained:
            raise Exception("Models not trained. Call train_ensemble_models() first.")

        if not horses:
            logger.warning(f"No horses found for race {race_data['race_id']}")
            return pd.DataFrame()

        horses_data = []

        # Sort horses by odds for ranking
        horses_sorted = sorted(horses, key=lambda x: x["odds"])

        for i, horse in enumerate(horses_sorted):
            # Get jockey/trainer stats from results database
            jockey_win_rate, trainer_win_rate = (
                self.get_jockey_trainer_stats_from_results(
                    horse["jockey"], horse["trainer"]
                )
            )

            # Create features
            odds_decimal = float(horse["odds"])
            implied_probability = 1.0 / odds_decimal
            log_odds = np.log(odds_decimal)
            horse_age = horse["age"]
            field_size = len(horses)
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
            field_competitive = field_size * market_position

            horse_features = {
                "horse_name": horse["horse_name"],
                "jockey": horse["jockey"],
                "trainer": horse["trainer"],
                "number": horse["number"],
                "form": horse["form"],
                "weight": horse["weight"],
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

        # Generate predictions
        predictions = {}

        # Model predictions
        rf_proba = self.models["RandomForest"].predict_proba(X)[:, 1]
        predictions["RandomForest"] = rf_proba

        gb_proba = self.models["GradientBoosting"].predict_proba(X)[:, 1]
        predictions["GradientBoosting"] = gb_proba

        lr_proba = self.models["LogisticRegression"].predict_proba(X_scaled)[:, 1]
        predictions["LogisticRegression"] = lr_proba

        # Ensemble prediction
        ensemble_proba = (
            predictions["RandomForest"] * 0.3
            + predictions["GradientBoosting"] * 0.3
            + predictions["LogisticRegression"] * 0.4
        )
        predictions["Ensemble"] = ensemble_proba

        # Add predictions to DataFrame
        for model_name, proba in predictions.items():
            df[f"{model_name}_win_prob"] = proba * 100

        # Sort by ensemble probability
        df = df.sort_values("Ensemble_win_prob", ascending=False)

        return df

    def generate_real_ai_selections(self):
        """Generate AI selections using real card data"""
        logger.info("🎯 Generating Real AI Selections from Card Data...")

        # Train models on historical results
        training_stats = self.train_ensemble_models()
        logger.info(f"📊 Training completed: {training_stats}")

        # Get upcoming races
        upcoming_races = self.get_upcoming_races(days_ahead=0)

        if not upcoming_races:
            logger.warning("No upcoming races found!")
            return []

        all_selections = []

        for race in upcoming_races:
            logger.info(
                f"🏇 Analyzing Race {race['race_id']} - {race['course']} {race['race_time']} ({race['date']})"
            )

            # Get horses for this race
            horses = self.get_race_horses(race["race_id"])

            if not horses:
                logger.warning(f"No horses found for race {race['race_id']}")
                continue

            # Generate predictions
            predictions_df = self.generate_race_predictions(race, horses)

            if predictions_df.empty:
                continue

            # Create race summary
            race_summary = {
                "race_id": race["race_id"],
                "course": race["course"],
                "time": str(race["race_time"]),
                "date": str(race["date"]),
                "race_name": race.get("race_name", "Unknown"),
                "distance": race.get("distance", "Unknown"),
                "field_size": len(horses),
                "selections": [],
            }

            # Top 3 selections
            for i, (_, horse) in enumerate(predictions_df.head(3).iterrows()):
                selection = {
                    "position": i + 1,
                    "horse_name": horse["horse_name"],
                    "number": horse["number"],
                    "jockey": horse["jockey"],
                    "trainer": horse["trainer"],
                    "form": horse["form"],
                    "weight": horse["weight"],
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
            top_selection = race_summary["selections"][0]
            logger.info(
                f"  🥇 Top Selection: {top_selection['horse_name']} (#{top_selection['number']}) - {top_selection['ai_win_probability']}"
            )
            if len(race_summary["selections"]) > 1:
                logger.info(
                    f"  🥈 Second Choice: {race_summary['selections'][1]['horse_name']} (#{race_summary['selections'][1]['number']}) - {race_summary['selections'][1]['ai_win_probability']}"
                )
            if len(race_summary["selections"]) > 2:
                logger.info(
                    f"  🥉 Third Choice: {race_summary['selections'][2]['horse_name']} (#{race_summary['selections'][2]['number']}) - {race_summary['selections'][2]['ai_win_probability']}"
                )

        return all_selections

    def display_real_selections(self, selections):
        """Display real AI selections"""
        logger.info("🎯 REAL AI RACING SELECTIONS")
        logger.info("=" * 70)
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        logger.info(
            f"🤖 AI Model: Ensemble (RF + GB + LR) trained on historical results"
        )
        logger.info(f"📊 Data Source: Real race cards from cards_horse_racing_db")
        logger.info("=" * 70)

        for race in selections:
            logger.info(
                f"\n🏇 RACE {race['race_id']} - {race['course']} {race['time']}"
            )
            logger.info(f"   📅 Date: {race['date']}")
            logger.info(f"   🏁 {race['race_name']} - {race['distance']}")
            logger.info(f"   🐎 Field Size: {race['field_size']} runners")
            logger.info("-" * 60)

            for selection in race["selections"]:
                confidence_emoji = (
                    "🔥"
                    if selection["confidence"] == "High"
                    else "⚡" if selection["confidence"] == "Medium" else "💡"
                )
                logger.info(
                    f"   {selection['position']}. {confidence_emoji} #{selection['number']} {selection['horse_name']}"
                )
                logger.info(f"      👤 Jockey: {selection['jockey']}")
                logger.info(f"      🎓 Trainer: {selection['trainer']}")
                logger.info(f"      📊 Form: {selection['form']}")
                logger.info(f"      ⚖️ Weight: {selection['weight']}")
                logger.info(f"      💰 Odds: {selection['odds']}")
                logger.info(
                    f"      🤖 AI Win Probability: {selection['ai_win_probability']}"
                )
                logger.info(f"      🎯 Confidence: {selection['confidence']}")
                logger.info("")

        logger.info("🎯 REAL AI SELECTIONS COMPLETE!")


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
            logger.warning("⚠️ No selections generated - no upcoming races found")

    except Exception as e:
        logger.error(f"❌ Real AI Selections failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
