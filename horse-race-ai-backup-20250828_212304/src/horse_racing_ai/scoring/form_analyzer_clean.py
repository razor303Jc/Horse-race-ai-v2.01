"""
Enhanced Form Analyzer for Horse Racing
=======================================

Advanced form analysis incorporating multiple factors for more accurate
horse performance evaluation.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

import numpy as np
import pandas as pd
import structlog
from sklearn.preprocessing import MinMaxScaler

logger = structlog.get_logger(__name__)


class SurfaceType(Enum):
    """Track surface types."""

    TURF = "turf"
    DIRT = "dirt"
    SYNTHETIC = "synthetic"
    ALL_WEATHER = "all_weather"


class RaceClass(Enum):
    """Race classification levels."""

    MAIDEN = 1
    CLAIMING = 2
    ALLOWANCE = 3
    STAKES = 4
    GRADED_STAKES = 5


@dataclass
class FormMetrics:
    """Comprehensive form analysis metrics."""

    # Recent form scores
    last_run_score: float
    recent_form_score: float  # Last 3 runs
    seasonal_form_score: float  # Current season

    # Speed metrics
    speed_rating: float
    pace_rating: float
    finishing_speed_index: float

    # Consistency metrics
    consistency_index: float
    reliability_score: float

    # Class and competition
    class_rating: float
    competition_strength: float

    # Track and conditions
    track_bias_adjustment: float
    condition_suitability: float

    # Distance and trip
    distance_suitability: float
    trip_efficiency: float

    # Jockey/Trainer combination
    jockey_form: float
    trainer_form: float
    combo_efficiency: float

    # Overall composite scores
    form_composite: float
    power_rating: float
    confidence_level: float


@dataclass
class RacePerformance:
    """Individual race performance data."""

    date: datetime
    track: str
    distance: float  # In furlongs
    surface: SurfaceType
    race_class: RaceClass
    field_size: int
    finish_position: int
    beaten_lengths: float
    time: Optional[float]  # In seconds
    speed_figure: Optional[int]
    pace_figures: Optional[Dict[str, int]]  # Early, middle, late pace
    weight_carried: int
    jockey: str
    trainer: str
    odds: Optional[float]
    purse: float
    conditions: str
    comments: Optional[str]


class EnhancedFormAnalyzer:
    """
    Enhanced form analyzer with comprehensive handicapping factors.

    Improvements over basic systems:
    - Multi-layered speed analysis (early, middle, late pace)
    - Dynamic class ratings based on performance
    - Trip efficiency analysis
    - Trainer/jockey form cycles
    - Surface and distance specialization
    - Pace scenario analysis
    - Recency weighting with quality adjustments
    """

    def __init__(self, lookback_days: int = 365):
        """
        Initialize the form analyzer.

        Args:
            lookback_days: How far back to analyze form data
        """
        self.lookback_days = lookback_days
        self.scaler = MinMaxScaler()
        self._initialize_weights()

    def _initialize_weights(self) -> None:
        """Initialize factor weights for composite scoring."""
        self.weights = {
            "recent_form": 0.25,
            "speed_rating": 0.20,
            "class_rating": 0.15,
            "consistency": 0.12,
            "distance_suitability": 0.08,
            "track_conditions": 0.08,
            "jockey_trainer": 0.07,
            "pace_rating": 0.05,
        }

    def analyze_horse_form(
        self,
        horse_name: str,
        performances: List[RacePerformance],
        target_race_conditions: Dict[str, Union[str, float, int]],
    ) -> FormMetrics:
        """
        Analyze comprehensive form for a horse.

        Args:
            horse_name: Name of the horse
            performances: List of recent race performances
            target_race_conditions: Conditions of upcoming race

        Returns:
            Comprehensive form metrics
        """
        logger.info(
            f"Analyzing form for {horse_name} with {len(performances)} performances"
        )

        if not performances:
            return self._default_form_metrics()

        # Filter relevant performances
        cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
        recent_performances = [p for p in performances if p.date >= cutoff_date]

        if not recent_performances:
            return self._default_form_metrics()

        # Calculate individual components
        recent_form = self._calculate_recent_form(recent_performances)
        speed_metrics = self._calculate_speed_metrics(
            recent_performances, target_race_conditions
        )
        consistency = self._calculate_consistency_metrics(recent_performances)
        class_metrics = self._calculate_class_metrics(
            recent_performances, target_race_conditions
        )
        track_metrics = self._calculate_track_metrics(
            recent_performances, target_race_conditions
        )
        distance_metrics = self._calculate_distance_metrics(
            recent_performances, target_race_conditions
        )
        jockey_trainer_metrics = self._calculate_jockey_trainer_metrics(
            recent_performances
        )

        # Calculate composite scores
        form_composite = self._calculate_composite_score(
            {
                "recent_form": recent_form,
                "speed_rating": speed_metrics["speed_rating"],
                "class_rating": class_metrics["class_rating"],
                "consistency": consistency["consistency_index"],
                "distance_suitability": distance_metrics["distance_suitability"],
                "track_conditions": track_metrics["condition_suitability"],
                "jockey_trainer": jockey_trainer_metrics["combo_efficiency"],
                "pace_rating": speed_metrics["pace_rating"],
            }
        )

        # Power rating calculation (0-150 scale)
        power_rating = min(
            150.0,
            max(
                0.0,
                form_composite * 100.0
                + speed_metrics["speed_rating"] * 0.3
                + class_metrics["class_rating"] * 0.2,
            ),
        )

        # Confidence calculation based on data quality and consistency
        confidence_level = self._calculate_confidence(
            recent_performances, consistency["reliability_score"]
        )

        return FormMetrics(
            last_run_score=recent_form,
            recent_form_score=self._calculate_weighted_recent_form(
                recent_performances[:3]
            ),
            seasonal_form_score=self._calculate_seasonal_form(recent_performances),
            speed_rating=speed_metrics["speed_rating"],
            pace_rating=speed_metrics["pace_rating"],
            finishing_speed_index=speed_metrics["finishing_speed_index"],
            consistency_index=consistency["consistency_index"],
            reliability_score=consistency["reliability_score"],
            class_rating=class_metrics["class_rating"],
            competition_strength=class_metrics["competition_strength"],
            track_bias_adjustment=track_metrics["track_bias_adjustment"],
            condition_suitability=track_metrics["condition_suitability"],
            distance_suitability=distance_metrics["distance_suitability"],
            trip_efficiency=distance_metrics["trip_efficiency"],
            jockey_form=jockey_trainer_metrics["jockey_form"],
            trainer_form=jockey_trainer_metrics["trainer_form"],
            combo_efficiency=jockey_trainer_metrics["combo_efficiency"],
            form_composite=form_composite,
            power_rating=power_rating,
            confidence_level=confidence_level,
        )

    def _calculate_recent_form(self, performances: List[RacePerformance]) -> float:
        """Calculate recent form score with recency weighting."""
        if not performances:
            return 0.5

        # Sort by date, most recent first
        sorted_perfs = sorted(performances, key=lambda x: x.date, reverse=True)

        # Calculate position-based scores (1st = 1.0, last = 0.0)
        scores = []
        weights = []

        for i, perf in enumerate(sorted_perfs[:5]):  # Last 5 runs
            # Position score (invert so 1st = highest)
            pos_score = max(
                0.0, 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            )

            # Beaten lengths adjustment
            if perf.beaten_lengths > 0:
                length_penalty = min(0.5, perf.beaten_lengths / 20.0)  # Max penalty 0.5
                pos_score = max(0.0, pos_score - length_penalty)

            # Recency weight (exponential decay)
            days_ago = (datetime.now() - perf.date).days
            recency_weight = np.exp(-days_ago / 60.0)  # 60-day half-life

            scores.append(pos_score)
            weights.append(recency_weight)

        if not scores:
            return 0.5

        # Weighted average
        weighted_score = float(np.average(scores, weights=weights))
        return min(1.0, max(0.0, weighted_score))

    def _calculate_speed_metrics(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, Union[str, float, int]],
    ) -> Dict[str, float]:
        """Calculate comprehensive speed metrics."""

        if not performances:
            return {
                "speed_rating": 50.0,
                "pace_rating": 50.0,
                "finishing_speed_index": 50.0,
            }

        speed_figures = [
            p.speed_figure for p in performances if p.speed_figure is not None
        ]

        if not speed_figures:
            # Calculate basic speed rating from times and class
            speed_rating = self._estimate_speed_from_performance(performances)
        else:
            # Use actual speed figures with adjustments
            if len(speed_figures) >= 3:
                recent_figures = speed_figures[-3:]
            else:
                recent_figures = speed_figures
            speed_rating = float(np.mean(recent_figures))
            speed_rating = max(0.0, min(120.0, speed_rating))  # Normalize

        # Pace analysis
        pace_rating = self._calculate_pace_rating(performances, target_conditions)

        # Finishing speed index (late pace and finishing kick)
        finishing_speed_index = self._calculate_finishing_speed(performances)

        return {
            "speed_rating": speed_rating,
            "pace_rating": pace_rating,
            "finishing_speed_index": finishing_speed_index,
        }

    def _calculate_consistency_metrics(
        self, performances: List[RacePerformance]
    ) -> Dict[str, float]:
        """Calculate consistency and reliability metrics."""

        if len(performances) < 3:
            return {"consistency_index": 0.5, "reliability_score": 0.5}

        # Position consistency
        positions = [p.finish_position for p in performances]
        field_sizes = [p.field_size for p in performances]

        # Normalize positions by field size
        normalized_positions = [
            pos / field_size for pos, field_size in zip(positions, field_sizes)
        ]

        # Calculate coefficient of variation (lower is more consistent)
        mean_pos = float(np.mean(normalized_positions))
        std_pos = float(np.std(normalized_positions))
        cv = std_pos / mean_pos if mean_pos > 0 else 1.0

        # Convert to consistency index (higher is better)
        consistency_index = max(0.0, 1.0 - cv)

        # Reliability based on frequency of poor runs
        poor_runs = sum(1 for pos in normalized_positions if pos > 0.7)
        reliability_score = max(0.0, 1.0 - (poor_runs / len(performances)))

        return {
            "consistency_index": consistency_index,
            "reliability_score": reliability_score,
        }

    def _calculate_class_metrics(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, Union[str, float, int]],
    ) -> Dict[str, float]:
        """Calculate class and competition strength metrics."""

        if not performances:
            return {"class_rating": 50.0, "competition_strength": 50.0}

        # Class progression analysis
        class_values = [p.race_class.value for p in performances]
        target_class = float(
            target_conditions.get("race_class", RaceClass.ALLOWANCE.value)
        )

        # Recent class level vs target
        recent_class = float(
            np.mean(class_values[-3:])
            if len(class_values) >= 3
            else np.mean(class_values)
        )
        class_differential = target_class - recent_class

        # Class rating (higher class = higher rating)
        class_rating = (
            50.0 + (recent_class - 2.5) * 20.0
        )  # Scale around allowance level
        class_rating = max(0.0, min(100.0, class_rating))

        # Competition strength based on purse and field quality
        purses = [p.purse for p in performances if p.purse > 0]
        avg_purse = float(np.mean(purses)) if purses else 50000.0

        # Normalize purse to 0-100 scale (log scale)
        competition_strength = min(
            100.0, max(0.0, 30.0 + 20.0 * np.log10(avg_purse / 10000.0))
        )

        return {
            "class_rating": class_rating,
            "competition_strength": competition_strength,
        }

    def _calculate_track_metrics(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, Union[str, float, int]],
    ) -> Dict[str, float]:
        """Calculate track and condition-specific metrics."""

        target_surface = str(target_conditions.get("surface", "dirt"))
        target_track = str(target_conditions.get("track", ""))

        # Surface specialization
        surface_performances = [
            p for p in performances if p.surface.value == target_surface
        ]

        if surface_performances:
            surface_form = self._calculate_recent_form(surface_performances)
        else:
            surface_form = 0.5  # Neutral if no surface experience

        # Track specialization
        track_performances = [p for p in performances if p.track == target_track]

        if track_performances:
            track_form = self._calculate_recent_form(track_performances)
        else:
            track_form = 0.5  # Neutral if no track experience

        # Condition suitability (combine surface and track)
        condition_suitability = surface_form * 0.7 + track_form * 0.3

        # Track bias adjustment (placeholder - would need track bias data)
        track_bias_adjustment = 0.0

        return {
            "condition_suitability": condition_suitability,
            "track_bias_adjustment": track_bias_adjustment,
        }

    def _calculate_distance_metrics(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, Union[str, float, int]],
    ) -> Dict[str, float]:
        """Calculate distance suitability and trip efficiency."""

        target_distance = float(
            target_conditions.get("distance", 8.0)
        )  # Default 1 mile

        # Distance specialization
        distance_tolerance = 1.0  # +/- 1 furlong tolerance

        suitable_distances = [
            p
            for p in performances
            if abs(p.distance - target_distance) <= distance_tolerance
        ]

        if suitable_distances:
            distance_form = self._calculate_recent_form(suitable_distances)
        else:
            # Use broader range if no exact matches
            broader_distances = [
                p for p in performances if abs(p.distance - target_distance) <= 2.0
            ]
            distance_form = (
                self._calculate_recent_form(broader_distances)
                if broader_distances
                else 0.5
            )

        # Trip efficiency (ability to handle the distance)
        trip_efficiency = self._calculate_trip_efficiency(performances, target_distance)

        return {
            "distance_suitability": distance_form,
            "trip_efficiency": trip_efficiency,
        }

    def _calculate_jockey_trainer_metrics(
        self, performances: List[RacePerformance]
    ) -> Dict[str, float]:
        """Calculate jockey and trainer form metrics."""

        if not performances:
            return {"jockey_form": 0.5, "trainer_form": 0.5, "combo_efficiency": 0.5}

        # Jockey form (recent performance with this jockey)
        jockeys = [p.jockey for p in performances]
        most_recent_jockey = jockeys[-1] if jockeys else ""

        jockey_performances = [
            p for p in performances if p.jockey == most_recent_jockey
        ]
        jockey_form = (
            self._calculate_recent_form(jockey_performances)
            if jockey_performances
            else 0.5
        )

        # Trainer form
        trainers = [p.trainer for p in performances]
        current_trainer = trainers[-1] if trainers else ""

        trainer_performances = [p for p in performances if p.trainer == current_trainer]
        trainer_form = (
            self._calculate_recent_form(trainer_performances)
            if trainer_performances
            else 0.5
        )

        # Combination efficiency
        combo_performances = [
            p
            for p in performances
            if p.jockey == most_recent_jockey and p.trainer == current_trainer
        ]

        if combo_performances:
            combo_efficiency = self._calculate_recent_form(combo_performances)
        else:
            # If no combination history, average jockey and trainer form
            combo_efficiency = (jockey_form + trainer_form) / 2.0

        return {
            "jockey_form": jockey_form,
            "trainer_form": trainer_form,
            "combo_efficiency": combo_efficiency,
        }

    def _calculate_weighted_recent_form(
        self, recent_performances: List[RacePerformance]
    ) -> float:
        """Calculate weighted form for last 3 runs."""
        if not recent_performances:
            return 0.5

        # Weight more recent performances higher
        weights = [0.5, 0.3, 0.2][: len(recent_performances)]

        scores = []
        for perf in recent_performances:
            pos_score = max(
                0.0, 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            )
            scores.append(pos_score)

        return float(np.average(scores, weights=weights[: len(scores)]))

    def _calculate_seasonal_form(self, performances: List[RacePerformance]) -> float:
        """Calculate form for current season."""
        current_year = datetime.now().year
        seasonal_performances = [p for p in performances if p.date.year == current_year]

        return self._calculate_recent_form(seasonal_performances)

    def _calculate_composite_score(self, components: Dict[str, float]) -> float:
        """Calculate weighted composite score."""
        total_weight = sum(self.weights.values())
        weighted_sum = sum(
            components.get(factor, 0.5) * weight
            for factor, weight in self.weights.items()
        )

        return weighted_sum / total_weight

    def _calculate_confidence(
        self, performances: List[RacePerformance], reliability: float
    ) -> float:
        """Calculate confidence level in the analysis."""
        # Base confidence on amount and quality of data
        data_points = len(performances)

        # Confidence increases with more data points
        data_confidence = min(1.0, data_points / 10.0)

        # Combine with reliability score
        overall_confidence = data_confidence * 0.6 + reliability * 0.4

        return overall_confidence

    # Helper methods for specific calculations
    def _estimate_speed_from_performance(
        self, performances: List[RacePerformance]
    ) -> float:
        """Estimate speed rating from performance data when speed figures unavailable."""
        # Simplified speed estimation based on class and finishing position
        if not performances:
            return 50.0

        recent_perfs = performances[-3:]
        scores = []

        for perf in recent_perfs:
            # Base speed from class
            class_speed = float(perf.race_class.value) * 15.0

            # Adjust for finishing position
            position_adjustment = -(perf.finish_position - 1) * 3.0

            # Adjust for field strength
            field_adjustment = min(5.0, max(-5.0, (perf.field_size - 8) * 0.5))

            speed_estimate = class_speed + position_adjustment + field_adjustment
            scores.append(max(0.0, min(120.0, speed_estimate)))

        return float(np.mean(scores))

    def _calculate_pace_rating(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, Union[str, float, int]],
    ) -> float:
        """Calculate pace rating and scenario suitability."""
        # Placeholder for pace analysis
        # Would analyze early/middle/late pace figures if available

        # For now, return a moderate pace rating
        return 50.0

    def _calculate_finishing_speed(self, performances: List[RacePerformance]) -> float:
        """Calculate finishing speed index."""
        # Placeholder for finishing speed analysis
        # Would analyze late pace and closing ability

        return 50.0

    def _calculate_trip_efficiency(
        self, performances: List[RacePerformance], target_distance: float
    ) -> float:
        """Calculate efficiency at handling different trip lengths."""
        if not performances:
            return 0.5

        # Analyze performance vs distance
        distance_performance = []

        for perf in performances:
            # Position quality vs distance
            pos_score = max(
                0.0, 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            )

            # Distance differential impact
            distance_diff = abs(perf.distance - target_distance)
            distance_factor = max(
                0.5, 1.0 - distance_diff / 5.0
            )  # Penalty for distance changes

            adjusted_score = pos_score * distance_factor
            distance_performance.append(adjusted_score)

        return float(np.mean(distance_performance))

    def _default_form_metrics(self) -> FormMetrics:
        """Return default metrics when no data available."""
        return FormMetrics(
            last_run_score=0.5,
            recent_form_score=0.5,
            seasonal_form_score=0.5,
            speed_rating=50.0,
            pace_rating=50.0,
            finishing_speed_index=50.0,
            consistency_index=0.5,
            reliability_score=0.5,
            class_rating=50.0,
            competition_strength=50.0,
            track_bias_adjustment=0.0,
            condition_suitability=0.5,
            distance_suitability=0.5,
            trip_efficiency=0.5,
            jockey_form=0.5,
            trainer_form=0.5,
            combo_efficiency=0.5,
            form_composite=0.5,
            power_rating=50.0,
            confidence_level=0.1,
        )
