#!/usr/bin/env python3
"""
ML Cyclic Training System
Integrates massive dataset generation with advanced ML training in cycles.
Provides performance monitoring and adaptive learning with comprehensive evaluation.
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import warnings

warnings.filterwarnings("ignore")

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from massive_dataset_generator import MassiveDatasetGenerator
from advanced_ml_integration_system import AdvancedMLIntegrationSystem
from race_trends_ml_integration import RaceTrendsMLIntegration

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ml_training_cycles.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MLCyclicTrainingSystem:
    """
    Advanced ML training system that performs cyclic learning with:
    - Massive dataset generation
    - Incremental model training
    - Performance monitoring every 10 cycles
    - Adaptive learning strategies
    - Comprehensive evaluation metrics
    """

    def __init__(
        self,
        db_path: str = "training_cycles.db",
        models_dir: str = "cycle_models",
        results_dir: str = "cycle_results",
    ):
        self.db_path = db_path
        self.models_dir = models_dir
        self.results_dir = results_dir

        # Create directories
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize components
        self.dataset_generator = MassiveDatasetGenerator(db_path=db_path)
        self.ml_system = None
        self.trends_system = None

        # Training state
        self.current_cycle = 0
        self.cycle_results = []
        self.best_performance = {"auc": 0.0, "cycle": 0, "model_path": None}
        self.performance_history = []

        logger.info("🎯 ML Cyclic Training System initialized")

    def generate_training_data(
        self,
        num_horses: int = 15000,
        num_days: int = 1095,  # 3 years
        start_date: str = "2022-01-01",
    ):
        """Generate comprehensive training dataset"""
        logger.info("🏗️ GENERATING MASSIVE TRAINING DATASET")
        logger.info("=" * 60)

        # Remove existing database for fresh start
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info(f"Removed existing database: {self.db_path}")

        # Generate massive dataset
        self.dataset_generator.generate_complete_dataset(
            num_horses=num_horses, start_date=start_date, num_days=num_days
        )

        # Load and validate data
        df = self._load_training_data()
        logger.info(f"✅ Dataset ready: {len(df):,} training examples")
        return df

    def _load_training_data(self) -> pd.DataFrame:
        """Load training data from database into DataFrame"""
        conn = sqlite3.connect(self.db_path)

        query = """
        SELECT 
            rp.*,
            h.name as horse_name,
            h.age,
            h.sex,
            h.rating as horse_rating,
            h.form_rating,
            h.career_wins,
            h.career_runs,
            h.earnings,
            j.name as jockey_name,
            j.skill_rating as jockey_skill,
            j.experience_years as jockey_experience,
            j.win_percentage as jockey_win_pct,
            t.name as trainer_name,
            t.skill_rating as trainer_skill,
            t.stable_size,
            t.win_percentage as trainer_win_pct,
            rc.date,
            rc.race_name,
            rc.race_type,
            rc.distance_meters,
            rc.track_condition,
            rc.weather,
            rc.prize_money,
            rc.num_runners,
            v.name as venue_name,
            v.track_type,
            v.left_right_handed
        FROM race_participants rp
        JOIN horses h ON rp.horse_id = h.horse_id
        JOIN jockeys j ON rp.jockey_id = j.jockey_id
        JOIN trainers t ON rp.trainer_id = t.trainer_id
        JOIN race_cards rc ON rp.race_id = rc.race_id
        JOIN venues v ON rc.venue_id = v.venue_id
        ORDER BY rc.date, rp.race_id
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Add derived features
        df["win"] = (df["actual_finish_position"] == 1).astype(int)
        df["place"] = (df["actual_finish_position"] <= 3).astype(int)
        df["career_win_rate"] = df["career_wins"] / df["career_runs"].clip(lower=1)
        df["weight_per_rating"] = df["weight_lbs"] / df["horse_rating"].clip(lower=1)
        df["odds_probability"] = 1 / df["odds_decimal"]
        df["value_indicator"] = df["odds_probability"] - (1 / df["num_runners"])

        return df

    def run_training_cycles(
        self,
        total_cycles: int = 100,
        evaluation_interval: int = 10,
        data_increment_pct: float = 0.1,
    ):
        """Run ML training in cycles with performance monitoring"""
        logger.info("🚀 STARTING CYCLIC ML TRAINING")
        logger.info("=" * 60)
        logger.info(f"📊 Configuration:")
        logger.info(f"   🔄 Total Cycles: {total_cycles}")
        logger.info(f"   📈 Evaluation Interval: {evaluation_interval}")
        logger.info(f"   📁 Data Increment: {data_increment_pct:.1%}")

        # Load initial training data
        if not os.path.exists(self.db_path):
            logger.info("No existing data found. Generating dataset...")
            self.generate_training_data()

        df = self._load_training_data()
        logger.info(f"📊 Total dataset size: {len(df):,} examples")

        # Initialize ML systems
        self._initialize_ml_systems()

        # Start training cycles
        for cycle in range(1, total_cycles + 1):
            self.current_cycle = cycle
            logger.info(f"\n🔄 TRAINING CYCLE {cycle}/{total_cycles}")
            logger.info("-" * 50)

            # Prepare cycle data
            cycle_data = self._prepare_cycle_data(df, cycle, data_increment_pct)

            # Train models
            cycle_results = self._train_cycle(cycle_data, cycle)

            # Store results
            self.cycle_results.append(cycle_results)

            # Performance evaluation every interval
            if cycle % evaluation_interval == 0:
                self._evaluate_performance_interval(cycle)
                self._save_checkpoint(cycle)

            # Log cycle summary
            logger.info(f"✅ Cycle {cycle} complete:")
            logger.info(f"   🎯 AUC: {cycle_results['auc']:.4f}")
            logger.info(f"   📊 Accuracy: {cycle_results['accuracy']:.4f}")
            logger.info(f"   🎪 Training Time: {cycle_results['training_time']:.2f}s")

        # Final evaluation
        self._final_evaluation()

        logger.info("🎉 CYCLIC TRAINING COMPLETE!")

    def _initialize_ml_systems(self):
        """Initialize ML training systems"""
        logger.info("🧠 Initializing ML systems...")

        # Advanced ML system
        self.ml_system = AdvancedMLIntegrationSystem()

        # Trends integration system
        self.trends_system = RaceTrendsMLIntegration()

        logger.info("✅ ML systems initialized")

    def _prepare_cycle_data(
        self, full_df: pd.DataFrame, cycle: int, increment_pct: float
    ) -> pd.DataFrame:
        """Prepare data for current training cycle"""

        # Progressive data increase strategy
        if cycle <= 10:
            # Start with smaller dataset, increase gradually
            data_fraction = 0.1 + (cycle - 1) * 0.05
        else:
            # Full dataset with rolling window
            data_fraction = min(1.0, 0.6 + (cycle - 10) * increment_pct)

        sample_size = int(len(full_df) * data_fraction)

        # Use chronological sampling (newer data for later cycles)
        if cycle <= 20:
            # Random sampling for early cycles
            cycle_data = full_df.sample(n=sample_size, random_state=cycle)
        else:
            # Recent data bias for later cycles
            sorted_df = full_df.sort_values("date")
            cycle_data = sorted_df.tail(sample_size)

        logger.info(
            f"📊 Cycle {cycle} data: {len(cycle_data):,} examples "
            f"({data_fraction:.1%} of total)"
        )

        return cycle_data

    def _train_cycle(self, cycle_data: pd.DataFrame, cycle: int) -> Dict[str, Any]:
        """Train models for current cycle"""
        start_time = datetime.now()

        # Prepare features and target
        feature_columns = [
            "age",
            "horse_rating",
            "form_rating",
            "career_wins",
            "career_runs",
            "career_win_rate",
            "weight_lbs",
            "weight_per_rating",
            "draw",
            "odds_decimal",
            "odds_probability",
            "value_indicator",
            "days_since_last_run",
            "course_wins",
            "distance_wins",
            "course_and_distance_wins",
            "jockey_skill",
            "jockey_experience",
            "jockey_win_pct",
            "trainer_skill",
            "stable_size",
            "trainer_win_pct",
            "distance_meters",
            "prize_money",
            "num_runners",
        ]

        # Handle missing values
        X = cycle_data[feature_columns].fillna(0)
        y = cycle_data["win"]

        # Add categorical encoding
        X = self._encode_categorical_features(X, cycle_data)

        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Train advanced ML system
        try:
            # Train with synthetic data for ML system
            synthetic_races = self._create_synthetic_races(cycle_data)
            ml_predictions = self.ml_system.predict_race(synthetic_races[0])

            # Evaluate performance
            from sklearn.metrics import (
                roc_auc_score,
                accuracy_score,
                classification_report,
            )
            from sklearn.ensemble import ExtraTreesClassifier

            # Train simple model for evaluation
            model = ExtraTreesClassifier(
                n_estimators=100, max_depth=10, random_state=cycle, n_jobs=-1
            )
            model.fit(X_train, y_train)

            # Predictions
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            y_pred = model.predict(X_test)

            # Calculate metrics
            auc = roc_auc_score(y_test, y_pred_proba)
            accuracy = accuracy_score(y_test, y_pred)

            # Feature importance
            feature_importance = dict(zip(X.columns, model.feature_importances_))
            top_features = sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            )[:10]

        except Exception as e:
            logger.warning(f"⚠️ ML training error in cycle {cycle}: {e}")
            auc = 0.5
            accuracy = 0.5
            top_features = []

        training_time = (datetime.now() - start_time).total_seconds()

        results = {
            "cycle": cycle,
            "auc": auc,
            "accuracy": accuracy,
            "training_time": training_time,
            "data_size": len(cycle_data),
            "test_size": len(X_test),
            "top_features": top_features,
            "timestamp": datetime.now().isoformat(),
        }

        # Update best performance
        if auc > self.best_performance["auc"]:
            self.best_performance.update(
                {
                    "auc": auc,
                    "cycle": cycle,
                    "model_path": f"{self.models_dir}/best_model_cycle_{cycle}.pkl",
                }
            )

            # Save best model
            with open(self.best_performance["model_path"], "wb") as f:
                pickle.dump(model, f)

        return results

    def _encode_categorical_features(
        self, X: pd.DataFrame, cycle_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Encode categorical features"""
        # Simple encoding for categorical variables
        categorical_mappings = {
            "sex": {"Colt": 1, "Filly": 2, "Gelding": 3, "Mare": 4, "Stallion": 5},
            "track_condition": {
                "Firm": 1,
                "Good to Firm": 2,
                "Good": 3,
                "Good to Soft": 4,
                "Soft": 5,
                "Heavy": 6,
            },
            "weather": {
                "Sunny": 1,
                "Cloudy": 2,
                "Overcast": 3,
                "Light Rain": 4,
                "Heavy Rain": 5,
                "Windy": 6,
            },
            "track_type": {"Flat": 1, "National Hunt": 2, "All Weather": 3},
            "left_right_handed": {"Left": 1, "Right": 2, "Straight": 3},
        }

        for col, mapping in categorical_mappings.items():
            if col in cycle_data.columns:
                X[f"{col}_encoded"] = cycle_data[col].map(mapping).fillna(0)

        return X

    def _create_synthetic_races(self, cycle_data: pd.DataFrame) -> List[Dict]:
        """Create synthetic race data for ML system"""
        races = []

        # Group by race_id to create race structures
        race_groups = cycle_data.groupby("race_id")

        for race_id, race_df in race_groups:
            if len(race_df) < 2:  # Skip races with too few runners
                continue

            race_info = {
                "race_id": race_id,
                "race_name": race_df.iloc[0]["race_name"],
                "distance": race_df.iloc[0]["distance_meters"],
                "venue": race_df.iloc[0]["venue_name"],
                "participants": [],
            }

            for _, horse in race_df.iterrows():
                participant = {
                    "horse_name": horse["horse_name"],
                    "age": horse["age"],
                    "weight": horse["weight_lbs"],
                    "rating": horse["horse_rating"],
                    "form_rating": horse["form_rating"],
                    "jockey_skill": horse["jockey_skill"],
                    "trainer_skill": horse["trainer_skill"],
                    "odds": horse["odds_decimal"],
                    "draw": horse["draw"],
                    "finish_position": horse["actual_finish_position"],
                }
                race_info["participants"].append(participant)

            races.append(race_info)

            if len(races) >= 100:  # Limit for performance
                break

        return races

    def _evaluate_performance_interval(self, cycle: int):
        """Evaluate performance every interval"""
        logger.info(f"\n📈 PERFORMANCE EVALUATION - CYCLE {cycle}")
        logger.info("=" * 60)

        # Get recent performance
        recent_cycles = (
            self.cycle_results[-10:]
            if len(self.cycle_results) >= 10
            else self.cycle_results
        )

        # Calculate trends
        aucs = [r["auc"] for r in recent_cycles]
        accuracies = [r["accuracy"] for r in recent_cycles]
        training_times = [r["training_time"] for r in recent_cycles]

        avg_auc = np.mean(aucs)
        avg_accuracy = np.mean(accuracies)
        avg_time = np.mean(training_times)

        auc_trend = np.polyfit(range(len(aucs)), aucs, 1)[0] if len(aucs) > 1 else 0

        # Performance analysis
        logger.info(f"📊 RECENT PERFORMANCE (Last {len(recent_cycles)} cycles):")
        logger.info(f"   🎯 Average AUC: {avg_auc:.4f}")
        logger.info(f"   📊 Average Accuracy: {avg_accuracy:.4f}")
        logger.info(f"   ⏱️ Average Training Time: {avg_time:.2f}s")
        logger.info(f"   📈 AUC Trend: {auc_trend:+.6f} per cycle")

        logger.info(f"\n🏆 BEST PERFORMANCE:")
        logger.info(
            f"   🥇 Best AUC: {self.best_performance['auc']:.4f} "
            f"(Cycle {self.best_performance['cycle']})"
        )

        # Store performance history
        performance_summary = {
            "evaluation_cycle": cycle,
            "avg_auc": avg_auc,
            "avg_accuracy": avg_accuracy,
            "avg_training_time": avg_time,
            "auc_trend": auc_trend,
            "best_auc": self.best_performance["auc"],
            "best_cycle": self.best_performance["cycle"],
            "cycles_evaluated": len(recent_cycles),
        }

        self.performance_history.append(performance_summary)

        # Feature importance analysis
        if recent_cycles:
            self._analyze_feature_importance(recent_cycles)

        # Adaptive learning recommendations
        self._adaptive_learning_analysis(performance_summary)

    def _analyze_feature_importance(self, recent_cycles: List[Dict]):
        """Analyze feature importance trends"""
        logger.info(f"\n🔍 FEATURE IMPORTANCE ANALYSIS:")

        # Aggregate feature importance
        feature_importance_sum = {}
        feature_count = {}

        for cycle_result in recent_cycles:
            for feature, importance in cycle_result.get("top_features", []):
                if feature not in feature_importance_sum:
                    feature_importance_sum[feature] = 0
                    feature_count[feature] = 0
                feature_importance_sum[feature] += importance
                feature_count[feature] += 1

        # Calculate average importance
        avg_importance = {}
        for feature in feature_importance_sum:
            avg_importance[feature] = (
                feature_importance_sum[feature] / feature_count[feature]
            )

        # Top features
        top_avg_features = sorted(
            avg_importance.items(), key=lambda x: x[1], reverse=True
        )[:8]

        logger.info(f"   🔝 Top Features (averaged over {len(recent_cycles)} cycles):")
        for i, (feature, importance) in enumerate(top_avg_features, 1):
            logger.info(f"      {i}. {feature}: {importance:.4f}")

    def _adaptive_learning_analysis(self, performance_summary: Dict):
        """Analyze performance and suggest adaptive strategies"""
        logger.info(f"\n🧠 ADAPTIVE LEARNING ANALYSIS:")

        auc_trend = performance_summary["auc_trend"]
        avg_auc = performance_summary["avg_auc"]

        if auc_trend > 0.001:
            logger.info(f"   ✅ Positive trend detected (+{auc_trend:.6f}/cycle)")
            logger.info(f"   💡 Recommendation: Continue current strategy")
        elif auc_trend < -0.001:
            logger.info(f"   ⚠️ Negative trend detected ({auc_trend:.6f}/cycle)")
            logger.info(
                f"   💡 Recommendation: Consider data augmentation or feature engineering"
            )
        else:
            logger.info(f"   📊 Stable performance (trend: {auc_trend:.6f}/cycle)")
            logger.info(f"   💡 Recommendation: Monitor for plateau effects")

        if avg_auc > 0.95:
            logger.info(f"   🎯 Excellent performance level achieved")
            logger.info(f"   💡 Focus: Model robustness and generalization")
        elif avg_auc > 0.85:
            logger.info(f"   👍 Good performance level")
            logger.info(f"   💡 Focus: Feature optimization and hyperparameter tuning")
        else:
            logger.info(f"   📈 Room for improvement")
            logger.info(f"   💡 Focus: Data quality and feature engineering")

    def _save_checkpoint(self, cycle: int):
        """Save training checkpoint"""
        checkpoint_data = {
            "current_cycle": cycle,
            "cycle_results": self.cycle_results,
            "best_performance": self.best_performance,
            "performance_history": self.performance_history,
        }

        checkpoint_path = f"{self.results_dir}/checkpoint_cycle_{cycle}.json"
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        logger.info(f"💾 Checkpoint saved: {checkpoint_path}")

    def _final_evaluation(self):
        """Perform final evaluation and summary"""
        logger.info(f"\n🎊 FINAL EVALUATION SUMMARY")
        logger.info("=" * 60)

        if not self.cycle_results:
            logger.warning("No cycle results available for evaluation")
            return

        # Overall statistics
        all_aucs = [r["auc"] for r in self.cycle_results]
        all_accuracies = [r["accuracy"] for r in self.cycle_results]
        all_times = [r["training_time"] for r in self.cycle_results]

        logger.info(f"📊 OVERALL STATISTICS:")
        logger.info(f"   🔄 Total Cycles: {len(self.cycle_results)}")
        logger.info(
            f"   🎯 Average AUC: {np.mean(all_aucs):.4f} ± {np.std(all_aucs):.4f}"
        )
        logger.info(
            f"   📊 Average Accuracy: {np.mean(all_accuracies):.4f} ± {np.std(all_accuracies):.4f}"
        )
        logger.info(
            f"   ⏱️ Average Training Time: {np.mean(all_times):.2f}s ± {np.std(all_times):.2f}s"
        )

        logger.info(f"\n🏆 PERFORMANCE RECORDS:")
        logger.info(
            f"   🥇 Best AUC: {max(all_aucs):.4f} (Cycle {np.argmax(all_aucs) + 1})"
        )
        logger.info(
            f"   🥈 Best Accuracy: {max(all_accuracies):.4f} (Cycle {np.argmax(all_accuracies) + 1})"
        )
        logger.info(
            f"   ⚡ Fastest Training: {min(all_times):.2f}s (Cycle {np.argmin(all_times) + 1})"
        )

        # Performance trend analysis
        if len(all_aucs) > 10:
            early_auc = np.mean(all_aucs[:10])
            late_auc = np.mean(all_aucs[-10:])
            improvement = late_auc - early_auc

            logger.info(f"\n📈 LEARNING PROGRESSION:")
            logger.info(f"   🎯 Early Performance (First 10 cycles): {early_auc:.4f}")
            logger.info(f"   🎯 Late Performance (Last 10 cycles): {late_auc:.4f}")
            logger.info(f"   📊 Overall Improvement: {improvement:+.4f}")

        # Save final results
        final_results = {
            "training_completed": datetime.now().isoformat(),
            "total_cycles": len(self.cycle_results),
            "best_performance": self.best_performance,
            "overall_stats": {
                "mean_auc": np.mean(all_aucs),
                "std_auc": np.std(all_aucs),
                "mean_accuracy": np.mean(all_accuracies),
                "std_accuracy": np.std(all_accuracies),
                "mean_training_time": np.mean(all_times),
                "std_training_time": np.std(all_times),
            },
            "cycle_results": self.cycle_results,
            "performance_history": self.performance_history,
        }

        final_path = f"{self.results_dir}/final_training_results.json"
        with open(final_path, "w") as f:
            json.dump(final_results, f, indent=2)

        logger.info(f"\n💾 Final results saved: {final_path}")
        logger.info(f"🏆 Best model saved: {self.best_performance['model_path']}")

        logger.info(f"\n🎉 CYCLIC TRAINING SUCCESSFULLY COMPLETED!")


def main():
    """Main function to run cyclic ML training"""
    training_system = MLCyclicTrainingSystem()

    # Configuration
    TOTAL_CYCLES = 100
    EVALUATION_INTERVAL = 10

    logger.info("🚀 STARTING ML CYCLIC TRAINING SYSTEM")
    logger.info(
        f"🔧 Configuration: {TOTAL_CYCLES} cycles, evaluate every {EVALUATION_INTERVAL}"
    )

    # Generate training data (if needed)
    if not os.path.exists("training_cycles.db"):
        logger.info("📊 Generating training dataset...")
        training_system.generate_training_data(
            num_horses=15000, num_days=1095, start_date="2022-01-01"  # 3 years
        )

    # Run training cycles
    training_system.run_training_cycles(
        total_cycles=TOTAL_CYCLES,
        evaluation_interval=EVALUATION_INTERVAL,
        data_increment_pct=0.05,
    )


if __name__ == "__main__":
    main()
