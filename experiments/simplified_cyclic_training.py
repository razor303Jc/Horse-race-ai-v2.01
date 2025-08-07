#!/usr/bin/env python3
"""
Simplified Cyclic Training System
A streamlined version focusing on core ML training with cycle monitoring.
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from massive_dataset_generator import MassiveDatasetGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplifiedCyclicTraining:
    """
    Simplified cyclic training system with focus on:
    - Progressive data loading
    - Model training and evaluation
    - Performance monitoring every N cycles
    - Comprehensive metrics tracking
    """

    def __init__(self, db_path: str = "simplified_training.db"):
        self.db_path = db_path
        self.cycle_results = []
        self.best_performance = {"auc": 0.0, "cycle": 0}

        logger.info("🎯 Simplified Cyclic Training System initialized")

    def generate_training_data(
        self,
        num_horses: int = 5000,
        num_days: int = 365,
        start_date: str = "2023-01-01",
    ):
        """Generate training dataset"""
        logger.info("🏗️ GENERATING TRAINING DATASET")
        logger.info("=" * 50)

        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        # Generate data
        generator = MassiveDatasetGenerator(db_path=self.db_path)
        generator.generate_complete_dataset(
            num_horses=num_horses, start_date=start_date, num_days=num_days
        )

        logger.info("✅ Training dataset generated")

    def load_and_prepare_data(self) -> pd.DataFrame:
        """Load and prepare data for training"""
        conn = sqlite3.connect(self.db_path)

        # Simplified query with essential features
        query = """
        SELECT 
            rp.horse_id,
            rp.race_id,
            rp.actual_finish_position,
            rp.odds_decimal,
            rp.weight_lbs,
            rp.draw,
            rp.days_since_last_run,
            rp.course_wins,
            rp.distance_wins,
            rp.course_and_distance_wins,
            h.age,
            h.rating as horse_rating,
            h.form_rating,
            h.career_wins,
            h.career_runs,
            h.sex,
            j.skill_rating as jockey_skill,
            j.win_percentage as jockey_win_pct,
            t.skill_rating as trainer_skill,
            t.win_percentage as trainer_win_pct,
            rc.distance_meters,
            rc.num_runners,
            rc.prize_money,
            rc.track_condition,
            rc.weather
        FROM race_participants rp
        JOIN horses h ON rp.horse_id = h.horse_id
        JOIN jockeys j ON rp.jockey_id = j.jockey_id
        JOIN trainers t ON rp.trainer_id = t.trainer_id
        JOIN race_cards rc ON rp.race_id = rc.race_id
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Create target variable
        df["win"] = (df["actual_finish_position"] == 1).astype(int)

        # Create additional features
        df["career_win_rate"] = df["career_wins"] / df["career_runs"].clip(lower=1)
        df["odds_probability"] = 1 / df["odds_decimal"]
        df["weight_rating_ratio"] = df["weight_lbs"] / df["horse_rating"].clip(lower=1)

        # Encode categorical variables
        le_sex = LabelEncoder()
        le_condition = LabelEncoder()
        le_weather = LabelEncoder()

        df["sex_encoded"] = le_sex.fit_transform(df["sex"].astype(str))
        df["condition_encoded"] = le_condition.fit_transform(
            df["track_condition"].astype(str)
        )
        df["weather_encoded"] = le_weather.fit_transform(df["weather"].astype(str))

        logger.info(f"📊 Data prepared: {len(df):,} training examples")
        logger.info(f"   🏆 Win rate: {df['win'].mean():.2%}")

        return df

    def run_training_cycles(
        self, total_cycles: int = 100, evaluation_interval: int = 10
    ):
        """Run training cycles with progressive data loading"""
        logger.info("🚀 STARTING CYCLIC TRAINING")
        logger.info("=" * 50)
        logger.info(f"   🔄 Total Cycles: {total_cycles}")
        logger.info(f"   📊 Evaluation Interval: {evaluation_interval}")

        # Load complete dataset
        df = self.load_and_prepare_data()

        # Feature columns
        feature_cols = [
            "horse_rating",
            "form_rating",
            "age",
            "career_wins",
            "career_runs",
            "career_win_rate",
            "weight_lbs",
            "weight_rating_ratio",
            "draw",
            "odds_decimal",
            "odds_probability",
            "days_since_last_run",
            "course_wins",
            "distance_wins",
            "course_and_distance_wins",
            "jockey_skill",
            "jockey_win_pct",
            "trainer_skill",
            "trainer_win_pct",
            "distance_meters",
            "num_runners",
            "prize_money",
            "sex_encoded",
            "condition_encoded",
            "weather_encoded",
        ]

        # Run cycles
        for cycle in range(1, total_cycles + 1):
            logger.info(f"\n🔄 CYCLE {cycle}/{total_cycles}")
            logger.info("-" * 30)

            # Progressive data sampling
            data_fraction = self._calculate_data_fraction(cycle, total_cycles)
            cycle_data = self._sample_cycle_data(df, data_fraction, cycle)

            # Train and evaluate
            results = self._train_and_evaluate(cycle_data, feature_cols, cycle)

            # Store results
            self.cycle_results.append(results)

            # Update best performance
            if results["auc"] > self.best_performance["auc"]:
                self.best_performance.update(
                    {
                        "auc": results["auc"],
                        "cycle": cycle,
                        "accuracy": results["accuracy"],
                    }
                )

            # Log cycle results
            logger.info(f"   🎯 AUC: {results['auc']:.4f}")
            logger.info(f"   📊 Accuracy: {results['accuracy']:.4f}")
            logger.info(f"   📈 Data Size: {results['data_size']:,}")

            # Evaluation every interval
            if cycle % evaluation_interval == 0:
                self._evaluate_performance_interval(cycle, evaluation_interval)

        # Final evaluation
        self._final_evaluation()

    def _calculate_data_fraction(self, cycle: int, total_cycles: int) -> float:
        """Calculate data fraction for current cycle"""
        if cycle <= 10:
            # Start with 10%, increase to 50% over first 10 cycles
            return 0.1 + (cycle - 1) * 0.04
        else:
            # Gradually increase to 100% over remaining cycles
            remaining_cycles = total_cycles - 10
            progress = (cycle - 10) / remaining_cycles
            return 0.5 + progress * 0.5

    def _sample_cycle_data(
        self, df: pd.DataFrame, data_fraction: float, cycle: int
    ) -> pd.DataFrame:
        """Sample data for current cycle"""
        sample_size = int(len(df) * data_fraction)

        # Use different sampling strategies
        if cycle <= 20:
            # Random sampling for early cycles
            return df.sample(n=sample_size, random_state=cycle)
        else:
            # Stratified sampling to maintain win rate
            wins = df[df["win"] == 1]
            losses = df[df["win"] == 0]

            win_sample_size = int(sample_size * df["win"].mean())
            loss_sample_size = sample_size - win_sample_size

            win_sample = wins.sample(
                n=min(win_sample_size, len(wins)), random_state=cycle
            )
            loss_sample = losses.sample(
                n=min(loss_sample_size, len(losses)), random_state=cycle
            )

            return pd.concat([win_sample, loss_sample]).sample(
                frac=1, random_state=cycle
            )

    def _train_and_evaluate(
        self, cycle_data: pd.DataFrame, feature_cols: List[str], cycle: int
    ) -> Dict[str, Any]:
        """Train model and evaluate performance"""
        start_time = datetime.now()

        # Prepare features and target
        X = cycle_data[feature_cols].fillna(0)
        y = cycle_data["win"]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=cycle, stratify=y
        )

        # Train models (ensemble approach)
        models = {
            "extra_trees": ExtraTreesClassifier(
                n_estimators=100, max_depth=12, random_state=cycle, n_jobs=-1
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=cycle, n_jobs=-1
            ),
        }

        best_auc = 0
        best_model = None
        best_model_name = ""

        for model_name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                auc = roc_auc_score(y_test, y_pred_proba)

                if auc > best_auc:
                    best_auc = auc
                    best_model = model
                    best_model_name = model_name

            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        # Final predictions with best model
        if best_model is not None:
            y_pred_proba = best_model.predict_proba(X_test)[:, 1]
            y_pred = best_model.predict(X_test)

            auc = roc_auc_score(y_test, y_pred_proba)
            accuracy = accuracy_score(y_test, y_pred)

            # Feature importance
            feature_importance = dict(
                zip(feature_cols, best_model.feature_importances_)
            )
            top_features = sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            )[:5]
        else:
            auc = 0.5
            accuracy = 0.5
            top_features = []
            best_model_name = "none"

        training_time = (datetime.now() - start_time).total_seconds()

        return {
            "cycle": cycle,
            "auc": auc,
            "accuracy": accuracy,
            "training_time": training_time,
            "data_size": len(cycle_data),
            "test_size": len(X_test),
            "best_model": best_model_name,
            "top_features": top_features,
            "win_rate": y.mean(),
        }

    def _evaluate_performance_interval(self, cycle: int, interval: int):
        """Evaluate performance over interval"""
        logger.info(f"\n📊 PERFORMANCE EVALUATION - CYCLE {cycle}")
        logger.info("=" * 50)

        # Get recent cycles
        recent_cycles = self.cycle_results[-interval:]

        # Calculate metrics
        aucs = [r["auc"] for r in recent_cycles]
        accuracies = [r["accuracy"] for r in recent_cycles]
        times = [r["training_time"] for r in recent_cycles]

        logger.info(f"📈 RECENT PERFORMANCE (Last {len(recent_cycles)} cycles):")
        logger.info(f"   🎯 Average AUC: {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")
        logger.info(
            f"   📊 Average Accuracy: {np.mean(accuracies):.4f} ± {np.std(accuracies):.4f}"
        )
        logger.info(f"   ⏱️ Average Time: {np.mean(times):.2f}s ± {np.std(times):.2f}s")

        logger.info(f"\n🏆 BEST PERFORMANCE:")
        logger.info(
            f"   🥇 Best AUC: {self.best_performance['auc']:.4f} "
            f"(Cycle {self.best_performance['cycle']})"
        )

        # Performance trend
        if len(aucs) > 3:
            trend = np.polyfit(range(len(aucs)), aucs, 1)[0]
            logger.info(f"   📈 AUC Trend: {trend:+.6f} per cycle")

            if trend > 0.001:
                logger.info("   ✅ Positive learning trend detected")
            elif trend < -0.001:
                logger.info("   ⚠️ Performance declining - consider adjustments")
            else:
                logger.info("   📊 Stable performance")

        # Feature analysis
        self._analyze_feature_trends(recent_cycles)

    def _analyze_feature_trends(self, recent_cycles: List[Dict]):
        """Analyze feature importance trends"""
        logger.info(f"\n🔍 FEATURE IMPORTANCE ANALYSIS:")

        # Aggregate feature importance
        feature_scores = {}
        for cycle_result in recent_cycles:
            for feature, score in cycle_result.get("top_features", []):
                if feature not in feature_scores:
                    feature_scores[feature] = []
                feature_scores[feature].append(score)

        # Average importance
        avg_importance = {}
        for feature, scores in feature_scores.items():
            avg_importance[feature] = np.mean(scores)

        # Top features
        top_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[
            :8
        ]

        logger.info(f"   🔝 Top Features (avg over {len(recent_cycles)} cycles):")
        for i, (feature, importance) in enumerate(top_features, 1):
            logger.info(f"      {i}. {feature}: {importance:.4f}")

    def _final_evaluation(self):
        """Final evaluation and summary"""
        logger.info(f"\n🎊 FINAL EVALUATION")
        logger.info("=" * 50)

        # Overall statistics
        aucs = [r["auc"] for r in self.cycle_results]
        accuracies = [r["accuracy"] for r in self.cycle_results]
        times = [r["training_time"] for r in self.cycle_results]

        logger.info(f"📊 OVERALL STATISTICS:")
        logger.info(f"   🔄 Total Cycles: {len(self.cycle_results)}")
        logger.info(f"   🎯 Average AUC: {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")
        logger.info(
            f"   📊 Average Accuracy: {np.mean(accuracies):.4f} ± {np.std(accuracies):.4f}"
        )
        logger.info(f"   ⏱️ Average Time: {np.mean(times):.2f}s ± {np.std(times):.2f}s")

        logger.info(f"\n🏆 PERFORMANCE RECORDS:")
        logger.info(
            f"   🥇 Best AUC: {max(aucs):.4f} (Cycle {aucs.index(max(aucs)) + 1})"
        )
        logger.info(
            f"   🥈 Best Accuracy: {max(accuracies):.4f} (Cycle {accuracies.index(max(accuracies)) + 1})"
        )

        # Learning progression
        if len(aucs) >= 20:
            early_auc = np.mean(aucs[:10])
            late_auc = np.mean(aucs[-10:])
            improvement = late_auc - early_auc

            logger.info(f"\n📈 LEARNING PROGRESSION:")
            logger.info(f"   🎯 Early AUC (first 10): {early_auc:.4f}")
            logger.info(f"   🎯 Late AUC (last 10): {late_auc:.4f}")
            logger.info(f"   📊 Improvement: {improvement:+.4f}")

        # Save results
        results = {
            "completed": datetime.now().isoformat(),
            "cycles": self.cycle_results,
            "best_performance": self.best_performance,
            "summary_stats": {
                "mean_auc": np.mean(aucs),
                "std_auc": np.std(aucs),
                "max_auc": max(aucs),
                "mean_accuracy": np.mean(accuracies),
                "std_accuracy": np.std(accuracies),
            },
        }

        with open("cyclic_training_results.json", "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n💾 Results saved to: cyclic_training_results.json")
        logger.info(f"🎉 CYCLIC TRAINING COMPLETE!")


def main():
    """Main function"""
    trainer = SimplifiedCyclicTraining()

    # Generate data if needed
    if not os.path.exists("simplified_training.db"):
        trainer.generate_training_data(
            num_horses=2000, num_days=365, start_date="2023-01-01"
        )

    # Run training
    trainer.run_training_cycles(total_cycles=100, evaluation_interval=10)


if __name__ == "__main__":
    main()
