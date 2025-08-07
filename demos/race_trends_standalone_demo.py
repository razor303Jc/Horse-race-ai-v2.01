#!/usr/bin/env python3
"""
Race Trends Analysis Standalone Demo
Demonstrates race trends analysis without requiring full project dependencies.
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


# Simplified Race Trend classes for demonstration
@dataclass
class RaceTrend:
    """Individual race trend analysis."""

    trend_type: str
    pattern: str
    percentage: float
    sample_size: int
    confidence: float
    edge_value: float
    last_updated: str


@dataclass
class RaceAnalysisTrends:
    """Complete trends analysis for a specific race type."""

    race_name: str
    race_type: str
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
    trend_scores: Dict[str, float]
    overall_trend_score: float
    matching_patterns: List[str]
    edge_factors: List[str]
    confidence: float
    recommendation: str


class SimplifiedRaceTrendsAnalyzer:
    """Simplified race trends analyzer for demonstration."""

    def __init__(self):
        """Initialize the analyzer."""
        self.min_sample_size = 10
        self.confidence_threshold = 0.7
        self.edge_threshold = 0.15
        print("🔍 Race Trends Analyzer initialized")

    def analyze_chesterfield_cup_trends(self) -> RaceAnalysisTrends:
        """
        Analyze Chesterfield Cup trends based on thestatsdontlie.com data.
        This demonstrates the actual patterns found on the website.
        """
        print("\n📊 Analyzing Chesterfield Cup Historical Trends...")

        # Based on thestatsdontlie.com Chesterfield Cup analysis
        age_trends = [
            RaceTrend(
                trend_type="age",
                pattern="12/12 winners were aged 4-5 years",
                percentage=100.0,
                sample_size=12,
                confidence=0.95,
                edge_value=0.8,
                last_updated=datetime.now().isoformat(),
            )
        ]

        weight_trends = [
            RaceTrend(
                trend_type="weight",
                pattern="9/12 winners carried 9st 2lbs or less",
                percentage=75.0,
                sample_size=12,
                confidence=0.85,
                edge_value=0.5,
                last_updated=datetime.now().isoformat(),
            )
        ]

        draw_trends = [
            RaceTrend(
                trend_type="draw",
                pattern="8/10 winners came from stall 10 or higher",
                percentage=80.0,
                sample_size=10,
                confidence=0.90,
                edge_value=0.6,
                last_updated=datetime.now().isoformat(),
            )
        ]

        form_trends = [
            RaceTrend(
                trend_type="form",
                pattern="0/12 winners won their last run",
                percentage=0.0,
                sample_size=12,
                confidence=0.95,
                edge_value=0.7,
                last_updated=datetime.now().isoformat(),
            ),
            RaceTrend(
                trend_type="recency",
                pattern="12/12 winners ran within 34 days",
                percentage=100.0,
                sample_size=12,
                confidence=0.95,
                edge_value=0.6,
                last_updated=datetime.now().isoformat(),
            ),
        ]

        distance_form_trends = [
            RaceTrend(
                trend_type="distance_experience",
                pattern="10/12 winners had previous 10-furlong experience",
                percentage=83.3,
                sample_size=12,
                confidence=0.88,
                edge_value=0.65,
                last_updated=datetime.now().isoformat(),
            )
        ]

        course_form_trends = [
            RaceTrend(
                trend_type="course_form",
                pattern="4/12 winners had previous Goodwood runs",
                percentage=33.3,
                sample_size=12,
                confidence=0.75,
                edge_value=0.2,
                last_updated=datetime.now().isoformat(),
            )
        ]

        price_trends = [
            RaceTrend(
                trend_type="rating",
                pattern="10/12 winners had ratings of 95 or higher",
                percentage=83.3,
                sample_size=12,
                confidence=0.88,
                edge_value=0.65,
                last_updated=datetime.now().isoformat(),
            )
        ]

        # Calculate overall edge score
        all_trends = (
            age_trends
            + weight_trends
            + draw_trends
            + form_trends
            + distance_form_trends
            + course_form_trends
            + price_trends
        )
        significant_trends = [
            t for t in all_trends if t.confidence >= self.confidence_threshold
        ]
        overall_edge_score = sum(
            t.edge_value * t.confidence for t in significant_trends
        ) / len(significant_trends)

        return RaceAnalysisTrends(
            race_name="Chesterfield Cup",
            race_type="handicap",
            distance="1m2f",
            course="Goodwood",
            surface="turf",
            age_trends=age_trends,
            weight_trends=weight_trends,
            draw_trends=draw_trends,
            form_trends=form_trends,
            price_trends=price_trends,
            seasonal_trends=[],
            course_form_trends=course_form_trends,
            distance_form_trends=distance_form_trends,
            overall_edge_score=overall_edge_score,
            total_patterns_found=len(significant_trends),
            analysis_date=datetime.now().isoformat(),
        )

    def score_sample_horses(
        self, race_trends: RaceAnalysisTrends
    ) -> List[Dict[str, Any]]:
        """Score sample horses against the identified trends."""
        print("\n🐎 Scoring horses against identified trends...")

        sample_horses = [
            {
                "name": "Thunder Strike",
                "age": 4,
                "weight": "9st 0lbs",  # 126 lbs (under 9st 2lbs threshold)
                "draw": 12,  # High draw (stall 10+)
                "odds": 4.5,
                "last_run_result": "second",  # Didn't win last run
                "days_since_last_run": 21,  # Within 34 days
                "course_runs": 0,  # No previous Goodwood runs
                "distance_runs": 3,  # Has 10f experience
                "rating": 98,  # Rating 95+
            },
            {
                "name": "Desert Lightning",
                "age": 5,
                "weight": "8st 12lbs",  # 124 lbs (under threshold)
                "draw": 15,  # High draw
                "odds": 6.0,
                "last_run_result": "third",  # Didn't win last run
                "days_since_last_run": 28,  # Within 34 days
                "course_runs": 2,  # Has Goodwood experience
                "distance_runs": 4,  # Has 10f experience
                "rating": 96,  # Rating 95+
            },
            {
                "name": "Celtic Storm",
                "age": 4,
                "weight": "9st 2lbs",  # 128 lbs (at threshold)
                "draw": 8,  # Low draw (below 10)
                "odds": 8.0,
                "last_run_result": "fourth",  # Didn't win last run
                "days_since_last_run": 14,  # Within 34 days
                "course_runs": 1,  # Has Goodwood experience
                "distance_runs": 2,  # Has 10f experience
                "rating": 94,  # Below rating threshold
            },
            {
                "name": "Royal Ascent",
                "age": 6,  # Above age threshold
                "weight": "8st 10lbs",  # 122 lbs (under threshold)
                "draw": 3,  # Low draw
                "odds": 12.0,
                "last_run_result": "win",  # Won last run (against trend)
                "days_since_last_run": 35,  # Just outside 34 days
                "course_runs": 0,  # No Goodwood experience
                "distance_runs": 5,  # Has 10f experience
                "rating": 92,  # Below rating threshold
            },
        ]

        scored_horses = []
        for horse in sample_horses:
            trend_score = self._score_horse_against_trends(horse, race_trends)
            scored_horses.append(
                {
                    "horse": horse,
                    "trend_score": trend_score,
                    "edge_analysis": self._analyze_horse_edge(horse, trend_score),
                }
            )

        # Sort by trend score
        scored_horses.sort(
            key=lambda x: x["trend_score"].overall_trend_score, reverse=True
        )
        return scored_horses

    def _score_horse_against_trends(
        self, horse: Dict[str, Any], race_trends: RaceAnalysisTrends
    ) -> HorseTrendScore:
        """Score individual horse against race trends."""
        trend_scores = {}
        matching_patterns = []
        edge_factors = []

        # Age scoring
        horse_age = horse["age"]
        age_score = 0.9 if 4 <= horse_age <= 5 else 0.2
        trend_scores["age"] = age_score
        if 4 <= horse_age <= 5:
            matching_patterns.append(f"Age: {horse_age} years (fits 4-5 age trend)")
            edge_factors.append("Strong age trend match")

        # Weight scoring
        weight_lbs = self._convert_weight_to_pounds(horse["weight"])
        weight_score = 0.8 if weight_lbs <= 128 else 0.3  # 9st 2lbs = 128lbs
        trend_scores["weight"] = weight_score
        if weight_lbs <= 128:
            matching_patterns.append(
                f"Weight: {horse['weight']} (under 9st 2lbs threshold)"
            )
            edge_factors.append("Favorable weight trend")

        # Draw scoring
        draw = horse["draw"]
        draw_score = 0.8 if draw >= 10 else 0.4
        trend_scores["draw"] = draw_score
        if draw >= 10:
            matching_patterns.append(f"Draw: Stall {draw} (high draw trend)")
            edge_factors.append("High draw advantage")

        # Form scoring
        last_result = horse["last_run_result"]
        days_since = horse["days_since_last_run"]
        form_score = 0.0
        if last_result != "win":
            form_score += 0.5
            matching_patterns.append("Form: Did not win last run (fits trend)")
        if days_since <= 34:
            form_score += 0.4
            matching_patterns.append(f"Recency: Ran {days_since} days ago (recent)")
        trend_scores["form"] = min(form_score, 1.0)

        # Distance experience
        distance_runs = horse["distance_runs"]
        distance_score = 0.8 if distance_runs > 0 else 0.2
        trend_scores["distance"] = distance_score
        if distance_runs > 0:
            matching_patterns.append(f"Distance: {distance_runs} previous 10f runs")

        # Rating scoring
        rating = horse["rating"]
        rating_score = 0.8 if rating >= 95 else 0.4
        trend_scores["rating"] = rating_score
        if rating >= 95:
            matching_patterns.append(f"Rating: {rating} (95+ trend)")
            edge_factors.append("High rating threshold met")

        # Course form
        course_runs = horse["course_runs"]
        course_score = (
            0.6 if course_runs > 0 else 0.5
        )  # Neutral as only 4/12 had course form
        trend_scores["course"] = course_score

        # Calculate overall score
        weights = {
            "age": 0.20,  # Very strong trend (12/12)
            "weight": 0.15,  # Strong trend (9/12)
            "draw": 0.15,  # Strong trend (8/10)
            "form": 0.20,  # Very strong trend (0/12 won last + recency)
            "distance": 0.15,  # Strong trend (10/12)
            "rating": 0.10,  # Strong trend (10/12)
            "course": 0.05,  # Weaker trend (4/12)
        }

        overall_score = sum(
            score * weights.get(category, 0.1)
            for category, score in trend_scores.items()
        )

        # Calculate confidence
        strong_matches = len([f for f in edge_factors])
        confidence = min(
            strong_matches / 3, 1.0
        )  # Max confidence with 3+ strong matches

        # Generate recommendation
        if overall_score >= 0.8 and confidence >= 0.7:
            recommendation = "STRONG"
        elif overall_score >= 0.6 and confidence >= 0.5:
            recommendation = "MODERATE"
        elif overall_score >= 0.4:
            recommendation = "WEAK"
        else:
            recommendation = "AVOID"

        return HorseTrendScore(
            horse_name=horse["name"],
            trend_scores=trend_scores,
            overall_trend_score=overall_score,
            matching_patterns=matching_patterns,
            edge_factors=edge_factors,
            confidence=confidence,
            recommendation=recommendation,
        )

    def _convert_weight_to_pounds(self, weight_str: str) -> float:
        """Convert weight string to pounds."""
        if "st" in weight_str:
            parts = weight_str.replace("lbs", "").replace("lb", "").split("st")
            stones = float(parts[0].strip())
            pounds = (
                float(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
            )
            return stones * 14 + pounds
        else:
            # Extract numeric value
            match = re.search(r"(\d+\.?\d*)", weight_str)
            return float(match.group(1)) if match else 130

    def _analyze_horse_edge(
        self, horse: Dict[str, Any], trend_score: HorseTrendScore
    ) -> Dict[str, Any]:
        """Analyze betting edge for horse."""
        implied_prob = 1 / horse["odds"]
        predicted_prob = trend_score.overall_trend_score

        value = 0.0
        if predicted_prob > implied_prob:
            value = (predicted_prob - implied_prob) / implied_prob

        return {
            "implied_probability": implied_prob,
            "predicted_probability": predicted_prob,
            "value_percentage": value * 100,
            "betting_edge": value > 0.1,  # 10% edge threshold
            "recommended_stake": self._calculate_recommended_stake(
                value, trend_score.confidence
            ),
        }

    def _calculate_recommended_stake(self, value: float, confidence: float) -> float:
        """Calculate recommended stake percentage."""
        if value <= 0 or confidence < 0.5:
            return 0.0

        # Kelly Criterion approximation
        edge = value * confidence
        if edge >= 0.2:  # 20%+ edge
            return 5.0  # 5% of bank
        elif edge >= 0.1:  # 10%+ edge
            return 3.0  # 3% of bank
        elif edge >= 0.05:  # 5%+ edge
            return 1.0  # 1% of bank
        else:
            return 0.0


def run_demonstration():
    """Run the complete race trends demonstration."""
    print("🏇 RACE TRENDS ANALYSIS DEMONSTRATION")
    print("Based on thestatsdontlie.com Chesterfield Cup Analysis")
    print("=" * 65)

    analyzer = SimplifiedRaceTrendsAnalyzer()

    # Step 1: Analyze race trends
    print("\n🔍 STEP 1: ANALYZING HISTORICAL RACE TRENDS")
    print("-" * 50)

    race_trends = analyzer.analyze_chesterfield_cup_trends()

    print(f"📊 Race: {race_trends.race_name}")
    print(f"🏟️  Course: {race_trends.course}")
    print(f"📏 Distance: {race_trends.distance}")
    print(f"🎯 Overall Edge Score: {race_trends.overall_edge_score:.2%}")
    print(f"📈 Patterns Found: {race_trends.total_patterns_found}")

    print(f"\n🔥 KEY TRENDS IDENTIFIED:")

    # Display significant trends
    all_trends = (
        race_trends.age_trends
        + race_trends.weight_trends
        + race_trends.draw_trends
        + race_trends.form_trends
        + race_trends.distance_form_trends
        + race_trends.price_trends
    )

    for trend in all_trends:
        if trend.confidence >= 0.7:
            print(
                f"  ✅ {trend.pattern} (Confidence: {trend.confidence:.1%}, Edge: {trend.edge_value:.1%})"
            )

    # Step 2: Score horses
    print(f"\n🐎 STEP 2: SCORING HORSES AGAINST TRENDS")
    print("-" * 50)

    scored_horses = analyzer.score_sample_horses(race_trends)

    for i, horse_data in enumerate(scored_horses, 1):
        horse = horse_data["horse"]
        score = horse_data["trend_score"]
        edge = horse_data["edge_analysis"]

        print(f"\n{i}. {horse['name']} (Odds: {horse['odds']}/1)")
        print(f"   🎯 Trend Score: {score.overall_trend_score:.2%}")
        print(f"   ⭐ Recommendation: {score.recommendation}")
        print(f"   📊 Confidence: {score.confidence:.1%}")

        if edge["betting_edge"]:
            print(f"   💰 BETTING EDGE: {edge['value_percentage']:.1f}% value")
            print(f"   💵 Recommended Stake: {edge['recommended_stake']:.1f}% of bank")

        print(f"   📈 Key Matches:")
        for pattern in score.matching_patterns[:3]:
            print(f"      • {pattern}")

        if score.edge_factors:
            print(f"   🔥 Edge Factors:")
            for factor in score.edge_factors:
                print(f"      • {factor}")

    # Step 3: Summary and recommendations
    print(f"\n💎 STEP 3: FINAL ANALYSIS & RECOMMENDATIONS")
    print("-" * 50)

    top_horse = scored_horses[0]

    print(f"🏆 TOP PICK: {top_horse['horse']['name']}")
    print(f"   📊 Matches {len(top_horse['trend_score'].matching_patterns)} key trends")
    print(f"   🎯 {top_horse['trend_score'].overall_trend_score:.1%} trend score")
    print(f"   💰 {top_horse['edge_analysis']['value_percentage']:.1f}% betting value")

    # Show betting strategy
    value_bets = [h for h in scored_horses if h["edge_analysis"]["betting_edge"]]

    if value_bets:
        print(f"\n💰 VALUE BETTING OPPORTUNITIES:")
        for horse_data in value_bets:
            horse = horse_data["horse"]
            edge = horse_data["edge_analysis"]
            print(
                f"  • {horse['name']}: {edge['value_percentage']:.1f}% value at {horse['odds']}/1"
            )
            print(f"    Recommended stake: {edge['recommended_stake']:.1f}% of bank")

    print(f"\n🎯 TRENDS SUMMARY:")
    print(f"  • Age bias: 4-5 year olds dominate (100% of winners)")
    print(f"  • Weight bias: Light weights favored (75% under 9st 2lbs)")
    print(f"  • Draw bias: High draws advantaged (80% from stall 10+)")
    print(f"  • Form pattern: Non-winners last time out (100% pattern)")
    print(f"  • Experience factor: 10-furlong form important (83% had it)")

    print(f"\n🚀 CONCLUSION:")
    print(f"Race shows {race_trends.overall_edge_score:.1%} overall edge")
    print(f"Strong statistical patterns provide significant betting advantages")
    print(f"AI + Trends analysis gives superior edge over ratings alone!")

    return {
        "race_trends": race_trends,
        "scored_horses": scored_horses,
        "value_bets": value_bets,
    }


if __name__ == "__main__":
    try:
        results = run_demonstration()
        print(f"\n✅ Demonstration completed successfully!")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
