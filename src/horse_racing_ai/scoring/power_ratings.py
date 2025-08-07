"""
Power Ratings System for Horse Racing
====================================

Advanced power rating calculations incorporating multiple performance factors
and dynamic adjustments for improved accuracy.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import structlog

from .form_analyzer import EnhancedFormAnalyzer, FormMetrics, RacePerformance

logger = structlog.get_logger(__name__)


@dataclass
class PowerRating:
    """Power rating result for a horse."""

    horse_name: str
    base_rating: float  # Core power rating (0-150)
    adjusted_rating: float  # Rating after adjustments
    speed_component: float
    class_component: float
    form_component: float
    consistency_component: float
    conditions_adjustment: float
    confidence_level: float
    factors_breakdown: Dict[str, float]


class RatingAdjustmentType(Enum):
    """Types of rating adjustments."""

    TRACK_BIAS = "track_bias"
    DISTANCE_SPECIALIZATION = "distance_specialization"
    SURFACE_SUITABILITY = "surface_suitability"
    JOCKEY_TRAINER = "jockey_trainer"
    EQUIPMENT_CHANGE = "equipment_change"
    LAY_OFF = "lay_off"
    CLASS_MOVEMENT = "class_movement"
    WEIGHT_ALLOWANCE = "weight_allowance"


@dataclass
class RatingAdjustment:
    """Individual rating adjustment."""

    adjustment_type: RatingAdjustmentType
    value: float  # Positive or negative adjustment
    reason: str
    confidence: float


class PowerRatingSystem:
    """
    Advanced power rating system with dynamic adjustments.

    Features:
    - Multi-component base rating calculation
    - Dynamic condition-specific adjustments
    - Track bias and surface specialization
    - Pace scenario analysis
    - Equipment and jockey change impacts
    - Class movement adjustments
    - Confidence-weighted final ratings
    """

    def __init__(self):
        """Initialize the power rating system."""
        self.form_analyzer = EnhancedFormAnalyzer()
        self._initialize_rating_weights()
        self._initialize_adjustment_factors()

    def _initialize_rating_weights(self) -> None:
        """Initialize component weights for base rating calculation."""
        self.rating_weights = {
            "speed_component": 0.35,
            "class_component": 0.25,
            "form_component": 0.20,
            "consistency_component": 0.20,
        }

    def _initialize_adjustment_factors(self) -> None:
        """Initialize adjustment factor ranges."""
        self.adjustment_ranges = {
            RatingAdjustmentType.TRACK_BIAS: (-8.0, 8.0),
            RatingAdjustmentType.DISTANCE_SPECIALIZATION: (-6.0, 6.0),
            RatingAdjustmentType.SURFACE_SUITABILITY: (-5.0, 5.0),
            RatingAdjustmentType.JOCKEY_TRAINER: (-4.0, 4.0),
            RatingAdjustmentType.EQUIPMENT_CHANGE: (-3.0, 3.0),
            RatingAdjustmentType.LAY_OFF: (-5.0, 0.0),
            RatingAdjustmentType.CLASS_MOVEMENT: (-8.0, 8.0),
            RatingAdjustmentType.WEIGHT_ALLOWANCE: (-3.0, 3.0),
        }

    def calculate_power_rating(
        self,
        horse_name: str,
        performances: List[RacePerformance],
        target_race_conditions: Dict[str, any],
        additional_factors: Optional[Dict[str, any]] = None,
    ) -> PowerRating:
        """
        Calculate comprehensive power rating for a horse.

        Args:
            horse_name: Name of the horse
            performances: Historical race performances
            target_race_conditions: Conditions of upcoming race
            additional_factors: Equipment changes, layoffs, etc.

        Returns:
            Complete power rating with breakdown
        """
        logger.info(f"Calculating power rating for {horse_name}")

        if not performances:
            return self._default_power_rating(horse_name)

        # Get form analysis
        form_metrics = self.form_analyzer.analyze_horse_form(
            horse_name, performances, target_race_conditions
        )

        # Calculate base rating components
        speed_component = self._calculate_speed_component(form_metrics, performances)
        class_component = self._calculate_class_component(
            form_metrics, target_race_conditions
        )
        form_component = self._calculate_form_component(form_metrics)
        consistency_component = self._calculate_consistency_component(form_metrics)

        # Calculate base rating
        base_rating = (
            speed_component * self.rating_weights["speed_component"]
            + class_component * self.rating_weights["class_component"]
            + form_component * self.rating_weights["form_component"]
            + consistency_component * self.rating_weights["consistency_component"]
        )

        # Calculate adjustments
        adjustments = self._calculate_adjustments(
            performances, target_race_conditions, additional_factors or {}
        )

        # Apply adjustments to base rating
        total_adjustment = sum(adj.value for adj in adjustments)
        adjusted_rating = max(0.0, min(150.0, base_rating + total_adjustment))

        # Calculate conditions-specific adjustment summary
        conditions_adjustment = total_adjustment

        # Create factors breakdown
        factors_breakdown = {
            "speed": speed_component,
            "class": class_component,
            "form": form_component,
            "consistency": consistency_component,
            "adjustments": total_adjustment,
        }

        # Add individual adjustment details
        for adj in adjustments:
            factors_breakdown[f"adj_{adj.adjustment_type.value}"] = adj.value

        return PowerRating(
            horse_name=horse_name,
            base_rating=base_rating,
            adjusted_rating=adjusted_rating,
            speed_component=speed_component,
            class_component=class_component,
            form_component=form_component,
            consistency_component=consistency_component,
            conditions_adjustment=conditions_adjustment,
            confidence_level=form_metrics.confidence_level,
            factors_breakdown=factors_breakdown,
        )

    def _calculate_speed_component(
        self, form_metrics: FormMetrics, performances: List[RacePerformance]
    ) -> float:
        """Calculate speed component of rating (0-150 scale)."""

        # Base speed rating from form analysis
        base_speed = form_metrics.speed_rating

        # Pace rating contribution
        pace_contribution = form_metrics.pace_rating * 0.3

        # Finishing speed contribution
        finishing_contribution = form_metrics.finishing_speed_index * 0.2

        # Recent speed trend
        speed_trend = self._calculate_speed_trend(performances)

        # Combine components
        speed_component = (
            base_speed * 0.6
            + pace_contribution
            + finishing_contribution
            + speed_trend * 10.0
        )

        return max(0.0, min(150.0, speed_component))

    def _calculate_class_component(
        self, form_metrics: FormMetrics, target_conditions: Dict[str, any]
    ) -> float:
        """Calculate class component of rating."""

        # Base class rating
        base_class = form_metrics.class_rating

        # Competition strength factor
        competition_factor = form_metrics.competition_strength * 0.3

        # Class trend (improvement/decline)
        class_trend = self._estimate_class_trend(form_metrics)

        class_component = base_class + competition_factor + class_trend

        return max(0.0, min(150.0, class_component))

    def _calculate_form_component(self, form_metrics: FormMetrics) -> float:
        """Calculate form component of rating."""

        # Weight different form timeframes
        form_component = (
            form_metrics.recent_form_score * 50.0 * 0.4  # Last 3 runs
            + form_metrics.seasonal_form_score * 50.0 * 0.35  # Season form
            + form_metrics.last_run_score * 50.0 * 0.25  # Last run
        )

        return max(0.0, min(150.0, form_component))

    def _calculate_consistency_component(self, form_metrics: FormMetrics) -> float:
        """Calculate consistency component of rating."""

        consistency_component = (
            form_metrics.consistency_index * 75.0
            + form_metrics.reliability_score * 75.0
        )

        return max(0.0, min(150.0, consistency_component))

    def _calculate_adjustments(
        self,
        performances: List[RacePerformance],
        target_conditions: Dict[str, any],
        additional_factors: Dict[str, any],
    ) -> List[RatingAdjustment]:
        """Calculate all rating adjustments."""

        adjustments = []

        # Track bias adjustment
        track_bias = self._calculate_track_bias_adjustment(
            performances, target_conditions
        )
        if abs(track_bias) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.TRACK_BIAS,
                    track_bias,
                    f"Track bias adjustment: {track_bias:+.1f}",
                    0.7,
                )
            )

        # Distance specialization
        distance_adj = self._calculate_distance_adjustment(
            performances, target_conditions
        )
        if abs(distance_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.DISTANCE_SPECIALIZATION,
                    distance_adj,
                    f"Distance specialization: {distance_adj:+.1f}",
                    0.8,
                )
            )

        # Surface suitability
        surface_adj = self._calculate_surface_adjustment(
            performances, target_conditions
        )
        if abs(surface_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.SURFACE_SUITABILITY,
                    surface_adj,
                    f"Surface suitability: {surface_adj:+.1f}",
                    0.8,
                )
            )

        # Jockey/Trainer changes
        jt_adj = self._calculate_jockey_trainer_adjustment(
            performances, additional_factors
        )
        if abs(jt_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.JOCKEY_TRAINER,
                    jt_adj,
                    f"Jockey/Trainer factor: {jt_adj:+.1f}",
                    0.6,
                )
            )

        # Equipment changes
        equipment_adj = self._calculate_equipment_adjustment(additional_factors)
        if abs(equipment_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.EQUIPMENT_CHANGE,
                    equipment_adj,
                    f"Equipment change: {equipment_adj:+.1f}",
                    0.5,
                )
            )

        # Layoff adjustment
        layoff_adj = self._calculate_layoff_adjustment(performances)
        if abs(layoff_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.LAY_OFF,
                    layoff_adj,
                    f"Layoff impact: {layoff_adj:+.1f}",
                    0.7,
                )
            )

        # Class movement
        class_adj = self._calculate_class_movement_adjustment(
            performances, target_conditions
        )
        if abs(class_adj) > 0.5:
            adjustments.append(
                RatingAdjustment(
                    RatingAdjustmentType.CLASS_MOVEMENT,
                    class_adj,
                    f"Class movement: {class_adj:+.1f}",
                    0.8,
                )
            )

        return adjustments

    def _calculate_speed_trend(self, performances: List[RacePerformance]) -> float:
        """Calculate recent speed trend (-1.0 to 1.0)."""
        if len(performances) < 3:
            return 0.0

        # Use speed figures if available, otherwise estimate from performance
        recent_perfs = sorted(performances, key=lambda x: x.date, reverse=True)[:5]

        speed_values = []
        for perf in recent_perfs:
            if perf.speed_figure:
                speed_values.append(perf.speed_figure)
            else:
                # Estimate speed from position and class
                estimated_speed = (
                    perf.race_class.value * 15
                    - (perf.finish_position - 1) * 2
                    + (8 - perf.field_size) * 0.5
                )
                speed_values.append(max(0, min(120, estimated_speed)))

        if len(speed_values) < 3:
            return 0.0

        # Calculate trend using linear regression slope
        x = np.arange(len(speed_values))
        y = np.array(speed_values)

        if np.std(y) == 0:
            return 0.0

        correlation = np.corrcoef(x, y)[0, 1]

        # Convert correlation to trend score
        return float(correlation) if not np.isnan(correlation) else 0.0

    def _estimate_class_trend(self, form_metrics: FormMetrics) -> float:
        """Estimate class trend from form metrics."""
        # Simplified class trend estimation
        if form_metrics.recent_form_score > form_metrics.seasonal_form_score:
            return 5.0  # Improving
        elif form_metrics.recent_form_score < form_metrics.seasonal_form_score * 0.8:
            return -5.0  # Declining
        else:
            return 0.0  # Stable

    def _calculate_track_bias_adjustment(
        self, performances: List[RacePerformance], target_conditions: Dict[str, any]
    ) -> float:
        """Calculate track bias adjustment."""
        # Placeholder for track bias analysis
        # Would need historical track bias data
        return 0.0

    def _calculate_distance_adjustment(
        self, performances: List[RacePerformance], target_conditions: Dict[str, any]
    ) -> float:
        """Calculate distance specialization adjustment."""
        target_distance = float(target_conditions.get("distance", 8.0))

        # Find performances at similar distances
        similar_distance_perfs = [
            p for p in performances if abs(p.distance - target_distance) <= 1.0
        ]

        if not similar_distance_perfs:
            return -2.0  # Penalty for no experience at distance

        # Calculate average performance at this distance
        distance_performance = []
        for perf in similar_distance_perfs:
            pos_score = 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            distance_performance.append(pos_score)

        avg_distance_performance = float(np.mean(distance_performance))

        # Calculate overall average performance
        overall_performance = []
        for perf in performances:
            pos_score = 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            overall_performance.append(pos_score)

        avg_overall_performance = float(np.mean(overall_performance))

        # Distance specialization bonus/penalty
        specialization_diff = avg_distance_performance - avg_overall_performance

        return min(6.0, max(-6.0, specialization_diff * 12.0))

    def _calculate_surface_adjustment(
        self, performances: List[RacePerformance], target_conditions: Dict[str, any]
    ) -> float:
        """Calculate surface suitability adjustment."""
        target_surface = str(target_conditions.get("surface", "dirt"))

        # Find performances on target surface
        surface_perfs = [p for p in performances if p.surface.value == target_surface]

        if not surface_perfs:
            return -2.0  # Penalty for no experience on surface

        # Similar logic to distance adjustment
        surface_performance = []
        for perf in surface_perfs:
            pos_score = 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            surface_performance.append(pos_score)

        avg_surface_performance = float(np.mean(surface_performance))

        overall_performance = []
        for perf in performances:
            pos_score = 1.0 - (perf.finish_position - 1) / max(1, perf.field_size - 1)
            overall_performance.append(pos_score)

        avg_overall_performance = float(np.mean(overall_performance))

        specialization_diff = avg_surface_performance - avg_overall_performance

        return min(5.0, max(-5.0, specialization_diff * 10.0))

    def _calculate_jockey_trainer_adjustment(
        self, performances: List[RacePerformance], additional_factors: Dict[str, any]
    ) -> float:
        """Calculate jockey/trainer change adjustment."""
        # Check for jockey/trainer changes
        jockey_change = additional_factors.get("jockey_change", False)
        trainer_change = additional_factors.get("trainer_change", False)

        adjustment = 0.0

        if jockey_change:
            # Analyze new jockey's record with horse or stable
            new_jockey_rating = additional_factors.get("new_jockey_rating", 0.5)
            adjustment += (new_jockey_rating - 0.5) * 4.0

        if trainer_change:
            # Analyze new trainer's record
            new_trainer_rating = additional_factors.get("new_trainer_rating", 0.5)
            adjustment += (new_trainer_rating - 0.5) * 3.0

        return min(4.0, max(-4.0, adjustment))

    def _calculate_equipment_adjustment(
        self, additional_factors: Dict[str, any]
    ) -> float:
        """Calculate equipment change adjustment."""
        equipment_changes = additional_factors.get("equipment_changes", [])

        adjustment = 0.0

        for change in equipment_changes:
            if change == "blinkers_on":
                adjustment += 2.0
            elif change == "blinkers_off":
                adjustment -= 1.0
            elif change == "tongue_tie":
                adjustment += 1.0
            elif change == "nose_band":
                adjustment += 0.5

        return min(3.0, max(-3.0, adjustment))

    def _calculate_layoff_adjustment(
        self, performances: List[RacePerformance]
    ) -> float:
        """Calculate layoff adjustment."""
        if not performances:
            return -3.0

        # Find days since last run
        last_run = max(performances, key=lambda x: x.date)
        days_since_last = (datetime.now() - last_run.date).days

        if days_since_last <= 30:
            return 0.0  # No adjustment for recent runs
        elif days_since_last <= 60:
            return -1.0  # Minor penalty
        elif days_since_last <= 120:
            return -2.5  # Moderate penalty
        else:
            return -4.0  # Significant penalty for long layoff

    def _calculate_class_movement_adjustment(
        self, performances: List[RacePerformance], target_conditions: Dict[str, any]
    ) -> float:
        """Calculate class movement adjustment."""
        if not performances:
            return 0.0

        target_class = target_conditions.get("race_class", 3)  # Default allowance

        # Find recent class level
        recent_perfs = sorted(performances, key=lambda x: x.date, reverse=True)[:3]
        recent_class = float(np.mean([p.race_class.value for p in recent_perfs]))

        # Class differential
        class_diff = float(target_class) - recent_class

        # Adjustment based on class movement
        if class_diff > 0:  # Stepping up in class
            return min(-1.0, class_diff * -2.0)
        elif class_diff < 0:  # Dropping in class
            return min(6.0, abs(class_diff) * 3.0)
        else:
            return 0.0

    def compare_horses(self, ratings: List[PowerRating]) -> List[PowerRating]:
        """Compare and rank horses by power rating."""
        return sorted(ratings, key=lambda x: x.adjusted_rating, reverse=True)

    def _default_power_rating(self, horse_name: str) -> PowerRating:
        """Return default power rating when no data available."""
        return PowerRating(
            horse_name=horse_name,
            base_rating=50.0,
            adjusted_rating=50.0,
            speed_component=50.0,
            class_component=50.0,
            form_component=50.0,
            consistency_component=50.0,
            conditions_adjustment=0.0,
            confidence_level=0.1,
            factors_breakdown={
                "speed": 50.0,
                "class": 50.0,
                "form": 50.0,
                "consistency": 50.0,
                "adjustments": 0.0,
            },
        )
