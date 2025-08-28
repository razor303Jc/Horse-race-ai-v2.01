#!/usr/bin/env python3
"""
AI Selections Performance Tracker
Compares AI selections with actual race results and tracks performance metrics
"""

import logging
import sys
import argparse
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import psycopg2
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AISelectionsPerformanceTracker:
    """Track and analyze AI selections performance against actual results"""

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

    def create_performance_tracking_table(self):
        """Create AI selections performance tracking table in results database"""
        logger.info("🏗️ Creating AI selections performance tracking table...")

        try:
            conn = psycopg2.connect(**self.results_db_config)
            cursor = conn.cursor()

            # Create ai_selections_performance table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_selections_performance (
                    performance_id SERIAL PRIMARY KEY,
                    race_date DATE NOT NULL,
                    race_id INTEGER NOT NULL,
                    course VARCHAR(100) NOT NULL,
                    race_number INTEGER NOT NULL,
                    horse_name VARCHAR(200) NOT NULL,
                    
                    -- AI Prediction Data
                    ai_win_probability DECIMAL(5,4) NOT NULL,
                    ai_confidence_score DECIMAL(5,4) NOT NULL,
                    ai_selection_type VARCHAR(20) NOT NULL DEFAULT 'win',
                    model_name VARCHAR(50) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    
                    -- Actual Race Results
                    actual_position INTEGER,
                    actual_starting_price DECIMAL(8,2),
                    actual_jockey VARCHAR(200),
                    actual_trainer VARCHAR(200),
                    
                    -- Performance Metrics
                    prediction_correct BOOLEAN,
                    win_prediction_correct BOOLEAN,
                    place_prediction_correct BOOLEAN,
                    roi_if_backed DECIMAL(8,2),
                    probability_accuracy_score DECIMAL(8,4),
                    
                    -- Ranking Analysis
                    ai_probability_rank INTEGER,
                    actual_finish_rank INTEGER,
                    rank_difference INTEGER,
                    
                    -- Metadata
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(race_date, race_id, horse_name, model_name)
                )
            """
            )

            # Create indexes for performance queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ai_perf_race_date 
                ON ai_selections_performance(race_date)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ai_perf_course_date 
                ON ai_selections_performance(course, race_date)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ai_perf_model 
                ON ai_selections_performance(model_name, model_version)
            """
            )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(
                "✅ AI selections performance tracking table created successfully"
            )

        except Exception as e:
            logger.error(f"❌ Failed to create performance tracking table: {e}")
            raise

    def get_ai_selections_for_date(self, target_date: str) -> pd.DataFrame:
        """Get AI selections from cards database for specified date"""
        logger.info(f"📊 Loading AI selections for {target_date}...")

        try:
            conn = psycopg2.connect(**self.cards_db_config)

            query = """
                SELECT 
                    race_id,
                    race_number,
                    course,
                    horse_name,
                    win_probability,
                    confidence_score,
                    ai_selection_type,
                    model_name,
                    model_version,
                    race_date
                FROM ai_selections
                WHERE race_date = %s
                ORDER BY course, race_number, win_probability DESC
            """

            df = pd.read_sql_query(query, conn, params=[target_date])
            conn.close()

            logger.info(
                f"✅ Loaded {len(df)} AI selections from {df['race_id'].nunique()} races"
            )
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load AI selections: {e}")
            raise

    def get_race_results_for_date(self, target_date: str) -> pd.DataFrame:
        """Get actual race results from results database for specified date"""
        logger.info(f"🏁 Loading race results for {target_date}...")

        try:
            conn = psycopg2.connect(**self.results_db_config)

            query = """
                SELECT 
                    r.race_id,
                    ra.race_number,
                    ra.course,
                    ra.date as race_date,
                    r.horse_name,
                    r.position as actual_position,
                    r.starting_price as actual_starting_price,
                    r.jockey as actual_jockey,
                    r.trainer as actual_trainer
                FROM records r
                JOIN races ra ON r.race_id = ra.race_id
                WHERE ra.date = %s
                ORDER BY ra.course, ra.race_number, r.position
            """

            df = pd.read_sql_query(query, conn, params=[target_date])
            conn.close()

            logger.info(
                f"✅ Loaded {len(df)} race results from {df['race_id'].nunique()} races"
            )
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load race results: {e}")
            raise

    def calculate_performance_metrics(
        self, ai_selections: pd.DataFrame, race_results: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate performance metrics by comparing AI selections with actual results"""
        logger.info("🔢 Calculating performance metrics...")

        # Merge AI selections with actual results
        merged = pd.merge(
            ai_selections, race_results, on=["race_id", "horse_name"], how="inner"
        )

        if len(merged) == 0:
            logger.warning(
                "⚠️ No matching horses found between AI selections and race results"
            )
            return pd.DataFrame()

        # Calculate performance metrics
        merged["prediction_correct"] = merged["actual_position"] == 1
        merged["win_prediction_correct"] = merged["prediction_correct"]
        merged["place_prediction_correct"] = merged["actual_position"] <= 3

        # Calculate ROI if backed (assuming £1 stake)
        merged["roi_if_backed"] = merged.apply(
            lambda row: (
                float(row["actual_starting_price"]) - 1.0
                if row["actual_position"] == 1
                else -1.0
            ),
            axis=1,
        )

        # Probability accuracy score (Brier Score)
        merged["probability_accuracy_score"] = merged.apply(
            lambda row: (
                row["win_probability"] - (1 if row["actual_position"] == 1 else 0)
            )
            ** 2,
            axis=1,
        )

        # Calculate probability ranks within each race
        merged["ai_probability_rank"] = merged.groupby("race_id")[
            "win_probability"
        ].rank(ascending=False, method="dense")
        merged["actual_finish_rank"] = merged["actual_position"]
        merged["rank_difference"] = (
            merged["ai_probability_rank"] - merged["actual_finish_rank"]
        )

        logger.info(f"✅ Calculated performance metrics for {len(merged)} selections")
        return merged

    def save_performance_data(self, performance_df: pd.DataFrame):
        """Save performance analysis to results database"""
        logger.info("💾 Saving performance data to database...")

        try:
            conn = psycopg2.connect(**self.results_db_config)
            cursor = conn.cursor()

            # Clear existing data for this date range if any
            if len(performance_df) > 0:
                race_dates = performance_df["race_date"].unique()
                for race_date in race_dates:
                    cursor.execute(
                        "DELETE FROM ai_selections_performance WHERE race_date = %s",
                        [race_date],
                    )

            # Insert new performance data
            for _, row in performance_df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO ai_selections_performance (
                        race_date, race_id, course, race_number, horse_name,
                        ai_win_probability, ai_confidence_score, ai_selection_type,
                        model_name, model_version,
                        actual_position, actual_starting_price, actual_jockey, actual_trainer,
                        prediction_correct, win_prediction_correct, place_prediction_correct,
                        roi_if_backed, probability_accuracy_score,
                        ai_probability_rank, actual_finish_rank, rank_difference
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    [
                        row["race_date"],
                        row["race_id"],
                        row["course_x"],
                        row["race_number_x"],
                        row["horse_name"],
                        float(row["win_probability"]),
                        float(row["confidence_score"]),
                        row["ai_selection_type"],
                        row["model_name"],
                        row["model_version"],
                        int(row["actual_position"]),
                        (
                            float(row["actual_starting_price"])
                            if row["actual_starting_price"]
                            else None
                        ),
                        row["actual_jockey"],
                        row["actual_trainer"],
                        bool(row["prediction_correct"]),
                        bool(row["win_prediction_correct"]),
                        bool(row["place_prediction_correct"]),
                        float(row["roi_if_backed"]),
                        float(row["probability_accuracy_score"]),
                        int(row["ai_probability_rank"]),
                        int(row["actual_finish_rank"]),
                        int(row["rank_difference"]),
                    ],
                )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(
                f"✅ Saved {len(performance_df)} performance records to database"
            )

        except Exception as e:
            logger.error(f"❌ Failed to save performance data: {e}")
            raise

    def analyze_performance_for_date(self, target_date: str):
        """Complete performance analysis for specified date"""
        logger.info(f"🎯 Starting AI selections performance analysis for {target_date}")

        try:
            # Create performance tracking table if it doesn't exist
            self.create_performance_tracking_table()

            # Get AI selections
            ai_selections = self.get_ai_selections_for_date(target_date)
            if len(ai_selections) == 0:
                logger.warning(f"❌ No AI selections found for {target_date}")
                return

            # Get race results
            race_results = self.get_race_results_for_date(target_date)
            if len(race_results) == 0:
                logger.warning(f"❌ No race results found for {target_date}")
                logger.info(
                    "ℹ️ Performance analysis will be available once race results are uploaded"
                )
                return

            # Calculate performance metrics
            performance_df = self.calculate_performance_metrics(
                ai_selections, race_results
            )
            if len(performance_df) == 0:
                logger.warning(
                    f"❌ No matching data found between AI selections and race results for {target_date}"
                )
                return

            # Save performance data
            self.save_performance_data(performance_df)

            # Generate performance summary
            self.generate_performance_summary(performance_df, target_date)

            logger.info(
                f"🎉 AI selections performance analysis completed for {target_date}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to complete performance analysis: {e}")
            raise

    def generate_performance_summary(
        self, performance_df: pd.DataFrame, target_date: str
    ):
        """Generate and display performance summary"""
        logger.info(f"📊 Performance Summary for {target_date}")
        logger.info("=" * 60)

        total_selections = len(performance_df)
        winners_predicted = performance_df["win_prediction_correct"].sum()
        place_predictions = performance_df["place_prediction_correct"].sum()

        win_accuracy = (
            (winners_predicted / total_selections) * 100 if total_selections > 0 else 0
        )
        place_accuracy = (
            (place_predictions / total_selections) * 100 if total_selections > 0 else 0
        )

        total_roi = performance_df["roi_if_backed"].sum()
        avg_roi_per_bet = total_roi / total_selections if total_selections > 0 else 0

        avg_brier_score = performance_df["probability_accuracy_score"].mean()

        logger.info(f"📈 Total AI Selections: {total_selections}")
        logger.info(f"🏆 Winners Predicted: {winners_predicted} ({win_accuracy:.1f}%)")
        logger.info(
            f"🥉 Place Predictions: {place_predictions} ({place_accuracy:.1f}%)"
        )
        logger.info(f"💰 Total ROI: £{total_roi:.2f}")
        logger.info(f"📊 Average ROI per bet: £{avg_roi_per_bet:.2f}")
        logger.info(f"🎯 Average Brier Score: {avg_brier_score:.4f} (lower is better)")

        # Top performing predictions
        top_winners = performance_df[performance_df["win_prediction_correct"]].nlargest(
            5, "win_probability"
        )
        if len(top_winners) > 0:
            logger.info(f"\n🏆 Top {len(top_winners)} Winners Predicted:")
            for _, row in top_winners.iterrows():
                logger.info(
                    f"  {row['horse_name']} ({row['course_x']}) - {row['win_probability']:.1%} probability, £{row['roi_if_backed']:.2f} ROI"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Analyze AI selections performance against race results"
    )
    parser.add_argument(
        "--date", type=str, required=True, help="Date for analysis (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    tracker = AISelectionsPerformanceTracker()
    tracker.analyze_performance_for_date(args.date)


if __name__ == "__main__":
    main()
