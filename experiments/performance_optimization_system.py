#!/usr/bin/env python3
"""
Performance Optimization System for Horse Racing AI v2.0
Advanced model stacking, hyperparameter optimization, and feature selection
Building upon the successful ensemble system to achieve peak performance
"""

import os
import sys
import json
import pickle
import logging
import numpy as np
import pandas as pd
import warnings
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Core ML libraries
from sklearn.model_selection import (
    cross_val_score,
    StratifiedKFold,
    GridSearchCV,
    RandomizedSearchCV,
    train_test_split,
    validation_curve,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
    StackingClassifier,
    AdaBoostClassifier,
    BaggingClassifier,
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
    f1_score,
    accuracy_score,
)
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.feature_selection import (
    SelectKBest,
    f_classif,
    mutual_info_classif,
    RFE,
    RFECV,
    SelectFromModel,
    VarianceThreshold,
)

# Advanced optimization libraries
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV, HalvingRandomSearchCV

# Feature engineering
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

# Imbalanced learning
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN
from imblearn.under_sampling import EditedNearestNeighbours
from imblearn.combine import SMOTETomek
from imblearn.ensemble import BalancedRandomForestClassifier

# Optional advanced optimization libraries (will handle import errors gracefully)
try:
    import optuna

    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

    HYPEROPT_AVAILABLE = True
except ImportError:
    HYPEROPT_AVAILABLE = False

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("performance_optimization.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")


