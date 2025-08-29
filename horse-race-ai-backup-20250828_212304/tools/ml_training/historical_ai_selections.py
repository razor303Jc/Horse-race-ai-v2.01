#!/usr/bin/env python3
"""
Historical AI Selections Generator for Horse Racing
Generate AI selections for specific historical dates using real card data
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

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HistoricalAISelectionsGenerator:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.trained = False

        # Database config - use host IP for external connection
        self.db_config = {
            "host": "172.18.0.3",
            "port": 5432,
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def connect_results_database(self):
        """Connect to results database for training"""
        return psycopg2.connect(**self.db_config, database="results_horse_racing_db")

    def connect_cards_database(self):
        """Connect to cards database for race card data"""
        return psycopg2.connect(**self.db_config, database="cards_horse_racing_db")

    def train_ensemble_models(self):
        """Train ML models on historical results data"""
        logger.info("🎯 Training ensemble models on historical results...")

        conn = self.connect_results_database()

        # Query historical race results for training
        query = """
        SELECT 
            r.race_id,
            r.date,
            r.course,
            rec.horse_id,
            rec.place,
            rec.sp as odds_decimal,
            rec.age as horse_age,
            COALESCE(rec.weight::float, 60.0) as horse_weight_kg,
            r.runners as field_size
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE rec.sp > 0 AND rec.place > 0
        ORDER BY r.date DESC
        LIMIT 5000
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if len(df) == 0:
            logger.error("No training data found!")
            return {}

        logger.info(
            f"📊 Loaded {len(df)} historical records from {df['race_id'].nunique()} races"
        )

        # Feature engineering
        features_df = df.copy()
        features_df["is_winner"] = (features_df["place"] == 1).astype(int)

        # Basic features
        features_df["implied_probability"] = 1.0 / features_df["odds_decimal"]
        features_df["log_odds"] = np.log(features_df["odds_decimal"])

        # Add odds rank within each race
        features_df["odds_rank"] = features_df.groupby("race_id")["odds_decimal"].rank()
        features_df["is_favorite"] = (features_df["odds_rank"] == 1).astype(int)

        # Performance features (simplified without jockey/trainer data)
        features_df["market_position"] = 1.0 / features_df["odds_rank"]
        features_df["field_dominance"] = (
            features_df["field_size"] / features_df["odds_rank"]
        )
        features_df["odds_value"] = features_df["implied_probability"] - (
            1.0 / features_df["field_size"]
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
            "market_position",
            "field_dominance",
            "odds_value",
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

    def get_races_for_date(self, target_date):
        """Get races for a specific date from cards database"""
        logger.info(f"🏇 Loading races for {target_date}...")

        conn = self.connect_cards_database()

        query = """
        SELECT r.race_id, r.course, r.race_time, r.date, r.race_name, r.distance, r.runners
        FROM races r
        WHERE r.date = %s
        ORDER BY r.race_time
        """

        df = pd.read_sql_query(query, conn, params=[target_date])
        conn.close()

        logger.info(f"📅 Found {len(df)} races for {target_date}")
        return df.to_dict("records")

    def get_race_horses(self, race_id):
        """Get horses for a specific race"""
        conn = self.connect_cards_database()

        query = """
        SELECT 
            rd.name as horse_name,
            rd.jockey,
            rd.trainer,
            rd.horse_number as number,
            COALESCE(rd.odds_decimal, 5.0) as odds,
            rd.age,
            rd.weight
        FROM racecard_details rd
        WHERE rd.race_id = %s
        ORDER BY rd.horse_number
        """

        df = pd.read_sql_query(query, conn, params=[race_id])
        conn.close()

        # Convert to list of dictionaries
        horse_list = []
        for _, horse in df.iterrows():
            horse_dict = {
                "horse_name": horse["horse_name"] or "Unknown",
                "jockey": horse["jockey"] or "Unknown",
                "trainer": horse["trainer"] or "Unknown",
                "number": horse["number"] or 1,
                "odds": max(float(horse["odds"]), 1.5),  # Ensure minimum odds
                "age": horse["age"] or 4,
                "weight": horse["weight"] or 60.0,
            }
            horse_list.append(horse_dict)

        return horse_list

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
            # Create features
            odds_decimal = float(horse["odds"])
            implied_probability = 1.0 / odds_decimal
            log_odds = np.log(odds_decimal)
            horse_age = horse["age"]
            horse_weight_kg = float(horse["weight"])
            field_size = len(horses)
            odds_rank = i + 1
            is_favorite = 1 if i == 0 else 0

            # Market features
            market_position = 1.0 / odds_rank
            field_dominance = field_size / odds_rank
            odds_value = implied_probability - (1.0 / field_size)

            horse_features = {
                "horse_name": horse["horse_name"],
                "jockey": horse["jockey"],
                "trainer": horse["trainer"],
                "number": horse["number"],
                "weight": horse["weight"],
                "odds_decimal": odds_decimal,
                "implied_probability": implied_probability,
                "log_odds": log_odds,
                "horse_weight_kg": horse_weight_kg,
                "horse_age": horse_age,
                "field_size": field_size,
                "odds_rank": odds_rank,
                "is_favorite": is_favorite,
                "market_position": market_position,
                "field_dominance": field_dominance,
                "odds_value": odds_value,
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

    def save_ai_selections_to_db(self, race_data, predictions_df):
        """Save AI selections to the cards database"""
        if predictions_df.empty:
            return

        conn = self.connect_cards_database()
        cursor = conn.cursor()

        try:
            # Save to ai_selections table - using the actual table structure
            for i, (_, horse) in enumerate(predictions_df.head(3).iterrows()):
                # Look up detail_id by matching race_id and horse_name
                cursor.execute(
                    "SELECT COALESCE(MIN(id), 1) FROM racecard_details WHERE race_id = %s AND name = %s",
                    (race_data["race_id"], horse["horse_name"]),
                )
                detail_id_result = cursor.fetchone()
                detail_id = detail_id_result[0] if detail_id_result else 1

                insert_query = """
                INSERT INTO ai_selections (
                    race_id, detail_id, horse_name, win_probability, confidence_score,
                    model_name, model_version, ai_selection_type, race_date,
                    course, race_number, features_used, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """

                confidence_score = horse["Ensemble_win_prob"] / 100.0

                cursor.execute(
                    insert_query,
                    (
                        race_data["race_id"],
                        detail_id,
                        horse["horse_name"],
                        confidence_score,
                        confidence_score,
                        "Ensemble_ML",
                        "v2.0_ensemble",
                        "AI_WIN_SELECTION",
                        race_data["date"],
                        race_data["course"],
                        i + 1,  # Selection rank as race number
                        "odds,probability,log_odds,weight,age,field_size,rank,favorite,market_pos,dominance,value",
                        datetime.now(),
                    ),
                )

            conn.commit()
            logger.info(f"  💾 Saved AI selections for race {race_data['race_id']}")

        except Exception as e:
            logger.error(f"Error saving AI selections: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def generate_ai_selections_for_date(self, target_date):
        """Generate AI selections for a specific date"""
        logger.info(f"🎯 Generating AI Selections for {target_date}...")

        # Train models on historical results
        if not self.trained:
            training_stats = self.train_ensemble_models()
            logger.info(f"📊 Training completed: {training_stats}")

        # Get races for the target date
        races = self.get_races_for_date(target_date)

        if not races:
            logger.warning(f"No races found for {target_date}!")
            return []

        all_selections = []

        for race in races:
            logger.info(
                f"🏇 Analyzing Race {race['race_id']} - {race['course']} {race['race_time']}"
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

            # Save to database
            self.save_ai_selections_to_db(race, predictions_df)

            # Create race summary
            race_summary = {
                "race_id": race["race_id"],
                "course": race["course"],
                "time": str(race["race_time"]),
                "date": str(race["date"]),
                "race_name": race.get("race_name", "Unknown"),
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
                    "odds": f"{horse['odds_decimal']:.1f}",
                    "ai_win_probability": f"{horse['Ensemble_win_prob']:.1f}%",
                    "confidence": (
                        "High"
                        if horse["Ensemble_win_prob"] > 25
                        else "Medium" if horse["Ensemble_win_prob"] > 15 else "Low"
                    ),
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

        return all_selections


def main():
    """Main function to generate AI selections for specific dates"""
    ai_selector = HistoricalAISelectionsGenerator()

    # Target dates to process
    target_dates = ["2025-08-22", "2025-08-24"]

    try:
        for date_str in target_dates:
            logger.info(f"\n🗓️  Processing {date_str}")
            logger.info("=" * 50)

            selections = ai_selector.generate_ai_selections_for_date(date_str)

            if selections:
                logger.info(
                    f"✅ Generated {len(selections)} race selections for {date_str}"
                )
            else:
                logger.warning(f"⚠️  No selections generated for {date_str}")

        logger.info("\n🎉 Historical AI Selections generation completed!")

    except Exception as e:
        logger.error(f"❌ AI Selections generation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
