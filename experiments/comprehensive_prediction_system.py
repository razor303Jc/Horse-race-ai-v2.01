#!/usr/bin/env python3
"""
Comprehensive ML Prediction System
Integrates multiple trained models for horse racing predictions
"""

import sqlite3
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveRacingPredictor:
    """Comprehensive prediction system using multiple trained models."""

    def __init__(self):
        self.models_dir = Path("trained_models")
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = {}
        self.performance = {}

        # Load all available models
        self.load_all_models()

    def load_all_models(self):
        """Load all trained models and components."""

        logger.info("🔧 Loading all trained models...")

        # Load race card models
        try:
            self.models["rc_rf"] = joblib.load(
                self.models_dir / "race_card_models/random_forest_race_card.joblib"
            )
            self.models["rc_gb"] = joblib.load(
                self.models_dir / "race_card_models/gradient_boosting_race_card.joblib"
            )
            self.models["rc_nn"] = joblib.load(
                self.models_dir / "race_card_models/neural_network_race_card.joblib"
            )
            self.models["rc_lr"] = joblib.load(
                self.models_dir
                / "race_card_models/logistic_regression_race_card.joblib"
            )

            self.scalers["race_card"] = joblib.load(
                self.models_dir / "race_card_models/scalers_race_card.joblib"
            )
            self.encoders["race_card"] = joblib.load(
                self.models_dir / "race_card_models/encoders_race_card.joblib"
            )
            self.feature_names["race_card"] = joblib.load(
                self.models_dir / "race_card_models/features_race_card.joblib"
            )
            self.performance["race_card"] = joblib.load(
                self.models_dir / "race_card_models/performance_race_card.joblib"
            )
            logger.info("✅ Race card models loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load race card models: {e}")

        logger.info(f"🎯 Total models loaded: {len(self.models)}")

    def predict_race_cards(
        self, race_cards_db: str = "race_cards_prediction_data.db", num_races: int = 10
    ) -> pd.DataFrame:
        """Make predictions on race cards using race card models."""

        logger.info(f"🏁 Making predictions on {num_races} race cards...")

        conn = sqlite3.connect(race_cards_db)

        # Get sample races for prediction
        races_query = """
        SELECT DISTINCT race_id 
        FROM race_cards 
        ORDER BY RANDOM() 
        LIMIT ?
        """

        race_ids = pd.read_sql_query(races_query, conn, params=[num_races])[
            "race_id"
        ].tolist()

        predictions = []

        for race_id in race_ids:
            race_pred = self.predict_single_race_card(conn, race_id)
            if race_pred is not None:
                predictions.append(race_pred)

        conn.close()

        if predictions:
            results_df = pd.concat(predictions, ignore_index=True)
            logger.info(f"✅ Generated predictions for {len(predictions)} races")
            return results_df
        else:
            logger.warning("⚠️ No predictions generated")
            return pd.DataFrame()

    def predict_single_race_card(self, conn, race_id: str) -> Optional[pd.DataFrame]:
        """Predict a single race card using race card models."""

        # Load race data
        query = """
        SELECT 
            rc.race_id,
            rc.course,
            rc.race_type,
            rc.distance,
            rc.surface,
            rc.field_size,
            rc.prize_money,
            rc.class_level,
            rc.weather_condition,
            rc.track_condition,
            rc.going,
            
            rce.entry_id,
            rce.horse_name,
            rce.horse_age,
            rce.horse_weight_kg,
            rce.draw,
            rce.morning_line_odds,
            rce.recent_form_rating,
            rce.speed_rating,
            rce.class_rating,
            rce.track_rating,
            rce.distance_rating,
            rce.jockey_rating,
            rce.trainer_rating,
            rce.career_starts,
            rce.career_wins,
            rce.career_places,
            rce.last_start_days,
            rce.form_string,
            rce.equipment,
            rce.comments
            
        FROM race_cards rc
        JOIN race_card_entries rce ON rc.race_id = rce.race_id
        WHERE rc.race_id = ?
        AND rce.morning_line_odds IS NOT NULL
        AND rce.morning_line_odds > 0
        """

        df = pd.read_sql_query(query, conn, params=[race_id])

        if df.empty:
            return None

        # Engineer features (same as training)
        df = self.engineer_race_card_features_for_prediction(df)

        # Prepare features
        X = self.prepare_features_for_race_card_prediction(df)

        if X is None:
            return None

        # Make predictions with all race card models
        predictions = {}

        # Random Forest
        if "rc_rf" in self.models:
            try:
                rf_probs = self.models["rc_rf"].predict_proba(X)[:, 1]
                predictions["rf_prob"] = rf_probs
            except Exception as e:
                logger.warning(f"RF prediction failed: {e}")

        # Gradient Boosting
        if "rc_gb" in self.models:
            try:
                gb_probs = self.models["rc_gb"].predict_proba(X)[:, 1]
                predictions["gb_prob"] = gb_probs
            except Exception as e:
                logger.warning(f"GB prediction failed: {e}")

        # Neural Network
        if "rc_nn" in self.models:
            try:
                X_scaled = self.scalers["race_card"]["feature_scaler"].transform(X)
                nn_probs = self.models["rc_nn"].predict_proba(X_scaled)[:, 1]
                predictions["nn_prob"] = nn_probs
            except Exception as e:
                logger.warning(f"NN prediction failed: {e}")

        # Logistic Regression
        if "rc_lr" in self.models:
            try:
                lr_probs = self.models["rc_lr"].predict_proba(X)[:, 1]
                predictions["lr_prob"] = lr_probs
            except Exception as e:
                logger.warning(f"LR prediction failed: {e}")

        if not predictions:
            return None

        # Create ensemble prediction
        prob_cols = list(predictions.keys())
        ensemble_prob = np.mean([predictions[col] for col in prob_cols], axis=0)
        predictions["ensemble_prob"] = ensemble_prob

        # Add predictions to dataframe
        result_df = df[
            [
                "race_id",
                "horse_name",
                "morning_line_odds",
                "recent_form_rating",
                "speed_rating",
                "class_rating",
            ]
        ].copy()

        for col, probs in predictions.items():
            result_df[col] = probs

        # Add rankings
        result_df["ml_rank"] = result_df["ensemble_prob"].rank(ascending=False)
        result_df["odds_rank"] = result_df["morning_line_odds"].rank()

        # Calculate confidence metrics
        result_df["confidence"] = (
            result_df["ensemble_prob"] / result_df["ensemble_prob"].max()
        )
        result_df["value_bet"] = result_df["ensemble_prob"] > (
            1.0 / result_df["morning_line_odds"]
        )

        return result_df.sort_values("ensemble_prob", ascending=False)

    def engineer_race_card_features_for_prediction(
        self, df: pd.DataFrame
    ) -> pd.DataFrame:
        """Engineer features for prediction (same as training)."""

        # Market features
        df["implied_prob"] = 1.0 / df["morning_line_odds"]
        df["market_share"] = df.groupby("race_id")["implied_prob"].transform(
            lambda x: x / x.sum()
        )

        # Odds features
        df["log_odds"] = np.log(df["morning_line_odds"])
        df["odds_rank"] = df.groupby("race_id")["morning_line_odds"].rank()
        df["odds_percentile"] = df.groupby("race_id")["morning_line_odds"].rank(
            pct=True
        )
        df["is_favorite"] = (
            df.groupby("race_id")["morning_line_odds"]
            .transform(lambda x: x == x.min())
            .astype(int)
        )
        df["is_outsider"] = (df["morning_line_odds"] >= 20.0).astype(int)
        df["market_strength"] = 1.0 / df["morning_line_odds"]

        # Competition features
        df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
        df["weight_percentile"] = df.groupby("race_id")["horse_weight_kg"].rank(
            pct=True
        )
        df["age_percentile"] = df.groupby("race_id")["horse_age"].rank(pct=True)

        # Rating features
        df["total_rating"] = (
            df["recent_form_rating"] + df["speed_rating"] + df["class_rating"]
        ) / 3
        df["form_rank"] = df.groupby("race_id")["recent_form_rating"].rank(
            ascending=False
        )
        df["speed_rank"] = df.groupby("race_id")["speed_rating"].rank(ascending=False)
        df["total_rating_rank"] = df.groupby("race_id")["total_rating"].rank(
            ascending=False
        )

        # Experience features
        df["win_rate"] = df["career_wins"] / (df["career_starts"] + 1)
        df["place_rate"] = df["career_places"] / (df["career_starts"] + 1)
        df["experience_score"] = np.log(df["career_starts"] + 1)

        # Recency features
        df["days_since_last_run"] = df["last_start_days"]
        df["freshness_score"] = 1.0 / (df["last_start_days"] + 1)

        # Form analysis
        def analyze_form_string(form_str):
            if pd.isna(form_str) or form_str == "":
                return 0, 0, 0

            recent_wins = form_str[:3].count("1")
            recent_places = form_str[:3].count("2") + form_str[:3].count("3")
            consistency = len([x for x in form_str[:5] if x.isdigit() and int(x) <= 5])

            return recent_wins, recent_places, consistency

        form_analysis = df["form_string"].apply(analyze_form_string)
        df["recent_wins"] = [x[0] for x in form_analysis]
        df["recent_places"] = [x[1] for x in form_analysis]
        df["form_consistency"] = [x[2] for x in form_analysis]

        # Distance processing
        df["distance_numeric"] = pd.to_numeric(
            df["distance"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
        ).fillna(1600)

        # Prize money features
        df["log_prize"] = np.log(df["prize_money"] + 1)
        df["prize_per_runner"] = df["prize_money"] / df["field_size"]

        # Equipment flags
        df["has_equipment"] = (~df["equipment"].isin(["", None])).astype(int)
        df["has_comments"] = (~df["comments"].isin(["", None])).astype(int)

        return df

    def prepare_features_for_race_card_prediction(self, df: pd.DataFrame):
        """Prepare features for race card prediction."""

        try:
            # Encode categorical features
            encoders = self.encoders["race_card"]
            categorical_features = [
                "course",
                "race_type",
                "surface",
                "class_level",
                "weather_condition",
                "track_condition",
                "going",
            ]

            for feature in categorical_features:
                if feature in encoders:
                    le = encoders[feature]
                    # Handle unseen categories
                    df[f"{feature}_encoded"] = (
                        df[feature]
                        .fillna("Unknown")
                        .map(lambda x: le.transform([x])[0] if x in le.classes_ else 0)
                    )

            # Use same features as training
            feature_columns = self.feature_names["race_card"]
            available_features = [col for col in feature_columns if col in df.columns]

            X = df[available_features].fillna(0)

            return X

        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            return None

    def display_predictions(self, predictions_df: pd.DataFrame):
        """Display predictions in a formatted way."""

        if predictions_df.empty:
            logger.warning("No predictions to display")
            return

        logger.info("\n🏆 RACE PREDICTIONS")
        logger.info("=" * 80)

        for race_id in predictions_df["race_id"].unique():
            race_data = predictions_df[predictions_df["race_id"] == race_id]

            logger.info(f"\n🏁 Race ID: {race_id}")
            logger.info("-" * 60)

            for idx, row in race_data.head(5).iterrows():  # Top 5 horses
                logger.info(
                    f"{int(row['ml_rank']):2d}. {row['horse_name']:<20} "
                    f"Odds: {row['morning_line_odds']:5.1f} "
                    f"ML Prob: {row['ensemble_prob']:.3f} "
                    f"Conf: {row['confidence']:.2f} "
                    f"{'💰' if row['value_bet'] else '  '}"
                )

    def analyze_model_performance(self):
        """Analyze and display model performance metrics."""

        logger.info("\n📊 MODEL PERFORMANCE ANALYSIS")
        logger.info("=" * 50)

        for model_type, performance in self.performance.items():
            logger.info(f"\n{model_type.upper()} Models:")
            logger.info("-" * 30)

            if isinstance(performance, dict):
                for model_name, metrics in performance.items():
                    if isinstance(metrics, dict) and "roc_auc" in metrics:
                        logger.info(
                            f"{model_name:<20} AUC: {metrics['roc_auc']:.4f} "
                            f"Acc: {metrics.get('accuracy', 0):.4f}"
                        )

    def save_predictions(self, predictions_df: pd.DataFrame, filename: str = None):
        """Save predictions to CSV file."""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"race_predictions_{timestamp}.csv"

        predictions_df.to_csv(filename, index=False)
        logger.info(f"💾 Predictions saved to {filename}")


def main():
    """Main prediction function."""

    predictor = ComprehensiveRacingPredictor()

    # Analyze model performance
    predictor.analyze_model_performance()

    # Make predictions on sample race cards
    predictions = predictor.predict_race_cards(num_races=5)

    if not predictions.empty:
        # Display predictions
        predictor.display_predictions(predictions)

        # Save predictions
        predictor.save_predictions(predictions)

        logger.info("\n✅ Prediction analysis complete!")
    else:
        logger.error("\n❌ No predictions generated")


if __name__ == "__main__":
    main()
