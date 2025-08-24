#!/usr/bin/env python3
"""
Enhanced Form Score Integration for Horse Racing AI v2.04
Comprehensive form analysis system for recent race performance scoring.

This module implements:
- Recent race performance scoring (last 3-5 runs)
- Form trend analysis (improving/declining patterns)
- Form confidence scoring
- Integration with existing prediction models
"""

import logging
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
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
    distance_suitability: float  # 0-1.0 based on recent distance performance


class EnhancedFormAnalyzer:
    """
    Comprehensive form analysis system for horse racing predictions.

    Analyzes recent race performance to provide:
    - Form scores based on recent finishing positions
    - Trend analysis (improving/declining form)
    - Consistency ratings
    - Distance and class suitability
    - Confidence scoring for form reliability
    """

    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Database configuration
        # Use docker exec to run queries since containers don't expose ports
        self.container_name = "horse_racing_postgres_clean"
        self.db_configs = {
            "results": {"database": "results_horse_racing_db", "user": "horse_racing"},
            "cards": {"database": "cards_horse_racing_db", "user": "horse_racing"},
            "metrics": {
                "database": "advanced_racing_metrics_db",
                "user": "horse_racing",
            },
        }

        # Form analysis configuration
        self.config = {
            "max_recent_runs": 5,  # Analyze last 5 races
            "min_runs_for_analysis": 2,  # Minimum runs needed for meaningful analysis
            "max_days_lookback": 180,  # Look back maximum 6 months
            "position_weights": [
                1.0,
                0.8,
                0.6,
                0.4,
                0.2,
            ],  # Weight recent runs more heavily
            "class_weight_factor": 0.15,  # Weight for class progression
            "distance_weight_factor": 0.10,  # Weight for distance suitability
        }

    def setup_logging(self):
        """Configure logging system"""
        # Create logs directory if it doesn't exist
        log_dir = "/home/jc/Documents/Horse-race-ai-v2.04/logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = f'{log_dir}/form_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
        )

    def get_database_connection(self, db_type: str):
        """Get database connection with error handling"""
        try:
            config = self.db_configs[db_type]
            conn = psycopg2.connect(**config)
            conn.autocommit = True
            return conn
        except Exception as e:
            self.logger.error(f"Database connection failed for {db_type}: {e}")
            raise

    def get_horse_recent_form(
        self, horse_id: int, analysis_date: date = None
    ) -> List[Dict]:
        """Get recent race form for a horse"""

        if analysis_date is None:
            analysis_date = date.today()

        cutoff_date = analysis_date - timedelta(days=self.config["max_days_lookback"])

        try:
            conn = self.get_database_connection("results")
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get recent race results
            query = """
                SELECT 
                    rr.race_id,
                    rr.horse_id,
                    rr.horse_name,
                    rr.finishing_position,
                    rr.total_runners,
                    rr.race_date,
                    rr.course,
                    rr.distance_yards,
                    rr.going,
                    rr.race_class,
                    rr.prize_money,
                    rr.beaten_lengths,
                    rr.jockey_name,
                    rr.trainer_name,
                    rr.weight_carried,
                    rr.odds_decimal
                FROM race_results rr
                WHERE rr.horse_id = %s 
                    AND rr.race_date >= %s
                    AND rr.race_date <= %s
                    AND rr.finishing_position IS NOT NULL
                ORDER BY rr.race_date DESC
                LIMIT %s
            """

            cursor.execute(
                query,
                (horse_id, cutoff_date, analysis_date, self.config["max_recent_runs"]),
            )
            recent_runs = cursor.fetchall()

            conn.close()

            return [dict(run) for run in recent_runs]

        except Exception as e:
            self.logger.error(f"Failed to get recent form for horse {horse_id}: {e}")
            return []

    def calculate_form_score(self, recent_runs: List[Dict]) -> float:
        """Calculate weighted form score based on recent finishing positions"""

        if not recent_runs:
            return 50.0  # Neutral score for no data

        total_weighted_score = 0.0
        total_weight = 0.0

        for i, run in enumerate(recent_runs):
            if i >= len(self.config["position_weights"]):
                break

            weight = self.config["position_weights"][i]
            position = run["finishing_position"]
            total_runners = run.get("total_runners", 12)  # Default field size

            # Convert position to percentage score (1st = 100%, last = 0%)
            if total_runners > 1:
                position_score = (
                    (total_runners - position) / (total_runners - 1)
                ) * 100
            else:
                position_score = 100.0 if position == 1 else 50.0

            total_weighted_score += position_score * weight
            total_weight += weight

        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 50.0

    def analyze_form_trend(self, recent_runs: List[Dict]) -> tuple[str, float]:
        """Analyze if horse's form is improving, declining, or stable"""

        if len(recent_runs) < 2:
            return "stable", 0.0

        # Calculate position percentages for trend analysis
        position_percentages = []
        for run in recent_runs:
            position = run["finishing_position"]
            total_runners = run.get("total_runners", 12)

            if total_runners > 1:
                percentage = ((total_runners - position) / (total_runners - 1)) * 100
            else:
                percentage = 100.0 if position == 1 else 50.0

            position_percentages.append(percentage)

        # Calculate trend using linear regression
        if len(position_percentages) >= 3:
            x = np.arange(len(position_percentages))
            y = np.array(position_percentages)

            # Fit linear trend
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]

            # Determine trend based on slope
            if slope > 5.0:  # Improving by >5% per run
                trend = "improving"
                trend_score = min(1.0, slope / 20.0)  # Cap at 1.0
            elif slope < -5.0:  # Declining by >5% per run
                trend = "declining"
                trend_score = max(-1.0, slope / 20.0)  # Cap at -1.0
            else:
                trend = "stable"
                trend_score = slope / 20.0

        else:
            # Simple comparison for 2 runs
            recent_avg = np.mean(position_percentages[:2])
            older_avg = np.mean(position_percentages[-2:])

            diff = recent_avg - older_avg

            if diff > 10.0:
                trend = "improving"
                trend_score = min(1.0, diff / 30.0)
            elif diff < -10.0:
                trend = "declining"
                trend_score = max(-1.0, diff / 30.0)
            else:
                trend = "stable"
                trend_score = diff / 30.0

        return trend, trend_score

    def calculate_consistency_rating(self, recent_runs: List[Dict]) -> float:
        """Calculate consistency rating based on variation in performance"""

        if len(recent_runs) < 2:
            return 50.0  # Neutral for insufficient data

        positions = [run["finishing_position"] for run in recent_runs]

        # Calculate coefficient of variation
        mean_position = np.mean(positions)
        std_position = np.std(positions)

        if mean_position > 0:
            cv = std_position / mean_position
            # Convert to 0-100 scale (lower CV = higher consistency)
            consistency = max(0, 100 - (cv * 50))
        else:
            consistency = 50.0

        return consistency

    def analyze_class_progression(self, recent_runs: List[Dict]) -> str:
        """Analyze if horse is moving up, down, or staying at same class level"""

        if len(recent_runs) < 2:
            return "same"

        class_levels = []
        for run in recent_runs:
            race_class = run.get("race_class", "Unknown")

            # Convert class to numeric for comparison
            if "Class 1" in str(race_class) or "Grade 1" in str(race_class):
                class_levels.append(1)
            elif "Class 2" in str(race_class) or "Grade 2" in str(race_class):
                class_levels.append(2)
            elif "Class 3" in str(race_class) or "Grade 3" in str(race_class):
                class_levels.append(3)
            elif "Class 4" in str(race_class):
                class_levels.append(4)
            elif "Class 5" in str(race_class):
                class_levels.append(5)
            elif "Class 6" in str(race_class):
                class_levels.append(6)
            else:
                class_levels.append(4)  # Default to Class 4

        if len(class_levels) >= 2:
            recent_class = np.mean(class_levels[:2])  # Most recent 2 runs
            older_class = np.mean(class_levels[-2:])  # Older runs

            if (
                recent_class < older_class - 0.5
            ):  # Moving to higher class (lower number)
                return "up"
            elif (
                recent_class > older_class + 0.5
            ):  # Moving to lower class (higher number)
                return "down"
            else:
                return "same"
        else:
            return "same"

    def calculate_distance_suitability(
        self, recent_runs: List[Dict], target_distance: int
    ) -> float:
        """Calculate suitability for target distance based on recent performances"""

        if not recent_runs or target_distance <= 0:
            return 0.5  # Neutral score

        distance_performances = []

        for run in recent_runs:
            run_distance = run.get("distance_yards", 0)
            if run_distance <= 0:
                continue

            # Calculate distance similarity (closer = better)
            distance_diff = abs(run_distance - target_distance)
            distance_similarity = max(0, 1 - (distance_diff / target_distance))

            # Get performance score for this run
            position = run["finishing_position"]
            total_runners = run.get("total_runners", 12)

            if total_runners > 1:
                performance_score = (total_runners - position) / (total_runners - 1)
            else:
                performance_score = 1.0 if position == 1 else 0.5

            # Weight performance by distance similarity
            weighted_performance = performance_score * distance_similarity
            distance_performances.append(weighted_performance)

        if distance_performances:
            return np.mean(distance_performances)
        else:
            return 0.5

    def calculate_form_confidence(
        self, recent_runs: List[Dict], analysis_result: FormAnalysisResult
    ) -> float:
        """Calculate confidence in form analysis based on data quality"""

        if not recent_runs:
            return 0.1  # Very low confidence

        confidence_factors = []

        # Factor 1: Number of recent runs (more runs = higher confidence)
        runs_factor = min(1.0, len(recent_runs) / self.config["max_recent_runs"])
        confidence_factors.append(runs_factor)

        # Factor 2: Recency of data (more recent = higher confidence)
        if recent_runs:
            days_since_last = analysis_result.days_since_last_run
            recency_factor = max(
                0.3, 1.0 - (days_since_last / 60.0)
            )  # Decay over 60 days
            confidence_factors.append(recency_factor)

        # Factor 3: Data completeness (complete data = higher confidence)
        complete_runs = sum(
            1
            for run in recent_runs
            if run.get("finishing_position") and run.get("total_runners")
        )
        completeness_factor = complete_runs / len(recent_runs) if recent_runs else 0
        confidence_factors.append(completeness_factor)

        # Factor 4: Consistency in analysis (stable form = higher confidence)
        if analysis_result.form_trend == "stable":
            trend_confidence = 0.8
        else:
            trend_confidence = min(
                0.9, 0.6 + abs(analysis_result.form_trend_score) * 0.3
            )
        confidence_factors.append(trend_confidence)

        # Calculate overall confidence
        overall_confidence = np.mean(confidence_factors)
        return max(0.1, min(1.0, overall_confidence))

    def analyze_horse_form(
        self,
        horse_id: int,
        horse_name: str,
        race_id: int,
        target_distance: int = None,
        analysis_date: date = None,
    ) -> FormAnalysisResult:
        """Perform comprehensive form analysis for a horse"""

        if analysis_date is None:
            analysis_date = date.today()

        try:
            # Get recent form data
            recent_runs = self.get_horse_recent_form(horse_id, analysis_date)

            if len(recent_runs) < self.config["min_runs_for_analysis"]:
                self.logger.warning(
                    f"Insufficient form data for horse {horse_name} (ID: {horse_id})"
                )
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
            consistency = self.calculate_consistency_rating(recent_runs)
            class_progression = self.analyze_class_progression(recent_runs)

            # Calculate distance suitability if target distance provided
            distance_suitability = 0.5
            if target_distance:
                distance_suitability = self.calculate_distance_suitability(
                    recent_runs, target_distance
                )

            # Calculate statistical metrics
            positions = [
                run["finishing_position"]
                for run in recent_runs
                if run["finishing_position"]
            ]
            best_position = min(positions) if positions else 99
            worst_position = max(positions) if positions else 99
            avg_position = np.mean(positions) if positions else 99.0

            # Calculate days since last run
            if recent_runs:
                last_run_date = recent_runs[0]["race_date"]
                if isinstance(last_run_date, str):
                    last_run_date = datetime.strptime(last_run_date, "%Y-%m-%d").date()
                days_since_last = (analysis_date - last_run_date).days
            else:
                days_since_last = 999

            # Create analysis result
            result = FormAnalysisResult(
                horse_id=horse_id,
                horse_name=horse_name,
                race_id=race_id,
                recent_form_score=form_score,
                form_trend=form_trend,
                form_trend_score=trend_score,
                consistency_rating=consistency,
                recent_runs_analyzed=len(recent_runs),
                best_recent_position=best_position,
                worst_recent_position=worst_position,
                average_recent_position=avg_position,
                days_since_last_run=days_since_last,
                form_confidence=0.0,  # Will be calculated next
                class_progression=class_progression,
                distance_suitability=distance_suitability,
            )

            # Calculate confidence score
            result.form_confidence = self.calculate_form_confidence(recent_runs, result)

            self.logger.info(
                f"Form analysis completed for {horse_name}: "
                f"Score={form_score:.1f}, Trend={form_trend}, Confidence={result.form_confidence:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Form analysis failed for horse {horse_name}: {e}")
            raise

    def create_form_analysis_table(self):
        """Create the horse_form_analysis table in the metrics database"""

        try:
            conn = self.get_database_connection("metrics")
            cursor = conn.cursor()

            create_table_sql = """
                CREATE TABLE IF NOT EXISTS horse_form_analysis (
                    id SERIAL PRIMARY KEY,
                    horse_id BIGINT NOT NULL,
                    horse_name VARCHAR(255) NOT NULL,
                    race_id BIGINT NOT NULL,
                    analysis_date DATE DEFAULT CURRENT_DATE,
                    
                    -- Form Scores
                    recent_form_score REAL NOT NULL,
                    form_trend VARCHAR(20),  -- 'improving', 'declining', 'stable'
                    form_trend_score REAL,  -- -1.0 to +1.0
                    consistency_rating REAL,
                    
                    -- Performance Statistics
                    recent_runs_analyzed INTEGER,
                    best_recent_position INTEGER,
                    worst_recent_position INTEGER,
                    average_recent_position REAL,
                    days_since_last_run INTEGER,
                    
                    -- Advanced Metrics
                    form_confidence REAL,  -- 0-1.0 confidence score
                    class_progression VARCHAR(10),  -- 'up', 'down', 'same'
                    distance_suitability REAL,  -- 0-1.0
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Constraints
                    CONSTRAINT unique_horse_race_analysis 
                        UNIQUE (horse_id, race_id, analysis_date)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_form_analysis_horse_race 
                    ON horse_form_analysis(horse_id, race_id);
                CREATE INDEX IF NOT EXISTS idx_form_analysis_date 
                    ON horse_form_analysis(analysis_date);
                CREATE INDEX IF NOT EXISTS idx_form_analysis_score 
                    ON horse_form_analysis(recent_form_score DESC);
            """

            cursor.execute(create_table_sql)
            conn.close()

            self.logger.info("Form analysis table created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create form analysis table: {e}")
            raise

    def save_form_analysis(self, analysis: FormAnalysisResult) -> bool:
        """Save form analysis result to database"""

        try:
            conn = self.get_database_connection("metrics")
            cursor = conn.cursor()

            insert_sql = """
                INSERT INTO horse_form_analysis (
                    horse_id, horse_name, race_id, 
                    recent_form_score, form_trend, form_trend_score, consistency_rating,
                    recent_runs_analyzed, best_recent_position, worst_recent_position, 
                    average_recent_position, days_since_last_run,
                    form_confidence, class_progression, distance_suitability
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (horse_id, race_id, analysis_date)
                DO UPDATE SET
                    recent_form_score = EXCLUDED.recent_form_score,
                    form_trend = EXCLUDED.form_trend,
                    form_trend_score = EXCLUDED.form_trend_score,
                    consistency_rating = EXCLUDED.consistency_rating,
                    recent_runs_analyzed = EXCLUDED.recent_runs_analyzed,
                    best_recent_position = EXCLUDED.best_recent_position,
                    worst_recent_position = EXCLUDED.worst_recent_position,
                    average_recent_position = EXCLUDED.average_recent_position,
                    days_since_last_run = EXCLUDED.days_since_last_run,
                    form_confidence = EXCLUDED.form_confidence,
                    class_progression = EXCLUDED.class_progression,
                    distance_suitability = EXCLUDED.distance_suitability,
                    created_at = CURRENT_TIMESTAMP
            """

            cursor.execute(
                insert_sql,
                (
                    analysis.horse_id,
                    analysis.horse_name,
                    analysis.race_id,
                    analysis.recent_form_score,
                    analysis.form_trend,
                    analysis.form_trend_score,
                    analysis.consistency_rating,
                    analysis.recent_runs_analyzed,
                    analysis.best_recent_position,
                    analysis.worst_recent_position,
                    analysis.average_recent_position,
                    analysis.days_since_last_run,
                    analysis.form_confidence,
                    analysis.class_progression,
                    analysis.distance_suitability,
                ),
            )

            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"Failed to save form analysis: {e}")
            return False

    def analyze_race_form(
        self, race_id: int, analysis_date: date = None
    ) -> List[FormAnalysisResult]:
        """Analyze form for all horses in a race"""

        if analysis_date is None:
            analysis_date = date.today()

        try:
            # Get horses in the race
            conn = self.get_database_connection("cards")
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                SELECT race_id, horse_id, horse_name, distance_yards
                FROM racecard_details
                WHERE race_id = %s
                ORDER BY horse_name
            """,
                (race_id,),
            )

            horses = cursor.fetchall()
            conn.close()

            if not horses:
                self.logger.warning(f"No horses found for race {race_id}")
                return []

            # Analyze form for each horse
            form_analyses = []

            self.logger.info(
                f"Analyzing form for {len(horses)} horses in race {race_id}"
            )

            for horse in horses:
                try:
                    analysis = self.analyze_horse_form(
                        horse_id=horse["horse_id"],
                        horse_name=horse["horse_name"],
                        race_id=race_id,
                        target_distance=horse.get("distance_yards"),
                        analysis_date=analysis_date,
                    )

                    # Save to database
                    save_success = self.save_form_analysis(analysis)
                    if save_success:
                        form_analyses.append(analysis)

                except Exception as e:
                    self.logger.error(
                        f"Failed to analyze form for horse {horse['horse_name']}: {e}"
                    )

            self.logger.info(f"Form analysis completed for {len(form_analyses)} horses")
            return form_analyses

        except Exception as e:
            self.logger.error(f"Failed to analyze race form for race {race_id}: {e}")
            return []


def main():
    """Main function for testing form analysis"""

    print("🏇 Enhanced Form Analysis System v2.04")
    print("=" * 50)

    try:
        # Initialize form analyzer
        analyzer = EnhancedFormAnalyzer()

        # Create database table
        analyzer.create_form_analysis_table()
        print("✅ Form analysis table created")

        # Get today's races for analysis
        conn = analyzer.get_database_connection("cards")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT race_id 
            FROM racecard_details 
            WHERE DATE(race_time) = CURRENT_DATE
            ORDER BY race_id
            LIMIT 3
        """
        )

        races = cursor.fetchall()
        conn.close()

        if not races:
            print("❌ No races found for today")
            return

        total_analyses = 0

        # Analyze form for each race
        for race_id_tuple in races:
            race_id = race_id_tuple[0]
            print(f"\n🔍 Analyzing form for race {race_id}...")

            form_results = analyzer.analyze_race_form(race_id)

            if form_results:
                print(f"✅ Form analysis completed for {len(form_results)} horses")
                total_analyses += len(form_results)

                # Display top form horses
                sorted_horses = sorted(
                    form_results, key=lambda x: x.recent_form_score, reverse=True
                )
                print(f"\nTop 3 horses by form score:")
                for i, horse in enumerate(sorted_horses[:3], 1):
                    print(
                        f"  {i}. {horse.horse_name}: {horse.recent_form_score:.1f} "
                        f"({horse.form_trend}, conf: {horse.form_confidence:.2f})"
                    )
            else:
                print(f"❌ No form analysis completed for race {race_id}")

        print(f"\n📊 Summary:")
        print(f"   Total form analyses: {total_analyses}")
        print(f"   Races analyzed: {len(races)}")

        if total_analyses > 0:
            print("✅ Form integration system operational!")
            return 0
        else:
            print("❌ Form integration system failed!")
            return 1

    except Exception as e:
        print(f"❌ Critical error in form analysis: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
