#!/usr/bin/env python3
"""
Enhanced ML Pipeline Integration - V2.01 Features
================================================

Upgraded pipeline that uses the sophisticated 53+ feature enhanced ML system
instead of the basic 6-feature approach. Integrates:

- V2.01 Ensemble Predictor (4-model ensemble)
- Enhanced feature preparation (53+ features)
- Composite scoring system
- Monte Carlo simulation integration
- Consensus rating system
- Advanced performance tracking

This replaces the basic pipeline_integration.py with the sophisticated system.
"""

import os
import sys
import time
import logging
import traceback
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import enhanced systems
from src.horse_racing_ai.ml.v2_01_ensemble_predictor import (
    V201EnsemblePredictor,
    EnsembleResults,
)
from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem

# Enhanced logging support
try:
    from tools.logging.enhanced_logging import HorseRacingLogger

    ENHANCED_LOGGING = True
    enhanced_logger = HorseRacingLogger("enhanced_ml_pipeline")
except ImportError:
    ENHANCED_LOGGING = False
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class EnhancedPipelineIntegration:
    """Enhanced ML Pipeline using V2.01 ensemble system with 53+ features."""

    def __init__(self):
        self.logger = enhanced_logger if ENHANCED_LOGGING else logger
        self.is_running = False
        self.models_path = Path("/app/models")

        # Database URLs - same as basic pipeline
        self.cards_db_url = os.getenv(
            "CARDS_DATABASE_URL",
            "postgresql://horse_racing:secure_password_123@postgres:5432/cards_horse_racing_db",
        )
        self.results_db_url = os.getenv(
            "RESULTS_DATABASE_URL",
            "postgresql://horse_racing:secure_password_123@postgres:5432/results_horse_racing_db",
        )
        self.advanced_db_url = os.getenv(
            "ADVANCED_DATABASE_URL",
            "postgresql://horse_racing:secure_password_123@postgres:5432/advanced_racing_metrics_db",
        )

        # Initialize enhanced systems
        self.ensemble_predictor = V201EnsemblePredictor(
            models_dir=str(self.models_path)
        )
        self.enhanced_ml_system = EnhancedMLRatingSystem()

        # Ensure directories exist
        self.models_path.mkdir(exist_ok=True)

        # Log initialization
        if ENHANCED_LOGGING:
            enhanced_logger.log_system_startup(
                {
                    "pipeline_type": "enhanced_v2_01",
                    "features": "53+_enhanced_features",
                    "models": "4_model_ensemble",
                    "databases": ["cards", "results", "advanced_metrics"],
                }
            )

    def load_enhanced_training_data(self) -> pd.DataFrame:
        """Load and prepare enhanced training data with 53+ features."""
        try:
            self.logger.info(
                "🔄 Loading enhanced training data from results database..."
            )

            engine = create_engine(self.results_db_url)

            # Load comprehensive race results data
            query = """
            SELECT 
                horse_name,
                race_date,
                track,
                distance,
                going,
                race_class,
                age,
                weight,
                jockey,
                trainer,
                or_rating,
                ts_rating,
                rpr_rating,
                position,
                total_runners as runners,
                starting_price as sp,
                favourite as fav,
                race_type,
                prize_money,
                beaten_lengths,
                course_type,
                race_time,
                winning_time,
                sectional_times,
                comments,
                form_figures,
                days_since_last_run,
                career_runs,
                career_wins,
                career_places,
                earnings,
                recent_form,
                track_record,
                distance_record,
                class_drops,
                class_rises
            FROM results 
            WHERE position IS NOT NULL 
            AND or_rating IS NOT NULL
            AND age IS NOT NULL
            ORDER BY race_date DESC
            LIMIT 10000
            """

            with engine.connect() as conn:
                df = pd.read_sql(query, conn)

            self.logger.info(f"📊 Loaded {len(df)} enhanced training records")
            return df

        except Exception as e:
            self.logger.error(f"❌ Failed to load enhanced training data: {e}")
            return None

    def prepare_enhanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare enhanced features using the sophisticated feature engineering system."""
        try:
            self.logger.info("🔧 Preparing enhanced features (53+)...")

            # Create target variable
            df["won"] = (df["position"] == 1).astype(int)

            # Use enhanced ML system to prepare features
            enhanced_df = self.enhanced_ml_system.prepare_enhanced_features(df)

            if enhanced_df is not None:
                feature_count = len(
                    [col for col in enhanced_df.columns if col != "won"]
                )
                self.logger.info(f"📊 Prepared {feature_count} enhanced features")

                # Log feature categories
                if ENHANCED_LOGGING:
                    enhanced_logger.log_feature_preparation(
                        {
                            "total_features": feature_count,
                            "feature_categories": {
                                "composite_scores": [
                                    "form_score",
                                    "power_rating",
                                    "speed_score",
                                    "class_score",
                                    "consistency_score",
                                ],
                                "historical_performance": [
                                    "avg_position_l5",
                                    "avg_beaten_lengths_l5",
                                    "speed_figure_trend",
                                ],
                                "betting_features": [
                                    "market_confidence",
                                    "odds_value",
                                    "public_confidence",
                                ],
                                "class_analysis": [
                                    "class_drop_flag",
                                    "class_rise_flag",
                                    "class_consistency",
                                ],
                                "track_conditions": [
                                    "going_preference",
                                    "distance_preference",
                                    "track_bias",
                                ],
                            },
                        }
                    )

                return enhanced_df
            else:
                # Fallback to basic features if enhanced preparation fails
                self.logger.warning(
                    "⚠️ Enhanced features failed, falling back to basic features"
                )
                return self._prepare_basic_features(df)

        except Exception as e:
            self.logger.error(f"❌ Enhanced feature preparation failed: {e}")
            # Fallback to basic features
            return self._prepare_basic_features(df)

    def _prepare_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fallback basic feature preparation."""
        try:
            # Create target variable
            df["won"] = (df["position"] == 1).astype(int)

            # Basic numeric features
            features = []

            if "age" in df.columns:
                df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0)
                features.append("age")

            if "or_rating" in df.columns:
                df["or_rating"] = pd.to_numeric(
                    df["or_rating"], errors="coerce"
                ).fillna(0)
                features.append("or_rating")

            if "runners" in df.columns:
                df["runners"] = pd.to_numeric(df["runners"], errors="coerce").fillna(0)
                features.append("runners")

            if "fav" in df.columns:
                df["is_favorite"] = (df["fav"] == 1).astype(int)
                features.append("is_favorite")

            if "sp" in df.columns:
                df["sp"] = pd.to_numeric(df["sp"], errors="coerce").fillna(0)
                features.append("sp")

            if "race_type" in df.columns:
                df["is_flat"] = (
                    df["race_type"].str.contains("Flat", na=False).astype(int)
                )
                features.append("is_flat")

            self.logger.info(f"📊 Prepared {len(features)} basic features (fallback)")
            return df[features + ["won"]].dropna()

        except Exception as e:
            self.logger.error(f"❌ Basic feature preparation failed: {e}")
            return None

    def train_enhanced_ensemble(self, training_data: pd.DataFrame) -> dict:
        """Train the enhanced 4-model ensemble system."""
        try:
            self.logger.info("🎯 Training enhanced ensemble (4 models)...")

            # Separate features and target
            target_col = "won"
            feature_cols = [col for col in training_data.columns if col != target_col]

            X = training_data[feature_cols]
            y = training_data[target_col]

            self.logger.info(
                f"📊 Training on {len(X)} samples with {len(feature_cols)} features"
            )

            # Train ensemble using V2.01 system
            training_results = self.ensemble_predictor.train_ensemble(X, y)

            if training_results:
                # Log detailed results
                self.logger.info("\n" + "=" * 60)
                self.logger.info("🎯 ENHANCED ENSEMBLE TRAINING RESULTS")
                self.logger.info("=" * 60)

                for model_name, metrics in training_results.items():
                    self.logger.info(f"\n{model_name.upper()}:")
                    for metric, value in metrics.items():
                        self.logger.info(f"  {metric}: {value:.4f}")

                # Save enhanced model
                model_save_path = self.models_path / "enhanced_ensemble_model.pkl"
                self.ensemble_predictor.save_model(str(model_save_path))
                self.logger.info(
                    f"💾 Enhanced ensemble model saved to {model_save_path}"
                )

                if ENHANCED_LOGGING:
                    enhanced_logger.log_model_training(
                        {
                            "model_type": "enhanced_ensemble",
                            "models_count": 4,
                            "features_count": len(feature_cols),
                            "training_samples": len(X),
                            "results": training_results,
                            "save_path": str(model_save_path),
                        }
                    )

                return training_results
            else:
                self.logger.error("❌ Enhanced ensemble training failed")
                return None

        except Exception as e:
            self.logger.error(f"❌ Enhanced ensemble training error: {e}")
            return None

    def run_enhanced_training_cycle(self):
        """Run a complete enhanced training cycle."""
        try:
            self.logger.info("🚀 Starting enhanced training cycle...")

            # Load enhanced training data
            raw_data = self.load_enhanced_training_data()
            if raw_data is None:
                self.logger.error("❌ No training data available")
                return

            # Prepare enhanced features
            training_data = self.prepare_enhanced_features(raw_data)
            if training_data is None:
                self.logger.error("❌ Feature preparation failed")
                return

            # Train enhanced ensemble
            results = self.train_enhanced_ensemble(training_data)
            if results is None:
                self.logger.error("❌ Enhanced training failed")
                return

            # Generate comprehensive performance report
            self.generate_performance_report(results, training_data)

            self.logger.info("✅ Enhanced training cycle completed successfully")

        except Exception as e:
            self.logger.error(f"❌ Enhanced training cycle failed: {e}")
            traceback.print_exc()

    def generate_performance_report(
        self, training_results: dict, training_data: pd.DataFrame
    ):
        """Generate detailed performance report for enhanced model."""
        try:
            feature_count = len([col for col in training_data.columns if col != "won"])
            sample_count = len(training_data)

            report = {
                "timestamp": datetime.now().isoformat(),
                "model_type": "enhanced_ensemble_v2_01",
                "features": {
                    "count": feature_count,
                    "type": "enhanced_composite_features",
                },
                "training": {
                    "samples": sample_count,
                    "models": list(training_results.keys()),
                    "results": training_results,
                },
                "performance_summary": {
                    "best_model": max(
                        training_results.keys(),
                        key=lambda k: training_results[k].get("roc_auc", 0),
                    ),
                    "avg_accuracy": np.mean(
                        [
                            metrics.get("accuracy", 0)
                            for metrics in training_results.values()
                        ]
                    ),
                    "avg_roc_auc": np.mean(
                        [
                            metrics.get("roc_auc", 0)
                            for metrics in training_results.values()
                        ]
                    ),
                },
            }

            # Save report
            report_path = (
                self.models_path
                / f"enhanced_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"📊 Performance report saved to {report_path}")

            if ENHANCED_LOGGING:
                enhanced_logger.log_performance_report(report)

        except Exception as e:
            self.logger.error(f"❌ Failed to generate performance report: {e}")

    def run(self):
        """Run the enhanced ML pipeline integration."""
        self.logger.info("🧠 Enhanced ML Pipeline Integration starting...")
        self.is_running = True

        try:
            while self.is_running:
                self.logger.info("🔄 Enhanced ML Pipeline check - system ready")

                # Run enhanced training cycle
                self.run_enhanced_training_cycle()

                # Wait before next cycle (longer interval for enhanced training)
                time.sleep(600)  # 10 minutes between enhanced training cycles

        except KeyboardInterrupt:
            self.logger.info("🛑 Enhanced ML Pipeline Integration stopped")
        except Exception as e:
            self.logger.error(f"❌ Enhanced ML Pipeline error: {e}")
            traceback.print_exc()
        finally:
            self.is_running = False


def main():
    """Main entry point for enhanced pipeline integration."""
    try:
        # Initialize and run enhanced pipeline
        pipeline = EnhancedPipelineIntegration()
        pipeline.run()

    except Exception as e:
        logger.error(f"❌ Enhanced pipeline initialization failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
