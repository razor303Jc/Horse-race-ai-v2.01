#!/usr/bin/env python3
"""
Race Results Integration & Performance Tracking System for Horse Racing AI v2.04

This module implements:
- Prediction accuracy tracking and validation
- ROI and betting performance analysis
- Win rate analysis by confidence level
- Performance validation for AI predictions
- Comprehensive reporting and analytics
"""

import logging
import sys
import os
import subprocess
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# Add project root to path
sys.path.append(".")


@dataclass
class PredictionResult:
    """Data class for prediction results"""

    prediction_id: int
    race_id: int
    horse_id: int
    horse_name: str
    prediction_date: date
    predicted_position: int
    actual_position: int
    confidence_level: str  # 'HIGH', 'MEDIUM', 'LOW'
    confidence_score: float  # 0-1.0
    predicted_win_probability: float
    predicted_place_probability: float
    starting_price: float
    prediction_type: str  # 'WIN', 'PLACE', 'SHOW'
    stake_amount: float
    potential_return: float
    actual_return: float
    profit_loss: float
    is_correct: bool


@dataclass
class PerformanceMetrics:
    """Data class for performance analytics"""

    total_predictions: int
    correct_predictions: int
    accuracy_percentage: float
    total_stakes: float
    total_returns: float
    total_profit_loss: float
    roi_percentage: float
    win_rate_by_confidence: Dict[str, float]
    average_odds: float
    best_performing_confidence: str
    worst_performing_confidence: str


