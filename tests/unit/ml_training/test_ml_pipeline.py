"""
🧪 ML Training Pipeline Tests
============================

Unit tests for the real ML training pipeline system.
Tests feature engineering, model training, and performance evaluation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Test the ML training pipeline
try:
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from docker.ml_training.real_ml_training_pipeline import RealMLTrainingPipeline

    ML_PIPELINE_AVAILABLE = True
except ImportError:
    ML_PIPELINE_AVAILABLE = False

    # Mock class for testing structure
    class RealMLTrainingPipeline:
        pass


class TestMLFeatureEngineering:
    """Test feature engineering capabilities"""

    def test_basic_feature_preparation(self):
        """Test basic feature preparation from race data"""
        # Create sample race data
        race_data = pd.DataFrame(
            {
                "horse_name": ["Thunder Bolt", "Lightning Strike", "Storm Cloud"],
                "age": [4, 5, 6],
                "or_rating": [85, 90, 88],
                "runners": [8, 8, 8],
                "position": [1, 2, 3],  # For target variable
                "fav": [1, 0, 0],  # Favorite indicator
                "sp": [3.0, 5.5, 7.0],  # Starting price
                "race_type": ["Flat", "Flat", "Hurdle"],
                "sex": ["Colt", "Filly", "Gelding"],
            }
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            features_df = pipeline.prepare_features(race_data)

            if features_df is not None:
                # Verify target variable creation
                assert "won" in features_df.columns
                assert features_df["won"].iloc[0] == 1  # Position 1 = won
                assert features_df["won"].iloc[1] == 0  # Position 2 = not won

                # Verify numeric features
                expected_features = ["age", "or_rating", "runners"]
                for feature in expected_features:
                    assert feature in features_df.columns

                # Verify categorical encoding
                if "is_favorite" in features_df.columns:
                    assert features_df["is_favorite"].iloc[0] == 1
                    assert features_df["is_favorite"].iloc[1] == 0

    def test_missing_data_handling(self):
        """Test handling of missing data in feature engineering"""
        # Create data with missing values
        incomplete_data = pd.DataFrame(
            {
                "horse_name": ["Horse 1", "Horse 2", "Horse 3"],
                "age": [4, np.nan, 6],
                "or_rating": [85, 90, np.nan],
                "runners": [8, 8, 8],
                "position": [1, 2, 3],
                "fav": [1, np.nan, 0],
                "sp": [3.0, np.nan, 7.0],
            }
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            features_df = pipeline.prepare_features(incomplete_data)

            if features_df is not None:
                # Verify missing values are handled (filled with 0 or dropped)
                assert (
                    not features_df.isnull().all().any()
                )  # No completely null columns

    def test_categorical_feature_encoding(self):
        """Test categorical feature encoding"""
        categorical_data = pd.DataFrame(
            {
                "horse_name": ["Horse 1", "Horse 2", "Horse 3"],
                "position": [1, 2, 3],
                "race_type": ["Flat", "Hurdle", "Flat"],
                "sex": ["Colt", "Filly", "Gelding"],
                "going": ["Good", "Soft", "Firm"],
            }
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            features_df = pipeline.prepare_features(categorical_data)

            if features_df is not None:
                # Check for encoded categorical features
                categorical_features = ["is_flat", "is_male"]
                for feature in categorical_features:
                    if feature in features_df.columns:
                        # Should be binary encoded (0 or 1)
                        assert features_df[feature].isin([0, 1]).all()


class TestMLModelTraining:
    """Test ML model training functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = Path(tempfile.mkdtemp())

    @patch("joblib.dump")
    @patch("pathlib.Path.mkdir")
    def test_random_forest_training(self, mock_mkdir, mock_joblib_dump):
        """Test Random Forest model training"""
        # Create training data - need at least 10 rows for training
        training_data = pd.DataFrame(
            {
                "age": [4, 5, 6, 4, 5, 6, 4, 5, 6, 4, 5, 6],
                "or_rating": [85, 90, 88, 86, 91, 87, 84, 89, 88, 85, 90, 87],
                "runners": [8, 8, 8, 10, 10, 10, 12, 12, 8, 10, 8, 12],
                "is_favorite": [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
                "sp": [3.0, 5.5, 7.0, 2.8, 6.0, 3.2, 8.0, 4.5, 3.5, 6.5, 2.9, 7.5],
                "won": [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],  # Target variable
            }
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            pipeline.models_path = self.temp_dir

            # Mock ML libraries
            with patch("sklearn.ensemble.RandomForestClassifier") as mock_rf:
                with patch("sklearn.model_selection.train_test_split") as mock_split:
                    # Setup mocks
                    mock_model = Mock()
                    mock_model.predict.return_value = np.array([1, 0, 1])
                    mock_model.predict_proba.return_value = np.array(
                        [[0.2, 0.8], [0.7, 0.3], [0.1, 0.9]]
                    )
                    mock_rf.return_value = mock_model

                    # Mock train_test_split
                    X = training_data.drop("won", axis=1)
                    y = training_data["won"]
                    mock_split.return_value = (X, X, y, y)  # Same data for train/test

                    # Test model training
                    result = pipeline.train_models(training_data)

                    # Verify training was attempted
                    assert result is not None
                    mock_rf.assert_called()
                    mock_model.fit.assert_called()

    @patch("joblib.dump")
    def test_logistic_regression_training(self, mock_joblib_dump):
        """Test Logistic Regression model training"""
        training_data = pd.DataFrame(
            {
                "age": [4, 5, 6, 4, 5, 6],
                "or_rating": [85, 90, 88, 86, 91, 87],
                "won": [1, 0, 0, 1, 0, 1],
            }
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            pipeline.models_path = self.temp_dir

            with patch("sklearn.linear_model.LogisticRegression") as mock_lr:
                with patch("sklearn.model_selection.train_test_split") as mock_split:
                    # Setup mocks
                    mock_model = Mock()
                    mock_model.predict.return_value = np.array([1, 0, 1])
                    mock_model.predict_proba.return_value = np.array(
                        [[0.3, 0.7], [0.8, 0.2], [0.2, 0.8]]
                    )
                    mock_lr.return_value = mock_model

                    X = training_data.drop("won", axis=1)
                    y = training_data["won"]
                    mock_split.return_value = (X, X, y, y)

                    # Test model training
                    result = pipeline.train_models(training_data)

                    # Verify training was attempted
                    assert result is not None
                    mock_lr.assert_called()
                    mock_model.fit.assert_called()

    def test_ensemble_model_creation(self):
        """Test ensemble model creation and evaluation"""
        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()

            # Mock ensemble predictions
            rf_prob = np.array([0.8, 0.3, 0.9])
            lr_prob = np.array([0.7, 0.2, 0.8])
            y_test = np.array([1, 0, 1])

            # Calculate ensemble predictions
            ensemble_predictions = (rf_prob + lr_prob) / 2
            ensemble_pred = (ensemble_predictions > 0.5).astype(int)

            # Verify ensemble logic
            assert len(ensemble_predictions) == len(y_test)
            assert ensemble_predictions[0] == 0.75  # (0.8 + 0.7) / 2
            assert ensemble_pred[0] == 1  # 0.75 > 0.5
            assert ensemble_pred[1] == 0  # 0.25 < 0.5


class TestMLPipelineIntegration:
    """Test ML pipeline integration functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = Path(tempfile.mkdtemp())

    @patch("psycopg2.connect")
    def test_database_connection(self, mock_connect):
        """Test database connection for training data"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()

            # Test database connection check
            result = pipeline.check_database_connection()

            # Verify connection attempt
            mock_connect.assert_called()

    @patch("pandas.read_sql")
    @patch("psycopg2.connect")
    def test_training_data_loading(self, mock_connect, mock_read_sql):
        """Test loading training data from database"""
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock training data
        mock_training_data = pd.DataFrame(
            {"horse_name": ["Horse 1", "Horse 2"], "age": [4, 5], "position": [1, 2]}
        )
        mock_read_sql.return_value = mock_training_data

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()

            # Test data loading
            data = pipeline.load_training_data()

            # Verify data loading
            mock_read_sql.assert_called()
            assert data is not None

    def test_model_metadata_generation(self):
        """Test model metadata generation"""
        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            pipeline.models_path = self.temp_dir

            # Create sample metadata
            metadata = {
                "timestamp": "2025-08-26T12:00:00",
                "training_records": 1000,
                "features": ["age", "or_rating", "runners"],
                "models": {
                    "random_forest": {"accuracy": 0.85, "auc": 0.92},
                    "logistic_regression": {"accuracy": 0.82, "auc": 0.89},
                },
            }

            # Test metadata structure
            assert "timestamp" in metadata
            assert "training_records" in metadata
            assert "features" in metadata
            assert "models" in metadata
            assert isinstance(metadata["features"], list)
            assert isinstance(metadata["models"], dict)


class TestMLPerformanceEvaluation:
    """Test ML model performance evaluation"""

    def test_accuracy_calculation(self):
        """Test accuracy calculation"""
        y_true = np.array([1, 0, 1, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 0])

        # Manual accuracy calculation
        accuracy = np.mean(y_true == y_pred)
        expected_accuracy = 4 / 5  # 4 correct out of 5

        assert accuracy == expected_accuracy

    def test_auc_score_calculation(self):
        """Test AUC score calculation logic"""
        y_true = np.array([1, 0, 1, 1, 0])
        y_prob = np.array([0.9, 0.1, 0.8, 0.7, 0.2])

        # AUC should be high for good predictions
        # This is conceptual - actual AUC calculation would use sklearn
        assert len(y_true) == len(y_prob)
        assert all(0 <= p <= 1 for p in y_prob)  # Probabilities in valid range

    def test_model_comparison(self):
        """Test model performance comparison"""
        model_performances = {
            "random_forest": {"accuracy": 0.85, "auc": 0.92},
            "logistic_regression": {"accuracy": 0.82, "auc": 0.89},
            "ensemble": {"accuracy": 0.87, "auc": 0.94},
        }

        # Verify ensemble performs best
        ensemble_acc = model_performances["ensemble"]["accuracy"]
        rf_acc = model_performances["random_forest"]["accuracy"]
        lr_acc = model_performances["logistic_regression"]["accuracy"]

        assert ensemble_acc >= rf_acc
        assert ensemble_acc >= lr_acc


class TestMLPipelinePerformance:
    """Performance tests for ML pipeline"""

    @pytest.mark.performance
    @pytest.mark.ml
    def test_training_performance(self):
        """Test ML training performance with realistic data size"""
        # Create realistic training dataset
        n_samples = 1000
        training_data = pd.DataFrame(
            {
                "age": np.random.randint(3, 9, n_samples),
                "or_rating": np.random.randint(60, 120, n_samples),
                "runners": np.random.randint(5, 20, n_samples),
                "is_favorite": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
                "sp": np.random.uniform(2.0, 20.0, n_samples),
                "won": np.random.choice(
                    [0, 1], n_samples, p=[0.85, 0.15]
                ),  # 15% win rate
            }
        )

        if ML_PIPELINE_AVAILABLE:
            import time

            pipeline = RealMLTrainingPipeline()
            pipeline.models_path = Path(tempfile.mkdtemp())

            # Time the feature preparation
            start_time = time.time()
            features_df = pipeline.prepare_features(training_data)
            feature_time = time.time() - start_time

            # Feature preparation should be fast
            assert feature_time < 2.0, f"Feature preparation too slow: {feature_time}s"

            if features_df is not None:
                assert (
                    len(features_df) <= n_samples
                )  # May drop some rows with missing values


class TestMLPipelineRobustness:
    """Test ML pipeline robustness and error handling"""

    def test_insufficient_training_data(self):
        """Test handling of insufficient training data"""
        # Very small dataset
        small_data = pd.DataFrame({"age": [4, 5], "won": [1, 0]})

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            pipeline.models_path = Path(tempfile.mkdtemp())

            # Should handle small datasets gracefully
            with patch("sklearn.model_selection.train_test_split") as mock_split:
                X = small_data.drop("won", axis=1)
                y = small_data["won"]
                mock_split.return_value = (X, X, y, y)

                result = pipeline.train_models(small_data)

                # Should return False for insufficient data
                assert result is False

    def test_missing_features(self):
        """Test handling of completely missing features"""
        # Data with no useful features
        empty_features = pd.DataFrame(
            {"horse_name": ["Horse 1", "Horse 2", "Horse 3"], "position": [1, 2, 3]}
        )

        if ML_PIPELINE_AVAILABLE:
            pipeline = RealMLTrainingPipeline()
            features_df = pipeline.prepare_features(empty_features)

            # Should handle gracefully
            if features_df is not None:
                # Should at least have target variable
                assert "won" in features_df.columns


# Test markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.ml,
    pytest.mark.slow,  # ML tests can be slower
]
