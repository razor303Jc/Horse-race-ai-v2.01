#!/usr/bin/env python3
"""
Advanced Metrics Pipeline Integration
Automates the generation of advanced metrics for both live and historical data,
integrating with ML training pipeline.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, date
from pathlib import Path
import psycopg2

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.03")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedMetricsPipeline:
    """Automated pipeline for advanced racing metrics generation and ML integration"""

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.03")
        self.data_dir = self.project_root / "data"
        self.tools_dir = self.project_root / "tools"

        # Database connection
        self.conn = psycopg2.connect(
            host="localhost",
            port="5434",
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )

    def run_full_pipeline(self) -> dict:
        """Run the complete advanced metrics pipeline"""
        logger.info("🚀 Advanced Metrics Pipeline - FULL INTEGRATION")
        logger.info("=" * 60)

        pipeline_result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stages": {},
        }

        try:
            # Stage 1: Generate current race metrics
            logger.info("📊 Stage 1: Current Race Metrics Generation")
            current_metrics = self._generate_current_metrics()
            pipeline_result["stages"]["current_metrics"] = current_metrics

            # Stage 2: Generate historical metrics
            logger.info("🏆 Stage 2: Historical Results Metrics Generation")
            historical_metrics = self._generate_historical_metrics()
            pipeline_result["stages"]["historical_metrics"] = historical_metrics

            # Stage 3: Prepare ML training data
            logger.info("🤖 Stage 3: ML Training Data Preparation")
            ml_data = self._prepare_ml_training_data()
            pipeline_result["stages"]["ml_training_data"] = ml_data

            # Stage 4: Database validation
            logger.info("🗄️ Stage 4: Database Validation")
            db_validation = self._validate_database()
            pipeline_result["stages"]["database_validation"] = db_validation

            # Stage 5: Pipeline integration
            logger.info("⚡ Stage 5: Pipeline Integration")
            integration = self._integrate_with_pipeline()
            pipeline_result["stages"]["pipeline_integration"] = integration

            logger.info("🎉 Advanced Metrics Pipeline - COMPLETE!")
            return pipeline_result

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            pipeline_result["success"] = False
            pipeline_result["error"] = str(e)
            return pipeline_result
        finally:
            self.conn.close()

    def _generate_current_metrics(self) -> dict:
        """Generate metrics for current race entries"""
        try:
            logger.info("   📈 Running current metrics generator...")
            result = subprocess.run(
                ["python3", str(self.tools_dir / "quick_metrics_generator.py")],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                logger.info("   ✅ Current metrics generated successfully")
                return {"success": True, "output": result.stdout}
            else:
                logger.error(f"   ❌ Current metrics failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"   ❌ Error generating current metrics: {e}")
            return {"success": False, "error": str(e)}

    def _generate_historical_metrics(self) -> dict:
        """Generate metrics from historical results data"""
        try:
            logger.info("   📚 Running historical metrics generator...")
            result = subprocess.run(
                ["python3", str(self.project_root / "run_batch_historical_metrics.py")],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                logger.info("   ✅ Historical metrics generated successfully")
                return {"success": True, "output": result.stdout}
            else:
                logger.error(f"   ❌ Historical metrics failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"   ❌ Error generating historical metrics: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_ml_training_data(self) -> dict:
        """Prepare consolidated ML training data"""
        try:
            # Find latest training data files
            ml_data_dir = self.data_dir / "ml_training_data"
            training_files = list(ml_data_dir.glob("training_features_*.json"))

            if not training_files:
                return {"success": False, "error": "No training data files found"}

            # Use the latest file
            latest_file = max(training_files, key=lambda x: x.stat().st_mtime)

            with open(latest_file, "r") as f:
                training_data = json.load(f)

            # Create consolidated training dataset
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            consolidated_file = ml_data_dir / f"consolidated_training_{timestamp}.json"

            # Add current race data features
            current_features = self._extract_current_race_features()

            consolidated_data = {
                "dataset_id": f"consolidated_{timestamp}",
                "created_at": datetime.now().isoformat(),
                "historical_records": len(training_data.get("data", [])),
                "current_records": len(current_features),
                "total_records": len(training_data.get("data", []))
                + len(current_features),
                "feature_columns": [
                    "power_rating",
                    "speed_figure",
                    "pace_rating",
                    "form_score",
                    "win_probability",
                    "class_adjustment",
                    "distance_furlongs",
                    "field_size",
                    "age",
                    "weight",
                    "odds",
                    "draw_position",
                ],
                "historical_data": training_data.get("data", []),
                "current_data": current_features,
            }

            with open(consolidated_file, "w") as f:
                json.dump(consolidated_data, f, indent=2, default=str)

            logger.info(f"   ✅ ML training data prepared: {consolidated_file.name}")
            logger.info(
                f"      📊 Historical records: {consolidated_data['historical_records']}"
            )
            logger.info(
                f"      📊 Current records: {consolidated_data['current_records']}"
            )

            return {
                "success": True,
                "file": str(consolidated_file),
                "historical_records": consolidated_data["historical_records"],
                "current_records": consolidated_data["current_records"],
                "total_records": consolidated_data["total_records"],
            }

        except Exception as e:
            logger.error(f"   ❌ Error preparing ML data: {e}")
            return {"success": False, "error": str(e)}

    def _extract_current_race_features(self) -> list:
        """Extract features from current race entries for ML training"""
        try:
            cursor = self.conn.cursor()

            # Get current race data with all metrics
            cursor.execute(
                """
                SELECT DISTINCT 
                    re.horse_id, re.horse_name, re.age, re.weight_kg, re.odds_decimal, re.draw,
                    hpr.power_rating, hpr.base_rating,
                    hsr.speed_figure, hsr.pace_rating,
                    hfs.form_score,
                    mcs.win_probability, mcs.place_probability, mcs.show_probability
                FROM race_entries re
                LEFT JOIN horse_power_ratings hpr ON re.horse_id = hpr.horse_id
                LEFT JOIN horse_speed_ratings hsr ON re.horse_id = hsr.horse_id  
                LEFT JOIN horse_form_scores hfs ON re.horse_id = hfs.horse_id
                LEFT JOIN monte_carlo_simulations mcs ON re.horse_id = mcs.horse_id
                WHERE re.horse_id IS NOT NULL
                ORDER BY re.horse_id
            """
            )

            current_features = []
            for row in cursor.fetchall():
                feature_record = {
                    "horse_id": row[0],
                    "horse_name": row[1],
                    "race_date": date.today().isoformat(),
                    "data_type": "current_prediction",
                    "features": {
                        "power_rating": row[6] or 70.0,
                        "speed_figure": row[8] or 60.0,
                        "pace_rating": row[9] or 50.0,
                        "form_score": row[10] or 50.0,
                        "win_probability": row[11] or 0.1,
                        "class_adjustment": 0,
                        "distance_furlongs": 8.0,  # Default
                        "field_size": 8,  # Default
                        "age": row[2] or 4,
                        "weight": row[3] or 60.0,
                        "odds": row[4] or 10.0,
                        "draw_position": row[5] or 5,
                    },
                    "target": {
                        "finishing_position": None,  # Unknown for current races
                        "won": None,
                        "placed": None,
                    },
                }
                current_features.append(feature_record)

            return current_features

        except Exception as e:
            logger.warning(f"Error extracting current features: {e}")
            return []

    def _validate_database(self) -> dict:
        """Validate database population and data quality"""
        try:
            cursor = self.conn.cursor()

            # Check table populations
            tables = [
                "horse_power_ratings",
                "horse_speed_ratings",
                "horse_form_scores",
                "monte_carlo_simulations",
            ]
            table_stats = {}

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_stats[table] = count

            # Check data quality
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT horse_id) as unique_horses,
                    AVG(power_rating) as avg_power_rating,
                    MIN(power_rating) as min_power_rating,
                    MAX(power_rating) as max_power_rating
                FROM horse_power_ratings
            """
            )
            power_stats = cursor.fetchone()

            validation_result = {
                "success": True,
                "table_populations": table_stats,
                "data_quality": {
                    "unique_horses": power_stats[0] if power_stats else 0,
                    "avg_power_rating": (
                        float(power_stats[1]) if power_stats and power_stats[1] else 0
                    ),
                    "power_rating_range": (
                        [float(power_stats[2]), float(power_stats[3])]
                        if power_stats
                        else [0, 0]
                    ),
                },
            }

            logger.info(f"   ✅ Database validation complete")
            logger.info(
                f"      🗄️ Power ratings: {table_stats.get('horse_power_ratings', 0)} records"
            )
            logger.info(
                f"      🗄️ Speed ratings: {table_stats.get('horse_speed_ratings', 0)} records"
            )
            logger.info(
                f"      🗄️ Form scores: {table_stats.get('horse_form_scores', 0)} records"
            )
            logger.info(
                f"      🗄️ Monte Carlo: {table_stats.get('monte_carlo_simulations', 0)} records"
            )

            return validation_result

        except Exception as e:
            logger.error(f"   ❌ Database validation failed: {e}")
            return {"success": False, "error": str(e)}

    def _integrate_with_pipeline(self) -> dict:
        """Integrate with existing ML training pipeline"""
        try:
            # Create pipeline configuration
            pipeline_config = {
                "advanced_metrics_enabled": True,
                "metrics_generation": {
                    "current_races": True,
                    "historical_results": True,
                    "feature_engineering": True,
                },
                "ml_training": {
                    "use_advanced_features": True,
                    "training_data_source": "consolidated",
                    "feature_selection": [
                        "power_rating",
                        "speed_figure",
                        "pace_rating",
                        "form_score",
                        "win_probability",
                        "age",
                        "weight",
                        "odds",
                    ],
                },
                "automation": {
                    "daily_generation": True,
                    "auto_retrain": True,
                    "performance_monitoring": True,
                },
            }

            # Save configuration
            config_file = (
                self.project_root / "config" / "advanced_metrics_pipeline.json"
            )
            with open(config_file, "w") as f:
                json.dump(pipeline_config, f, indent=2)

            # Create automation script
            automation_script = self._create_automation_script()

            logger.info("   ✅ Pipeline integration complete")
            logger.info(f"      ⚙️ Configuration saved: {config_file.name}")
            logger.info(f"      🤖 Automation script: {automation_script}")

            return {
                "success": True,
                "config_file": str(config_file),
                "automation_script": automation_script,
                "features_enabled": len(
                    pipeline_config["ml_training"]["feature_selection"]
                ),
            }

        except Exception as e:
            logger.error(f"   ❌ Pipeline integration failed: {e}")
            return {"success": False, "error": str(e)}

    def _create_automation_script(self) -> str:
        """Create daily automation script"""
        automation_content = """#!/bin/bash
# Advanced Metrics Daily Automation Script
# Run this script daily to generate fresh metrics and retrain ML models

cd /home/jc/Documents/Horse-race-ai-v2.03

echo "🐎 Daily Advanced Metrics Generation - $(date)"
echo "=================================================="

# Generate current race metrics
echo "📊 Generating current race metrics..."
python3 tools/quick_metrics_generator.py

# Generate historical metrics if new results data available
echo "🏆 Processing historical results..."
python3 run_batch_historical_metrics.py

# Run ML model training with new features
echo "🤖 Training ML models with advanced features..."
python3 -c "
from src.horse_racing_ai.training.ml_trainer import MLTrainer
trainer = MLTrainer()
trainer.train_with_advanced_features()
"

# Update predictions with new models
echo "🔮 Updating predictions..."
python3 -c "
from src.horse_racing_ai.prediction.advanced_predictor import AdvancedPredictor
predictor = AdvancedPredictor()
predictor.generate_daily_predictions()
"

echo "✅ Daily advanced metrics pipeline complete!"
"""

        automation_file = self.project_root / "scripts" / "daily_advanced_metrics.sh"
        with open(automation_file, "w") as f:
            f.write(automation_content)

        # Make executable
        os.chmod(automation_file, 0o755)

        return str(automation_file)


def main():
    """Run the advanced metrics pipeline"""
    pipeline = AdvancedMetricsPipeline()
    result = pipeline.run_full_pipeline()

    print("\n" + "=" * 70)
    print("🚀 ADVANCED METRICS PIPELINE - INTEGRATION COMPLETE!")
    print("=" * 70)

    if result["success"]:
        for stage_name, stage_result in result["stages"].items():
            status = "✅" if stage_result.get("success", False) else "❌"
            print(f"{status} {stage_name.replace('_', ' ').title()}")

        print(f"\n📊 Pipeline Summary:")
        print(f"   🕐 Completed: {result['timestamp']}")
        print(f"   ⚡ Stages: {len(result['stages'])}")
        print(f"   🎯 Ready for ML Training: {'✅' if result['success'] else '❌'}")

    else:
        print(f"❌ Pipeline Failed: {result.get('error', 'Unknown error')}")

    print("=" * 70)


if __name__ == "__main__":
    main()
