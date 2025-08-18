#!/usr/bin/env python3
"""
🎯 Production ML Model Training - Feature-Aligned Training System
Trains production ML models that align with our current data pipeline

This script addresses the feature mismatch issue by:
1. Using the current data from ml_feature_preparation.py
2. Training models with the exact feature set we have
3. Ensuring prediction compatibility
4. Creating production-ready models

Author: AI Assistant
Date: August 11, 2025
"""

import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
import psycopg2
from sklearn.compose import ColumnTransformer

# ML imports
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionMLTrainer:
    """Production ML trainer aligned with current data pipeline."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "trained_models" / "production"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Database connection
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        self.trained_models = {}
        self.feature_names = []
        self.scaler = None

    def load_current_data(self) -> pd.DataFrame:
        """Load data using the same query as ml_feature_preparation.py"""
        logger.info("📊 Loading data from current pipeline...")

        query = """
            SELECT 
                rr.*,
                js.wins as jockey_wins,
                js.runs as jockey_runs,
                js.win_percentage as jockey_win_pct,
                ts.wins as trainer_wins,
                ts.runs as trainer_runs,
                ts.win_percentage as trainer_win_pct
            FROM race_results rr
            LEFT JOIN jockey_stats js ON rr.jockey_name = js.jockey_name
            LEFT JOIN trainer_stats ts ON rr.trainer_name = ts.trainer_name
            WHERE rr.jockey_name != 'Unknown' 
            AND rr.trainer_name != 'Unknown'
            AND rr.course != 'Unknown'
            ORDER BY rr.race_date DESC, rr.race_id
        """

        try:
            connection = psycopg2.connect(**self.db_config)
            df = pd.read_sql_query(query, connection)
            connection.close()

            logger.info(f"✅ Loaded {len(df)} records from database")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            raise

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features exactly as in ml_feature_preparation.py"""
        logger.info("⚙️ Engineering features...")

        # Clean and convert data types
        df["win_odds"] = pd.to_numeric(df["win_odds"], errors="coerce")
        df["horse_age"] = pd.to_numeric(df["horse_age"], errors="coerce")
        df["horse_weight_kg"] = pd.to_numeric(df["horse_weight_kg"], errors="coerce")
        df["draw"] = pd.to_numeric(df["draw"], errors="coerce")
        df["finished_position"] = pd.to_numeric(
            df["finished_position"], errors="coerce"
        )
        df["prize_money"] = pd.to_numeric(df["prize_money"], errors="coerce")

        # Fill missing values
        df["win_odds"] = df["win_odds"].fillna(df["win_odds"].median())
        df["horse_age"] = df["horse_age"].fillna(4)
        df["horse_weight_kg"] = df["horse_weight_kg"].fillna(57)
        df["draw"] = df["draw"].fillna(8)
        df["prize_money"] = df["prize_money"].fillna(0)
        df["jockey_win_pct"] = df["jockey_win_pct"].fillna(0)
        df["trainer_win_pct"] = df["trainer_win_pct"].fillna(0)

        # 1. ODDS-BASED FEATURES
        df["log_odds"] = np.log(df["win_odds"] + 1)
        df["implied_probability"] = 1 / df["win_odds"]
        df["odds_rank"] = df.groupby("race_id")["win_odds"].rank()
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)

        # 2. PERFORMANCE FEATURES
        df["combined_performance"] = (df["jockey_win_pct"] + df["trainer_win_pct"]) / 2

        # 3. RACE CONTEXT FEATURES
        race_stats = (
            df.groupby("race_id")
            .agg(
                {
                    "horse_name": "count",  # field_size
                    "win_odds": ["min", "max", "mean"],  # market dynamics
                    "prize_money": "first",
                }
            )
            .reset_index()
        )

        race_stats.columns = [
            "race_id",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "race_prize",
        ]
        df = df.merge(race_stats, on="race_id", how="left")

        # 4. POSITIONAL FEATURES
        df["draw_percentile"] = df.groupby("race_id")["draw"].rank(pct=True)
        df["weight_percentile"] = df.groupby("race_id")["horse_weight_kg"].rank(
            pct=True
        )
        df["age_category"] = pd.cut(
            df["horse_age"], bins=[0, 3, 5, 7, 15], labels=[0, 1, 2, 3]
        )

        # 5. TARGET VARIABLE
        df["is_winner"] = (df["finished_position"] == 1).astype(int)

        # Select final features for training
        feature_columns = [
            "log_odds",
            "implied_probability",
            "odds_rank",
            "is_favorite",
            "combined_performance",
            "field_size",
            "min_odds",
            "max_odds",
            "avg_odds",
            "draw_percentile",
            "weight_percentile",
            "age_category",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "jockey_win_pct",
            "trainer_win_pct",
        ]

        # Ensure all features exist and are numeric
        for col in feature_columns:
            if col not in df.columns:
                logger.warning(f"Missing feature {col}, filling with 0")
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        self.feature_names = feature_columns
        logger.info(f"✅ Feature engineering complete: {len(feature_columns)} features")

        return df[feature_columns + ["is_winner", "race_id", "horse_name"]]

    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training."""
        logger.info("🎯 Preparing training data...")

        # Remove rows with missing target
        df_clean = df.dropna(subset=["is_winner"])

        # Prepare features and target
        X = df_clean[self.feature_names].values
        y = df_clean["is_winner"].values

        logger.info(f"📊 Training data prepared:")
        logger.info(f"   Features: {X.shape[1]}")
        logger.info(f"   Samples: {X.shape[0]:,}")
        logger.info(f"   Win rate: {y.mean():.4f}")

        return X, y

    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train multiple ML models."""
        logger.info("🚀 Training production ML models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Define models
        models = {
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
            ),
            "logistic_regression": LogisticRegression(random_state=42, max_iter=1000),
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
            ),
        }

        results = {}

        for name, model in models.items():
            logger.info(f"   🎯 Training {name}...")

            # Use scaled data for logistic regression and neural network
            if name in ["logistic_regression", "neural_network"]:
                model.fit(X_train_scaled, y_train)
                train_pred = model.predict_proba(X_train_scaled)[:, 1]
                test_pred = model.predict_proba(X_test_scaled)[:, 1]
                test_pred_binary = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                train_pred = model.predict_proba(X_train)[:, 1]
                test_pred = model.predict_proba(X_test)[:, 1]
                test_pred_binary = model.predict(X_test)

            # Calculate metrics
            train_auc = roc_auc_score(y_train, train_pred)
            test_auc = roc_auc_score(y_test, test_pred)
            test_accuracy = accuracy_score(y_test, test_pred_binary)
            test_precision = precision_score(y_test, test_pred_binary)
            test_recall = recall_score(y_test, test_pred_binary)
            test_f1 = f1_score(y_test, test_pred_binary)

            # Cross-validation
            cv_scores = cross_val_score(
                model,
                (
                    X_train_scaled
                    if name in ["logistic_regression", "neural_network"]
                    else X_train
                ),
                y_train,
                cv=5,
                scoring="roc_auc",
            )

            results[name] = {
                "model": model,
                "train_auc": train_auc,
                "test_auc": test_auc,
                "test_accuracy": test_accuracy,
                "test_precision": test_precision,
                "test_recall": test_recall,
                "test_f1": test_f1,
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
            }

            logger.info(
                f"       📈 {name}: Test AUC {test_auc:.4f}, Accuracy {test_accuracy:.4f}"
            )

        self.trained_models = results
        return results

    def save_models(self) -> None:
        """Save all trained models and metadata."""
        logger.info("💾 Saving production models...")

        # Save individual models
        for name, result in self.trained_models.items():
            model_file = self.models_dir / f"{name}_production.joblib"
            joblib.dump(result["model"], model_file)
            logger.info(f"   ✅ Saved {name}")

        # Save scaler
        scaler_file = self.models_dir / "scaler_production.joblib"
        joblib.dump(self.scaler, scaler_file)

        # Save feature names
        features_file = self.models_dir / "features_production.joblib"
        joblib.dump(self.feature_names, features_file)

        # Save performance metrics
        performance = {}
        for name, result in self.trained_models.items():
            performance[name] = {
                "test_auc": result["test_auc"],
                "test_accuracy": result["test_accuracy"],
                "test_precision": result["test_precision"],
                "test_recall": result["test_recall"],
                "test_f1": result["test_f1"],
                "cv_mean": result["cv_mean"],
                "cv_std": result["cv_std"],
            }

        performance_file = self.models_dir / "performance_production.joblib"
        joblib.dump(performance, performance_file)

        logger.info(f"📁 All models saved to: {self.models_dir}")

    def create_prediction_interface(self) -> None:
        """Create a simple prediction interface for production use."""
        interface_code = '''#!/usr/bin/env python3
"""
Production ML Model Interface
Simple interface for making predictions with aligned features
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class ProductionMLPredictor:
    """Production ML predictor with correct feature alignment."""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.load_models()
    
    def load_models(self):
        """Load all production models."""
        try:
            # Load models
            for model_name in ['random_forest', 'gradient_boosting', 'logistic_regression', 'neural_network']:
                model_file = self.models_dir / f"{model_name}_production.joblib"
                if model_file.exists():
                    self.models[model_name] = joblib.load(model_file)
            
            # Load scaler and features
            self.scaler = joblib.load(self.models_dir / "scaler_production.joblib")
            self.feature_names = joblib.load(self.models_dir / "features_production.joblib")
            
            print(f"✅ Loaded {len(self.models)} production models")
            print(f"📊 Expected features: {len(self.feature_names)}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def predict(self, horse_data: dict, model_name: str = 'gradient_boosting') -> float:
        """Make prediction for a single horse."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        # Prepare features in correct order
        features = []
        for feature in self.feature_names:
            features.append(horse_data.get(feature, 0))
        
        features_array = np.array(features).reshape(1, -1)
        
        # Scale if needed
        if model_name in ['logistic_regression', 'neural_network']:
            features_array = self.scaler.transform(features_array)
        
        # Make prediction
        model = self.models[model_name]
        win_probability = model.predict_proba(features_array)[0, 1]
        
        return win_probability
    
    def predict_race(self, race_data: list, model_name: str = 'gradient_boosting') -> list:
        """Make predictions for all horses in a race."""
        predictions = []
        
        for horse_data in race_data:
            win_prob = self.predict(horse_data, model_name)
            predictions.append({
                'horse_name': horse_data.get('horse_name', 'Unknown'),
                'win_probability': win_prob,
                'model_used': model_name
            })
        
        # Sort by win probability
        predictions.sort(key=lambda x: x['win_probability'], reverse=True)
        return predictions

# Example usage
if __name__ == "__main__":
    predictor = ProductionMLPredictor()
    
    # Example horse data
    example_horse = {
        'log_odds': 1.5,
        'implied_probability': 0.2,
        'odds_rank': 3,
        'is_favorite': 0,
        'combined_performance': 0.15,
        'field_size': 12,
        'min_odds': 2.0,
        'max_odds': 50.0,
        'avg_odds': 8.5,
        'draw_percentile': 0.4,
        'weight_percentile': 0.6,
        'age_category': 1,
        'horse_age': 4,
        'horse_weight_kg': 57,
        'draw': 8,
        'jockey_win_pct': 0.12,
        'trainer_win_pct': 0.18
    }
    
    win_prob = predictor.predict(example_horse)
    print(f"Win probability: {win_prob:.4f}")
'''

        interface_file = self.models_dir / "production_predictor.py"
        with open(interface_file, "w") as f:
            f.write(interface_code)

        logger.info(f"📝 Created prediction interface: {interface_file}")

    def run_complete_training(self) -> None:
        """Run the complete training pipeline."""
        logger.info("🎯 Starting Production ML Training Pipeline")
        logger.info("=" * 60)

        # Load data
        df = self.load_current_data()

        # Engineer features
        df_features = self.engineer_features(df)

        # Prepare training data
        X, y = self.prepare_training_data(df_features)

        # Train models
        results = self.train_models(X, y)

        # Save models
        self.save_models()

        # Create prediction interface
        self.create_prediction_interface()

        # Print summary
        logger.info("\n🏆 PRODUCTION TRAINING COMPLETE!")
        logger.info("=" * 60)
        logger.info("📊 Model Performance Summary:")

        for name, result in results.items():
            logger.info(f"   {name}:")
            logger.info(f"     AUC: {result['test_auc']:.4f}")
            logger.info(f"     Accuracy: {result['test_accuracy']:.4f}")
            logger.info(f"     F1-Score: {result['test_f1']:.4f}")

        # Find best model
        best_model = max(results.keys(), key=lambda k: results[k]["test_auc"])
        best_auc = results[best_model]["test_auc"]

        logger.info(f"\n🥇 Best Model: {best_model} (AUC: {best_auc:.4f})")
        logger.info(f"📁 Models saved to: {self.models_dir}")
        logger.info(f"🎯 Feature count: {len(self.feature_names)}")
        logger.info("✅ Ready for production use!")


def main():
    """Main training function."""
    trainer = ProductionMLTrainer()
    trainer.run_complete_training()


if __name__ == "__main__":
    main()
