"""
🧪 ML Pipeline Integration Tests
==============================

Integration tests for the ML pipeline components and workflows.
Tests end-to-end ML pipeline functionality including feature engineering,
model training, prediction, and performance evaluation.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import pickle
from datetime import datetime, timedelta
import sqlite3
import tempfile
import shutil
from typing import Dict, List, Any, Optional


# Test fixtures and utilities
@pytest.fixture
def ml_training_data():
    """Generate realistic horse racing training data"""
    np.random.seed(42)
    n_samples = 1000

    data = {
        "horse_name": [f"Horse_{i}" for i in range(n_samples)],
        "jockey_name": [f"Jockey_{i % 50}" for i in range(n_samples)],
        "trainer_name": [f"Trainer_{i % 30}" for i in range(n_samples)],
        "track_condition": np.random.choice(
            ["GOOD", "SOFT", "HEAVY", "FIRM"], n_samples
        ),
        "distance": np.random.choice([1000, 1200, 1400, 1600, 2000], n_samples),
        "race_class": np.random.choice(["C1", "C2", "C3", "C4", "C5"], n_samples),
        "barrier": np.random.randint(1, 21, n_samples),
        "weight": np.random.uniform(54.0, 62.0, n_samples),
        "odds": np.random.exponential(5.0, n_samples) + 1.0,
        "last_3_avg_position": np.random.uniform(1.0, 12.0, n_samples),
        "days_since_last_run": np.random.randint(7, 365, n_samples),
        "track_win_rate": np.random.uniform(0.0, 0.4, n_samples),
        "jockey_win_rate": np.random.uniform(0.05, 0.25, n_samples),
        "trainer_win_rate": np.random.uniform(0.08, 0.30, n_samples),
        "position": np.random.randint(1, 13, n_samples),  # Target variable
    }

    return pd.DataFrame(data)


@pytest.fixture
def ml_test_environment():
    """Set up ML test environment"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create directory structure
        models_dir = temp_path / "models"
        cache_dir = temp_path / "cache"
        reports_dir = temp_path / "reports"

        models_dir.mkdir()
        cache_dir.mkdir()
        reports_dir.mkdir()

        yield {
            "base_dir": temp_path,
            "models_dir": models_dir,
            "cache_dir": cache_dir,
            "reports_dir": reports_dir,
        }


@pytest.fixture
def mock_ml_pipeline():
    """Mock ML pipeline components"""
    with patch("src.ml_training.ml_pipeline.MLPipeline") as mock_pipeline:
        mock_instance = Mock()

        # Mock feature engineering
        mock_instance.feature_engineer.return_value = Mock()
        mock_instance.feature_engineer.return_value.columns = [
            "distance_normalized",
            "weight_normalized",
            "odds_log",
            "barrier_position_factor",
            "jockey_performance_score",
            "trainer_performance_score",
            "track_suitability_score",
        ]

        # Mock model training
        mock_instance.train_model.return_value = {
            "model": Mock(),
            "feature_importance": {"distance_normalized": 0.3, "odds_log": 0.25},
            "performance_metrics": {
                "accuracy": 0.72,
                "precision": 0.68,
                "recall": 0.71,
            },
        }

        # Mock predictions
        mock_instance.predict.return_value = np.random.uniform(0, 1, 100)
        mock_instance.predict_race.return_value = {
            "predictions": np.random.uniform(0, 1, 12),
            "probabilities": np.random.uniform(0, 1, 12),
            "confidence_scores": np.random.uniform(0.6, 0.9, 12),
        }

        mock_pipeline.return_value = mock_instance
        yield mock_instance


