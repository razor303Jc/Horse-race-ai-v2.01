#!/usr/bin/env python3
"""
Form Score Integration for Horse Racing AI v2.04
Simplified version that works with the existing database setup.

This module implements:
- Recent race performance scoring (last 3-5 runs)
- Form trend analysis (improving/declining patterns)
- Form confidence scoring
- Integration with existing prediction models
"""

import logging
import sys
import os
import subprocess
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(".")


@dataclass
class FormAnalysisResult:
    """Data class for form analysis results"""

    horse_id: int
    horse_name: str
    race_id: int
    recent_form_score: float  # 0-100 scale
    form_trend: str  # 'improving', 'declining', 'stable'
    form_trend_score: float  # -1.0 to +1.0
    consistency_rating: float  # 0-100 scale
    recent_runs_analyzed: int
    best_recent_position: int
    worst_recent_position: int
    average_recent_position: float
    days_since_last_run: int
    form_confidence: float  # 0-1.0 confidence score
    class_progression: str  # 'up', 'down', 'same'
    distance_suitability: float  # 0-1.0


class FormAnalyzer:
    """
    Simplified form analysis system that works with Docker containers.
    """

    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.container_name = "horse_racing_postgres_clean"

        # Form analysis configuration
        self.config = {
            "max_recent_runs": 5,
            "min_runs_for_analysis": 2,
            "max_days_lookback": 180,
            "position_weights": [1.0, 0.8, 0.6, 0.4, 0.2],
        }

    def setup_logging(self):
        """Configure logging system"""
        log_dir = "/home/jc/Documents/Horse-race-ai-v2.04/logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = f'{log_dir}/form_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
        )

    def execute_query(self, database: str, query: str) -> List[Dict]:
        """Execute SQL query using docker exec"""
        try:
            # Prepare the command
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

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                self.logger.error(f"Query failed: {result.stderr}")
                return []

            # Parse the results
            lines = result.stdout.strip().split("\n")
            if not lines or lines == [""]:
                return []

            # Get column names from first line if it exists
            data = []
            for line in lines:
                if line and "|" in line:
                    values = line.split("|")
                    data.append(values)

            return data

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []

    def get_horse_recent_form(
        self, horse_id: int, analysis_date: date = None
    ) -> List[Dict]:
        """Get recent race form for a horse"""

        if analysis_date is None:
            analysis_date = date.today()

        cutoff_date = analysis_date - timedelta(days=self.config["max_days_lookback"])

        query = f"""
            SELECT 
                r.race_id, r.horse_id, r.name as horse_name, r.place as finishing_position,
                races.runners as total_runners, races.date, races.course, 
                0 as distance_yards, races.going, races.class, r.sp as odds_decimal
            FROM records r
            JOIN races ON r.race_id = races.race_id
            WHERE r.horse_id = {horse_id}
                AND races.date >= '{cutoff_date}'
                AND races.date <= '{analysis_date}'
                AND r.place IS NOT NULL
            ORDER BY races.date DESC
            LIMIT {self.config['max_recent_runs']};
        """

        raw_data = self.execute_query("results_horse_racing_db", query)

        # Convert to dict format
        recent_runs = []
        for row in raw_data:
            if len(row) >= 11:
                recent_runs.append(
                    {
                        "race_id": int(row[0]) if row[0].isdigit() else 0,
                        "horse_id": int(row[1]) if row[1].isdigit() else 0,
                        "horse_name": row[2],
                        "finishing_position": int(row[3]) if row[3].isdigit() else 99,
                        "total_runners": int(row[4]) if row[4].isdigit() else 12,
                        "race_date": row[5],
                        "course": row[6],
                        "distance_yards": int(row[7]) if row[7].isdigit() else 0,
                        "going": row[8],
                        "race_class": row[9],
                        "odds_decimal": (
                            float(row[10])
                            if row[10].replace(".", "").isdigit()
                            else 0.0
                        ),
                    }
                )

        return recent_runs

    def calculate_form_score(self, recent_runs: List[Dict]) -> float:
        """Calculate weighted form score based on recent finishing positions"""

        if not recent_runs:
            return 50.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for i, run in enumerate(recent_runs):
            if i >= len(self.config["position_weights"]):
                break

            weight = self.config["position_weights"][i]
            position = run["finishing_position"]
            total_runners = run.get("total_runners", 12)

            # Convert position to percentage score (1st = 100%, last = 0%)
            if total_runners > 1:
                position_score = (
                    (total_runners - position) / (total_runners - 1)
                ) * 100
            else:
                position_score = 100.0 if position == 1 else 50.0

            total_weighted_score += position_score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 50.0

    def analyze_form_trend(self, recent_runs: List[Dict]) -> tuple[str, float]:
        """Analyze if horse's form is improving, declining, or stable"""

        if len(recent_runs) < 2:
            return "stable", 0.0

        # Get position percentages
        position_percentages = []
        for run in recent_runs:
            position = run["finishing_position"]
            total_runners = run.get("total_runners", 12)

            if total_runners > 1:
                percentage = ((total_runners - position) / (total_runners - 1)) * 100
            else:
                percentage = 100.0 if position == 1 else 50.0

            position_percentages.append(percentage)

        # Simple trend analysis
        if len(position_percentages) >= 3:
            recent_avg = sum(position_percentages[:2]) / 2
            older_avg = sum(position_percentages[-2:]) / 2
        else:
            recent_avg = position_percentages[0]
            older_avg = position_percentages[-1]

        diff = recent_avg - older_avg

        if diff > 10.0:
            return "improving", min(1.0, diff / 30.0)
        elif diff < -10.0:
            return "declining", max(-1.0, diff / 30.0)
        else:
            return "stable", diff / 30.0

    def analyze_horse_form(
        self, horse_id: int, horse_name: str, race_id: int
    ) -> FormAnalysisResult:
        """Perform form analysis for a horse"""

        try:
            # Get recent form data
            recent_runs = self.get_horse_recent_form(horse_id)

            if len(recent_runs) < self.config["min_runs_for_analysis"]:
                # Return neutral analysis for insufficient data
                return FormAnalysisResult(
                    horse_id=horse_id,
                    horse_name=horse_name,
                    race_id=race_id,
                    recent_form_score=50.0,
                    form_trend="stable",
                    form_trend_score=0.0,
                    consistency_rating=50.0,
                    recent_runs_analyzed=len(recent_runs),
                    best_recent_position=99,
                    worst_recent_position=99,
                    average_recent_position=99.0,
                    days_since_last_run=999,
                    form_confidence=0.1,
                    class_progression="same",
                    distance_suitability=0.5,
                )

            # Calculate form metrics
            form_score = self.calculate_form_score(recent_runs)
            form_trend, trend_score = self.analyze_form_trend(recent_runs)

            # Calculate statistical metrics
            positions = [
                run["finishing_position"]
                for run in recent_runs
                if run["finishing_position"] and run["finishing_position"] != 99
            ]

            best_position = min(positions) if positions else 99
            worst_position = max(positions) if positions else 99
            avg_position = sum(positions) / len(positions) if positions else 99.0

            # Calculate consistency (lower standard deviation = higher consistency)
            if len(positions) > 1:
                mean_pos = sum(positions) / len(positions)
                variance = sum((x - mean_pos) ** 2 for x in positions) / len(positions)
                std_dev = variance**0.5
                # Convert to 0-100 scale (lower std dev = higher consistency)
                consistency = max(0, 100 - (std_dev * 10))
            else:
                consistency = 50.0

            # Calculate days since last run
            if recent_runs:
                last_run_date = recent_runs[0]["race_date"]
                if isinstance(last_run_date, str):
                    try:
                        last_date = datetime.strptime(last_run_date, "%Y-%m-%d").date()
                        days_since_last = (date.today() - last_date).days
                    except:
                        days_since_last = 999
                else:
                    days_since_last = 999
            else:
                days_since_last = 999

            # Calculate confidence based on data quality
            confidence_factors = []
            confidence_factors.append(
                min(1.0, len(recent_runs) / self.config["max_recent_runs"])
            )
            confidence_factors.append(max(0.3, 1.0 - (days_since_last / 60.0)))
            confidence_factors.append(
                len(positions) / len(recent_runs) if recent_runs else 0
            )

            form_confidence = sum(confidence_factors) / len(confidence_factors)

            return FormAnalysisResult(
                horse_id=horse_id,
                horse_name=horse_name,
                race_id=race_id,
                recent_form_score=round(form_score, 1),
                form_trend=form_trend,
                form_trend_score=round(trend_score, 2),
                consistency_rating=round(consistency, 1),
                recent_runs_analyzed=len(recent_runs),
                best_recent_position=best_position,
                worst_recent_position=worst_position,
                average_recent_position=round(avg_position, 1),
                days_since_last_run=days_since_last,
                form_confidence=round(form_confidence, 2),
                class_progression="same",  # Simplified for now
                distance_suitability=0.5,  # Simplified for now
            )

        except Exception as e:
            self.logger.error(f"Form analysis failed for horse {horse_name}: {e}")
            raise

    def create_form_analysis_table(self):
        """Create the horse_form_analysis table"""

        create_table_query = """
            CREATE TABLE IF NOT EXISTS horse_form_analysis (
                id SERIAL PRIMARY KEY,
                horse_id BIGINT NOT NULL,
                horse_name VARCHAR(255) NOT NULL,
                race_id BIGINT NOT NULL,
                analysis_date DATE DEFAULT CURRENT_DATE,
                recent_form_score REAL NOT NULL,
                form_trend VARCHAR(20),
                form_trend_score REAL,
                consistency_rating REAL,
                recent_runs_analyzed INTEGER,
                best_recent_position INTEGER,
                worst_recent_position INTEGER,
                average_recent_position REAL,
                days_since_last_run INTEGER,
                form_confidence REAL,
                class_progression VARCHAR(10),
                distance_suitability REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_horse_race_analysis 
                    UNIQUE (horse_id, race_id, analysis_date)
            );
        """

        try:
            # Execute using docker exec
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
                create_table_query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info("Form analysis table created successfully")
                return True
            else:
                self.logger.error(f"Failed to create table: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error creating form analysis table: {e}")
            return False

    def analyze_race_form(self, race_id: int) -> List[FormAnalysisResult]:
        """Analyze form for all horses in a race"""

        try:
            # Get horses in the race
            query = f"""
                SELECT race_id, horse_id, name as horse_name, weight
                FROM racecard_details
                WHERE race_id = {race_id}
                ORDER BY name;
            """

            horses_data = self.execute_query("cards_horse_racing_db", query)

            if not horses_data:
                self.logger.warning(f"No horses found for race {race_id}")
                return []

            # Analyze form for each horse
            form_analyses = []

            self.logger.info(
                f"Analyzing form for {len(horses_data)} horses in race {race_id}"
            )

            for horse_row in horses_data:
                if len(horse_row) >= 3:
                    try:
                        horse_id = int(horse_row[1]) if horse_row[1].isdigit() else 0
                        horse_name = horse_row[2]

                        if horse_id > 0:
                            analysis = self.analyze_horse_form(
                                horse_id=horse_id,
                                horse_name=horse_name,
                                race_id=race_id,
                            )
                            form_analyses.append(analysis)

                    except Exception as e:
                        self.logger.error(
                            f"Failed to analyze form for horse {horse_row[2]}: {e}"
                        )

            self.logger.info(f"Form analysis completed for {len(form_analyses)} horses")
            return form_analyses

        except Exception as e:
            self.logger.error(f"Failed to analyze race form for race {race_id}: {e}")
            return []


