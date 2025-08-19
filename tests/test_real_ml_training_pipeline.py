#!/usr/bin/env python3
"""
Test Real ML Training Pipeline
Test the fixed ML training implementation
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "docker" / "ml_training"))

# Import the real training pipeline
from real_ml_training_pipeline import RealMLTrainingPipeline


class TestRealMLTrainingPipeline(unittest.TestCase):
    """Test suite for Real ML Training Pipeline"""

    def setUp(self):
        """Set up test environment"""
        # Mock the paths for testing
        with patch.object(Path, "mkdir"):
            self.pipeline = RealMLTrainingPipeline()
            # Override paths for testing
            self.pipeline.models_path = Path("./models")
            self.pipeline.trained_models_path = Path("./trained_models")

        # Create test data
        self.test_data = pd.DataFrame(
            {
                "race_id": ["123", "123", "124", "124"],
                "course": ["Ayr", "Ayr", "Newmarket", "Newmarket"],
                "distance": ["6f", "6f", "1m", "1m"],
                "race_type": ["Flat Turf", "Flat Turf", "Flat Turf", "Flat Turf"],
                "runners": [8, 8, 12, 12],
                "horse": ["Horse A", "Horse B", "Horse C", "Horse D"],
                "position": [1, 2, 1, 3],
                "age": [4, 5, 3, 6],
                "or_rating": [85, 80, 90, 75],
                "weight": [9.2, 9.0, 8.8, 9.5],
                "jockey": ["J Smith", "J Jones", "M Brown", "P Wilson"],
                "trainer": ["T1", "T2", "T3", "T4"],
                "fav": [1, 0, 1, 0],
                "sp": [2.5, 4.0, 3.2, 8.0],
                "horse_name": ["Horse A", "Horse B", "Horse C", "Horse D"],
                "sex": ["Colt", "Filly", "Gelding", "Horse"],
                "color": ["Bay", "Chestnut", "Grey", "Brown"],
            }
        )

    def test_prepare_features(self):
        """Test feature preparation"""
        prepared_data = self.pipeline.prepare_features(self.test_data)

        self.assertIsNotNone(prepared_data)
        self.assertIn("won", prepared_data.columns)
        self.assertIn("age", prepared_data.columns)
        self.assertIn("or_rating", prepared_data.columns)

        # Check target variable
        self.assertEqual(prepared_data["won"].sum(), 2)  # 2 winners in test data

    @patch("psycopg2.connect")
    def test_database_connection(self, mock_connect):
        """Test database connection check"""
        # Mock successful connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [(50,), (400,), (300,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.pipeline.check_database_connection()
        self.assertTrue(result)

        # Test failure case
        mock_connect.side_effect = Exception("Connection failed")
        result = self.pipeline.check_database_connection()
        self.assertFalse(result)

    @patch("pandas.read_sql_query")
    @patch("psycopg2.connect")
    def test_load_training_data(self, mock_connect, mock_read_sql):
        """Test training data loading"""
        mock_connect.return_value = Mock()
        mock_read_sql.return_value = self.test_data

        result = self.pipeline.load_training_data()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)

    @patch("joblib.dump")
    def test_train_models(self, mock_joblib_dump):
        """Test model training"""
        # Prepare test data
        prepared_data = self.pipeline.prepare_features(self.test_data)

        # Mock scikit-learn imports
        with patch.dict(
            "sys.modules",
            {
                "sklearn.ensemble": MagicMock(),
                "sklearn.linear_model": MagicMock(),
                "sklearn.model_selection": MagicMock(),
                "sklearn.metrics": MagicMock(),
                "joblib": MagicMock(),
            },
        ):
            # Mock train_test_split
            with patch("sklearn.model_selection.train_test_split") as mock_split:
                mock_split.return_value = (
                    prepared_data.drop("won", axis=1).iloc[:3],  # X_train
                    prepared_data.drop("won", axis=1).iloc[3:],  # X_test
                    prepared_data["won"].iloc[:3],  # y_train
                    prepared_data["won"].iloc[3:],  # y_test
                )

                # Mock model predictions
                with patch("sklearn.ensemble.RandomForestClassifier") as mock_rf:
                    with patch("sklearn.linear_model.LogisticRegression") as mock_lr:
                        mock_rf_instance = Mock()
                        mock_lr_instance = Mock()

                        mock_rf_instance.predict.return_value = [0]
                        mock_rf_instance.predict_proba.return_value = [[0.3, 0.7]]

                        mock_lr_instance.predict.return_value = [1]
                        mock_lr_instance.predict_proba.return_value = [[0.2, 0.8]]

                        mock_rf.return_value = mock_rf_instance
                        mock_lr.return_value = mock_lr_instance

                        # Mock accuracy and AUC functions
                        with patch("sklearn.metrics.accuracy_score", return_value=0.75):
                            with patch(
                                "sklearn.metrics.roc_auc_score", return_value=0.80
                            ):
                                result = self.pipeline.train_models(prepared_data)

                                self.assertTrue(result)

                                # Verify models were trained
                                self.assertTrue(mock_rf_instance.fit.called)
                                self.assertTrue(mock_lr_instance.fit.called)

    @patch.object(RealMLTrainingPipeline, "train_models")
    @patch.object(RealMLTrainingPipeline, "prepare_features")
    @patch.object(RealMLTrainingPipeline, "load_training_data")
    @patch.object(RealMLTrainingPipeline, "check_database_connection")
    def test_run_real_training_cycle(
        self, mock_db_check, mock_load_data, mock_prepare_features, mock_train_models
    ):
        """Test complete training cycle"""
        # Mock successful pipeline
        mock_db_check.return_value = True
        mock_load_data.return_value = self.test_data
        mock_prepare_features.return_value = self.pipeline.prepare_features(
            self.test_data
        )
        mock_train_models.return_value = True

        result = self.pipeline.run_real_training_cycle()

        self.assertTrue(result)
        self.assertTrue(mock_db_check.called)
        self.assertTrue(mock_load_data.called)
        self.assertTrue(mock_prepare_features.called)
        self.assertTrue(mock_train_models.called)

        # Test failure cases
        mock_db_check.return_value = False
        result = self.pipeline.run_real_training_cycle()
        self.assertFalse(result)


def run_integration_test():
    """Run integration test with real database if available"""
    print("🧪 Running ML Training Pipeline Integration Test...")

    try:
        pipeline = RealMLTrainingPipeline()

        # Test database connection
        print("📊 Testing database connection...")
        db_available = pipeline.check_database_connection()

        if db_available:
            print("✅ Database connection successful")

            # Test data loading
            print("📥 Testing data loading...")
            data = pipeline.load_training_data()

            if data is not None and len(data) > 0:
                print(f"✅ Data loaded: {len(data)} records")

                # Test feature preparation
                print("🔧 Testing feature preparation...")
                features = pipeline.prepare_features(data)

                if features is not None and len(features) > 0:
                    print(
                        f"✅ Features prepared: {len(features)} rows, {len(features.columns)} columns"
                    )
                    print(f"📊 Features: {list(features.columns)}")

                    print(
                        "🎯 Integration test PASSED - Pipeline ready for real training!"
                    )
                    return True
                else:
                    print("❌ Feature preparation failed")
                    return False
            else:
                print("❌ Data loading failed")
                return False
        else:
            print("⚠️ Database not available - skipping integration test")
            return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running ML Training Pipeline Unit Tests...")
    unittest.main(argv=[""], exit=False, verbosity=2)

    # Run integration test
    print("\n" + "=" * 60)
    run_integration_test()
