#!/usr/bin/env python3
"""
Race Trends Integration Demo
Demonstrates how the Race Trends Analyzer gives additional edge when combined
with AI ratings and form analysis.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.append("/home/jc/Documents/Horse-race-handicaping-ai/Horse-race-ai-v2.0/src")

from horse_racing_ai.analysis.race_trends_analyzer import (
    HorseTrendScore,
    RaceAnalysisTrends,
    RaceTrendsAnalyzer,
)
from horse_racing_ai.betting.advanced_strategies import AdvancedBettingStrategies
from horse_racing_ai.integration.ai_betting_integration import (
    AIBettingIntegrationSystem,
)
from horse_racing_ai.ml.enhanced_ml_rating_system import EnhancedMLRatingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceTrendsIntegrationDemo:
    """Demonstrates race trends analysis integration with existing AI system."""

    def __init__(self):
        """Initialize the integrated system."""
        self.trends_analyzer = RaceTrendsAnalyzer()
        self.ml_rating_system = EnhancedMLRatingSystem()
        self.betting_strategies = AdvancedBettingStrategies()
        self.ai_betting_integration = AIBettingIntegrationSystem()

        logger.info("Race Trends Integration Demo initialized")

    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of race trends integration."""
        print("🏇 RACE TRENDS INTEGRATION DEMONSTRATION")
        print("=" * 60)

        # Generate sample race data
        sample_race = self._generate_sample_race_data()
        historical_races = self._generate_historical_race_data()

        print(f"\n📊 ANALYZING RACE: {sample_race['race_name']}")
        print(f"Course: {sample_race['course']}")
        print(f"Distance: {sample_race['distance']}")
        print(f"Surface: {sample_race['surface']}")
        print(f"Race Type: {sample_race['race_type']}")

        # Step 1: Analyze race trends
        print("\n🔍 STEP 1: ANALYZING RACE TRENDS")
        print("-" * 40)

        race_trends = self.trends_analyzer.analyze_race_trends(
            sample_race, historical_races
        )

        self._display_race_trends(race_trends)

        # Step 2: Analyze each horse with trends + AI ratings
        print("\n🐎 STEP 2: HORSE ANALYSIS WITH TRENDS + AI")
        print("-" * 40)

        enhanced_horses = []
        for horse in sample_race["horses"]:
            # Get AI rating
            ai_score = await self._get_ai_rating(horse)

            # Get trends score
            trend_score = self.trends_analyzer.score_horse_trends(horse, race_trends)

            # Calculate combined score
            combined_score = self._calculate_combined_score(ai_score, trend_score)

            enhanced_horses.append(
                {
                    "horse": horse,
                    "ai_score": ai_score,
                    "trend_score": trend_score,
                    "combined_score": combined_score,
                }
            )

        # Sort by combined score
        enhanced_horses.sort(
            key=lambda x: x["combined_score"]["overall_score"], reverse=True
        )

        self._display_horse_analysis(enhanced_horses)

        # Step 3: Apply betting strategies with enhanced analysis
        print("\n💰 STEP 3: BETTING STRATEGIES WITH TRENDS EDGE")
        print("-" * 40)

        betting_analysis = await self._analyze_betting_opportunities(
            enhanced_horses, race_trends
        )

        self._display_betting_analysis(betting_analysis)

        # Step 4: Generate final recommendations
        print("\n📈 STEP 4: FINAL RECOMMENDATIONS")
        print("-" * 40)

        recommendations = self._generate_final_recommendations(
            enhanced_horses, race_trends, betting_analysis
        )

        self._display_final_recommendations(recommendations)

        return {
            "race_data": sample_race,
            "race_trends": race_trends,
            "enhanced_horses": enhanced_horses,
            "betting_analysis": betting_analysis,
            "recommendations": recommendations,
        }

    def _generate_sample_race_data(self) -> Dict[str, Any]:
        """Generate realistic sample race data."""
        return {
            "race_name": "Chesterfield Cup",
            "course": "Goodwood",
            "distance": "1m2f",
            "surface": "turf",
            "race_type": "handicap",
            "race_date": datetime.now().isoformat(),
            "horses": [
                {
                    "name": "Thunder Strike",
                    "age": 4,
                    "weight": "9st 0lbs",
                    "draw": 12,
                    "odds": 4.5,
                    "jockey": "Ryan Moore",
                    "trainer": "Aidan O'Brien",
                    "last_run_result": "second",
                    "days_since_last_run": 21,
                    "course_wins": 0,
                    "course_runs": 0,
                    "distance_wins": 1,
                    "distance_runs": 3,
                    "rating": 98,
                    "form": "2-1-3-1",
                },
                {
                    "name": "Desert Lightning",
                    "age": 5,
                    "weight": "8st 12lbs",
                    "draw": 15,
                    "odds": 6.0,
                    "jockey": "William Buick",
                    "trainer": "Charlie Appleby",
                    "last_run_result": "third",
                    "days_since_last_run": 28,
                    "course_wins": 1,
                    "course_runs": 2,
                    "distance_wins": 2,
                    "distance_runs": 4,
                    "rating": 96,
                    "form": "3-1-1-2",
                },
                {
                    "name": "Celtic Storm",
                    "age": 4,
                    "weight": "9st 2lbs",
                    "draw": 8,
                    "odds": 8.0,
                    "jockey": "Frankie Dettori",
                    "trainer": "John Gosden",
                    "last_run_result": "fourth",
                    "days_since_last_run": 14,
                    "course_wins": 0,
                    "course_runs": 1,
                    "distance_wins": 0,
                    "distance_runs": 2,
                    "rating": 94,
                    "form": "4-2-1-5",
                },
                {
                    "name": "Royal Ascent",
                    "age": 6,
                    "weight": "8st 10lbs",
                    "draw": 3,
                    "odds": 12.0,
                    "jockey": "Oisin Murphy",
                    "trainer": "Andrew Balding",
                    "last_run_result": "win",
                    "days_since_last_run": 35,
                    "course_wins": 0,
                    "course_runs": 0,
                    "distance_wins": 1,
                    "distance_runs": 5,
                    "rating": 92,
                    "form": "1-3-2-6",
                },
            ],
        }

    def _generate_historical_race_data(self) -> List[Dict[str, Any]]:
        """Generate historical race data for trends analysis."""
        historical_races = []

        # Based on thestatsdontlie.com Chesterfield Cup trends
        for i in range(15):
            race = {
                "race_name": "Chesterfield Cup",
                "course": "Goodwood",
                "distance": "1m2f",
                "surface": "turf",
                "race_type": "handicap",
                "race_date": (
                    datetime.now() - timedelta(days=365 * i + 30)
                ).isoformat(),
                "winner": {
                    "age": 4 if i < 8 else 5,  # 8/12 aged 4, 4/12 aged 5
                    "weight": 126 if i < 9 else 132,  # 9/12 carried 9st 2lbs or less
                    "draw": 12 if i < 8 else 5,  # 8/10 from stall 10+
                    "odds": 5.5 if i < 6 else 15.0,  # Mix of prices
                    "last_run_result": "second" if i < 12 else "win",  # 0/12 won last
                    "days_since_last_run": 25,  # All ran within 34 days
                    "course_wins": 1 if i < 4 else 0,  # 4/12 had course wins
                    "course_runs": 1,
                    "distance_wins": 1 if i < 10 else 0,  # 10/12 had distance form
                    "distance_runs": 2,
                    "rating": 97 if i < 10 else 88,  # 10/12 rated 95+
                },
            }
            historical_races.append(race)

        return historical_races

    async def _get_ai_rating(self, horse: Dict[str, Any]) -> Dict[str, float]:
        """Get AI rating for horse (simulated)."""
        # Simulate AI rating based on form and stats
        base_rating = horse.get("rating", 90) / 100

        # Adjust for recent form
        form_adjustment = (
            0.1 if horse.get("last_run_result") in ["win", "second"] else -0.05
        )

        # Adjust for distance experience
        distance_adjustment = 0.1 if horse.get("distance_wins", 0) > 0 else 0.0

        ai_score = base_rating + form_adjustment + distance_adjustment

        return {
            "overall_rating": min(max(ai_score, 0.0), 1.0),
            "confidence": 0.8,
            "form_score": 0.7,
            "class_score": base_rating,
            "fitness_score": 0.75,
        }

    def _calculate_combined_score(
        self, ai_score: Dict[str, float], trend_score: HorseTrendScore
    ) -> Dict[str, Any]:
        """Calculate combined AI + trends score."""
        # Weight AI vs trends analysis
        ai_weight = 0.6
        trends_weight = 0.4

        combined_overall = (
            ai_score["overall_rating"] * ai_weight
            + trend_score.overall_trend_score * trends_weight
        )

        # Calculate confidence based on both systems
        combined_confidence = (
            ai_score["confidence"] * ai_weight + trend_score.confidence * trends_weight
        )

        # Edge calculation
        edge_value = 0.0
        if trend_score.recommendation in ["STRONG", "MODERATE"]:
            edge_value = 0.2 if trend_score.recommendation == "STRONG" else 0.1

        return {
            "overall_score": combined_overall,
            "confidence": combined_confidence,
            "edge_value": edge_value,
            "ai_component": ai_score["overall_rating"],
            "trends_component": trend_score.overall_trend_score,
            "recommendation": self._get_combined_recommendation(
                combined_overall, combined_confidence, edge_value
            ),
        }

    def _get_combined_recommendation(
        self, score: float, confidence: float, edge: float
    ) -> str:
        """Get combined recommendation."""
        if score >= 0.8 and confidence >= 0.7 and edge >= 0.15:
            return "STRONG_BUY"
        elif score >= 0.7 and confidence >= 0.6:
            return "BUY"
        elif score >= 0.6:
            return "MODERATE"
        elif score >= 0.4:
            return "WEAK"
        else:
            return "AVOID"

    async def _analyze_betting_opportunities(
        self, enhanced_horses: List[Dict], race_trends: RaceAnalysisTrends
    ) -> Dict[str, Any]:
        """Analyze betting opportunities with trends edge."""
        opportunities = {
            "value_bets": [],
            "dutching_opportunities": [],
            "lay_opportunities": [],
            "trends_edge_bets": [],
        }

        for horse_analysis in enhanced_horses:
            horse = horse_analysis["horse"]
            combined = horse_analysis["combined_score"]
            trend_score = horse_analysis["trend_score"]

            # Value betting analysis
            implied_prob = 1 / horse["odds"]
            predicted_prob = combined["overall_score"]

            if predicted_prob > implied_prob * 1.1:  # 10% edge required
                value = (predicted_prob - implied_prob) / implied_prob
                opportunities["value_bets"].append(
                    {
                        "horse": horse["name"],
                        "odds": horse["odds"],
                        "predicted_prob": predicted_prob,
                        "implied_prob": implied_prob,
                        "value": value,
                        "confidence": combined["confidence"],
                    }
                )

            # Trends-specific edge bets
            if trend_score.recommendation == "STRONG" and combined["edge_value"] > 0.15:
                opportunities["trends_edge_bets"].append(
                    {
                        "horse": horse["name"],
                        "odds": horse["odds"],
                        "trend_patterns": trend_score.matching_patterns,
                        "edge_factors": trend_score.edge_factors,
                        "edge_value": combined["edge_value"],
                    }
                )

        # Dutching analysis
        top_horses = enhanced_horses[:3]
        if len(top_horses) >= 2:
            total_prob = sum(h["combined_score"]["overall_score"] for h in top_horses)
            if total_prob > 0.7:  # Strong confidence in top picks
                opportunities["dutching_opportunities"].append(
                    {
                        "horses": [h["horse"]["name"] for h in top_horses],
                        "total_probability": total_prob,
                        "recommended_stakes": self._calculate_dutching_stakes(
                            top_horses
                        ),
                    }
                )

        return opportunities

    def _calculate_dutching_stakes(self, horses: List[Dict]) -> Dict[str, float]:
        """Calculate optimal dutching stakes."""
        stakes = {}
        total_stake = 100  # £100 total stake

        # Simple equal profit dutching
        for horse_data in horses:
            horse = horse_data["horse"]
            odds = horse["odds"]
            prob = horse_data["combined_score"]["overall_score"]

            # Calculate stake for equal profit
            stake = total_stake / (len(horses) * odds)
            stakes[horse["name"]] = round(stake, 2)

        return stakes

    def _display_race_trends(self, race_trends: RaceAnalysisTrends):
        """Display race trends analysis."""
        print(f"Overall Edge Score: {race_trends.overall_edge_score:.2%}")
        print(f"Total Patterns Found: {race_trends.total_patterns_found}")

        if race_trends.age_trends:
            print("\n🎂 Age Trends:")
            for trend in race_trends.age_trends:
                if trend.confidence >= 0.7:
                    print(f"  ✅ {trend.pattern} ({trend.percentage:.1f}%)")

        if race_trends.weight_trends:
            print("\n⚖️ Weight Trends:")
            for trend in race_trends.weight_trends:
                if trend.confidence >= 0.7:
                    print(f"  ✅ {trend.pattern} ({trend.percentage:.1f}%)")

        if race_trends.draw_trends:
            print("\n🎯 Draw Trends:")
            for trend in race_trends.draw_trends:
                if trend.confidence >= 0.7:
                    print(f"  ✅ {trend.pattern} ({trend.percentage:.1f}%)")

        if race_trends.form_trends:
            print("\n📊 Form Trends:")
            for trend in race_trends.form_trends:
                if trend.confidence >= 0.7:
                    print(f"  ✅ {trend.pattern} ({trend.percentage:.1f}%)")

    def _display_horse_analysis(self, enhanced_horses: List[Dict]):
        """Display enhanced horse analysis."""
        for i, horse_data in enumerate(enhanced_horses[:4], 1):
            horse = horse_data["horse"]
            ai_score = horse_data["ai_score"]
            trend_score = horse_data["trend_score"]
            combined = horse_data["combined_score"]

            print(f"\n{i}. {horse['name']} (Odds: {horse['odds']}/1)")
            print(f"   🤖 AI Score: {ai_score['overall_rating']:.2%}")
            print(f"   📈 Trends Score: {trend_score.overall_trend_score:.2%}")
            print(f"   🎯 Combined Score: {combined['overall_score']:.2%}")
            print(f"   ⭐ Recommendation: {combined['recommendation']}")

            if trend_score.matching_patterns:
                print(f"   📊 Trend Matches:")
                for pattern in trend_score.matching_patterns[:2]:
                    print(f"      • {pattern}")

    def _display_betting_analysis(self, betting_analysis: Dict[str, Any]):
        """Display betting analysis results."""
        if betting_analysis["value_bets"]:
            print("\n💎 VALUE BETTING OPPORTUNITIES:")
            for bet in betting_analysis["value_bets"]:
                print(
                    f"  • {bet['horse']}: {bet['value']:.1%} value at {bet['odds']}/1"
                )

        if betting_analysis["trends_edge_bets"]:
            print("\n🔥 TRENDS EDGE OPPORTUNITIES:")
            for bet in betting_analysis["trends_edge_bets"]:
                print(f"  • {bet['horse']}: {bet['edge_value']:.1%} edge")
                for factor in bet["edge_factors"][:2]:
                    print(f"    - {factor}")

        if betting_analysis["dutching_opportunities"]:
            print("\n🎯 DUTCHING OPPORTUNITIES:")
            for dutch in betting_analysis["dutching_opportunities"]:
                print(f"  • Horses: {', '.join(dutch['horses'])}")
                print(f"  • Total Probability: {dutch['total_probability']:.1%}")

    def _display_final_recommendations(self, recommendations: Dict[str, Any]):
        """Display final recommendations."""
        print(f"🏆 TOP PICK: {recommendations['top_pick']['horse']}")
        print(f"   Score: {recommendations['top_pick']['score']:.2%}")
        print(f"   Reason: {recommendations['top_pick']['reason']}")

        if recommendations["betting_strategy"]:
            print(
                f"\n💰 BETTING STRATEGY: {recommendations['betting_strategy']['type']}"
            )
            print(f"   Stake: £{recommendations['betting_strategy']['stake']}")
            print(
                f"   Expected Return: {recommendations['betting_strategy']['expected_return']:.1%}"
            )

        print(f"\n📊 CONFIDENCE LEVEL: {recommendations['confidence_level']}")
        print(f"🎯 TREND EDGE: {recommendations['trend_edge']:.1%}")

    def _generate_final_recommendations(
        self,
        enhanced_horses: List[Dict],
        race_trends: RaceAnalysisTrends,
        betting_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate final recommendations."""
        top_horse = enhanced_horses[0]

        # Determine betting strategy
        betting_strategy = None
        if betting_analysis["trends_edge_bets"]:
            betting_strategy = {
                "type": "TRENDS_EDGE_BET",
                "stake": 25,
                "expected_return": top_horse["combined_score"]["edge_value"] * 100,
            }
        elif betting_analysis["value_bets"]:
            betting_strategy = {
                "type": "VALUE_BET",
                "stake": 20,
                "expected_return": betting_analysis["value_bets"][0]["value"] * 100,
            }
        elif betting_analysis["dutching_opportunities"]:
            betting_strategy = {
                "type": "DUTCHING",
                "stake": 50,
                "expected_return": 15.0,
            }

        return {
            "top_pick": {
                "horse": top_horse["horse"]["name"],
                "score": top_horse["combined_score"]["overall_score"],
                "reason": f"Strong combined AI + Trends analysis ({top_horse['trend_score'].recommendation})",
            },
            "betting_strategy": betting_strategy,
            "confidence_level": (
                "HIGH" if race_trends.overall_edge_score > 0.3 else "MODERATE"
            ),
            "trend_edge": race_trends.overall_edge_score,
        }


async def main():
    """Run the race trends integration demonstration."""
    demo = RaceTrendsIntegrationDemo()

    try:
        print("🚀 Starting Race Trends Integration Demo...")
        results = await demo.run_comprehensive_demo()

        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETE!")
        print("=" * 60)

        print(f"\nThe Race Trends Analyzer successfully identified:")
        print(f"• {results['race_trends'].total_patterns_found} statistical patterns")
        print(f"• {results['race_trends'].overall_edge_score:.1%} overall betting edge")
        print(f"• Enhanced predictions for {len(results['enhanced_horses'])} horses")

        print(f"\nThis demonstrates how thestatsdontlie.com style analysis")
        print(f"provides additional edge when combined with AI ratings!")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
