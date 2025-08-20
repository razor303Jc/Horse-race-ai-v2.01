"""
80/20 Strategy Integration with Enhanced AI Selections
=====================================================

Integrates the InformRacing 80/20 betting strategy with our enhanced AI selections system.
This bridges our enhanced value detection with the place-focused 80/20 approach.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

# Import our existing components
from improved_ai_selections_generator import (
    ImprovedAISelectionsGenerator,
    EnhancedValueDetector,
)
from src.horse_racing_ai.betting.eighty_twenty_strategy import (
    EightyTwentyStrategy,
    EightyTwentyBet,
    StakeAllocation,
)

logger = logging.getLogger(__name__)


class EightyTwentyAIIntegration:
    """Integration between Enhanced AI Selections and 80/20 betting strategy"""

    def __init__(
        self,
        selections_generator: ImprovedAISelectionsGenerator,
        starting_bankroll: float = 1000.0,
    ):
        """
        Initialize the integration system

        Args:
            selections_generator: Our enhanced AI selections system
            starting_bankroll: Starting bankroll for 80/20 strategy
        """
        self.ai_selections = selections_generator
        self.eighty_twenty = EightyTwentyStrategy(starting_bankroll=starting_bankroll)
        self.value_detector = EnhancedValueDetector()

        # Integration settings
        self.min_ai_confidence = 0.6
        self.min_place_probability = 0.4
        self.max_win_odds = 15.0  # Don't bet on horses over 15/1

        # Performance tracking
        self.integration_stats = {
            "races_analyzed": 0,
            "ai_selections_made": 0,
            "eighty_twenty_opportunities": 0,
            "bets_placed": 0,
            "profitable_bets": 0,
        }

    def analyze_race_with_ai_eighty_twenty(self, race_data: pd.DataFrame) -> Dict:
        """
        Complete race analysis combining AI selections with 80/20 strategy

        Args:
            race_data: DataFrame with race data

        Returns:
            Dict with complete analysis and betting recommendations
        """
        self.integration_stats["races_analyzed"] += 1

        # Step 1: Generate enhanced AI selections
        logger.info("🤖 Generating enhanced AI selections...")
        ai_results = self.ai_selections.generate_improved_selections(race_data)

        if not ai_results or "selections" not in ai_results:
            return {"error": "No AI selections generated"}

        ai_selections = ai_results["selections"]
        self.integration_stats["ai_selections_made"] += len(ai_selections)

        # Step 2: Convert AI selections to 80/20 format
        logger.info("🔄 Converting AI selections for 80/20 analysis...")
        eighty_twenty_candidates = self._convert_ai_to_eighty_twenty_format(
            ai_selections, race_data
        )

        # Step 3: Analyze with 80/20 strategy
        logger.info("📊 Analyzing 80/20 opportunities...")
        eighty_twenty_opportunities = self.eighty_twenty.analyze_race_for_eighty_twenty(
            eighty_twenty_candidates
        )

        self.integration_stats["eighty_twenty_opportunities"] += len(
            eighty_twenty_opportunities
        )

        # Step 4: Combine insights and rank opportunities
        logger.info("🎯 Combining AI and 80/20 insights...")
        combined_opportunities = self._combine_ai_and_eighty_twenty_insights(
            ai_selections, eighty_twenty_opportunities
        )

        # Step 5: Generate final recommendations
        recommendations = self._generate_integrated_recommendations(
            combined_opportunities
        )

        return {
            "race_analysis": {
                "ai_selections": ai_selections,
                "eighty_twenty_opportunities": eighty_twenty_opportunities,
                "combined_opportunities": combined_opportunities,
                "final_recommendations": recommendations,
            },
            "integration_stats": self.integration_stats.copy(),
            "strategy_performance": self.eighty_twenty.get_performance_summary(),
        }

    def _convert_ai_to_eighty_twenty_format(
        self, ai_selections: List[Dict], race_data: pd.DataFrame
    ) -> List[Dict]:
        """Convert AI selections to format suitable for 80/20 analysis"""

        eighty_twenty_format = []

        for selection in ai_selections:
            horse_name = selection.get("horse_name", "Unknown")

            # Find corresponding race data
            horse_row = race_data[race_data["horse_name"] == horse_name]
            if horse_row.empty:
                continue

            horse_data = horse_row.iloc[0]

            # Extract/calculate required data
            win_odds = horse_data.get("odds", 0.0)
            if win_odds <= 1.0:
                continue

            # Estimate place odds (typically 1/3 to 1/4 of win odds for place part)
            # Using exchange-style calculation
            if win_odds <= 3.0:
                place_odds = 1.0 + (
                    (win_odds - 1.0) * 0.25
                )  # 1/4 odds for short prices
            else:
                place_odds = 1.0 + (
                    (win_odds - 1.0) * 0.33
                )  # 1/3 odds for longer prices

            # Use AI confidence as win probability
            ai_confidence = selection.get("confidence", 0.5)
            win_probability = ai_confidence

            # Estimate place probability (typically 2-3x win probability)
            place_probability = min(0.85, win_probability * 2.5)

            # Enhanced value score as overall confidence
            enhanced_value = selection.get("enhanced_value_score", 1.0)
            overall_confidence = min(1.0, (ai_confidence + (enhanced_value - 1.0)) / 2)

            eighty_twenty_format.append(
                {
                    "horse_name": horse_name,
                    "win_odds": win_odds,
                    "place_odds": place_odds,
                    "win_probability": win_probability,
                    "place_probability": place_probability,
                    "confidence": overall_confidence,
                    "ai_selection_data": selection,
                    "race_data": horse_data.to_dict(),
                }
            )

        return eighty_twenty_format

    def _combine_ai_and_eighty_twenty_insights(
        self, ai_selections: List[Dict], eighty_twenty_opportunities: List[Dict]
    ) -> List[Dict]:
        """Combine insights from both AI selections and 80/20 analysis"""

        combined = []

        for opportunity in eighty_twenty_opportunities:
            bet = opportunity["bet"]
            suitability = opportunity["suitability"]

            # Find corresponding AI selection
            ai_selection = None
            for ai_sel in ai_selections:
                if ai_sel.get("horse_name") == bet.horse_name:
                    ai_selection = ai_sel
                    break

            if not ai_selection:
                continue

            # Calculate combined confidence score
            ai_confidence = ai_selection.get("confidence", 0.5)
            eighty_twenty_confidence = bet.confidence
            suitability_score = suitability["suitability_score"] / 100.0

            # Weighted combination (AI 40%, 80/20 strategy 35%, suitability 25%)
            combined_confidence = (
                (ai_confidence * 0.4)
                + (eighty_twenty_confidence * 0.35)
                + (suitability_score * 0.25)
            )

            # Enhanced scoring based on value category
            value_category = ai_selection.get("value_category", "CONSIDER")
            value_multiplier = {
                "EXCEPTIONAL VALUE": 1.2,
                "STRONG VALUE": 1.1,
                "GOOD VALUE": 1.05,
                "EACH WAY VALUE": 1.15,  # Bonus for place-focused bets
                "HIGH CONFIDENCE": 1.1,
                "SMALL VALUE": 1.0,
                "MARGINAL VALUE": 0.95,
                "CONSIDER": 0.9,
            }.get(value_category, 1.0)

            final_score = combined_confidence * value_multiplier

            # Risk assessment
            if (
                ai_confidence >= 0.7
                and bet.expected_value > 0
                and suitability["recommendation"] in ["EXCELLENT", "GOOD"]
            ):
                integrated_risk = "LOW"
            elif (
                ai_confidence >= 0.5
                and bet.expected_value >= -0.5
                and suitability["recommendation"] in ["GOOD", "FAIR"]
            ):
                integrated_risk = "MEDIUM"
            else:
                integrated_risk = "HIGH"

            combined.append(
                {
                    "horse_name": bet.horse_name,
                    "ai_selection": ai_selection,
                    "eighty_twenty_bet": bet,
                    "suitability_assessment": suitability,
                    "combined_confidence": combined_confidence,
                    "final_score": final_score,
                    "integrated_risk": integrated_risk,
                    "value_category": value_category,
                    "recommendation_reasons": self._generate_recommendation_reasons(
                        ai_selection, bet, suitability, final_score
                    ),
                }
            )

        # Sort by final score (highest first)
        combined.sort(key=lambda x: x["final_score"], reverse=True)

        return combined

    def _generate_recommendation_reasons(
        self,
        ai_selection: Dict,
        bet: EightyTwentyBet,
        suitability: Dict,
        final_score: float,
    ) -> List[str]:
        """Generate detailed reasons for the recommendation"""

        reasons = []

        # AI insights
        ai_confidence = ai_selection.get("confidence", 0.0)
        if ai_confidence >= 0.8:
            reasons.append(f"High AI confidence: {ai_confidence:.1%}")
        elif ai_confidence >= 0.6:
            reasons.append(f"Good AI confidence: {ai_confidence:.1%}")

        value_category = ai_selection.get("value_category", "CONSIDER")
        if value_category in ["EXCEPTIONAL VALUE", "STRONG VALUE", "GOOD VALUE"]:
            reasons.append(f"AI detected {value_category.lower()}")

        # 80/20 insights
        if bet.expected_value > 1.0:
            reasons.append(f"Strong expected value: £{bet.expected_value:.2f}")
        elif bet.expected_value > 0:
            reasons.append(f"Positive expected value: £{bet.expected_value:.2f}")

        if bet.place_profit > 0:
            reasons.append(f"Profitable if placed: £{bet.place_profit:.2f}")

        # Suitability insights
        if suitability["recommendation"] == "EXCELLENT":
            reasons.append("Excellent 80/20 suitability")
        elif suitability["recommendation"] == "GOOD":
            reasons.append("Good 80/20 suitability")

        # Risk assessment
        if bet.risk_level == "LOW":
            reasons.append("Low risk profile")

        # Final score assessment
        if final_score >= 0.8:
            reasons.append("Outstanding combined score")
        elif final_score >= 0.7:
            reasons.append("Strong combined score")

        return reasons

    def _generate_integrated_recommendations(
        self, combined_opportunities: List[Dict]
    ) -> List[Dict]:
        """Generate final betting recommendations"""

        recommendations = []

        for opportunity in combined_opportunities[:3]:  # Top 3 opportunities
            bet = opportunity["eighty_twenty_bet"]

            # Should we bet?
            should_bet = (
                opportunity["final_score"] >= 0.65
                and opportunity["integrated_risk"] in ["LOW", "MEDIUM"]
                and bet.expected_value > -0.5
            )

            if should_bet:
                # Determine stake allocation based on confidence
                if opportunity["final_score"] >= 0.8:
                    allocation = StakeAllocation.AGGRESSIVE  # 60/40
                elif opportunity["final_score"] >= 0.7:
                    allocation = StakeAllocation.MODERATE  # 70/30
                else:
                    allocation = StakeAllocation.CONSERVATIVE  # 80/20

            recommendation = {
                "horse_name": bet.horse_name,
                "recommendation": "BET" if should_bet else "AVOID",
                "confidence_level": opportunity["final_score"],
                "risk_assessment": opportunity["integrated_risk"],
                "suggested_allocation": allocation.name if should_bet else None,
                "expected_outcome": {
                    "total_stake": bet.total_stake,
                    "place_stake": bet.place_stake,
                    "win_stake": bet.win_stake,
                    "expected_value": bet.expected_value,
                    "win_profit_potential": bet.win_profit,
                    "place_profit_potential": bet.place_profit,
                },
                "reasons": opportunity["recommendation_reasons"],
                "ai_insights": {
                    "value_category": opportunity["value_category"],
                    "ai_confidence": opportunity["ai_selection"].get("confidence", 0.0),
                    "enhanced_value_score": opportunity["ai_selection"].get(
                        "enhanced_value_score", 1.0
                    ),
                },
                "eighty_twenty_insights": {
                    "suitability": opportunity["suitability_assessment"][
                        "recommendation"
                    ],
                    "suitability_score": opportunity["suitability_assessment"][
                        "suitability_score"
                    ],
                    "roi_if_win": bet.roi_if_win,
                    "roi_if_place": bet.roi_if_place,
                },
            }

            recommendations.append(recommendation)

        return recommendations

    def execute_integrated_betting(self, recommendations: List[Dict]) -> List[Dict]:
        """Execute betting based on integrated recommendations"""

        executed_bets = []

        for rec in recommendations:
            if rec["recommendation"] == "BET":
                # Find the original 80/20 bet
                horse_name = rec["horse_name"]

                # Create bet with suggested allocation
                allocation_name = rec["suggested_allocation"]
                allocation = getattr(StakeAllocation, allocation_name)

                # We would need the original odds data to recreate the bet
                # For now, log the intention
                logger.info(f"🎯 Would execute 80/20 bet: {horse_name}")
                logger.info(f"   Allocation: {allocation_name}")
                logger.info(f"   Confidence: {rec['confidence_level']:.1%}")
                logger.info(
                    f"   Expected Value: £{rec['expected_outcome']['expected_value']:.2f}"
                )

                self.integration_stats["bets_placed"] += 1

                executed_bets.append(
                    {
                        "horse_name": horse_name,
                        "status": "SIMULATED",
                        "allocation_used": allocation_name,
                        "confidence": rec["confidence_level"],
                        "reasons": rec["reasons"],
                    }
                )

        return executed_bets

    def get_integration_performance(self) -> Dict:
        """Get performance statistics for the integrated system"""

        stats = self.integration_stats.copy()
        eighty_twenty_performance = self.eighty_twenty.get_performance_summary()

        # Calculate integration-specific metrics
        if stats["races_analyzed"] > 0:
            stats["ai_selections_per_race"] = (
                stats["ai_selections_made"] / stats["races_analyzed"]
            )
            stats["opportunities_per_race"] = (
                stats["eighty_twenty_opportunities"] / stats["races_analyzed"]
            )
            stats["bets_per_race"] = stats["bets_placed"] / stats["races_analyzed"]

        if stats["bets_placed"] > 0:
            stats["profitable_bet_rate"] = (
                stats["profitable_bets"] / stats["bets_placed"]
            ) * 100

        return {
            "integration_stats": stats,
            "eighty_twenty_performance": eighty_twenty_performance,
            "system_status": "ACTIVE",
            "last_update": "Real-time",
        }


def demonstrate_integrated_system():
    """Demonstration of the integrated AI + 80/20 system"""

    print("🤖🎯 Enhanced AI Selections + 80/20 Strategy Integration")
    print("=" * 60)

    # Create sample race data
    sample_race_data = pd.DataFrame(
        [
            {
                "horse_name": "Thunder Strike",
                "odds": 3.0,
                "jockey": "J. Smith",
                "trainer": "M. Johnson",
                "weight": 9.2,
                "age": 4,
                "form": "112",
                "days_since_last_run": 14,
                "course_name": "Newmarket",
                "distance": 1200,
                "going": "Good",
                "rating": 85,
            },
            {
                "horse_name": "Lightning Bolt",
                "odds": 5.0,
                "jockey": "R. Moore",
                "trainer": "A. O'Brien",
                "weight": 9.0,
                "age": 3,
                "form": "231",
                "days_since_last_run": 21,
                "course_name": "Newmarket",
                "distance": 1200,
                "going": "Good",
                "rating": 82,
            },
            {
                "horse_name": "Storm Chaser",
                "odds": 7.0,
                "jockey": "W. Buick",
                "trainer": "J. Gosden",
                "weight": 8.8,
                "age": 5,
                "form": "321",
                "days_since_last_run": 28,
                "course_name": "Newmarket",
                "distance": 1200,
                "going": "Good",
                "rating": 80,
            },
        ]
    )

    # Initialize systems
    ai_generator = ImprovedAISelectionsGenerator()
    integration = EightyTwentyAIIntegration(ai_generator, starting_bankroll=500.0)

    print("\n📊 Analyzing race with integrated system...")

    # This would normally work with real data
    # For demonstration, we'll simulate the process
    print("\n🤖 AI Selections would be generated...")
    print("📊 80/20 opportunities would be analyzed...")
    print("🎯 Integration would combine insights...")
    print("💡 Final recommendations would be produced...")

    print("\n✅ Integration system ready for live racing data!")
    print("\nKey Benefits:")
    print("- AI confidence combined with 80/20 place focus")
    print("- Multi-factor suitability assessment")
    print("- Risk-adjusted stake allocation")
    print("- Expected value optimization")
    print("- Comprehensive performance tracking")


if __name__ == "__main__":
    demonstrate_integrated_system()
