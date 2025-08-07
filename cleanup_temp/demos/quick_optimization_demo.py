#!/usr/bin/env python3
"""
Quick Performance Optimization Demo
Creates a smaller dataset and runs optimization pipeline
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from imblearn.over_sampling import BorderlineSMOTE
import warnings

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_quick_dataset(n_samples=5000):
    """Create a quick synthetic dataset for testing optimization"""
    logger.info(f"🔧 Creating synthetic dataset with {n_samples:,} samples...")

    np.random.seed(42)

    # Generate synthetic features similar to horse racing data
    data = {
        # Horse characteristics
        "age": np.random.choice(
            [2, 3, 4, 5, 6, 7, 8],
            size=n_samples,
            p=[0.15, 0.25, 0.20, 0.15, 0.10, 0.10, 0.05],
        ),
        "rating": np.random.normal(75, 15, n_samples).clip(40, 130),
        "form_rating": np.random.normal(75, 12, n_samples).clip(30, 140),
        "career_wins": np.random.poisson(3, n_samples),
        "career_runs": np.random.poisson(12, n_samples) + 1,
        # Jockey and trainer
        "jockey_skill": np.random.normal(75, 12, n_samples).clip(50, 95),
        "trainer_skill": np.random.normal(75, 10, n_samples).clip(60, 95),
        "jockey_win_pct": np.random.uniform(5, 25, n_samples),
        "trainer_win_pct": np.random.uniform(10, 30, n_samples),
        # Race conditions
        "distance_meters": np.random.choice([1200, 1400, 1600, 2000, 2400], n_samples),
        "num_runners": np.random.choice([6, 8, 10, 12, 14, 16], n_samples),
        "draw": np.random.randint(1, 17, n_samples),
        "weight_lbs": np.random.randint(110, 140, n_samples),
        "odds_decimal": np.random.exponential(5, n_samples) + 1.1,
        # Track and weather
        "track_condition_num": np.random.choice(
            [0, 1, 2, 3, 4, 5], n_samples, p=[0.05, 0.1, 0.15, 0.3, 0.25, 0.15]
        ),
        "weather_num": np.random.choice(
            [-2, -1, 0, 1, 2, 3], n_samples, p=[0.05, 0.1, 0.15, 0.25, 0.25, 0.2]
        ),
        # Experience factors
        "days_since_last_run": np.random.exponential(30, n_samples).clip(7, 200),
        "course_wins": np.random.poisson(1, n_samples),
        "distance_wins": np.random.poisson(2, n_samples),
        "course_and_distance_wins": np.random.poisson(0.5, n_samples),
    }

    df = pd.DataFrame(data)

    # Engineering advanced features
    df["horse_win_rate"] = df["career_wins"] / (df["career_runs"] + 1)
    df["performance_index"] = (
        df["rating"] * 0.4
        + df["form_rating"] * 0.3
        + df["jockey_skill"] * 0.2
        + df["trainer_skill"] * 0.1
    )
    df["odds_rank"] = df.groupby(df.index // df["num_runners"])["odds_decimal"].rank()
    df["rating_rank"] = df.groupby(df.index // df["num_runners"])["rating"].rank(
        ascending=False
    )
    df["jockey_trainer_synergy"] = df["jockey_skill"] * df["trainer_skill"] / 100
    df["weight_rating_ratio"] = df["weight_lbs"] / (df["rating"] + 1)
    df["draw_field_size_ratio"] = df["draw"] / df["num_runners"]
    df["recency_factor"] = 1 / (1 + df["days_since_last_run"] / 30)
    df["experience_factor"] = np.log1p(df["career_runs"])

    # Create realistic target based on multiple factors
    win_probability = (
        (df["rating"] - 75) / 100 * 0.3
        + (df["jockey_skill"] - 75) / 100 * 0.2
        + (df["trainer_skill"] - 75) / 100 * 0.1
        + df["horse_win_rate"] * 0.2
        + (1 / df["odds_decimal"]) * 0.1
        + df["recency_factor"] * 0.05
        + np.random.normal(0, 0.1, n_samples) * 0.05
    ).clip(0.01, 0.99)

    # Generate wins based on probability
    y = np.random.binomial(1, win_probability, n_samples)

    logger.info(f"✅ Dataset created: {len(df)} samples, {len(df.columns)} features")
    logger.info(f"🎯 Win rate: {y.mean():.1%}")

    return df, y


def quick_optimization_demo():
    """Quick demo of optimization techniques"""
    logger.info("🚀 STARTING QUICK PERFORMANCE OPTIMIZATION DEMO")
    logger.info("=" * 60)

    # Create dataset
    X, y = create_quick_dataset(5000)

    # Models to test
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "Neural Network": MLPClassifier(
            hidden_layer_sizes=(50,), random_state=42, max_iter=1000
        ),
        "Logistic Regression": LogisticRegression(
            random_state=42, max_iter=5000, solver="liblinear"
        ),
    }

    logger.info(f"\n📊 Testing {len(models)} models...")

    # Baseline results
    baseline_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=3, scoring="roc_auc", n_jobs=-1)
        baseline_results[name] = scores.mean()
        logger.info(f"  📈 {name}: {scores.mean():.4f} ± {scores.std():.4f}")

    # Apply scaling
    logger.info(f"\n🔧 Applying StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    scaled_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_scaled, y, cv=3, scoring="roc_auc", n_jobs=-1)
        scaled_results[name] = scores.mean()
        improvement = scores.mean() - baseline_results[name]
        logger.info(
            f"  📈 {name}: {scores.mean():.4f} ± {scores.std():.4f} "
            f"(+{improvement:+.4f})"
        )

    # Apply SMOTE balancing
    logger.info(f"\n⚖️ Applying BorderlineSMOTE...")
    smote = BorderlineSMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

    logger.info(f"   Original: {len(y)} samples, {y.mean():.1%} win rate")
    logger.info(
        f"   Resampled: {len(y_resampled)} samples, {y_resampled.mean():.1%} win rate"
    )

    smote_results = {}
    for name, model in models.items():
        scores = cross_val_score(
            model, X_resampled, y_resampled, cv=3, scoring="roc_auc", n_jobs=-1
        )
        smote_results[name] = scores.mean()
        improvement = scores.mean() - baseline_results[name]
        logger.info(
            f"  📈 {name}: {scores.mean():.4f} ± {scores.std():.4f} "
            f"(+{improvement:+.4f})"
        )

    # Hyperparameter optimization for best model
    best_model_name = max(smote_results.keys(), key=lambda k: smote_results[k])
    logger.info(f"\n🎛️ Optimizing hyperparameters for {best_model_name}...")

    if best_model_name == "Random Forest":
        from sklearn.model_selection import GridSearchCV

        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20, None],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2],
        }
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42),
            param_grid,
            cv=3,
            scoring="roc_auc",
            n_jobs=-1,
        )
        grid_search.fit(X_resampled, y_resampled)

        improvement = grid_search.best_score_ - smote_results[best_model_name]
        logger.info(f"  🏆 Best params: {grid_search.best_params_}")
        logger.info(
            f"  📈 Best score: {grid_search.best_score_:.4f} (+{improvement:+.4f})"
        )

    # Create ensemble
    logger.info(f"\n🏗️ Creating ensemble...")
    from sklearn.ensemble import VotingClassifier

    ensemble = VotingClassifier(
        [
            ("rf", RandomForestClassifier(n_estimators=200, random_state=42)),
            ("et", ExtraTreesClassifier(n_estimators=200, random_state=42)),
            (
                "nn",
                MLPClassifier(hidden_layer_sizes=(50,), random_state=42, max_iter=1000),
            ),
            (
                "lr",
                LogisticRegression(random_state=42, max_iter=5000, solver="liblinear"),
            ),
        ],
        voting="soft",
    )

    ensemble_scores = cross_val_score(
        ensemble, X_resampled, y_resampled, cv=3, scoring="roc_auc", n_jobs=-1
    )
    best_single = max(smote_results.values())
    ensemble_improvement = ensemble_scores.mean() - best_single

    logger.info(
        f"  📈 Ensemble: {ensemble_scores.mean():.4f} ± {ensemble_scores.std():.4f}"
    )
    logger.info(
        f"  🚀 Improvement over best single model: +{ensemble_improvement:+.4f}"
    )

    # Summary
    logger.info(f"\n🎉 OPTIMIZATION SUMMARY")
    logger.info("=" * 40)
    logger.info(
        f"📊 Original best model: {max(baseline_results, key=baseline_results.get)} "
        f"({max(baseline_results.values()):.4f})"
    )
    logger.info(f"🔧 After scaling: {max(scaled_results.values()):.4f}")
    logger.info(f"⚖️ After SMOTE: {max(smote_results.values()):.4f}")
    logger.info(f"🏗️ Final ensemble: {ensemble_scores.mean():.4f}")

    total_improvement = ensemble_scores.mean() - max(baseline_results.values())
    logger.info(
        f"🚀 TOTAL IMPROVEMENT: +{total_improvement:+.4f} "
        f"({total_improvement/max(baseline_results.values())*100:+.1f}%)"
    )

    return {
        "baseline": baseline_results,
        "scaled": scaled_results,
        "smote": smote_results,
        "ensemble": ensemble_scores.mean(),
        "total_improvement": total_improvement,
    }


if __name__ == "__main__":
    results = quick_optimization_demo()
