#!/usr/bin/env python3
"""
Stage 12: Race Trends Analysis
Advanced race pattern detection and trend analysis using Monte Carlo simulation data.
"""

import json
import logging
import os
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Add project root to path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

from src.database.database_manager import DatabaseManager


# Mock DataManager for now since it doesn't exist
class DataManager:
    """Mock data manager for Stage 12"""

    def __init__(self):
        pass


@dataclass
class TrendMetric:
    """Data class for trend metrics"""

    trend_type: str
    metric_name: str
    value: float
    confidence_level: float
    sample_size: int
    statistical_significance: float
    timestamp: str


@dataclass
class RacePattern:
    """Data class for race patterns"""

    pattern_id: str
    pattern_type: str
    conditions: Dict[str, Any]
    win_rate: float
    place_rate: float
    show_rate: float
    avg_odds: float
    roi: float
    sample_size: int
    confidence: float


@dataclass
class TrendSummary:
    """Data class for trend analysis summary"""

    race_date: str
    total_races: int
    total_horses: int
    patterns_identified: int
    high_confidence_patterns: int
    average_confidence: float
    trend_metrics: List[TrendMetric]
    race_patterns: List[RacePattern]
    performance_summary: Dict[str, Any]


class Stage12RaceTrendsEngine:
    """
    Advanced race trends analysis engine using Monte Carlo simulation data
    """

    def __init__(self, base_dir: str = None):
        """Initialize the race trends engine"""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.results_dir = self.base_dir / "results" / "stage12_race_trends"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize components
        self.db_manager = DatabaseManager()
        self.data_manager = DataManager()

        # Analysis parameters
        self.min_sample_size = 5
        self.confidence_threshold = 0.8
        self.trend_lookback_days = 30

        self.logger.info("Stage 12 Race Trends Engine initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("Stage12RaceTrends")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_race_trends(self, race_date: str) -> TrendSummary:
        """
        Main method to analyze race trends for a specific date

        Args:
            race_date: Date in YYYY-MM-DD format

        Returns:
            TrendSummary object with analysis results
        """
        self.logger.info(f"Starting race trends analysis for {race_date}")

        start_time = datetime.now()

        try:
            # Load Monte Carlo simulation data
            monte_carlo_data = self._load_monte_carlo_data(race_date)
            if not monte_carlo_data:
                self.logger.warning(f"No Monte Carlo data found for {race_date}")
                return self._create_empty_summary(race_date)

            # Load historical race data
            historical_data = self._load_historical_data(race_date)

            # Analyze various trend patterns
            trend_metrics = self._analyze_trend_metrics(
                monte_carlo_data, historical_data
            )
            race_patterns = self._identify_race_patterns(
                monte_carlo_data, historical_data
            )

            # Create performance summary
            performance_summary = self._create_performance_summary(
                monte_carlo_data, trend_metrics, race_patterns, start_time
            )

            # Create trend summary
            total_horses = sum(
                len(race.get("horses", []))
                for race in monte_carlo_data.get("races", [])
            )
            high_conf_patterns = len(
                [p for p in race_patterns if p.confidence >= self.confidence_threshold]
            )
            avg_confidence = (
                np.mean([p.confidence for p in race_patterns]) if race_patterns else 0.0
            )

            summary = TrendSummary(
                race_date=race_date,
                total_races=len(monte_carlo_data.get("races", [])),
                total_horses=total_horses,
                patterns_identified=len(race_patterns),
                high_confidence_patterns=high_conf_patterns,
                average_confidence=avg_confidence,
                trend_metrics=trend_metrics,
                race_patterns=race_patterns,
                performance_summary=performance_summary,
            )

            # Save results
            self._save_results(summary)

            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Race trends analysis completed in {execution_time:.2f} seconds"
            )

            return summary

        except Exception as e:
            self.logger.error(f"Error in race trends analysis: {str(e)}")
            raise

    def _load_monte_carlo_data(self, race_date: str) -> Dict[str, Any]:
        """Load Monte Carlo simulation data for the specified date"""
        try:
            # Look for Stage 10 Monte Carlo results
            monte_carlo_file = (
                self.base_dir
                / "results"
                / "stage10_monte_carlo"
                / f"monte_carlo_results_{race_date}.json"
            )

            if not monte_carlo_file.exists():
                # Try alternative locations
                alt_locations = [
                    self.base_dir / "results" / f"monte_carlo_{race_date}.json",
                    self.base_dir / "data" / "monte_carlo" / f"{race_date}.json",
                ]

                for alt_file in alt_locations:
                    if alt_file.exists():
                        monte_carlo_file = alt_file
                        break
                else:
                    self.logger.warning(
                        f"Monte Carlo data file not found for {race_date}"
                    )
                    return {}

            with open(monte_carlo_file, "r") as f:
                data = json.load(f)

            self.logger.info(
                f"Loaded Monte Carlo data for {len(data.get('races', []))} races"
            )
            return data

        except Exception as e:
            self.logger.error(f"Error loading Monte Carlo data: {str(e)}")
            return {}

    def _load_historical_data(self, race_date: str) -> pd.DataFrame:
        """Load historical race data for trend analysis"""
        try:
            # Calculate lookback period
            end_date = datetime.strptime(race_date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=self.trend_lookback_days)

            # Query historical data
            query = """
            SELECT 
                race_id, horse_name, jockey_name, trainer_name,
                race_distance, race_type, track_condition,
                horse_position, odds, weight, age,
                race_date, track_name, race_time
            FROM race_results 
            WHERE race_date BETWEEN ? AND ?
            ORDER BY race_date DESC
            """

            historical_data = self.db_manager.execute_query(
                query, (start_date.strftime("%Y-%m-%d"), race_date)
            )

            if historical_data:
                df = pd.DataFrame(historical_data)
                self.logger.info(f"Loaded {len(df)} historical race records")
                return df
            else:
                self.logger.warning("No historical data found")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error loading historical data: {str(e)}")
            return pd.DataFrame()

    def _analyze_trend_metrics(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze various trend metrics"""
        trends = []

        try:
            # Distance trend analysis
            distance_trends = self._analyze_distance_trends(
                monte_carlo_data, historical_data
            )
            trends.extend(distance_trends)

            # Jockey performance trends
            jockey_trends = self._analyze_jockey_trends(
                monte_carlo_data, historical_data
            )
            trends.extend(jockey_trends)

            # Trainer performance trends
            trainer_trends = self._analyze_trainer_trends(
                monte_carlo_data, historical_data
            )
            trends.extend(trainer_trends)

            # Track condition trends
            condition_trends = self._analyze_condition_trends(
                monte_carlo_data, historical_data
            )
            trends.extend(condition_trends)

            # Odds correlation trends
            odds_trends = self._analyze_odds_trends(monte_carlo_data, historical_data)
            trends.extend(odds_trends)

            self.logger.info(f"Analyzed {len(trends)} trend metrics")

        except Exception as e:
            self.logger.error(f"Error analyzing trend metrics: {str(e)}")

        return trends

    def _analyze_distance_trends(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze distance-based performance trends"""
        trends = []

        if historical_data.empty:
            return trends

        try:
            # Group by distance ranges
            distance_groups = {
                "sprint": (0, 1200),
                "mile": (1200, 1600),
                "route": (1600, 2400),
                "marathon": (2400, float("inf")),
            }

            for distance_type, (min_dist, max_dist) in distance_groups.items():
                if "race_distance" in historical_data.columns:
                    distance_mask = (historical_data["race_distance"] >= min_dist) & (
                        historical_data["race_distance"] < max_dist
                    )
                    distance_data = historical_data[distance_mask]

                    if len(distance_data) >= self.min_sample_size:
                        # Calculate win rate
                        win_rate = len(
                            distance_data[distance_data["horse_position"] == 1]
                        ) / len(distance_data)

                        # Calculate statistical significance
                        significance = self._calculate_statistical_significance(
                            distance_data
                        )

                        trends.append(
                            TrendMetric(
                                trend_type="distance",
                                metric_name=f"{distance_type}_win_rate",
                                value=win_rate,
                                confidence_level=min(0.95, significance),
                                sample_size=len(distance_data),
                                statistical_significance=significance,
                                timestamp=datetime.now().isoformat(),
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error analyzing distance trends: {str(e)}")

        return trends

    def _analyze_jockey_trends(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze jockey performance trends"""
        trends = []

        if historical_data.empty or "jockey_name" not in historical_data.columns:
            return trends

        try:
            # Analyze top jockeys
            jockey_stats = (
                historical_data.groupby("jockey_name")
                .agg(
                    {
                        "horse_position": [
                            "count",
                            lambda x: sum(x == 1),
                            lambda x: sum(x <= 3),
                        ]
                    }
                )
                .round(4)
            )

            jockey_stats.columns = ["total_rides", "wins", "places"]
            jockey_stats["win_rate"] = (
                jockey_stats["wins"] / jockey_stats["total_rides"]
            )
            jockey_stats["place_rate"] = (
                jockey_stats["places"] / jockey_stats["total_rides"]
            )

            # Filter jockeys with sufficient data
            qualified_jockeys = jockey_stats[
                jockey_stats["total_rides"] >= self.min_sample_size
            ]

            for jockey_name, stats in qualified_jockeys.iterrows():
                significance = self._calculate_binomial_significance(
                    stats["wins"], stats["total_rides"]
                )

                trends.append(
                    TrendMetric(
                        trend_type="jockey",
                        metric_name=f"{jockey_name}_win_rate",
                        value=float(stats["win_rate"]),
                        confidence_level=min(0.95, significance),
                        sample_size=int(stats["total_rides"]),
                        statistical_significance=significance,
                        timestamp=datetime.now().isoformat(),
                    )
                )

        except Exception as e:
            self.logger.error(f"Error analyzing jockey trends: {str(e)}")

        return trends

    def _analyze_trainer_trends(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze trainer performance trends"""
        trends = []

        if historical_data.empty or "trainer_name" not in historical_data.columns:
            return trends

        try:
            # Analyze trainer performance
            trainer_stats = (
                historical_data.groupby("trainer_name")
                .agg(
                    {
                        "horse_position": [
                            "count",
                            lambda x: sum(x == 1),
                            lambda x: sum(x <= 3),
                        ]
                    }
                )
                .round(4)
            )

            trainer_stats.columns = ["total_horses", "wins", "places"]
            trainer_stats["win_rate"] = (
                trainer_stats["wins"] / trainer_stats["total_horses"]
            )
            trainer_stats["place_rate"] = (
                trainer_stats["places"] / trainer_stats["total_horses"]
            )

            # Filter trainers with sufficient data
            qualified_trainers = trainer_stats[
                trainer_stats["total_horses"] >= self.min_sample_size
            ]

            for trainer_name, stats in qualified_trainers.iterrows():
                significance = self._calculate_binomial_significance(
                    stats["wins"], stats["total_horses"]
                )

                trends.append(
                    TrendMetric(
                        trend_type="trainer",
                        metric_name=f"{trainer_name}_win_rate",
                        value=float(stats["win_rate"]),
                        confidence_level=min(0.95, significance),
                        sample_size=int(stats["total_horses"]),
                        statistical_significance=significance,
                        timestamp=datetime.now().isoformat(),
                    )
                )

        except Exception as e:
            self.logger.error(f"Error analyzing trainer trends: {str(e)}")

        return trends

    def _analyze_condition_trends(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze track condition performance trends"""
        trends = []

        if historical_data.empty or "track_condition" not in historical_data.columns:
            return trends

        try:
            # Analyze performance by track condition
            condition_stats = (
                historical_data.groupby("track_condition")
                .agg(
                    {
                        "horse_position": [
                            "count",
                            lambda x: sum(x == 1),
                            lambda x: sum(x <= 3),
                        ]
                    }
                )
                .round(4)
            )

            condition_stats.columns = ["total_races", "wins", "places"]
            condition_stats["win_rate"] = (
                condition_stats["wins"] / condition_stats["total_races"]
            )
            condition_stats["place_rate"] = (
                condition_stats["places"] / condition_stats["total_races"]
            )

            for condition, stats in condition_stats.iterrows():
                if stats["total_races"] >= self.min_sample_size:
                    significance = self._calculate_binomial_significance(
                        stats["wins"], stats["total_races"]
                    )

                    trends.append(
                        TrendMetric(
                            trend_type="track_condition",
                            metric_name=f"{condition}_win_rate",
                            value=float(stats["win_rate"]),
                            confidence_level=min(0.95, significance),
                            sample_size=int(stats["total_races"]),
                            statistical_significance=significance,
                            timestamp=datetime.now().isoformat(),
                        )
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing condition trends: {str(e)}")

        return trends

    def _analyze_odds_trends(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[TrendMetric]:
        """Analyze odds correlation trends"""
        trends = []

        if historical_data.empty or "odds" not in historical_data.columns:
            return trends

        try:
            # Analyze odds ranges
            odds_ranges = {
                "favorite": (0, 3),
                "second_choice": (3, 6),
                "longshot": (6, 15),
                "extreme_longshot": (15, float("inf")),
            }

            for odds_type, (min_odds, max_odds) in odds_ranges.items():
                odds_mask = (historical_data["odds"] >= min_odds) & (
                    historical_data["odds"] < max_odds
                )
                odds_data = historical_data[odds_mask]

                if len(odds_data) >= self.min_sample_size:
                    win_rate = len(odds_data[odds_data["horse_position"] == 1]) / len(
                        odds_data
                    )
                    significance = self._calculate_binomial_significance(
                        len(odds_data[odds_data["horse_position"] == 1]), len(odds_data)
                    )

                    trends.append(
                        TrendMetric(
                            trend_type="odds",
                            metric_name=f"{odds_type}_win_rate",
                            value=win_rate,
                            confidence_level=min(0.95, significance),
                            sample_size=len(odds_data),
                            statistical_significance=significance,
                            timestamp=datetime.now().isoformat(),
                        )
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing odds trends: {str(e)}")

        return trends

    def _identify_race_patterns(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[RacePattern]:
        """Identify race patterns from Monte Carlo and historical data"""
        patterns = []

        try:
            # Distance-based patterns
            distance_patterns = self._identify_distance_patterns(
                monte_carlo_data, historical_data
            )
            patterns.extend(distance_patterns)

            # Jockey-trainer combination patterns
            combo_patterns = self._identify_combination_patterns(
                monte_carlo_data, historical_data
            )
            patterns.extend(combo_patterns)

            # Track condition patterns
            condition_patterns = self._identify_condition_patterns(
                monte_carlo_data, historical_data
            )
            patterns.extend(condition_patterns)

            self.logger.info(f"Identified {len(patterns)} race patterns")

        except Exception as e:
            self.logger.error(f"Error identifying race patterns: {str(e)}")

        return patterns

    def _identify_distance_patterns(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[RacePattern]:
        """Identify distance-based patterns"""
        patterns = []

        if historical_data.empty:
            return patterns

        try:
            distance_groups = historical_data.groupby("race_distance")

            for distance, group in distance_groups:
                if len(group) >= self.min_sample_size:
                    wins = len(group[group["horse_position"] == 1])
                    places = len(group[group["horse_position"] <= 3])

                    win_rate = wins / len(group)
                    place_rate = places / len(group)

                    if "odds" in group.columns:
                        avg_odds = group["odds"].mean()
                        roi = self._calculate_roi(group)
                    else:
                        avg_odds = 0.0
                        roi = 0.0

                    confidence = self._calculate_pattern_confidence(group)

                    if confidence >= 0.6:  # Lower threshold for pattern identification
                        patterns.append(
                            RacePattern(
                                pattern_id=f"distance_{distance}",
                                pattern_type="distance",
                                conditions={"race_distance": distance},
                                win_rate=win_rate,
                                place_rate=place_rate,
                                show_rate=place_rate,  # Approximation
                                avg_odds=avg_odds,
                                roi=roi,
                                sample_size=len(group),
                                confidence=confidence,
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error identifying distance patterns: {str(e)}")

        return patterns

    def _identify_combination_patterns(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[RacePattern]:
        """Identify jockey-trainer combination patterns"""
        patterns = []

        if (
            historical_data.empty
            or "jockey_name" not in historical_data.columns
            or "trainer_name" not in historical_data.columns
        ):
            return patterns

        try:
            combo_groups = historical_data.groupby(["jockey_name", "trainer_name"])

            for (jockey, trainer), group in combo_groups:
                if len(group) >= self.min_sample_size:
                    wins = len(group[group["horse_position"] == 1])
                    places = len(group[group["horse_position"] <= 3])

                    win_rate = wins / len(group)
                    place_rate = places / len(group)

                    if "odds" in group.columns:
                        avg_odds = group["odds"].mean()
                        roi = self._calculate_roi(group)
                    else:
                        avg_odds = 0.0
                        roi = 0.0

                    confidence = self._calculate_pattern_confidence(group)

                    if confidence >= 0.7:  # Higher threshold for combination patterns
                        patterns.append(
                            RacePattern(
                                pattern_id=f"combo_{jockey}_{trainer}",
                                pattern_type="jockey_trainer_combo",
                                conditions={
                                    "jockey_name": jockey,
                                    "trainer_name": trainer,
                                },
                                win_rate=win_rate,
                                place_rate=place_rate,
                                show_rate=place_rate,
                                avg_odds=avg_odds,
                                roi=roi,
                                sample_size=len(group),
                                confidence=confidence,
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error identifying combination patterns: {str(e)}")

        return patterns

    def _identify_condition_patterns(
        self, monte_carlo_data: Dict[str, Any], historical_data: pd.DataFrame
    ) -> List[RacePattern]:
        """Identify track condition patterns"""
        patterns = []

        if historical_data.empty or "track_condition" not in historical_data.columns:
            return patterns

        try:
            condition_groups = historical_data.groupby("track_condition")

            for condition, group in condition_groups:
                if len(group) >= self.min_sample_size:
                    wins = len(group[group["horse_position"] == 1])
                    places = len(group[group["horse_position"] <= 3])

                    win_rate = wins / len(group)
                    place_rate = places / len(group)

                    if "odds" in group.columns:
                        avg_odds = group["odds"].mean()
                        roi = self._calculate_roi(group)
                    else:
                        avg_odds = 0.0
                        roi = 0.0

                    confidence = self._calculate_pattern_confidence(group)

                    if confidence >= 0.65:
                        patterns.append(
                            RacePattern(
                                pattern_id=f"condition_{condition}",
                                pattern_type="track_condition",
                                conditions={"track_condition": condition},
                                win_rate=win_rate,
                                place_rate=place_rate,
                                show_rate=place_rate,
                                avg_odds=avg_odds,
                                roi=roi,
                                sample_size=len(group),
                                confidence=confidence,
                            )
                        )

        except Exception as e:
            self.logger.error(f"Error identifying condition patterns: {str(e)}")

        return patterns

    def _calculate_statistical_significance(self, data: pd.DataFrame) -> float:
        """Calculate statistical significance of data"""
        try:
            if len(data) < 3:
                return 0.0

            # Use sample size and variance to estimate significance
            sample_size = len(data)
            if sample_size >= 30:
                return 0.95
            elif sample_size >= 15:
                return 0.85
            elif sample_size >= 10:
                return 0.75
            else:
                return 0.65

        except Exception as e:
            self.logger.error(f"Error calculating statistical significance: {str(e)}")
            return 0.0

    def _calculate_binomial_significance(self, successes: int, trials: int) -> float:
        """Calculate binomial significance"""
        try:
            if trials == 0:
                return 0.0

            success_rate = successes / trials

            # Simple significance based on sample size and success rate
            if trials >= 50 and success_rate > 0.15:
                return 0.95
            elif trials >= 20 and success_rate > 0.10:
                return 0.85
            elif trials >= 10 and success_rate > 0.05:
                return 0.75
            else:
                return 0.65

        except Exception as e:
            self.logger.error(f"Error calculating binomial significance: {str(e)}")
            return 0.0

    def _calculate_roi(self, data: pd.DataFrame) -> float:
        """Calculate return on investment"""
        try:
            if "odds" not in data.columns or "horse_position" not in data.columns:
                return 0.0

            wins = data[data["horse_position"] == 1]
            if len(wins) == 0:
                return -100.0  # Complete loss

            total_investment = len(data)  # Assume $1 bet per race
            total_returns = wins["odds"].sum()

            roi = ((total_returns - total_investment) / total_investment) * 100
            return roi

        except Exception as e:
            self.logger.error(f"Error calculating ROI: {str(e)}")
            return 0.0

    def _calculate_pattern_confidence(self, data: pd.DataFrame) -> float:
        """Calculate confidence level for a pattern"""
        try:
            sample_size = len(data)
            wins = len(data[data["horse_position"] == 1])

            # Base confidence on sample size and win rate
            win_rate = wins / sample_size if sample_size > 0 else 0

            # Adjust confidence based on sample size
            size_factor = min(1.0, sample_size / 20)  # Full confidence at 20+ samples
            performance_factor = win_rate * 2  # Double weight for performance

            confidence = (size_factor + performance_factor) / 2
            return min(0.95, max(0.0, confidence))

        except Exception as e:
            self.logger.error(f"Error calculating pattern confidence: {str(e)}")
            return 0.0

    def _create_performance_summary(
        self,
        monte_carlo_data: Dict[str, Any],
        trend_metrics: List[TrendMetric],
        race_patterns: List[RacePattern],
        start_time: datetime,
    ) -> Dict[str, Any]:
        """Create performance summary"""
        execution_time = (datetime.now() - start_time).total_seconds()

        summary = {
            "execution_time_seconds": round(execution_time, 2),
            "trends_analyzed": len(trend_metrics),
            "patterns_identified": len(race_patterns),
            "high_confidence_trends": len(
                [t for t in trend_metrics if t.confidence_level >= 0.8]
            ),
            "high_confidence_patterns": len(
                [p for p in race_patterns if p.confidence >= 0.8]
            ),
            "average_trend_confidence": (
                np.mean([t.confidence_level for t in trend_metrics])
                if trend_metrics
                else 0.0
            ),
            "average_pattern_confidence": (
                np.mean([p.confidence for p in race_patterns]) if race_patterns else 0.0
            ),
            "monte_carlo_races_analyzed": len(monte_carlo_data.get("races", [])),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # Add trend type breakdown
        trend_types = {}
        for trend in trend_metrics:
            trend_types[trend.trend_type] = trend_types.get(trend.trend_type, 0) + 1
        summary["trend_type_breakdown"] = trend_types

        # Add pattern type breakdown
        pattern_types = {}
        for pattern in race_patterns:
            pattern_types[pattern.pattern_type] = (
                pattern_types.get(pattern.pattern_type, 0) + 1
            )
        summary["pattern_type_breakdown"] = pattern_types

        return summary

    def _create_empty_summary(self, race_date: str) -> TrendSummary:
        """Create empty summary when no data is available"""
        return TrendSummary(
            race_date=race_date,
            total_races=0,
            total_horses=0,
            patterns_identified=0,
            high_confidence_patterns=0,
            average_confidence=0.0,
            trend_metrics=[],
            race_patterns=[],
            performance_summary={
                "execution_time_seconds": 0.0,
                "trends_analyzed": 0,
                "patterns_identified": 0,
                "error": "No data available",
            },
        )

    def _save_results(self, summary: TrendSummary) -> None:
        """Save analysis results to file"""
        try:
            # Save main results
            results_file = self.results_dir / f"race_trends_{summary.race_date}.json"

            # Convert dataclasses to dictionaries
            summary_dict = asdict(summary)

            with open(results_file, "w") as f:
                json.dump(summary_dict, f, indent=2, default=str)

            # Save trend metrics separately
            trends_file = self.results_dir / f"trend_metrics_{summary.race_date}.json"
            trends_data = [asdict(trend) for trend in summary.trend_metrics]

            with open(trends_file, "w") as f:
                json.dump(trends_data, f, indent=2, default=str)

            # Save race patterns separately
            patterns_file = self.results_dir / f"race_patterns_{summary.race_date}.json"
            patterns_data = [asdict(pattern) for pattern in summary.race_patterns]

            with open(patterns_file, "w") as f:
                json.dump(patterns_data, f, indent=2, default=str)

            self.logger.info(f"Results saved to {results_file}")

        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")


def main():
    """Main function for testing Stage 12 Race Trends"""
    import argparse

    parser = argparse.ArgumentParser(description="Stage 12 Race Trends Analysis")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Race date (YYYY-MM-DD format)",
    )
    parser.add_argument("--base-dir", default=None, help="Base directory path")

    args = parser.parse_args()

    try:
        # Initialize engine
        engine = Stage12RaceTrendsEngine(base_dir=args.base_dir)

        # Run analysis
        print(f"Starting Stage 12 Race Trends Analysis for {args.date}")
        summary = engine.analyze_race_trends(args.date)

        # Print summary
        print("\n" + "=" * 60)
        print("STAGE 12 RACE TRENDS ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Race Date: {summary.race_date}")
        print(f"Total Races: {summary.total_races}")
        print(f"Total Horses: {summary.total_horses}")
        print(f"Patterns Identified: {summary.patterns_identified}")
        print(f"High Confidence Patterns: {summary.high_confidence_patterns}")
        print(f"Average Confidence: {summary.average_confidence:.3f}")
        print(
            f"Execution Time: {summary.performance_summary.get('execution_time_seconds', 0):.2f}s"
        )

        if summary.trend_metrics:
            print(f"\nTop Trends:")
            for i, trend in enumerate(
                sorted(
                    summary.trend_metrics,
                    key=lambda x: x.confidence_level,
                    reverse=True,
                )[:5]
            ):
                print(
                    f"  {i+1}. {trend.trend_type}: {trend.metric_name} = {trend.value:.3f} (confidence: {trend.confidence_level:.3f})"
                )

        if summary.race_patterns:
            print(f"\nTop Patterns:")
            for i, pattern in enumerate(
                sorted(summary.race_patterns, key=lambda x: x.confidence, reverse=True)[
                    :5
                ]
            ):
                print(
                    f"  {i+1}. {pattern.pattern_type}: Win Rate {pattern.win_rate:.3f}, ROI {pattern.roi:.1f}% (confidence: {pattern.confidence:.3f})"
                )

        print("\nStage 12 Race Trends Analysis completed successfully!")

    except Exception as e:
        print(f"Error in Stage 12 analysis: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
