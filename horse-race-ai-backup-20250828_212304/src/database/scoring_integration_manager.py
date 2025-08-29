#!/usr/bin/env python3
"""
Horse Racing Scoring Integration Manager

Integrates the existing scoring systems (FormAnalyzer, PowerRatingSystem,
CompositeScorer) with the database for persistent storage and analysis.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import json

from .scoring_database_manager import ScoringDatabaseManager
from horse_racing_ai.scoring.form_analyzer import (
    FormMetrics,
    EnhancedFormAnalyzer,
    RacePerformance,
)
from horse_racing_ai.scoring.power_ratings import PowerRating, PowerRatingSystem
from horse_racing_ai.scoring.composite_scorer import CompositeScore, CompositeScorer

logger = logging.getLogger(__name__)


class ScoringIntegrationManager:
    """Manages integration between scoring systems and database storage"""

    def __init__(self, database_url: str = None):
        """Initialize with scoring systems and database manager"""
        self.scoring_db = ScoringDatabaseManager(database_url)
        self.form_analyzer = EnhancedFormAnalyzer()
        self.power_rating_system = PowerRatingSystem()
        self.composite_scorer = CompositeScorer()

    async def analyze_and_store_horse(
        self,
        horse_data: Dict[str, Any],
        race_data: Dict[str, Any],
        target_conditions: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Perform complete analysis on a horse and store results in database

        Args:
            horse_data: Horse information and form history
            race_data: Current race information
            target_conditions: Target race conditions for analysis

        Returns:
            Dict containing all analysis results and database status
        """
        horse_name = horse_data.get("name", "Unknown")
        race_id = race_data.get("race_id", "Unknown")

        logger.info(
            f"🏇 Starting complete analysis for {horse_name} " f"in race {race_id}"
        )

        results = {
            "horse_name": horse_name,
            "race_id": race_id,
            "analysis_timestamp": datetime.now(),
            "success": False,
            "errors": [],
        }

        try:
            # 1. Form Analysis
            logger.info(f"📊 Analyzing form for {horse_name}")
            # Analyze form
            form_metrics = await self._analyze_form(
                horse_data, race_data, horse_data.get("performances", [])
            )
            if form_metrics:
                # Store form analysis
                form_saved = self.scoring_db.save_form_analysis(
                    horse_name, race_id, form_metrics.__dict__, target_conditions
                )
                results["form_analysis"] = {
                    "metrics": form_metrics.__dict__,
                    "saved_to_db": form_saved,
                }
                logger.info(f"✅ Form analysis completed for {horse_name}")
            else:
                results["errors"].append("Form analysis failed")

            # 2. Power Rating
            logger.info(f"⚡ Calculating power rating for {horse_name}")
            # Calculate power rating
            power_rating = await self._calculate_power_rating(
                horse_data, race_data, target_conditions
            )
            if power_rating:
                # Store power rating
                power_saved = self.scoring_db.save_power_rating(
                    horse_name, race_id, power_rating.__dict__, target_conditions
                )
                results["power_rating"] = {
                    "rating": power_rating.__dict__,
                    "saved_to_db": power_saved,
                }
                logger.info(f"✅ Power rating completed for {horse_name}")
            else:
                results["errors"].append("Power rating calculation failed")

            # 3. Speed/Pace Analysis
            logger.info(f"🏃 Analyzing speed/pace for {horse_name}")
            speed_pace_data = await self._analyze_speed_pace(horse_data, race_data)
            if speed_pace_data:
                # Store speed/pace analysis
                speed_saved = self.scoring_db.save_speed_pace_analysis(
                    horse_name, race_id, speed_pace_data
                )
                results["speed_pace_analysis"] = {
                    "data": speed_pace_data,
                    "saved_to_db": speed_saved,
                }
                logger.info(f"✅ Speed/pace analysis completed for {horse_name}")
            else:
                results["errors"].append("Speed/pace analysis failed")

            # 4. Composite Scoring (combines form and power rating)
            if form_metrics and power_rating:
                logger.info(f"🎯 Calculating composite score for {horse_name}")
                composite_score = await self._calculate_composite_score(
                    horse_data, form_metrics, power_rating, race_data
                )
                if composite_score:
                    # Store composite score
                    composite_saved = self.scoring_db.save_composite_score(
                        horse_name, race_id, composite_score.__dict__
                    )
                    results["composite_score"] = {
                        "score": composite_score.__dict__,
                        "saved_to_db": composite_saved,
                    }
                    logger.info(f"✅ Composite scoring completed for {horse_name}")
                else:
                    results["errors"].append("Composite scoring failed")
            else:
                results["errors"].append(
                    "Cannot calculate composite score without form and power rating"
                )

            # Mark as successful if no errors
            results["success"] = len(results["errors"]) == 0

            if results["success"]:
                logger.info(f"🎉 Complete analysis successful for {horse_name}")
            else:
                logger.warning(
                    f"⚠️ Analysis completed with errors for {horse_name}: "
                    f"{results['errors']}"
                )

        except Exception as e:
            logger.error(f"❌ Analysis failed for {horse_name}: {e}")
            results["errors"].append(f"Critical error: {str(e)}")

        return results

    async def analyze_and_store_race(
        self, race_data: Dict[str, Any], horses_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze all horses in a race and store race-level analysis

        Args:
            race_data: Race information
            horses_data: List of horse data for the race

        Returns:
            Dict containing race analysis results and individual horse results
        """
        race_id = race_data.get("race_id", "Unknown")
        logger.info(
            f"🏁 Starting race analysis for race {race_id} "
            f"with {len(horses_data)} horses"
        )

        results = {
            "race_id": race_id,
            "analysis_timestamp": datetime.now(),
            "horses_analyzed": 0,
            "horses_results": [],
            "race_analysis": None,
            "success": False,
            "errors": [],
        }

        try:
            # Analyze each horse in the race
            target_conditions = self._extract_race_conditions(race_data)

            for horse_data in horses_data:
                horse_result = await self.analyze_and_store_horse(
                    horse_data, race_data, target_conditions
                )
                results["horses_results"].append(horse_result)
                if horse_result["success"]:
                    results["horses_analyzed"] += 1
                else:
                    results["errors"].extend(horse_result["errors"])

            # Perform race-level analysis
            logger.info(f"🏁 Performing race-level analysis for {race_id}")
            race_analysis = await self._analyze_race(race_data, horses_data)
            if race_analysis:
                # Store race analysis
                race_saved = self.scoring_db.save_race_analysis(race_id, race_analysis)
                results["race_analysis"] = {
                    "analysis": race_analysis,
                    "saved_to_db": race_saved,
                }
                logger.info(f"✅ Race analysis completed for {race_id}")
            else:
                results["errors"].append("Race analysis failed")

            # Calculate final rankings and probabilities
            await self._calculate_race_rankings(race_id)

            results["success"] = results["horses_analyzed"] > 0

            logger.info(
                f"🎉 Race analysis completed for {race_id}: "
                f"{results['horses_analyzed']}/{len(horses_data)} horses analyzed"
            )

        except Exception as e:
            logger.error(f"❌ Race analysis failed for {race_id}: {e}")
            results["errors"].append(f"Critical error: {str(e)}")

        return results

    # =================== PRIVATE HELPER METHODS ===================

    async def _analyze_form(
        self,
        horse_data: Dict[str, Any],
        race_data: Dict[str, Any],
        performances: List[RacePerformance],
    ) -> Optional[FormMetrics]:
        """Analyze horse form using EnhancedFormAnalyzer"""
        try:
            # Use the enhanced form analyzer
            form_metrics = self.form_analyzer.analyze_horse_form(
                horse_name=horse_data["horse_name"],
                performances=performances,
                target_race_conditions=self._extract_race_conditions(race_data),
            )

            return form_metrics

        except Exception as e:
            logger.error(f"Form analysis error: {e}")
            return None

    async def _calculate_power_rating(
        self,
        horse_data: Dict[str, Any],
        race_data: Dict[str, Any],
        target_conditions: Dict[str, Any] = None,
    ) -> Optional[PowerRating]:
        """Calculate power rating using PowerRatingSystem"""
        try:
            # Use the power rating system
            power_rating = self.power_rating_system.calculate_power_rating(
                horse_name=horse_data["horse_name"],
                performances=horse_data.get("performances", []),
                target_race_conditions=(
                    target_conditions or self._extract_race_conditions(race_data)
                ),
                additional_factors=horse_data.get("additional_factors", {}),
            )

            return power_rating

        except Exception as e:
            logger.error(f"Power rating calculation error: {e}")
            return None

    async def _analyze_speed_pace(
        self, horse_data: Dict[str, Any], race_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze speed and pace characteristics"""
        try:
            # Extract speed and pace data
            speed_figures = horse_data.get("speed_figures", [])
            pace_data = horse_data.get("pace_data", [])
            sectional_times = horse_data.get("sectional_times", [])

            # Calculate speed/pace metrics
            speed_pace_analysis = {
                "base_speed_rating": self._calculate_base_speed_rating(speed_figures),
                "adjusted_speed_rating": self._calculate_adjusted_speed_rating(
                    speed_figures, race_data
                ),
                "speed_figure": max(speed_figures) if speed_figures else 0,
                "early_pace_rating": self._calculate_early_pace_rating(pace_data),
                "middle_pace_rating": self._calculate_middle_pace_rating(pace_data),
                "late_pace_rating": self._calculate_late_pace_rating(pace_data),
                "finishing_kick_rating": self._calculate_finishing_kick(pace_data),
                "pace_scenario": self._determine_pace_scenario(pace_data),
                "pace_suitability_score": self._calculate_pace_suitability(
                    pace_data, race_data
                ),
                "speed_trend_direction": self._analyze_speed_trend(speed_figures),
                "speed_trend_score": self._calculate_speed_trend_score(speed_figures),
                "speed_consistency": self._calculate_speed_consistency(speed_figures),
                "distance_speed_rating": self._calculate_distance_speed_rating(
                    speed_figures, race_data
                ),
                "surface_speed_rating": self._calculate_surface_speed_rating(
                    speed_figures, race_data
                ),
                "class_par_speed": self._calculate_class_par_speed(race_data),
                "speed_vs_class": self._calculate_speed_vs_class(
                    speed_figures, race_data
                ),
                "trip_rating": self._calculate_trip_rating(horse_data),
                "trouble_encountered": horse_data.get("trouble_in_running", False),
                "wide_trip": horse_data.get("wide_trip", False),
                "traffic_issues": horse_data.get("traffic_issues", False),
                "track_variant": race_data.get("track_variant", 0),
                "track_condition": race_data.get("track_condition", "Good"),
                "wind_factor": race_data.get("wind_factor", 0),
                "sectional_times": sectional_times,
                "fractional_times": horse_data.get("fractional_times", {}),
                "analysis_confidence": self._calculate_analysis_confidence(horse_data),
                "data_quality_score": self._calculate_data_quality_score(horse_data),
            }

            return speed_pace_analysis

        except Exception as e:
            logger.error(f"Speed/pace analysis error: {e}")
            return None

    async def _calculate_composite_score(
        self,
        horse_data: Dict[str, Any],
        form_metrics: FormMetrics,
        power_rating: PowerRating,
        race_data: Dict[str, Any],
    ) -> Optional[CompositeScore]:
        """Calculate composite score using CompositeScorer"""
        try:
            # Use the composite scorer
            composite_score = self.composite_scorer.score_horse(
                horse_name=horse_data["horse_name"],
                performances=horse_data.get("performances", []),
                race_conditions=race_data,
                betting_odds=horse_data.get("current_odds", 5.0),
            )

            return composite_score

        except Exception as e:
            logger.error(f"Composite scoring error: {e}")
            return None

    async def _analyze_race(
        self, race_data: Dict[str, Any], horses_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Perform race-level analysis"""
        try:
            race_analysis = {
                "race_conditions": race_data,
                "field_size": len(horses_data),
                "race_type": race_data.get("race_type", "Unknown"),
                "distance": race_data.get("distance", 0),
                "surface": race_data.get("surface", "Turf"),
                "track_condition": race_data.get("track_condition", "Good"),
                "predicted_pace_scenario": self._predict_pace_scenario(horses_data),
                "pace_competitiveness": self._analyze_pace_competitiveness(horses_data),
                "early_speed_horses": self._count_early_speed_horses(horses_data),
                "closers_count": self._count_closers(horses_data),
                "track_bias": race_data.get("track_bias", "None"),
                "bias_strength": race_data.get("bias_strength", 0),
                "weather_impact": race_data.get("weather_impact", "None"),
                "field_strength_rating": self._calculate_field_strength(horses_data),
                "class_homogeneity": self._calculate_class_homogeneity(horses_data),
                "form_spread": self._calculate_form_spread(horses_data),
                "key_angles": self._identify_key_angles(horses_data, race_data),
                "betting_angles": self._identify_betting_angles(horses_data),
                "value_opportunities": self._identify_value_opportunities(horses_data),
                "potential_overlays": self._identify_potential_overlays(horses_data),
                "competitiveness_rating": self._calculate_competitiveness_rating(
                    horses_data
                ),
                "expected_margin": self._calculate_expected_margin(horses_data),
                "confidence_in_analysis": self._calculate_analysis_confidence_race(
                    horses_data, race_data
                ),
            }

            return race_analysis

        except Exception as e:
            logger.error(f"Race analysis error: {e}")
            return None

    def _extract_race_conditions(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract target conditions from race data"""
        return {
            "distance": race_data.get("distance", 1600),
            "surface": race_data.get("surface", "Turf"),
            "track_condition": race_data.get("track_condition", "Good"),
            "race_class": race_data.get("race_class", "Maiden"),
            "field_size": race_data.get("field_size", 12),
            "track_name": race_data.get("track_name", "Unknown"),
        }

    async def _calculate_race_rankings(self, race_id: str):
        """Calculate and update race rankings based on composite scores"""
        try:
            # Get all composite scores for the race
            composite_scores = self.scoring_db.db_manager.execute_query(
                "SELECT horse_name, composite_score FROM composite_scores "
                "WHERE race_id = %s ORDER BY composite_score DESC",
                (race_id,),
            )

            # Update rankings
            for rank, score_data in enumerate(composite_scores, 1):
                self.scoring_db.db_manager.execute_query(
                    "UPDATE composite_scores SET composite_rank = %s "
                    "WHERE race_id = %s AND horse_name = %s",
                    (rank, race_id, score_data["horse_name"]),
                )

            logger.info(
                f"✅ Updated rankings for {len(composite_scores)} horses in race {race_id}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to calculate race rankings: {e}")

    # =================== SPEED/PACE CALCULATION HELPERS ===================

    def _calculate_base_speed_rating(self, speed_figures: List[float]) -> float:
        """Calculate base speed rating from speed figures"""
        if not speed_figures:
            return 0.0
        return sum(speed_figures) / len(speed_figures)

    def _calculate_adjusted_speed_rating(
        self, speed_figures: List[float], race_data: Dict[str, Any]
    ) -> float:
        """Calculate adjusted speed rating considering race conditions"""
        base_rating = self._calculate_base_speed_rating(speed_figures)

        # Apply adjustments for conditions
        track_adj = 0
        distance_adj = 0
        class_adj = 0

        # Track condition adjustment
        track_condition = race_data.get("track_condition", "Good")
        if track_condition == "Heavy":
            track_adj = -5
        elif track_condition == "Soft":
            track_adj = -2
        elif track_condition == "Firm":
            track_adj = 2

        return base_rating + track_adj + distance_adj + class_adj

    def _calculate_early_pace_rating(self, pace_data: List[Dict]) -> float:
        """Calculate early pace rating"""
        if not pace_data:
            return 50.0

        early_positions = [p.get("early_position", 6) for p in pace_data]
        avg_early_pos = sum(early_positions) / len(early_positions)

        # Convert position to rating (lower position = higher rating)
        return max(0, 100 - (avg_early_pos * 8))

    def _calculate_middle_pace_rating(self, pace_data: List[Dict]) -> float:
        """Calculate middle pace rating"""
        if not pace_data:
            return 50.0

        middle_positions = [p.get("middle_position", 6) for p in pace_data]
        avg_middle_pos = sum(middle_positions) / len(middle_positions)

        return max(0, 100 - (avg_middle_pos * 8))

    def _calculate_late_pace_rating(self, pace_data: List[Dict]) -> float:
        """Calculate late pace rating"""
        if not pace_data:
            return 50.0

        late_positions = [p.get("late_position", 6) for p in pace_data]
        avg_late_pos = sum(late_positions) / len(late_positions)

        return max(0, 100 - (avg_late_pos * 8))

    def _calculate_finishing_kick(self, pace_data: List[Dict]) -> float:
        """Calculate finishing kick rating"""
        if not pace_data:
            return 50.0

        kick_ratings = []
        for p in pace_data:
            middle_pos = p.get("middle_position", 6)
            final_pos = p.get("final_position", 6)
            kick = max(0, middle_pos - final_pos) * 10
            kick_ratings.append(kick)

        return sum(kick_ratings) / len(kick_ratings) if kick_ratings else 50.0

    def _determine_pace_scenario(self, pace_data: List[Dict]) -> str:
        """Determine the horse's preferred pace scenario"""
        if not pace_data:
            return "Unknown"

        early_avg = self._calculate_early_pace_rating(pace_data)
        late_avg = self._calculate_late_pace_rating(pace_data)

        if early_avg > 70:
            return "Front Runner"
        elif late_avg > 70:
            return "Closer"
        else:
            return "Stalker"

    # Add more helper methods as needed...
    def _calculate_pace_suitability(
        self, pace_data: List[Dict], race_data: Dict[str, Any]
    ) -> float:
        """Calculate how suitable the pace scenario is"""
        return 75.0  # Placeholder

    def _analyze_speed_trend(self, speed_figures: List[float]) -> str:
        """Analyze speed trend direction"""
        if len(speed_figures) < 3:
            return "Insufficient Data"

        recent = speed_figures[:3]
        if recent[0] > recent[-1]:
            return "Improving"
        elif recent[0] < recent[-1]:
            return "Declining"
        else:
            return "Stable"

    def _calculate_speed_trend_score(self, speed_figures: List[float]) -> float:
        """Calculate speed trend score"""
        if len(speed_figures) < 2:
            return 50.0

        trend_score = (speed_figures[0] - speed_figures[-1]) * 2
        return max(0, min(100, 50 + trend_score))

    def _calculate_speed_consistency(self, speed_figures: List[float]) -> float:
        """Calculate speed consistency score"""
        if len(speed_figures) < 2:
            return 50.0

        import statistics

        try:
            std_dev = statistics.stdev(speed_figures)
            # Lower standard deviation = higher consistency
            consistency = max(0, 100 - (std_dev * 5))
            return consistency
        except:
            return 50.0

    # Add more calculation methods as needed...
    def _calculate_distance_speed_rating(
        self, speed_figures: List[float], race_data: Dict[str, Any]
    ) -> float:
        """Calculate distance-specific speed rating"""
        return self._calculate_base_speed_rating(speed_figures)  # Placeholder

    def _calculate_surface_speed_rating(
        self, speed_figures: List[float], race_data: Dict[str, Any]
    ) -> float:
        """Calculate surface-specific speed rating"""
        return self._calculate_base_speed_rating(speed_figures)  # Placeholder

    def _calculate_class_par_speed(self, race_data: Dict[str, Any]) -> float:
        """Calculate class par speed for the race"""
        race_class = race_data.get("race_class", "Maiden")
        class_pars = {
            "Group 1": 110,
            "Group 2": 105,
            "Group 3": 100,
            "Listed": 95,
            "Handicap": 90,
            "Maiden": 80,
        }
        return class_pars.get(race_class, 85)

    def _calculate_speed_vs_class(
        self, speed_figures: List[float], race_data: Dict[str, Any]
    ) -> float:
        """Calculate speed relative to class"""
        avg_speed = self._calculate_base_speed_rating(speed_figures)
        class_par = self._calculate_class_par_speed(race_data)
        return avg_speed - class_par

    def _calculate_trip_rating(self, horse_data: Dict[str, Any]) -> float:
        """Calculate trip difficulty rating"""
        factors = 0
        if horse_data.get("wide_trip", False):
            factors -= 5
        if horse_data.get("traffic_issues", False):
            factors -= 10
        if horse_data.get("trouble_in_running", False):
            factors -= 15
        return max(0, 100 + factors)

    def _calculate_analysis_confidence(self, horse_data: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis"""
        confidence = 100

        # Reduce confidence based on data quality
        if not horse_data.get("speed_figures"):
            confidence -= 20
        if not horse_data.get("pace_data"):
            confidence -= 15
        if not horse_data.get("form_history"):
            confidence -= 25

        return max(0, confidence)

    def _calculate_data_quality_score(self, horse_data: Dict[str, Any]) -> float:
        """Calculate data quality score"""
        quality_score = 0
        total_possible = 0

        # Check data completeness
        data_elements = [
            "speed_figures",
            "pace_data",
            "form_history",
            "recent_runs",
            "class_ratings",
            "jockey_stats",
        ]

        for element in data_elements:
            total_possible += 1
            if horse_data.get(element):
                quality_score += 1

        return (quality_score / total_possible) * 100 if total_possible > 0 else 0

    # =================== RACE ANALYSIS HELPERS ===================

    def _predict_pace_scenario(self, horses_data: List[Dict[str, Any]]) -> str:
        """Predict the pace scenario for the race"""
        early_speed_count = self._count_early_speed_horses(horses_data)
        field_size = len(horses_data)

        if early_speed_count / field_size > 0.5:
            return "Hot Pace"
        elif early_speed_count / field_size < 0.2:
            return "Slow Pace"
        else:
            return "Moderate Pace"

    def _analyze_pace_competitiveness(self, horses_data: List[Dict[str, Any]]) -> float:
        """Analyze how competitive the pace will be"""
        early_speed_count = self._count_early_speed_horses(horses_data)
        return min(100, early_speed_count * 15)

    def _count_early_speed_horses(self, horses_data: List[Dict[str, Any]]) -> int:
        """Count horses with early speed"""
        count = 0
        for horse in horses_data:
            pace_data = horse.get("pace_data", [])
            early_rating = self._calculate_early_pace_rating(pace_data)
            if early_rating > 70:
                count += 1
        return count

    def _count_closers(self, horses_data: List[Dict[str, Any]]) -> int:
        """Count closing horses"""
        count = 0
        for horse in horses_data:
            pace_data = horse.get("pace_data", [])
            late_rating = self._calculate_late_pace_rating(pace_data)
            if late_rating > 70:
                count += 1
        return count

    def _calculate_field_strength(self, horses_data: List[Dict[str, Any]]) -> float:
        """Calculate overall field strength"""
        if not horses_data:
            return 50.0

        strength_ratings = []
        for horse in horses_data:
            # Use recent performance as proxy for strength
            speed_figures = horse.get("speed_figures", [])
            if speed_figures:
                strength_ratings.append(max(speed_figures))
            else:
                strength_ratings.append(70)  # Default average

        return sum(strength_ratings) / len(strength_ratings)

    def _calculate_class_homogeneity(self, horses_data: List[Dict[str, Any]]) -> float:
        """Calculate how similar the class levels are"""
        return 75.0  # Placeholder implementation

    def _calculate_form_spread(self, horses_data: List[Dict[str, Any]]) -> float:
        """Calculate the spread in form across the field"""
        return 60.0  # Placeholder implementation

    def _identify_key_angles(
        self, horses_data: List[Dict[str, Any]], race_data: Dict[str, Any]
    ) -> List[str]:
        """Identify key angles for the race"""
        angles = []

        # Distance angle
        distance = race_data.get("distance", 1600)
        if distance > 2000:
            angles.append("Stamina Test")
        elif distance < 1200:
            angles.append("Speed Test")

        # Surface angle
        surface = race_data.get("surface", "Turf")
        if surface == "All Weather":
            angles.append("All Weather Specialists")

        return angles

    def _identify_betting_angles(self, horses_data: List[Dict[str, Any]]) -> List[str]:
        """Identify betting angles"""
        return ["Form Reversal", "Class Drop", "Track Specialist"]  # Placeholder

    def _identify_value_opportunities(
        self, horses_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify value betting opportunities"""
        return ["Overlooked Form", "Improvement Expected"]  # Placeholder

    def _identify_potential_overlays(
        self, horses_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify potential overlay horses"""
        overlays = []
        for horse in horses_data:
            horse_name = horse.get("name", "Unknown")
            odds = horse.get("current_odds", 10.0)

            # Simple overlay detection (placeholder)
            if odds > 8.0:
                overlays.append(horse_name)

        return overlays

    def _calculate_competitiveness_rating(
        self, horses_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate how competitive the race is"""
        field_strength = self._calculate_field_strength(horses_data)
        field_size = len(horses_data)

        # More horses and higher strength = more competitive
        competitiveness = (field_strength * 0.7) + (min(field_size, 20) * 1.5)
        return min(100, competitiveness)

    def _calculate_expected_margin(self, horses_data: List[Dict[str, Any]]) -> float:
        """Calculate expected winning margin"""
        return 2.5  # Placeholder - average winning margin in lengths

    def _calculate_analysis_confidence_race(
        self, horses_data: List[Dict[str, Any]], race_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in race analysis"""
        confidence = 100

        # Reduce confidence based on field size and data quality
        field_size = len(horses_data)
        if field_size > 16:
            confidence -= 15  # Large fields are harder to predict
        elif field_size < 8:
            confidence -= 10  # Small fields may lack competitiveness

        # Check data completeness across field
        complete_data_count = 0
        for horse in horses_data:
            if (
                horse.get("speed_figures")
                and horse.get("form_history")
                and horse.get("pace_data")
            ):
                complete_data_count += 1

        data_completeness = complete_data_count / field_size
        confidence *= data_completeness

        return max(20, confidence)  # Minimum 20% confidence

    def close(self):
        """Close database connections"""
        if self.scoring_db:
            self.scoring_db.close()


# =================== DEMO/TESTING FUNCTIONS ===================


async def demo_integration():
    """Demo the scoring integration system"""
    logger.info("🎯 Starting Horse Racing Scoring Integration Demo")

    integration_manager = ScoringIntegrationManager()

    # Sample horse data
    sample_horse = {
        "name": "Thunderbolt",
        "speed_figures": [95, 92, 98, 90, 94],
        "pace_data": [
            {"early_position": 2, "middle_position": 3, "final_position": 1},
            {"early_position": 1, "middle_position": 2, "final_position": 2},
            {"early_position": 3, "middle_position": 2, "final_position": 1},
        ],
        "form_history": ["1-2-1-3-2"],
        "recent_runs": [
            {"position": 1, "beaten_margin": 0, "class": "Listed"},
            {"position": 2, "beaten_margin": 0.5, "class": "Group 3"},
            {"position": 1, "beaten_margin": 0, "class": "Handicap"},
        ],
        "current_odds": 4.5,
        "jockey_stats": {"win_rate": 0.15, "place_rate": 0.35},
        "trainer_stats": {"win_rate": 0.18, "place_rate": 0.40},
    }

    # Sample race data
    sample_race = {
        "race_id": "DEMO_RACE_001",
        "distance": 1600,
        "surface": "Turf",
        "track_condition": "Good",
        "race_class": "Group 3",
        "field_size": 12,
        "track_name": "Demo Track",
    }

    # Analyze and store horse
    result = await integration_manager.analyze_and_store_horse(
        sample_horse, sample_race
    )

    logger.info(f"📊 Analysis Result: {result['success']}")
    if result["errors"]:
        logger.warning(f"⚠️ Errors: {result['errors']}")

    # Get stored data back
    form_data = integration_manager.scoring_db.get_horse_form_analysis("Thunderbolt", 1)
    power_data = integration_manager.scoring_db.get_horse_power_ratings(
        "Thunderbolt", 1
    )
    composite_data = integration_manager.scoring_db.get_horse_composite_scores(
        "Thunderbolt", 1
    )

    logger.info(f"📈 Retrieved form data: {len(form_data)} records")
    logger.info(f"⚡ Retrieved power data: {len(power_data)} records")
    logger.info(f"🎯 Retrieved composite data: {len(composite_data)} records")

    # Get statistics
    stats = integration_manager.scoring_db.get_scoring_statistics()
    logger.info(f"📊 Database Statistics: {stats}")

    integration_manager.close()
    logger.info("✅ Demo completed successfully")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_integration())
