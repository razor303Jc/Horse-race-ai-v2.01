#!/usr/bin/env python3
"""
Enhanced ML Ensemble System Integration
======================================

Integrates V2.01's multiple ensemble models (76.5% AUC performance) into the main pipeline.
This replaces basic individual models with sophisticated ensemble prediction system.

Key Features:
- 4-model ensemble: Random Forest, Gradient Boosting, Neural Network, Logistic Regression
- Consensus rating system with market features
- Performance validation and monitoring
- Automated model training and deployment
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import psycopg2
import joblib

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import V2.01 ML components
from src.horse_racing_ai.ml.v2_01_ensemble_predictor import EnsemblePredictor
from src.horse_racing_ai.ml.v2_01_consensus_rating import ConsensusRatingSystem
from src.horse_racing_ai.ml.v2_01_market_features import MarketFeatureExtractor
from src.horse_racing_ai.ml.v2_01_performance_validation import PerformanceValidator
from src.horse_racing_ai.ml.v2_01_enhanced_integration import EnhancedMLIntegrator


class EnhancedMLEnsemblePipeline:
    """
    Enhanced ML ensemble pipeline that integrates V2.01's advanced ML features
    with automated training, validation, and deployment
    """

    def __init__(self, pipeline_config=None):
        self.project_root = project_root
        self.pipeline_config = pipeline_config or {}
        self.logger = self.setup_logging()

        # Initialize V2.01 components
        self.ensemble_predictor = EnsemblePredictor()
        self.consensus_rating = ConsensusRatingSystem()
        self.market_features = MarketFeatureExtractor()
        self.performance_validator = PerformanceValidator()
        self.ml_integrator = EnhancedMLIntegrator()

        # Pipeline state
        self.ml_results = {}
        self.errors = []

    def setup_logging(self):
        """Setup pipeline logging"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = (
            log_dir
            / f"enhanced_ml_ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        return logging.getLogger(__name__)

    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5434",
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            self.cursor = self.conn.cursor()
            self.logger.info("✅ Connected to database for ML pipeline")
            return True
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False

    def load_training_data(self):
        """
        Step 1: Load and prepare training data with market features
        """
        self.logger.info("📊 Step 1: Loading training data...")

        try:
            # Load comprehensive training data
            query = """
            SELECT 
                r.race_id, r.course, r.distance, r.race_type, r.class,
                rec.horse_id, rec.horse, rec.age, rec.weight, rec.or_rating,
                rec.jockey_id, rec.jockey, rec.trainer_id, rec.trainer,
                rec.draw, rec.sp, rec.position,
                CASE WHEN rec.position = 1 THEN 1 ELSE 0 END as won
            FROM records rec
            JOIN races r ON rec.race_id = r.race_id
            WHERE rec.position IS NOT NULL 
            AND rec.sp IS NOT NULL 
            AND rec.sp > 0
            ORDER BY r.date DESC
            """

            df = pd.read_sql_query(query, self.conn)

            if df.empty:
                raise Exception("No training data found in database")

            self.logger.info(f"📊 Loaded {len(df)} training records from database")

            # Extract market features
            df_with_features = self.market_features.extract_features(df)

            self.ml_results["training_data"] = df_with_features
            self.logger.info(
                f"✅ Training data prepared with {len(df_with_features.columns)} features"
            )

            return df_with_features

        except Exception as e:
            self.logger.error(f"❌ Failed to load training data: {e}")
            self.errors.append(f"Load training data: {e}")
            return None

    def train_ensemble_models(self, training_data):
        """
        Step 2: Train V2.01 ensemble models (4-model system)
        """
        self.logger.info("🤖 Step 2: Training ensemble models...")

        try:
            # Prepare features and target
            feature_columns = [
                col
                for col in training_data.columns
                if col
                not in ["race_id", "horse", "jockey", "trainer", "position", "won"]
            ]

            X = training_data[feature_columns]
            y = training_data["won"]

            self.logger.info(
                f"Training with {len(feature_columns)} features on {len(X)} samples"
            )

            # Train ensemble predictor
            training_results = self.ensemble_predictor.train_ensemble(X, y)

            if training_results:
                self.ml_results["ensemble_training"] = training_results
                self.logger.info(f"✅ Ensemble training completed:")
                self.logger.info(
                    f"   - Random Forest AUC: {training_results.get('rf_auc', 0):.3f}"
                )
                self.logger.info(
                    f"   - Gradient Boosting AUC: {training_results.get('gb_auc', 0):.3f}"
                )
                self.logger.info(
                    f"   - Neural Network AUC: {training_results.get('nn_auc', 0):.3f}"
                )
                self.logger.info(
                    f"   - Logistic Regression AUC: {training_results.get('lr_auc', 0):.3f}"
                )
                self.logger.info(
                    f"   - Ensemble AUC: {training_results.get('ensemble_auc', 0):.3f}"
                )

                return training_results
            else:
                raise Exception("Ensemble training failed")

        except Exception as e:
            self.logger.error(f"❌ Ensemble training failed: {e}")
            self.errors.append(f"Ensemble training: {e}")
            return None

    def initialize_consensus_rating(self, training_data):
        """
        Step 3: Initialize consensus rating system
        """
        self.logger.info("🎯 Step 3: Initializing consensus rating system...")

        try:
            # Initialize consensus rating with historical data
            consensus_results = self.consensus_rating.initialize_system(training_data)

            if consensus_results:
                self.ml_results["consensus_rating"] = consensus_results
                self.logger.info(f"✅ Consensus rating system initialized")
                self.logger.info(
                    f"   - Base accuracy: {consensus_results.get('base_accuracy', 0):.3f}"
                )
                self.logger.info(
                    f"   - Confidence threshold: {consensus_results.get('confidence_threshold', 0):.3f}"
                )

                return consensus_results
            else:
                raise Exception("Consensus rating initialization failed")

        except Exception as e:
            self.logger.error(f"❌ Consensus rating initialization failed: {e}")
            self.errors.append(f"Consensus rating: {e}")
            return None

    def validate_model_performance(self, training_data):
        """
        Step 4: Validate model performance using V2.01 validation system
        """
        self.logger.info("✅ Step 4: Validating model performance...")

        try:
            # Run comprehensive performance validation
            validation_results = (
                self.performance_validator.validate_ensemble_performance(
                    self.ensemble_predictor, training_data, test_size=0.2
                )
            )

            if validation_results:
                self.ml_results["performance_validation"] = validation_results
                self.logger.info(f"✅ Performance validation completed:")
                self.logger.info(
                    f"   - Overall accuracy: {validation_results.get('accuracy', 0):.3f}"
                )
                self.logger.info(
                    f"   - Precision: {validation_results.get('precision', 0):.3f}"
                )
                self.logger.info(
                    f"   - Recall: {validation_results.get('recall', 0):.3f}"
                )
                self.logger.info(
                    f"   - F1 Score: {validation_results.get('f1_score', 0):.3f}"
                )
                self.logger.info(
                    f"   - ROC AUC: {validation_results.get('roc_auc', 0):.3f}"
                )

                # Check if performance meets V2.01 standards
                if validation_results.get("roc_auc", 0) >= 0.75:
                    self.logger.info(
                        "🎉 Model performance meets V2.01 standards (AUC >= 0.75)"
                    )
                    return validation_results
                else:
                    self.logger.warning("⚠️ Model performance below V2.01 standards")
                    return validation_results
            else:
                raise Exception("Performance validation failed")

        except Exception as e:
            self.logger.error(f"❌ Performance validation failed: {e}")
            self.errors.append(f"Performance validation: {e}")
            return None

    def deploy_enhanced_models(self):
        """
        Step 5: Deploy enhanced models with V2.01 integration
        """
        self.logger.info("🚀 Step 5: Deploying enhanced models...")

        try:
            # Deploy using enhanced integration system
            deployment_results = self.ml_integrator.deploy_ensemble_system(
                ensemble_predictor=self.ensemble_predictor,
                consensus_rating=self.consensus_rating,
                market_features=self.market_features,
            )

            if deployment_results:
                self.ml_results["deployment"] = deployment_results

                # Save models to production directory
                models_dir = self.project_root / "models" / "production"
                models_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Save ensemble predictor
                ensemble_path = models_dir / f"ensemble_predictor_{timestamp}.joblib"
                joblib.dump(self.ensemble_predictor, ensemble_path)

                # Save consensus rating system
                consensus_path = models_dir / f"consensus_rating_{timestamp}.joblib"
                joblib.dump(self.consensus_rating, consensus_path)

                # Save model metadata
                metadata = {
                    "deployment_timestamp": datetime.now().isoformat(),
                    "model_type": "v2_01_enhanced_ensemble",
                    "ensemble_auc": self.ml_results.get("ensemble_training", {}).get(
                        "ensemble_auc", 0
                    ),
                    "validation_auc": self.ml_results.get(
                        "performance_validation", {}
                    ).get("roc_auc", 0),
                    "model_files": {
                        "ensemble_predictor": str(ensemble_path),
                        "consensus_rating": str(consensus_path),
                    },
                }

                metadata_path = models_dir / f"model_metadata_{timestamp}.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

                self.logger.info(f"✅ Enhanced models deployed successfully")
                self.logger.info(f"   - Ensemble predictor: {ensemble_path.name}")
                self.logger.info(f"   - Consensus rating: {consensus_path.name}")
                self.logger.info(f"   - Metadata: {metadata_path.name}")

                return deployment_results
            else:
                raise Exception("Model deployment failed")

        except Exception as e:
            self.logger.error(f"❌ Model deployment failed: {e}")
            self.errors.append(f"Model deployment: {e}")
            return None

    def save_pipeline_results(self):
        """Save pipeline results for tracking and monitoring"""
        results_file = (
            self.project_root / "reports" / "enhanced_ml_ensemble_results.json"
        )

        pipeline_results = {
            "pipeline_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "ml_results": self.ml_results,
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }

        with open(results_file, "w") as f:
            json.dump(pipeline_results, f, indent=2, default=str)

        self.logger.info(f"Pipeline results saved to: {results_file}")
        return pipeline_results

    def run_enhanced_ml_pipeline(self):
        """
        Execute the complete enhanced ML ensemble pipeline

        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.logger.info("🚀 Starting Enhanced ML Ensemble Pipeline")
        self.logger.info("=" * 60)

        if not self.connect_to_database():
            return False

        pipeline_steps = [
            ("Load Training Data", self.load_training_data),
            (
                "Train Ensemble Models",
                lambda: self.train_ensemble_models(
                    self.ml_results.get("training_data")
                ),
            ),
            (
                "Initialize Consensus Rating",
                lambda: self.initialize_consensus_rating(
                    self.ml_results.get("training_data")
                ),
            ),
            (
                "Validate Performance",
                lambda: self.validate_model_performance(
                    self.ml_results.get("training_data")
                ),
            ),
            ("Deploy Enhanced Models", self.deploy_enhanced_models),
        ]

        success_count = 0
        total_steps = len(pipeline_steps)

        for step_name, step_function in pipeline_steps:
            self.logger.info(f"\n📋 Executing: {step_name}")
            try:
                result = step_function()
                if result is not None:
                    self.logger.info(f"✅ {step_name} completed successfully")
                    success_count += 1
                else:
                    self.logger.error(f"❌ {step_name} failed")
            except Exception as e:
                self.logger.error(f"💥 {step_name} crashed: {e}")
                self.errors.append(f"{step_name}: {e}")

        # Clean up database connection
        if hasattr(self, "conn"):
            self.conn.close()

        # Save results
        results = self.save_pipeline_results()

        # Final summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 ENHANCED ML ENSEMBLE PIPELINE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Steps completed: {success_count}/{total_steps}")
        self.logger.info(f"Errors encountered: {len(self.errors)}")

        if self.errors:
            self.logger.error("❌ Pipeline completed with errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        else:
            self.logger.info("✅ Enhanced ML ensemble pipeline completed successfully!")
            self.logger.info("🎉 V2.01 ensemble system now active!")

        return success_count == total_steps and len(self.errors) == 0


# Integration hook for main pipeline
def run_enhanced_ml_ensemble_pipeline(config=None):
    """
    Main entry point for pipeline integration
    Called by the main pipeline orchestrator
    """
    pipeline = EnhancedMLEnsemblePipeline(config)
    return pipeline.run_enhanced_ml_pipeline()


if __name__ == "__main__":
    # Allow running standalone for testing
    pipeline = EnhancedMLEnsemblePipeline()
    success = pipeline.run_enhanced_ml_pipeline()

    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Enhanced ML Ensemble Pipeline completed successfully!")
