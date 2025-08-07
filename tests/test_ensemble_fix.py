#!/usr/bin/env python3
"""
Quick test to verify the optimization fixes
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    VotingClassifier,
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_classification
import warnings

warnings.filterwarnings("ignore")


def test_ensemble_fix():
    """Test the fixed ensemble approach"""
    print("🧪 Testing fixed ensemble approach...")

    # Create synthetic data
    X, y = make_classification(
        n_samples=1000, n_features=20, n_classes=2, random_state=42
    )

    # Build ensemble with known good models
    ensemble_models = [
        ("random_forest", RandomForestClassifier(n_estimators=50, random_state=42)),
        ("extra_trees", ExtraTreesClassifier(n_estimators=50, random_state=42)),
        (
            "gradient_boosting",
            GradientBoostingClassifier(n_estimators=50, random_state=42),
        ),
        (
            "logistic",
            LogisticRegression(random_state=42, max_iter=5000, solver="liblinear"),
        ),
        (
            "neural_net",
            MLPClassifier(hidden_layer_sizes=(50,), random_state=42, max_iter=1000),
        ),
    ]

    # Test VotingClassifier
    print("Testing VotingClassifier (Soft)...")
    voting_soft = VotingClassifier(ensemble_models, voting="soft")

    try:
        scores = cross_val_score(voting_soft, X, y, cv=3, scoring="roc_auc")
        print(f"✅ VotingClassifier (Soft): {scores.mean():.4f} ± {scores.std():.4f}")

        # Test individual model probability prediction
        for name, model in ensemble_models:
            if hasattr(model, "predict_proba"):
                print(f"✅ {name}: has predict_proba")
            elif hasattr(model, "decision_function"):
                print(f"⚠️ {name}: has decision_function only")
            else:
                print(f"❌ {name}: no probability prediction")

    except Exception as e:
        print(f"❌ VotingClassifier failed: {e}")

    print("🎉 Ensemble test complete!")


if __name__ == "__main__":
    test_ensemble_fix()
