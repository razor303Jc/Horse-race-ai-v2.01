#!/usr/bin/env python3
"""
AI Selection Performance Tracker
Creates performance tracking table and analyzes AI selection accuracy against actual race results
"""

import logging
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import pandas as pd
import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AISelectionPerformanceTracker:
    """Tracks and analyzes AI selection performance against actual race results"""

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

    def create_performance_table(self):
        """Create the AI selection performance tracking table"""
        logger.info("🏗️ Creating AI selection performance tracking table...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)
            cursor = conn.cursor()

            # Drop table if exists (for development)
            cursor.execute("DROP TABLE IF EXISTS ai_selection_performance")

            # Create performance tracking table
            cursor.execute(
                """
                CREATE TABLE ai_selection_performance (
                    performance_id SERIAL PRIMARY KEY,
                    race_date DATE NOT NULL,
                    race_id INTEGER NOT NULL,
                    selection_id INTEGER NOT NULL,
                    horse_name VARCHAR(255) NOT NULL,
                    predicted_win_probability DECIMAL(10, 6) NOT NULL,
                    actual_position INTEGER,
                    actual_win BOOLEAN,
                    starting_price DECIMAL(10, 2),
                    prediction_correct BOOLEAN,
                    profit_loss DECIMAL(10, 2),
                    model_name VARCHAR(100) NOT NULL,
                    model_version VARCHAR(50) NOT NULL,
                    course VARCHAR(100) NOT NULL,
                    race_number INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Foreign key to ai_selections table
                    FOREIGN KEY (selection_id) REFERENCES ai_selections(selection_id),
                    
                    -- Indexes for performance
                    INDEX idx_performance_date (race_date),
                    INDEX idx_performance_race (race_id),
                    INDEX idx_performance_model (model_name, model_version),
                    INDEX idx_performance_profit (profit_loss)
                )
            """
            )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info("✅ Performance tracking table created successfully")

        except Exception as e:
            logger.error(f"❌ Failed to create performance table: {e}")
            raise

    def analyze_performance_for_date(self, target_date: str):
        """Analyze AI selection performance for a specific date"""
        logger.info(f"📊 Analyzing AI selection performance for {target_date}...")

        try:
            # Get AI selections for the date
            cards_conn = psycopg2.connect(**self.cards_db_config)
            results_conn = psycopg2.connect(**self.results_db_config)

            # Query AI selections
            ai_selections_query = """
                SELECT 
                    selection_id, race_id, horse_name, win_probability,
                    model_name, model_version, course, race_number
                FROM ai_selections 
                WHERE race_date = %s
                ORDER BY race_id, win_probability DESC
            """

            df_selections = pd.read_sql_query(
                ai_selections_query, cards_conn, params=[target_date]
            )

            if len(df_selections) == 0:
                logger.warning(f"❌ No AI selections found for {target_date}")
                return

            logger.info(f"📋 Found {len(df_selections)} AI selections for analysis")

            # Query actual race results
            results_query = """
                SELECT 
                    r.race_id, r.course, r.race_number,
                    rec.horse_name, rec.position, rec.starting_price
                FROM races r
                JOIN records rec ON r.race_id = rec.race_id
                WHERE r.date = %s
                ORDER BY r.race_id, rec.position
            """

            df_results = pd.read_sql_query(
                results_query, results_conn, params=[target_date]
            )

            if len(df_results) == 0:
                logger.warning(f"❌ No race results found for {target_date}")
                logger.info("💡 Results may not be available yet for this date")
                return

            logger.info(f"🏁 Found {len(df_results)} race results for analysis")

            # Merge selections with results
            df_performance = self._merge_selections_with_results(
                df_selections, df_results, target_date
            )

            # Calculate performance metrics
            performance_summary = self._calculate_performance_metrics(df_performance)

            # Save performance data
            self._save_performance_data(df_performance)

            # Display results
            self._display_performance_summary(performance_summary, target_date)

            cards_conn.close()
            results_conn.close()

        except Exception as e:
            logger.error(f"❌ Failed to analyze performance: {e}")
            raise

    def _merge_selections_with_results(
        self, df_selections: pd.DataFrame, df_results: pd.DataFrame, target_date: str
    ) -> pd.DataFrame:
        """Merge AI selections with actual race results"""

        # Merge on race_id and horse_name
        df_merged = pd.merge(
            df_selections, df_results, on=["race_id", "horse_name"], how="left"
        )

        # Calculate derived fields
        df_merged["actual_win"] = df_merged["position"] == 1
        df_merged["prediction_correct"] = df_merged["actual_win"]

        # Calculate profit/loss (assuming £1 stake per selection)
        df_merged["profit_loss"] = df_merged.apply(
            lambda row: (row["starting_price"] - 1.0) if row["actual_win"] else -1.0,
            axis=1,
        )

        df_merged["race_date"] = target_date

        return df_merged

    def _calculate_performance_metrics(self, df_performance: pd.DataFrame) -> Dict:
        """Calculate comprehensive performance metrics"""

        total_selections = len(df_performance)
        winners = df_performance["actual_win"].sum()
        accuracy = (winners / total_selections * 100) if total_selections > 0 else 0

        total_profit_loss = df_performance["profit_loss"].sum()
        roi = (
            (total_profit_loss / total_selections * 100) if total_selections > 0 else 0
        )

        # Top prediction accuracy (highest probability per race)
        top_picks = df_performance.loc[
            df_performance.groupby("race_id")["win_probability"].idxmax()
        ]
        top_pick_winners = top_picks["actual_win"].sum()
        top_pick_accuracy = (
            (top_pick_winners / len(top_picks) * 100) if len(top_picks) > 0 else 0
        )

        return {
            "total_selections": total_selections,
            "winners": winners,
            "accuracy": accuracy,
            "total_profit_loss": total_profit_loss,
            "roi": roi,
            "top_picks": len(top_picks),
            "top_pick_winners": top_pick_winners,
            "top_pick_accuracy": top_pick_accuracy,
            "average_win_probability": df_performance["win_probability"].mean(),
            "average_winner_probability": (
                df_performance[df_performance["actual_win"]]["win_probability"].mean()
                if winners > 0
                else 0
            ),
        }

    def _save_performance_data(self, df_performance: pd.DataFrame):
        """Save performance data to database"""
        logger.info("💾 Saving performance data to database...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)
            cursor = conn.cursor()

            # Clear existing performance data for this date
            cursor.execute(
                "DELETE FROM ai_selection_performance WHERE race_date = %s",
                [df_performance["race_date"].iloc[0]],
            )

            # Insert performance data
            for _, row in df_performance.iterrows():
                cursor.execute(
                    """
                    INSERT INTO ai_selection_performance (
                        race_date, race_id, selection_id, horse_name,
                        predicted_win_probability, actual_position, actual_win,
                        starting_price, prediction_correct, profit_loss,
                        model_name, model_version, course, race_number
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    [
                        row["race_date"],
                        row["race_id"],
                        row["selection_id"],
                        row["horse_name"],
                        float(row["win_probability"]),
                        int(row["position"]) if pd.notna(row["position"]) else None,
                        bool(row["actual_win"]),
                        (
                            float(row["starting_price"])
                            if pd.notna(row["starting_price"])
                            else None
                        ),
                        bool(row["prediction_correct"]),
                        float(row["profit_loss"]),
                        row["model_name"],
                        row["model_version"],
                        row["course_x"],
                        row["race_number_x"],
                    ],
                )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Saved {len(df_performance)} performance records")

        except Exception as e:
            logger.error(f"❌ Failed to save performance data: {e}")
            raise

    def _display_performance_summary(self, metrics: Dict, target_date: str):
        """Display comprehensive performance summary"""

        logger.info(f"🎯 AI Selection Performance Summary for {target_date}")
        logger.info("=" * 60)
        logger.info(f"📊 Total Selections: {metrics['total_selections']}")
        logger.info(f"🏆 Winners: {metrics['winners']}")
        logger.info(f"🎯 Overall Accuracy: {metrics['accuracy']:.2f}%")
        logger.info(f"💰 Total P&L: £{metrics['total_profit_loss']:.2f}")
        logger.info(f"📈 ROI: {metrics['roi']:.2f}%")
        logger.info("")
        logger.info(f"🎯 Top Pick Performance:")
        logger.info(f"   Races: {metrics['top_picks']}")
        logger.info(f"   Winners: {metrics['top_pick_winners']}")
        logger.info(f"   Accuracy: {metrics['top_pick_accuracy']:.2f}%")
        logger.info("")
        logger.info(f"📊 Probability Analysis:")
        logger.info(
            f"   Average Predicted Probability: {metrics['average_win_probability']:.4f}"
        )
        logger.info(
            f"   Average Winner Probability: {metrics['average_winner_probability']:.4f}"
        )

    def get_model_performance_history(self, days: int = 30):
        """Get historical model performance over specified days"""
        logger.info(f"📈 Retrieving model performance history for last {days} days...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)

            query = """
                SELECT 
                    race_date,
                    model_name,
                    model_version,
                    COUNT(*) as total_selections,
                    SUM(CASE WHEN actual_win = true THEN 1 ELSE 0 END) as winners,
                    ROUND(AVG(CASE WHEN actual_win = true THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy,
                    ROUND(SUM(profit_loss), 2) as total_pnl,
                    ROUND(AVG(profit_loss) * 100, 2) as roi
                FROM ai_selection_performance
                WHERE race_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY race_date, model_name, model_version
                ORDER BY race_date DESC, model_name
            """

            df_history = pd.read_sql_query(query, conn, params=[days])
            conn.close()

            if len(df_history) == 0:
                logger.warning("❌ No performance history found")
                return

            logger.info(f"📊 Performance History ({len(df_history)} records):")
            logger.info(df_history.to_string(index=False))

        except Exception as e:
            logger.error(f"❌ Failed to retrieve performance history: {e}")


def main():
    """Main function to run AI selection performance analysis"""
    parser = argparse.ArgumentParser(description="Analyze AI selection performance")
    parser.add_argument("--date", type=str, help="Date for analysis (YYYY-MM-DD)")
    parser.add_argument(
        "--create-table", action="store_true", help="Create performance tracking table"
    )
    parser.add_argument(
        "--history", type=int, default=30, help="Show performance history for N days"
    )

    args = parser.parse_args()

    tracker = AISelectionPerformanceTracker()

    if args.create_table:
        tracker.create_performance_table()

    if args.date:
        tracker.analyze_performance_for_date(args.date)

    if not args.date and not args.create_table:
        tracker.get_model_performance_history(args.history)


if __name__ == "__main__":
    main()
