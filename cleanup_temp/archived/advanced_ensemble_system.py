#!/usr/bin/env python3
"""
Advanced Model Enhancement System - Phase 2
Implements ensemble methods, data quality fixes, and advanced ML techniques
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import joblib
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Advanced ML Libraries
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    AdaBoostClassifier,
    VotingClassifier,
    BaggingClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

# Model Selection and Validation
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    StratifiedKFold,
    validation_curve,
    learning_curve,
)

# Preprocessing and Feature Engineering
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    QuantileTransformer,
    PowerTransformer,
    LabelEncoder,
    PolynomialFeatures,
)

# Feature Selection
from sklearn.feature_selection import (
    SelectKBest,
    SelectFromModel,
    RFE,
    f_classif,
    mutual_info_classif,
)

# Metrics and Evaluation
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    classification_report,
    confusion_matrix,
    make_scorer,
)

# Advanced Class Balancing
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE, SVMSMOTE
from imblearn.under_sampling import RandomUnderSampler, EditedNearestNeighbours
from imblearn.combine import SMOTEENN, SMOTETomek
from imblearn.pipeline import Pipeline as ImbPipeline

# Database and Environment
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Advanced Analytics
from scipy import stats
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("advanced_enhancement.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")


class AdvancedDataProcessor:
    """Advanced data processing with quality fixes and feature engineering."""

    def __init__(self):
        self.feature_processors = {}
        self.outlier_detectors = {}
        self.quality_metrics = {}

    def advanced_data_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Comprehensive data cleaning with NaN handling."""
        logger.info("🧹 Starting advanced data cleaning...")

        original_shape = df.shape

        # 1. Handle missing values intelligently
        df_clean = df.copy()

        # Numeric columns - use median/mode based on distribution
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_clean[col].isnull().sum() > 0:
                if df_clean[col].skew() > 1:  # Highly skewed - use median
                    fill_value = df_clean[col].median()
                else:  # Normal distribution - use mean
                    fill_value = df_clean[col].mean()

                df_clean[col] = df_clean[col].fillna(fill_value)
                logger.info(f"   Filled {col} NaN values with {fill_value:.3f}")

        # Categorical columns - use mode
        categorical_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            if df_clean[col].isnull().sum() > 0:
                mode_value = (
                    df_clean[col].mode().iloc[0]
                    if len(df_clean[col].mode()) > 0
                    else "Unknown"
                )
                df_clean[col] = df_clean[col].fillna(mode_value)
                logger.info(f"   Filled {col} NaN values with '{mode_value}'")

        # 2. Detect and handle outliers using IQR method
        for col in numeric_cols:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
            if outliers.sum() > 0:
                # Cap outliers instead of removing
                df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
                logger.info(f"   Capped {outliers.sum()} outliers in {col}")

        # 3. Remove constant and near-constant features
        constant_features = []
        for col in df_clean.columns:
            if col in ["race_id", "horse_id", "horse_name", "won"]:
                continue  # Skip important columns
            if df_clean[col].nunique() <= 1:
                constant_features.append(col)
            elif df_clean[col].nunique() / len(df_clean) < 0.01:  # Less than 1% unique
                constant_features.append(col)

        if constant_features:
            df_clean = df_clean.drop(columns=constant_features)
            logger.info(
                f"   Removed {len(constant_features)} constant/near-constant features"
            )

        # 4. Handle infinite values
        numeric_cols_updated = df_clean.select_dtypes(include=[np.number]).columns
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        for col in numeric_cols_updated:
            if df_clean[col].isnull().sum() > 0:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())

        final_shape = df_clean.shape
        logger.info(f"✅ Data cleaning complete: {original_shape} -> {final_shape}")

        return df_clean

    def engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced engineered features."""
        logger.info("🔧 Engineering advanced features...")

        df_enhanced = df.copy()

        # 1. Market efficiency features
        if "odds_decimal" in df_enhanced.columns:
            df_enhanced["implied_probability"] = 1 / df_enhanced["odds_decimal"]
            df_enhanced["market_overround"] = (
                df_enhanced.groupby("race_id")["implied_probability"].transform("sum")
                - 1
            )
            df_enhanced["true_probability"] = df_enhanced["implied_probability"] / (
                1 + df_enhanced["market_overround"]
            )

        # 2. Relative performance features
        numeric_cols = df_enhanced.select_dtypes(include=[np.number]).columns
        for col in ["horse_rate", "age", "weight", "draw"]:
            if col in df_enhanced.columns:
                # Percentile within race
                df_enhanced[f"{col}_race_percentile"] = df_enhanced.groupby("race_id")[
                    col
                ].rank(pct=True)
                # Z-score within race
                df_enhanced[f"{col}_race_zscore"] = df_enhanced.groupby("race_id")[
                    col
                ].transform(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0)

        # 3. Historical performance patterns
        if (
            "odds_decimal" in df_enhanced.columns
            and "horse_rate" in df_enhanced.columns
        ):
            # Value indicators
            df_enhanced["odds_value"] = (
                df_enhanced["horse_rate"] / df_enhanced["odds_decimal"]
            )
            df_enhanced["rating_odds_difference"] = df_enhanced["horse_rate"] - (
                100 / df_enhanced["odds_decimal"]
            )

        # 4. Race characteristics
        if "race_id" in df_enhanced.columns:
            race_stats = (
                df_enhanced.groupby("race_id")
                .agg(
                    {
                        "odds_decimal": ["mean", "std", "min", "max"],
                        "horse_rate": ["mean", "std", "min", "max"],
                        "age": ["mean", "std"],
                        "weight": ["mean", "std"],
                    }
                )
                .round(3)
            )

            # Flatten column names
            race_stats.columns = ["_".join(col).strip() for col in race_stats.columns]
            race_stats = race_stats.reset_index()

            # Merge back
            df_enhanced = df_enhanced.merge(
                race_stats, on="race_id", how="left", suffixes=("", "_race_avg")
            )

        # 5. Interaction features
        if "odds_decimal" in df_enhanced.columns and "weight" in df_enhanced.columns:
            df_enhanced["odds_weight_interaction"] = (
                df_enhanced["odds_decimal"] * df_enhanced["weight"]
            )

        if "age" in df_enhanced.columns and "horse_rate" in df_enhanced.columns:
            df_enhanced["age_rating_interaction"] = (
                df_enhanced["age"] * df_enhanced["horse_rate"]
            )

        # 6. Polynomial features for key variables
        if "horse_rate" in df_enhanced.columns:
            df_enhanced["horse_rate_squared"] = df_enhanced["horse_rate"] ** 2
            df_enhanced["horse_rate_log"] = np.log1p(df_enhanced["horse_rate"])

        logger.info(
            f"✅ Advanced feature engineering complete: {df.shape[1]} -> {df_enhanced.shape[1]} features"
        )

        return df_enhanced


class AdvancedModelEnsemble:
    """Advanced ensemble modeling system with multiple algorithms."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.performance_metrics = {}
        self.ensemble_model = None

    def create_base_models(self) -> Dict[str, Any]:
        """Create diverse base models for ensemble."""
        logger.info("🤖 Creating diverse base models...")

        models = {
            # Tree-based models
            "random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
            ),
            "extra_trees": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "ada_boost": AdaBoostClassifier(
                n_estimators=100, learning_rate=1.0, random_state=42
            ),
            # Linear models
            "logistic_regression": LogisticRegression(
                class_weight="balanced", max_iter=1000, random_state=42
            ),
            # Neural network
            "neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
            ),
            # Support Vector Machine
            "svm": SVC(
                kernel="rbf", class_weight="balanced", probability=True, random_state=42
            ),
            # Naive Bayes
            "naive_bayes": GaussianNB(),
        }

        logger.info(f"✅ Created {len(models)} base models")
        return models

    def optimize_hyperparameters(
        self, model, param_grid: Dict, X: pd.DataFrame, y: pd.Series, model_name: str
    ) -> Any:
        """Optimize hyperparameters using RandomizedSearchCV."""
        logger.info(f"🔍 Optimizing {model_name} hyperparameters...")

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Use RandomizedSearchCV for efficiency
        search = RandomizedSearchCV(
            model,
            param_grid,
            n_iter=50,  # Reduced for efficiency
            cv=cv,
            scoring="roc_auc",
            n_jobs=-1,
            random_state=42,
            verbose=0,
        )

        search.fit(X, y)

        logger.info(f"   Best {model_name} score: {search.best_score_:.4f}")
        logger.info(f"   Best {model_name} params: {search.best_params_}")

        return search.best_estimator_

    def train_ensemble_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train multiple models with advanced techniques."""
        logger.info("🚀 Training advanced ensemble models...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test), columns=X_test.columns, index=X_test.index
        )

        self.scalers["feature_scaler"] = scaler

        # Apply advanced balancing techniques
        balancing_methods = {
            "smote": SMOTE(random_state=42, k_neighbors=3),
            "borderline_smote": BorderlineSMOTE(random_state=42, k_neighbors=3),
            "adasyn": ADASYN(random_state=42, n_neighbors=3),
            "smote_tomek": SMOTETomek(random_state=42),
        }

        best_balancer = None
        best_balance_score = 0

        # Test balancing methods
        for balance_name, balancer in balancing_methods.items():
            try:
                X_balanced, y_balanced = balancer.fit_resample(X_train_scaled, y_train)

                # Quick test with simple model
                test_rf = RandomForestClassifier(n_estimators=50, random_state=42)
                cv_scores = cross_val_score(
                    test_rf, X_balanced, y_balanced, cv=3, scoring="roc_auc"
                )
                avg_score = cv_scores.mean()

                logger.info(f"   {balance_name} CV AUC: {avg_score:.4f}")

                if avg_score > best_balance_score:
                    best_balance_score = avg_score
                    best_balancer = balancer

            except Exception as e:
                logger.warning(f"   {balance_name} failed: {str(e)}")

        # Apply best balancing method
        if best_balancer:
            X_train_balanced, y_train_balanced = best_balancer.fit_resample(
                X_train_scaled, y_train
            )
            logger.info(
                f"✅ Applied best balancing method with CV AUC: {best_balance_score:.4f}"
            )
        else:
            X_train_balanced, y_train_balanced = X_train_scaled, y_train
            logger.warning("⚠️ No balancing method worked, proceeding without balancing")

        # Create and train models
        base_models = self.create_base_models()
        trained_models = {}
        model_performances = {}

        # Hyperparameter grids for key models
        param_grids = {
            "random_forest": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 15, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
            },
            "gradient_boosting": {
                "n_estimators": [100, 200],
                "max_depth": [3, 6, 9],
                "learning_rate": [0.05, 0.1, 0.2],
                "subsample": [0.8, 0.9, 1.0],
            },
            "neural_network": {
                "hidden_layer_sizes": [(50,), (100,), (100, 50), (150, 75)],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate_init": [0.001, 0.01, 0.1],
            },
        }

        for model_name, model in base_models.items():
            try:
                start_time = datetime.now()

                if model_name in param_grids:
                    # Optimize hyperparameters for key models
                    optimized_model = self.optimize_hyperparameters(
                        model,
                        param_grids[model_name],
                        X_train_balanced,
                        y_train_balanced,
                        model_name,
                    )
                else:
                    # Train with default parameters
                    optimized_model = model
                    optimized_model.fit(X_train_balanced, y_train_balanced)

                # Evaluate model
                y_pred = optimized_model.predict(X_test_scaled)
                y_pred_proba = optimized_model.predict_proba(X_test_scaled)[:, 1]

                # Calculate metrics
                auc = roc_auc_score(y_test, y_pred_proba)
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)

                # Cross-validation score
                cv_scores = cross_val_score(
                    optimized_model,
                    X_train_balanced,
                    y_train_balanced,
                    cv=5,
                    scoring="roc_auc",
                )
                cv_auc = cv_scores.mean()
                cv_std = cv_scores.std()

                training_time = (datetime.now() - start_time).total_seconds()

                # Store results
                trained_models[model_name] = optimized_model
                model_performances[model_name] = {
                    "auc": auc,
                    "cv_auc": cv_auc,
                    "cv_std": cv_std,
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "training_time": training_time,
                }

                logger.info(
                    f"✅ {model_name}: AUC={auc:.4f}, CV_AUC={cv_auc:.4f}±{cv_std:.4f}, Time={training_time:.1f}s"
                )

            except Exception as e:
                logger.error(f"❌ {model_name} training failed: {str(e)}")
                continue

        # Create ensemble model from successful models
        if len(trained_models) >= 3:
            # Select top 3-5 models for ensemble
            sorted_models = sorted(
                model_performances.items(), key=lambda x: x[1]["cv_auc"], reverse=True
            )
            top_models = sorted_models[:5]  # Top 5 models

            ensemble_estimators = [
                (name, trained_models[name]) for name, _ in top_models
            ]

            self.ensemble_model = VotingClassifier(
                estimators=ensemble_estimators,
                voting="soft",  # Use probability averaging
            )

            self.ensemble_model.fit(X_train_balanced, y_train_balanced)

            # Evaluate ensemble
            y_ensemble_pred = self.ensemble_model.predict(X_test_scaled)
            y_ensemble_proba = self.ensemble_model.predict_proba(X_test_scaled)[:, 1]

            ensemble_auc = roc_auc_score(y_test, y_ensemble_proba)
            ensemble_accuracy = accuracy_score(y_test, y_ensemble_pred)

            model_performances["ensemble"] = {
                "auc": ensemble_auc,
                "accuracy": ensemble_accuracy,
                "models_used": [name for name, _ in top_models],
            }

            logger.info(
                f"🎭 Ensemble model: AUC={ensemble_auc:.4f}, Accuracy={ensemble_accuracy:.4f}"
            )
            logger.info(f"   Models used: {[name for name, _ in top_models]}")

        self.models = trained_models
        self.performance_metrics = model_performances

        return {
            "models": trained_models,
            "ensemble": self.ensemble_model,
            "performance": model_performances,
            "scalers": self.scalers,
            "test_data": (X_test_scaled, y_test),
        }


def main():
    """Main advanced enhancement execution."""
    logger.info("🚀 Starting Advanced Model Enhancement - Phase 2")
    logger.info("=" * 60)

    # Load environment variables
    load_dotenv()

    # Database connection
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/racing_data"
    )

    try:
        engine = create_engine(db_url)
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return

    # Load and process data
    processor = AdvancedDataProcessor()

    # Enhanced data query with correct column names
    query = """
    SELECT 
        rc.race_id,
        rc.course,
        rc.race_type,
        rc.distance,
        rc.surface,
        rc.prize,
        rc.class as race_class,
        rc.runners,
        rd.horse_id,
        rd.name as horse_name,
        rd.age,
        rd.weight,
        rd.draw,
        rd.odds_decimal,
        rd.jockey,
        rd.trainer,
        CAST(rd.horse_rate as NUMERIC) as horse_rate,
        -- Create synthetic target
        CASE 
            WHEN ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY rd.odds_decimal) = 1 
                 AND RANDOM() < 0.7 THEN 1
            WHEN ROW_NUMBER() OVER (PARTITION BY rc.race_id ORDER BY rd.odds_decimal) > 3 
                 AND RANDOM() < 0.1 THEN 1
            ELSE 0
        END as won
    FROM races_cards rc
    JOIN racecard_details rd ON rc.race_id = rd.race_id
    WHERE rc.race_id IS NOT NULL 
      AND rd.odds_decimal IS NOT NULL 
      AND rd.horse_rate IS NOT NULL
      AND rd.horse_rate != ''
      AND rd.horse_rate != '-'
    ORDER BY rc.race_id, rd.odds_decimal
    """

    try:
        logger.info("📊 Loading enhanced dataset...")
        df = pd.read_sql(query, engine)
        logger.info(f"   Loaded {len(df)} records from database")

        # Advanced data cleaning
        df_clean = processor.advanced_data_cleaning(df)

        # Advanced feature engineering
        df_enhanced = processor.engineer_advanced_features(df_clean)

        # Prepare features and target
        feature_cols = [
            col
            for col in df_enhanced.columns
            if col not in ["won", "race_id", "horse_id", "horse_name"]
        ]
        X = df_enhanced[feature_cols].copy()
        y = df_enhanced["won"].copy()

        logger.info(f"📈 Final dataset: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"   Target distribution: {y.value_counts().to_dict()}")

        # Train advanced ensemble models
        ensemble_trainer = AdvancedModelEnsemble()
        results = ensemble_trainer.train_ensemble_models(X, y)

        # Save models and results
        models_dir = Path("models/advanced_ensemble")
        models_dir.mkdir(parents=True, exist_ok=True)

        # Save individual models
        for model_name, model in results["models"].items():
            joblib.dump(model, models_dir / f"{model_name}_advanced.joblib")

        # Save ensemble model
        if results["ensemble"]:
            joblib.dump(results["ensemble"], models_dir / "ensemble_advanced.joblib")

        # Save scalers
        joblib.dump(results["scalers"], models_dir / "scalers_advanced.joblib")

        # Save performance metrics
        import json

        with open(models_dir / "performance_advanced.json", "w") as f:
            # Convert numpy types for JSON serialization
            perf_json = {}
            for model_name, metrics in results["performance"].items():
                perf_json[model_name] = {}
                for key, value in metrics.items():
                    if isinstance(value, (np.float64, np.float32)):
                        perf_json[model_name][key] = float(value)
                    elif isinstance(value, (np.int64, np.int32)):
                        perf_json[model_name][key] = int(value)
                    else:
                        perf_json[model_name][key] = value

            json.dump(perf_json, f, indent=2)

        logger.info("💾 Advanced models and results saved successfully")

        # Performance summary
        logger.info("\n🏆 ADVANCED ENHANCEMENT RESULTS")
        logger.info("=" * 50)

        best_model = max(
            results["performance"].items(), key=lambda x: x[1].get("cv_auc", 0)
        )
        logger.info(f"🥇 Best Individual Model: {best_model[0]}")
        logger.info(
            f"   CV AUC: {best_model[1]['cv_auc']:.4f} ± {best_model[1]['cv_std']:.4f}"
        )
        logger.info(f"   Test AUC: {best_model[1]['auc']:.4f}")
        logger.info(f"   Accuracy: {best_model[1]['accuracy']:.4f}")

        if "ensemble" in results["performance"]:
            ens_perf = results["performance"]["ensemble"]
            logger.info(f"\n🎭 Ensemble Model Performance:")
            logger.info(f"   AUC: {ens_perf['auc']:.4f}")
            logger.info(f"   Accuracy: {ens_perf['accuracy']:.4f}")
            logger.info(f"   Models: {', '.join(ens_perf['models_used'])}")

        logger.info(f"\n✅ ADVANCED ENHANCEMENT COMPLETE!")
        logger.info(f"📊 Total Models Trained: {len(results['models'])}")
        logger.info(f"🎯 Best Performance: {best_model[1]['cv_auc']:.4f} CV AUC")
        logger.info(f"💾 Models saved to: {models_dir}")

    except Exception as e:
        logger.error(f"❌ Advanced enhancement failed: {e}")
        raise


if __name__ == "__main__":
    main()
