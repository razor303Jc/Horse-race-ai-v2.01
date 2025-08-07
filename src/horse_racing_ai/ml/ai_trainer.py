#!/usr/bin/env python3
"""
AI Trainer for Horse Racing ML Models
====================================

Comprehensive AI training system that integrates:
- Enhanced ML models with ratings and Z-scores
- Monte Carlo simulation optimization
- Real-time performance tracking
- Automated model retraining
- Performance feedback loops
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import structlog
from sklearn.model_selection import ParameterGrid

from ..core.config import config
from ..scoring.composite_scorer import CompositeScore, CompositeScorer
from ..scoring.form_analyzer import EnhancedFormAnalyzer, RacePerformance
from ..scoring.power_ratings import PowerRatingSystem
from ..simulation.monte_carlo_simulator import MonteCarloAnalysis, MonteCarloSimulator
from .enhanced_ml_models import (
    AIPerformanceMetrics,
    EnhancedMLRatingSystem,
    MLModelPrediction,
    MonteCarloAIEnhancer,
    ZScoreMLPredictor,
)

logger = structlog.get_logger(__name__)


@dataclass
class TrainingSession:
    """Record of a training session."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    training_races: int
    validation_races: int
    models_trained: List[str]
    performance_metrics: Dict[str, float]
    improvement_metrics: Dict[str, float]
    session_notes: str
    status: str  # 'running', 'completed', 'failed'


@dataclass
class AITrainingPlan:
    """Comprehensive AI training plan."""

    plan_id: str
    objective: str
    target_metrics: Dict[str, float]
    training_schedule: Dict[str, Any]
    model_configurations: List[Dict[str, Any]]
    evaluation_criteria: Dict[str, float]
    expected_duration: timedelta
    priority: int


