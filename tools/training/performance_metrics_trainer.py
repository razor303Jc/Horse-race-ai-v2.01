#!/usr/bin/env python3
"""
Enhanced AI Performance Metrics Trainer
======================================
Real training with actual AI model execution and performance measurement
"""

import json
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceMetricsTrainer:
    """Real AI model trainer with comprehensive performance metrics"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.ai_model_path = self.base_dir / "src" / "ai_selections.py"
        self.metrics = {}
        self.training_start = datetime.now()

    def execute_docker_query(self, database: str, query: str) -> Optional[str]:
        """Execute SQL query via Docker and return results"""
        try:
            cmd = [
                "docker",
                "exec",
                "horse_racing_postgres_clean",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                database,
                "-t",
                "-A",
                "-F",
                "|",
                "-c",
                query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Database query failed: {result.stderr}")
                return None

            return result.stdout.strip()

        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None

    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        stats = {}

        try:
            # Main database stats
            main_count = self.execute_docker_query(
                "results_horse_racing_db", "SELECT COUNT(*) FROM records;"
            )

            races_count = self.execute_docker_query(
                "results_horse_racing_db",
                "SELECT COUNT(DISTINCT race_id) FROM records;",
            )

            horses_count = self.execute_docker_query(
                "results_horse_racing_db",
                "SELECT COUNT(DISTINCT horse_id) FROM records;",
            )

            # Enriched database stats
            power_ratings = self.execute_docker_query(
                "advanced_racing_metrics_db",
                "SELECT COUNT(*) FROM horse_power_ratings;",
            )

            speed_ratings = self.execute_docker_query(
                "advanced_racing_metrics_db",
                "SELECT COUNT(*) FROM horse_speed_pace_ratings;",
            )

            monte_carlo = self.execute_docker_query(
                "advanced_racing_metrics_db",
                "SELECT COUNT(*) FROM monte_carlo_simulations;",
            )

            stats = {
                "main_records": int(main_count) if main_count else 0,
                "unique_races": int(races_count) if races_count else 0,
                "unique_horses": int(horses_count) if horses_count else 0,
                "power_ratings": int(power_ratings) if power_ratings else 0,
                "speed_ratings": int(speed_ratings) if speed_ratings else 0,
                "monte_carlo_sims": int(monte_carlo) if monte_carlo else 0,
            }

            # Calculate derived metrics
            stats["total_enriched"] = (
                stats["power_ratings"]
                + stats["speed_ratings"]
                + stats["monte_carlo_sims"]
            )
            stats["data_richness"] = stats["total_enriched"] / max(
                stats["main_records"], 1
            )

            logger.info(f"📊 Database Statistics:")
            logger.info(f"   🏇 Main records: {stats['main_records']:,}")
            logger.info(f"   🏁 Unique races: {stats['unique_races']:,}")
            logger.info(f"   🐎 Unique horses: {stats['unique_horses']:,}")
            logger.info(f"   🔥 Power ratings: {stats['power_ratings']:,}")
            logger.info(f"   ⚡ Speed ratings: {stats['speed_ratings']:,}")
            logger.info(f"   🎲 Monte Carlo sims: {stats['monte_carlo_sims']:,}")
            logger.info(f"   📈 Data richness: {stats['data_richness']:.2f}")

        except Exception as e:
            logger.error(f"Error getting database stats: {e}")

        return stats

    def run_ai_model_execution(self) -> Dict:
        """Execute the actual AI model and capture performance metrics"""
        logger.info("🧠 Executing enhanced AI model for performance measurement...")

        try:
            # Execute the enhanced AI model
            start_time = time.time()

            result = subprocess.run(
                [sys.executable, str(self.ai_model_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            execution_time = time.time() - start_time

            # Parse output for metrics
            output_lines = result.stdout.split("\n")
            stderr_lines = result.stderr.split("\n")

            metrics = {
                "execution_time_seconds": execution_time,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "output_lines": len(output_lines),
                "error_lines": len(stderr_lines),
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            # Extract specific metrics from output
            predictions_count = 0
            accuracy_scores = []
            feature_counts = []
            model_names = []

            for line in output_lines:
                # Look for prediction counts
                if "predictions" in line.lower() and any(
                    char.isdigit() for char in line
                ):
                    numbers = [int(s) for s in line.split() if s.isdigit()]
                    if numbers:
                        predictions_count = max(numbers)

                # Look for accuracy scores
                if "accuracy" in line.lower() or "score" in line.lower():
                    import re

                    scores = re.findall(r"(\d+\.?\d*)%", line)
                    for score in scores:
                        try:
                            accuracy_scores.append(float(score))
                        except ValueError:
                            pass

                    # Also look for decimal scores
                    decimal_scores = re.findall(r"0\.\d+", line)
                    for score in decimal_scores:
                        try:
                            accuracy_scores.append(float(score) * 100)
                        except ValueError:
                            pass

                # Look for feature information
                if "feature" in line.lower() and any(char.isdigit() for char in line):
                    numbers = [int(s) for s in line.split() if s.isdigit()]
                    feature_counts.extend(numbers)

                # Look for model names
                if any(
                    model in line.lower()
                    for model in [
                        "random",
                        "gradient",
                        "forest",
                        "logistic",
                        "ensemble",
                    ]
                ):
                    for model in [
                        "RandomForest",
                        "GradientBoosting",
                        "ExtraTrees",
                        "LogisticRegression",
                        "Ensemble",
                    ]:
                        if model.lower() in line.lower():
                            model_names.append(model)

            # Calculate derived metrics
            metrics.update(
                {
                    "predictions_generated": predictions_count,
                    "accuracy_scores": accuracy_scores,
                    "average_accuracy": (
                        np.mean(accuracy_scores) if accuracy_scores else 0
                    ),
                    "max_accuracy": max(accuracy_scores) if accuracy_scores else 0,
                    "min_accuracy": min(accuracy_scores) if accuracy_scores else 0,
                    "feature_count": max(feature_counts) if feature_counts else 0,
                    "models_detected": list(set(model_names)),
                    "model_count": len(set(model_names)),
                }
            )

            # Performance classification
            if metrics["average_accuracy"] > 85:
                metrics["performance_grade"] = "A - Excellent"
            elif metrics["average_accuracy"] > 75:
                metrics["performance_grade"] = "B - Good"
            elif metrics["average_accuracy"] > 65:
                metrics["performance_grade"] = "C - Fair"
            else:
                metrics["performance_grade"] = "D - Poor"

            logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
            logger.info(f"🎯 Return code: {result.returncode}")
            logger.info(f"📊 Predictions: {predictions_count}")
            logger.info(f"🎯 Average accuracy: {metrics['average_accuracy']:.1f}%")
            logger.info(f"🏆 Performance grade: {metrics['performance_grade']}")
            logger.info(f"🤖 Models used: {', '.join(metrics['models_detected'])}")

            if not metrics["success"]:
                logger.error(f"❌ AI model execution failed:")
                logger.error(f"   Stderr: {result.stderr[:200]}...")

            return metrics

        except subprocess.TimeoutExpired:
            logger.error("⏰ AI model execution timed out")
            return {"success": False, "error": "timeout", "execution_time_seconds": 120}
        except Exception as e:
            logger.error(f"❌ AI model execution error: {e}")
            return {"success": False, "error": str(e), "execution_time_seconds": 0}

    def analyze_feature_performance(self, ai_metrics: Dict) -> Dict:
        """Analyze feature engineering performance"""
        logger.info("📊 Analyzing feature engineering performance...")

        feature_analysis = {
            "total_features": ai_metrics.get("feature_count", 0),
            "baseline_features": 17,  # Known baseline
            "enhanced_features": max(0, ai_metrics.get("feature_count", 0) - 17),
            "feature_expansion_ratio": (
                ai_metrics.get("feature_count", 0) / 17
                if ai_metrics.get("feature_count", 0) > 0
                else 0
            ),
            "feature_quality_score": 0,
        }

        # Calculate feature quality based on accuracy improvement
        if ai_metrics.get("average_accuracy", 0) > 80:
            feature_analysis["feature_quality_score"] = "High"
        elif ai_metrics.get("average_accuracy", 0) > 70:
            feature_analysis["feature_quality_score"] = "Medium"
        else:
            feature_analysis["feature_quality_score"] = "Low"

        logger.info(f"🔧 Total features: {feature_analysis['total_features']}")
        logger.info(f"➕ Enhanced features: {feature_analysis['enhanced_features']}")
        logger.info(
            f"📈 Expansion ratio: {feature_analysis['feature_expansion_ratio']:.1f}x"
        )
        logger.info(f"🏆 Quality score: {feature_analysis['feature_quality_score']}")

        return feature_analysis

    def run_comprehensive_training_cycle(self) -> Dict:
        """Run a complete training cycle with performance metrics"""
        cycle_start = time.time()

        logger.info("🚀 Starting comprehensive training cycle...")

        # Get database statistics
        db_stats = self.get_database_stats()

        # Execute AI model for performance measurement
        ai_metrics = self.run_ai_model_execution()

        # Analyze feature performance
        feature_analysis = self.analyze_feature_performance(ai_metrics)

        # Calculate overall cycle metrics
        cycle_time = time.time() - cycle_start

        comprehensive_metrics = {
            "cycle_start_time": self.training_start.isoformat(),
            "cycle_end_time": datetime.now().isoformat(),
            "cycle_duration_seconds": cycle_time,
            "database_stats": db_stats,
            "ai_performance": ai_metrics,
            "feature_analysis": feature_analysis,
            "overall_success": ai_metrics.get("success", False),
            "performance_summary": {
                "data_volume": db_stats.get("main_records", 0),
                "enrichment_level": db_stats.get("data_richness", 0),
                "model_accuracy": ai_metrics.get("average_accuracy", 0),
                "feature_count": feature_analysis.get("total_features", 0),
                "execution_efficiency": 1
                / max(ai_metrics.get("execution_time_seconds", 1), 0.1),
                "overall_score": self.calculate_overall_score(
                    ai_metrics, feature_analysis, db_stats
                ),
            },
        }

        # Log comprehensive summary
        self.log_performance_summary(comprehensive_metrics)

        return comprehensive_metrics

    def calculate_overall_score(
        self, ai_metrics: Dict, feature_analysis: Dict, db_stats: Dict
    ) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Accuracy score (40% weight)
            accuracy_score = min(ai_metrics.get("average_accuracy", 0), 100) * 0.4

            # Feature engineering score (30% weight)
            feature_ratio = feature_analysis.get("feature_expansion_ratio", 1)
            feature_score = min(feature_ratio * 20, 30)  # Cap at 30

            # Data utilization score (20% weight)
            data_richness = db_stats.get("data_richness", 0)
            data_score = min(data_richness * 100, 20)  # Cap at 20

            # Execution efficiency score (10% weight)
            exec_time = ai_metrics.get("execution_time_seconds", 60)
            efficiency_score = max(0, 10 - (exec_time / 10))  # Better if faster

            total_score = accuracy_score + feature_score + data_score + efficiency_score
            return round(total_score, 1)

        except Exception:
            return 0.0

    def log_performance_summary(self, metrics: Dict):
        """Log a comprehensive performance summary"""
        summary = metrics.get("performance_summary", {})

        logger.info("🏆 PERFORMANCE SUMMARY")
        logger.info("=" * 40)
        logger.info(f"📊 Data Volume: {summary.get('data_volume', 0):,} records")
        logger.info(f"🔥 Enrichment Level: {summary.get('enrichment_level', 0):.2f}")
        logger.info(f"🎯 Model Accuracy: {summary.get('model_accuracy', 0):.1f}%")
        logger.info(f"🔧 Feature Count: {summary.get('feature_count', 0)}")
        logger.info(
            f"⚡ Execution Efficiency: {summary.get('execution_efficiency', 0):.2f}"
        )
        logger.info(f"🏆 Overall Score: {summary.get('overall_score', 0):.1f}/100")
        logger.info("=" * 40)

    def save_metrics_report(self, metrics: Dict) -> Path:
        """Save detailed metrics report"""
        reports_dir = self.base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"performance_metrics_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"💾 Metrics report saved: {report_file}")
        return report_file


def main():
    """Main training function with comprehensive performance metrics"""
    print("🧠 Enhanced AI Performance Metrics Trainer v2.04")
    print("=" * 55)
    print("🎯 Real AI model execution with performance measurement")
    print("📊 Comprehensive metrics collection and analysis")
    print()

    try:
        trainer = PerformanceMetricsTrainer()

        # Run comprehensive training cycle
        metrics = trainer.run_comprehensive_training_cycle()

        # Save detailed report
        report_file = trainer.save_metrics_report(metrics)

        # Final status
        if metrics.get("overall_success", False):
            overall_score = metrics["performance_summary"]["overall_score"]
            print(f"\n✅ Enhanced AI training completed successfully!")
            print(f"🏆 Overall Performance Score: {overall_score:.1f}/100")
            print(
                f"📊 Model Accuracy: {metrics['ai_performance'].get('average_accuracy', 0):.1f}%"
            )
            print(
                f"🔧 Features: {metrics['feature_analysis'].get('total_features', 0)}"
            )
            print(f"💾 Detailed report: {report_file.name}")
            return 0
        else:
            print(f"\n❌ Enhanced AI training had issues")
            print(f"💡 Check model execution and database connectivity")
            print(f"📄 Error details in: {report_file.name}")
            return 1

    except Exception as e:
        print(f"\n❌ Training error: {e}")
        logger.error(f"Training error: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
