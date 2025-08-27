#!/usr/bin/env python3
"""
Automated AI Selections Performance Reporter
Daily automated analysis and reporting system
"""

import logging
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List
import psycopg2
import pandas as pd
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AutomatedAIReporter:
    """Automated daily AI selections performance reporting"""

    def __init__(self):
        # Database configurations
        self.results_db_config = {
            "host": "postgres",
            "port": "5432",
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        self.cards_db_config = {
            "host": "postgres",
            "port": "5432",
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def check_available_dates(self) -> Dict:
        """Check what dates have AI selections and results data"""
        logger.info("🔍 Checking available data dates...")

        try:
            # Check AI selections dates
            cards_conn = psycopg2.connect(**self.cards_db_config)
            ai_query = """
                SELECT race_date, COUNT(*) as selections_count
                FROM ai_selections
                GROUP BY race_date
                ORDER BY race_date DESC
                LIMIT 10
            """
            ai_dates = pd.read_sql_query(ai_query, cards_conn)
            cards_conn.close()

            # Check race results dates
            results_conn = psycopg2.connect(**self.results_db_config)
            results_query = """
                SELECT date as race_date, COUNT(*) as results_count
                FROM races
                GROUP BY date
                ORDER BY date DESC
                LIMIT 10
            """
            results_dates = pd.read_sql_query(results_query, results_conn)
            results_conn.close()

            # Check performance data dates
            perf_query = """
                SELECT race_date, COUNT(*) as performance_count
                FROM ai_selections_performance
                GROUP BY race_date
                ORDER BY race_date DESC
            """
            perf_dates = pd.read_sql_query(perf_query, results_conn)

            return {
                "ai_selections_dates": ai_dates.to_dict("records"),
                "race_results_dates": results_dates.to_dict("records"),
                "performance_dates": perf_dates.to_dict("records"),
            }

        except Exception as e:
            logger.error(f"❌ Failed to check available dates: {e}")
            return {}

    def identify_missing_performance_analysis(self) -> List[str]:
        """Identify dates that have both AI selections and results but no performance analysis"""
        logger.info("🔍 Identifying dates needing performance analysis...")

        try:
            results_conn = psycopg2.connect(**self.results_db_config)

            query = """
                WITH ai_dates AS (
                    SELECT DISTINCT race_date 
                    FROM (
                        SELECT '2025-08-22'::date as race_date
                        UNION
                        SELECT '2025-08-23'::date as race_date
                        UNION 
                        SELECT '2025-08-24'::date as race_date
                    ) ai
                ),
                result_dates AS (
                    SELECT DISTINCT date as race_date
                    FROM races
                    WHERE date IN ('2025-08-22', '2025-08-23', '2025-08-24')
                ),
                perf_dates AS (
                    SELECT DISTINCT race_date
                    FROM ai_selections_performance
                )
                SELECT ai.race_date
                FROM ai_dates ai
                JOIN result_dates rd ON ai.race_date = rd.race_date
                LEFT JOIN perf_dates pd ON ai.race_date = pd.race_date
                WHERE pd.race_date IS NULL
                ORDER BY ai.race_date
            """

            df = pd.read_sql_query(query, results_conn)
            results_conn.close()

            missing_dates = df["race_date"].dt.strftime("%Y-%m-%d").tolist()
            logger.info(
                f"📅 Found {len(missing_dates)} dates needing analysis: {missing_dates}"
            )

            return missing_dates

        except Exception as e:
            logger.error(f"❌ Failed to identify missing analysis: {e}")
            return []

    def generate_daily_summary_report(self) -> Dict:
        """Generate daily summary report of AI performance"""
        logger.info("📊 Generating daily summary report...")

        try:
            results_conn = psycopg2.connect(**self.results_db_config)

            # Overall metrics
            overall_query = """
                SELECT 
                    COUNT(*) as total_selections,
                    COUNT(DISTINCT race_date) as racing_days,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as total_winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as win_accuracy,
                    SUM(CASE WHEN place_prediction_correct THEN 1 ELSE 0 END) as place_winners,
                    ROUND(AVG(CASE WHEN place_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as place_accuracy,
                    ROUND(SUM(roi_if_backed), 2) as total_roi,
                    ROUND(AVG(roi_if_backed), 2) as avg_roi_per_bet,
                    MIN(race_date) as earliest_date,
                    MAX(race_date) as latest_date
                FROM ai_selections_performance
            """

            overall_df = pd.read_sql_query(overall_query, results_conn)
            overall_metrics = overall_df.iloc[0].to_dict()

            # Best predictions today/recent
            best_query = """
                SELECT 
                    horse_name,
                    course,
                    race_date,
                    ROUND(ai_win_probability, 4) as probability,
                    actual_starting_price as odds,
                    CASE WHEN win_prediction_correct THEN 'WON' ELSE 'LOST' END as result,
                    ROUND(roi_if_backed, 2) as roi
                FROM ai_selections_performance
                WHERE win_prediction_correct = true
                ORDER BY race_date DESC, ai_win_probability DESC
                LIMIT 5
            """

            best_df = pd.read_sql_query(best_query, results_conn)

            # Daily performance by date
            daily_query = """
                SELECT 
                    race_date,
                    COUNT(*) as selections,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy,
                    ROUND(SUM(roi_if_backed), 2) as daily_roi
                FROM ai_selections_performance
                GROUP BY race_date
                ORDER BY race_date DESC
            """

            daily_df = pd.read_sql_query(daily_query, results_conn)
            results_conn.close()

            report = {
                "report_date": datetime.now().isoformat(),
                "overall_metrics": overall_metrics,
                "best_predictions": best_df.to_dict("records"),
                "daily_performance": daily_df.to_dict("records"),
                "status": "success",
            }

            return report

        except Exception as e:
            logger.error(f"❌ Failed to generate summary report: {e}")
            return {"status": "error", "error": str(e)}

    def display_summary_report(self, report: Dict):
        """Display formatted summary report"""
        if report.get("status") != "success":
            logger.error(
                f"❌ Report generation failed: {report.get('error', 'Unknown error')}"
            )
            return

        metrics = report.get("overall_metrics", {})

        logger.info("🎯 AI SELECTIONS PERFORMANCE SUMMARY")
        logger.info("=" * 60)
        logger.info(
            f"📊 Period: {metrics.get('earliest_date')} to {metrics.get('latest_date')}"
        )
        logger.info(f"📅 Racing Days: {metrics.get('racing_days', 0)}")
        logger.info(f"🔢 Total Selections: {metrics.get('total_selections', 0)}")
        logger.info(
            f"🏆 Winners: {metrics.get('total_winners', 0)} ({metrics.get('win_accuracy', 0)}%)"
        )
        logger.info(
            f"🥉 Place Finishes: {metrics.get('place_winners', 0)} ({metrics.get('place_accuracy', 0)}%)"
        )
        logger.info(f"💰 Total P&L: £{metrics.get('total_roi', 0)}")
        logger.info(f"📈 Avg ROI/Bet: £{metrics.get('avg_roi_per_bet', 0)}")

        # Best predictions
        best = report.get("best_predictions", [])
        if best:
            logger.info("")
            logger.info("🏆 RECENT TOP WINNERS:")
            for pred in best[:3]:
                logger.info(
                    f"   {pred['horse_name']} ({pred['course']}) - {pred['probability']*100:.1f}% → {pred['result']} (£{pred['roi']} ROI)"
                )

        # Daily breakdown
        daily = report.get("daily_performance", [])
        if daily:
            logger.info("")
            logger.info("📈 DAILY PERFORMANCE:")
            for day in daily:
                logger.info(
                    f"   {day['race_date']}: {day['winners']}/{day['selections']} ({day['accuracy']}%) = £{day['daily_roi']} ROI"
                )

        logger.info("=" * 60)

    def run_daily_analysis(self):
        """Run complete daily analysis workflow"""
        logger.info("🚀 Starting automated daily AI performance analysis...")

        # Check data availability
        dates_info = self.check_available_dates()

        # Identify missing performance analysis
        missing_dates = self.identify_missing_performance_analysis()

        if missing_dates:
            logger.info(
                f"⚠️ Found {len(missing_dates)} dates needing performance analysis"
            )
            logger.info("💡 Run the performance tracker for these dates:")
            for date in missing_dates:
                logger.info(
                    f"   python tools/ml_training/ai_selections_performance_tracker.py --date {date}"
                )

        # Generate and display summary report
        report = self.generate_daily_summary_report()
        self.display_summary_report(report)

        return report


def main():
    reporter = AutomatedAIReporter()
    report = reporter.run_daily_analysis()

    # Save report to file
    report_file = f"/workspace/reports/ai_performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"📄 Detailed report saved to {report_file}")


if __name__ == "__main__":
    main()
