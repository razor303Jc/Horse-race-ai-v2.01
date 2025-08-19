#!/usr/bin/env python3
"""
Real-Time Performance Tracking Integration
==========================================

Implements V2.01's live ROI tracking and hit rate monitoring to replace mock performance data.
This creates comprehensive performance tracking with automated alerts and analytics.

Key Features:
- Live bet tracking and ROI calculation
- Real-time accuracy monitoring
- Performance history database tables
- Automated performance alerts and notifications
- Profit/loss tracking with detailed analytics
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import psycopg2
from decimal import Decimal

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class RealTimePerformanceTracker:
    """
    Real-time performance tracking system that monitors ML model performance,
    betting outcomes, and ROI in real-time
    """

    def __init__(self, pipeline_config=None):
        self.project_root = project_root
        self.pipeline_config = pipeline_config or {}
        self.logger = self.setup_logging()

        # Performance thresholds
        self.performance_thresholds = {
            "min_accuracy": 0.65,
            "min_roi": 0.05,  # 5% ROI
            "max_drawdown": -0.15,  # -15% maximum drawdown
            "min_hit_rate": 0.60,
            "profit_alert_threshold": 100.0,  # £100
            "loss_alert_threshold": -50.0,  # -£50
        }

        # Tracking state
        self.performance_data = {}
        self.alerts = []
        self.errors = []

    def setup_logging(self):
        """Setup pipeline logging"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = (
            log_dir
            / f"performance_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
            self.logger.info("✅ Connected to database for performance tracking")
            return True
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False

    def create_performance_tables(self):
        """
        Step 1: Create performance history database tables
        """
        self.logger.info("🗄️ Step 1: Creating performance history tables...")

        try:
            # Create bet tracking table
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bet_tracking (
                    id SERIAL PRIMARY KEY,
                    bet_id VARCHAR(255) UNIQUE,
                    race_id VARCHAR(255),
                    horse_id BIGINT,
                    horse_name VARCHAR(255),
                    prediction_confidence DECIMAL(5,4),
                    predicted_probability DECIMAL(5,4),
                    bet_amount DECIMAL(10,2),
                    odds DECIMAL(8,2),
                    bet_type VARCHAR(50),
                    outcome VARCHAR(20),
                    profit_loss DECIMAL(10,2),
                    bet_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_timestamp TIMESTAMP,
                    model_version VARCHAR(100)
                )
            """
            )

            # Create performance metrics table
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_date DATE,
                    total_bets INTEGER,
                    winning_bets INTEGER,
                    hit_rate DECIMAL(5,4),
                    total_staked DECIMAL(10,2),
                    total_returns DECIMAL(10,2),
                    profit_loss DECIMAL(10,2),
                    roi DECIMAL(6,4),
                    accuracy DECIMAL(5,4),
                    precision_score DECIMAL(5,4),
                    recall_score DECIMAL(5,4),
                    f1_score DECIMAL(5,4),
                    auc_score DECIMAL(5,4),
                    average_odds DECIMAL(6,2),
                    max_drawdown DECIMAL(6,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create performance alerts table
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id SERIAL PRIMARY KEY,
                    alert_type VARCHAR(50),
                    alert_level VARCHAR(20),
                    message TEXT,
                    metric_value DECIMAL(10,4),
                    threshold_value DECIMAL(10,4),
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """
            )

            self.conn.commit()
            self.logger.info("✅ Performance tables created successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to create performance tables: {e}")
            self.errors.append(f"Create performance tables: {e}")
            return False

    def track_live_betting_performance(self):
        """
        Step 2: Track live betting performance and ROI calculation
        """
        self.logger.info("📊 Step 2: Tracking live betting performance...")

        try:
            # Get recent betting data (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)

            self.cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(bet_amount) as total_staked,
                    SUM(CASE WHEN outcome = 'won' THEN (bet_amount * odds) ELSE 0 END) as total_returns,
                    SUM(profit_loss) as total_profit_loss,
                    AVG(odds) as average_odds,
                    AVG(prediction_confidence) as avg_confidence
                FROM bet_tracking 
                WHERE bet_timestamp >= %s
            """,
                (cutoff_date,),
            )

            betting_stats = self.cursor.fetchone()

            if betting_stats[0] > 0:  # If we have bets
                (
                    total_bets,
                    winning_bets,
                    total_staked,
                    total_returns,
                    total_profit_loss,
                    avg_odds,
                    avg_confidence,
                ) = betting_stats

                # Calculate performance metrics
                hit_rate = winning_bets / total_bets if total_bets > 0 else 0
                roi = total_profit_loss / total_staked if total_staked > 0 else 0

                performance_metrics = {
                    "total_bets": total_bets,
                    "winning_bets": winning_bets,
                    "hit_rate": hit_rate,
                    "total_staked": float(total_staked or 0),
                    "total_returns": float(total_returns or 0),
                    "profit_loss": float(total_profit_loss or 0),
                    "roi": roi,
                    "average_odds": float(avg_odds or 0),
                    "avg_confidence": float(avg_confidence or 0),
                }

                self.performance_data["betting_performance"] = performance_metrics

                self.logger.info(f"📊 Live Betting Performance (30 days):")
                self.logger.info(f"   - Total Bets: {total_bets}")
                self.logger.info(f"   - Hit Rate: {hit_rate:.1%}")
                self.logger.info(f"   - ROI: {roi:.1%}")
                self.logger.info(f"   - Profit/Loss: £{total_profit_loss:.2f}")

                return performance_metrics
            else:
                # No betting data yet - create sample tracking structure
                self.logger.info(
                    "📊 No betting data found - setting up tracking structure"
                )
                performance_metrics = {
                    "total_bets": 0,
                    "winning_bets": 0,
                    "hit_rate": 0,
                    "total_staked": 0,
                    "total_returns": 0,
                    "profit_loss": 0,
                    "roi": 0,
                    "average_odds": 0,
                    "avg_confidence": 0,
                }
                self.performance_data["betting_performance"] = performance_metrics
                return performance_metrics

        except Exception as e:
            self.logger.error(f"❌ Live betting tracking failed: {e}")
            self.errors.append(f"Live betting tracking: {e}")
            return None

    def monitor_model_accuracy(self):
        """
        Step 3: Real-time accuracy monitoring
        """
        self.logger.info("🎯 Step 3: Monitoring model accuracy...")

        try:
            # Get recent predictions vs actual results
            self.cursor.execute(
                """
                SELECT 
                    bt.predicted_probability,
                    bt.prediction_confidence,
                    bt.outcome,
                    r.position
                FROM bet_tracking bt
                JOIN records r ON bt.race_id = r.race_id AND bt.horse_id = r.horse_id
                WHERE bt.bet_timestamp >= %s
                AND r.position IS NOT NULL
            """,
                (datetime.now() - timedelta(days=7),),
            )  # Last 7 days

            prediction_data = self.cursor.fetchall()

            if prediction_data:
                df = pd.DataFrame(
                    prediction_data,
                    columns=[
                        "predicted_probability",
                        "confidence",
                        "outcome",
                        "actual_position",
                    ],
                )

                # Calculate accuracy metrics
                df["predicted_win"] = df["predicted_probability"] > 0.5
                df["actual_win"] = df["actual_position"] == 1

                accuracy = (df["predicted_win"] == df["actual_win"]).mean()

                # Calculate precision, recall for wins
                true_positives = (
                    (df["predicted_win"] == True) & (df["actual_win"] == True)
                ).sum()
                false_positives = (
                    (df["predicted_win"] == True) & (df["actual_win"] == False)
                ).sum()
                false_negatives = (
                    (df["predicted_win"] == False) & (df["actual_win"] == True)
                ).sum()

                precision = (
                    true_positives / (true_positives + false_positives)
                    if (true_positives + false_positives) > 0
                    else 0
                )
                recall = (
                    true_positives / (true_positives + false_negatives)
                    if (true_positives + false_negatives) > 0
                    else 0
                )
                f1_score = (
                    2 * (precision * recall) / (precision + recall)
                    if (precision + recall) > 0
                    else 0
                )

                accuracy_metrics = {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "sample_size": len(df),
                }

                self.performance_data["accuracy_metrics"] = accuracy_metrics

                self.logger.info(f"🎯 Model Accuracy (7 days):")
                self.logger.info(f"   - Accuracy: {accuracy:.1%}")
                self.logger.info(f"   - Precision: {precision:.1%}")
                self.logger.info(f"   - Recall: {recall:.1%}")
                self.logger.info(f"   - F1 Score: {f1_score:.3f}")
                self.logger.info(f"   - Sample Size: {len(df)}")

                return accuracy_metrics
            else:
                self.logger.info(
                    "🎯 No recent prediction data for accuracy calculation"
                )
                return {
                    "accuracy": 0,
                    "precision": 0,
                    "recall": 0,
                    "f1_score": 0,
                    "sample_size": 0,
                }

        except Exception as e:
            self.logger.error(f"❌ Model accuracy monitoring failed: {e}")
            self.errors.append(f"Model accuracy monitoring: {e}")
            return None

    def generate_performance_alerts(self):
        """
        Step 4: Generate automated performance alerts and notifications
        """
        self.logger.info("🚨 Step 4: Generating performance alerts...")

        try:
            alerts_generated = []

            # Check betting performance alerts
            betting_perf = self.performance_data.get("betting_performance", {})
            accuracy_metrics = self.performance_data.get("accuracy_metrics", {})

            # ROI alert
            if betting_perf.get("roi", 0) < self.performance_thresholds["min_roi"]:
                alert = {
                    "type": "roi_low",
                    "level": "warning",
                    "message": f"ROI below threshold: {betting_perf.get('roi', 0):.1%} < {self.performance_thresholds['min_roi']:.1%}",
                    "value": betting_perf.get("roi", 0),
                    "threshold": self.performance_thresholds["min_roi"],
                }
                alerts_generated.append(alert)

            # Hit rate alert
            if (
                betting_perf.get("hit_rate", 0)
                < self.performance_thresholds["min_hit_rate"]
            ):
                alert = {
                    "type": "hit_rate_low",
                    "level": "warning",
                    "message": f"Hit rate below threshold: {betting_perf.get('hit_rate', 0):.1%} < {self.performance_thresholds['min_hit_rate']:.1%}",
                    "value": betting_perf.get("hit_rate", 0),
                    "threshold": self.performance_thresholds["min_hit_rate"],
                }
                alerts_generated.append(alert)

            # Accuracy alert
            if (
                accuracy_metrics.get("accuracy", 0)
                < self.performance_thresholds["min_accuracy"]
            ):
                alert = {
                    "type": "accuracy_low",
                    "level": "critical",
                    "message": f"Model accuracy below threshold: {accuracy_metrics.get('accuracy', 0):.1%} < {self.performance_thresholds['min_accuracy']:.1%}",
                    "value": accuracy_metrics.get("accuracy", 0),
                    "threshold": self.performance_thresholds["min_accuracy"],
                }
                alerts_generated.append(alert)

            # Profit/Loss alerts
            profit_loss = betting_perf.get("profit_loss", 0)
            if profit_loss >= self.performance_thresholds["profit_alert_threshold"]:
                alert = {
                    "type": "profit_milestone",
                    "level": "info",
                    "message": f"Profit milestone reached: £{profit_loss:.2f}",
                    "value": profit_loss,
                    "threshold": self.performance_thresholds["profit_alert_threshold"],
                }
                alerts_generated.append(alert)
            elif profit_loss <= self.performance_thresholds["loss_alert_threshold"]:
                alert = {
                    "type": "loss_threshold",
                    "level": "critical",
                    "message": f"Loss threshold exceeded: £{profit_loss:.2f}",
                    "value": profit_loss,
                    "threshold": self.performance_thresholds["loss_alert_threshold"],
                }
                alerts_generated.append(alert)

            # Save alerts to database
            for alert in alerts_generated:
                self.cursor.execute(
                    """
                    INSERT INTO performance_alerts 
                    (alert_type, alert_level, message, metric_value, threshold_value)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        alert["type"],
                        alert["level"],
                        alert["message"],
                        alert["value"],
                        alert["threshold"],
                    ),
                )

            self.conn.commit()

            self.alerts = alerts_generated

            if alerts_generated:
                self.logger.info(
                    f"🚨 Generated {len(alerts_generated)} performance alerts"
                )
                for alert in alerts_generated:
                    level_emoji = {"info": "💡", "warning": "⚠️", "critical": "🚨"}
                    self.logger.info(
                        f"   {level_emoji.get(alert['level'], '📢')} {alert['message']}"
                    )
            else:
                self.logger.info(
                    "✅ No performance alerts - all metrics within thresholds"
                )

            return alerts_generated

        except Exception as e:
            self.logger.error(f"❌ Performance alerts generation failed: {e}")
            self.errors.append(f"Performance alerts: {e}")
            return []

    def save_daily_performance_snapshot(self):
        """
        Step 5: Save daily performance snapshot for historical tracking
        """
        self.logger.info("📈 Step 5: Saving daily performance snapshot...")

        try:
            today = datetime.now().date()

            # Get today's performance data
            betting_perf = self.performance_data.get("betting_performance", {})
            accuracy_metrics = self.performance_data.get("accuracy_metrics", {})

            # Check if today's snapshot already exists
            self.cursor.execute(
                """
                SELECT id FROM performance_metrics WHERE metric_date = %s
            """,
                (today,),
            )

            existing = self.cursor.fetchone()

            if existing:
                # Update existing record
                self.cursor.execute(
                    """
                    UPDATE performance_metrics SET
                        total_bets = %s,
                        winning_bets = %s,
                        hit_rate = %s,
                        total_staked = %s,
                        total_returns = %s,
                        profit_loss = %s,
                        roi = %s,
                        accuracy = %s,
                        precision_score = %s,
                        recall_score = %s,
                        f1_score = %s
                    WHERE metric_date = %s
                """,
                    (
                        betting_perf.get("total_bets", 0),
                        betting_perf.get("winning_bets", 0),
                        betting_perf.get("hit_rate", 0),
                        betting_perf.get("total_staked", 0),
                        betting_perf.get("total_returns", 0),
                        betting_perf.get("profit_loss", 0),
                        betting_perf.get("roi", 0),
                        accuracy_metrics.get("accuracy", 0),
                        accuracy_metrics.get("precision", 0),
                        accuracy_metrics.get("recall", 0),
                        accuracy_metrics.get("f1_score", 0),
                        today,
                    ),
                )
                self.logger.info(f"📈 Updated performance snapshot for {today}")
            else:
                # Insert new record
                self.cursor.execute(
                    """
                    INSERT INTO performance_metrics 
                    (metric_date, total_bets, winning_bets, hit_rate, total_staked, 
                     total_returns, profit_loss, roi, accuracy, precision_score, 
                     recall_score, f1_score, average_odds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        today,
                        betting_perf.get("total_bets", 0),
                        betting_perf.get("winning_bets", 0),
                        betting_perf.get("hit_rate", 0),
                        betting_perf.get("total_staked", 0),
                        betting_perf.get("total_returns", 0),
                        betting_perf.get("profit_loss", 0),
                        betting_perf.get("roi", 0),
                        accuracy_metrics.get("accuracy", 0),
                        accuracy_metrics.get("precision", 0),
                        accuracy_metrics.get("recall", 0),
                        accuracy_metrics.get("f1_score", 0),
                        betting_perf.get("average_odds", 0),
                    ),
                )
                self.logger.info(f"📈 Created new performance snapshot for {today}")

            self.conn.commit()
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save performance snapshot: {e}")
            self.errors.append(f"Save performance snapshot: {e}")
            return False

    def save_pipeline_results(self):
        """Save pipeline results for tracking and monitoring"""
        results_file = (
            self.project_root / "reports" / "performance_tracking_results.json"
        )

        pipeline_results = {
            "pipeline_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "performance_data": self.performance_data,
            "alerts": self.alerts,
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }

        with open(results_file, "w") as f:
            json.dump(pipeline_results, f, indent=2, default=str)

        self.logger.info(f"Pipeline results saved to: {results_file}")
        return pipeline_results

    def run_performance_tracking_pipeline(self):
        """
        Execute the complete real-time performance tracking pipeline

        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.logger.info("🚀 Starting Real-Time Performance Tracking Pipeline")
        self.logger.info("=" * 60)

        if not self.connect_to_database():
            return False

        pipeline_steps = [
            ("Create Performance Tables", self.create_performance_tables),
            ("Track Live Betting Performance", self.track_live_betting_performance),
            ("Monitor Model Accuracy", self.monitor_model_accuracy),
            ("Generate Performance Alerts", self.generate_performance_alerts),
            ("Save Daily Performance Snapshot", self.save_daily_performance_snapshot),
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
        self.logger.info("📊 PERFORMANCE TRACKING PIPELINE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Steps completed: {success_count}/{total_steps}")
        self.logger.info(f"Alerts generated: {len(self.alerts)}")
        self.logger.info(f"Errors encountered: {len(self.errors)}")

        if self.errors:
            self.logger.error("❌ Pipeline completed with errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        else:
            self.logger.info("✅ Performance tracking pipeline completed successfully!")
            self.logger.info("📊 Real-time performance monitoring now active!")

        return success_count == total_steps and len(self.errors) == 0


# Integration hook for main pipeline
def run_performance_tracking_pipeline(config=None):
    """
    Main entry point for pipeline integration
    Called by the main pipeline orchestrator
    """
    pipeline = RealTimePerformanceTracker(config)
    return pipeline.run_performance_tracking_pipeline()


if __name__ == "__main__":
    # Allow running standalone for testing
    pipeline = RealTimePerformanceTracker()
    success = pipeline.run_performance_tracking_pipeline()

    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Real-Time Performance Tracking Pipeline completed successfully!")
