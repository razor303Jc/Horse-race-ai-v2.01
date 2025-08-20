#!/usr/bin/env python3
"""
Strategy-Aware ML Model Training Pipeline
Train ML models with betting strategy features and strategy classification
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import logging
from typing import Dict, List, Tuple, Any
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem
from src.database.database_manager import DatabaseManager
from scripts.strategy_integrated_ml import StrategyIntegratedMLSystem

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.03/logs/strategy_training.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class StrategyAwareModelTrainer:
    """Comprehensive training pipeline for strategy-aware ML models"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.enhanced_ml = EnhancedMLRatingSystem()
        self.strategy_ml = StrategyIntegratedMLSystem()

        # Training parameters
        self.lookback_days = 90  # Last 3 months for training
        self.min_races_required = 100
        self.strategy_success_threshold = 0.65

        # Output directory
        self.model_dir = "/home/jc/Documents/Horse-race-ai-v2.03/models/strategy_aware"
        os.makedirs(self.model_dir, exist_ok=True)

    def collect_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Collect historical race data with results for training"""
        logger.info("Collecting historical training data...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)

        # Query historical races with results
        query = """
        SELECT 
            r.*,
            rr.finishing_position,
            rr.starting_price_decimal,
            rr.betfair_win_price,
            rr.betfair_place_price,
            rr.official_rating,
            rr.jockey_claim,
            rr.equipment_change
        FROM races r
        JOIN race_results rr ON r.race_id = rr.race_id
        WHERE r.race_date BETWEEN ? AND ?
        AND rr.finishing_position IS NOT NULL
        AND rr.starting_price_decimal > 0
        ORDER BY r.race_date DESC, r.race_time DESC
        """

        race_data = self.db_manager.execute_query(
            query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )

        if len(race_data) < self.min_races_required:
            logger.warning(
                f"Insufficient training data: {len(race_data)} races (minimum {self.min_races_required})"
            )
            return pd.DataFrame(), pd.DataFrame()

        logger.info(f"Collected {len(race_data)} race entries for training")

        # Convert to DataFrame and prepare features
        df = pd.DataFrame(race_data)

        # Create target variables
        df["won"] = (df["finishing_position"] == 1).astype(int)
        df["placed"] = (df["finishing_position"] <= 3).astype(int)

        # Calculate betting outcomes
        df = self._calculate_betting_outcomes(df)

        return df, df

    def _calculate_betting_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate betting strategy outcomes for training targets"""
        logger.info("Calculating betting strategy outcomes...")

        # Group by race to calculate strategy outcomes
        strategy_outcomes = []

        for race_id, race_group in df.groupby("race_id"):
            race_horses = race_group.copy()

            # Calculate 80/20 strategy outcomes
            eighty_twenty_profitable = self._calculate_80_20_outcomes(race_horses)

            # Calculate dutching outcomes
            dutching_profitable = self._calculate_dutching_outcomes(race_horses)

            # Add strategy profitability to each horse
            for idx, horse in race_horses.iterrows():
                horse_data = horse.to_dict()
                horse_data["eighty_twenty_profitable"] = eighty_twenty_profitable
                horse_data["dutching_profitable"] = dutching_profitable

                # Individual horse strategy suitability
                horse_data["suitable_for_80_20"] = self._is_suitable_for_80_20(horse)
                horse_data["suitable_for_dutching"] = self._is_suitable_for_dutching(
                    horse, race_horses
                )

                strategy_outcomes.append(horse_data)

        result_df = pd.DataFrame(strategy_outcomes)
        logger.info(f"Calculated strategy outcomes for {len(result_df)} horse entries")

        return result_df

    def _calculate_80_20_outcomes(self, race_horses: pd.DataFrame) -> int:
        """Calculate if 80/20 strategy would be profitable in this race"""
        # 80/20 strategy: back top-rated horses where odds > 4.0 for place
        suitable_horses = race_horses[
            (race_horses["starting_price_decimal"] >= 4.0)
            & (
                race_horses["official_rating"]
                >= race_horses["official_rating"].quantile(0.8)
            )
        ]

        if len(suitable_horses) == 0:
            return 0

        # Check if any suitable horse placed
        placed_horses = suitable_horses[suitable_horses["placed"] == 1]
        return 1 if len(placed_horses) > 0 else 0

    def _calculate_dutching_outcomes(self, race_horses: pd.DataFrame) -> int:
        """Calculate if dutching would be profitable in this race"""
        # Select top 3-4 horses by rating for dutching
        top_horses = race_horses.nlargest(4, "official_rating")

        if len(top_horses) < 3:
            return 0

        # Calculate dutching stakes and returns
        total_inverse_odds = sum(
            1.0 / horse["starting_price_decimal"] for _, horse in top_horses.iterrows()
        )

        if total_inverse_odds >= 1.0:  # No profit possible
            return 0

        # Check if any dutched horse won
        winners = top_horses[top_horses["won"] == 1]
        return 1 if len(winners) > 0 else 0

    def _is_suitable_for_80_20(self, horse: pd.Series) -> int:
        """Determine if individual horse is suitable for 80/20 strategy"""
        return (
            1
            if (
                horse["starting_price_decimal"] >= 4.0
                and horse["official_rating"] >= 70
                and horse.get("recent_form_score", 50) >= 60
            )
            else 0
        )

    def _is_suitable_for_dutching(
        self, horse: pd.Series, race_horses: pd.DataFrame
    ) -> int:
        """Determine if horse is suitable for dutching strategy"""
        # Top 4 horses by rating
        top_ratings = race_horses["official_rating"].nlargest(4)
        return 1 if horse["official_rating"] in top_ratings.values else 0

    def prepare_enhanced_features(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepare enhanced features including strategy features"""
        logger.info("Preparing enhanced features with strategy integration...")

        feature_data = []
        targets = {
            "win": [],
            "place": [],
            "eighty_twenty_suitable": [],
            "dutching_suitable": [],
            "eighty_twenty_profitable": [],
            "dutching_profitable": [],
        }

        for idx, horse in df.iterrows():
            try:
                # Convert horse data to feature dictionary
                feature_dict = {
                    "official_rating": horse.get("official_rating", 70),
                    "jockey_claim": horse.get("jockey_claim", 0),
                    "recent_form_score": horse.get("recent_form_score", 50),
                    "speed_rating": horse.get("speed_rating", 70),
                    "consistency_score": horse.get("consistency_score", 70),
                    "distance_specialization": horse.get(
                        "distance_specialization", 0.5
                    ),
                    "course_form": horse.get("course_form", 0.5),
                    "composite_score": horse.get("composite_score", 75),
                }

                # Race conditions
                race_conditions = {
                    "race_class": horse.get("race_class", "MAIDEN"),
                    "going": horse.get("going", "GOOD"),
                    "distance_yards": horse.get("distance_yards", 1760),
                    "field_size": 10,  # Default
                }

                # Generate enhanced features with strategy features
                enhanced_features = self.enhanced_ml.prepare_enhanced_features(
                    pd.DataFrame([feature_dict]), race_conditions
                )

                if len(enhanced_features) > 0:
                    feature_data.append(enhanced_features[0])

                    # Collect targets
                    targets["win"].append(horse.get("won", 0))
                    targets["place"].append(horse.get("placed", 0))
                    targets["eighty_twenty_suitable"].append(
                        horse.get("suitable_for_80_20", 0)
                    )
                    targets["dutching_suitable"].append(
                        horse.get("suitable_for_dutching", 0)
                    )
                    targets["eighty_twenty_profitable"].append(
                        horse.get("eighty_twenty_profitable", 0)
                    )
                    targets["dutching_profitable"].append(
                        horse.get("dutching_profitable", 0)
                    )

            except Exception as e:
                logger.warning(f"Error processing horse features: {e}")
                continue

        if len(feature_data) == 0:
            logger.error("No valid features generated")
            return np.array([]), {}

        # Convert to arrays
        X = np.array(feature_data)
        y = {key: np.array(values) for key, values in targets.items()}

        logger.info(
            f"Prepared features: {X.shape}, targets: {[f'{k}:{len(v)}' for k,v in y.items()]}"
        )

        return X, y

    def train_strategy_models(self, X: np.ndarray, y: Dict[str, np.ndarray]):
        """Train all strategy-aware models"""
        logger.info("Training strategy-aware models...")

        if len(X) == 0:
            logger.error("No training data available")
            return

        # Train enhanced ML models with strategy features
        logger.info("Training enhanced ML rating system...")
        self.enhanced_ml.train_models(X, y["win"], y["place"])

        # Save enhanced ML models
        enhanced_model_path = os.path.join(
            self.model_dir, "enhanced_ml_with_strategy.joblib"
        )
        joblib.dump(self.enhanced_ml, enhanced_model_path)
        logger.info(f"Saved enhanced ML model to {enhanced_model_path}")

        # Train strategy classification models
        logger.info("Training strategy classification models...")

        # Create combined training data for strategy ML system
        strategy_training_data = []
        for i in range(len(X)):
            horse_data = {
                "features": X[i],
                "win_prob": y["win"][i],
                "place_prob": y["place"][i],
                "eighty_twenty_suitable": y["eighty_twenty_suitable"][i],
                "dutching_suitable": y["dutching_suitable"][i],
                "eighty_twenty_profitable": y["eighty_twenty_profitable"][i],
                "dutching_profitable": y["dutching_profitable"][i],
            }
            strategy_training_data.append(horse_data)

        # Train strategy ML system
        self.strategy_ml.train_strategy_classifiers(strategy_training_data)

        # Save strategy models
        strategy_model_path = os.path.join(
            self.model_dir, "strategy_integrated_ml.joblib"
        )
        joblib.dump(self.strategy_ml, strategy_model_path)
        logger.info(f"Saved strategy ML system to {strategy_model_path}")

        # Generate training summary
        self._generate_training_summary(X, y)

    def _generate_training_summary(self, X: np.ndarray, y: Dict[str, np.ndarray]):
        """Generate comprehensive training summary"""
        logger.info("Generating training summary...")

        summary = {
            "training_date": datetime.now().isoformat(),
            "training_period": f"{self.lookback_days} days",
            "total_samples": len(X),
            "feature_count": X.shape[1] if len(X) > 0 else 0,
            "target_distributions": {
                key: {
                    "positive_samples": int(np.sum(values)),
                    "negative_samples": int(len(values) - np.sum(values)),
                    "positive_rate": float(np.mean(values)),
                }
                for key, values in y.items()
            },
            "strategy_performance": {
                "eighty_twenty_success_rate": float(
                    np.mean(y["eighty_twenty_profitable"])
                ),
                "dutching_success_rate": float(np.mean(y["dutching_profitable"])),
                "eighty_twenty_suitability_rate": float(
                    np.mean(y["eighty_twenty_suitable"])
                ),
                "dutching_suitability_rate": float(np.mean(y["dutching_suitable"])),
            },
        }

        # Save summary
        summary_path = os.path.join(self.model_dir, "training_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Training Summary:")
        logger.info(f"  - Total samples: {summary['total_samples']}")
        logger.info(f"  - Features: {summary['feature_count']}")
        logger.info(
            f"  - 80/20 success rate: {summary['strategy_performance']['eighty_twenty_success_rate']:.2%}"
        )
        logger.info(
            f"  - Dutching success rate: {summary['strategy_performance']['dutching_success_rate']:.2%}"
        )
        logger.info(f"Saved training summary to {summary_path}")


def main():
    """Main training pipeline execution"""
    logger.info("Starting Strategy-Aware ML Model Training Pipeline")

    try:
        trainer = StrategyAwareModelTrainer()

        # Collect training data
        df, _ = trainer.collect_training_data()

        if df.empty:
            logger.error("No training data available")
            return

        # Prepare features
        X, y = trainer.prepare_enhanced_features(df)

        if len(X) == 0:
            logger.error("Feature preparation failed")
            return

        # Train models
        trainer.train_strategy_models(X, y)

        logger.info("Strategy-aware model training completed successfully!")

    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
