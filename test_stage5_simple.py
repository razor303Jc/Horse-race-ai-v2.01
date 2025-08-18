#!/usr/bin/env python3
"""
🧪 Stage 5 Manual Test & Development (Simple Version)
====================================================

Create test models and run Stage 5 model validation using only built-in sklearn.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_models():
    """Create some test ML models for Stage 5 validation"""
    logger.info("🚀 Creating test models for Stage 5 validation...")

    # Create models directory
    models_dir = Path("/app/models")
    models_dir.mkdir(exist_ok=True)

    # Generate sample training data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20

    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, 3, n_samples)  # 3-class classification

    feature_names = [f"feature_{i}" for i in range(n_features)]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create and train different model types
    models_to_create = {
        "random_forest_win_predictor": RandomForestClassifier(
            n_estimators=100, random_state=42
        ),
        "random_forest_place_predictor": RandomForestClassifier(
            n_estimators=50, random_state=42
        ),
        "logistic_regression_win": LogisticRegression(random_state=42, max_iter=1000),
    }

    created_models = []

    for model_name, model in models_to_create.items():
        try:
            logger.info(f"📊 Training {model_name}...")

            # Train the model
            model.fit(X_train, y_train)

            # Add some metadata
            model.feature_names_in_ = feature_names
            model.training_accuracy_ = model.score(X_train, y_train)
            model.test_accuracy_ = model.score(X_test, y_test)
            model.trained_at_ = datetime.now().isoformat()

            # Save the model
            model_path = models_dir / f"{model_name}.joblib"
            joblib.dump(model, model_path)

            logger.info(f"✅ Saved {model_name} to {model_path}")
            logger.info(f"   Training accuracy: {model.training_accuracy_:.3f}")
            logger.info(f"   Test accuracy: {model.test_accuracy_:.3f}")

            created_models.append(str(model_path))

        except Exception as e:
            logger.error(f"❌ Failed to create {model_name}: {e}")

    return created_models


def run_stage5_validation():
    """Run Stage 5 model validation"""
    logger.info("🔍 Running Stage 5 model validation...")

    try:
        # Import the model validator
        import sys

        sys.path.append("/app/tools/pipeline")
        from phase5_model_validator import ModelValidator

        # Create validator and run validation
        validator = ModelValidator()

        # Discover models
        discovered_models = validator.discover_trained_models()
        logger.info(f"📋 Discovered {len(discovered_models)} models")

        # Validate each model
        validated_models = []
        for model_path in discovered_models:
            validation_result = validator.validate_model_file(model_path)
            validated_models.append(validation_result)

            status = validation_result["validation_status"]
            logger.info(f"   {model_path.name}: {status}")

        # Organize for production
        if validated_models:
            success = validator.organize_production_models(validated_models)
            if success:
                logger.info("✅ Stage 5 model validation completed successfully!")
                return True
            else:
                logger.error("❌ Failed to organize models for production")
                return False
        else:
            logger.warning("⚠️ No models found to validate")
            return False

    except Exception as e:
        logger.error(f"❌ Stage 5 validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    logger.info("🧪 Starting Stage 5 Test & Development")

    # Step 1: Create test models
    created_models = create_test_models()

    if created_models:
        logger.info(f"✅ Created {len(created_models)} test models")

        # Step 2: Run Stage 5 validation
        validation_success = run_stage5_validation()

        if validation_success:
            logger.info("🎉 Stage 5 test completed successfully!")
        else:
            logger.error("❌ Stage 5 test failed")
    else:
        logger.error("❌ No test models created")


if __name__ == "__main__":
    main()
