#!/usr/bin/env python3
"""
AI Selections Performance Dashboard
Comprehensive analysis and reporting for AI horse racing predictions
"""

import logging
import sys
import argparse
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional
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


class AIPerformanceDashboard:
    """Comprehensive AI selections performance dashboard and analytics"""

    def __init__(self):
        # Database configurations for container environment
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

    def get_overall_performance_summary(self, days: int = 30) -> Dict:
        """Get comprehensive performance summary for specified days"""
        logger.info(
            f"📊 Generating overall performance summary for last {days} days..."
        )

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    COUNT(*) as total_selections,
                    COUNT(DISTINCT race_date) as racing_days,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as total_winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as win_accuracy_pct,
                    SUM(CASE WHEN place_prediction_correct THEN 1 ELSE 0 END) as total_place_winners,
                    ROUND(AVG(CASE WHEN place_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as place_accuracy_pct,
                    ROUND(SUM(roi_if_backed), 2) as total_roi,
                    ROUND(AVG(roi_if_backed), 2) as avg_roi_per_bet,
                    ROUND(AVG(ai_win_probability), 4) as avg_win_probability,
                    ROUND(AVG(probability_accuracy_score), 4) as avg_brier_score,
                    MIN(race_date) as earliest_date,
                    MAX(race_date) as latest_date
                FROM ai_selections_performance
                WHERE race_date >= CURRENT_DATE - INTERVAL '%s days'
            """

            df = pd.read_sql_query(query, conn, params=[days])
            conn.close()

            if len(df) == 0:
                logger.warning("❌ No performance data found")
                return {}

            summary = df.iloc[0].to_dict()

            # Calculate additional metrics
            if summary["total_selections"] > 0:
                summary["strike_rate"] = (
                    summary["total_winners"] / summary["total_selections"]
                ) * 100
                summary["place_rate"] = (
                    summary["total_place_winners"] / summary["total_selections"]
                ) * 100
                summary["profit_factor"] = (
                    abs(summary["total_roi"] / summary["total_selections"])
                    if summary["total_selections"] > 0
                    else 0
                )

            return summary

        except Exception as e:
            logger.error(f"❌ Failed to get performance summary: {e}")
            return {}

    def get_daily_performance_trend(self, days: int = 14) -> pd.DataFrame:
        """Get daily performance trends"""
        logger.info(f"📈 Analyzing daily performance trends for last {days} days...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    race_date,
                    COUNT(*) as daily_selections,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as daily_winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as daily_win_accuracy,
                    ROUND(SUM(roi_if_backed), 2) as daily_roi,
                    ROUND(AVG(ai_win_probability), 4) as avg_daily_probability,
                    SUM(CASE WHEN place_prediction_correct THEN 1 ELSE 0 END) as daily_place_winners,
                    ROUND(AVG(CASE WHEN place_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as daily_place_accuracy
                FROM ai_selections_performance
                WHERE race_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY race_date
                ORDER BY race_date DESC
            """

            df = pd.read_sql_query(query, conn, params=[days])
            conn.close()

            logger.info(f"✅ Retrieved {len(df)} days of performance data")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to get daily trends: {e}")
            return pd.DataFrame()

    def get_top_performing_horses(self, limit: int = 20) -> pd.DataFrame:
        """Get top performing horse predictions"""
        logger.info(f"🏆 Finding top {limit} performing horse predictions...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    horse_name,
                    course,
                    race_date,
                    ROUND(ai_win_probability, 4) as predicted_probability,
                    actual_starting_price as odds,
                    CASE WHEN win_prediction_correct THEN 'WON' ELSE 'LOST' END as result,
                    ROUND(roi_if_backed, 2) as roi,
                    actual_position,
                    ROUND(ai_confidence_score, 4) as confidence
                FROM ai_selections_performance
                WHERE win_prediction_correct = true
                ORDER BY ai_win_probability DESC, roi_if_backed DESC
                LIMIT %s
            """

            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()

            logger.info(f"✅ Found {len(df)} winning predictions")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to get top horses: {e}")
            return pd.DataFrame()

    def get_probability_calibration_analysis(self) -> Dict:
        """Analyze how well probability predictions are calibrated"""
        logger.info("🎯 Analyzing probability calibration...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            # Group predictions by probability ranges
            query = """
                SELECT 
                    CASE 
                        WHEN ai_win_probability >= 0.7 THEN '70%+'
                        WHEN ai_win_probability >= 0.6 THEN '60-70%'
                        WHEN ai_win_probability >= 0.5 THEN '50-60%'
                        WHEN ai_win_probability >= 0.4 THEN '40-50%'
                        WHEN ai_win_probability >= 0.3 THEN '30-40%'
                        ELSE 'Under 30%'
                    END as probability_range,
                    COUNT(*) as selections_count,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as actual_winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as actual_win_rate,
                    ROUND(AVG(ai_win_probability) * 100, 2) as avg_predicted_rate,
                    ROUND(SUM(roi_if_backed), 2) as total_roi
                FROM ai_selections_performance
                GROUP BY 
                    CASE 
                        WHEN ai_win_probability >= 0.7 THEN '70%+'
                        WHEN ai_win_probability >= 0.6 THEN '60-70%'
                        WHEN ai_win_probability >= 0.5 THEN '50-60%'
                        WHEN ai_win_probability >= 0.4 THEN '40-50%'
                        WHEN ai_win_probability >= 0.3 THEN '30-40%'
                        ELSE 'Under 30%'
                    END
                ORDER BY 
                    CASE 
                        WHEN ai_win_probability >= 0.7 THEN 1
                        WHEN ai_win_probability >= 0.6 THEN 2
                        WHEN ai_win_probability >= 0.5 THEN 3
                        WHEN ai_win_probability >= 0.4 THEN 4
                        WHEN ai_win_probability >= 0.3 THEN 5
                        ELSE 6
                    END
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            calibration_data = df.to_dict("records")

            logger.info(
                f"✅ Analyzed calibration across {len(calibration_data)} probability ranges"
            )
            return {"calibration_ranges": calibration_data}

        except Exception as e:
            logger.error(f"❌ Failed to analyze calibration: {e}")
            return {}

    def get_course_performance_analysis(self) -> pd.DataFrame:
        """Analyze performance by course"""
        logger.info("🏁 Analyzing performance by course...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    course,
                    COUNT(*) as total_selections,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as winners,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as win_accuracy_pct,
                    ROUND(SUM(roi_if_backed), 2) as total_roi,
                    ROUND(AVG(roi_if_backed), 2) as avg_roi_per_bet,
                    ROUND(AVG(ai_win_probability), 4) as avg_probability
                FROM ai_selections_performance
                GROUP BY course
                HAVING COUNT(*) >= 3  -- Only courses with 3+ selections
                ORDER BY win_accuracy_pct DESC, total_roi DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            logger.info(f"✅ Analyzed performance across {len(df)} courses")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to analyze course performance: {e}")
            return pd.DataFrame()

    def generate_strategy_optimization_report(self) -> Dict:
        """Generate strategy optimization recommendations"""
        logger.info("⚡ Generating strategy optimization recommendations...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            # Analyze optimal probability thresholds
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
            threshold_analysis = []

            for threshold in thresholds:
                query = """
                    SELECT 
                        COUNT(*) as selections,
                        SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as winners,
                        ROUND(AVG(CASE WHEN win_prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy,
                        ROUND(SUM(roi_if_backed), 2) as total_roi,
                        ROUND(AVG(roi_if_backed), 2) as avg_roi
                    FROM ai_selections_performance
                    WHERE ai_win_probability >= %s
                """

                df = pd.read_sql_query(query, conn, params=[threshold])
                if len(df) > 0:
                    result = df.iloc[0].to_dict()
                    result["threshold"] = threshold
                    threshold_analysis.append(result)

            conn.close()

            # Find optimal threshold (best accuracy with reasonable volume)
            optimal_threshold = None
            best_score = 0
            for analysis in threshold_analysis:
                if analysis["selections"] >= 10:  # Minimum volume
                    score = (analysis["accuracy"] * 0.7) + (analysis["avg_roi"] * 0.3)
                    if score > best_score:
                        best_score = score
                        optimal_threshold = analysis

            recommendations = {
                "threshold_analysis": threshold_analysis,
                "optimal_threshold": optimal_threshold,
                "recommendations": [],
            }

            if optimal_threshold:
                recommendations["recommendations"].append(
                    {
                        "type": "probability_threshold",
                        "recommendation": f"Focus on selections with {optimal_threshold['threshold']*100:.0f}%+ probability",
                        "rationale": f"Achieves {optimal_threshold['accuracy']:.1f}% accuracy with £{optimal_threshold['avg_roi']:.2f} average ROI",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"❌ Failed to generate strategy recommendations: {e}")
            return {}

    def generate_comprehensive_report(self, days: int = 30, output_file: str = None):
        """Generate comprehensive performance report"""
        logger.info(f"📋 Generating comprehensive AI performance report...")

        report = {
            "generation_time": datetime.now().isoformat(),
            "analysis_period_days": days,
            "overall_summary": self.get_overall_performance_summary(days),
            "daily_trends": self.get_daily_performance_trend(14).to_dict("records"),
            "top_predictions": self.get_top_performing_horses(15).to_dict("records"),
            "probability_calibration": self.get_probability_calibration_analysis(),
            "course_analysis": self.get_course_performance_analysis().to_dict(
                "records"
            ),
            "strategy_optimization": self.generate_strategy_optimization_report(),
        }

        # Display key findings
        self.display_report_summary(report)

        # Save to file if specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📄 Report saved to {output_file}")

        return report

    def display_report_summary(self, report: Dict):
        """Display formatted report summary"""
        summary = report.get("overall_summary", {})

        logger.info("=" * 80)
        logger.info("🎯 AI SELECTIONS PERFORMANCE DASHBOARD SUMMARY")
        logger.info("=" * 80)

        if summary:
            logger.info(
                f"📊 Analysis Period: {summary.get('racing_days', 0)} racing days"
            )
            logger.info(f"🔢 Total Selections: {summary.get('total_selections', 0)}")
            logger.info(f"🏆 Win Accuracy: {summary.get('win_accuracy_pct', 0)}%")
            logger.info(f"🥉 Place Accuracy: {summary.get('place_accuracy_pct', 0)}%")
            logger.info(f"💰 Total ROI: £{summary.get('total_roi', 0)}")
            logger.info(f"📈 Avg ROI per bet: £{summary.get('avg_roi_per_bet', 0)}")
            logger.info(
                f"🎲 Avg Win Probability: {summary.get('avg_win_probability', 0)}"
            )

        # Top prediction
        top_predictions = report.get("top_predictions", [])
        if top_predictions:
            top = top_predictions[0]
            logger.info("")
            logger.info("🏆 TOP PREDICTION:")
            logger.info(
                f"   {top['horse_name']} ({top['course']}) - {top['predicted_probability']*100:.1f}% prob, £{top['roi']} ROI"
            )

        # Strategy recommendation
        strategy = report.get("strategy_optimization", {})
        recommendations = strategy.get("recommendations", [])
        if recommendations:
            logger.info("")
            logger.info("⚡ STRATEGY RECOMMENDATIONS:")
            for rec in recommendations[:3]:
                logger.info(f"   • {rec['recommendation']}")

        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="AI Selections Performance Dashboard and Analytics"
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze (default: 30)"
    )
    parser.add_argument(
        "--output", type=str, help="Output file for detailed report (JSON format)"
    )
    parser.add_argument(
        "--action",
        type=str,
        choices=["summary", "trends", "calibration", "courses", "strategy"],
        default="summary",
        help="Specific analysis to run",
    )

    args = parser.parse_args()

    dashboard = AIPerformanceDashboard()

    if args.action == "summary":
        dashboard.generate_comprehensive_report(args.days, args.output)
    elif args.action == "trends":
        trends = dashboard.get_daily_performance_trend(args.days)
        logger.info("📈 Daily Performance Trends:")
        logger.info(trends.to_string(index=False))
    elif args.action == "calibration":
        calibration = dashboard.get_probability_calibration_analysis()
        logger.info("🎯 Probability Calibration Analysis:")
        for range_data in calibration.get("calibration_ranges", []):
            logger.info(
                f"   {range_data['probability_range']}: {range_data['actual_win_rate']}% actual vs {range_data['avg_predicted_rate']}% predicted"
            )
    elif args.action == "courses":
        courses = dashboard.get_course_performance_analysis()
        logger.info("🏁 Course Performance Analysis:")
        logger.info(courses.to_string(index=False))
    elif args.action == "strategy":
        strategy = dashboard.generate_strategy_optimization_report()
        logger.info("⚡ Strategy Optimization Analysis:")
        for rec in strategy.get("recommendations", []):
            logger.info(f"   • {rec['recommendation']}: {rec['rationale']}")


if __name__ == "__main__":
    main()
