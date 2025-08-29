#!/usr/bin/env python3
"""
Race Trends Analyzer for Horse Racing AI v2.0
Advanced statistical analysis of race patterns and trends to identify betting
edges. Inspired by thestatsdontlie.com methodology for comprehensive race
analysis.
"""

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RaceTrend:
    """Individual race trend analysis."""

    trend_type: str  # e.g., "age", "weight", "draw", "form"
    pattern: str  # Description of the pattern
    percentage: float  # Percentage of winners fitting this pattern
    sample_size: int  # Number of races analyzed
    confidence: float  # Statistical confidence (0-1)
    edge_value: float  # Betting edge value (0-1)
    last_updated: str


@dataclass
class RaceAnalysisTrends:
    """Complete trends analysis for a specific race type."""

    race_name: str
    race_type: str  # e.g., "handicap", "stakes", "maiden"
    distance: str
    course: str
    surface: str
    age_trends: List[RaceTrend]
    weight_trends: List[RaceTrend]
    draw_trends: List[RaceTrend]
    form_trends: List[RaceTrend]
    price_trends: List[RaceTrend]
    seasonal_trends: List[RaceTrend]
    course_form_trends: List[RaceTrend]
    distance_form_trends: List[RaceTrend]
    overall_edge_score: float
    total_patterns_found: int
    analysis_date: str


@dataclass
class HorseTrendScore:
    """Trend-based scoring for individual horse."""

    horse_name: str
    trend_scores: Dict[str, float]  # Category -> score
    overall_trend_score: float
    matching_patterns: List[str]
    edge_factors: List[str]
    confidence: float
    recommendation: str  # "STRONG", "MODERATE", "WEAK", "AVOID"


