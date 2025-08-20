#!/usr/bin/env python3
"""
🎯 Enhanced AI Selections Generator with Advanced Metrics
========================================================

Integrates the new advanced metrics ML models into the AI selections system.

Features:
- Advanced metrics integration (power ratings, speed figures, pace analysis)
- Multiple prediction models (win, position, place probabilities)
- Enhanced feature engineering with advanced metrics
- Backward compatibility with existing system

Author: AI Assistant
Date: August 20, 2025
"""

import json
import logging
import sys
import traceback
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import joblib
import numpy as np
import pandas as pd
import psycopg2

warnings.filterwarnings("ignore")


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class EnhancedAISelectionsGenerator:
    """Enhanced AI selections generator with advanced metrics integration."""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.models_dir = self.project_root / "models"

        # Database connection
        self.db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Model containers
        self.legacy_models = {}
        self.advanced_models = {}
        self.scalers = {}
        self.feature_columns = []

        # Load all models
        self.load_models()

    def load_models(self) -> None:
        """Load both legacy and advanced metrics models."""
        logger.info("🤖 Loading AI models...")

        try:
            # Load legacy models for backward compatibility
            self.load_legacy_models()

            # Load new advanced metrics models
            self.load_advanced_metrics_models()

            logger.info(
                f"✅ Loaded {len(self.legacy_models)} legacy + "
                f"{len(self.advanced_models)} advanced models"
            )

        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            raise

    def load_legacy_models(self) -> None:
        """Load original production models for fallback."""
        legacy_dir = self.project_root / "trained_models" / "production"

        model_files = {
            "random_forest": "random_forest_production.joblib",
            "gradient_boosting": "gradient_boosting_production.joblib",
            "logistic_regression": "logistic_regression_production.joblib",
            "neural_network": "neural_network_production.joblib",
        }

        for name, filename in model_files.items():
            model_path = legacy_dir / filename
            if model_path.exists():
                self.legacy_models[name] = joblib.load(model_path)
                logger.info(f"   ✅ Legacy {name} loaded")

        # Load legacy scaler if available
        scaler_path = legacy_dir / "scaler_production.joblib"
        if scaler_path.exists():
            self.scalers["legacy"] = joblib.load(scaler_path)

    def load_advanced_metrics_models(self) -> None:
        """Load the new advanced metrics models."""
        # Find the latest advanced metrics model package
        model_files = list(self.models_dir.glob("advanced_metrics_models_*.joblib"))

        if not model_files:
            logger.warning("⚠️ No advanced metrics models found - using legacy only")
            return

        # Sort by filename to get the latest
        latest_model = sorted(model_files, key=lambda x: x.name)[-1]
        logger.info(f"📦 Loading advanced metrics from {latest_model.name}")

        try:
            # Load the complete model package
            model_data = joblib.load(latest_model)

            self.advanced_models = model_data["models"]
            self.scalers.update(model_data.get("scalers", {}))
            self.feature_columns = model_data["feature_columns"]

            logger.info(f"   ✅ Advanced metrics: {len(self.advanced_models)} models")
            logger.info(f"   ✅ Features: {len(self.feature_columns)} columns")
            logger.info(f"   ✅ Model types: {list(self.advanced_models.keys())}")

        except Exception as e:
            logger.error(f"❌ Failed to load advanced metrics models: {e}")
            self.advanced_models = {}
            self.feature_columns = []

    def parse_distance_to_furlongs(self, distance_str):
        """Convert UK racing distance format to furlongs."""
        try:
            if pd.isna(distance_str) or distance_str == "":
                return 8.0  # Default 1 mile

            distance_str = str(distance_str).strip().lower()

            # Initialize totals
            total_furlongs = 0.0

            # Parse miles (1m = 8 furlongs)
            if "m" in distance_str:
                parts = distance_str.split("m")
                if len(parts) > 1:
                    # Extract miles part
                    miles_part = parts[0].strip()
                    if miles_part.isdigit():
                        total_furlongs += float(miles_part) * 8
                    # Continue with remainder
                    distance_str = parts[1].strip()

            # Parse furlongs (f)
            if "f" in distance_str:
                parts = distance_str.split("f")
                furlongs_part = parts[0].strip()
                if furlongs_part.isdigit():
                    total_furlongs += float(furlongs_part)
                # Continue with remainder for yards
                if len(parts) > 1:
                    distance_str = parts[1].strip()

            # Parse yards (y) - 220 yards = 1 furlong
            if "y" in distance_str:
                yards_part = distance_str.replace("y", "").strip()
                if yards_part.isdigit():
                    total_furlongs += float(yards_part) / 220.0

            return total_furlongs if total_furlongs > 0 else 8.0

        except Exception:
            return 8.0  # Default fallback

    def get_db_connection(self):
        """Get database connection."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def load_race_data(self) -> pd.DataFrame:
        """Load today's race data with enhanced metrics."""
        logger.info("📊 Loading race data with advanced metrics...")

        connection = self.get_db_connection()

        # Enhanced query that includes advanced metrics if available
        query = """
            SELECT DISTINCT
                rc.race_id,
                rc.course,
                rc.race_number,
                rc.race_time,
                rc.race_date,
                rc.race_name,
                rc.distance,
                rc.prize,
                re.horse_name,
                re.jockey,
                re.trainer,
                re.age as horse_age,
                re.weight_kg as horse_weight_kg,
                re.draw,
                re.odds as win_odds,
                re.odds_decimal / 3.0 as place_odds,

                -- Advanced metrics (if available)
                pr.power_rating,
                sr.speed_figure,
                sr.pace_rating,
                fs.form_score,
                mc.win_probability as mc_win_probability,
                mc.place_probability as mc_place_probability,

                -- Jockey stats
                COALESCE(js_agg.avg_win_pct, 0) as jockey_win_pct,

                -- Trainer stats
                COALESCE(ts_agg.avg_win_pct, 0) as trainer_win_pct

            FROM race_entries re
            JOIN race_cards rc ON re.race_id = rc.race_id

            -- Advanced metrics joins
            LEFT JOIN horse_power_ratings pr ON re.horse_name = pr.horse_name
                AND rc.race_date = pr.race_date
            LEFT JOIN horse_speed_ratings sr ON re.horse_name = sr.horse_name
                AND rc.race_date = sr.race_date
            LEFT JOIN horse_form_scores fs ON re.horse_name = fs.horse_name
                AND rc.race_date = fs.race_date
            LEFT JOIN monte_carlo_simulations mc ON re.horse_name = mc.horse_name
                AND rc.race_date = mc.race_date

            -- Stats joins
            LEFT JOIN (
                SELECT
                    jockey_name,
                    AVG(percentage_wins) as avg_win_pct
                FROM jockeys_stats
                GROUP BY jockey_name
            ) js_agg ON re.jockey = js_agg.jockey_name
            LEFT JOIN (
                SELECT
                    trainer_name,
                    AVG(percentage_wins) as avg_win_pct
                FROM trainers_stats
                GROUP BY trainer_name
            ) ts_agg ON re.trainer = ts_agg.trainer_name

            WHERE rc.race_date = CURRENT_DATE
            AND re.jockey IS NOT NULL
            AND re.trainer IS NOT NULL
            ORDER BY rc.course, rc.race_number, re.horse_name
        """

        df = pd.read_sql_query(query, connection)
        connection.close()

        logger.info(
            f"✅ Loaded {len(df)} runners from {df['course'].nunique()} courses"
        )

        # Check for advanced metrics availability
        advanced_cols = ["power_rating", "speed_figure", "pace_rating", "form_score"]
        has_advanced = df[advanced_cols].notna().any().any()

        if has_advanced:
            logger.info("🎯 Advanced metrics data found!")
        else:
            logger.warning("⚠️ No advanced metrics data - will use legacy features only")

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for both legacy and advanced predictions."""
        logger.info("⚙️ Engineering features...")

        # Basic feature engineering (legacy)
        df = self.engineer_legacy_features(df)

        # Advanced metrics feature engineering
        df = self.engineer_advanced_features(df)

        logger.info(f"✅ Features engineered: {len(df.columns)} total columns")
        return df

    def engineer_legacy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer legacy features for backward compatibility."""
        # Convert odds to numeric, handling any non-numeric values
        df["win_odds"] = pd.to_numeric(df["win_odds"], errors="coerce").fillna(10.0)
        df["place_odds"] = pd.to_numeric(df["place_odds"], errors="coerce").fillna(4.0)

        # Basic odds processing
        df["log_odds"] = np.log(df["win_odds"])
        df["implied_probability"] = 1.0 / df["win_odds"]

        # Race-level features
        race_groups = df.groupby(["course", "race_number"])
        df["field_size"] = race_groups["horse_name"].transform("count")
        df["odds_rank"] = race_groups["win_odds"].rank()
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)

        # Stats features
        df["jockey_win_pct"] = df["jockey_win_pct"].fillna(0)
        df["trainer_win_pct"] = df["trainer_win_pct"].fillna(0)
        df["combined_performance"] = (df["jockey_win_pct"] + df["trainer_win_pct"]) / 2

        # Percentile features
        df["draw_percentile"] = df.groupby(["course", "race_number"])["draw"].rank(
            pct=True
        )
        df["weight_percentile"] = df.groupby(["course", "race_number"])[
            "horse_weight_kg"
        ].rank(pct=True)

        # Age categories
        df["age_category"] = pd.cut(
            df["horse_age"], bins=[0, 3, 5, 8, 15], labels=[0, 1, 2, 3]
        )
        df["age_category"] = df["age_category"].astype(int)

        # Odds statistics per race
        df["min_odds"] = race_groups["win_odds"].transform("min")
        df["max_odds"] = race_groups["win_odds"].transform("max")
        df["avg_odds"] = race_groups["win_odds"].transform("mean")

        return df

    def engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer advanced metrics features."""
        # Fill missing advanced metrics with defaults
        df["power_rating"] = df["power_rating"].fillna(70.0)  # Default rating
        df["speed_figure"] = df["speed_figure"].fillna(80.0)  # Default speed
        df["pace_rating"] = df["pace_rating"].fillna(
            df["speed_figure"]
        )  # Use speed as default
        df["form_score"] = df["form_score"].fillna(75.0)  # Default form

        # Handle Monte Carlo probabilities
        if "mc_win_probability" in df.columns:
            df["win_probability"] = df["mc_win_probability"].fillna(0.1)
        else:
            df["win_probability"] = 0.1  # Default probability

        # Advanced derived features (matching training data)
        df["rating_speed_ratio"] = df["power_rating"] / (df["speed_figure"] + 1)
        df["power_form_ratio"] = df["power_rating"] / (df["form_score"] + 1)

        # Field strength calculation per race
        race_groups = df.groupby(["course", "race_number"])
        df["field_strength"] = (
            race_groups["power_rating"].transform("mean") * df["field_size"]
        )
        df["win_prob_adjusted"] = df["win_probability"] * df["field_size"]

        # Class adjustment (calculated from power rating relative to field)
        df["class_adjustment"] = df["power_rating"] - race_groups[
            "power_rating"
        ].transform("mean")

        # Distance in furlongs (converted from UK racing format)
        if "distance" in df.columns:
            df["distance_furlongs"] = df["distance"].apply(
                self.parse_distance_to_furlongs
            )
        else:
            df["distance_furlongs"] = 8.0  # Default 1 mile

        return df

    def generate_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate predictions using both legacy and advanced models."""
        logger.info("🎯 Generating AI predictions...")

        predictions_df = df.copy()

        # Generate legacy predictions for comparison
        legacy_predictions = self.generate_legacy_predictions(df)

        # Generate advanced metrics predictions
        advanced_predictions = self.generate_advanced_predictions(df)

        # Combine predictions
        for key, values in legacy_predictions.items():
            predictions_df[f"legacy_{key}"] = values

        for key, values in advanced_predictions.items():
            predictions_df[f"advanced_{key}"] = values

        # Create enhanced ensemble that combines both approaches
        self.create_enhanced_ensemble(predictions_df)

        return predictions_df

    def generate_legacy_predictions(self, df: pd.DataFrame) -> Dict:
        """Generate predictions using legacy models."""
        if not self.legacy_models:
            return {}

        logger.info("📊 Generating legacy predictions...")

        # Legacy feature columns
        legacy_features = [
            "log_odds",
            "implied_probability",
            "odds_rank",
            "is_favorite",
            "combined_performance",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "draw_percentile",
            "weight_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "jockey_win_pct",
            "trainer_win_pct",
        ]

        # Ensure all features exist
        for feature in legacy_features:
            if feature not in df.columns:
                df[feature] = 0.0

        X = df[legacy_features].values

        # Scale if scaler available
        if "legacy" in self.scalers:
            X = self.scalers["legacy"].transform(X)

        predictions = {}
        for name, model in self.legacy_models.items():
            try:
                pred_proba = model.predict_proba(X)[:, 1]
                predictions[f"{name}_probability"] = pred_proba
                logger.info(f"   ✅ Legacy {name}: {len(pred_proba)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️ Legacy {name} failed: {e}")

        # Legacy ensemble
        if predictions:
            ensemble_probs = np.mean(list(predictions.values()), axis=0)
            predictions["ensemble_probability"] = ensemble_probs

        return predictions

    def generate_advanced_predictions(self, df: pd.DataFrame) -> Dict:
        """Generate predictions using advanced metrics models."""
        if not self.advanced_models or not self.feature_columns:
            logger.warning("⚠️ No advanced models available")
            return {}

        logger.info("🎯 Generating advanced metrics predictions...")

        # Ensure all advanced features exist
        for feature in self.feature_columns:
            if feature not in df.columns:
                logger.warning(f"⚠️ Missing feature: {feature}")
                df[feature] = 0.0

        X = df[self.feature_columns].values

        predictions = {}

        # Win probability predictions
        if "win_ensemble" in self.advanced_models:
            try:
                model = self.advanced_models["win_ensemble"]
                win_probs = model.predict_proba(X)[:, 1]
                predictions["win_probability"] = win_probs
                logger.info(f"   ✅ Advanced win: {len(win_probs)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️ Advanced win model failed: {e}")

        # Finishing position predictions
        if "position_ensemble" in self.advanced_models:
            try:
                model = self.advanced_models["position_ensemble"]
                positions = model.predict(X)
                predictions["predicted_position"] = positions
                logger.info(f"   ✅ Advanced position: {len(positions)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️ Advanced position model failed: {e}")

        # Place probability predictions
        if "place_ensemble" in self.advanced_models:
            try:
                model = self.advanced_models["place_ensemble"]
                place_probs = model.predict_proba(X)[:, 1]
                predictions["place_probability"] = place_probs
                logger.info(f"   ✅ Advanced place: {len(place_probs)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️ Advanced place model failed: {e}")

        return predictions

    def create_enhanced_ensemble(self, df: pd.DataFrame) -> None:
        """Create enhanced ensemble combining legacy and advanced predictions."""
        logger.info("🎯 Creating enhanced ensemble predictions...")

        # Weights for combining predictions (favor advanced if available)
        advanced_weight = 0.7
        legacy_weight = 0.3

        # Win probability ensemble
        win_cols = []
        if "advanced_win_probability" in df.columns:
            win_cols.append(("advanced_win_probability", advanced_weight))
        if "legacy_ensemble_probability" in df.columns:
            win_cols.append(("legacy_ensemble_probability", legacy_weight))

        # If no model predictions, use Monte Carlo or implied probability as fallback
        if not win_cols:
            if "mc_win_probability" in df.columns:
                df["enhanced_win_probability"] = df["mc_win_probability"]
            elif "win_probability" in df.columns:
                df["enhanced_win_probability"] = df["win_probability"]
            else:
                # Use implied probability from odds as ultimate fallback
                df["enhanced_win_probability"] = df.get("implied_probability", 0.1)
        else:
            weighted_win = sum(df[col] * weight for col, weight in win_cols)
            total_weight = sum(weight for _, weight in win_cols)
            df["enhanced_win_probability"] = weighted_win / total_weight

        # Place probability ensemble
        place_cols = []
        if "advanced_place_probability" in df.columns:
            place_cols.append(("advanced_place_probability", advanced_weight))
        if "legacy_ensemble_probability" in df.columns:
            # Use legacy win prob * 2.5 as place estimate
            place_cols.append(("legacy_ensemble_probability", legacy_weight * 2.5))

        if not place_cols:
            if "mc_place_probability" in df.columns:
                df["enhanced_place_probability"] = df["mc_place_probability"]
            else:
                # Estimate place as 2.5x win probability (typical racing ratio)
                df["enhanced_place_probability"] = np.minimum(
                    df["enhanced_win_probability"] * 2.5, 0.9
                )
        else:
            weighted_place = sum(df[col] * weight for col, weight in place_cols)
            total_weight = sum(weight for _, weight in place_cols)
            df["enhanced_place_probability"] = np.minimum(
                weighted_place / total_weight, 0.9
            )

        # Position prediction (use advanced if available, otherwise derive from win prob)
        if "advanced_predicted_position" in df.columns:
            df["enhanced_predicted_position"] = df["advanced_predicted_position"]
        else:
            # Estimate position from win probability (inverse relationship)
            race_groups = df.groupby(["course", "race_number"])
            df["enhanced_predicted_position"] = race_groups[
                "enhanced_win_probability"
            ].rank(ascending=False)

        # Confidence score (based on model agreement)
        if (
            "advanced_win_probability" in df.columns
            and "legacy_ensemble_probability" in df.columns
        ):
            # Calculate agreement between advanced and legacy
            agreement = 1.0 - np.abs(
                df["advanced_win_probability"] - df["legacy_ensemble_probability"]
            )
            df["prediction_confidence"] = np.minimum(agreement, 0.95)
        elif "advanced_win_probability" in df.columns:
            df["prediction_confidence"] = 0.85  # High confidence for advanced models
        elif "legacy_ensemble_probability" in df.columns:
            df["prediction_confidence"] = 0.7  # Lower confidence for legacy only
        else:
            df["prediction_confidence"] = 0.6  # Fallback confidence

        logger.info("✅ Enhanced ensemble predictions created")

    def generate_selections(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Generate AI selections for each race."""
        logger.info("🏆 Generating enhanced AI selections...")

        selections = {}

        for course in df["course"].unique():
            course_data = df[df["course"] == course].copy()
            course_selections = []

            for race_num in sorted(course_data["race_number"].unique()):
                race_data = course_data[course_data["race_number"] == race_num].copy()

                if len(race_data) == 0:
                    continue

                # Sort by enhanced win probability (highest first)
                race_data = race_data.sort_values(
                    "enhanced_win_probability", ascending=False
                )

                # Get top 3 selections
                top_3 = race_data.head(3)

                race_info = {
                    "race_number": race_num,
                    "race_time": race_data.iloc[0]["race_time"],
                    "field_size": len(race_data),
                    "course": course,
                    "selections": [],
                }

                for idx, (_, horse) in enumerate(top_3.iterrows()):
                    selection = {
                        "position": idx + 1,
                        "horse_name": horse["horse_name"],
                        "jockey": horse["jockey"],
                        "trainer": horse["trainer"],
                        "win_odds": horse["win_odds"],
                        "enhanced_win_prob": horse.get("enhanced_win_probability", 0),
                        "enhanced_place_prob": horse.get(
                            "enhanced_place_probability", 0
                        ),
                        "predicted_position": horse.get(
                            "enhanced_predicted_position", idx + 1
                        ),
                        "confidence": horse.get("prediction_confidence", 0.7),
                        "power_rating": horse.get("power_rating", "N/A"),
                        "speed_figure": horse.get("speed_figure", "N/A"),
                        "form_score": horse.get("form_score", "N/A"),
                        "betting_recommendation": self.get_betting_recommendation(
                            horse
                        ),
                    }
                    race_info["selections"].append(selection)

                course_selections.append(race_info)

            selections[course] = course_selections

        return selections

    def get_betting_recommendation(self, horse: pd.Series) -> str:
        """Generate betting recommendation based on enhanced analysis."""
        win_prob = horse.get("enhanced_win_probability", 0)
        place_prob = horse.get("enhanced_place_probability", 0)
        confidence = horse.get("prediction_confidence", 0.7)
        odds = horse.get("win_odds", 10.0)

        # Calculate value
        implied_prob = 1.0 / odds if odds > 0 else 0
        value = win_prob - implied_prob

        # Recommendations based on advanced metrics
        if value > 0.1 and confidence > 0.8:
            return "STRONG VALUE BET"
        elif value > 0.05 and confidence > 0.7:
            return "VALUE BET"
        elif place_prob > 0.5 and odds > 3.0:
            return "EACH WAY VALUE"
        elif win_prob > 0.3 and confidence > 0.8:
            return "HIGH CONFIDENCE"
        elif value > 0.02:
            return "SMALL VALUE"
        else:
            return "CONSIDER"

    def format_selections_report(self, selections: Dict[str, List[Dict]]) -> str:
        """Format enhanced selections into a readable report."""
        report = f"""
🎯 ENHANCED AI RACING SELECTIONS - {date.today().strftime('%A, %B %d, %Y')}
{'=' * 80}

Generated using Advanced Metrics ML Models
• Power Ratings, Speed Figures, Pace Analysis, Form Scores
• Multiple Model Types: Win Probability, Position Prediction, Place Probability
• Enhanced Ensemble Combining Legacy + Advanced Predictions

"""

        total_races = sum(len(course_races) for course_races in selections.values())
        total_selections = sum(
            len(race["selections"])
            for course_races in selections.values()
            for race in course_races
        )

        report += f"📊 Summary: {total_races} races, {total_selections} selections\n\n"

        for course, races in selections.items():
            report += f"🏇 {course.upper()}\n"
            report += "─" * 60 + "\n"

            for race in races:
                report += f"\nRace {race['race_number']} - {race['race_time']} ({race['field_size']} runners)\n"

                for selection in race["selections"]:
                    power = selection["power_rating"]
                    speed = selection["speed_figure"]
                    form = selection["form_score"]

                    report += f"  {selection['position']}. {selection['horse_name']} "
                    report += f"({selection['jockey']}) "
                    report += f"- {selection['win_odds']}/1\n"

                    report += f"     Win: {selection['enhanced_win_prob']:.1%} | "
                    report += f"Place: {selection['enhanced_place_prob']:.1%} | "
                    report += f"Pos: {selection['predicted_position']:.1f} | "
                    report += f"Conf: {selection['confidence']:.1%}\n"

                    if power != "N/A":
                        report += f"     Power: {power:.1f} | Speed: {speed:.1f} | Form: {form:.1f}\n"

                    report += f"     {selection['betting_recommendation']}\n"

                report += "\n"

            report += "\n"

        report += f"""
{'=' * 80}
🤖 Model Information:
• Advanced Metrics Models: {'✅ Active' if self.advanced_models else '❌ Not Available'}
• Legacy Models: {'✅ Active' if self.legacy_models else '❌ Not Available'}
• Feature Engineering: Enhanced with power ratings, speed figures, pace analysis
• Prediction Confidence: Based on model agreement and advanced metrics quality

💡 Betting Recommendations:
• STRONG VALUE BET: High confidence + significant edge over market
• VALUE BET: Good confidence + positive expected value
• EACH WAY VALUE: Strong place probability with decent odds
• HIGH CONFIDENCE: High win probability with good model confidence
• SMALL VALUE: Slight edge detected
• CONSIDER: Worth monitoring but no strong edge

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report

    def run_daily_selections(self) -> None:
        """Generate and display enhanced daily AI selections."""
        try:
            logger.info("🚀 Starting Enhanced AI Selections Generation")
            logger.info(f"📅 Date: {date.today()}")

            # Load race data
            races_df = self.load_race_data()

            if len(races_df) == 0:
                logger.warning("⚠️ No race data found for today")
                return

            # Engineer features
            features_df = self.engineer_features(races_df)

            # Generate predictions
            predictions_df = self.generate_predictions(features_df)

            # Generate selections
            selections = self.generate_selections(predictions_df)

            # Format and display report
            report = self.format_selections_report(selections)
            print(report)

            # Save report
            report_file = Path(
                f"enhanced_ai_selections_{date.today().strftime('%Y%m%d')}.txt"
            )
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(
                f"✅ Enhanced AI selections complete! Report saved: {report_file}"
            )

        except Exception as e:
            logger.error(f"❌ Enhanced AI selections failed: {e}")
            traceback.print_exc()


def main():
    """Main function."""
    print("🎯 Enhanced AI Racing Selections Generator")
    print("==========================================")

    generator = EnhancedAISelectionsGenerator()
    generator.run_daily_selections()


if __name__ == "__main__":
    main()
