#!/usr/bin/env python3
"""
🔧 Stage 5 Enhanced Test
=======================

Enhanced test for Stage 5 that creates proper test models and validates them.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_realistic_test_models():
    """Create realistic test models with proper metadata"""
    logger.info("🚀 Creating realistic test models...")

    models_dir = Path("/app/models")
    models_dir.mkdir(exist_ok=True)

    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 15

    X = np.random.rand(n_samples, n_features)
    y_win = np.random.randint(0, 2, n_samples)  # Win/lose
    y_place = np.random.randint(0, 3, n_samples)  # Win/place/lose

    feature_names = [
        "horse_age",
        "jockey_rating",
        "trainer_rating",
        "track_condition",
        "distance",
        "weight",
        "odds",
        "recent_form",
        "class_rating",
        "speed_rating",
        "stamina",
        "draw_position",
        "going_preference",
        "course_form",
        "distance_form",
    ]

    # Model configurations
    models_config = {
        "win_predictor_rf": {
            "model": RandomForestClassifier(n_estimators=100, random_state=42),
            "target": y_win,
            "description": "Random Forest model for win probability prediction",
        },
        "place_predictor_rf": {
            "model": RandomForestClassifier(n_estimators=50, random_state=42),
            "target": y_place,
            "description": "Random Forest model for place probability prediction",
        },
        "win_predictor_lr": {
            "model": LogisticRegression(random_state=42, max_iter=1000),
            "target": y_win,
            "description": "Logistic regression model for win probability",
        },
    }

    created_models = []

    for model_name, config in models_config.items():
        try:
            logger.info(f"📊 Training {model_name}...")

            model = config["model"]
            target = config["target"]

            # Train the model
            model.fit(X, target)

            # Add comprehensive metadata
            model.feature_names_in_ = np.array(feature_names)
            model.training_accuracy_ = float(model.score(X, target))
            model.trained_at_ = datetime.now().isoformat()
            model.model_description_ = config["description"]
            model.model_version_ = "1.0.0"
            model.n_features_trained_ = int(n_features)
            model.n_samples_trained_ = int(n_samples)

            # Save the model
            model_path = models_dir / f"{model_name}.joblib"
            joblib.dump(model, model_path)

            logger.info(f"✅ Saved {model_name}")
            logger.info(f"   Accuracy: {model.training_accuracy_:.3f}")
            logger.info(f"   Features: {n_features}")

            created_models.append(str(model_path))

        except Exception as e:
            logger.error(f"❌ Failed to create {model_name}: {e}")

    return created_models


def test_stage5_workflow():
    """Test the complete Stage 5 workflow"""
    logger.info("🧪 Testing Stage 5 workflow...")

    try:
        # Step 1: Create test models
        created_models = create_realistic_test_models()

        if not created_models:
            logger.error("❌ No models created for testing")
            return False

        logger.info(f"✅ Created {len(created_models)} test models")

        # Step 2: Import and run Stage 5 validator
        import sys

        sys.path.append("/app/tools/pipeline")
        from phase5_model_validator import ModelValidator

        validator = ModelValidator()

        # Step 3: Discover models
        discovered_models = validator.discover_trained_models()
        logger.info(f"📋 Discovered {len(discovered_models)} models")

        # Step 4: Validate models
        validated_models = []
        for model_path in discovered_models:
            validation_result = validator.validate_model_file(model_path)
            validated_models.append(validation_result)

            status = validation_result["validation_status"]
            model_type = validation_result.get("model_type", "unknown")
            logger.info(f"   📊 {model_path.name}: {status} ({model_type})")

        # Step 5: Organize for production
        if validated_models:
            success = validator.organize_production_models(validated_models)
            if success:
                logger.info("✅ Models organized for production")
            else:
                logger.error("❌ Failed to organize models")
                return False

        # Step 6: Create metadata
        metadata_success = validator.create_model_metadata(validated_models)
        if metadata_success:
            logger.info("✅ Model metadata created")
        else:
            logger.error("❌ Failed to create metadata")
            return False

        # Step 7: Archive training artifacts
        archive_success = validator.archive_training_artifacts()
        if archive_success:
            logger.info("✅ Training artifacts archived")

        logger.info("🎉 Stage 5 workflow completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Stage 5 workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_stage5_outputs():
    """Check the outputs created by Stage 5"""
    logger.info("🔍 Checking Stage 5 outputs...")

    # Check production directory
    production_dir = Path("/app/models/production")
    if production_dir.exists():
        production_models = list(production_dir.glob("*.joblib"))
        logger.info(f"📁 Production models: {len(production_models)}")
        for model in production_models:
            logger.info(f"   📊 {model.name}")

        # Check manifest
        manifest_file = production_dir / "production_manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
            logger.info(
                f"📋 Manifest: {len(manifest.get('active_models', []))} active models"
            )
        else:
            logger.warning("⚠️ No production manifest found")
    else:
        logger.warning("⚠️ No production directory found")

    # Check metadata
    metadata_file = Path("/app/models/model_metadata.json")
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        logger.info(
            f"📊 Metadata: {metadata.get('valid_models', 0)}/{metadata.get('total_models', 0)} valid models"
        )
    else:
        logger.warning("⚠️ No model metadata found")


def main():
    """Main function"""
    logger.info("🚀 Starting Stage 5 Enhanced Test")

    # Test the workflow
    success = test_stage5_workflow()

    if success:
        # Check outputs
        check_stage5_outputs()
        logger.info("🎉 Stage 5 enhanced test completed successfully!")
    else:
        logger.error("❌ Stage 5 enhanced test failed")


if __name__ == "__main__":
    main()