class AITrainer:
    """Comprehensive AI trainer for horse racing prediction systems."""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the AI trainer.

        Args:
            data_path: Path to training data directory
        """
        self.data_path = data_path or config.data_dir

        # Initialize components
        self.ml_system = EnhancedMLRatingSystem(enable_neural_networks=True)
        self.z_score_predictor = ZScoreMLPredictor()
        self.monte_carlo_enhancer = MonteCarloAIEnhancer()
        self.composite_scorer = CompositeScorer()
        self.form_analyzer = EnhancedFormAnalyzer()
        self.power_rating_system = PowerRatingSystem()
        self.monte_carlo_simulator = MonteCarloSimulator()

        # Training tracking
        self.training_sessions: List[TrainingSession] = []
        self.training_plans: List[AITrainingPlan] = []
        self.performance_history: List[Dict[str, Any]] = []

        # Configuration
        self.auto_retrain_threshold = 0.05  # Retrain if accuracy drops by 5%
        self.min_training_races = 1000
        self.validation_split = 0.2

        logger.info("AI Trainer initialized")

    async def load_and_prepare_training_data(self) -> pd.DataFrame:
        """Load and prepare comprehensive training data.

        Returns:
            Prepared training DataFrame
        """
        logger.info("Loading and preparing training data")

        # Load massive training data
        training_file = self.data_path / "massive_training_data.csv"
        if not training_file.exists():
            raise FileNotFoundError(f"Training data not found: {training_file}")

        # Load raw data
        raw_data = pd.read_csv(training_file)
        logger.info(f"Loaded {len(raw_data)} raw training records")

        # Prepare enhanced features
        prepared_data = await self._prepare_enhanced_training_features(raw_data)

        logger.info(
            f"Prepared {len(prepared_data)} training samples with {len(prepared_data.columns)} features"
        )
        return prepared_data

    async def _prepare_enhanced_training_features(
        self, raw_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Prepare enhanced features from raw training data.

        Args:
            raw_data: Raw training data

        Returns:
            Enhanced feature DataFrame
        """
        logger.info("Preparing enhanced training features")

        enhanced_features = []

        # Group by race for proper feature engineering
        races = raw_data.groupby(["race_date", "track", "race_number"])

        for race_key, race_data in races:
            race_date, track, race_number = race_key

            # Create race performances for each horse
            race_performances = []
            composite_scores = []

            for _, horse_row in race_data.iterrows():
                # Create RacePerformance object (simplified for training)
                try:
                    performance = RacePerformance(
                        horse_name=horse_row.get("horse_name", "Unknown"),
                        date=(
                            pd.to_datetime(race_date)
                            if isinstance(race_date, str)
                            else race_date
                        ),
                        track=track,
                        distance=horse_row.get("distance", 8.0),
                        finish_position=horse_row.get("finish_position", 5),
                        field_size=len(race_data),
                        beaten_lengths=horse_row.get("beaten_lengths", 2.0),
                        speed_figure=horse_row.get("speed_figure", 80),
                        jockey=horse_row.get("jockey", "Unknown"),
                        trainer=horse_row.get("trainer", "Unknown"),
                        odds=horse_row.get("odds", 5.0),
                        weight=horse_row.get("weight", 120),
                        conditions=horse_row.get("conditions", "Fast"),
                        surface=horse_row.get("surface", "dirt"),
                        race_class=horse_row.get("race_class", "ALLOWANCE"),
                        purse=horse_row.get("purse", 50000),
                        age=horse_row.get("age", 4),
                        sex=horse_row.get("sex", "G"),
                    )
                    race_performances.append(performance)

                    # Create composite score
                    composite_score = CompositeScore(
                        horse_name=horse_row.get("horse_name", "Unknown"),
                        composite_score=horse_row.get("composite_score", 75.0),
                        form_score=horse_row.get("form_score", 70.0),
                        power_rating=horse_row.get("power_rating", 100.0),
                        speed_score=horse_row.get("speed_score", 80.0),
                        class_score=horse_row.get("class_score", 75.0),
                        consistency_score=horse_row.get("consistency_score", 60.0),
                        conditions_score=horse_row.get("conditions_score", 70.0),
                        confidence_level=horse_row.get("confidence_level", 0.7),
                        factors=[],
                    )
                    composite_scores.append(composite_score)

                except Exception as e:
                    logger.warning(f"Error creating performance object: {e}")
                    continue

            if not race_performances:
                continue

            # Prepare race conditions
            race_conditions = {
                "distance": race_data.iloc[0].get("distance", 8.0),
                "surface": race_data.iloc[0].get("surface", "dirt"),
                "conditions": race_data.iloc[0].get("conditions", "Fast"),
                "race_class": race_data.iloc[0].get("race_class", "ALLOWANCE"),
                "field_size": len(race_data),
                "purse": race_data.iloc[0].get("purse", 50000),
            }

            # Generate features using ML system
            try:
                feature_df = self.ml_system.prepare_enhanced_features(
                    horse_data=[race_performances],  # Single race for each horse
                    composite_scores=composite_scores,
                    race_conditions=race_conditions,
                )

                # Add target variables
                for i, (_, horse_row) in enumerate(race_data.iterrows()):
                    if i < len(feature_df):
                        # Target rating (can be composite score or actual performance rating)
                        target_rating = horse_row.get(
                            "target_rating", horse_row.get("composite_score", 75.0)
                        )
                        feature_df.loc[i, "target_rating"] = target_rating

                        # Target finish position
                        feature_df.loc[i, "target_position"] = horse_row.get(
                            "finish_position", 5
                        )

                        # Won race (binary target)
                        feature_df.loc[i, "target_won"] = (
                            1 if horse_row.get("finish_position", 5) == 1 else 0
                        )

                        # Placed (top 3)
                        feature_df.loc[i, "target_placed"] = (
                            1 if horse_row.get("finish_position", 5) <= 3 else 0
                        )

                        # Add metadata
                        feature_df.loc[i, "race_date"] = race_date
                        feature_df.loc[i, "track"] = track
                        feature_df.loc[i, "race_number"] = race_number
                        feature_df.loc[i, "horse_name"] = horse_row.get(
                            "horse_name", "Unknown"
                        )

                enhanced_features.append(feature_df)

            except Exception as e:
                logger.warning(f"Error processing race {race_key}: {e}")
                continue

            # Progress logging
            if len(enhanced_features) % 100 == 0:
                logger.info(f"Processed {len(enhanced_features)} races...")

        # Combine all features
        if enhanced_features:
            combined_features = pd.concat(enhanced_features, ignore_index=True)
            logger.info(
                f"Created enhanced features for {len(combined_features)} horses from {len(enhanced_features)} races"
            )
            return combined_features
        else:
            raise ValueError("No valid training features could be created")

    async def train_comprehensive_ml_system(
        self,
        training_data: Optional[pd.DataFrame] = None,
        retrain_existing: bool = False,
    ) -> TrainingSession:
        """Train the comprehensive ML system.

        Args:
            training_data: Optional pre-loaded training data
            retrain_existing: Whether to retrain existing models

        Returns:
            Training session record
        """
        session_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TrainingSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            training_races=0,
            validation_races=0,
            models_trained=[],
            performance_metrics={},
            improvement_metrics={},
            session_notes="Comprehensive ML system training",
            status="running",
        )

        self.training_sessions.append(session)
        logger.info(f"Starting training session: {session_id}")

        try:
            # Load training data if not provided
            if training_data is None:
                training_data = await self.load_and_prepare_training_data()

            # Split data by race (not by individual horses)
            race_groups = training_data.groupby(["race_date", "track", "race_number"])
            race_keys = list(race_groups.groups.keys())

            # Split races for training/validation
            split_point = int(len(race_keys) * (1 - self.validation_split))
            train_race_keys = race_keys[:split_point]
            val_race_keys = race_keys[split_point:]

            # Create training and validation datasets
            train_indices = []
            val_indices = []

            for race_key in train_race_keys:
                train_indices.extend(race_groups.get_group(race_key).index.tolist())

            for race_key in val_race_keys:
                val_indices.extend(race_groups.get_group(race_key).index.tolist())

            train_data = training_data.loc[train_indices]
            val_data = training_data.loc[val_indices]

            session.training_races = len(train_race_keys)
            session.validation_races = len(val_race_keys)

            logger.info(
                f"Training on {len(train_data)} horses from {session.training_races} races"
            )
            logger.info(
                f"Validating on {len(val_data)} horses from {session.validation_races} races"
            )

            # 1. Train main ML rating system
            logger.info("Training enhanced ML rating system...")
            rating_performance = self.ml_system.train_models(
                training_data=train_data,
                target_column="target_rating",
                validation_split=0.0,  # Already split by races
            )

            session.models_trained.append("enhanced_ml_rating")

            # Store performance metrics
            for model_name, metrics in rating_performance.items():
                session.performance_metrics[f"rating_{model_name}_r2"] = (
                    metrics.r2_score
                )
                session.performance_metrics[f"rating_{model_name}_rmse"] = metrics.rmse
                session.performance_metrics[f"rating_{model_name}_mae"] = metrics.mae

            # 2. Train Z-score predictor
            logger.info("Training Z-score predictor...")
            if len(train_data) > 100:  # Ensure sufficient data
                # Prepare Z-score training data
                z_ratings = train_data["target_rating"].tolist()
                z_contexts = []
                z_actuals = []

                for race_key in train_race_keys[
                    :500
                ]:  # Use subset for Z-score training
                    race_group = race_groups.get_group(race_key)
                    if len(race_group) > 3:  # Need reasonable field size
                        ratings = race_group["target_rating"].values
                        mean_rating = np.mean(ratings)
                        std_rating = max(np.std(ratings), 1.0)
                        z_scores = (ratings - mean_rating) / std_rating

                        for i, rating in enumerate(ratings):
                            z_ratings.append(rating)
                            z_contexts.append(
                                {
                                    "field_size": len(race_group),
                                    "avg_field_rating": mean_rating,
                                    "field_strength": std_rating,
                                    "race_competitiveness": min(std_rating / 10.0, 1.0),
                                }
                            )
                            z_actuals.append(z_scores[i])

                if len(z_actuals) > 50:
                    z_accuracy = self.z_score_predictor.train_z_score_model(
                        z_ratings, z_contexts, z_actuals
                    )
                    session.models_trained.append("z_score_predictor")
                    session.performance_metrics["z_score_accuracy"] = z_accuracy

            # 3. Optimize Monte Carlo parameters
            logger.info("Optimizing Monte Carlo parameters...")
            mc_params = self.monte_carlo_enhancer.optimize_simulation_parameters(
                historical_results=[],  # Would be filled with actual results
                simulation_configs=[],  # Would be filled with tested configs
            )
            session.models_trained.append("monte_carlo_optimizer")
            session.performance_metrics["mc_optimization"] = 1.0  # Placeholder

            # 4. Validate overall system performance
            logger.info("Validating overall system performance...")
            validation_metrics = await self._validate_system_performance(val_data)
            session.performance_metrics.update(validation_metrics)

            # 5. Save trained models
            model_path = self.ml_system.save_enhanced_models(
                f"comprehensive_{session_id}"
            )
            logger.info(f"Models saved to: {model_path}")

            # Complete session
            session.end_time = datetime.now()
            session.status = "completed"
            session.session_notes += f" | Models saved to {model_path.name}"

            logger.info(f"Training session {session_id} completed successfully")

            return session

        except Exception as e:
            session.end_time = datetime.now()
            session.status = "failed"
            session.session_notes += f" | Error: {str(e)}"
            logger.error(f"Training session {session_id} failed: {e}")
            raise

    async def _validate_system_performance(
        self, validation_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Validate the overall system performance.

        Args:
            validation_data: Validation dataset

        Returns:
            Dictionary of validation metrics
        """
        logger.info("Validating system performance on held-out data")

        metrics = {}

        # Group validation data by race
        race_groups = validation_data.groupby(["race_date", "track", "race_number"])

        total_races = 0
        correct_winners = 0
        correct_placers = 0
        total_predictions = 0

        for race_key, race_data in race_groups:
            if len(race_data) < 3:  # Skip small fields
                continue

            try:
                # Create simplified objects for prediction
                composite_scores = []
                for _, horse_row in race_data.iterrows():
                    score = CompositeScore(
                        horse_name=horse_row["horse_name"],
                        composite_score=horse_row.get("composite_score", 75.0),
                        form_score=horse_row.get("form_score", 70.0),
                        power_rating=horse_row.get("power_rating", 100.0),
                        speed_score=horse_row.get("speed_score", 80.0),
                        class_score=horse_row.get("class_score", 75.0),
                        consistency_score=horse_row.get("consistency_score", 60.0),
                        conditions_score=horse_row.get("conditions_score", 70.0),
                        confidence_level=horse_row.get("confidence_level", 0.7),
                        factors=[],
                    )
                    composite_scores.append(score)

                # Create race conditions
                race_conditions = {
                    "distance": race_data.iloc[0].get("distance", 8.0),
                    "surface": race_data.iloc[0].get("surface", "dirt"),
                    "field_size": len(race_data),
                }

                # Get predictions (simplified without full performance history)
                predictions = self.ml_system.predict_race_with_ml(
                    horse_data=[],  # Empty for validation
                    composite_scores=composite_scores,
                    race_conditions=race_conditions,
                )

                # Check predictions against actual results
                actual_winner = (
                    race_data[race_data["target_position"] == 1]["horse_name"].iloc[0]
                    if len(race_data[race_data["target_position"] == 1]) > 0
                    else None
                )
                actual_placers = race_data[race_data["target_position"] <= 3][
                    "horse_name"
                ].tolist()

                # Find predicted winner (highest win probability)
                if predictions:
                    predicted_winner = max(predictions, key=lambda p: p.win_probability)

                    if predicted_winner.horse_name == actual_winner:
                        correct_winners += 1

                    # Check place predictions (top 3 by win probability)
                    top_3_predictions = sorted(
                        predictions, key=lambda p: p.win_probability, reverse=True
                    )[:3]
                    predicted_placers = [p.horse_name for p in top_3_predictions]

                    # Count how many predicted placers actually placed
                    correct_place_count = len(
                        set(predicted_placers) & set(actual_placers)
                    )
                    if correct_place_count >= 2:  # At least 2 out of 3 correct
                        correct_placers += 1

                total_races += 1
                total_predictions += len(predictions) if predictions else 0

                if total_races % 50 == 0:
                    logger.info(f"Validated {total_races} races...")

            except Exception as e:
                logger.warning(f"Error validating race {race_key}: {e}")
                continue

        # Calculate metrics
        if total_races > 0:
            metrics["win_accuracy"] = correct_winners / total_races
            metrics["place_accuracy"] = correct_placers / total_races
            metrics["overall_accuracy"] = (correct_winners + correct_placers) / (
                total_races * 2
            )
            metrics["total_validation_races"] = total_races
            metrics["total_validation_predictions"] = total_predictions

        logger.info(f"Validation complete: {metrics}")
        return metrics

    async def create_training_plan(
        self, objective: str, target_accuracy: float = 0.65, priority: int = 1
    ) -> AITrainingPlan:
        """Create a comprehensive AI training plan.

        Args:
            objective: Training objective description
            target_accuracy: Target accuracy to achieve
            priority: Priority level (1-10)

        Returns:
            AI training plan
        """
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = AITrainingPlan(
            plan_id=plan_id,
            objective=objective,
            target_metrics={
                "win_accuracy": target_accuracy,
                "place_accuracy": target_accuracy + 0.1,
                "overall_accuracy": target_accuracy + 0.05,
            },
            training_schedule={
                "initial_training": "comprehensive",
                "retraining_frequency": "weekly",
                "validation_frequency": "daily",
                "performance_monitoring": "continuous",
            },
            model_configurations=[
                {"name": "enhanced_ml", "type": "ensemble", "priority": 1},
                {"name": "z_score_predictor", "type": "specialized", "priority": 2},
                {"name": "monte_carlo_optimizer", "type": "simulation", "priority": 3},
            ],
            evaluation_criteria={
                "accuracy_improvement": 0.02,
                "consistency_requirement": 0.9,
                "confidence_threshold": 0.7,
            },
            expected_duration=timedelta(hours=4),
            priority=priority,
        )

        self.training_plans.append(plan)
        logger.info(f"Created training plan: {plan_id}")

        return plan

    async def monitor_ai_performance(self) -> Dict[str, Any]:
        """Monitor AI performance and trigger retraining if needed.

        Returns:
            Performance monitoring report
        """
        logger.info("Monitoring AI performance")

        # Get current AI metrics
        ai_metrics = self.ml_system.get_ai_performance_report()

        # Check if retraining is needed
        needs_retraining = False
        reasons = []

        if ai_metrics["win_accuracy"] < 0.25:
            needs_retraining = True
            reasons.append("Win accuracy below threshold")

        if ai_metrics["average_accuracy"] < 0.4:
            needs_retraining = True
            reasons.append("Overall accuracy declining")

        # Check recent performance trend
        if ai_metrics["performance_trend"]:
            recent_accuracies = [
                entry["accuracy"] for entry in ai_metrics["performance_trend"][-5:]
            ]
            if len(recent_accuracies) >= 3:
                trend = np.polyfit(range(len(recent_accuracies)), recent_accuracies, 1)[
                    0
                ]
                if trend < -0.02:  # Declining trend
                    needs_retraining = True
                    reasons.append("Performance trend declining")

        monitoring_report = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": ai_metrics,
            "needs_retraining": needs_retraining,
            "retraining_reasons": reasons,
            "last_training_session": (
                self.training_sessions[-1].session_id
                if self.training_sessions
                else None
            ),
            "recommendation": "retrain" if needs_retraining else "continue_monitoring",
        }

        # Store performance history
        self.performance_history.append(monitoring_report)

        logger.info(
            f"Performance monitoring complete. Needs retraining: {needs_retraining}"
        )

        return monitoring_report

    async def auto_retrain_if_needed(self) -> Optional[TrainingSession]:
        """Automatically retrain models if performance has degraded.

        Returns:
            Training session if retraining was triggered, None otherwise
        """
        logger.info("Checking if automatic retraining is needed")

        # Monitor performance
        monitoring_report = await self.monitor_ai_performance()

        if monitoring_report["needs_retraining"]:
            logger.info(
                "Performance degradation detected, triggering automatic retraining"
            )

            # Create retraining plan
            plan = await self.create_training_plan(
                objective="Automatic retraining due to performance degradation",
                target_accuracy=0.6,
                priority=10,  # High priority
            )

            # Execute retraining
            session = await self.train_comprehensive_ml_system(retrain_existing=True)

            logger.info(f"Automatic retraining completed: {session.session_id}")
            return session
        else:
            logger.info("No retraining needed at this time")
            return None

    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary.

        Returns:
            Training summary report
        """
        summary = {
            "total_training_sessions": len(self.training_sessions),
            "successful_sessions": len(
                [s for s in self.training_sessions if s.status == "completed"]
            ),
            "failed_sessions": len(
                [s for s in self.training_sessions if s.status == "failed"]
            ),
            "active_training_plans": len([p for p in self.training_plans]),
            "performance_history_length": len(self.performance_history),
            "system_status": "trained" if self.ml_system.is_trained else "untrained",
            "last_training": (
                self.training_sessions[-1].start_time.isoformat()
                if self.training_sessions
                else None
            ),
            "models_available": (
                list(self.ml_system.models.keys()) if self.ml_system.is_trained else []
            ),
            "current_ai_metrics": (
                self.ml_system.ai_metrics
                if hasattr(self.ml_system, "ai_metrics")
                else {}
            ),
        }

        # Add recent performance if available
        if self.performance_history:
            recent_performance = self.performance_history[-1]
            summary["recent_performance"] = {
                "timestamp": recent_performance["timestamp"],
                "needs_retraining": recent_performance["needs_retraining"],
                "win_accuracy": recent_performance["current_metrics"].get(
                    "win_accuracy", 0.0
                ),
                "place_accuracy": recent_performance["current_metrics"].get(
                    "place_accuracy", 0.0
                ),
            }

        return summary

    async def save_training_state(self, filepath: Optional[Path] = None) -> Path:
        """Save the complete training state.

        Args:
            filepath: Optional path to save state

        Returns:
            Path to saved state file
        """
        if filepath is None:
            filepath = (
                config.models_dir
                / f"training_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        state_data = {
            "training_sessions": [
                asdict(session) for session in self.training_sessions
            ],
            "training_plans": [asdict(plan) for plan in self.training_plans],
            "performance_history": self.performance_history,
            "config": {
                "auto_retrain_threshold": self.auto_retrain_threshold,
                "min_training_races": self.min_training_races,
                "validation_split": self.validation_split,
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Convert datetime objects to strings for JSON serialization
        for session in state_data["training_sessions"]:
            if session["start_time"]:
                session["start_time"] = (
                    session["start_time"].isoformat()
                    if isinstance(session["start_time"], datetime)
                    else session["start_time"]
                )
            if session["end_time"]:
                session["end_time"] = (
                    session["end_time"].isoformat()
                    if isinstance(session["end_time"], datetime)
                    else session["end_time"]
                )

        for plan in state_data["training_plans"]:
            if plan["expected_duration"]:
                plan["expected_duration"] = str(plan["expected_duration"])

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(state_data, f, indent=2, default=str)

        logger.info(f"Training state saved to {filepath}")
        return filepath

    async def load_training_state(self, filepath: Path) -> None:
        """Load previously saved training state.

        Args:
            filepath: Path to saved state file
        """
        logger.info(f"Loading training state from {filepath}")

        with open(filepath, "r") as f:
            state_data = json.load(f)

        # Restore training sessions
        self.training_sessions = []
        for session_data in state_data.get("training_sessions", []):
            session = TrainingSession(
                session_id=session_data["session_id"],
                start_time=(
                    datetime.fromisoformat(session_data["start_time"])
                    if session_data.get("start_time")
                    else datetime.now()
                ),
                end_time=(
                    datetime.fromisoformat(session_data["end_time"])
                    if session_data.get("end_time")
                    else None
                ),
                training_races=session_data.get("training_races", 0),
                validation_races=session_data.get("validation_races", 0),
                models_trained=session_data.get("models_trained", []),
                performance_metrics=session_data.get("performance_metrics", {}),
                improvement_metrics=session_data.get("improvement_metrics", {}),
                session_notes=session_data.get("session_notes", ""),
                status=session_data.get("status", "unknown"),
            )
            self.training_sessions.append(session)

        # Restore training plans
        self.training_plans = []
        for plan_data in state_data.get("training_plans", []):
            # Convert expected_duration back from string
            duration_str = plan_data.get("expected_duration", "4:00:00")
            if isinstance(duration_str, str):
                # Parse duration string (format: HH:MM:SS or days, HH:MM:SS)
                if "," in duration_str:
                    days_part, time_part = duration_str.split(", ")
                    days = int(days_part.split()[0])
                    hours, minutes, seconds = map(int, time_part.split(":"))
                    expected_duration = timedelta(
                        days=days, hours=hours, minutes=minutes, seconds=seconds
                    )
                else:
                    hours, minutes, seconds = map(int, duration_str.split(":"))
                    expected_duration = timedelta(
                        hours=hours, minutes=minutes, seconds=seconds
                    )
            else:
                expected_duration = timedelta(hours=4)  # Default

            plan = AITrainingPlan(
                plan_id=plan_data["plan_id"],
                objective=plan_data.get("objective", ""),
                target_metrics=plan_data.get("target_metrics", {}),
                training_schedule=plan_data.get("training_schedule", {}),
                model_configurations=plan_data.get("model_configurations", []),
                evaluation_criteria=plan_data.get("evaluation_criteria", {}),
                expected_duration=expected_duration,
                priority=plan_data.get("priority", 1),
            )
            self.training_plans.append(plan)

        # Restore performance history
        self.performance_history = state_data.get("performance_history", [])

        # Restore configuration
        config_data = state_data.get("config", {})
        self.auto_retrain_threshold = config_data.get("auto_retrain_threshold", 0.05)
        self.min_training_races = config_data.get("min_training_races", 1000)
        self.validation_split = config_data.get("validation_split", 0.2)

        logger.info(
            f"Training state loaded: {len(self.training_sessions)} sessions, {len(self.training_plans)} plans"
        )


# Convenience function for quick training
async def quick_train_ai_system(data_path: Optional[Path] = None) -> TrainingSession:
    """Quick training function for the AI system.

    Args:
        data_path: Optional path to training data

    Returns:
        Training session result
    """
    trainer = AITrainer(data_path)

    logger.info("Starting quick AI system training")

    # Create training plan
    plan = await trainer.create_training_plan(
        objective="Quick comprehensive AI training", target_accuracy=0.6, priority=5
    )

    # Execute training
    session = await trainer.train_comprehensive_ml_system()

    logger.info(f"Quick training completed: {session.session_id}")
    return session