class RaceTrendsAnalyzer:
    """
    Advanced race trends analyzer that identifies statistical patterns
    and edges in horse racing data to enhance prediction accuracy.
    """

    def __init__(self):
        """Initialize the trends analyzer."""
        self.historical_data: List[Dict[str, Any]] = []
        self.trend_database: Dict[str, RaceAnalysisTrends] = {}
        self.pattern_cache: Dict[str, List[RaceTrend]] = {}

        # Statistical thresholds
        self.min_sample_size = 10  # Minimum races for reliable trends
        self.confidence_threshold = 0.7  # Minimum confidence for actionable
        self.edge_threshold = 0.15  # Minimum edge value for betting

        logger.info("Race Trends Analyzer initialized")

    def analyze_race_trends(
        self, race_data: Dict[str, Any], historical_races: List[Dict[str, Any]]
    ) -> RaceAnalysisTrends:
        """
        Analyze comprehensive race trends similar to thestatsdontlie.com methodology.

        Args:
            race_data: Current race information
            historical_races: Historical race data for pattern analysis

        Returns:
            RaceAnalysisTrends with comprehensive statistical analysis
        """
        try:
            race_name = race_data.get("race_name", "Unknown Race")
            race_type = race_data.get("race_type", "handicap")
            distance = race_data.get("distance", "1m2f")
            course = race_data.get("course", "Unknown")
            surface = race_data.get("surface", "turf")

            # Filter relevant historical data
            relevant_races = self._filter_relevant_races(race_data, historical_races)

            if len(relevant_races) < self.min_sample_size:
                logger.warning(
                    f"Insufficient data for {race_name}: {len(relevant_races)} races"
                )
                return self._create_empty_trends(race_data)

            # Analyze different trend categories
            age_trends = self._analyze_age_trends(relevant_races)
            weight_trends = self._analyze_weight_trends(relevant_races)
            draw_trends = self._analyze_draw_trends(relevant_races)
            form_trends = self._analyze_form_trends(relevant_races)
            price_trends = self._analyze_price_trends(relevant_races)
            seasonal_trends = self._analyze_seasonal_trends(relevant_races)
            course_form_trends = self._analyze_course_form_trends(relevant_races)
            distance_form_trends = self._analyze_distance_form_trends(relevant_races)

            # Calculate overall edge score
            all_trends = (
                age_trends
                + weight_trends
                + draw_trends
                + form_trends
                + price_trends
                + seasonal_trends
                + course_form_trends
                + distance_form_trends
            )

            overall_edge_score = self._calculate_overall_edge_score(all_trends)
            total_patterns = len(
                [t for t in all_trends if t.confidence >= self.confidence_threshold]
            )

            return RaceAnalysisTrends(
                race_name=race_name,
                race_type=race_type,
                distance=distance,
                course=course,
                surface=surface,
                age_trends=age_trends,
                weight_trends=weight_trends,
                draw_trends=draw_trends,
                form_trends=form_trends,
                price_trends=price_trends,
                seasonal_trends=seasonal_trends,
                course_form_trends=course_form_trends,
                distance_form_trends=distance_form_trends,
                overall_edge_score=overall_edge_score,
                total_patterns_found=total_patterns,
                analysis_date=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Error analyzing race trends: {e}")
            return self._create_empty_trends(race_data)

    def score_horse_trends(
        self, horse_data: Dict[str, Any], race_trends: RaceAnalysisTrends
    ) -> HorseTrendScore:
        """
        Score individual horse based on race trends analysis.

        Args:
            horse_data: Horse information and form
            race_trends: Analyzed race trends

        Returns:
            HorseTrendScore with trend-based assessment
        """
        horse_name = horse_data.get("name", "Unknown")
        trend_scores = {}
        matching_patterns = []
        edge_factors = []

        try:
            # Score against age trends
            age_score = self._score_age_trends(horse_data, race_trends.age_trends)
            trend_scores["age"] = age_score

            # Score against weight trends
            weight_score = self._score_weight_trends(
                horse_data, race_trends.weight_trends
            )
            trend_scores["weight"] = weight_score

            # Score against draw trends
            draw_score = self._score_draw_trends(horse_data, race_trends.draw_trends)
            trend_scores["draw"] = draw_score

            # Score against form trends
            form_score = self._score_form_trends(horse_data, race_trends.form_trends)
            trend_scores["form"] = form_score

            # Score against price trends
            price_score = self._score_price_trends(horse_data, race_trends.price_trends)
            trend_scores["price"] = price_score

            # Score against seasonal trends
            seasonal_score = self._score_seasonal_trends(
                horse_data, race_trends.seasonal_trends
            )
            trend_scores["seasonal"] = seasonal_score

            # Score against course form trends
            course_score = self._score_course_form_trends(
                horse_data, race_trends.course_form_trends
            )
            trend_scores["course_form"] = course_score

            # Score against distance form trends
            distance_score = self._score_distance_form_trends(
                horse_data, race_trends.distance_form_trends
            )
            trend_scores["distance_form"] = distance_score

            # Calculate overall trend score
            weights = {
                "age": 0.15,
                "weight": 0.15,
                "draw": 0.10,
                "form": 0.20,
                "price": 0.10,
                "seasonal": 0.10,
                "course_form": 0.10,
                "distance_form": 0.10,
            }

            overall_score = sum(
                score * weights.get(category, 0.1)
                for category, score in trend_scores.items()
            )

            # Identify matching patterns and edge factors
            matching_patterns = self._identify_matching_patterns(
                horse_data, race_trends
            )
            edge_factors = self._identify_edge_factors(trend_scores, race_trends)

            # Calculate confidence based on number of strong trend matches
            confidence = self._calculate_trend_confidence(
                trend_scores, matching_patterns
            )

            # Generate recommendation
            recommendation = self._generate_trend_recommendation(
                overall_score, confidence, edge_factors
            )

            return HorseTrendScore(
                horse_name=horse_name,
                trend_scores=trend_scores,
                overall_trend_score=overall_score,
                matching_patterns=matching_patterns,
                edge_factors=edge_factors,
                confidence=confidence,
                recommendation=recommendation,
            )

        except Exception as e:
            logger.error(f"Error scoring horse trends for {horse_name}: {e}")
            return HorseTrendScore(
                horse_name=horse_name,
                trend_scores={},
                overall_trend_score=0.5,
                matching_patterns=[],
                edge_factors=[],
                confidence=0.0,
                recommendation="INSUFFICIENT_DATA",
            )

    def _filter_relevant_races(
        self, race_data: Dict[str, Any], historical_races: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter historical races relevant to current race type."""
        relevant = []

        target_distance = race_data.get("distance", "")
        target_surface = race_data.get("surface", "")
        target_course = race_data.get("course", "")
        target_race_type = race_data.get("race_type", "")

        for race in historical_races:
            # Match by distance (within 200m)
            if self._is_similar_distance(race.get("distance", ""), target_distance):
                # Match by surface
                if race.get("surface", "") == target_surface or not target_surface:
                    # Prefer same course, but include similar courses
                    course_match = race.get(
                        "course", ""
                    ) == target_course or self._is_similar_course(
                        race.get("course", ""), target_course
                    )

                    # Match race type
                    type_match = race.get(
                        "race_type", ""
                    ) == target_race_type or self._is_similar_race_type(
                        race.get("race_type", ""), target_race_type
                    )

                    if course_match and type_match:
                        relevant.append(race)

        # Sort by relevance (same course and exact distance first)
        relevant.sort(
            key=lambda r: (
                r.get("course", "") == target_course,
                r.get("distance", "") == target_distance,
                r.get("race_date", ""),
            ),
            reverse=True,
        )

        return relevant[:50]  # Limit to most relevant 50 races

    def _analyze_age_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze age-related winning trends."""
        age_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner and "age" in winner:
                age_data.append(winner["age"])

        if len(age_data) < self.min_sample_size:
            return []

        trends = []

        # Analyze age distribution
        age_counter = Counter(age_data)
        total_winners = len(age_data)

        for age, count in age_counter.most_common():
            percentage = (count / total_winners) * 100
            if percentage >= 20:  # Only include significant patterns
                confidence = min(count / 10, 1.0)  # Higher confidence with more samples
                edge_value = max(0, (percentage - 20) / 80)  # Edge above random chance

                trends.append(
                    RaceTrend(
                        trend_type="age",
                        pattern=f"{count}/{total_winners} winners were aged {age}",
                        percentage=percentage,
                        sample_size=total_winners,
                        confidence=confidence,
                        edge_value=edge_value,
                        last_updated=datetime.now().isoformat(),
                    )
                )

        # Analyze age ranges
        young_horses = len([age for age in age_data if age <= 4])
        mature_horses = len([age for age in age_data if 5 <= age <= 7])
        veteran_horses = len([age for age in age_data if age >= 8])

        if young_horses / total_winners >= 0.6:
            trends.append(
                RaceTrend(
                    trend_type="age_range",
                    pattern=f"{young_horses}/{total_winners} winners were 4 years old or younger",
                    percentage=(young_horses / total_winners) * 100,
                    sample_size=total_winners,
                    confidence=min(young_horses / 8, 1.0),
                    edge_value=(young_horses / total_winners - 0.4) * 2.5,
                    last_updated=datetime.now().isoformat(),
                )
            )

        return trends

    def _analyze_weight_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze weight-related winning trends."""
        weight_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner and "weight" in winner:
                # Convert weight to standardized format (pounds)
                weight = self._normalize_weight(winner["weight"])
                if weight:
                    weight_data.append(weight)

        if len(weight_data) < self.min_sample_size:
            return []

        trends = []
        total_winners = len(weight_data)

        # Analyze weight ranges
        light_weight = len([w for w in weight_data if w <= 120])  # 120 lbs or less
        medium_weight = len([w for w in weight_data if 121 <= w <= 130])
        heavy_weight = len([w for w in weight_data if w >= 131])

        categories = [
            ("light", light_weight, "120 lbs or less"),
            ("medium", medium_weight, "121-130 lbs"),
            ("heavy", heavy_weight, "131 lbs or more"),
        ]

        for category, count, description in categories:
            if count > 0:
                percentage = (count / total_winners) * 100
                if percentage >= 25:  # Significant pattern
                    confidence = min(count / 8, 1.0)
                    edge_value = max(
                        0, (percentage - 33.33) / 66.67
                    )  # Edge above random

                    trends.append(
                        RaceTrend(
                            trend_type="weight",
                            pattern=f"{count}/{total_winners} winners carried {description}",
                            percentage=percentage,
                            sample_size=total_winners,
                            confidence=confidence,
                            edge_value=edge_value,
                            last_updated=datetime.now().isoformat(),
                        )
                    )

        return trends

    def _analyze_draw_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze draw/stall position trends."""
        draw_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner and "draw" in winner:
                draw_data.append(winner["draw"])

        if len(draw_data) < self.min_sample_size:
            return []

        trends = []
        total_winners = len(draw_data)

        # Analyze draw bias
        low_draws = len([d for d in draw_data if d <= 5])
        middle_draws = len([d for d in draw_data if 6 <= d <= 10])
        high_draws = len([d for d in draw_data if d >= 11])

        categories = [
            ("low", low_draws, "low draws (1-5)"),
            ("middle", middle_draws, "middle draws (6-10)"),
            ("high", high_draws, "high draws (11+)"),
        ]

        for category, count, description in categories:
            if count > 0:
                percentage = (count / total_winners) * 100
                if percentage >= 40:  # Significant draw bias
                    confidence = min(count / 6, 1.0)
                    edge_value = max(0, (percentage - 33.33) / 66.67)

                    trends.append(
                        RaceTrend(
                            trend_type="draw",
                            pattern=f"{count}/{total_winners} winners came from {description}",
                            percentage=percentage,
                            sample_size=total_winners,
                            confidence=confidence,
                            edge_value=edge_value,
                            last_updated=datetime.now().isoformat(),
                        )
                    )

        return trends

    def _analyze_form_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze form-related trends."""
        trends = []

        # Analyze last run trends
        last_run_data = []
        last_run_wins = 0
        days_since_last_run = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner:
                if winner.get("last_run_result") == "win":
                    last_run_wins += 1

                if "days_since_last_run" in winner:
                    days_since_last_run.append(winner["days_since_last_run"])

                last_run_data.append(winner)

        total_winners = len(last_run_data)

        if total_winners >= self.min_sample_size:
            # Last run win/loss pattern
            non_winners_last_run = total_winners - last_run_wins
            if non_winners_last_run >= total_winners * 0.7:
                percentage = (non_winners_last_run / total_winners) * 100
                trends.append(
                    RaceTrend(
                        trend_type="last_run",
                        pattern=f"{non_winners_last_run}/{total_winners} winners did not win their last run",
                        percentage=percentage,
                        sample_size=total_winners,
                        confidence=min(non_winners_last_run / 8, 1.0),
                        edge_value=(percentage - 60) / 40,
                        last_updated=datetime.now().isoformat(),
                    )
                )

            # Days since last run
            if days_since_last_run:
                recent_runs = len([d for d in days_since_last_run if d <= 30])
                if recent_runs >= len(days_since_last_run) * 0.8:
                    percentage = (recent_runs / len(days_since_last_run)) * 100
                    trends.append(
                        RaceTrend(
                            trend_type="recency",
                            pattern=f"{recent_runs}/{len(days_since_last_run)} winners ran within 30 days",
                            percentage=percentage,
                            sample_size=len(days_since_last_run),
                            confidence=min(recent_runs / 8, 1.0),
                            edge_value=(percentage - 60) / 40,
                            last_updated=datetime.now().isoformat(),
                        )
                    )

        return trends

    def _analyze_price_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze betting price/odds trends."""
        price_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner and "odds" in winner:
                price_data.append(winner["odds"])

        if len(price_data) < self.min_sample_size:
            return []

        trends = []
        total_winners = len(price_data)

        # Analyze price ranges
        favourites = len([p for p in price_data if p <= 3.0])
        second_choices = len([p for p in price_data if 3.1 <= p <= 6.0])
        outsiders = len([p for p in price_data if p > 6.0])

        categories = [
            ("favourites", favourites, "favourites (odds 3.0 or less)"),
            ("second_choices", second_choices, "second choices (odds 3.1-6.0)"),
            ("outsiders", outsiders, "outsiders (odds over 6.0)"),
        ]

        for category, count, description in categories:
            if count > 0:
                percentage = (count / total_winners) * 100
                if percentage >= 25:
                    confidence = min(count / 6, 1.0)
                    edge_value = max(0, (percentage - 20) / 80)

                    trends.append(
                        RaceTrend(
                            trend_type="price",
                            pattern=f"{count}/{total_winners} winners were {description}",
                            percentage=percentage,
                            sample_size=total_winners,
                            confidence=confidence,
                            edge_value=edge_value,
                            last_updated=datetime.now().isoformat(),
                        )
                    )

        return trends

    def _analyze_seasonal_trends(self, races: List[Dict[str, Any]]) -> List[RaceTrend]:
        """Analyze seasonal and timing trends."""
        trends = []
        seasonal_data = []

        for race in races:
            race_date = race.get("race_date")
            if race_date:
                # Extract month from date
                if isinstance(race_date, str):
                    try:
                        date_obj = datetime.fromisoformat(
                            race_date.replace("Z", "+00:00")
                        )
                        seasonal_data.append(date_obj.month)
                    except:
                        continue
                elif hasattr(race_date, "month"):
                    seasonal_data.append(race_date.month)

        if len(seasonal_data) >= self.min_sample_size:
            month_counter = Counter(seasonal_data)
            total_races = len(seasonal_data)

            # Find seasonal patterns
            spring_months = sum(month_counter[m] for m in [3, 4, 5])
            summer_months = sum(month_counter[m] for m in [6, 7, 8])
            autumn_months = sum(month_counter[m] for m in [9, 10, 11])
            winter_months = sum(month_counter[m] for m in [12, 1, 2])

            seasons = [
                ("spring", spring_months, "spring months (Mar-May)"),
                ("summer", summer_months, "summer months (Jun-Aug)"),
                ("autumn", autumn_months, "autumn months (Sep-Nov)"),
                ("winter", winter_months, "winter months (Dec-Feb)"),
            ]

            for season, count, description in seasons:
                if count > 0:
                    percentage = (count / total_races) * 100
                    if percentage >= 30:  # Seasonal bias
                        confidence = min(count / 6, 1.0)
                        edge_value = max(0, (percentage - 25) / 75)

                        trends.append(
                            RaceTrend(
                                trend_type="seasonal",
                                pattern=f"{count}/{total_races} races occurred in {description}",
                                percentage=percentage,
                                sample_size=total_races,
                                confidence=confidence,
                                edge_value=edge_value,
                                last_updated=datetime.now().isoformat(),
                            )
                        )

        return trends

    def _analyze_course_form_trends(
        self, races: List[Dict[str, Any]]
    ) -> List[RaceTrend]:
        """Analyze course form trends."""
        trends = []
        course_form_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner:
                course_wins = winner.get("course_wins", 0)
                course_runs = winner.get("course_runs", 0)
                course_form_data.append(
                    {
                        "wins": course_wins,
                        "runs": course_runs,
                        "has_course_form": course_runs > 0,
                        "has_course_win": course_wins > 0,
                    }
                )

        if len(course_form_data) >= self.min_sample_size:
            total_winners = len(course_form_data)

            # Previous course form
            with_course_form = len(
                [d for d in course_form_data if d["has_course_form"]]
            )
            with_course_wins = len([d for d in course_form_data if d["has_course_win"]])

            if with_course_form >= total_winners * 0.4:
                percentage = (with_course_form / total_winners) * 100
                trends.append(
                    RaceTrend(
                        trend_type="course_form",
                        pattern=f"{with_course_form}/{total_winners} winners had previous course form",
                        percentage=percentage,
                        sample_size=total_winners,
                        confidence=min(with_course_form / 8, 1.0),
                        edge_value=(percentage - 30) / 70,
                        last_updated=datetime.now().isoformat(),
                    )
                )

        return trends

    def _analyze_distance_form_trends(
        self, races: List[Dict[str, Any]]
    ) -> List[RaceTrend]:
        """Analyze distance form trends."""
        trends = []
        distance_form_data = []

        for race in races:
            winner = self._get_race_winner(race)
            if winner:
                distance_wins = winner.get("distance_wins", 0)
                distance_runs = winner.get("distance_runs", 0)
                distance_form_data.append(
                    {
                        "wins": distance_wins,
                        "runs": distance_runs,
                        "has_distance_form": distance_runs > 0,
                        "has_distance_win": distance_wins > 0,
                    }
                )

        if len(distance_form_data) >= self.min_sample_size:
            total_winners = len(distance_form_data)

            # Previous distance form
            with_distance_form = len(
                [d for d in distance_form_data if d["has_distance_form"]]
            )
            with_distance_wins = len(
                [d for d in distance_form_data if d["has_distance_win"]]
            )

            if with_distance_form >= total_winners * 0.6:
                percentage = (with_distance_form / total_winners) * 100
                trends.append(
                    RaceTrend(
                        trend_type="distance_form",
                        pattern=f"{with_distance_form}/{total_winners} winners had previous distance form",
                        percentage=percentage,
                        sample_size=total_winners,
                        confidence=min(with_distance_form / 8, 1.0),
                        edge_value=(percentage - 50) / 50,
                        last_updated=datetime.now().isoformat(),
                    )
                )

            if with_distance_wins >= total_winners * 0.5:
                percentage = (with_distance_wins / total_winners) * 100
                trends.append(
                    RaceTrend(
                        trend_type="distance_wins",
                        pattern=f"{with_distance_wins}/{total_winners} winners had previous distance wins",
                        percentage=percentage,
                        sample_size=total_winners,
                        confidence=min(with_distance_wins / 8, 1.0),
                        edge_value=(percentage - 40) / 60,
                        last_updated=datetime.now().isoformat(),
                    )
                )

        return trends

    def _score_age_trends(
        self, horse_data: Dict[str, Any], age_trends: List[RaceTrend]
    ) -> float:
        """Score horse against age trends."""
        horse_age = horse_data.get("age", 0)
        score = 0.5  # Default neutral score

        for trend in age_trends:
            if trend.confidence >= self.confidence_threshold:
                if "aged" in trend.pattern:
                    # Extract age from pattern
                    age_match = re.search(r"aged (\d+)", trend.pattern)
                    if age_match and int(age_match.group(1)) == horse_age:
                        score += trend.edge_value * trend.confidence

                elif "4 years old or younger" in trend.pattern and horse_age <= 4:
                    score += trend.edge_value * trend.confidence
                elif "5-7" in trend.pattern and 5 <= horse_age <= 7:
                    score += trend.edge_value * trend.confidence
                elif "8" in trend.pattern and horse_age >= 8:
                    score += trend.edge_value * trend.confidence

        return min(max(score, 0.0), 1.0)

    def _score_weight_trends(
        self, horse_data: Dict[str, Any], weight_trends: List[RaceTrend]
    ) -> float:
        """Score horse against weight trends."""
        horse_weight = self._normalize_weight(horse_data.get("weight", 0))
        if not horse_weight:
            return 0.5

        score = 0.5

        for trend in weight_trends:
            if trend.confidence >= self.confidence_threshold:
                if "120 lbs or less" in trend.pattern and horse_weight <= 120:
                    score += trend.edge_value * trend.confidence
                elif "121-130 lbs" in trend.pattern and 121 <= horse_weight <= 130:
                    score += trend.edge_value * trend.confidence
                elif "131 lbs or more" in trend.pattern and horse_weight >= 131:
                    score += trend.edge_value * trend.confidence

        return min(max(score, 0.0), 1.0)

    def _score_draw_trends(
        self, horse_data: Dict[str, Any], draw_trends: List[RaceTrend]
    ) -> float:
        """Score horse against draw trends."""
        horse_draw = horse_data.get("draw", 0)
        if not horse_draw:
            return 0.5

        score = 0.5

        for trend in draw_trends:
            if trend.confidence >= self.confidence_threshold:
                if "low draws" in trend.pattern and horse_draw <= 5:
                    score += trend.edge_value * trend.confidence
                elif "middle draws" in trend.pattern and 6 <= horse_draw <= 10:
                    score += trend.edge_value * trend.confidence
                elif "high draws" in trend.pattern and horse_draw >= 11:
                    score += trend.edge_value * trend.confidence

        return min(max(score, 0.0), 1.0)

    def _score_form_trends(
        self, horse_data: Dict[str, Any], form_trends: List[RaceTrend]
    ) -> float:
        """Score horse against form trends."""
        score = 0.5

        for trend in form_trends:
            if trend.confidence >= self.confidence_threshold:
                if "did not win their last run" in trend.pattern:
                    if horse_data.get("last_run_result") != "win":
                        score += trend.edge_value * trend.confidence

                if "ran within 30 days" in trend.pattern:
                    days_since = horse_data.get("days_since_last_run", 999)
                    if days_since <= 30:
                        score += trend.edge_value * trend.confidence

        return min(max(score, 0.0), 1.0)

    def _score_price_trends(
        self, horse_data: Dict[str, Any], price_trends: List[RaceTrend]
    ) -> float:
        """Score horse against price trends."""
        horse_odds = horse_data.get("odds", 10.0)
        score = 0.5

        for trend in price_trends:
            if trend.confidence >= self.confidence_threshold:
                if "favourites" in trend.pattern and horse_odds <= 3.0:
                    score += trend.edge_value * trend.confidence
                elif "second choices" in trend.pattern and 3.1 <= horse_odds <= 6.0:
                    score += trend.edge_value * trend.confidence
                elif "outsiders" in trend.pattern and horse_odds > 6.0:
                    score += trend.edge_value * trend.confidence

        return min(max(score, 0.0), 1.0)

    def _score_seasonal_trends(
        self, horse_data: Dict[str, Any], seasonal_trends: List[RaceTrend]
    ) -> float:
        """Score horse against seasonal trends."""
        # This would be based on current race date vs historical patterns
        # For now, return neutral score
        return 0.5

    def _score_course_form_trends(
        self, horse_data: Dict[str, Any], course_form_trends: List[RaceTrend]
    ) -> float:
        """Score horse against course form trends."""
        score = 0.5

        has_course_form = horse_data.get("course_runs", 0) > 0
        has_course_wins = horse_data.get("course_wins", 0) > 0

        for trend in course_form_trends:
            if trend.confidence >= self.confidence_threshold:
                if "previous course form" in trend.pattern and has_course_form:
                    score += trend.edge_value * trend.confidence
                if "previous course win" in trend.pattern and has_course_wins:
                    score += (
                        trend.edge_value * trend.confidence * 1.2
                    )  # Extra bonus for wins

        return min(max(score, 0.0), 1.0)

    def _score_distance_form_trends(
        self, horse_data: Dict[str, Any], distance_form_trends: List[RaceTrend]
    ) -> float:
        """Score horse against distance form trends."""
        score = 0.5

        has_distance_form = horse_data.get("distance_runs", 0) > 0
        has_distance_wins = horse_data.get("distance_wins", 0) > 0

        for trend in distance_form_trends:
            if trend.confidence >= self.confidence_threshold:
                if "previous distance form" in trend.pattern and has_distance_form:
                    score += trend.edge_value * trend.confidence
                if "previous distance wins" in trend.pattern and has_distance_wins:
                    score += (
                        trend.edge_value * trend.confidence * 1.3
                    )  # Extra bonus for wins

        return min(max(score, 0.0), 1.0)

    # Helper methods
    def _get_race_winner(self, race: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract winner information from race data."""
        if "winner" in race:
            return race["winner"]

        if "horses" in race:
            for horse in race["horses"]:
                if horse.get("finish_position") == 1:
                    return horse

        return None

    def _normalize_weight(self, weight: Any) -> Optional[float]:
        """Normalize weight to pounds."""
        if isinstance(weight, (int, float)):
            return float(weight)

        if isinstance(weight, str):
            # Parse weight strings like "9st 2lbs" or "130 lbs"
            if "st" in weight:
                # British stone format
                parts = weight.replace("lbs", "").replace("lb", "").split("st")
                if len(parts) == 2:
                    stones = float(parts[0].strip())
                    pounds = float(parts[1].strip()) if parts[1].strip() else 0
                    return stones * 14 + pounds
            else:
                # Extract numeric value
                import re

                match = re.search(r"(\d+\.?\d*)", weight)
                if match:
                    return float(match.group(1))

        return None

    def _is_similar_distance(self, dist1: str, dist2: str) -> bool:
        """Check if distances are similar."""
        # Simple similarity check - could be enhanced
        return dist1 == dist2 or abs(len(dist1) - len(dist2)) <= 2

    def _is_similar_course(self, course1: str, course2: str) -> bool:
        """Check if courses are similar."""
        return (
            course1 == course2
            or course1.lower() in course2.lower()
            or course2.lower() in course1.lower()
        )

    def _is_similar_race_type(self, type1: str, type2: str) -> bool:
        """Check if race types are similar."""
        return (
            type1 == type2
            or type1.lower() in type2.lower()
            or type2.lower() in type1.lower()
        )

    def _calculate_overall_edge_score(self, trends: List[RaceTrend]) -> float:
        """Calculate overall edge score from all trends."""
        if not trends:
            return 0.0

        significant_trends = [
            t for t in trends if t.confidence >= self.confidence_threshold
        ]
        if not significant_trends:
            return 0.0

        total_edge = sum(t.edge_value * t.confidence for t in significant_trends)
        return min(total_edge / len(significant_trends), 1.0)

    def _create_empty_trends(self, race_data: Dict[str, Any]) -> RaceAnalysisTrends:
        """Create empty trends object for insufficient data."""
        return RaceAnalysisTrends(
            race_name=race_data.get("race_name", "Unknown"),
            race_type=race_data.get("race_type", "unknown"),
            distance=race_data.get("distance", "unknown"),
            course=race_data.get("course", "unknown"),
            surface=race_data.get("surface", "unknown"),
            age_trends=[],
            weight_trends=[],
            draw_trends=[],
            form_trends=[],
            price_trends=[],
            seasonal_trends=[],
            course_form_trends=[],
            distance_form_trends=[],
            overall_edge_score=0.0,
            total_patterns_found=0,
            analysis_date=datetime.now().isoformat(),
        )

    def _identify_matching_patterns(
        self, horse_data: Dict[str, Any], race_trends: RaceAnalysisTrends
    ) -> List[str]:
        """Identify patterns that the horse matches."""
        patterns = []

        # Check each trend category
        all_trends = (
            race_trends.age_trends
            + race_trends.weight_trends
            + race_trends.draw_trends
            + race_trends.form_trends
            + race_trends.price_trends
            + race_trends.course_form_trends
            + race_trends.distance_form_trends
        )

        for trend in all_trends:
            if trend.confidence >= self.confidence_threshold:
                # Check if horse matches this trend pattern
                matches = self._horse_matches_trend(horse_data, trend)
                if matches:
                    patterns.append(f"{trend.trend_type}: {trend.pattern}")

        return patterns

    def _horse_matches_trend(
        self, horse_data: Dict[str, Any], trend: RaceTrend
    ) -> bool:
        """Check if horse matches a specific trend."""
        # Simplified matching logic - could be enhanced
        if trend.trend_type == "age":
            horse_age = horse_data.get("age", 0)
            return str(horse_age) in trend.pattern
        elif trend.trend_type == "weight":
            horse_weight = self._normalize_weight(horse_data.get("weight", 0))
            if horse_weight:
                if "120 lbs or less" in trend.pattern:
                    return horse_weight <= 120
                elif "121-130 lbs" in trend.pattern:
                    return 121 <= horse_weight <= 130
                elif "131 lbs or more" in trend.pattern:
                    return horse_weight >= 131
        # Add more matching logic for other trend types...

        return False

    def _identify_edge_factors(
        self, trend_scores: Dict[str, float], race_trends: RaceAnalysisTrends
    ) -> List[str]:
        """Identify factors that give betting edge."""
        edge_factors = []

        for category, score in trend_scores.items():
            if score >= 0.7:  # Strong positive score
                edge_factors.append(f"Strong {category} trend match")
            elif score >= 0.6:
                edge_factors.append(f"Good {category} trend match")

        return edge_factors

    def _calculate_trend_confidence(
        self, trend_scores: Dict[str, float], matching_patterns: List[str]
    ) -> float:
        """Calculate overall confidence in trend analysis."""
        strong_scores = len([s for s in trend_scores.values() if s >= 0.7])
        total_patterns = len(matching_patterns)

        # Base confidence on number of strong trend matches
        confidence = (strong_scores / max(len(trend_scores), 1)) * 0.7
        confidence += (total_patterns / 10) * 0.3  # Bonus for multiple pattern matches

        return min(confidence, 1.0)

    def _generate_trend_recommendation(
        self, overall_score: float, confidence: float, edge_factors: List[str]
    ) -> str:
        """Generate betting recommendation based on trends."""
        if confidence < 0.3:
            return "INSUFFICIENT_DATA"

        if overall_score >= 0.75 and confidence >= 0.7:
            return "STRONG"
        elif overall_score >= 0.6 and confidence >= 0.6:
            return "MODERATE"
        elif overall_score >= 0.4:
            return "WEAK"
        else:
            return "AVOID"

    def export_trends_analysis(self, race_trends: RaceAnalysisTrends) -> Dict[str, Any]:
        """Export trends analysis for integration with other systems."""
        return {
            "race_info": {
                "name": race_trends.race_name,
                "type": race_trends.race_type,
                "distance": race_trends.distance,
                "course": race_trends.course,
                "surface": race_trends.surface,
            },
            "trends_summary": {
                "overall_edge_score": race_trends.overall_edge_score,
                "total_patterns_found": race_trends.total_patterns_found,
                "analysis_date": race_trends.analysis_date,
            },
            "trend_categories": {
                "age_trends": [asdict(t) for t in race_trends.age_trends],
                "weight_trends": [asdict(t) for t in race_trends.weight_trends],
                "draw_trends": [asdict(t) for t in race_trends.draw_trends],
                "form_trends": [asdict(t) for t in race_trends.form_trends],
                "price_trends": [asdict(t) for t in race_trends.price_trends],
                "seasonal_trends": [asdict(t) for t in race_trends.seasonal_trends],
                "course_form_trends": [
                    asdict(t) for t in race_trends.course_form_trends
                ],
                "distance_form_trends": [
                    asdict(t) for t in race_trends.distance_form_trends
                ],
            },
            "actionable_insights": self._generate_actionable_insights(race_trends),
        }

    def _generate_actionable_insights(
        self, race_trends: RaceAnalysisTrends
    ) -> List[str]:
        """Generate actionable insights from trends analysis."""
        insights = []

        all_trends = (
            race_trends.age_trends
            + race_trends.weight_trends
            + race_trends.draw_trends
            + race_trends.form_trends
            + race_trends.price_trends
            + race_trends.course_form_trends
            + race_trends.distance_form_trends
        )

        strong_trends = [
            t for t in all_trends if t.confidence >= 0.7 and t.edge_value >= 0.2
        ]

        for trend in strong_trends:
            insights.append(
                f"EDGE: {trend.pattern} (confidence: {trend.confidence:.1%})"
            )

        if race_trends.overall_edge_score >= 0.3:
            insights.append(
                f"Race shows overall betting edge: {race_trends.overall_edge_score:.1%}"
            )

        return insights