def main():
    """Main function for testing form analysis"""

    print("🏇 Form Analysis System v2.04")
    print("=" * 40)

    try:
        # Initialize form analyzer
        analyzer = FormAnalyzer()

        # Create database table
        table_created = analyzer.create_form_analysis_table()
        if table_created:
            print("✅ Form analysis table created/verified")
        else:
            print("❌ Failed to create form analysis table")
            return 1

        # Test with a specific race ID that we know exists
        race_id = 183443  # Latest race ID we found earlier

        print(f"\n🔍 Testing form analysis on race {race_id}...")

        form_results = analyzer.analyze_race_form(race_id)

        if form_results:
            print(f"✅ Form analysis completed for {len(form_results)} horses")

            # Display top form horses
            sorted_horses = sorted(
                form_results, key=lambda x: x.recent_form_score, reverse=True
            )

            print(f"\nTop 3 horses by form score:")
            for i, horse in enumerate(sorted_horses[:3], 1):
                print(
                    f"  {i}. {horse.horse_name}: {horse.recent_form_score} "
                    f"({horse.form_trend}, confidence: {horse.form_confidence})"
                )

            print("\n✅ Form analysis system operational!")
            return 0
        else:
            print("❌ No form analysis completed")
            return 1

    except Exception as e:
        print(f"❌ Critical error in form analysis: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
