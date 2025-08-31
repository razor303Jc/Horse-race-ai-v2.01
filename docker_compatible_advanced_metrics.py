#!/usr/bin/env python3
"""
Docker-Compatible Advanced Metrics Database Population Script
Populates the ai_horse_racing_db with calculated metrics from results_horse_racing_db
Horse Racing AI v2.05 - Docker Container Compatible Version
"""

import json
import os
import sys
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import math
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DockerAdvancedMetricsPopulator:
    """Populates advanced metrics database from results database - Docker compatible"""

    def __init__(self):
        """Initialize database connections and configuration"""
        # Use Docker network configuration
        self.db_config = {
            "host": "postgres",  # Docker service name
            "port": 5432,
            "user": "horse_racing",
            "password": "horse_racing_password",
        }

        # Database connections
        self.results_conn = None
        self.advanced_conn = None
        self.results_cursor = None
        self.advanced_cursor = None

        # Processing configuration
        self.batch_size = 100
        self.speed_figure_scale = 120  # Maximum speed figure
        self.power_rating_scale = 140  # Maximum power rating

        logger.info("🚀 Docker Advanced Metrics Populator initialized")

    def connect_databases(self) -> bool:
        """Connect to both results and advanced metrics databases"""
        try:
            # Connect to results database
            self.results_conn = psycopg2.connect(
                **self.db_config, database="results_horse_racing_db"
            )
            self.results_cursor = self.results_conn.cursor()
            logger.info("✅ Connected to results_horse_racing_db")

            # Connect to AI database (not advanced_horse_racing_db)
            self.advanced_conn = psycopg2.connect(
                **self.db_config, database="ai_horse_racing_db"
            )
            self.advanced_cursor = self.advanced_conn.cursor()
            logger.info("✅ Connected to ai_horse_racing_db")

            return True

        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def get_race_results_data(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Extract race results data from results database"""
        logger.info("📊 Extracting race results data...")

        query = """
        SELECT DISTINCT
            rr.race_id,
            rr.horse_name,
            r.date as race_date,
            rr.finishing_position,
            r.race_time,
            CASE 
                WHEN r.distance ~ '^[0-9.]+f$' THEN CAST(REGEXP_REPLACE(r.distance, '[^0-9.]', '', 'g') AS DECIMAL)
                WHEN r.distance ~ '^[0-9.]+m' THEN CAST(REGEXP_REPLACE(r.distance, '[^0-9.]', '', 'g') AS DECIMAL) * 8
                ELSE 8.0
            END as distance_furlongs,
            r.class as race_class,
            r.surface as going,
            r.course as track,
            rr.jockey,
            rr.trainer,
            rr.weight as weight_carried,
            rr.starting_price as odds,
            CASE WHEN rr.finishing_position = 1 THEN 1 ELSE 0 END as won,
            CASE WHEN rr.finishing_position <= 3 THEN 1 ELSE 0 END as placed
        FROM result_records rr
        JOIN result_races r ON rr.race_id = r.race_id
        WHERE rr.finishing_position IS NOT NULL 
            AND rr.horse_name IS NOT NULL
            AND r.date >= (CURRENT_DATE - INTERVAL '365 days')
        ORDER BY r.date DESC, rr.race_id
        """

        if limit:
            query += f" LIMIT {limit}"

        try:
            df = pd.read_sql_query(query, self.results_conn)
            logger.info(f"📈 Extracted {len(df)} race result records")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to extract race results: {e}")
            return pd.DataFrame()

    def calculate_speed_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate speed ratings for each horse performance"""
        logger.info("🏃 Calculating speed ratings...")

        def speed_rating_for_performance(row):
            """Calculate speed rating for a single performance"""
            base_rating = 60

            # Finishing position adjustment
            if row["finishing_position"] == 1:
                position_bonus = 20
            elif row["finishing_position"] == 2:
                position_bonus = 15
            elif row["finishing_position"] == 3:
                position_bonus = 10
            elif row["finishing_position"] <= 5:
                position_bonus = 5
            else:
                position_bonus = max(0, 10 - row["finishing_position"])

            # Class adjustment
            class_bonus = self._get_class_rating(row["race_class"])

            # Distance adjustment
            distance_factor = min(1.2, max(0.8, row["distance_furlongs"] / 8.0))

            # Odds adjustment (better odds = higher rating)
            if pd.notna(row["odds"]) and row["odds"] > 0:
                odds_factor = max(0.8, min(1.3, 10 / row["odds"]))
            else:
                odds_factor = 1.0

            # Calculate final speed figure
            speed_figure = (
                (base_rating + position_bonus + class_bonus)
                * distance_factor
                * odds_factor
            )

            return min(self.speed_figure_scale, max(20, speed_figure))

        # Apply speed rating calculation
        df["speed_figure"] = df.apply(speed_rating_for_performance, axis=1)
        df["pace_rating"] = df["speed_figure"] * np.random.uniform(
            0.85, 1.15, len(df)
        )  # Add some variance

        logger.info(f"✅ Calculated speed ratings for {len(df)} performances")
        return df

    def calculate_power_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate power ratings for each horse"""
        logger.info("⚡ Calculating power ratings...")

        # Group by horse for power rating calculation
        horse_ratings = []

        for horse_name in df["horse_name"].unique():
            horse_data = df[df["horse_name"] == horse_name].copy()

            if len(horse_data) == 0:
                continue

            # Base power rating from recent speed figures
            recent_speed_avg = horse_data.head(5)["speed_figure"].mean()

            # Consistency factor
            speed_std = horse_data.head(10)["speed_figure"].std()
            consistency = max(0.7, 1.2 - (speed_std / 20))

            # Win percentage
            win_rate = horse_data["won"].mean()
            place_rate = horse_data["placed"].mean()

            # Class performance
            class_performance = self._calculate_class_performance(horse_data)

            # Recent form (last 3 runs)
            recent_form = horse_data.head(3)["finishing_position"].mean()
            form_factor = max(0.8, 2.0 - (recent_form / 5))

            # Calculate power rating
            power_rating = (
                recent_speed_avg * 0.4
                + (win_rate * 50 + place_rate * 30) * 0.3
                + class_performance * 0.2
                + (consistency * form_factor * 20) * 0.1
            )

            power_rating = min(self.power_rating_scale, max(40, power_rating))

            horse_ratings.append(
                {
                    "horse_name": horse_name,
                    "power_rating": power_rating,
                    "base_rating": recent_speed_avg,
                    "consistency_factor": consistency,
                    "win_rate": win_rate,
                    "place_rate": place_rate,
                    "recent_form_average": recent_form,
                    "races_analyzed": len(horse_data),
                }
            )

        power_df = pd.DataFrame(horse_ratings)
        logger.info(f"✅ Calculated power ratings for {len(power_df)} horses")
        return power_df

    def calculate_form_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate form scores for each horse"""
        logger.info("📊 Calculating form scores...")

        form_scores = []

        for horse_name in df["horse_name"].unique():
            horse_data = df[df["horse_name"] == horse_name].head(10)  # Last 10 races

            if len(horse_data) == 0:
                continue

            # Weighted form score (recent races matter more)
            weights = np.exp(-0.1 * np.arange(len(horse_data)))  # Exponential decay

            # Position-based scores
            position_scores = []
            for pos in horse_data["finishing_position"]:
                if pos == 1:
                    position_scores.append(100)
                elif pos == 2:
                    position_scores.append(80)
                elif pos == 3:
                    position_scores.append(65)
                elif pos <= 5:
                    position_scores.append(50)
                else:
                    position_scores.append(max(10, 40 - pos * 3))

            # Calculate weighted form score
            weighted_form = np.average(position_scores, weights=weights)

            # Trend analysis
            if len(horse_data) >= 3:
                recent_positions = horse_data.head(3)["finishing_position"].tolist()
                trend_improvement = sum(
                    1
                    for i in range(1, len(recent_positions))
                    if recent_positions[i] < recent_positions[i - 1]
                )
                trend_factor = 1.0 + (trend_improvement * 0.1)
            else:
                trend_factor = 1.0

            final_form_score = weighted_form * trend_factor
            final_form_score = min(100, max(10, final_form_score))

            form_scores.append(
                {
                    "horse_name": horse_name,
                    "form_score": final_form_score,
                    "recent_runs": len(horse_data),
                    "trend_factor": trend_factor,
                }
            )

        form_df = pd.DataFrame(form_scores)
        logger.info(f"✅ Calculated form scores for {len(form_df)} horses")
        return form_df

    def run_monte_carlo_simulations(
        self, df: pd.DataFrame, power_ratings: pd.DataFrame
    ) -> pd.DataFrame:
        """Run Monte Carlo simulations for win probabilities"""
        logger.info("🎲 Running Monte Carlo simulations...")

        # Merge power ratings with race data
        df_with_power = df.merge(
            power_ratings[["horse_name", "power_rating"]], on="horse_name", how="left"
        )
        df_with_power["power_rating"].fillna(70, inplace=True)

        simulation_results = []

        # Group by race for simulation
        for race_id in df_with_power["race_id"].unique():
            race_horses = df_with_power[df_with_power["race_id"] == race_id].copy()

            if len(race_horses) < 2:
                continue

            # Run 10,000 simulations for this race
            n_simulations = 10000
            win_counts = {horse: 0 for horse in race_horses["horse_name"]}
            place_counts = {horse: 0 for horse in race_horses["horse_name"]}
            show_counts = {horse: 0 for horse in race_horses["horse_name"]}

            for _ in range(n_simulations):
                # Add random variation to power ratings
                simulated_ratings = []
                for _, horse in race_horses.iterrows():
                    noise = np.random.normal(0, 10)  # Random variation
                    sim_rating = horse["power_rating"] + noise
                    simulated_ratings.append((horse["horse_name"], sim_rating))

                # Sort by simulated rating (highest first)
                simulated_ratings.sort(key=lambda x: x[1], reverse=True)

                # Count placings
                for i, (horse_name, _) in enumerate(simulated_ratings):
                    if i == 0:  # Winner
                        win_counts[horse_name] += 1
                        place_counts[horse_name] += 1
                        show_counts[horse_name] += 1
                    elif i == 1:  # Place
                        place_counts[horse_name] += 1
                        show_counts[horse_name] += 1
                    elif i == 2:  # Show
                        show_counts[horse_name] += 1

            # Calculate probabilities
            for horse_name in race_horses["horse_name"]:
                win_prob = win_counts[horse_name] / n_simulations
                place_prob = place_counts[horse_name] / n_simulations
                show_prob = show_counts[horse_name] / n_simulations

                simulation_results.append(
                    {
                        "race_id": race_id,
                        "horse_name": horse_name,
                        "win_probability": win_prob,
                        "place_probability": place_prob,
                        "show_probability": show_prob,
                        "simulations_run": n_simulations,
                    }
                )

        mc_df = pd.DataFrame(simulation_results)
        logger.info(
            f"✅ Monte Carlo simulations complete for {len(mc_df)} horse-race combinations"
        )
        return mc_df

    def populate_speed_ratings_table(self, df: pd.DataFrame):
        """Populate horse_speed_ratings table"""
        logger.info("📝 Populating horse_speed_ratings table...")

        # Clear existing data
        self.advanced_cursor.execute("DELETE FROM horse_speed_ratings")

        # Group by horse for latest ratings
        for horse_name in df["horse_name"].unique():
            horse_data = df[df["horse_name"] == horse_name].head(1)  # Most recent

            if len(horse_data) == 0:
                continue

            row = horse_data.iloc[0]

            insert_query = """
            INSERT INTO horse_speed_ratings 
            (horse_id, horse_name, speed_figure, pace_rating, distance_specialist, 
             surface_rating, last_updated)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """

            self.advanced_cursor.execute(
                insert_query,
                (
                    row["horse_name"],
                    float(row["speed_figure"]),
                    float(row["pace_rating"]),
                    row["distance_furlongs"] >= 10,  # Distance specialist
                    70.0,  # Default surface rating
                ),
            )

        self.advanced_conn.commit()
        logger.info("✅ Speed ratings table populated")

    def populate_power_ratings_table(self, power_df: pd.DataFrame):
        """Populate horse_power_ratings table"""
        logger.info("📝 Populating horse_power_ratings table...")

        # Clear existing data
        self.advanced_cursor.execute("DELETE FROM horse_power_ratings")

        for _, row in power_df.iterrows():
            insert_query = """
            INSERT INTO horse_power_ratings 
            (horse_id, horse_name, power_rating, base_rating, class_adjustment,
             age_factor, weight_factor, distance_factor, confidence_score, last_updated)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """

            self.advanced_cursor.execute(
                insert_query,
                (
                    row["horse_name"],
                    float(row["power_rating"]),
                    float(row["base_rating"]),
                    0.0,  # Class adjustment
                    1.0,  # Age factor
                    1.0,  # Weight factor
                    1.0,  # Distance factor
                    float(row["consistency_factor"]),
                ),
            )

        self.advanced_conn.commit()
        logger.info("✅ Power ratings table populated")

    def populate_form_scores_table(self, form_df: pd.DataFrame):
        """Populate horse_form_scores table"""
        logger.info("📝 Populating horse_form_scores table...")

        # Clear existing data
        self.advanced_cursor.execute("DELETE FROM horse_form_scores")

        for _, row in form_df.iterrows():
            insert_query = """
            INSERT INTO horse_form_scores 
            (horse_id, horse_name, form_score, recent_form_trend, consistency_rating,
             last_updated)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """

            self.advanced_cursor.execute(
                insert_query,
                (
                    row["horse_name"],
                    float(row["form_score"]),
                    "improving" if row["trend_factor"] > 1.0 else "stable",
                    float(row["trend_factor"]),
                ),
            )

        self.advanced_conn.commit()
        logger.info("✅ Form scores table populated")

    def populate_monte_carlo_table(self, mc_df: pd.DataFrame):
        """Populate monte_carlo_simulations table"""
        logger.info("📝 Populating monte_carlo_simulations table...")

        # Clear existing data
        self.advanced_cursor.execute("DELETE FROM monte_carlo_simulations")

        for _, row in mc_df.iterrows():
            insert_query = """
            INSERT INTO monte_carlo_simulations 
            (simulation_id, horse_id, horse_name, race_id, win_probability,
             place_probability, show_probability, expected_finish_position,
             confidence_interval, last_updated)
            VALUES (gen_random_uuid(), gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """

            # Estimate expected finish position from win probability
            expected_position = max(
                1, min(20, int(1 / max(0.01, row["win_probability"])))
            )

            self.advanced_cursor.execute(
                insert_query,
                (
                    row["horse_name"],
                    row["race_id"],
                    float(row["win_probability"]),
                    float(row["place_probability"]),
                    float(row["show_probability"]),
                    expected_position,
                    "[0.95]",  # 95% confidence interval
                ),
            )

        self.advanced_conn.commit()
        logger.info("✅ Monte Carlo simulations table populated")

    def create_advanced_metrics_summary(
        self,
        speed_df: pd.DataFrame,
        power_df: pd.DataFrame,
        form_df: pd.DataFrame,
        mc_df: pd.DataFrame,
    ):
        """Create comprehensive advanced metrics table"""
        logger.info("📝 Creating advanced metrics summary...")

        # Clear existing data
        self.advanced_cursor.execute("DELETE FROM horse_advanced_metrics")

        # Merge all metrics by horse name
        all_horses = set()
        all_horses.update(speed_df["horse_name"].unique())
        all_horses.update(power_df["horse_name"].unique())
        all_horses.update(form_df["horse_name"].unique())

        for horse_name in all_horses:
            # Get latest metrics for each horse
            speed_data = speed_df[speed_df["horse_name"] == horse_name]
            power_data = power_df[power_df["horse_name"] == horse_name]
            form_data = form_df[form_df["horse_name"] == horse_name]
            mc_data = mc_df[mc_df["horse_name"] == horse_name]

            # Calculate composite metrics
            speed_figure = (
                speed_data["speed_figure"].iloc[0] if len(speed_data) > 0 else 60.0
            )
            power_rating = (
                power_data["power_rating"].iloc[0] if len(power_data) > 0 else 70.0
            )
            form_score = form_data["form_score"].iloc[0] if len(form_data) > 0 else 50.0
            avg_win_prob = (
                mc_data["win_probability"].mean() if len(mc_data) > 0 else 0.1
            )

            # Overall rating calculation
            overall_rating = (
                speed_figure * 0.25
                + power_rating * 0.35
                + form_score * 0.25
                + (avg_win_prob * 100) * 0.15
            )

            insert_query = """
            INSERT INTO horse_advanced_metrics 
            (horse_id, horse_name, overall_rating, speed_figure, power_rating,
             form_score, win_probability, consistency_score, last_updated)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """

            consistency = (
                power_data["consistency_factor"].iloc[0] if len(power_data) > 0 else 1.0
            )

            self.advanced_cursor.execute(
                insert_query,
                (
                    horse_name,
                    float(overall_rating),
                    float(speed_figure),
                    float(power_rating),
                    float(form_score),
                    float(avg_win_prob),
                    float(consistency),
                ),
            )

        self.advanced_conn.commit()
        logger.info("✅ Advanced metrics summary table populated")

    def _get_class_rating(self, race_class: str) -> int:
        """Convert race class to numeric rating"""
        if not race_class:
            return 10

        class_map = {
            "Class 1": 25,
            "Class 2": 20,
            "Class 3": 15,
            "Class 4": 10,
            "Class 5": 5,
            "Class 6": 2,
            "Listed": 30,
            "Group 1": 40,
            "Group 2": 35,
            "Group 3": 30,
            "Handicap": 12,
            "Maiden": 5,
            "Novice": 7,
        }

        for key, value in class_map.items():
            if key.lower() in race_class.lower():
                return value
        return 10

    def _calculate_class_performance(self, horse_data: pd.DataFrame) -> float:
        """Calculate how well horse performs in different classes"""
        if len(horse_data) == 0:
            return 50.0

        class_performances = []
        for _, race in horse_data.iterrows():
            class_rating = self._get_class_rating(race["race_class"])
            performance = 100 / max(
                1, race["finishing_position"]
            )  # Higher for better positions
            weighted_performance = performance * (
                class_rating / 20
            )  # Weight by class quality
            class_performances.append(weighted_performance)

        return np.mean(class_performances)

    def run_population(self):
        """Run the complete population process"""
        logger.info("🚀 Starting Advanced Metrics Database Population")
        logger.info("=" * 50)

        try:
            # Connect to databases
            if not self.connect_databases():
                raise Exception("Failed to connect to databases")

            # Extract race results data
            df = self.get_race_results_data(limit=5000)  # Limit for testing
            if df.empty:
                raise Exception("No race results data found")

            # Calculate all metrics
            df_with_speed = self.calculate_speed_ratings(df)
            power_ratings = self.calculate_power_ratings(df_with_speed)
            form_scores = self.calculate_form_scores(df_with_speed)
            monte_carlo_results = self.run_monte_carlo_simulations(
                df_with_speed, power_ratings
            )

            # Populate database tables
            self.populate_speed_ratings_table(df_with_speed)
            self.populate_power_ratings_table(power_ratings)
            self.populate_form_scores_table(form_scores)
            self.populate_monte_carlo_table(monte_carlo_results)
            self.create_advanced_metrics_summary(
                df_with_speed, power_ratings, form_scores, monte_carlo_results
            )

            # Final summary
            logger.info("🎉 Advanced Metrics Population COMPLETE!")
            logger.info(f"📊 Processed {len(df)} race results")
            logger.info(f"🏇 Calculated metrics for {len(power_ratings)} horses")
            logger.info(
                f"🎲 Generated {len(monte_carlo_results)} Monte Carlo predictions"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Population failed: {e}")
            return False

        finally:
            # Close database connections
            if self.results_conn:
                self.results_conn.close()
            if self.advanced_conn:
                self.advanced_conn.close()


def main():
    """Main function"""
    print("\n🚀 Docker Advanced Metrics Database Populator")
    print("=" * 50)

    populator = DockerAdvancedMetricsPopulator()
    success = populator.run_population()

    if success:
        print("✅ Population completed successfully!")
    else:
        print("❌ Population failed!")

    return success


if __name__ == "__main__":
    main()
