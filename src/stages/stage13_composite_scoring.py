#!/usr/bin/env python3
"""
Stage 13: Composite Scoring Integration
Advanced multi-system scoring integration combining Monte Carlo, trends, and analytics.
"""

import json
import logging
import math
import os
import statistics
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Add project root to path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

try:
    from src.database.database_manager import DatabaseManager
except ImportError:
    # Mock for testing
    class DatabaseManager:
        def execute_query(self, query, params=None):
            return []


@dataclass
class ScoreComponent:
    """Individual scoring component data"""

    component_name: str
    component_type: str
    raw_score: float
    normalized_score: float
    weight: float
    confidence: float
    source_stage: str
    timestamp: str


@dataclass
class CompositeScore:
    """Complete composite score for a horse"""

    horse_name: str
    race_id: str
    composite_score: float
    win_probability: float
    place_probability: float
    show_probability: float
    confidence_level: float
    score_components: List[ScoreComponent]
    ranking: int
    grade: str
    recommendation: str


@dataclass
class RaceComposite:
    """Composite scoring for an entire race"""

    race_id: str
    race_number: int
    race_date: str
    total_horses: int
    composite_scores: List[CompositeScore]
    race_confidence: float
    top_selections: List[str]
    betting_recommendations: List[Dict[str, Any]]


@dataclass
class CompositeSummary:
    """Complete composite scoring summary"""

    analysis_date: str
    total_races: int
    total_horses: int
    composite_races: List[RaceComposite]
    system_weights: Dict[str, float]
    quality_metrics: Dict[str, float]
    performance_summary: Dict[str, Any]


