#!/usr/bin/env python3
"""
Horse Racing Scoring Database Manager Extension

Handles database operations for form analysis, power ratings, and speed/pace analysis.
Extends the existing DatabaseManager with scoring-specific functionality.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
import json

from src.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScoringDatabaseManager:
    """Extended database manager for horse racing scoring data"""

    def __init__(self, database_url: str = None):
        """Initialize with existing database manager"""
        self.db_manager = DatabaseManager(database_url)

    def save_form_analysis(
        self,
        horse_name: str,
        race_id: str,
        form_metrics: Dict[str, Any],
        target_conditions: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save form analysis results to database"""
        try:
            query = """
                INSERT INTO form_analysis (
                    horse_name, race_id, analysis_date,
                    last_run_score, recent_form_score, seasonal_form_score,
                    speed_rating, pace_rating, finishing_speed_index,
                    consistency_index, reliability_score,
                    class_rating, competition_strength,
                    track_bias_adjustment, condition_suitability,
                    distance_suitability, trip_efficiency,
                    jockey_form, trainer_form, combo_efficiency,
                    form_composite, power_rating, confidence_level,
                    target_race_conditions, factors_breakdown
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (horse_name, race_id, analysis_date)
                DO UPDATE SET
                    last_run_score = EXCLUDED.last_run_score,
                    recent_form_score = EXCLUDED.recent_form_score,
                    seasonal_form_score = EXCLUDED.seasonal_form_score,
                    speed_rating = EXCLUDED.speed_rating,
                    pace_rating = EXCLUDED.pace_rating,
                    finishing_speed_index = EXCLUDED.finishing_speed_index,
                    consistency_index = EXCLUDED.consistency_index,
                    reliability_score = EXCLUDED.reliability_score,
                    class_rating = EXCLUDED.class_rating,
                    competition_strength = EXCLUDED.competition_strength,
                    track_bias_adjustment = EXCLUDED.track_bias_adjustment,
                    condition_suitability = EXCLUDED.condition_suitability,
                    distance_suitability = EXCLUDED.distance_suitability,
                    trip_efficiency = EXCLUDED.trip_efficiency,
                    jockey_form = EXCLUDED.jockey_form,
                    trainer_form = EXCLUDED.trainer_form,
                    combo_efficiency = EXCLUDED.combo_efficiency,
                    form_composite = EXCLUDED.form_composite,
                    power_rating = EXCLUDED.power_rating,
                    confidence_level = EXCLUDED.confidence_level,
                    target_race_conditions = EXCLUDED.target_race_conditions,
                    factors_breakdown = EXCLUDED.factors_breakdown
            """

            params = (
                horse_name,
                race_id,
                datetime.now(),
                form_metrics.get("last_run_score"),
                form_metrics.get("recent_form_score"),
                form_metrics.get("seasonal_form_score"),
                form_metrics.get("speed_rating"),
                form_metrics.get("pace_rating"),
                form_metrics.get("finishing_speed_index"),
                form_metrics.get("consistency_index"),
                form_metrics.get("reliability_score"),
                form_metrics.get("class_rating"),
                form_metrics.get("competition_strength"),
                form_metrics.get("track_bias_adjustment"),
                form_metrics.get("condition_suitability"),
                form_metrics.get("distance_suitability"),
                form_metrics.get("trip_efficiency"),
                form_metrics.get("jockey_form"),
                form_metrics.get("trainer_form"),
                form_metrics.get("combo_efficiency"),
                form_metrics.get("form_composite"),
                form_metrics.get("power_rating"),
                form_metrics.get("confidence_level"),
                json.dumps(target_conditions) if target_conditions else None,
                json.dumps(form_metrics),
            )

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()

            logger.info(f"✅ Saved form analysis for {horse_name} in race {race_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save form analysis: {e}")
            return False

    def save_power_rating(
        self,
        horse_name: str,
        race_id: str,
        power_rating_data: Dict[str, Any],
        target_conditions: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save power rating results to database"""
        try:
            query = """
                INSERT INTO power_ratings (
                    horse_name, race_id, rating_date,
                    base_rating, adjusted_rating,
                    speed_component, class_component, form_component,
                    consistency_component, conditions_adjustment, track_bias_adj,
                    distance_specialization_adj, surface_suitability_adj,
                    jockey_trainer_adj, equipment_change_adj, layoff_adj,
                    class_movement_adj, weight_allowance_adj,
                    confidence_level, target_race_conditions,
                    adjustment_factors, factors_breakdown
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (horse_name, race_id, rating_date)
                DO UPDATE SET
                    base_rating = EXCLUDED.base_rating,
                    adjusted_rating = EXCLUDED.adjusted_rating,
                    speed_component = EXCLUDED.speed_component,
                    class_component = EXCLUDED.class_component,
                    form_component = EXCLUDED.form_component,
                    consistency_component = EXCLUDED.consistency_component,
                    conditions_adjustment = EXCLUDED.conditions_adjustment,
                    track_bias_adj = EXCLUDED.track_bias_adj,
                    distance_specialization_adj = EXCLUDED.distance_specialization_adj,
                    surface_suitability_adj = EXCLUDED.surface_suitability_adj,
                    jockey_trainer_adj = EXCLUDED.jockey_trainer_adj,
                    equipment_change_adj = EXCLUDED.equipment_change_adj,
                    layoff_adj = EXCLUDED.layoff_adj,
                    class_movement_adj = EXCLUDED.class_movement_adj,
                    weight_allowance_adj = EXCLUDED.weight_allowance_adj,
                    confidence_level = EXCLUDED.confidence_level,
                    target_race_conditions = EXCLUDED.target_race_conditions,
                    adjustment_factors = EXCLUDED.adjustment_factors,
                    factors_breakdown = EXCLUDED.factors_breakdown
            """

            params = (
                horse_name,
                race_id,
                datetime.now(),
                power_rating_data.get("base_rating"),
                power_rating_data.get("adjusted_rating"),
                power_rating_data.get("speed_component"),
                power_rating_data.get("class_component"),
                power_rating_data.get("form_component"),
                power_rating_data.get("consistency_component"),
                power_rating_data.get("conditions_adjustment"),
                power_rating_data.get("track_bias_adj", 0.0),
                power_rating_data.get("distance_specialization_adj", 0.0),
                power_rating_data.get("surface_suitability_adj", 0.0),
                power_rating_data.get("jockey_trainer_adj", 0.0),
                power_rating_data.get("equipment_change_adj", 0.0),
                power_rating_data.get("layoff_adj", 0.0),
                power_rating_data.get("class_movement_adj", 0.0),
                power_rating_data.get("weight_allowance_adj", 0.0),
                power_rating_data.get("confidence_level"),
                json.dumps(target_conditions) if target_conditions else None,
                json.dumps(power_rating_data.get("adjustment_factors", {})),
                json.dumps(power_rating_data.get("factors_breakdown", {})),
            )

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()

            logger.info(f"✅ Saved power rating for {horse_name} in race {race_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save power rating: {e}")
            return False

    def save_composite_score(
        self, horse_name: str, race_id: str, composite_data: Dict[str, Any]
    ) -> bool:
        """Save composite scoring results to database"""
        try:
            query = """
                INSERT INTO composite_scores (
                    horse_name, race_id, scoring_date,
                    form_score, power_rating, composite_score,
                    speed_score, class_score, consistency_score,
                    form_trend_score, conditions_score,
                    win_probability, place_probability, show_probability,
                    confidence_level, composite_rank, power_rating_rank, form_rank,
                    betting_odds, betting_value,
                    key_factors, concerns, factors_breakdown
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (horse_name, race_id, scoring_date)
                DO UPDATE SET
                    form_score = EXCLUDED.form_score,
                    power_rating = EXCLUDED.power_rating,
                    composite_score = EXCLUDED.composite_score,
                    speed_score = EXCLUDED.speed_score,
                    class_score = EXCLUDED.class_score,
                    consistency_score = EXCLUDED.consistency_score,
                    form_trend_score = EXCLUDED.form_trend_score,
                    conditions_score = EXCLUDED.conditions_score,
                    win_probability = EXCLUDED.win_probability,
                    place_probability = EXCLUDED.place_probability,
                    show_probability = EXCLUDED.show_probability,
                    confidence_level = EXCLUDED.confidence_level,
                    composite_rank = EXCLUDED.composite_rank,
                    power_rating_rank = EXCLUDED.power_rating_rank,
                    form_rank = EXCLUDED.form_rank,
                    betting_odds = EXCLUDED.betting_odds,
                    betting_value = EXCLUDED.betting_value,
                    key_factors = EXCLUDED.key_factors,
                    concerns = EXCLUDED.concerns,
                    factors_breakdown = EXCLUDED.factors_breakdown
            """

            params = (
                horse_name,
                race_id,
                datetime.now(),
                composite_data.get("form_score"),
                composite_data.get("power_rating"),
                composite_data.get("composite_score"),
                composite_data.get("speed_score"),
                composite_data.get("class_score"),
                composite_data.get("consistency_score"),
                composite_data.get("form_trend_score"),
                composite_data.get("conditions_score"),
                composite_data.get("win_probability"),
                composite_data.get("place_probability"),
                composite_data.get("show_probability"),
                composite_data.get("confidence_level"),
                composite_data.get("composite_rank"),
                composite_data.get("power_rating_rank"),
                composite_data.get("form_rank"),
                composite_data.get("betting_odds"),
                composite_data.get("betting_value"),
                composite_data.get("key_factors", []),
                composite_data.get("concerns", []),
                json.dumps(composite_data.get("factors_breakdown", {})),
            )

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()

            logger.info(f"✅ Saved composite score for {horse_name} in race {race_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save composite score: {e}")
            return False

    def save_speed_pace_analysis(
        self, horse_name: str, race_id: str, speed_pace_data: Dict[str, Any]
    ) -> bool:
        """Save speed and pace analysis to database"""
        try:
            query = """
                INSERT INTO speed_pace_analysis (
                    horse_name, race_id, analysis_date,
                    base_speed_rating, adjusted_speed_rating, speed_figure,
                    early_pace_rating, middle_pace_rating, late_pace_rating,
                    finishing_kick_rating, pace_scenario, pace_suitability_score,
                    speed_trend_direction, speed_trend_score, speed_consistency,
                    distance_speed_rating, surface_speed_rating,
                    class_par_speed, speed_vs_class, trip_rating,
                    trouble_encountered, wide_trip, traffic_issues,
                    track_variant, track_condition, wind_factor,
                    sectional_times, fractional_times,
                    analysis_confidence, data_quality_score
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (horse_name, race_id, analysis_date)
                DO UPDATE SET
                    base_speed_rating = EXCLUDED.base_speed_rating,
                    adjusted_speed_rating = EXCLUDED.adjusted_speed_rating,
                    speed_figure = EXCLUDED.speed_figure,
                    early_pace_rating = EXCLUDED.early_pace_rating,
                    middle_pace_rating = EXCLUDED.middle_pace_rating,
                    late_pace_rating = EXCLUDED.late_pace_rating,
                    finishing_kick_rating = EXCLUDED.finishing_kick_rating,
                    pace_scenario = EXCLUDED.pace_scenario,
                    pace_suitability_score = EXCLUDED.pace_suitability_score,
                    speed_trend_direction = EXCLUDED.speed_trend_direction,
                    speed_trend_score = EXCLUDED.speed_trend_score,
                    speed_consistency = EXCLUDED.speed_consistency,
                    distance_speed_rating = EXCLUDED.distance_speed_rating,
                    surface_speed_rating = EXCLUDED.surface_speed_rating,
                    class_par_speed = EXCLUDED.class_par_speed,
                    speed_vs_class = EXCLUDED.speed_vs_class,
                    trip_rating = EXCLUDED.trip_rating,
                    trouble_encountered = EXCLUDED.trouble_encountered,
                    wide_trip = EXCLUDED.wide_trip,
                    traffic_issues = EXCLUDED.traffic_issues,
                    track_variant = EXCLUDED.track_variant,
                    track_condition = EXCLUDED.track_condition,
                    wind_factor = EXCLUDED.wind_factor,
                    sectional_times = EXCLUDED.sectional_times,
                    fractional_times = EXCLUDED.fractional_times,
                    analysis_confidence = EXCLUDED.analysis_confidence,
                    data_quality_score = EXCLUDED.data_quality_score
            """

            params = (
                horse_name,
                race_id,
                datetime.now(),
                speed_pace_data.get("base_speed_rating"),
                speed_pace_data.get("adjusted_speed_rating"),
                speed_pace_data.get("speed_figure"),
                speed_pace_data.get("early_pace_rating"),
                speed_pace_data.get("middle_pace_rating"),
                speed_pace_data.get("late_pace_rating"),
                speed_pace_data.get("finishing_kick_rating"),
                speed_pace_data.get("pace_scenario"),
                speed_pace_data.get("pace_suitability_score"),
                speed_pace_data.get("speed_trend_direction"),
                speed_pace_data.get("speed_trend_score"),
                speed_pace_data.get("speed_consistency"),
                speed_pace_data.get("distance_speed_rating"),
                speed_pace_data.get("surface_speed_rating"),
                speed_pace_data.get("class_par_speed"),
                speed_pace_data.get("speed_vs_class"),
                speed_pace_data.get("trip_rating"),
                speed_pace_data.get("trouble_encountered", False),
                speed_pace_data.get("wide_trip", False),
                speed_pace_data.get("traffic_issues", False),
                speed_pace_data.get("track_variant"),
                speed_pace_data.get("track_condition"),
                speed_pace_data.get("wind_factor"),
                json.dumps(speed_pace_data.get("sectional_times", {})),
                json.dumps(speed_pace_data.get("fractional_times", {})),
                speed_pace_data.get("analysis_confidence"),
                speed_pace_data.get("data_quality_score"),
            )

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()

            logger.info(
                f"✅ Saved speed/pace analysis for {horse_name} in race {race_id}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save speed/pace analysis: {e}")
            return False

    def save_race_analysis(
        self, race_id: str, race_analysis_data: Dict[str, Any]
    ) -> bool:
        """Save race-level analysis to database"""
        try:
            query = """
                INSERT INTO race_analysis (
                    race_id, analysis_date, race_conditions, field_size,
                    race_type, distance, surface, track_condition,
                    predicted_pace_scenario, pace_competitiveness,
                    early_speed_horses, closers_count, track_bias, bias_strength,
                    weather_impact, field_strength_rating, class_homogeneity,
                    form_spread, key_angles, betting_angles, value_opportunities,
                    potential_overlays, competitiveness_rating, expected_margin,
                    confidence_in_analysis
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (race_id, analysis_date)
                DO UPDATE SET
                    race_conditions = EXCLUDED.race_conditions,
                    field_size = EXCLUDED.field_size,
                    race_type = EXCLUDED.race_type,
                    distance = EXCLUDED.distance,
                    surface = EXCLUDED.surface,
                    track_condition = EXCLUDED.track_condition,
                    predicted_pace_scenario = EXCLUDED.predicted_pace_scenario,
                    pace_competitiveness = EXCLUDED.pace_competitiveness,
                    early_speed_horses = EXCLUDED.early_speed_horses,
                    closers_count = EXCLUDED.closers_count,
                    track_bias = EXCLUDED.track_bias,
                    bias_strength = EXCLUDED.bias_strength,
                    weather_impact = EXCLUDED.weather_impact,
                    field_strength_rating = EXCLUDED.field_strength_rating,
                    class_homogeneity = EXCLUDED.class_homogeneity,
                    form_spread = EXCLUDED.form_spread,
                    key_angles = EXCLUDED.key_angles,
                    betting_angles = EXCLUDED.betting_angles,
                    value_opportunities = EXCLUDED.value_opportunities,
                    potential_overlays = EXCLUDED.potential_overlays,
                    competitiveness_rating = EXCLUDED.competitiveness_rating,
                    expected_margin = EXCLUDED.expected_margin,
                    confidence_in_analysis = EXCLUDED.confidence_in_analysis
            """

            params = (
                race_id,
                datetime.now(),
                json.dumps(race_analysis_data.get("race_conditions", {})),
                race_analysis_data.get("field_size"),
                race_analysis_data.get("race_type"),
                race_analysis_data.get("distance"),
                race_analysis_data.get("surface"),
                race_analysis_data.get("track_condition"),
                race_analysis_data.get("predicted_pace_scenario"),
                race_analysis_data.get("pace_competitiveness"),
                race_analysis_data.get("early_speed_horses"),
                race_analysis_data.get("closers_count"),
                race_analysis_data.get("track_bias"),
                race_analysis_data.get("bias_strength"),
                race_analysis_data.get("weather_impact"),
                race_analysis_data.get("field_strength_rating"),
                race_analysis_data.get("class_homogeneity"),
                race_analysis_data.get("form_spread"),
                race_analysis_data.get("key_angles", []),
                race_analysis_data.get("betting_angles", []),
                race_analysis_data.get("value_opportunities", []),
                race_analysis_data.get("potential_overlays", []),
                race_analysis_data.get("competitiveness_rating"),
                race_analysis_data.get("expected_margin"),
                race_analysis_data.get("confidence_in_analysis"),
            )

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()

            logger.info(f"✅ Saved race analysis for race {race_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save race analysis: {e}")
            return False

    # =================== RETRIEVAL METHODS ===================

    def get_horse_form_analysis(
        self, horse_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent form analysis for a horse"""
        query = """
            SELECT * FROM form_analysis
            WHERE horse_name = %s
            ORDER BY analysis_date DESC
            LIMIT %s
        """
        return self.db_manager.execute_query(query, (horse_name, limit))

    def get_horse_power_ratings(
        self, horse_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent power ratings for a horse"""
        query = """
            SELECT * FROM power_ratings
            WHERE horse_name = %s
            ORDER BY rating_date DESC
            LIMIT %s
        """
        return self.db_manager.execute_query(query, (horse_name, limit))

    def get_horse_composite_scores(
        self, horse_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent composite scores for a horse"""
        query = """
            SELECT * FROM composite_scores
            WHERE horse_name = %s
            ORDER BY scoring_date DESC
            LIMIT %s
        """
        return self.db_manager.execute_query(query, (horse_name, limit))

    def get_race_scoring_summary(self, race_id: str) -> Dict[str, Any]:
        """Get complete scoring summary for a race"""
        # Get all horses' scores for the race
        horses_query = """
            SELECT horse_name, composite_score, win_probability,
                   composite_rank, power_rating, form_score
            FROM composite_scores
            WHERE race_id = %s
            ORDER BY composite_rank ASC
        """
        horses = self.db_manager.execute_query(horses_query, (race_id,))

        # Get race analysis
        race_query = """
            SELECT * FROM race_analysis
            WHERE race_id = %s
            ORDER BY analysis_date DESC
            LIMIT 1
        """
        race_analysis = self.db_manager.execute_single(race_query, (race_id,))

        return {
            "race_id": race_id,
            "horses": horses,
            "race_analysis": race_analysis,
            "field_size": len(horses),
        }

    def get_top_rated_horses(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top-rated horses based on recent composite scores"""
        query = """
            SELECT DISTINCT ON (horse_name)
                horse_name, composite_score, win_probability,
                power_rating, form_score, scoring_date
            FROM composite_scores
            WHERE scoring_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY horse_name, scoring_date DESC
        """

        recent_scores = self.db_manager.execute_query(query)

        # Sort by composite score
        recent_scores.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

        return recent_scores[:limit]

    def get_speed_leaders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get horses with highest speed ratings"""
        query = """
            SELECT DISTINCT ON (horse_name)
                horse_name, base_speed_rating, adjusted_speed_rating,
                speed_figure, pace_scenario, analysis_date
            FROM speed_pace_analysis
            WHERE analysis_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY horse_name, analysis_date DESC
        """

        recent_speeds = self.db_manager.execute_query(query)

        # Sort by adjusted speed rating
        recent_speeds.sort(
            key=lambda x: x.get("adjusted_speed_rating", 0), reverse=True
        )

        return recent_speeds[:limit]

    def get_form_trends(self, horse_name: str) -> Dict[str, Any]:
        """Get form trend analysis for a horse"""
        query = """
            SELECT analysis_date, recent_form_score, speed_rating,
                   consistency_index, confidence_level
            FROM form_analysis
            WHERE horse_name = %s
            ORDER BY analysis_date DESC
            LIMIT 10
        """

        form_data = self.db_manager.execute_query(query, (horse_name,))

        if not form_data:
            return {"horse_name": horse_name, "trend": "no_data", "data_points": []}

        # Calculate trend
        recent_scores = [
            d["recent_form_score"] for d in form_data if d["recent_form_score"]
        ]

        if len(recent_scores) >= 3:
            if recent_scores[0] > recent_scores[-1] * 1.1:
                trend = "improving"
            elif recent_scores[0] < recent_scores[-1] * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "horse_name": horse_name,
            "trend": trend,
            "data_points": form_data,
            "latest_score": recent_scores[0] if recent_scores else None,
        }

    def get_scoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scoring statistics"""
        stats = {}

        # Form analysis stats
        form_stats = self.db_manager.execute_single(
            """
            SELECT COUNT(*) as total_analyses,
                   AVG(speed_rating) as avg_speed_rating,
                   AVG(consistency_index) as avg_consistency,
                   AVG(confidence_level) as avg_confidence
            FROM form_analysis
            WHERE analysis_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        )
        stats["form_analysis"] = form_stats

        # Power rating stats
        power_stats = self.db_manager.execute_single(
            """
            SELECT COUNT(*) as total_ratings,
                   AVG(adjusted_rating) as avg_power_rating,
                   MAX(adjusted_rating) as max_rating,
                   MIN(adjusted_rating) as min_rating
            FROM power_ratings
            WHERE rating_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        )
        stats["power_ratings"] = power_stats

        # Composite score stats
        composite_stats = self.db_manager.execute_single(
            """
            SELECT COUNT(*) as total_scores,
                   AVG(composite_score) as avg_composite_score,
                   AVG(win_probability) as avg_win_probability
            FROM composite_scores
            WHERE scoring_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        )
        stats["composite_scores"] = composite_stats

        # Race analysis stats
        race_stats = self.db_manager.execute_single(
            """
            SELECT COUNT(*) as total_races,
                   AVG(field_size) as avg_field_size,
                   AVG(competitiveness_rating) as avg_competitiveness
            FROM race_analysis
            WHERE analysis_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        )
        stats["race_analysis"] = race_stats

        return stats

    def close(self):
        """Close database connections"""
        if self.db_manager:
            self.db_manager.close()


if __name__ == "__main__":
    # Test the scoring database manager
    scoring_db = ScoringDatabaseManager()

    # Test getting statistics
    stats = scoring_db.get_scoring_statistics()
    print("📊 Scoring Database Statistics:")
    for category, data in stats.items():
        print(f"  {category}: {data}")

    scoring_db.close()
