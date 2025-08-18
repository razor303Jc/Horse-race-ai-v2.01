#!/usr/bin/env python3
"""
🚀 Stage 6 Production Implementation
===================================

Production-ready Stage 6 implementation that:
1. Loads validated models from Stage 5
2. Creates a functional prediction service
3. Verifies service readiness without external dependencies
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Stage6ProductionService:
    """Production Stage 6 prediction service"""

    def __init__(self):
        self.models_dir = Path("/app/models/production")
        self.metadata_file = Path("/app/models/model_metadata.json")
        self.loaded_models = {}
        self.model_metadata = {}

    def load_and_validate_models(self) -> bool:
        """Load and validate production models from Stage 5"""
        logger.info("📊 Loading production models from Stage 5...")

        try:
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    self.model_metadata = json.load(f)
                total_models = self.model_metadata.get("total_models", 0)
                logger.info(f"✅ Found metadata for {total_models} models")

            # Load production manifest
            manifest_file = self.models_dir / "production_manifest.json"
            if not manifest_file.exists():
                logger.error("❌ No production manifest found")
                return False

            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            # Load each active model
            active_models = manifest.get("active_models", [])
            unique_models = list(set(active_models))  # Remove duplicates

            logger.info(f"🔍 Found {len(unique_models)} unique models to load")

            for model_id in unique_models[:3]:  # Load first 3 unique models
                model_info = manifest["models"].get(model_id, {})
                model_path = Path(model_info.get("file_path", ""))

                if model_path.exists():
                    try:
                        model = joblib.load(model_path)

                        # Validate model can make predictions
                        feature_count = model_info["metadata"].get("feature_count", 10)
                        test_input = np.random.rand(1, feature_count)
                        _ = model.predict(test_input)

                        self.loaded_models[model_id] = {
                            "model": model,
                            "metadata": model_info["metadata"],
                            "type": model_info["model_type"],
                            "file_path": str(model_path),
                        }
                        logger.info(f"✅ Loaded and validated: {model_id}")

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load {model_id}: {e}")

            loaded_count = len(self.loaded_models)
            logger.info(f"📊 Successfully loaded {loaded_count} models")

            return loaded_count > 0

        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            return False

    def test_prediction_capabilities(self) -> bool:
        """Test prediction capabilities of loaded models"""
        logger.info("🧪 Testing prediction capabilities...")

        if not self.loaded_models:
            logger.error("❌ No models loaded for testing")
            return False

        test_results = {}

        for model_id, model_data in self.loaded_models.items():
            try:
                model = model_data["model"]
                feature_count = model_data["metadata"].get("feature_count", 10)

                # Create test input
                test_input = np.random.rand(5, feature_count)

                # Test predictions
                predictions = model.predict(test_input)

                # Test probability predictions if available
                probabilities = None
                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba(test_input)

                test_results[model_id] = {
                    "prediction_shape": predictions.shape,
                    "has_probabilities": probabilities is not None,
                    "feature_count": feature_count,
                    "model_type": model_data["type"],
                }

                logger.info(f"✅ {model_id}: {predictions.shape} predictions")
                if probabilities is not None:
                    logger.info(f"   📊 Probabilities: {probabilities.shape}")

            except Exception as e:
                logger.error(f"❌ Prediction test failed for {model_id}: {e}")
                return False

        logger.info("🎉 All prediction tests passed!")
        return True

    def create_prediction_interface(self) -> bool:
        """Create prediction interface functions"""
        logger.info("🔮 Creating prediction interface...")

        def predict_single_horse(features: List[float], model_id: str = None):
            """Make prediction for a single horse"""
            if not model_id:
                model_id = list(self.loaded_models.keys())[0]

            if model_id not in self.loaded_models:
                raise ValueError(f"Model {model_id} not found")

            model_data = self.loaded_models[model_id]
            model = model_data["model"]
            expected_features = model_data["metadata"].get(
                "feature_count", len(features)
            )

            # Adjust feature vector length
            if len(features) < expected_features:
                features.extend([0.0] * (expected_features - len(features)))
            elif len(features) > expected_features:
                features = features[:expected_features]

            # Make prediction
            X = np.array(features).reshape(1, -1)
            prediction = model.predict(X)[0]

            probability = None
            if hasattr(model, "predict_proba"):
                probability = model.predict_proba(X)[0]

            return {
                "prediction": prediction,
                "probability": (
                    probability.tolist() if probability is not None else None
                ),
                "model_used": model_id,
                "model_type": model_data["type"],
                "timestamp": datetime.now().isoformat(),
            }

        def predict_race(horses_features: List[List[float]], model_id: str = None):
            """Make predictions for multiple horses in a race"""
            return [
                predict_single_horse(features, model_id) for features in horses_features
            ]

        # Store functions for later use
        self.predict_single_horse = predict_single_horse
        self.predict_race = predict_race

        # Test the interface
        try:
            test_features = [5.0, 75.0, 80.0, 0.6, 1200.0, 56.0, 4.5, 3.5, 75.0, 85.0]
            result = predict_single_horse(test_features)
            logger.info(f"✅ Prediction interface working")
            logger.info(f"   📊 Test prediction: {result['prediction']}")
            logger.info(f"   🎯 Model: {result['model_type']}")

            return True

        except Exception as e:
            logger.error(f"❌ Prediction interface test failed: {e}")
            return False

    def generate_service_summary(self) -> Dict:
        """Generate a summary of the prediction service"""
        summary = {
            "stage": 6,
            "service_name": "Horse Racing Prediction Service",
            "status": "operational",
            "models_loaded": len(self.loaded_models),
            "model_details": {},
            "capabilities": {
                "single_horse_prediction": True,
                "race_prediction": True,
                "probability_predictions": False,
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Add model details
        for model_id, model_data in self.loaded_models.items():
            summary["model_details"][model_id] = {
                "type": model_data["type"],
                "feature_count": model_data["metadata"].get("feature_count"),
                "classes": model_data["metadata"].get("classes"),
                "file_path": model_data["file_path"],
            }

            # Check if any model has probability predictions
            if hasattr(model_data["model"], "predict_proba"):
                summary["capabilities"]["probability_predictions"] = True

        return summary

    def run_stage6_workflow(self) -> bool:
        """Run the complete Stage 6 workflow"""
        logger.info("🚀 Starting Stage 6: Production Prediction Service")
        logger.info("=" * 60)

        # Step 1: Load and validate models
        if not self.load_and_validate_models():
            logger.error("❌ Failed to load production models")
            return False

        # Step 2: Test prediction capabilities
        if not self.test_prediction_capabilities():
            logger.error("❌ Prediction capability tests failed")
            return False

        # Step 3: Create prediction interface
        if not self.create_prediction_interface():
            logger.error("❌ Failed to create prediction interface")
            return False

        # Step 4: Generate service summary
        summary = self.generate_service_summary()

        logger.info("=" * 60)
        logger.info("🎉 Stage 6 completed successfully!")
        logger.info(f"📊 Service Status: {summary['status']}")
        logger.info(f"🤖 Models Loaded: {summary['models_loaded']}")
        logger.info(f"🔮 Capabilities: Single horse ✅, Race prediction ✅")
        logger.info(
            f"📈 Probabilities: {'✅' if summary['capabilities']['probability_predictions'] else '❌'}"
        )

        # Save summary
        summary_file = Path("/app/models/stage6_service_summary.json")
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"💾 Service summary saved: {summary_file}")

        return True


def main():
    """Main Stage 6 function"""
    logger.info("🚀 Starting Stage 6: Production Prediction Service Implementation")

    service = Stage6ProductionService()
    success = service.run_stage6_workflow()

    if success:
        logger.info("\n🎉 STAGE 6 COMPLETE!")
        logger.info("✅ Production prediction service is ready")
        logger.info("✅ Models loaded and validated")
        logger.info("✅ Prediction interface created")
        logger.info("✅ Ready for Stage 7 integration")
    else:
        logger.error("\n❌ STAGE 6 FAILED!")


if __name__ == "__main__":
    main()