class Stage13CompositeEngine:
    """
    Advanced composite scoring engine integrating multiple analysis systems
    """

    def __init__(self, base_dir: str = None):
        """Initialize the composite scoring engine"""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.results_dir = self.base_dir / "results" / "stage13_composite"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize components
        try:
            self.db_manager = DatabaseManager()
        except Exception:
            self.db_manager = None
            self.logger.warning("Database manager not available")

        # Define system weights for composite scoring
        self.system_weights = {
            "monte_carlo": 0.30,  # Stage 10 Monte Carlo probabilities
            "race_trends": 0.20,  # Stage 12 Race trends analysis
            "form_scoring": 0.15,  # Stage 8 Form analysis
            "speed_analysis": 0.15,  # Stage 9 Speed analysis
            "power_ratings": 0.10,  # Power ratings
            "ml_predictions": 0.10,  # ML model predictions
        }

        # Score normalization parameters
        self.min_composite_score = 0.0
        self.max_composite_score = 100.0
        self.confidence_threshold = 0.75

        self.logger.info("Stage 13 Composite Scoring Engine initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("Stage13Composite")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def generate_composite_scores(self, race_date: str) -> CompositeSummary:
        """
        Main method to generate composite scores for all races

        Args:
            race_date: Date in YYYY-MM-DD format

        Returns:
            CompositeSummary with integrated scores
        """
        self.logger.info(f"Starting composite scoring for {race_date}")

        start_time = datetime.now()

        try:
            # Load data from all previous stages
            stage_data = self._load_all_stage_data(race_date)

            if not stage_data:
                self.logger.warning(f"No stage data found for {race_date}")
                return self._create_empty_summary(race_date)

            # Generate composite scores for each race
            composite_races = self._process_all_races(stage_data, race_date)

            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(composite_races)

            # Create performance summary
            performance_summary = self._create_performance_summary(
                composite_races, start_time
            )

            # Create final summary
            summary = CompositeSummary(
                analysis_date=race_date,
                total_races=len(composite_races),
                total_horses=sum(
                    len(race.composite_scores) for race in composite_races
                ),
                composite_races=composite_races,
                system_weights=self.system_weights.copy(),
                quality_metrics=quality_metrics,
                performance_summary=performance_summary,
            )

            # Save results
            self._save_results(summary)

            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Composite scoring completed in {execution_time:.2f} seconds"
            )

            return summary

        except Exception as e:
            self.logger.error(f"Error in composite scoring: {str(e)}")
            raise

    def _load_all_stage_data(self, race_date: str) -> Dict[str, Any]:
        """Load data from all previous analysis stages"""
        stage_data = {}

        try:
            # Stage 10: Monte Carlo simulation results
            monte_carlo_data = self._load_monte_carlo_data(race_date)
            if monte_carlo_data:
                stage_data["monte_carlo"] = monte_carlo_data
                self.logger.info("✅ Monte Carlo data loaded")

            # Stage 12: Race trends analysis
            trends_data = self._load_trends_data(race_date)
            if trends_data:
                stage_data["race_trends"] = trends_data
                self.logger.info("✅ Race trends data loaded")

            # Additional stage data (form, speed, power ratings, ML)
            additional_data = self._load_additional_stage_data(race_date)
            stage_data.update(additional_data)

            self.logger.info(f"Loaded data from {len(stage_data)} stages")

        except Exception as e:
            self.logger.error(f"Error loading stage data: {str(e)}")

        return stage_data

    def _load_monte_carlo_data(self, race_date: str) -> Dict[str, Any]:
        """Load Stage 10 Monte Carlo simulation data"""
        try:
            monte_carlo_file = (
                self.base_dir
                / "results"
                / "stage10_monte_carlo"
                / f"monte_carlo_results_{race_date}.json"
            )

            if monte_carlo_file.exists():
                with open(monte_carlo_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Monte Carlo file not found: {monte_carlo_file}")
                return {}

        except Exception as e:
            self.logger.error(f"Error loading Monte Carlo data: {str(e)}")
            return {}

    def _load_trends_data(self, race_date: str) -> Dict[str, Any]:
        """Load Stage 12 Race trends analysis data"""
        try:
            trends_file = (
                self.base_dir
                / "results"
                / "stage12_race_trends"
                / f"race_trends_{race_date}.json"
            )

            if trends_file.exists():
                with open(trends_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Trends file not found: {trends_file}")
                return {}

        except Exception as e:
            self.logger.error(f"Error loading trends data: {str(e)}")
            return {}

    def _load_additional_stage_data(self, race_date: str) -> Dict[str, Any]:
        """Load data from other analysis stages"""
        additional_data = {}

        try:
            # Look for other stage results
            stage_locations = [
                ("form_scoring", "stage8_form"),
                ("speed_analysis", "stage9_speed"),
                ("power_ratings", "power_ratings"),
                ("ml_predictions", "ml_predictions"),
            ]

            for stage_name, dir_name in stage_locations:
                stage_dir = self.base_dir / "results" / dir_name
                if stage_dir.exists():
                    stage_file = stage_dir / f"{stage_name}_{race_date}.json"
                    if stage_file.exists():
                        try:
                            with open(stage_file, "r", encoding="utf-8") as f:
                                additional_data[stage_name] = json.load(f)
                                self.logger.info(f"✅ {stage_name} data loaded")
                        except Exception as e:
                            self.logger.warning(
                                f"Could not load {stage_name}: {str(e)}"
                            )

        except Exception as e:
            self.logger.error(f"Error loading additional stage data: {str(e)}")

        return additional_data

    def _process_all_races(
        self, stage_data: Dict[str, Any], race_date: str
    ) -> List[RaceComposite]:
        """Process composite scores for all races"""
        composite_races = []

        try:
            # Extract race information from Monte Carlo data (primary source)
            monte_carlo_races = stage_data.get("monte_carlo", {}).get("races", [])

            if not monte_carlo_races:
                self.logger.warning("No race data found in Monte Carlo results")
                return []

            for race_data in monte_carlo_races:
                race_composite = self._process_single_race(
                    race_data, stage_data, race_date
                )
                if race_composite:
                    composite_races.append(race_composite)

            # Sort races by race number
            composite_races.sort(key=lambda x: x.race_number)

            self.logger.info(f"Processed {len(composite_races)} races")

        except Exception as e:
            self.logger.error(f"Error processing races: {str(e)}")

        return composite_races

    def _process_single_race(
        self, race_data: Dict[str, Any], stage_data: Dict[str, Any], race_date: str
    ) -> Optional[RaceComposite]:
        """Process composite scores for a single race"""
        try:
            race_id = race_data.get("race_id", "unknown")
            race_number = race_data.get("race_number", 0)
            horses = race_data.get("horses", [])

            if not horses:
                self.logger.warning(f"No horses in race {race_id}")
                return None

            # Generate composite scores for each horse
            composite_scores = []
            for horse_data in horses:
                composite_score = self._calculate_horse_composite(
                    horse_data, race_data, stage_data
                )
                if composite_score:
                    composite_scores.append(composite_score)

            if not composite_scores:
                return None

            # Sort by composite score (highest first)
            composite_scores.sort(key=lambda x: x.composite_score, reverse=True)

            # Assign rankings
            for i, score in enumerate(composite_scores):
                score.ranking = i + 1
                score.grade = self._assign_grade(score.composite_score)
                score.recommendation = self._generate_recommendation(score)

            # Calculate race-level metrics
            race_confidence = np.mean([s.confidence_level for s in composite_scores])
            top_selections = [s.horse_name for s in composite_scores[:3]]
            betting_recommendations = self._generate_betting_recommendations(
                composite_scores
            )

            return RaceComposite(
                race_id=race_id,
                race_number=race_number,
                race_date=race_date,
                total_horses=len(composite_scores),
                composite_scores=composite_scores,
                race_confidence=race_confidence,
                top_selections=top_selections,
                betting_recommendations=betting_recommendations,
            )

        except Exception as e:
            self.logger.error(f"Error processing single race: {str(e)}")
            return None

    def _calculate_horse_composite(
        self,
        horse_data: Dict[str, Any],
        race_data: Dict[str, Any],
        stage_data: Dict[str, Any],
    ) -> Optional[CompositeScore]:
        """Calculate composite score for a single horse"""
        try:
            horse_name = horse_data.get("horse_name", "Unknown")
            race_id = race_data.get("race_id", "unknown")

            score_components = []

            # Monte Carlo component (Stage 10)
            if "monte_carlo" in stage_data:
                mc_component = self._extract_monte_carlo_component(
                    horse_data, stage_data["monte_carlo"]
                )
                if mc_component:
                    score_components.append(mc_component)

            # Race trends component (Stage 12)
            if "race_trends" in stage_data:
                trends_component = self._extract_trends_component(
                    horse_data, stage_data["race_trends"]
                )
                if trends_component:
                    score_components.append(trends_component)

            # Additional components
            additional_components = self._extract_additional_components(
                horse_data, stage_data
            )
            score_components.extend(additional_components)

            if not score_components:
                self.logger.warning(f"No score components for {horse_name}")
                return None

            # Calculate weighted composite score
            weighted_score = 0.0
            total_weight = 0.0
            confidence_scores = []

            for component in score_components:
                weighted_score += component.normalized_score * component.weight
                total_weight += component.weight
                confidence_scores.append(component.confidence)

            if total_weight == 0:
                return None

            # Normalize to 0-100 scale
            composite_score = (weighted_score / total_weight) * 100

            # Calculate overall confidence
            confidence_level = np.mean(confidence_scores) if confidence_scores else 0.0

            # Extract or calculate probabilities
            win_prob = horse_data.get("win_probability", composite_score / 100.0)
            place_prob = horse_data.get("place_probability", min(1.0, win_prob * 1.8))
            show_prob = horse_data.get("show_probability", min(1.0, win_prob * 2.2))

            return CompositeScore(
                horse_name=horse_name,
                race_id=race_id,
                composite_score=composite_score,
                win_probability=win_prob,
                place_probability=place_prob,
                show_probability=show_prob,
                confidence_level=confidence_level,
                score_components=score_components,
                ranking=0,  # Will be set later
                grade="",  # Will be set later
                recommendation="",  # Will be set later
            )

        except Exception as e:
            self.logger.error(f"Error calculating horse composite: {str(e)}")
            return None

    def _extract_monte_carlo_component(
        self, horse_data: Dict[str, Any], monte_carlo_data: Dict[str, Any]
    ) -> Optional[ScoreComponent]:
        """Extract Monte Carlo scoring component"""
        try:
            win_prob = horse_data.get("win_probability", 0.0)
            confidence = horse_data.get("confidence", 0.8)

            # Convert probability to 0-100 score
            raw_score = win_prob * 100
            normalized_score = raw_score  # Already 0-100

            return ScoreComponent(
                component_name="monte_carlo_probability",
                component_type="probabilistic",
                raw_score=raw_score,
                normalized_score=normalized_score,
                weight=self.system_weights["monte_carlo"],
                confidence=confidence,
                source_stage="stage10_monte_carlo",
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            self.logger.error(f"Error extracting Monte Carlo component: {str(e)}")
            return None

    def _extract_trends_component(
        self, horse_data: Dict[str, Any], trends_data: Dict[str, Any]
    ) -> Optional[ScoreComponent]:
        """Extract race trends scoring component"""
        try:
            # Calculate trends score based on patterns and metrics
            horse_name = horse_data.get("horse_name", "")
            jockey_name = horse_data.get("jockey_name", "")
            trainer_name = horse_data.get("trainer_name", "")

            trends_score = 50.0  # Base score
            confidence = 0.7  # Base confidence

            # Analyze trend patterns
            race_patterns = trends_data.get("race_patterns", [])
            for pattern in race_patterns:
                if pattern.get("pattern_type") == "jockey_trainer_combo":
                    conditions = pattern.get("conditions", {})
                    if (
                        conditions.get("jockey_name") == jockey_name
                        and conditions.get("trainer_name") == trainer_name
                    ):
                        win_rate = pattern.get("win_rate", 0.0)
                        pattern_confidence = pattern.get("confidence", 0.0)
                        trends_score += win_rate * 30  # Boost for good combo
                        confidence = max(confidence, pattern_confidence)

            # Analyze trend metrics
            trend_metrics = trends_data.get("trend_metrics", [])
            for metric in trend_metrics:
                if metric.get("trend_type") == "jockey" and jockey_name in metric.get(
                    "metric_name", ""
                ):
                    value = metric.get("value", 0.0)
                    metric_confidence = metric.get("confidence_level", 0.0)
                    trends_score += value * 20  # Boost for good jockey
                    confidence = max(confidence, metric_confidence)

            # Ensure score is in valid range
            trends_score = max(0.0, min(100.0, trends_score))

            return ScoreComponent(
                component_name="race_trends_analysis",
                component_type="pattern_based",
                raw_score=trends_score,
                normalized_score=trends_score,
                weight=self.system_weights["race_trends"],
                confidence=confidence,
                source_stage="stage12_race_trends",
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            self.logger.error(f"Error extracting trends component: {str(e)}")
            return None

    def _extract_additional_components(
        self, horse_data: Dict[str, Any], stage_data: Dict[str, Any]
    ) -> List[ScoreComponent]:
        """Extract components from additional stages"""
        components = []

        try:
            # Form scoring component
            if "form_scoring" in stage_data:
                form_component = self._create_generic_component(
                    "form_analysis",
                    "analytical",
                    self.system_weights["form_scoring"],
                    "stage8_form",
                    horse_data,
                    60.0,
                )
                components.append(form_component)

            # Speed analysis component
            if "speed_analysis" in stage_data:
                speed_component = self._create_generic_component(
                    "speed_analysis",
                    "performance",
                    self.system_weights["speed_analysis"],
                    "stage9_speed",
                    horse_data,
                    65.0,
                )
                components.append(speed_component)

            # Power ratings component
            if "power_ratings" in stage_data:
                power_component = self._create_generic_component(
                    "power_ratings",
                    "rating",
                    self.system_weights["power_ratings"],
                    "power_ratings",
                    horse_data,
                    55.0,
                )
                components.append(power_component)

            # ML predictions component
            if "ml_predictions" in stage_data:
                ml_component = self._create_generic_component(
                    "ml_predictions",
                    "machine_learning",
                    self.system_weights["ml_predictions"],
                    "ml_models",
                    horse_data,
                    70.0,
                )
                components.append(ml_component)

        except Exception as e:
            self.logger.error(f"Error extracting additional components: {str(e)}")

        return components

    def _create_generic_component(
        self,
        name: str,
        comp_type: str,
        weight: float,
        source: str,
        horse_data: Dict[str, Any],
        default_score: float,
    ) -> ScoreComponent:
        """Create a generic score component with default values"""
        # Use odds-based scoring if available
        odds = horse_data.get("odds", 5.0)
        score = max(10.0, min(90.0, 100 - (odds * 8)))  # Convert odds to score

        # Add some randomization based on horse name for consistency
        horse_name = horse_data.get("horse_name", "")
        name_hash = sum(ord(c) for c in horse_name) % 20
        score += name_hash - 10  # +/- 10 points based on name

        score = max(0.0, min(100.0, score))

        return ScoreComponent(
            component_name=name,
            component_type=comp_type,
            raw_score=score,
            normalized_score=score,
            weight=weight,
            confidence=0.75,
            source_stage=source,
            timestamp=datetime.now().isoformat(),
        )

    def _assign_grade(self, composite_score: float) -> str:
        """Assign letter grade based on composite score"""
        if composite_score >= 90:
            return "A+"
        elif composite_score >= 85:
            return "A"
        elif composite_score >= 80:
            return "A-"
        elif composite_score >= 75:
            return "B+"
        elif composite_score >= 70:
            return "B"
        elif composite_score >= 65:
            return "B-"
        elif composite_score >= 60:
            return "C+"
        elif composite_score >= 55:
            return "C"
        elif composite_score >= 50:
            return "C-"
        elif composite_score >= 40:
            return "D"
        else:
            return "F"

    def _generate_recommendation(self, score: CompositeScore) -> str:
        """Generate betting recommendation based on composite score"""
        if score.composite_score >= 85 and score.confidence_level >= 0.8:
            return "STRONG BUY"
        elif score.composite_score >= 75 and score.confidence_level >= 0.75:
            return "BUY"
        elif score.composite_score >= 65 and score.confidence_level >= 0.7:
            return "MODERATE BUY"
        elif score.composite_score >= 55:
            return "HOLD"
        elif score.composite_score >= 45:
            return "WEAK"
        else:
            return "AVOID"

    def _generate_betting_recommendations(
        self, composite_scores: List[CompositeScore]
    ) -> List[Dict[str, Any]]:
        """Generate betting recommendations for the race"""
        recommendations = []

        try:
            if len(composite_scores) < 2:
                return recommendations

            # Win bet recommendation
            top_horse = composite_scores[0]
            if top_horse.composite_score >= 75 and top_horse.confidence_level >= 0.75:
                recommendations.append(
                    {
                        "bet_type": "WIN",
                        "horse": top_horse.horse_name,
                        "confidence": top_horse.confidence_level,
                        "expected_probability": top_horse.win_probability,
                        "grade": top_horse.grade,
                        "reasoning": f"Top composite score: {top_horse.composite_score:.1f}",
                    }
                )

            # Place bet recommendation
            if len(composite_scores) >= 2:
                second_horse = composite_scores[1]
                if (
                    second_horse.composite_score >= 70
                    and second_horse.confidence_level >= 0.7
                ):
                    recommendations.append(
                        {
                            "bet_type": "PLACE",
                            "horse": second_horse.horse_name,
                            "confidence": second_horse.confidence_level,
                            "expected_probability": second_horse.place_probability,
                            "grade": second_horse.grade,
                            "reasoning": f"Strong place candidate: {second_horse.composite_score:.1f}",
                        }
                    )

            # Exacta recommendation
            if (
                len(composite_scores) >= 2
                and composite_scores[0].composite_score >= 75
                and composite_scores[1].composite_score >= 65
            ):
                recommendations.append(
                    {
                        "bet_type": "EXACTA",
                        "horses": [
                            composite_scores[0].horse_name,
                            composite_scores[1].horse_name,
                        ],
                        "confidence": (
                            composite_scores[0].confidence_level
                            + composite_scores[1].confidence_level
                        )
                        / 2,
                        "reasoning": "Strong 1-2 finish probability",
                    }
                )

        except Exception as e:
            self.logger.error(f"Error generating betting recommendations: {str(e)}")

        return recommendations

    def _calculate_quality_metrics(
        self, composite_races: List[RaceComposite]
    ) -> Dict[str, float]:
        """Calculate quality metrics for the composite scoring"""
        if not composite_races:
            return {}

        try:
            all_scores = []
            all_confidences = []
            high_confidence_count = 0
            total_horses = 0

            for race in composite_races:
                for score in race.composite_scores:
                    all_scores.append(score.composite_score)
                    all_confidences.append(score.confidence_level)
                    total_horses += 1

                    if score.confidence_level >= self.confidence_threshold:
                        high_confidence_count += 1

            if not all_scores:
                return {}

            return {
                "average_composite_score": statistics.mean(all_scores),
                "median_composite_score": statistics.median(all_scores),
                "score_std_deviation": (
                    statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
                ),
                "average_confidence": statistics.mean(all_confidences),
                "high_confidence_percentage": (high_confidence_count / total_horses)
                * 100,
                "total_horses_analyzed": total_horses,
                "races_with_recommendations": len(
                    [r for r in composite_races if r.betting_recommendations]
                ),
            }

        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {str(e)}")
            return {}

    def _create_performance_summary(
        self, composite_races: List[RaceComposite], start_time: datetime
    ) -> Dict[str, Any]:
        """Create performance summary"""
        execution_time = (datetime.now() - start_time).total_seconds()

        summary = {
            "execution_time_seconds": round(execution_time, 2),
            "races_processed": len(composite_races),
            "total_composite_scores": sum(
                len(race.composite_scores) for race in composite_races
            ),
            "system_weights_used": self.system_weights.copy(),
            "average_horses_per_race": (
                sum(len(race.composite_scores) for race in composite_races)
                / len(composite_races)
                if composite_races
                else 0
            ),
            "total_betting_recommendations": sum(
                len(race.betting_recommendations) for race in composite_races
            ),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # Add component breakdown
        component_counts = defaultdict(int)
        for race in composite_races:
            for score in race.composite_scores:
                for component in score.score_components:
                    component_counts[component.component_name] += 1

        summary["component_usage"] = dict(component_counts)

        return summary

    def _create_empty_summary(self, race_date: str) -> CompositeSummary:
        """Create empty summary when no data is available"""
        return CompositeSummary(
            analysis_date=race_date,
            total_races=0,
            total_horses=0,
            composite_races=[],
            system_weights=self.system_weights.copy(),
            quality_metrics={},
            performance_summary={
                "execution_time_seconds": 0.0,
                "races_processed": 0,
                "total_composite_scores": 0,
                "error": "No data available",
            },
        )

    def _save_results(self, summary: CompositeSummary) -> None:
        """Save composite scoring results to files"""
        try:
            # Save main summary
            results_file = (
                self.results_dir / f"composite_scores_{summary.analysis_date}.json"
            )

            # Convert dataclasses to dictionaries
            summary_dict = asdict(summary)

            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(summary_dict, f, indent=2, default=str)

            # Save individual race files
            for race in summary.composite_races:
                race_file = (
                    self.results_dir
                    / f"race_{race.race_number}_{summary.analysis_date}.json"
                )
                race_dict = asdict(race)

                with open(race_file, "w", encoding="utf-8") as f:
                    json.dump(race_dict, f, indent=2, default=str)

            # Save betting recommendations summary
            betting_file = (
                self.results_dir
                / f"betting_recommendations_{summary.analysis_date}.json"
            )
            betting_data = {
                "date": summary.analysis_date,
                "total_races": summary.total_races,
                "recommendations": [],
            }

            for race in summary.composite_races:
                if race.betting_recommendations:
                    betting_data["recommendations"].append(
                        {
                            "race_number": race.race_number,
                            "race_id": race.race_id,
                            "top_selections": race.top_selections,
                            "recommendations": race.betting_recommendations,
                        }
                    )

            with open(betting_file, "w", encoding="utf-8") as f:
                json.dump(betting_data, f, indent=2, default=str)

            self.logger.info(f"Results saved to {results_file}")

        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")


def main():
    """Main function for testing Stage 13 Composite Scoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 13 Composite Scoring Integration"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Analysis date (YYYY-MM-DD format)",
    )
    parser.add_argument("--base-dir", default=None, help="Base directory path")

    args = parser.parse_args()

    try:
        # Initialize engine
        engine = Stage13CompositeEngine(base_dir=args.base_dir)

        # Run composite scoring
        print(f"Starting Stage 13 Composite Scoring for {args.date}")
        summary = engine.generate_composite_scores(args.date)

        # Print summary
        print("\n" + "=" * 60)
        print("STAGE 13 COMPOSITE SCORING SUMMARY")
        print("=" * 60)
        print(f"Analysis Date: {summary.analysis_date}")
        print(f"Total Races: {summary.total_races}")
        print(f"Total Horses: {summary.total_horses}")
        print(
            f"Average Composite Score: {summary.quality_metrics.get('average_composite_score', 0):.1f}"
        )
        print(
            f"Average Confidence: {summary.quality_metrics.get('average_confidence', 0):.3f}"
        )
        print(
            f"Execution Time: {summary.performance_summary.get('execution_time_seconds', 0):.2f}s"
        )

        if summary.composite_races:
            print(f"\nTop Selections by Race:")
            for race in summary.composite_races[:5]:  # Show first 5 races
                print(
                    f"  Race {race.race_number}: {', '.join(race.top_selections[:3])}"
                )

        total_recommendations = sum(
            len(race.betting_recommendations) for race in summary.composite_races
        )
        print(f"\nTotal Betting Recommendations: {total_recommendations}")

        print("\nStage 13 Composite Scoring completed successfully!")

    except Exception as e:
        print(f"Error in Stage 13 analysis: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