class RaceResultsTracker:
    """
    Comprehensive race results integration and performance tracking system.

    Tracks AI prediction accuracy, calculates ROI, analyzes performance
    by confidence level, and provides detailed analytics for betting
    strategy optimization.
    """

    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.container_name = "horse_racing_postgres_clean"

        # Performance tracking configuration
        self.config = {
            "default_stake_amount": 10.00,  # £10 default stake
            "confidence_thresholds": {
                "HIGH": 0.70,  # 70%+ confidence
                "MEDIUM": 0.50,  # 50-69% confidence
                "LOW": 0.30,  # 30-49% confidence
            },
            "roi_calculation_period": 30,  # Days for ROI calculation
            "min_predictions_for_analysis": 10,  # Minimum predictions needed
        }

    def setup_logging(self):
        """Configure logging system"""
        log_dir = "/home/jc/Documents/Horse-race-ai-v2.04/logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = f'{log_dir}/results_tracker_{datetime.now().strftime("%Y%m%d")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
        )

    def execute_query(self, database: str, query: str) -> List[List[str]]:
        """Execute SQL query using docker exec"""
        try:
            cmd = [
                "docker",
                "exec",
                self.container_name,
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
                self.logger.error(f"Query failed: {result.stderr}")
                return []

            # Parse the results
            lines = result.stdout.strip().split("\n")
            if not lines or lines == [""]:
                return []

            data = []
            for line in lines:
                if line and "|" in line:
                    values = line.split("|")
                    data.append(values)

            return data

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []

    def create_performance_tracking_tables(self):
        """Create tables for prediction tracking and performance analysis"""

        try:
            # Create prediction results table
            create_predictions_table = """
                CREATE TABLE IF NOT EXISTS prediction_results (
                    id SERIAL PRIMARY KEY,
                    race_id BIGINT NOT NULL,
                    horse_id BIGINT NOT NULL,
                    horse_name VARCHAR(255) NOT NULL,
                    prediction_date DATE DEFAULT CURRENT_DATE,
                    
                    -- Prediction Details
                    predicted_position INTEGER,
                    actual_position INTEGER,
                    confidence_level VARCHAR(10),
                    confidence_score REAL,
                    predicted_win_probability REAL,
                    predicted_place_probability REAL,
                    
                    -- Financial Details
                    starting_price REAL,
                    prediction_type VARCHAR(10),
                    stake_amount REAL DEFAULT 10.00,
                    potential_return REAL,
                    actual_return REAL,
                    profit_loss REAL,
                    
                    -- Result Analysis
                    is_correct BOOLEAN,
                    prediction_source VARCHAR(50) DEFAULT 'AI_SYSTEM',
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT unique_race_horse_prediction
                        UNIQUE (race_id, horse_id, prediction_date)
                );

                -- Create performance summary table
                CREATE TABLE IF NOT EXISTS performance_summary (
                    id SERIAL PRIMARY KEY,
                    analysis_date DATE DEFAULT CURRENT_DATE,
                    period_start DATE,
                    period_end DATE,
                    
                    -- Overall Performance
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    accuracy_percentage REAL,
                    
                    -- Financial Performance
                    total_stakes REAL,
                    total_returns REAL,
                    total_profit_loss REAL,
                    roi_percentage REAL,
                    
                    -- Confidence Level Analysis
                    high_confidence_accuracy REAL,
                    medium_confidence_accuracy REAL,
                    low_confidence_accuracy REAL,
                    
                    -- Best Performing Metrics
                    best_performing_confidence VARCHAR(10),
                    average_starting_price REAL,
                    longest_winning_streak INTEGER,
                    longest_losing_streak INTEGER,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_prediction_results_race_date
                    ON prediction_results(prediction_date);
                CREATE INDEX IF NOT EXISTS idx_prediction_results_confidence
                    ON prediction_results(confidence_level);
                CREATE INDEX IF NOT EXISTS idx_prediction_results_accuracy
                    ON prediction_results(is_correct);
                CREATE INDEX IF NOT EXISTS idx_performance_summary_date
                    ON performance_summary(analysis_date);
            """

            cmd = [
                "docker",
                "exec",
                self.container_name,
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "advanced_racing_metrics_db",
                "-c",
                create_predictions_table,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info("Performance tracking tables created successfully")
                return True
            else:
                self.logger.error(f"Failed to create tables: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error creating performance tracking tables: {e}")
            return False

    def get_ai_predictions(
        self, start_date: date = None, end_date: date = None
    ) -> List[Dict]:
        """Get AI predictions from the database"""

        if start_date is None:
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()

        query = f"""
            SELECT 
                race_id, horse_id, horse_name, prediction_date,
                predicted_position, confidence_score, 
                predicted_win_probability, predicted_place_probability
            FROM ai_predictions 
            WHERE prediction_date >= '{start_date}'
                AND prediction_date <= '{end_date}'
            ORDER BY prediction_date DESC, race_id;
        """

        raw_data = self.execute_query("advanced_racing_metrics_db", query)

        predictions = []
        for row in raw_data:
            if len(row) >= 8:
                predictions.append(
                    {
                        "race_id": int(row[0]) if row[0].isdigit() else 0,
                        "horse_id": int(row[1]) if row[1].isdigit() else 0,
                        "horse_name": row[2],
                        "prediction_date": row[3],
                        "predicted_position": int(row[4]) if row[4].isdigit() else 99,
                        "confidence_score": (
                            float(row[5]) if row[5].replace(".", "").isdigit() else 0.0
                        ),
                        "predicted_win_probability": (
                            float(row[6]) if row[6].replace(".", "").isdigit() else 0.0
                        ),
                        "predicted_place_probability": (
                            float(row[7]) if row[7].replace(".", "").isdigit() else 0.0
                        ),
                    }
                )

        return predictions

    def get_race_results(self, race_id: int) -> List[Dict]:
        """Get actual race results for comparison"""

        query = f"""
            SELECT 
                r.race_id, r.horse_id, r.name as horse_name, r.place as actual_position,
                r.sp as starting_price, races.date as race_date
            FROM records r
            JOIN races ON r.race_id = races.race_id
            WHERE r.race_id = {race_id}
                AND r.place IS NOT NULL
            ORDER BY r.place;
        """

        raw_data = self.execute_query("results_horse_racing_db", query)

        results = []
        for row in raw_data:
            if len(row) >= 6:
                results.append(
                    {
                        "race_id": int(row[0]) if row[0].isdigit() else 0,
                        "horse_id": int(row[1]) if row[1].isdigit() else 0,
                        "horse_name": row[2],
                        "actual_position": int(row[3]) if row[3].isdigit() else 99,
                        "starting_price": (
                            float(row[4]) if row[4].replace(".", "").isdigit() else 0.0
                        ),
                        "race_date": row[5],
                    }
                )

        return results

    def classify_confidence_level(self, confidence_score: float) -> str:
        """Classify confidence score into HIGH/MEDIUM/LOW categories"""

        if confidence_score >= self.config["confidence_thresholds"]["HIGH"]:
            return "HIGH"
        elif confidence_score >= self.config["confidence_thresholds"]["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"

    def calculate_returns(
        self,
        predicted_position: int,
        actual_position: int,
        starting_price: float,
        stake_amount: float,
    ) -> Tuple[float, float, float]:
        """Calculate potential return, actual return, and profit/loss"""

        # Potential return (if prediction was correct)
        if predicted_position == 1:  # Win bet
            potential_return = stake_amount * starting_price
        elif predicted_position <= 3:  # Place bet (assuming 1/4 odds)
            potential_return = stake_amount * (1 + (starting_price - 1) / 4)
        else:
            potential_return = 0.0

        # Actual return (what actually happened)
        if actual_position == predicted_position:
            actual_return = potential_return
        elif predicted_position <= 3 and actual_position <= 3:  # Place bet hit
            actual_return = stake_amount * (1 + (starting_price - 1) / 4)
        else:
            actual_return = 0.0

        # Profit/Loss
        profit_loss = actual_return - stake_amount

        return potential_return, actual_return, profit_loss

    def analyze_prediction_accuracy(
        self, predictions: List[Dict]
    ) -> List[PredictionResult]:
        """Analyze prediction accuracy against actual results"""

        prediction_results = []

        self.logger.info(f"Analyzing accuracy for {len(predictions)} predictions...")

        for prediction in predictions:
            try:
                race_id = prediction["race_id"]

                # Get actual race results
                race_results = self.get_race_results(race_id)

                if not race_results:
                    self.logger.warning(f"No race results found for race {race_id}")
                    continue

                # Find matching horse in results
                actual_result = None
                for result in race_results:
                    if result["horse_id"] == prediction["horse_id"]:
                        actual_result = result
                        break

                if not actual_result:
                    self.logger.warning(
                        f"Horse {prediction['horse_name']} not found in race {race_id} results"
                    )
                    continue

                # Calculate performance metrics
                predicted_position = prediction["predicted_position"]
                actual_position = actual_result["actual_position"]
                confidence_score = prediction["confidence_score"]
                starting_price = actual_result["starting_price"]
                stake_amount = self.config["default_stake_amount"]

                # Classify confidence level
                confidence_level = self.classify_confidence_level(confidence_score)

                # Calculate returns
                potential_return, actual_return, profit_loss = self.calculate_returns(
                    predicted_position, actual_position, starting_price, stake_amount
                )

                # Determine if prediction was correct
                is_correct = predicted_position == actual_position

                # Create prediction result
                result = PredictionResult(
                    prediction_id=0,  # Will be set when saved to DB
                    race_id=race_id,
                    horse_id=prediction["horse_id"],
                    horse_name=prediction["horse_name"],
                    prediction_date=datetime.strptime(
                        prediction["prediction_date"], "%Y-%m-%d"
                    ).date(),
                    predicted_position=predicted_position,
                    actual_position=actual_position,
                    confidence_level=confidence_level,
                    confidence_score=confidence_score,
                    predicted_win_probability=prediction["predicted_win_probability"],
                    predicted_place_probability=prediction[
                        "predicted_place_probability"
                    ],
                    starting_price=starting_price,
                    prediction_type="WIN" if predicted_position == 1 else "PLACE",
                    stake_amount=stake_amount,
                    potential_return=potential_return,
                    actual_return=actual_return,
                    profit_loss=profit_loss,
                    is_correct=is_correct,
                )

                prediction_results.append(result)

            except Exception as e:
                self.logger.error(
                    f"Error analyzing prediction for race {prediction.get('race_id', 'unknown')}: {e}"
                )

        self.logger.info(
            f"Analysis completed for {len(prediction_results)} predictions"
        )
        return prediction_results

    def calculate_performance_metrics(
        self, prediction_results: List[PredictionResult]
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""

        if not prediction_results:
            return PerformanceMetrics(
                total_predictions=0,
                correct_predictions=0,
                accuracy_percentage=0.0,
                total_stakes=0.0,
                total_returns=0.0,
                total_profit_loss=0.0,
                roi_percentage=0.0,
                win_rate_by_confidence={},
                average_odds=0.0,
                best_performing_confidence="NONE",
                worst_performing_confidence="NONE",
            )

        # Overall metrics
        total_predictions = len(prediction_results)
        correct_predictions = sum(1 for r in prediction_results if r.is_correct)
        accuracy_percentage = (correct_predictions / total_predictions) * 100

        # Financial metrics
        total_stakes = sum(r.stake_amount for r in prediction_results)
        total_returns = sum(r.actual_return for r in prediction_results)
        total_profit_loss = sum(r.profit_loss for r in prediction_results)
        roi_percentage = (
            (total_profit_loss / total_stakes) * 100 if total_stakes > 0 else 0.0
        )

        # Confidence level analysis
        confidence_stats = {}
        for level in ["HIGH", "MEDIUM", "LOW"]:
            level_results = [
                r for r in prediction_results if r.confidence_level == level
            ]
            if level_results:
                level_correct = sum(1 for r in level_results if r.is_correct)
                confidence_stats[level] = (level_correct / len(level_results)) * 100
            else:
                confidence_stats[level] = 0.0

        # Best/worst performing confidence levels
        best_confidence = (
            max(confidence_stats.items(), key=lambda x: x[1])[0]
            if confidence_stats
            else "NONE"
        )
        worst_confidence = (
            min(confidence_stats.items(), key=lambda x: x[1])[0]
            if confidence_stats
            else "NONE"
        )

        # Average odds
        valid_odds = [
            r.starting_price for r in prediction_results if r.starting_price > 0
        ]
        average_odds = np.mean(valid_odds) if valid_odds else 0.0

        return PerformanceMetrics(
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            accuracy_percentage=accuracy_percentage,
            total_stakes=total_stakes,
            total_returns=total_returns,
            total_profit_loss=total_profit_loss,
            roi_percentage=roi_percentage,
            win_rate_by_confidence=confidence_stats,
            average_odds=average_odds,
            best_performing_confidence=best_confidence,
            worst_performing_confidence=worst_confidence,
        )

    def save_prediction_results(
        self, prediction_results: List[PredictionResult]
    ) -> bool:
        """Save prediction results to database"""

        try:
            self.logger.info(f"Saving {len(prediction_results)} prediction results...")

            for result in prediction_results:
                insert_query = f"""
                    INSERT INTO prediction_results (
                        race_id, horse_id, horse_name, prediction_date,
                        predicted_position, actual_position, confidence_level, confidence_score,
                        predicted_win_probability, predicted_place_probability,
                        starting_price, prediction_type, stake_amount,
                        potential_return, actual_return, profit_loss, is_correct
                    ) VALUES (
                        {result.race_id}, {result.horse_id}, '{result.horse_name}', '{result.prediction_date}',
                        {result.predicted_position}, {result.actual_position}, '{result.confidence_level}', {result.confidence_score},
                        {result.predicted_win_probability}, {result.predicted_place_probability},
                        {result.starting_price}, '{result.prediction_type}', {result.stake_amount},
                        {result.potential_return}, {result.actual_return}, {result.profit_loss}, {result.is_correct}
                    ) ON CONFLICT (race_id, horse_id, prediction_date) DO UPDATE SET
                        actual_position = EXCLUDED.actual_position,
                        starting_price = EXCLUDED.starting_price,
                        actual_return = EXCLUDED.actual_return,
                        profit_loss = EXCLUDED.profit_loss,
                        is_correct = EXCLUDED.is_correct;
                """

                cmd = [
                    "docker",
                    "exec",
                    self.container_name,
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "advanced_racing_metrics_db",
                    "-c",
                    insert_query,
                ]

                result_exec = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30
                )

                if result_exec.returncode != 0:
                    self.logger.error(
                        f"Failed to save prediction result: {result_exec.stderr}"
                    )
                    return False

            self.logger.info("All prediction results saved successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error saving prediction results: {e}")
            return False

    def save_performance_summary(
        self, metrics: PerformanceMetrics, period_start: date, period_end: date
    ) -> bool:
        """Save performance summary to database"""

        try:
            insert_query = f"""
                INSERT INTO performance_summary (
                    period_start, period_end, total_predictions, correct_predictions,
                    accuracy_percentage, total_stakes, total_returns, total_profit_loss,
                    roi_percentage, high_confidence_accuracy, medium_confidence_accuracy,
                    low_confidence_accuracy, best_performing_confidence, average_starting_price
                ) VALUES (
                    '{period_start}', '{period_end}', {metrics.total_predictions}, {metrics.correct_predictions},
                    {metrics.accuracy_percentage}, {metrics.total_stakes}, {metrics.total_returns}, {metrics.total_profit_loss},
                    {metrics.roi_percentage}, {metrics.win_rate_by_confidence.get('HIGH', 0.0)}, 
                    {metrics.win_rate_by_confidence.get('MEDIUM', 0.0)}, {metrics.win_rate_by_confidence.get('LOW', 0.0)},
                    '{metrics.best_performing_confidence}', {metrics.average_odds}
                );
            """

            cmd = [
                "docker",
                "exec",
                self.container_name,
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "advanced_racing_metrics_db",
                "-c",
                insert_query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info("Performance summary saved successfully")
                return True
            else:
                self.logger.error(
                    f"Failed to save performance summary: {result.stderr}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error saving performance summary: {e}")
            return False

    def generate_performance_report(
        self, metrics: PerformanceMetrics, period_start: date, period_end: date
    ) -> str:
        """Generate comprehensive performance report"""

        report = f"""
🏇 AI HORSE RACING PREDICTION PERFORMANCE REPORT
{'=' * 60}

📅 ANALYSIS PERIOD: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}

📊 OVERALL PERFORMANCE METRICS
{'-' * 40}
Total Predictions:      {metrics.total_predictions:,}
Correct Predictions:    {metrics.correct_predictions:,}
Accuracy Rate:          {metrics.accuracy_percentage:.2f}%

💰 FINANCIAL PERFORMANCE
{'-' * 40}
Total Stakes:           £{metrics.total_stakes:,.2f}
Total Returns:          £{metrics.total_returns:,.2f}
Net Profit/Loss:        £{metrics.total_profit_loss:,.2f}
ROI Percentage:         {metrics.roi_percentage:+.2f}%

🎯 CONFIDENCE LEVEL ANALYSIS
{'-' * 40}
High Confidence:        {metrics.win_rate_by_confidence.get('HIGH', 0.0):.2f}% accuracy
Medium Confidence:      {metrics.win_rate_by_confidence.get('MEDIUM', 0.0):.2f}% accuracy
Low Confidence:         {metrics.win_rate_by_confidence.get('LOW', 0.0):.2f}% accuracy

🏆 PERFORMANCE INSIGHTS
{'-' * 40}
Best Confidence Level:  {metrics.best_performing_confidence}
Worst Confidence Level: {metrics.worst_performing_confidence}
Average Starting Price: {metrics.average_odds:.2f}

📈 STRATEGY RECOMMENDATIONS
{'-' * 40}
"""

        # Add strategy recommendations based on performance
        if metrics.roi_percentage > 5:
            report += "✅ POSITIVE ROI - Current strategy is profitable\n"
            report += "💡 Consider increasing stakes on high-confidence bets\n"
        elif metrics.roi_percentage > -5:
            report += "⚠️  BREAK-EVEN - Fine-tune strategy for better performance\n"
            report += "💡 Focus on improving confidence scoring accuracy\n"
        else:
            report += "❌ NEGATIVE ROI - Strategy needs significant improvement\n"
            report += "💡 Reduce stakes or revise prediction algorithms\n"

        if metrics.win_rate_by_confidence.get("HIGH", 0) > 60:
            report += "🎯 High-confidence predictions are performing well\n"

        if metrics.win_rate_by_confidence.get("LOW", 0) < 25:
            report += "⚠️  Consider filtering out low-confidence predictions\n"

        report += (
            f"\n📊 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        return report

    def run_performance_analysis(self, days_back: int = 30) -> bool:
        """Run comprehensive performance analysis"""

        try:
            # Set analysis period
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)

            self.logger.info(
                f"Running performance analysis for {start_date} to {end_date}"
            )

            # Get AI predictions
            predictions = self.get_ai_predictions(start_date, end_date)

            if not predictions:
                self.logger.warning("No AI predictions found for analysis period")
                return False

            # Analyze prediction accuracy
            prediction_results = self.analyze_prediction_accuracy(predictions)

            if not prediction_results:
                self.logger.warning("No prediction results could be analyzed")
                return False

            # Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics(prediction_results)

            # Save results to database
            save_success = self.save_prediction_results(prediction_results)
            summary_success = self.save_performance_summary(
                performance_metrics, start_date, end_date
            )

            if save_success and summary_success:
                self.logger.info("Performance analysis results saved successfully")

            # Generate and display report
            report = self.generate_performance_report(
                performance_metrics, start_date, end_date
            )
            print(report)

            # Save report to file
            report_file = f'/home/jc/Documents/Horse-race-ai-v2.04/reports/performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            os.makedirs(os.path.dirname(report_file), exist_ok=True)

            with open(report_file, "w") as f:
                f.write(report)

            self.logger.info(f"Performance report saved to: {report_file}")

            return True

        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return False


def main():
    """Main function for testing race results integration"""

    print("🏇 Race Results Integration & Performance Tracking v2.04")
    print("=" * 60)

    try:
        # Initialize results tracker
        tracker = RaceResultsTracker()

        # Create database tables
        tables_created = tracker.create_performance_tracking_tables()
        if tables_created:
            print("✅ Performance tracking tables created/verified")
        else:
            print("❌ Failed to create performance tracking tables")
            return 1

        # Run performance analysis
        print("\n🔍 Running performance analysis...")
        analysis_success = tracker.run_performance_analysis(days_back=30)

        if analysis_success:
            print("\n✅ Race Results Integration system operational!")
            print("📊 Performance analysis completed successfully")
            print("💰 ROI and betting performance tracked")
            print("🎯 AI prediction validation complete")
            return 0
        else:
            print("\n⚠️  Performance analysis completed with limited data")
            print("💡 System is operational but needs more historical data")
            return 0

    except Exception as e:
        print(f"❌ Critical error in race results integration: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
