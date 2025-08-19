#!/usr/bin/env python3
"""
Automated Model Retraining System for Horse Racing AI V2.03
Manages automated model lifecycle with performance monitoring and retraining
"""

import os
import sys
import json
import logging
import asyncio
import sqlite3
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import shutil
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Model performance metrics"""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    cross_val_score: float
    sample_count: int
    timestamp: datetime


@dataclass
class ModelConfig:
    """Model configuration for retraining"""

    model_name: str
    model_type: str  # 'random_forest', 'logistic_regression'
    target_column: str
    feature_columns: List[str]
    hyperparameters: Dict[str, Any]
    retraining_threshold: float  # Performance threshold for retraining
    min_samples: int
    validation_split: float


@dataclass
class RetrainingJob:
    """Retraining job configuration"""

    job_id: str
    model_name: str
    scheduled_time: datetime
    status: str  # 'pending', 'running', 'completed', 'failed'
    trigger_reason: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    metrics_before: Optional[ModelMetrics]
    metrics_after: Optional[ModelMetrics]


class AutomatedModelRetrainer:
    """
    Automated Model Retraining System
    Monitors model performance and automatically retrain when needed
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Automated Model Retrainer"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.models_dir = Path(self.config.get("models_directory", "models"))
        self.backup_dir = Path(self.config.get("backup_directory", "models/backup"))

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Model configurations
        self.model_configs = self._initialize_model_configs()

        # Performance tracking
        self.performance_history = {}

        # Job queue
        self.retraining_queue = []

        # Statistics
        self.stats = {
            "models_monitored": 0,
            "retraining_jobs_completed": 0,
            "performance_improvements": 0,
            "last_monitoring_cycle": None,
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "models_directory": "models",
            "backup_directory": "models/backup",
            "monitoring_interval": 3600,  # 1 hour
            "performance_window_days": 7,
            "min_performance_decline": 0.05,  # 5% decline triggers retraining
            "max_concurrent_jobs": 2,
            "feature_engineering": {
                "include_external_data": True,
                "feature_selection": True,
                "automated_feature_creation": True,
            },
            "notification": {"email_alerts": False, "log_level": "INFO"},
        }

    def _initialize_model_configs(self) -> List[ModelConfig]:
        """Initialize model configurations for retraining"""
        configs = []

        # Win Predictor Random Forest
        configs.append(
            ModelConfig(
                model_name="win_predictor_rf",
                model_type="random_forest",
                target_column="win",
                feature_columns=[
                    "horse_age",
                    "jockey_win_rate",
                    "trainer_win_rate",
                    "recent_form_score",
                    "distance_preference",
                    "track_suitability",
                    "weight_carried",
                    "days_since_last_race",
                    "prize_money",
                    "class_rating",
                    "speed_figure",
                    "consistency_score",
                ],
                hyperparameters={
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 5,
                    "min_samples_leaf": 2,
                    "random_state": 42,
                },
                retraining_threshold=0.05,
                min_samples=1000,
                validation_split=0.2,
            )
        )

        # Place Predictor Random Forest
        configs.append(
            ModelConfig(
                model_name="place_predictor_rf",
                model_type="random_forest",
                target_column="placed",
                feature_columns=[
                    "horse_age",
                    "jockey_place_rate",
                    "trainer_place_rate",
                    "recent_form_score",
                    "distance_preference",
                    "track_suitability",
                    "weight_carried",
                    "days_since_last_race",
                    "prize_money",
                    "class_rating",
                    "speed_figure",
                    "consistency_score",
                ],
                hyperparameters={
                    "n_estimators": 100,
                    "max_depth": 12,
                    "min_samples_split": 4,
                    "min_samples_leaf": 2,
                    "random_state": 42,
                },
                retraining_threshold=0.04,
                min_samples=1000,
                validation_split=0.2,
            )
        )

        # Win Predictor Logistic Regression
        configs.append(
            ModelConfig(
                model_name="win_predictor_lr",
                model_type="logistic_regression",
                target_column="win",
                feature_columns=[
                    "horse_age",
                    "jockey_win_rate",
                    "trainer_win_rate",
                    "recent_form_score",
                    "distance_preference",
                    "track_suitability",
                    "weight_carried",
                    "days_since_last_race",
                ],
                hyperparameters={
                    "C": 1.0,
                    "penalty": "l2",
                    "solver": "liblinear",
                    "random_state": 42,
                    "max_iter": 1000,
                },
                retraining_threshold=0.06,
                min_samples=800,
                validation_split=0.2,
            )
        )

        return configs

    async def initialize_database(self):
        """Initialize database tables for model retraining tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Model performance tracking table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_performance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    accuracy REAL NOT NULL,
                    precision_score REAL NOT NULL,
                    recall_score REAL NOT NULL,
                    f1_score REAL NOT NULL,
                    cross_val_score REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    feature_count INTEGER,
                    training_duration REAL,
                    data_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Retraining jobs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS retraining_jobs (
                    job_id TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    trigger_reason TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    metrics_before_json TEXT,
                    metrics_after_json TEXT,
                    improvement_achieved REAL
                )
            """
            )

            # Model configurations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_configurations (
                    model_name TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    target_column TEXT NOT NULL,
                    feature_columns_json TEXT NOT NULL,
                    hyperparameters_json TEXT NOT NULL,
                    retraining_threshold REAL NOT NULL,
                    min_samples INTEGER NOT NULL,
                    validation_split REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_model_perf_name_time ON model_performance_history(model_name, timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_retraining_status ON retraining_jobs(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_retraining_model ON retraining_jobs(model_name)"
            )

            conn.commit()
            conn.close()

            logger.info("Model retraining database tables initialized")

        except Exception as e:
            logger.error(f"Error initializing retraining database: {e}")
            raise

    async def get_training_data(
        self, config: ModelConfig, start_date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get training data for model retraining"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Build query based on configuration
            feature_cols = ", ".join(config.feature_columns)

            if start_date:
                date_filter = f"AND race_date >= '{start_date.strftime('%Y-%m-%d')}'"
            else:
                # Default to last 6 months of data
                start_date = datetime.now() - timedelta(days=180)
                date_filter = f"AND race_date >= '{start_date.strftime('%Y-%m-%d')}'"

            # Query with feature engineering
            query = f"""
                SELECT 
                    {feature_cols},
                    {config.target_column},
                    race_date,
                    horse_name,
                    track_code
                FROM race_results 
                WHERE {config.target_column} IS NOT NULL 
                {date_filter}
                ORDER BY race_date DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            if len(df) < config.min_samples:
                raise ValueError(
                    f"Insufficient training data: {len(df)} < {config.min_samples}"
                )

            # Feature engineering if enabled
            if self.config.get("feature_engineering", {}).get(
                "automated_feature_creation", True
            ):
                df = await self._engineer_features(df, config)

            # Prepare features and targets
            X = df[config.feature_columns]
            y = df[config.target_column]

            # Handle missing values
            X = X.fillna(X.mean())

            logger.info(
                f"Prepared training data for {config.model_name}: {len(df)} samples, {len(config.feature_columns)} features"
            )

            return X, y

        except Exception as e:
            logger.error(f"Error getting training data for {config.model_name}: {e}")
            raise

    async def _engineer_features(
        self, df: pd.DataFrame, config: ModelConfig
    ) -> pd.DataFrame:
        """Apply automated feature engineering"""
        try:
            # Create interaction features
            if "jockey_win_rate" in df.columns and "trainer_win_rate" in df.columns:
                df["jockey_trainer_synergy"] = (
                    df["jockey_win_rate"] * df["trainer_win_rate"]
                )

            # Create ratio features
            if "weight_carried" in df.columns and "horse_age" in df.columns:
                df["weight_age_ratio"] = df["weight_carried"] / (df["horse_age"] + 1)

            # Create recency features
            if "days_since_last_race" in df.columns:
                df["recency_factor"] = 1 / (df["days_since_last_race"] + 1)

            # Add external data features if available
            if self.config.get("feature_engineering", {}).get(
                "include_external_data", True
            ):
                df = await self._add_external_features(df)

            return df

        except Exception as e:
            logger.warning(f"Error in feature engineering: {e}")
            return df

    async def _add_external_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features from external data sources"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Add weather features
            weather_query = """
                SELECT track_code, 
                       AVG(CASE WHEN JSON_EXTRACT(content_json, '$.temperature') != '' 
                               THEN CAST(JSON_EXTRACT(content_json, '$.temperature') AS REAL) END) as avg_temp,
                       AVG(CASE WHEN JSON_EXTRACT(content_json, '$.humidity') != ''
                               THEN CAST(JSON_EXTRACT(content_json, '$.humidity') AS REAL) END) as avg_humidity
                FROM external_data_records 
                WHERE data_type = 'weather' 
                AND timestamp >= datetime('now', '-30 days')
                GROUP BY track_code
            """

            weather_df = pd.read_sql_query(weather_query, conn)

            if not weather_df.empty:
                # Merge weather data
                df = df.merge(weather_df, on="track_code", how="left")

                # Fill missing values with averages
                df["avg_temp"] = df["avg_temp"].fillna(df["avg_temp"].mean())
                df["avg_humidity"] = df["avg_humidity"].fillna(
                    df["avg_humidity"].mean()
                )

            conn.close()

        except Exception as e:
            logger.warning(f"Error adding external features: {e}")

        return df

    def _create_model(self, config: ModelConfig):
        """Create model instance based on configuration"""
        if config.model_type == "random_forest":
            return RandomForestClassifier(**config.hyperparameters)
        elif config.model_type == "logistic_regression":
            return LogisticRegression(**config.hyperparameters)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")

    async def evaluate_model_performance(self, config: ModelConfig) -> ModelMetrics:
        """Evaluate current model performance"""
        try:
            # Load current model
            model_path = self.models_dir / f"{config.model_name}.joblib"
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")

            model = joblib.load(model_path)

            # Get recent data for evaluation
            start_date = datetime.now() - timedelta(
                days=self.config.get("performance_window_days", 7)
            )
            X, y = await self.get_training_data(config, start_date)

            # Split for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.validation_split, random_state=42
            )

            # Predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(
                y_test, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

            # Cross-validation score
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring="accuracy"
            )
            cv_score = cv_scores.mean()

            metrics = ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                cross_val_score=cv_score,
                sample_count=len(X),
                timestamp=datetime.now(),
            )

            logger.info(
                f"Model {config.model_name} performance: Accuracy={accuracy:.3f}, F1={f1:.3f}"
            )

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating model {config.model_name}: {e}")
            raise

    async def train_new_model(self, config: ModelConfig) -> Tuple[Any, ModelMetrics]:
        """Train a new model with current data"""
        try:
            # Get training data
            X, y = await self.get_training_data(config)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.validation_split, random_state=42
            )

            # Create and train model
            model = self._create_model(config)

            start_time = datetime.now()
            model.fit(X_train, y_train)
            training_duration = (datetime.now() - start_time).total_seconds()

            # Evaluate new model
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(
                y_test, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring="accuracy"
            )
            cv_score = cv_scores.mean()

            metrics = ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                cross_val_score=cv_score,
                sample_count=len(X),
                timestamp=datetime.now(),
            )

            logger.info(
                f"New model {config.model_name} trained: Accuracy={accuracy:.3f}, Training time={training_duration:.1f}s"
            )

            return model, metrics

        except Exception as e:
            logger.error(f"Error training new model {config.model_name}: {e}")
            raise

    async def backup_model(self, model_name: str) -> bool:
        """Backup current model before replacement"""
        try:
            model_path = self.models_dir / f"{model_name}.joblib"
            if not model_path.exists():
                logger.warning(f"Model {model_name} not found for backup")
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{model_name}_{timestamp}.joblib"

            shutil.copy2(model_path, backup_path)

            # Also backup metadata if exists
            metadata_path = self.models_dir / f"{model_name}_metadata.json"
            if metadata_path.exists():
                backup_metadata_path = (
                    self.backup_dir / f"{model_name}_{timestamp}_metadata.json"
                )
                shutil.copy2(metadata_path, backup_metadata_path)

            logger.info(f"Model {model_name} backed up to {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error backing up model {model_name}: {e}")
            return False

    async def deploy_model(
        self, model: Any, config: ModelConfig, metrics: ModelMetrics
    ) -> bool:
        """Deploy new model to production"""
        try:
            # Backup current model
            await self.backup_model(config.model_name)

            # Save new model
            model_path = self.models_dir / f"{config.model_name}.joblib"
            joblib.dump(model, model_path)

            # Save metadata
            metadata = {
                "model_name": config.model_name,
                "model_type": config.model_type,
                "training_timestamp": metrics.timestamp.isoformat(),
                "performance_metrics": asdict(metrics),
                "feature_columns": config.feature_columns,
                "hyperparameters": config.hyperparameters,
                "version": datetime.now().strftime("%Y%m%d_%H%M%S"),
            }

            metadata_path = self.models_dir / f"{config.model_name}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.info(f"Model {config.model_name} deployed successfully")
            return True

        except Exception as e:
            logger.error(f"Error deploying model {config.model_name}: {e}")
            return False

    async def save_performance_metrics(
        self, config: ModelConfig, metrics: ModelMetrics
    ):
        """Save performance metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO model_performance_history 
                (model_name, timestamp, accuracy, precision_score, recall_score, 
                 f1_score, cross_val_score, sample_count, feature_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    config.model_name,
                    metrics.timestamp,
                    metrics.accuracy,
                    metrics.precision,
                    metrics.recall,
                    metrics.f1_score,
                    metrics.cross_val_score,
                    metrics.sample_count,
                    len(config.feature_columns),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")

    async def check_retraining_needed(self, config: ModelConfig) -> Tuple[bool, str]:
        """Check if model needs retraining based on performance"""
        try:
            # Get recent performance
            current_metrics = await self.evaluate_model_performance(config)

            # Save current metrics
            await self.save_performance_metrics(config, current_metrics)

            # Get historical performance
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get average performance from last 30 days (excluding last 7 days)
            cursor.execute(
                """
                SELECT AVG(accuracy), AVG(f1_score)
                FROM model_performance_history
                WHERE model_name = ?
                AND timestamp BETWEEN datetime('now', '-30 days') AND datetime('now', '-7 days')
            """,
                (config.model_name,),
            )

            result = cursor.fetchone()
            conn.close()

            if result[0] is None:
                return False, "Insufficient historical data"

            historical_accuracy, historical_f1 = result

            # Check for performance decline
            accuracy_decline = historical_accuracy - current_metrics.accuracy
            f1_decline = historical_f1 - current_metrics.f1_score

            threshold = config.retraining_threshold

            if accuracy_decline > threshold or f1_decline > threshold:
                reason = f"Performance decline detected: Accuracy {accuracy_decline:.3f}, F1 {f1_decline:.3f}"
                return True, reason

            # Check data staleness (if no retraining for 30 days)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MAX(completed_at)
                FROM retraining_jobs
                WHERE model_name = ? AND status = 'completed'
            """,
                (config.model_name,),
            )

            last_retraining = cursor.fetchone()[0]
            conn.close()

            if last_retraining:
                last_retraining_date = datetime.fromisoformat(last_retraining)
                if (datetime.now() - last_retraining_date).days > 30:
                    return True, "Scheduled retraining (30 days since last training)"

            return False, "Performance within acceptable range"

        except Exception as e:
            logger.error(f"Error checking retraining need for {config.model_name}: {e}")
            return False, f"Error: {e}"

    async def schedule_retraining_job(self, config: ModelConfig, reason: str) -> str:
        """Schedule a retraining job"""
        job_id = f"{config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        job = RetrainingJob(
            job_id=job_id,
            model_name=config.model_name,
            scheduled_time=datetime.now(),
            status="pending",
            trigger_reason=reason,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error_message=None,
            metrics_before=None,
            metrics_after=None,
        )

        self.retraining_queue.append(job)

        # Save to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO retraining_jobs 
                (job_id, model_name, scheduled_time, status, trigger_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    job.job_id,
                    job.model_name,
                    job.scheduled_time,
                    job.status,
                    job.trigger_reason,
                    job.created_at,
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"Retraining job scheduled: {job_id}")

        except Exception as e:
            logger.error(f"Error scheduling retraining job: {e}")

        return job_id

    async def execute_retraining_job(self, job: RetrainingJob) -> bool:
        """Execute a retraining job"""
        try:
            # Update job status
            job.status = "running"
            job.started_at = datetime.now()

            # Get model configuration
            config = next(
                (c for c in self.model_configs if c.model_name == job.model_name), None
            )
            if not config:
                raise ValueError(f"Model configuration not found: {job.model_name}")

            # Get current performance
            job.metrics_before = await self.evaluate_model_performance(config)

            # Train new model
            new_model, new_metrics = await self.train_new_model(config)
            job.metrics_after = new_metrics

            # Check if new model is better
            improvement = new_metrics.f1_score - job.metrics_before.f1_score

            if improvement > 0.01:  # At least 1% improvement
                # Deploy new model
                success = await self.deploy_model(new_model, config, new_metrics)

                if success:
                    job.status = "completed"
                    self.stats["performance_improvements"] += 1
                    logger.info(
                        f"Model {job.model_name} retrained successfully. Improvement: {improvement:.3f}"
                    )
                else:
                    job.status = "failed"
                    job.error_message = "Failed to deploy new model"
            else:
                job.status = "completed"
                job.error_message = f"New model not significantly better (improvement: {improvement:.3f})"
                logger.info(
                    f"Model {job.model_name} retrained but not deployed due to insufficient improvement"
                )

            job.completed_at = datetime.now()
            self.stats["retraining_jobs_completed"] += 1

            # Update database
            await self._update_retraining_job_status(job, improvement)

            return job.status == "completed"

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now()

            logger.error(f"Error executing retraining job {job.job_id}: {e}")
            await self._update_retraining_job_status(job, 0.0)

            return False

    async def _update_retraining_job_status(
        self, job: RetrainingJob, improvement: float
    ):
        """Update retraining job status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE retraining_jobs 
                SET status = ?, started_at = ?, completed_at = ?, error_message = ?,
                    metrics_before_json = ?, metrics_after_json = ?, improvement_achieved = ?
                WHERE job_id = ?
            """,
                (
                    job.status,
                    job.started_at,
                    job.completed_at,
                    job.error_message,
                    (
                        json.dumps(asdict(job.metrics_before), default=str)
                        if job.metrics_before
                        else None
                    ),
                    (
                        json.dumps(asdict(job.metrics_after), default=str)
                        if job.metrics_after
                        else None
                    ),
                    improvement,
                    job.job_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating retraining job status: {e}")

    async def monitor_all_models(self) -> Dict[str, Any]:
        """Monitor all configured models and schedule retraining if needed"""
        results = {
            "models_checked": 0,
            "retraining_jobs_scheduled": 0,
            "models_needing_retraining": [],
            "performance_summary": {},
        }

        try:
            for config in self.model_configs:
                try:
                    logger.info(f"Monitoring model: {config.model_name}")

                    # Check if retraining is needed
                    needs_retraining, reason = await self.check_retraining_needed(
                        config
                    )

                    results["models_checked"] += 1
                    self.stats["models_monitored"] += 1

                    if needs_retraining:
                        # Schedule retraining job
                        job_id = await self.schedule_retraining_job(config, reason)

                        results["retraining_jobs_scheduled"] += 1
                        results["models_needing_retraining"].append(
                            {
                                "model_name": config.model_name,
                                "reason": reason,
                                "job_id": job_id,
                            }
                        )

                        logger.info(
                            f"Retraining scheduled for {config.model_name}: {reason}"
                        )
                    else:
                        logger.info(
                            f"Model {config.model_name} performance is acceptable: {reason}"
                        )

                    # Get current performance for summary
                    current_metrics = await self.evaluate_model_performance(config)
                    results["performance_summary"][config.model_name] = {
                        "accuracy": current_metrics.accuracy,
                        "f1_score": current_metrics.f1_score,
                        "sample_count": current_metrics.sample_count,
                        "timestamp": current_metrics.timestamp.isoformat(),
                    }

                except Exception as e:
                    logger.error(f"Error monitoring model {config.model_name}: {e}")
                    continue

            self.stats["last_monitoring_cycle"] = datetime.now()

        except Exception as e:
            logger.error(f"Error in model monitoring cycle: {e}")

        return results

    async def process_retraining_queue(self) -> Dict[str, Any]:
        """Process pending retraining jobs"""
        results = {
            "jobs_processed": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "job_results": [],
        }

        # Process pending jobs
        pending_jobs = [job for job in self.retraining_queue if job.status == "pending"]

        # Limit concurrent jobs
        max_concurrent = self.config.get("max_concurrent_jobs", 2)
        jobs_to_process = pending_jobs[:max_concurrent]

        for job in jobs_to_process:
            try:
                logger.info(f"Processing retraining job: {job.job_id}")

                success = await self.execute_retraining_job(job)

                results["jobs_processed"] += 1

                if success:
                    results["jobs_completed"] += 1
                else:
                    results["jobs_failed"] += 1

                results["job_results"].append(
                    {
                        "job_id": job.job_id,
                        "model_name": job.model_name,
                        "status": job.status,
                        "error_message": job.error_message,
                    }
                )

                # Remove completed job from queue
                self.retraining_queue.remove(job)

            except Exception as e:
                logger.error(f"Error processing retraining job {job.job_id}: {e}")
                results["jobs_failed"] += 1

        return results

    async def get_retraining_statistics(self) -> Dict[str, Any]:
        """Get retraining system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Job statistics
            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM retraining_jobs
                GROUP BY status
            """
            )
            job_stats = {row[0]: row[1] for row in cursor.fetchall()}

            # Recent performance
            cursor.execute(
                """
                SELECT model_name, 
                       AVG(accuracy) as avg_accuracy,
                       AVG(f1_score) as avg_f1,
                       COUNT(*) as measurement_count
                FROM model_performance_history
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY model_name
            """
            )
            recent_performance = [
                {
                    "model_name": row[0],
                    "avg_accuracy": round(row[1], 3),
                    "avg_f1": round(row[2], 3),
                    "measurement_count": row[3],
                }
                for row in cursor.fetchall()
            ]

            # Queue status
            queue_stats = {
                "pending_jobs": len(
                    [j for j in self.retraining_queue if j.status == "pending"]
                ),
                "running_jobs": len(
                    [j for j in self.retraining_queue if j.status == "running"]
                ),
                "total_in_queue": len(self.retraining_queue),
            }

            conn.close()

            return {
                "system_stats": self.stats.copy(),
                "job_statistics": job_stats,
                "recent_performance": recent_performance,
                "queue_status": queue_stats,
                "configured_models": len(self.model_configs),
            }

        except Exception as e:
            logger.error(f"Error getting retraining statistics: {e}")
            return {"error": str(e)}


async def main():
    """Main function for testing the Automated Model Retrainer"""

    print("🤖 Automated Model Retraining System V2.03")
    print("=" * 50)

    try:
        # Initialize retrainer
        retrainer = AutomatedModelRetrainer()

        # Initialize database
        print("📊 Initializing database...")
        await retrainer.initialize_database()

        # Monitor all models
        print("🔍 Monitoring models...")
        monitoring_results = await retrainer.monitor_all_models()

        print(f"✅ Monitoring completed:")
        print(f"   - Models checked: {monitoring_results['models_checked']}")
        print(
            f"   - Retraining jobs scheduled: {monitoring_results['retraining_jobs_scheduled']}"
        )

        if monitoring_results["models_needing_retraining"]:
            print("   - Models needing retraining:")
            for model_info in monitoring_results["models_needing_retraining"]:
                print(f"     • {model_info['model_name']}: {model_info['reason']}")

        # Process retraining queue
        if monitoring_results["retraining_jobs_scheduled"] > 0:
            print("\n🔄 Processing retraining jobs...")
            processing_results = await retrainer.process_retraining_queue()

            print(f"   - Jobs processed: {processing_results['jobs_processed']}")
            print(f"   - Jobs completed: {processing_results['jobs_completed']}")
            print(f"   - Jobs failed: {processing_results['jobs_failed']}")

        # Get statistics
        print("\n📈 Retraining Statistics:")
        stats = await retrainer.get_retraining_statistics()

        print(f"   - Configured models: {stats['configured_models']}")
        print(f"   - Models monitored: {stats['system_stats']['models_monitored']}")
        print(
            f"   - Jobs completed: {stats['system_stats']['retraining_jobs_completed']}"
        )
        print(
            f"   - Performance improvements: {stats['system_stats']['performance_improvements']}"
        )

        if stats["recent_performance"]:
            print("   - Recent model performance:")
            for perf in stats["recent_performance"]:
                print(
                    f"     • {perf['model_name']}: Accuracy={perf['avg_accuracy']}, F1={perf['avg_f1']}"
                )

        print("\n✅ Automated Model Retraining testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
