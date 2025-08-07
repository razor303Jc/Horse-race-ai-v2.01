#!/usr/bin/env python3
"""
Advanced Performance Optimization Analysis
Real-world implementation of sophisticated optimization techniques
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
    StackingClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import (
    cross_val_score,
    GridSearchCV,
    RandomizedSearchCV,
    train_test_split,
)
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.metrics import roc_auc_score, classification_report
from imblearn.over_sampling import BorderlineSMOTE, ADASYN
from imblearn.combine import SMOTETomek
import warnings

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedPerformanceAnalyzer:
    """Advanced performance optimization and analysis system"""

    def __init__(self):
        self.results = {}
        self.best_models = {}

    def create_advanced_dataset(self, n_samples=10000):
        """Create a more sophisticated synthetic dataset"""
        logger.info(f"🔧 Creating advanced dataset with {n_samples:,} samples...")

        np.random.seed(42)

        # More realistic horse racing features
        data = {}

        # Horse characteristics with realistic distributions
        ages = np.random.choice(
            [2, 3, 4, 5, 6, 7, 8, 9],
            size=n_samples,
            p=[0.12, 0.22, 0.18, 0.15, 0.12, 0.10, 0.08, 0.03],
        )
        data["age"] = ages

        # Rating with age correlation
        base_ratings = np.random.normal(75, 15, n_samples)
        age_adjustments = np.where(ages <= 3, -5, np.where(ages >= 7, -3, 0))
        data["rating"] = np.clip(base_ratings + age_adjustments, 40, 130)

        # Form rating correlated with official rating
        data["form_rating"] = data["rating"] + np.random.normal(0, 8, n_samples)
        data["form_rating"] = np.clip(data["form_rating"], 30, 140)

        # Career statistics based on age and ability
        career_runs = np.maximum(
            1, np.round(ages * np.random.exponential(2.5, n_samples))
        )
        data["career_runs"] = career_runs.astype(int)

        win_prob = np.clip((data["rating"] - 60) / 80, 0.05, 0.35)
        data["career_wins"] = np.random.binomial(data["career_runs"], win_prob)

        # Jockey and trainer skills with realistic ranges
        data["jockey_skill"] = np.clip(np.random.normal(75, 12, n_samples), 50, 95)
        data["trainer_skill"] = np.clip(np.random.normal(75, 10, n_samples), 60, 95)

        # Win percentages correlated with skills
        data["jockey_win_pct"] = np.clip(
            (data["jockey_skill"] - 50) / 3 + np.random.normal(0, 3, n_samples), 5, 30
        )
        data["trainer_win_pct"] = np.clip(
            (data["trainer_skill"] - 60) / 2.5 + np.random.normal(0, 2, n_samples),
            8,
            35,
        )

        # Race conditions
        distances = np.random.choice(
            [1000, 1200, 1400, 1600, 1800, 2000, 2400, 3200],
            size=n_samples,
            p=[0.05, 0.15, 0.20, 0.25, 0.15, 0.10, 0.08, 0.02],
        )
        data["distance_meters"] = distances

        data["num_runners"] = np.random.choice(
            [6, 8, 10, 12, 14, 16, 18],
            size=n_samples,
            p=[0.05, 0.15, 0.25, 0.25, 0.15, 0.10, 0.05],
        )

        data["draw"] = np.random.randint(1, data["num_runners"] + 1)
        data["weight_lbs"] = np.random.randint(110, 140, n_samples)

        # Odds based on market efficiency with some noise
        market_rating = (
            data["rating"] * 0.6
            + data["jockey_skill"] * 0.2
            + data["trainer_skill"] * 0.2
            + np.random.normal(0, 5, n_samples)
        )
        data["odds_decimal"] = np.clip(100 / np.maximum(market_rating - 50, 5), 1.1, 50)

        # Track and weather conditions
        data["track_condition_num"] = np.random.choice(
            [0, 1, 2, 3, 4, 5], n_samples, p=[0.03, 0.07, 0.15, 0.35, 0.25, 0.15]
        )
        data["weather_num"] = np.random.choice(
            [-2, -1, 0, 1, 2, 3], n_samples, p=[0.05, 0.08, 0.12, 0.30, 0.30, 0.15]
        )

        # Experience and recency factors
        data["days_since_last_run"] = np.clip(
            np.random.exponential(35, n_samples), 7, 300
        )
        data["course_wins"] = np.random.poisson(1.2, n_samples)
        data["distance_wins"] = np.random.poisson(1.8, n_samples)
        data["course_and_distance_wins"] = np.minimum(
            data["course_wins"], data["distance_wins"]
        )

        df = pd.DataFrame(data)

        # Advanced feature engineering
        df["horse_win_rate"] = df["career_wins"] / (df["career_runs"] + 1)

        # Performance indices
        df["performance_index"] = (
            df["rating"] * 0.35
            + df["form_rating"] * 0.25
            + df["jockey_skill"] * 0.20
            + df["trainer_skill"] * 0.20
        )

        # Market analysis
        df = df.copy()  # Ensure we can group properly
        race_groups = df.index // df["num_runners"]
        df["odds_rank"] = df.groupby(race_groups)["odds_decimal"].rank()
        df["rating_rank"] = df.groupby(race_groups)["rating"].rank(ascending=False)
        df["market_confidence"] = 1 / df["odds_decimal"]

        # Interaction features
        df["jockey_trainer_synergy"] = df["jockey_skill"] * df["trainer_skill"] / 100
        df["weight_advantage"] = (df["weight_lbs"].mean() - df["weight_lbs"]) / df[
            "rating"
        ]
        df["draw_bias"] = (
            np.abs(df["draw"] - (df["num_runners"] + 1) / 2) / df["num_runners"]
        )

        # Experience factors
        df["recency_factor"] = 1 / (1 + df["days_since_last_run"] / 35)
        df["experience_factor"] = np.log1p(df["career_runs"])
        df["success_consistency"] = df["career_wins"] / np.maximum(df["career_runs"], 1)

        # Track specialization
        df["track_preference"] = (df["track_condition_num"] - 2.5) * 0.1
        df["weather_impact"] = df["weather_num"] * 0.05

        # Distance specialization
        optimal_distances = {2: 1200, 3: 1400, 4: 1600, 5: 1800, 6: 2000, 7: 2200}
        df["distance_suitability"] = (
            1
            - np.abs(
                df["distance_meters"] - df["age"].map(optimal_distances).fillna(1600)
            )
            / 800
        )
        df["distance_suitability"] = np.clip(df["distance_suitability"], 0.2, 1.0)

        # Course and distance advantages
        df["c_and_d_advantage"] = df["course_and_distance_wins"] * 0.15
        df["course_advantage"] = (
            df["course_wins"] - df["course_and_distance_wins"]
        ) * 0.08
        df["distance_advantage"] = (
            df["distance_wins"] - df["course_and_distance_wins"]
        ) * 0.05

        # Create sophisticated target variable
        win_probability = (
            # Base ability (40%)
            np.clip((df["performance_index"] - 75) / 50, -0.3, 0.3) * 0.40
            +
            # Market opinion (20%)
            np.clip((1 - df["odds_rank"] / df["num_runners"]) * 0.5, 0, 0.2) * 0.20
            +
            # Recent form and experience (15%)
            (df["horse_win_rate"] * df["recency_factor"]) * 0.15
            +
            # Track/distance suitability (10%)
            (df["distance_suitability"] + df["c_and_d_advantage"]) * 0.10
            +
            # Jockey/trainer combination (10%)
            np.clip((df["jockey_trainer_synergy"] - 75) / 25, -0.1, 0.1) * 0.10
            +
            # Draw and weight factors (5%)
            (df["weight_advantage"] - df["draw_bias"]) * 0.05
            +
            # Random racing factors
            np.random.normal(0, 0.08, n_samples)
        )

        # Ensure realistic probability range
        win_probability = np.clip(win_probability + 0.1, 0.01, 0.8)

        # Generate wins based on probability
        y = np.random.binomial(1, win_probability, n_samples)

        logger.info(
            f"✅ Advanced dataset created: {len(df)} samples, {len(df.columns)} features"
        )
        logger.info(f"🎯 Win rate: {y.mean():.1%}")
        logger.info(
            f"📊 Performance index range: {df['performance_index'].min():.1f} - {df['performance_index'].max():.1f}"
        )

        return df, y

    def comprehensive_optimization_analysis(self):
        """Run comprehensive optimization analysis"""
        logger.info("🚀 STARTING COMPREHENSIVE OPTIMIZATION ANALYSIS")
        logger.info("=" * 70)

        # Create sophisticated dataset
        X, y = self.create_advanced_dataset(10000)

        # Phase 1: Baseline Model Performance
        logger.info("\n📊 PHASE 1: BASELINE MODEL PERFORMANCE")
        logger.info("-" * 50)

        models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=100, random_state=42
            ),
            "Neural Network": MLPClassifier(
                hidden_layer_sizes=(100, 50), random_state=42, max_iter=2000
            ),
            "Logistic Regression": LogisticRegression(
                random_state=42, max_iter=5000, solver='liblinear'
            ),
            "SVM": SVC(probability=True, random_state=42),
            "AdaBoost": AdaBoostClassifier(
                n_estimators=100, random_state=42, algorithm='SAMME'
            ),
        }

        baseline_results = {}
        for name, model in models.items():
            try:
                scores = cross_val_score(
                    model, X, y, cv=3, scoring="roc_auc", n_jobs=-1
                )
                baseline_results[name] = scores.mean()
                logger.info(f"  📈 {name}: {scores.mean():.4f} ± {scores.std():.4f}")
            except Exception as e:
                logger.warning(f"  ⚠️ {name} failed: {str(e)}")

        self.results["baseline"] = baseline_results

        # Phase 2: Feature Selection Optimization
        logger.info("\n🎯 PHASE 2: FEATURE SELECTION OPTIMIZATION")
        logger.info("-" * 50)

        # Test different feature selection methods
        selectors = {
            "All Features": None,
            "Top 20 (F-score)": SelectKBest(score_func=f_classif, k=20),
            "Top 15 (F-score)": SelectKBest(score_func=f_classif, k=15),
            "RFE (15 features)": RFE(
                RandomForestClassifier(n_estimators=50, random_state=42),
                n_features_to_select=15,
            ),
        }

        best_model = max(baseline_results.items(), key=lambda x: x[1])
        test_model = models[best_model[0]]

        feature_selection_results = {}
        for sel_name, selector in selectors.items():
            try:
                if selector is None:
                    X_selected = X
                else:
                    X_selected = selector.fit_transform(X, y)

                scores = cross_val_score(
                    test_model, X_selected, y, cv=3, scoring="roc_auc", n_jobs=-1
                )
                n_features = X_selected.shape[1]
                feature_selection_results[sel_name] = {
                    "score": scores.mean(),
                    "std": scores.std(),
                    "n_features": n_features,
                }
                logger.info(
                    f"  🔍 {sel_name}: {scores.mean():.4f} ± {scores.std():.4f} ({n_features} features)"
                )
            except Exception as e:
                logger.warning(f"  ⚠️ {sel_name} failed: {str(e)}")

        self.results["feature_selection"] = feature_selection_results

        # Phase 3: Preprocessing Optimization
        logger.info("\n🔧 PHASE 3: PREPROCESSING OPTIMIZATION")
        logger.info("-" * 50)

        preprocessing_combinations = {
            "None": (None, None),
            "StandardScaler": (StandardScaler(), None),
            "RobustScaler": (RobustScaler(), None),
            "StandardScaler + SMOTE": (
                StandardScaler(),
                BorderlineSMOTE(random_state=42),
            ),
            "RobustScaler + SMOTE": (RobustScaler(), BorderlineSMOTE(random_state=42)),
            "StandardScaler + ADASYN": (StandardScaler(), ADASYN(random_state=42)),
            "StandardScaler + SMOTETomek": (
                StandardScaler(),
                SMOTETomek(random_state=42),
            ),
        }

        preprocessing_results = {}
        for prep_name, (scaler, sampler) in preprocessing_combinations.items():
            try:
                X_prep = X.copy()
                y_prep = y.copy()

                # Apply scaling
                if scaler is not None:
                    X_prep = pd.DataFrame(
                        scaler.fit_transform(X_prep), columns=X_prep.columns
                    )

                # Apply sampling
                if sampler is not None:
                    X_prep, y_prep = sampler.fit_resample(X_prep, y_prep)

                scores = cross_val_score(
                    test_model, X_prep, y_prep, cv=3, scoring="roc_auc", n_jobs=-1
                )
                preprocessing_results[prep_name] = {
                    "score": scores.mean(),
                    "std": scores.std(),
                    "sample_size": len(X_prep),
                }
                logger.info(
                    f"  🔄 {prep_name}: {scores.mean():.4f} ± {scores.std():.4f} ({len(X_prep)} samples)"
                )

            except Exception as e:
                logger.warning(f"  ⚠️ {prep_name} failed: {str(e)}")

        self.results["preprocessing"] = preprocessing_results

        # Phase 4: Hyperparameter Optimization
        logger.info("\n🎛️ PHASE 4: HYPERPARAMETER OPTIMIZATION")
        logger.info("-" * 50)

        # Get best preprocessing
        best_prep = max(preprocessing_results.items(), key=lambda x: x[1]["score"])
        logger.info(f"Using best preprocessing: {best_prep[0]}")

        scaler, sampler = preprocessing_combinations[best_prep[0]]
        X_optimized = X.copy()
        y_optimized = y.copy()

        if scaler is not None:
            X_optimized = pd.DataFrame(
                scaler.fit_transform(X_optimized), columns=X_optimized.columns
            )
        if sampler is not None:
            X_optimized, y_optimized = sampler.fit_resample(X_optimized, y_optimized)

        # Optimize top 3 models
        top_models = sorted(baseline_results.items(), key=lambda x: x[1], reverse=True)[
            :3
        ]

        hyperopt_results = {}
        for model_name, _ in top_models:
            try:
                logger.info(f"  🎯 Optimizing {model_name}...")

                if model_name == "Random Forest":
                    param_grid = {
                        "n_estimators": [100, 200, 300],
                        "max_depth": [10, 20, None],
                        "min_samples_split": [2, 5],
                        "min_samples_leaf": [1, 2],
                    }
                    model = RandomForestClassifier(random_state=42)

                elif model_name == "Extra Trees":
                    param_grid = {
                        "n_estimators": [100, 200, 300],
                        "max_depth": [10, 20, None],
                        "min_samples_split": [2, 5],
                        "min_samples_leaf": [1, 2],
                    }
                    model = ExtraTreesClassifier(random_state=42)

                elif model_name == "Gradient Boosting":
                    param_grid = {
                        "n_estimators": [100, 200],
                        "learning_rate": [0.05, 0.1, 0.2],
                        "max_depth": [3, 5, 7],
                    }
                    model = GradientBoostingClassifier(random_state=42)

                else:
                    continue

                grid_search = GridSearchCV(
                    model, param_grid, cv=3, scoring="roc_auc", n_jobs=-1
                )
                grid_search.fit(X_optimized, y_optimized)

                hyperopt_results[model_name] = {
                    "best_score": grid_search.best_score_,
                    "best_params": grid_search.best_params_,
                    "improvement": grid_search.best_score_
                    - baseline_results[model_name],
                }

                logger.info(
                    f"    ✅ Best score: {grid_search.best_score_:.4f} "
                    f"(+{grid_search.best_score_ - baseline_results[model_name]:+.4f})"
                )

            except Exception as e:
                logger.warning(f"    ⚠️ {model_name} optimization failed: {str(e)}")

        self.results["hyperparameter_optimization"] = hyperopt_results

        # Phase 5: Advanced Ensemble Creation
        logger.info("\n🏗️ PHASE 5: ADVANCED ENSEMBLE CREATION")
        logger.info("-" * 50)

        # Create optimized models
        optimized_models = []
        for model_name, results in hyperopt_results.items():
            if model_name == "Random Forest":
                model = RandomForestClassifier(
                    **results["best_params"], random_state=42
                )
            elif model_name == "Extra Trees":
                model = ExtraTreesClassifier(**results["best_params"], random_state=42)
            elif model_name == "Gradient Boosting":
                model = GradientBoostingClassifier(
                    **results["best_params"], random_state=42
                )
            else:
                continue
            optimized_models.append((model_name.lower().replace(" ", "_"), model))

        # Build ensemble with known good models that support probability prediction
        ensemble_models = [
            ("random_forest", RandomForestClassifier(n_estimators=100, random_state=42)),
            ("extra_trees", ExtraTreesClassifier(n_estimators=100, random_state=42)),
            ("gradient_boosting", GradientBoostingClassifier(n_estimators=100, random_state=42)),
            ("logistic", LogisticRegression(
                random_state=42, max_iter=5000, solver='liblinear'
            )),
            ("neural_net", MLPClassifier(
                hidden_layer_sizes=(100, 50), random_state=42, max_iter=2000
            )),
        ]

        # Test different ensemble strategies
        ensemble_strategies = {
            "Voting (Soft)": VotingClassifier(ensemble_models, voting="soft"),
            "Stacking (LR)": StackingClassifier(
                ensemble_models,
                final_estimator=LogisticRegression(
                    random_state=42, max_iter=5000, solver='liblinear'
                ),
                cv=3,
            ),
            "Stacking (RF)": StackingClassifier(
                ensemble_models,
                final_estimator=RandomForestClassifier(
                    n_estimators=50, random_state=42
                ),
                cv=3,
            ),
        }

        ensemble_results = {}
        for ens_name, ensemble in ensemble_strategies.items():
            try:
                scores = cross_val_score(
                    ensemble,
                    X_optimized,
                    y_optimized,
                    cv=3,
                    scoring="roc_auc",
                    n_jobs=-1,
                )
                ensemble_results[ens_name] = {
                    "score": scores.mean(),
                    "std": scores.std(),
                }
                logger.info(f"  🏗️ {ens_name}: {scores.mean():.4f} ± {scores.std():.4f}")
            except Exception as e:
                logger.warning(f"  ⚠️ {ens_name} failed: {str(e)}")

        self.results["ensemble"] = ensemble_results

        # Final Summary
        logger.info("\n" + "=" * 70)
        logger.info("🎉 COMPREHENSIVE OPTIMIZATION ANALYSIS COMPLETE")
        logger.info("=" * 70)

        # Calculate total improvement
        original_best = max(baseline_results.values())
        final_best = (
            max(ensemble_results.values(), key=lambda x: x["score"])["score"]
            if ensemble_results
            else original_best
        )
        total_improvement = final_best - original_best

        logger.info(
            f"📊 Original best model: {max(baseline_results.items(), key=lambda x: x[1])[0]} ({original_best:.4f})"
        )

        if feature_selection_results:
            best_fs = max(
                feature_selection_results.items(), key=lambda x: x[1]["score"]
            )
            logger.info(
                f"🎯 Best feature selection: {best_fs[0]} ({best_fs[1]['score']:.4f})"
            )

        if preprocessing_results:
            best_prep = max(preprocessing_results.items(), key=lambda x: x[1]["score"])
            logger.info(
                f"🔧 Best preprocessing: {best_prep[0]} ({best_prep[1]['score']:.4f})"
            )

        if hyperopt_results:
            best_hyperopt = max(
                hyperopt_results.items(), key=lambda x: x[1]["best_score"]
            )
            logger.info(
                f"🎛️ Best hyperopt model: {best_hyperopt[0]} ({best_hyperopt[1]['best_score']:.4f})"
            )

        if ensemble_results:
            best_ensemble = max(ensemble_results.items(), key=lambda x: x[1]["score"])
            logger.info(
                f"�️ Best ensemble: {best_ensemble[0]} ({best_ensemble[1]['score']:.4f})"
            )

        logger.info(
            f"🚀 TOTAL IMPROVEMENT: +{total_improvement:+.4f} "
            f"({total_improvement/original_best*100:+.1f}%)"
        )

        return self.results


def main():
    """Run advanced performance optimization analysis"""
    analyzer = AdvancedPerformanceAnalyzer()
    results = analyzer.comprehensive_optimization_analysis()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"advanced_optimization_results_{timestamp}.txt"

    with open(results_file, "w") as f:
        f.write("ADVANCED PERFORMANCE OPTIMIZATION RESULTS\n")
        f.write("=" * 50 + "\n\n")

        for phase, data in results.items():
            f.write(f"{phase.upper()}:\n")
            f.write("-" * 30 + "\n")
            for key, value in data.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")

    logger.info(f"📄 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