class PerformanceOptimizer:
    """Advanced performance optimization system for ML models"""

    def __init__(self, data_path: str = "horse_racing_data.db"):
        self.data_path = data_path
        self.models_dir = "models/performance_optimized_v3"
        os.makedirs(self.models_dir, exist_ok=True)

        # Performance tracking
        self.optimization_results = {}
        self.best_models = {}
        self.feature_importance_analysis = {}

        # Advanced model configurations
        self.advanced_models = {
            "random_forest": RandomForestClassifier(random_state=42),
            "extra_trees": ExtraTreesClassifier(random_state=42),
            "gradient_boost": None,  # Will use XGBoost/LightGBM if available
            "neural_network": MLPClassifier(random_state=42),
            "logistic_regression": LogisticRegression(random_state=42),
            "svm": SVC(probability=True, random_state=42),
            "ada_boost": AdaBoostClassifier(random_state=42, algorithm="SAMME"),
            "balanced_rf": BalancedRandomForestClassifier(random_state=42),
            "ridge": RidgeClassifier(random_state=42),
            "knn": KNeighborsClassifier(),
            "naive_bayes": GaussianNB(),
            "lda": LinearDiscriminantAnalysis(),
        }

        # Hyperparameter search spaces
        self.hyperparameter_spaces = {
            "random_forest": {
                "n_estimators": [100, 200, 300, 500],
                "max_depth": [10, 20, 30, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None],
                "bootstrap": [True, False],
            },
            "extra_trees": {
                "n_estimators": [100, 200, 300, 500],
                "max_depth": [10, 20, 30, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None],
                "bootstrap": [True, False],
            },
            "neural_network": {
                "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50), (100, 100)],
                "activation": ["relu", "tanh", "logistic"],
                "solver": ["adam", "lbfgs"],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate": ["constant", "adaptive"],
            },
            "logistic_regression": {
                "C": [0.001, 0.01, 0.1, 1, 10, 100],
                "solver": ["liblinear", "lbfgs", "saga"],
                "penalty": ["l1", "l2", "elasticnet", None],
                "max_iter": [1000, 2000, 5000],
            },
            "svm": {
                "C": [0.1, 1, 10, 100],
                "gamma": ["scale", "auto", 0.001, 0.01, 0.1],
                "kernel": ["rbf", "poly", "sigmoid"],
            },
        }

        # Feature selection methods
        self.feature_selectors = {
            "variance_threshold": VarianceThreshold(threshold=0.01),
            "k_best_f_score": SelectKBest(score_func=f_classif, k=30),
            "k_best_mutual_info": SelectKBest(score_func=mutual_info_classif, k=30),
            "rfe_rf": RFE(
                RandomForestClassifier(n_estimators=100, random_state=42),
                n_features_to_select=30,
            ),
            "rfecv_rf": RFECV(
                RandomForestClassifier(n_estimators=100, random_state=42), cv=3
            ),
            "select_from_model_rf": SelectFromModel(
                RandomForestClassifier(n_estimators=100, random_state=42)
            ),
            "select_from_model_et": SelectFromModel(
                ExtraTreesClassifier(n_estimators=100, random_state=42)
            ),
        }

        # Stacking configurations
        self.stacking_configs = {
            "level_1_basic": ["random_forest", "extra_trees", "neural_network"],
            "level_1_diverse": [
                "random_forest",
                "extra_trees",
                "neural_network",
                "svm",
                "logistic_regression",
            ],
            "level_1_ensemble": [
                "random_forest",
                "extra_trees",
                "neural_network",
                "ada_boost",
                "balanced_rf",
            ],
            "level_1_comprehensive": [
                "random_forest",
                "extra_trees",
                "neural_network",
                "svm",
                "logistic_regression",
                "ada_boost",
                "balanced_rf",
                "ridge",
            ],
        }

    def load_and_prepare_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and prepare data with advanced feature engineering"""
        logger.info("🔄 Loading and preparing data for optimization...")

        try:
            import sqlite3

            conn = sqlite3.connect(self.data_path)

            # Enhanced query with more features
            query = """
            SELECT 
                rp.*,
                h.age, h.sex, h.rating, h.form_rating,
                h.career_wins, h.career_runs,
                CASE WHEN h.career_runs > 0 THEN 
                    CAST(h.career_wins AS FLOAT) / h.career_runs 
                ELSE 0 END as horse_win_rate,
                
                j.skill_rating as jockey_skill,
                j.win_percentage as jockey_win_pct,
                
                t.skill_rating as trainer_skill,
                t.win_percentage as trainer_win_pct,
                t.stable_size,
                
                rc.distance_meters, rc.track_condition, rc.weather,
                rc.prize_money, rc.num_runners,
                
                v.track_type, v.left_right_handed
                
            FROM race_participants rp
            JOIN horses h ON rp.horse_id = h.horse_id
            JOIN jockeys j ON rp.jockey_id = j.jockey_id  
            JOIN trainers t ON rp.trainer_id = t.trainer_id
            JOIN race_cards rc ON rp.race_id = rc.race_id
            JOIN venues v ON rc.venue_id = v.venue_id
            WHERE rp.actual_finish_position IS NOT NULL
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            logger.info(f"📊 Loaded {len(df):,} race records")

            # Advanced feature engineering
            df = self._engineer_advanced_features(df)

            # Prepare target variable (win = 1, others = 0)
            y = (df["actual_finish_position"] == 1).astype(int)

            # Select feature columns
            feature_cols = [
                col
                for col in df.columns
                if col
                not in [
                    "participant_id",
                    "race_id",
                    "horse_id",
                    "jockey_id",
                    "trainer_id",
                    "actual_finish_position",
                    "form_string",
                ]
            ]

            X = df[feature_cols].copy()

            # Handle missing values
            X = self._handle_missing_values(X)

            logger.info(
                f"🔧 Final dataset: {X.shape[0]:,} samples, {X.shape[1]} features"
            )
            logger.info(f"🎯 Class distribution: {y.value_counts().to_dict()}")

            return X, y

        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            raise

    def _engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer advanced features for optimization"""
        logger.info("🔧 Engineering advanced features...")

        # Performance ratios and indices
        df["performance_index"] = (
            df["rating"] * 0.4
            + df["form_rating"] * 0.3
            + df["jockey_skill"] * 0.2
            + df["trainer_skill"] * 0.1
        )

        # Market intelligence
        df["odds_rank"] = df.groupby("race_id")["odds_decimal"].rank()
        df["rating_rank"] = df.groupby("race_id")["rating"].rank(ascending=False)
        df["form_rank"] = df.groupby("race_id")["form_rating"].rank(ascending=False)

        # Advanced interactions
        df["jockey_trainer_synergy"] = df["jockey_skill"] * df["trainer_skill"] / 100
        df["weight_rating_ratio"] = df["weight_lbs"] / (df["rating"] + 1)
        df["draw_field_size_ratio"] = df["draw"] / df["num_runners"]

        # Distance and track specialization
        df["distance_category"] = pd.cut(
            df["distance_meters"],
            bins=[0, 1400, 1800, 2400, 3200, 10000],
            labels=["sprint", "mile", "middle", "staying", "extreme"],
        )

        # Prize money pressure
        df["prize_pressure"] = np.log1p(df["prize_money"]) / df["num_runners"]

        # Recency factors
        df["days_since_log"] = np.log1p(df["days_since_last_run"])
        df["recency_factor"] = 1 / (1 + df["days_since_last_run"] / 30)

        # Experience factors
        df["experience_factor"] = np.log1p(df["career_runs"])
        df["success_rate"] = df["career_wins"] / (df["career_runs"] + 1)

        # Track condition adjustments
        track_condition_map = {
            "Firm": 5,
            "Good to Firm": 4,
            "Good": 3,
            "Good to Soft": 2,
            "Soft": 1,
            "Heavy": 0,
        }
        df["track_condition_num"] = (
            df["track_condition"].map(track_condition_map).fillna(3)
        )

        # Weather impact
        weather_map = {
            "Sunny": 3,
            "Cloudy": 2,
            "Overcast": 1,
            "Light Rain": 0,
            "Heavy Rain": -1,
            "Windy": -2,
        }
        df["weather_num"] = df["weather"].map(weather_map).fillna(1)

        # Categorical encoding for important features
        df["sex_num"] = pd.Categorical(df["sex"]).codes
        df["track_type_num"] = pd.Categorical(df["track_type"]).codes
        df["handedness_num"] = pd.Categorical(df["left_right_handed"]).codes

        # Age adjustments
        df["age_factor"] = np.where(
            df["age"] <= 3, 1.1, np.where(df["age"] >= 8, 0.9, 1.0)
        )

        # Stable size impact
        df["stable_size_factor"] = np.log1p(df["stable_size"]) / 10

        # Create polynomial features for key variables
        df["rating_squared"] = df["rating"] ** 2
        df["odds_log"] = np.log1p(df["odds_decimal"])

        logger.info(
            f"✅ Feature engineering complete: {len(df.columns)} total features"
        )
        return df

    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        logger.info("🔄 Handling missing values...")

        # Fill numeric columns with median
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if X[col].isnull().any():
                X[col].fillna(X[col].median(), inplace=True)

        # Fill categorical columns with mode
        categorical_cols = X.select_dtypes(include=["object", "category"]).columns
        for col in categorical_cols:
            if X[col].isnull().any():
                X[col].fillna(
                    X[col].mode()[0] if not X[col].mode().empty else "Unknown",
                    inplace=True,
                )

        logger.info("✅ Missing values handled")
        return X

    def optimize_feature_selection(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Dict[str, Any]:
        """Optimize feature selection using multiple methods"""
        logger.info("🎯 Optimizing feature selection...")

        feature_selection_results = {}
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features for certain selectors
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        for name, selector in self.feature_selectors.items():
            try:
                logger.info(f"  🔍 Testing {name}...")

                if "scaled" in name or name in ["svm", "neural_network"]:
                    X_train_sel = selector.fit_transform(X_train_scaled, y_train)
                    X_test_sel = selector.transform(X_test_scaled)
                else:
                    X_train_sel = selector.fit_transform(X_train, y_train)
                    X_test_sel = selector.transform(X_test)

                # Quick evaluation with Random Forest
                rf = RandomForestClassifier(n_estimators=100, random_state=42)
                rf.fit(X_train_sel, y_train)

                train_score = roc_auc_score(
                    y_train, rf.predict_proba(X_train_sel)[:, 1]
                )
                test_score = roc_auc_score(y_test, rf.predict_proba(X_test_sel)[:, 1])

                n_features = X_train_sel.shape[1]

                feature_selection_results[name] = {
                    "n_features": n_features,
                    "train_auc": train_score,
                    "test_auc": test_score,
                    "overfitting": train_score - test_score,
                    "selector": selector,
                }

                logger.info(
                    f"    ✅ {name}: {n_features} features, AUC: {test_score:.4f}"
                )

            except Exception as e:
                logger.warning(f"    ⚠️ {name} failed: {str(e)}")
                continue

        # Find best feature selector
        best_selector = max(
            feature_selection_results.items(), key=lambda x: x[1]["test_auc"]
        )

        logger.info(
            f"🏆 Best feature selector: {best_selector[0]} "
            f"(AUC: {best_selector[1]['test_auc']:.4f}, "
            f"Features: {best_selector[1]['n_features']})"
        )

        self.feature_importance_analysis = feature_selection_results
        return feature_selection_results

    def optimize_hyperparameters(
        self, X: pd.DataFrame, y: pd.Series, model_name: str = "random_forest"
    ) -> Dict[str, Any]:
        """Optimize hyperparameters using advanced search strategies"""
        logger.info(f"🎛️ Optimizing hyperparameters for {model_name}...")

        if model_name not in self.hyperparameter_spaces:
            logger.warning(f"No hyperparameter space defined for {model_name}")
            return {}

        model = self.advanced_models[model_name]
        param_space = self.hyperparameter_spaces[model_name]

        optimization_results = {}

        # 1. Grid Search with Cross-Validation
        logger.info("  🔍 Running GridSearchCV...")
        try:
            grid_search = GridSearchCV(
                model, param_space, cv=3, scoring="roc_auc", n_jobs=-1, verbose=1
            )
            grid_search.fit(X, y)

            optimization_results["grid_search"] = {
                "best_params": grid_search.best_params_,
                "best_score": grid_search.best_score_,
                "cv_results": grid_search.cv_results_,
            }

            logger.info(f"    ✅ Grid Search Best AUC: {grid_search.best_score_:.4f}")

        except Exception as e:
            logger.warning(f"    ⚠️ Grid Search failed: {str(e)}")

        # 2. Randomized Search
        logger.info("  🎲 Running RandomizedSearchCV...")
        try:
            random_search = RandomizedSearchCV(
                model,
                param_space,
                n_iter=50,
                cv=3,
                scoring="roc_auc",
                n_jobs=-1,
                random_state=42,
                verbose=1,
            )
            random_search.fit(X, y)

            optimization_results["random_search"] = {
                "best_params": random_search.best_params_,
                "best_score": random_search.best_score_,
                "cv_results": random_search.cv_results_,
            }

            logger.info(
                f"    ✅ Random Search Best AUC: {random_search.best_score_:.4f}"
            )

        except Exception as e:
            logger.warning(f"    ⚠️ Random Search failed: {str(e)}")

        # 3. Halving Grid Search (if available)
        try:
            logger.info("  ⚡ Running HalvingGridSearchCV...")
            halving_search = HalvingGridSearchCV(
                model, param_space, cv=3, scoring="roc_auc", n_jobs=-1, random_state=42
            )
            halving_search.fit(X, y)

            optimization_results["halving_search"] = {
                "best_params": halving_search.best_params_,
                "best_score": halving_search.best_score_,
            }

            logger.info(
                f"    ✅ Halving Search Best AUC: {halving_search.best_score_:.4f}"
            )

        except Exception as e:
            logger.warning(f"    ⚠️ Halving Search failed: {str(e)}")

        # Find best optimization result
        best_method = max(
            optimization_results.items(), key=lambda x: x[1]["best_score"]
        )

        logger.info(
            f"🏆 Best optimization method: {best_method[0]} "
            f"(AUC: {best_method[1]['best_score']:.4f})"
        )

        return optimization_results

    def create_stacked_ensemble(
        self, X: pd.DataFrame, y: pd.Series, config_name: str = "level_1_diverse"
    ) -> Dict[str, Any]:
        """Create advanced stacked ensemble"""
        logger.info(f"🏗️ Creating stacked ensemble: {config_name}...")

        config = self.stacking_configs[config_name]

        # Prepare base models
        base_models = []
        for model_name in config:
            if model_name in self.advanced_models:
                model = self.advanced_models[model_name]
                base_models.append((model_name, model))

        # Meta-learner options
        meta_learners = {
            "logistic": LogisticRegression(random_state=42),
            "ridge": RidgeClassifier(random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "neural_network": MLPClassifier(hidden_layer_sizes=(50,), random_state=42),
        }

        stacking_results = {}

        for meta_name, meta_learner in meta_learners.items():
            logger.info(f"  🔧 Testing meta-learner: {meta_name}...")

            try:
                # Create stacking classifier
                stacking_clf = StackingClassifier(
                    estimators=base_models,
                    final_estimator=meta_learner,
                    cv=3,
                    stack_method="predict_proba",
                    n_jobs=-1,
                )

                # Cross-validation evaluation
                cv_scores = cross_val_score(
                    stacking_clf, X, y, cv=3, scoring="roc_auc", n_jobs=-1
                )

                stacking_results[meta_name] = {
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std(),
                    "cv_scores": cv_scores.tolist(),
                    "model": stacking_clf,
                }

                logger.info(
                    f"    ✅ {meta_name}: AUC {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
                )

            except Exception as e:
                logger.warning(f"    ⚠️ {meta_name} failed: {str(e)}")
                continue

        # Find best stacking configuration
        if stacking_results:
            best_stack = max(stacking_results.items(), key=lambda x: x[1]["cv_mean"])

            logger.info(
                f"🏆 Best stacking config: {best_stack[0]} "
                f"(AUC: {best_stack[1]['cv_mean']:.4f})"
            )

            return {
                "config_name": config_name,
                "best_meta_learner": best_stack[0],
                "results": stacking_results,
                "best_model": best_stack[1]["model"],
            }

        return {}

    def optimize_data_preprocessing(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Dict[str, Any]:
        """Optimize data preprocessing strategies"""
        logger.info("🔄 Optimizing data preprocessing...")

        preprocessing_results = {}

        # Test different scaling methods
        scalers = {
            "standard": StandardScaler(),
            "robust": RobustScaler(),
            "minmax": MinMaxScaler(),
            "none": None,
        }

        # Test different sampling strategies
        samplers = {
            "none": None,
            "smote": SMOTE(random_state=42),
            "borderline_smote": BorderlineSMOTE(random_state=42),
            "adasyn": ADASYN(random_state=42),
            "smote_tomek": SMOTETomek(random_state=42),
        }

        for scaler_name, scaler in scalers.items():
            for sampler_name, sampler in samplers.items():

                try:
                    logger.info(f"  🧪 Testing {scaler_name} + {sampler_name}...")

                    # Prepare data
                    X_prep = X.copy()
                    y_prep = y.copy()

                    # Apply scaling
                    if scaler is not None:
                        X_prep = pd.DataFrame(
                            scaler.fit_transform(X_prep),
                            columns=X_prep.columns,
                            index=X_prep.index,
                        )

                    # Apply sampling
                    if sampler is not None:
                        X_prep, y_prep = sampler.fit_resample(X_prep, y_prep)

                    # Quick evaluation with Random Forest
                    rf = RandomForestClassifier(n_estimators=100, random_state=42)
                    cv_scores = cross_val_score(
                        rf, X_prep, y_prep, cv=3, scoring="roc_auc", n_jobs=-1
                    )

                    combo_name = f"{scaler_name}_{sampler_name}"
                    preprocessing_results[combo_name] = {
                        "scaler": scaler_name,
                        "sampler": sampler_name,
                        "cv_mean": cv_scores.mean(),
                        "cv_std": cv_scores.std(),
                        "sample_size": len(X_prep),
                    }

                    logger.info(
                        f"    ✅ AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
                    )

                except Exception as e:
                    logger.warning(
                        f"    ⚠️ {scaler_name} + {sampler_name} failed: {str(e)}"
                    )
                    continue

        # Find best preprocessing combination
        best_prep = max(preprocessing_results.items(), key=lambda x: x[1]["cv_mean"])

        logger.info(
            f"🏆 Best preprocessing: {best_prep[0]} "
            f"(AUC: {best_prep[1]['cv_mean']:.4f})"
        )

        return preprocessing_results

    def comprehensive_model_evaluation(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Dict[str, Any]:
        """Comprehensive evaluation of all model types"""
        logger.info("📊 Comprehensive model evaluation...")

        evaluation_results = {}

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Apply best preprocessing (example: standard scaling + BorderlineSMOTE)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        sampler = BorderlineSMOTE(random_state=42)
        X_train_resampled, y_train_resampled = sampler.fit_resample(
            X_train_scaled, y_train
        )

        for model_name, model in self.advanced_models.items():
            if model is None:
                continue

            try:
                logger.info(f"  📈 Evaluating {model_name}...")

                # Train model
                model.fit(X_train_resampled, y_train_resampled)

                # Predictions
                y_train_pred = model.predict_proba(X_train_resampled)[:, 1]
                y_test_pred = model.predict_proba(X_test_scaled)[:, 1]

                # Metrics
                train_auc = roc_auc_score(y_train_resampled, y_train_pred)
                test_auc = roc_auc_score(y_test, y_test_pred)

                y_test_pred_binary = (y_test_pred > 0.5).astype(int)
                accuracy = accuracy_score(y_test, y_test_pred_binary)
                f1 = f1_score(y_test, y_test_pred_binary)

                # Cross-validation
                cv_scores = cross_val_score(
                    model,
                    X_train_resampled,
                    y_train_resampled,
                    cv=3,
                    scoring="roc_auc",
                    n_jobs=-1,
                )

                evaluation_results[model_name] = {
                    "train_auc": train_auc,
                    "test_auc": test_auc,
                    "cv_auc_mean": cv_scores.mean(),
                    "cv_auc_std": cv_scores.std(),
                    "accuracy": accuracy,
                    "f1_score": f1,
                    "overfitting": train_auc - test_auc,
                    "model": model,
                }

                logger.info(
                    f"    ✅ {model_name}: Test AUC {test_auc:.4f}, "
                    f"CV AUC {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
                )

            except Exception as e:
                logger.warning(f"    ⚠️ {model_name} failed: {str(e)}")
                continue

        return evaluation_results

    def create_ultimate_ensemble(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Create the ultimate optimized ensemble"""
        logger.info("🚀 Creating ultimate optimized ensemble...")

        # Get best models from comprehensive evaluation
        model_results = self.comprehensive_model_evaluation(X, y)

        # Select top performing models
        top_models = sorted(
            model_results.items(), key=lambda x: x[1]["test_auc"], reverse=True
        )[:5]

        logger.info("🏆 Top 5 models for ultimate ensemble:")
        for i, (name, results) in enumerate(top_models, 1):
            logger.info(f"  {i}. {name}: AUC {results['test_auc']:.4f}")

        # Create ensemble with top models
        base_estimators = [(name, results["model"]) for name, results in top_models]

        # Multiple ensemble strategies
        ensemble_strategies = {
            "voting_soft": VotingClassifier(estimators=base_estimators, voting="soft"),
            "voting_hard": VotingClassifier(estimators=base_estimators, voting="hard"),
            "stacking_lr": StackingClassifier(
                estimators=base_estimators,
                final_estimator=LogisticRegression(random_state=42),
                cv=3,
            ),
            "stacking_rf": StackingClassifier(
                estimators=base_estimators,
                final_estimator=RandomForestClassifier(
                    n_estimators=100, random_state=42
                ),
                cv=3,
            ),
        }

        ensemble_results = {}

        for strategy_name, ensemble in ensemble_strategies.items():
            try:
                logger.info(f"  🔧 Testing {strategy_name}...")

                cv_scores = cross_val_score(
                    ensemble, X, y, cv=3, scoring="roc_auc", n_jobs=-1
                )

                ensemble_results[strategy_name] = {
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std(),
                    "cv_scores": cv_scores.tolist(),
                    "model": ensemble,
                }

                logger.info(
                    f"    ✅ {strategy_name}: AUC {cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
                )

            except Exception as e:
                logger.warning(f"    ⚠️ {strategy_name} failed: {str(e)}")
                continue

        # Find best ensemble
        best_ensemble = max(ensemble_results.items(), key=lambda x: x[1]["cv_mean"])

        logger.info(
            f"🏆 Best ultimate ensemble: {best_ensemble[0]} "
            f"(AUC: {best_ensemble[1]['cv_mean']:.4f})"
        )

        return {
            "top_models": top_models,
            "ensemble_results": ensemble_results,
            "best_ensemble": best_ensemble,
        }

    def save_optimization_results(self, results: Dict[str, Any]):
        """Save all optimization results"""
        logger.info("💾 Saving optimization results...")

        # Save results as JSON
        results_file = os.path.join(self.models_dir, "optimization_results.json")
        with open(results_file, "w") as f:
            # Convert non-serializable objects
            serializable_results = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    serializable_results[key] = {
                        k: v
                        for k, v in value.items()
                        if not hasattr(v, "fit")  # Skip model objects
                    }
                else:
                    serializable_results[key] = value

            json.dump(serializable_results, f, indent=2, default=str)

        # Save best models
        if (
            "ultimate_ensemble" in results
            and "best_ensemble" in results["ultimate_ensemble"]
        ):
            best_ensemble_model = results["ultimate_ensemble"]["best_ensemble"][1][
                "model"
            ]
            model_file = os.path.join(self.models_dir, "ultimate_ensemble_model.pkl")

            with open(model_file, "wb") as f:
                pickle.dump(best_ensemble_model, f)

        logger.info(f"✅ Results saved to {self.models_dir}")

    def run_complete_optimization(self):
        """Run complete performance optimization pipeline"""
        logger.info("🚀 STARTING COMPLETE PERFORMANCE OPTIMIZATION")
        logger.info("=" * 70)

        start_time = datetime.now()

        try:
            # Load data
            X, y = self.load_and_prepare_data()

            # Optimization pipeline
            results = {}

            # 1. Feature selection optimization
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 1: FEATURE SELECTION OPTIMIZATION")
            logger.info("=" * 50)
            results["feature_selection"] = self.optimize_feature_selection(X, y)

            # 2. Preprocessing optimization
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 2: PREPROCESSING OPTIMIZATION")
            logger.info("=" * 50)
            results["preprocessing"] = self.optimize_data_preprocessing(X, y)

            # 3. Hyperparameter optimization for key models
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 3: HYPERPARAMETER OPTIMIZATION")
            logger.info("=" * 50)

            key_models = [
                "random_forest",
                "extra_trees",
                "neural_network",
                "logistic_regression",
            ]
            results["hyperparameter_optimization"] = {}

            for model_name in key_models:
                results["hyperparameter_optimization"][model_name] = (
                    self.optimize_hyperparameters(X, y, model_name)
                )

            # 4. Comprehensive model evaluation
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 4: COMPREHENSIVE MODEL EVALUATION")
            logger.info("=" * 50)
            results["model_evaluation"] = self.comprehensive_model_evaluation(X, y)

            # 5. Stacking ensemble optimization
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 5: STACKING ENSEMBLE OPTIMIZATION")
            logger.info("=" * 50)

            stacking_results = {}
            for config_name in self.stacking_configs.keys():
                stacking_results[config_name] = self.create_stacked_ensemble(
                    X, y, config_name
                )

            results["stacking_optimization"] = stacking_results

            # 6. Ultimate ensemble creation
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 6: ULTIMATE ENSEMBLE CREATION")
            logger.info("=" * 50)
            results["ultimate_ensemble"] = self.create_ultimate_ensemble(X, y)

            # Save results
            self.save_optimization_results(results)

            # Final summary
            end_time = datetime.now()
            duration = end_time - start_time

            logger.info("\n" + "=" * 70)
            logger.info("🎉 PERFORMANCE OPTIMIZATION COMPLETE!")
            logger.info("=" * 70)
            logger.info(f"⏱️  Total Duration: {duration}")
            logger.info(f"📊 Data Size: {X.shape[0]:,} samples, {X.shape[1]} features")

            # Best results summary
            if results.get("ultimate_ensemble") and results["ultimate_ensemble"].get(
                "best_ensemble"
            ):
                best_auc = results["ultimate_ensemble"]["best_ensemble"][1]["cv_mean"]
                best_method = results["ultimate_ensemble"]["best_ensemble"][0]
                logger.info(f"🏆 Best Model: {best_method}")
                logger.info(f"🎯 Best AUC: {best_auc:.4f}")

            if results.get("feature_selection"):
                best_fs = max(
                    results["feature_selection"].items(), key=lambda x: x[1]["test_auc"]
                )
                logger.info(
                    f"🔍 Best Feature Selection: {best_fs[0]} "
                    f"({best_fs[1]['n_features']} features)"
                )

            if results.get("preprocessing"):
                best_prep = max(
                    results["preprocessing"].items(), key=lambda x: x[1]["cv_mean"]
                )
                logger.info(f"🔧 Best Preprocessing: {best_prep[0]}")

            logger.info(f"💾 All results saved to: {self.models_dir}")
            logger.info("=" * 70)

            return results

        except Exception as e:
            logger.error(f"❌ Optimization failed: {str(e)}")
            raise


def main():
    """Main function to run performance optimization"""

    # Check if we have necessary data
    data_files = ["horse_racing_data.db", "massive_racing_data.db"]
    available_data = None

    for data_file in data_files:
        if os.path.exists(data_file):
            available_data = data_file
            break

    if not available_data:
        logger.error("❌ No horse racing data found. Please run data generation first.")
        return

    logger.info(f"📊 Using data file: {available_data}")

    # Create optimizer
    optimizer = PerformanceOptimizer(data_path=available_data)

    # Run complete optimization
    results = optimizer.run_complete_optimization()

    logger.info("🚀 Performance optimization complete!")


if __name__ == "__main__":
    main()