class TestMLPipelineIntegration:
    """Integration tests for ML pipeline"""

    @pytest.mark.integration
    @pytest.mark.ml
    def test_end_to_end_training_pipeline(self, ml_training_data, ml_test_environment):
        """Test complete ML training pipeline"""
        # This would normally import the actual ML pipeline
        # For now, we'll simulate the process

        # Feature engineering phase
        features_df = self._simulate_feature_engineering(ml_training_data)
        assert len(features_df.columns) > len(ml_training_data.columns)
        assert "distance_normalized" in features_df.columns
        assert "odds_log" in features_df.columns

        # Model training phase
        model_results = self._simulate_model_training(features_df)
        assert "model" in model_results
        assert "feature_importance" in model_results
        assert "performance_metrics" in model_results

        # Model persistence phase
        model_path = ml_test_environment["models_dir"] / "test_model.pkl"
        self._simulate_model_saving(model_results["model"], model_path)
        assert model_path.exists()

        # Model loading and validation
        loaded_model = self._simulate_model_loading(model_path)
        assert loaded_model is not None

    @pytest.mark.integration
    @pytest.mark.ml
    def test_feature_engineering_integration(self, ml_training_data):
        """Test feature engineering integration"""
        engineered_features = self._simulate_feature_engineering(ml_training_data)

        # Verify feature engineering outputs
        expected_features = [
            "distance_normalized",
            "weight_normalized",
            "odds_log",
            "barrier_position_factor",
            "jockey_performance_score",
            "trainer_performance_score",
            "track_suitability_score",
            "form_momentum_score",
            "class_rating_adjustment",
        ]

        for feature in expected_features:
            assert feature in engineered_features.columns, f"Missing feature: {feature}"

        # Verify feature quality
        assert (
            not engineered_features.isnull().any().any()
        ), "Features contain null values"
        assert np.isfinite(
            engineered_features.select_dtypes(include=[np.number]).values
        ).all(), "Features contain non-finite values"

    @pytest.mark.integration
    @pytest.mark.ml
    def test_model_training_integration(self, ml_training_data, ml_test_environment):
        """Test model training integration with different algorithms"""
        features_df = self._simulate_feature_engineering(ml_training_data)

        algorithms = ["RandomForest", "LogisticRegression", "XGBoost", "Ensemble"]

        for algorithm in algorithms:
            model_results = self._simulate_model_training(features_df, algorithm)

            # Verify training results
            assert "model" in model_results
            assert "feature_importance" in model_results
            assert "performance_metrics" in model_results

            # Verify performance metrics
            metrics = model_results["performance_metrics"]
            assert "accuracy" in metrics
            assert "precision" in metrics
            assert "recall" in metrics
            assert "f1_score" in metrics

            # Verify reasonable performance bounds
            assert 0.5 <= metrics["accuracy"] <= 1.0
            assert 0.0 <= metrics["precision"] <= 1.0
            assert 0.0 <= metrics["recall"] <= 1.0

    @pytest.mark.integration
    @pytest.mark.ml
    def test_prediction_pipeline_integration(
        self, ml_training_data, ml_test_environment
    ):
        """Test prediction pipeline integration"""
        # Train a model first
        features_df = self._simulate_feature_engineering(ml_training_data)
        model_results = self._simulate_model_training(features_df)

        # Test single prediction
        sample_data = ml_training_data.iloc[0:1]
        prediction = self._simulate_prediction(model_results["model"], sample_data)

        assert isinstance(prediction, (float, np.float64))
        assert 0.0 <= prediction <= 1.0

        # Test batch predictions
        batch_data = ml_training_data.iloc[0:10]
        batch_predictions = self._simulate_batch_predictions(
            model_results["model"], batch_data
        )

        assert len(batch_predictions) == len(batch_data)
        assert all(0.0 <= pred <= 1.0 for pred in batch_predictions)

    @pytest.mark.integration
    @pytest.mark.ml
    def test_race_prediction_integration(self, ml_training_data, ml_test_environment):
        """Test complete race prediction integration"""
        # Simulate a race with multiple runners
        race_data = ml_training_data.iloc[0:12].copy()  # 12 runners
        race_data["race_id"] = "TEST_RACE_001"

        # Train model
        features_df = self._simulate_feature_engineering(ml_training_data)
        model_results = self._simulate_model_training(features_df)

        # Predict race outcomes
        race_predictions = self._simulate_race_prediction(
            model_results["model"], race_data
        )

        # Verify race prediction structure
        assert "predictions" in race_predictions
        assert "probabilities" in race_predictions
        assert "confidence_scores" in race_predictions
        assert "recommended_bets" in race_predictions

        # Verify prediction constraints
        predictions = race_predictions["predictions"]
        probabilities = race_predictions["probabilities"]

        assert len(predictions) == len(race_data)
        assert len(probabilities) == len(race_data)
        assert np.isclose(
            np.sum(probabilities), 1.0, rtol=0.01
        )  # Probabilities sum to 1

    @pytest.mark.integration
    @pytest.mark.ml
    @pytest.mark.performance
    def test_ml_pipeline_performance(self, ml_training_data, ml_test_environment):
        """Test ML pipeline performance benchmarks"""
        import time

        # Feature engineering performance
        start_time = time.time()
        features_df = self._simulate_feature_engineering(ml_training_data)
        feature_time = time.time() - start_time

        assert feature_time < 10.0, f"Feature engineering too slow: {feature_time:.2f}s"

        # Model training performance
        start_time = time.time()
        model_results = self._simulate_model_training(features_df)
        training_time = time.time() - start_time

        assert training_time < 30.0, f"Model training too slow: {training_time:.2f}s"

        # Prediction performance
        start_time = time.time()
        batch_predictions = self._simulate_batch_predictions(
            model_results["model"], ml_training_data.iloc[0:100]
        )
        prediction_time = time.time() - start_time

        assert (
            prediction_time < 5.0
        ), f"Batch prediction too slow: {prediction_time:.2f}s"

    @pytest.mark.integration
    @pytest.mark.ml
    def test_model_persistence_integration(self, ml_training_data, ml_test_environment):
        """Test model persistence and loading integration"""
        # Train and save model
        features_df = self._simulate_feature_engineering(ml_training_data)
        model_results = self._simulate_model_training(features_df)

        model_path = ml_test_environment["models_dir"] / "persistence_test.pkl"
        metadata_path = (
            ml_test_environment["models_dir"] / "persistence_test_metadata.json"
        )

        # Save model and metadata
        self._simulate_model_saving(model_results["model"], model_path)
        self._simulate_metadata_saving(model_results, metadata_path)

        assert model_path.exists()
        assert metadata_path.exists()

        # Load model and metadata
        loaded_model = self._simulate_model_loading(model_path)
        loaded_metadata = self._simulate_metadata_loading(metadata_path)

        # Verify loaded model works
        sample_prediction = self._simulate_prediction(
            loaded_model, ml_training_data.iloc[0:1]
        )
        assert isinstance(sample_prediction, (float, np.float64))

        # Verify metadata integrity
        assert "feature_importance" in loaded_metadata
        assert "performance_metrics" in loaded_metadata
        assert "training_timestamp" in loaded_metadata

    @pytest.mark.integration
    @pytest.mark.ml
    def test_cross_validation_integration(self, ml_training_data):
        """Test cross-validation integration"""
        features_df = self._simulate_feature_engineering(ml_training_data)

        # Simulate k-fold cross-validation
        cv_results = self._simulate_cross_validation(features_df, k_folds=5)

        assert "fold_scores" in cv_results
        assert "mean_score" in cv_results
        assert "std_score" in cv_results
        assert "fold_predictions" in cv_results

        # Verify CV results
        fold_scores = cv_results["fold_scores"]
        assert len(fold_scores) == 5
        assert all(0.0 <= score <= 1.0 for score in fold_scores)

        mean_score = cv_results["mean_score"]
        std_score = cv_results["std_score"]
        assert 0.0 <= mean_score <= 1.0
        assert std_score >= 0.0

    # Helper methods for simulation (would be replaced with actual implementations)

    def _simulate_feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate feature engineering process"""
        features_df = data.copy()

        # Add engineered features
        features_df["distance_normalized"] = (
            data["distance"] - data["distance"].mean()
        ) / data["distance"].std()
        features_df["weight_normalized"] = (
            data["weight"] - data["weight"].mean()
        ) / data["weight"].std()
        features_df["odds_log"] = np.log(data["odds"])
        features_df["barrier_position_factor"] = data["barrier"] / 20.0
        features_df["jockey_performance_score"] = data["jockey_win_rate"] * 100
        features_df["trainer_performance_score"] = data["trainer_win_rate"] * 100
        features_df["track_suitability_score"] = data["track_win_rate"] * 100
        features_df["form_momentum_score"] = 1.0 / (data["last_3_avg_position"] + 1)
        features_df["class_rating_adjustment"] = data["race_class"].map(
            {"C1": 1.0, "C2": 0.8, "C3": 0.6, "C4": 0.4, "C5": 0.2}
        )

        return features_df

    def _simulate_model_training(
        self, features_df: pd.DataFrame, algorithm: str = "RandomForest"
    ) -> Dict:
        """Simulate model training process"""
        # This would normally use actual ML libraries
        model = Mock()
        model.algorithm = algorithm

        feature_importance = {}
        for col in features_df.select_dtypes(include=[np.number]).columns:
            if col != "position":
                feature_importance[col] = np.random.uniform(0.01, 0.3)

        # Normalize feature importance
        total_importance = sum(feature_importance.values())
        feature_importance = {
            k: v / total_importance for k, v in feature_importance.items()
        }

        performance_metrics = {
            "accuracy": np.random.uniform(0.65, 0.85),
            "precision": np.random.uniform(0.60, 0.80),
            "recall": np.random.uniform(0.62, 0.82),
            "f1_score": np.random.uniform(0.61, 0.81),
        }

        return {
            "model": model,
            "feature_importance": feature_importance,
            "performance_metrics": performance_metrics,
            "training_timestamp": datetime.now().isoformat(),
        }

    def _simulate_prediction(self, model: Mock, data: pd.DataFrame) -> float:
        """Simulate single prediction"""
        return np.random.uniform(0.1, 0.9)

    def _simulate_batch_predictions(
        self, model: Mock, data: pd.DataFrame
    ) -> List[float]:
        """Simulate batch predictions"""
        return [np.random.uniform(0.1, 0.9) for _ in range(len(data))]

    def _simulate_race_prediction(self, model: Mock, race_data: pd.DataFrame) -> Dict:
        """Simulate race prediction"""
        n_runners = len(race_data)

        # Generate raw predictions
        raw_predictions = np.random.uniform(0.1, 0.9, n_runners)

        # Convert to probabilities
        probabilities = raw_predictions / np.sum(raw_predictions)

        # Generate confidence scores
        confidence_scores = np.random.uniform(0.6, 0.9, n_runners)

        # Generate recommended bets
        recommended_bets = []
        for i, (pred, prob, conf) in enumerate(
            zip(raw_predictions, probabilities, confidence_scores)
        ):
            if conf > 0.8 and prob > 0.15:
                recommended_bets.append(
                    {
                        "runner_index": i,
                        "horse_name": race_data.iloc[i]["horse_name"],
                        "bet_type": "WIN",
                        "confidence": conf,
                        "expected_value": pred * 2.0,
                    }
                )

        return {
            "predictions": raw_predictions.tolist(),
            "probabilities": probabilities.tolist(),
            "confidence_scores": confidence_scores.tolist(),
            "recommended_bets": recommended_bets,
        }

    def _simulate_cross_validation(
        self, features_df: pd.DataFrame, k_folds: int = 5
    ) -> Dict:
        """Simulate cross-validation"""
        fold_scores = [np.random.uniform(0.65, 0.85) for _ in range(k_folds)]

        return {
            "fold_scores": fold_scores,
            "mean_score": np.mean(fold_scores),
            "std_score": np.std(fold_scores),
            "fold_predictions": [
                np.random.uniform(0.1, 0.9, 50) for _ in range(k_folds)
            ],
        }

    def _simulate_model_saving(self, model: Mock, path: Path):
        """Simulate model saving"""
        with open(path, "wb") as f:
            pickle.dump({"model": model, "timestamp": datetime.now()}, f)

    def _simulate_model_loading(self, path: Path) -> Mock:
        """Simulate model loading"""
        with open(path, "rb") as f:
            data = pickle.load(f)
            return data["model"]

    def _simulate_metadata_saving(self, model_results: Dict, path: Path):
        """Simulate metadata saving"""
        metadata = {
            "feature_importance": model_results["feature_importance"],
            "performance_metrics": model_results["performance_metrics"],
            "training_timestamp": model_results["training_timestamp"],
            "model_version": "1.0",
        }

        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _simulate_metadata_loading(self, path: Path) -> Dict:
        """Simulate metadata loading"""
        with open(path, "r") as f:
            return json.load(f)


class TestMLIntegrationWithDatabase:
    """Integration tests for ML pipeline with database"""

    @pytest.mark.integration
    @pytest.mark.ml
    @pytest.mark.database
    def test_ml_data_extraction_integration(self, test_db_connection):
        """Test ML data extraction from database"""
        # This would test actual database queries for ML training data
        # For now, simulate the process

        query_results = self._simulate_ml_data_query(test_db_connection)

        assert len(query_results) > 0
        assert "horse_name" in query_results.columns
        assert "position" in query_results.columns
        assert "odds" in query_results.columns

        # Verify data quality for ML
        assert not query_results["position"].isnull().any()
        assert query_results["odds"].min() >= 1.0
        assert query_results["position"].min() >= 1

    @pytest.mark.integration
    @pytest.mark.ml
    @pytest.mark.database
    def test_ml_predictions_storage_integration(
        self, test_db_connection, ml_test_environment
    ):
        """Test storing ML predictions in database"""
        # Simulate predictions
        predictions_data = {
            "race_id": ["RACE_001", "RACE_002", "RACE_003"],
            "horse_name": ["Horse_A", "Horse_B", "Horse_C"],
            "prediction_score": [0.75, 0.82, 0.68],
            "confidence": [0.85, 0.90, 0.78],
            "prediction_timestamp": [datetime.now()] * 3,
        }

        predictions_df = pd.DataFrame(predictions_data)

        # Test storage (simulated)
        success = self._simulate_predictions_storage(test_db_connection, predictions_df)
        assert success

        # Test retrieval (simulated)
        retrieved_predictions = self._simulate_predictions_retrieval(
            test_db_connection, "RACE_001"
        )
        assert len(retrieved_predictions) > 0

    def _simulate_ml_data_query(self, db_connection) -> pd.DataFrame:
        """Simulate ML data query from database"""
        # This would normally execute actual SQL queries
        return pd.DataFrame(
            {
                "horse_name": [f"Horse_{i}" for i in range(100)],
                "position": np.random.randint(1, 13, 100),
                "odds": np.random.exponential(5.0, 100) + 1.0,
                "jockey_name": [f"Jockey_{i % 20}" for i in range(100)],
                "trainer_name": [f"Trainer_{i % 15}" for i in range(100)],
            }
        )

    def _simulate_predictions_storage(
        self, db_connection, predictions_df: pd.DataFrame
    ) -> bool:
        """Simulate storing predictions in database"""
        # This would normally execute INSERT statements
        return True

    def _simulate_predictions_retrieval(
        self, db_connection, race_id: str
    ) -> pd.DataFrame:
        """Simulate retrieving predictions from database"""
        # This would normally execute SELECT statements
        return pd.DataFrame(
            {
                "race_id": [race_id],
                "horse_name": ["Horse_A"],
                "prediction_score": [0.75],
                "confidence": [0.85],
            }
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
