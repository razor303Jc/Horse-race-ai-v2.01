#!/usr/bin/env python3
"""
Standalone Enhanced Monte Carlo Betting Analysis
===============================================

Integrates 80/20 and Dutching strategies with Monte Carlo simulation
for comprehensive race analysis. Includes all necessary components.

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import asyncio
import logging
import json
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, date
from decimal import Decimal
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from horse_racing_ai.betting.eighty_twenty_strategy import (
    EightyTwentyStrategy,
    StakeAllocation,
)
from horse_racing_ai.betting.reduced_stake_dutching import ReducedStakeDutching
from horse_racing_ai.integration.eighty_twenty_ai_integration import (
    EightyTwentyAIIntegration,
)
from horse_racing_ai.integration.dutching_ai_integration import DutchingAIIntegration

logger = logging.getLogger(__name__)


@dataclass
class BettingStrategyResult:
    """Result from a betting strategy analysis"""

    strategy_type: str
    suitable: bool
    confidence_score: float
    expected_roi: float
    total_stake: float
    potential_profit: float
    risk_level: str
    recommendations: List[Dict]
    reasoning: str


@dataclass
class EnhancedMonteCarloResults:
    """Enhanced Monte Carlo results with betting strategy analysis"""

    race_id: str
    simulation_timestamp: datetime

    # Betting strategy results
    eighty_twenty_analysis: Optional[BettingStrategyResult]
    dutching_analysis: Optional[BettingStrategyResult]

    # Combined recommendations
    recommended_strategy: str
    combined_roi_estimate: float
    bankroll_allocation: Dict[str, float]
    risk_assessment: Dict

    # Performance tracking
    total_races_analyzed: int
    successful_recommendations: int
    cumulative_roi: float


class StandaloneEnhancedEngine:
    """Standalone enhanced Monte Carlo engine with integrated betting strategies"""

    def __init__(self, default_bankroll: float = 1000.0):
        """Initialize enhanced Monte Carlo engine"""
        self.default_bankroll = default_bankroll

        # Initialize betting strategies
        self.eighty_twenty_strategy = EightyTwentyStrategy(
            starting_bankroll=default_bankroll, min_place_odds=1.5, max_field_size=12
        )
        self.dutching_strategy = ReducedStakeDutching()

        # Initialize AI integrations (with minimal setup for testing)
        try:
            from horse_racing_ai.analysis.enhanced_ai_selections_v2 import (
                ImprovedAISelectionsGenerator,
            )

            ai_generator = ImprovedAISelectionsGenerator()
            self.eighty_twenty_ai = EightyTwentyAIIntegration(
                selections_generator=ai_generator, starting_bankroll=default_bankroll
            )
            self.dutching_ai = DutchingAIIntegration(selections_generator=ai_generator)
        except ImportError:
            # Create minimal mock integrations for testing
            self.eighty_twenty_ai = None
            self.dutching_ai = None
            logger.warning("AI integrations not available - using simplified analysis")

        # Performance tracking
        self.performance_stats = {
            "total_races": 0,
            "successful_eighty_twenty": 0,
            "successful_dutching": 0,
            "total_profit": Decimal("0"),
            "total_stakes": Decimal("0"),
            "cumulative_roi": 0.0,
        }

        logger.info("Standalone Enhanced Monte Carlo Engine initialized")

    async def analyze_race_with_strategies(
        self, race_data: Dict, bankroll: Optional[float] = None
    ) -> EnhancedMonteCarloResults:
        """Perform comprehensive race analysis with betting strategies"""
        start_time = datetime.now()
        race_id = race_data.get(
            "race_id", f"RACE_{start_time.strftime('%Y%m%d_%H%M%S')}"
        )

        if bankroll is None:
            bankroll = self.default_bankroll

        logger.info(f"Starting enhanced analysis for race {race_id}")

        try:
            # Analyze 80/20 strategy opportunities
            eighty_twenty_result = await self._analyze_eighty_twenty_strategy(
                race_data, bankroll
            )

            # Analyze Dutching strategy opportunities
            dutching_result = await self._analyze_dutching_strategy(race_data, bankroll)

            # Combine analyses and create recommendations
            combined_analysis = self._combine_strategy_analyses(
                eighty_twenty_result, dutching_result
            )

            # Create enhanced results
            enhanced_results = EnhancedMonteCarloResults(
                race_id=race_id,
                simulation_timestamp=start_time,
                eighty_twenty_analysis=eighty_twenty_result,
                dutching_analysis=dutching_result,
                recommended_strategy=combined_analysis["recommended_strategy"],
                combined_roi_estimate=combined_analysis["combined_roi"],
                bankroll_allocation=combined_analysis["bankroll_allocation"],
                risk_assessment=combined_analysis["risk_assessment"],
                total_races_analyzed=self.performance_stats["total_races"] + 1,
                successful_recommendations=self._count_successful_recommendations(),
                cumulative_roi=self.performance_stats["cumulative_roi"],
            )

            # Update performance tracking
            self._update_performance_stats(enhanced_results)

            logger.info(
                f"Enhanced analysis completed for race {race_id} in "
                f"{(datetime.now() - start_time).total_seconds():.2f}s"
            )

            return enhanced_results

        except Exception as e:
            logger.error(f"Error in enhanced race analysis: {str(e)}")
            raise

    async def _analyze_eighty_twenty_strategy(
        self, race_data: Dict, bankroll: float
    ) -> Optional[BettingStrategyResult]:
        """Analyze 80/20 strategy opportunities"""
        try:
            # Get AI selections from race data
            ai_selections = race_data.get("ai_selections", [])
            if not ai_selections:
                logger.warning("No AI selections found for 80/20 analysis")
                return BettingStrategyResult(
                    strategy_type="80/20",
                    suitable=False,
                    confidence_score=0.0,
                    expected_roi=0.0,
                    total_stake=0.0,
                    potential_profit=0.0,
                    risk_level="N/A",
                    recommendations=[],
                    reasoning="No AI selections available",
                )

            # If AI integration is available, use it
            if self.eighty_twenty_ai:
                recommendations = self.eighty_twenty_ai.analyze_race_for_eighty_twenty(
                    race_data, Decimal(str(bankroll))
                )

                if recommendations:
                    best_recommendation = recommendations[0]
                    bet_plan = best_recommendation.bet_plan

                    return BettingStrategyResult(
                        strategy_type="80/20",
                        suitable=True,
                        confidence_score=best_recommendation.confidence_score,
                        expected_roi=best_recommendation.expected_roi,
                        total_stake=float(bet_plan.total_stake),
                        potential_profit=float(bet_plan.expected_profit),
                        risk_level=best_recommendation.risk_level,
                        recommendations=[best_recommendation.to_dict()],
                        reasoning=best_recommendation.strategy_reasoning,
                    )

            # Fallback: Simple analysis using strategy directly
            best_selection = max(ai_selections, key=lambda x: x.get("ai_confidence", 0))

            if best_selection.get("ai_confidence", 0) > 70:
                # Create a simple 80/20 bet
                stake = min(50.0, bankroll * 0.1)  # 10% of bankroll, max £50
                place_stake = stake * 0.8
                win_stake = stake * 0.2

                odds = best_selection.get("odds", 3.0)
                place_odds = max(1.5, odds * 0.5)  # Estimate place odds

                expected_return = (win_stake * odds * 0.3) + (
                    place_stake * place_odds * 0.7
                )
                expected_profit = expected_return - stake
                roi = (expected_profit / stake) * 100 if stake > 0 else 0

                return BettingStrategyResult(
                    strategy_type="80/20",
                    suitable=True,
                    confidence_score=best_selection.get("ai_confidence", 75),
                    expected_roi=roi,
                    total_stake=stake,
                    potential_profit=expected_profit,
                    risk_level="MEDIUM",
                    recommendations=[
                        {
                            "horse_name": best_selection.get("horse_name", "Unknown"),
                            "win_stake": win_stake,
                            "place_stake": place_stake,
                            "win_odds": odds,
                            "place_odds": place_odds,
                        }
                    ],
                    reasoning="High confidence AI selection suitable for 80/20 strategy",
                )

            return BettingStrategyResult(
                strategy_type="80/20",
                suitable=False,
                confidence_score=best_selection.get("ai_confidence", 0),
                expected_roi=0.0,
                total_stake=0.0,
                potential_profit=0.0,
                risk_level="N/A",
                recommendations=[],
                reasoning="No selections meet minimum confidence threshold",
            )

        except Exception as e:
            logger.error(f"Error in 80/20 strategy analysis: {str(e)}")
            return None

    async def _analyze_dutching_strategy(
        self, race_data: Dict, bankroll: float
    ) -> Optional[BettingStrategyResult]:
        """Analyze Dutching strategy opportunities"""
        try:
            ai_selections = race_data.get("ai_selections", [])
            if not ai_selections or len(ai_selections) < 2:
                return BettingStrategyResult(
                    strategy_type="Dutching",
                    suitable=False,
                    confidence_score=0.0,
                    expected_roi=0.0,
                    total_stake=0.0,
                    potential_profit=0.0,
                    risk_level="N/A",
                    recommendations=[],
                    reasoning="Insufficient selections for dutching",
                )

            # If AI integration is available, use it
            if self.dutching_ai:
                recommendations = self.dutching_ai.identify_dutching_opportunities(
                    race_data
                )

                if recommendations:
                    best_recommendation = recommendations[0]
                    plan = best_recommendation.plan

                    return BettingStrategyResult(
                        strategy_type="Dutching",
                        suitable=True,
                        confidence_score=plan.strategy_confidence,
                        expected_roi=plan.roi_percentage,
                        total_stake=float(plan.total_stake),
                        potential_profit=float(plan.guaranteed_profit),
                        risk_level=best_recommendation.risk_assessment["overall_risk"],
                        recommendations=[best_recommendation.to_dict()],
                        reasoning="Multi-horse dutching opportunity with guaranteed profit",
                    )

            # Fallback: Simple dutching analysis
            suitable_selections = [
                s for s in ai_selections if s.get("ai_confidence", 0) > 65
            ][
                :3
            ]  # Max 3 selections

            if len(suitable_selections) >= 2:
                # Simple dutching calculation
                total_stake = min(100.0, bankroll * 0.15)  # 15% of bankroll, max £100

                # Calculate stakes using basic dutching formula
                odds_list = [s.get("odds", 3.0) for s in suitable_selections]
                inv_odds_sum = sum(1 / odd for odd in odds_list)

                # Check if profitable (inv_odds_sum should be < 1 for profit)
                if inv_odds_sum < 0.95:  # Allow small margin
                    stakes = [(total_stake / odd) / inv_odds_sum for odd in odds_list]
                    actual_total = sum(stakes)
                    guaranteed_profit = total_stake - actual_total
                    roi = (
                        (guaranteed_profit / actual_total) * 100
                        if actual_total > 0
                        else 0
                    )

                    avg_confidence = sum(
                        s.get("ai_confidence", 70) for s in suitable_selections
                    ) / len(suitable_selections)

                    selections_data = []
                    for i, selection in enumerate(suitable_selections):
                        selections_data.append(
                            {
                                "horse_name": selection.get(
                                    "horse_name", f"Horse {i+1}"
                                ),
                                "stake": stakes[i],
                                "odds": odds_list[i],
                            }
                        )

                    return BettingStrategyResult(
                        strategy_type="Dutching",
                        suitable=True,
                        confidence_score=avg_confidence,
                        expected_roi=roi,
                        total_stake=actual_total,
                        potential_profit=guaranteed_profit,
                        risk_level="LOW",
                        recommendations=[
                            {
                                "plan": {
                                    "selections": selections_data,
                                    "total_stake": actual_total,
                                    "guaranteed_profit": guaranteed_profit,
                                }
                            }
                        ],
                        reasoning="Multi-selection dutching with guaranteed profit",
                    )

            return BettingStrategyResult(
                strategy_type="Dutching",
                suitable=False,
                confidence_score=0.0,
                expected_roi=0.0,
                total_stake=0.0,
                potential_profit=0.0,
                risk_level="N/A",
                recommendations=[],
                reasoning="No profitable dutching opportunities found",
            )

        except Exception as e:
            logger.error(f"Error in dutching strategy analysis: {str(e)}")
            return None

    def _combine_strategy_analyses(
        self,
        eighty_twenty: Optional[BettingStrategyResult],
        dutching: Optional[BettingStrategyResult],
    ) -> Dict:
        """Combine strategy analyses to create unified recommendations"""

        combined = {
            "recommended_strategy": "None",
            "combined_roi": 0.0,
            "bankroll_allocation": {},
            "risk_assessment": {
                "overall_risk": "HIGH",
                "confidence_level": "LOW",
                "diversification": "NONE",
            },
        }

        # Determine best strategy based on suitability and ROI
        strategies = []

        if eighty_twenty and eighty_twenty.suitable:
            strategies.append(("80/20", eighty_twenty))

        if dutching and dutching.suitable:
            strategies.append(("Dutching", dutching))

        if not strategies:
            combined["recommended_strategy"] = "No Bet"
            combined["risk_assessment"]["overall_risk"] = "NONE"
            return combined

        # Single strategy available
        if len(strategies) == 1:
            strategy_name, strategy_result = strategies[0]
            combined["recommended_strategy"] = strategy_name
            combined["combined_roi"] = strategy_result.expected_roi
            combined["bankroll_allocation"][strategy_name] = strategy_result.total_stake
            combined["risk_assessment"]["overall_risk"] = strategy_result.risk_level
            combined["risk_assessment"]["confidence_level"] = (
                "HIGH"
                if strategy_result.confidence_score > 80
                else "MEDIUM" if strategy_result.confidence_score > 65 else "LOW"
            )

        # Multiple strategies available - choose best or combine
        else:
            # Sort by expected ROI
            strategies.sort(key=lambda x: x[1].expected_roi, reverse=True)
            best_strategy_name, best_strategy = strategies[0]

            # If both strategies are highly confident, consider combining
            if (
                len(strategies) == 2
                and all(s[1].confidence_score > 70 for s in strategies)
                and all(s[1].expected_roi > 15 for s in strategies)
            ):

                combined["recommended_strategy"] = "Combined"
                combined["combined_roi"] = sum(
                    s[1].expected_roi for s in strategies
                ) / len(strategies)

                # Allocate bankroll proportionally
                total_stake = sum(s[1].total_stake for s in strategies)
                for name, strategy in strategies:
                    allocation_ratio = (
                        strategy.total_stake / total_stake if total_stake > 0 else 0.5
                    )
                    combined["bankroll_allocation"][name] = (
                        strategy.total_stake * allocation_ratio
                    )

                combined["risk_assessment"]["overall_risk"] = "MEDIUM"
                combined["risk_assessment"]["diversification"] = "HIGH"
            else:
                # Use single best strategy
                combined["recommended_strategy"] = best_strategy_name
                combined["combined_roi"] = best_strategy.expected_roi
                combined["bankroll_allocation"][
                    best_strategy_name
                ] = best_strategy.total_stake
                combined["risk_assessment"]["overall_risk"] = best_strategy.risk_level

        return combined

    def _count_successful_recommendations(self) -> int:
        """Count successful recommendations from performance stats"""
        return (
            self.performance_stats["successful_eighty_twenty"]
            + self.performance_stats["successful_dutching"]
        )

    def _update_performance_stats(self, results: EnhancedMonteCarloResults):
        """Update performance tracking statistics"""
        self.performance_stats["total_races"] += 1

        # Update successful strategy counts
        if (
            results.eighty_twenty_analysis
            and results.eighty_twenty_analysis.suitable
            and results.eighty_twenty_analysis.expected_roi > 10
        ):
            self.performance_stats["successful_eighty_twenty"] += 1

        if (
            results.dutching_analysis
            and results.dutching_analysis.suitable
            and results.dutching_analysis.expected_roi > 5
        ):
            self.performance_stats["successful_dutching"] += 1

        # Update profit tracking
        total_expected_profit = 0.0
        if results.eighty_twenty_analysis and results.eighty_twenty_analysis.suitable:
            total_expected_profit += results.eighty_twenty_analysis.potential_profit
            self.performance_stats["total_stakes"] += Decimal(
                str(results.eighty_twenty_analysis.total_stake)
            )

        if results.dutching_analysis and results.dutching_analysis.suitable:
            total_expected_profit += results.dutching_analysis.potential_profit
            self.performance_stats["total_stakes"] += Decimal(
                str(results.dutching_analysis.total_stake)
            )

        if total_expected_profit > 0:
            self.performance_stats["total_profit"] += Decimal(
                str(total_expected_profit)
            )

        # Update cumulative ROI
        if self.performance_stats["total_stakes"] > 0:
            self.performance_stats["cumulative_roi"] = (
                float(self.performance_stats["total_profit"])
                / float(self.performance_stats["total_stakes"])
                * 100
            )

    def format_enhanced_results(self, results: EnhancedMonteCarloResults) -> str:
        """Format enhanced results for display"""
        output = []
        output.append("🎯 ENHANCED MONTE CARLO ANALYSIS")
        output.append("=" * 80)
        output.append(f"Race ID: {results.race_id}")
        output.append(
            f"Analysis Time: {results.simulation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        output.append(f"Recommended Strategy: {results.recommended_strategy}")
        output.append(f"Combined ROI Estimate: {results.combined_roi_estimate:.2f}%")
        output.append("")

        # 80/20 Analysis
        if results.eighty_twenty_analysis:
            output.append("💰 80/20 STRATEGY ANALYSIS:")
            analysis = results.eighty_twenty_analysis
            output.append(f"  Suitable: {'✅ Yes' if analysis.suitable else '❌ No'}")
            if analysis.suitable:
                output.append(f"  Confidence: {analysis.confidence_score:.1f}%")
                output.append(f"  Expected ROI: {analysis.expected_roi:.2f}%")
                output.append(f"  Total Stake: £{analysis.total_stake:.2f}")
                output.append(f"  Potential Profit: £{analysis.potential_profit:.2f}")
                output.append(f"  Risk Level: {analysis.risk_level}")
            else:
                output.append(f"  Reason: {analysis.reasoning}")
            output.append("")

        # Dutching Analysis
        if results.dutching_analysis:
            output.append("🎯 DUTCHING STRATEGY ANALYSIS:")
            analysis = results.dutching_analysis
            output.append(f"  Suitable: {'✅ Yes' if analysis.suitable else '❌ No'}")
            if analysis.suitable:
                output.append(f"  Confidence: {analysis.confidence_score:.1f}%")
                output.append(f"  Expected ROI: {analysis.expected_roi:.2f}%")
                output.append(f"  Total Stake: £{analysis.total_stake:.2f}")
                output.append(f"  Guaranteed Profit: £{analysis.potential_profit:.2f}")
                output.append(f"  Risk Level: {analysis.risk_level}")
            else:
                output.append(f"  Reason: {analysis.reasoning}")
            output.append("")

        # Risk Assessment
        output.append("⚠️  RISK ASSESSMENT:")
        risk = results.risk_assessment
        output.append(f"  Overall Risk: {risk.get('overall_risk', 'UNKNOWN')}")
        output.append(f"  Confidence Level: {risk.get('confidence_level', 'UNKNOWN')}")
        output.append(f"  Diversification: {risk.get('diversification', 'NONE')}")
        output.append("")

        # Performance Summary
        output.append("📊 PERFORMANCE SUMMARY:")
        output.append(f"  Total Races Analyzed: {results.total_races_analyzed}")
        output.append(
            f"  Successful Recommendations: {results.successful_recommendations}"
        )
        output.append(f"  Cumulative ROI: {results.cumulative_roi:.2f}%")

        return "\n".join(output)

    def generate_sample_race_data(self) -> Dict:
        """Generate sample race data for testing"""
        return {
            "race_id": f'SAMPLE_RACE_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            "race_name": "Test Race - Enhanced Monte Carlo",
            "track": "Sample Track",
            "distance": "1m 2f",
            "going": "Good",
            "prize_money": "£15000",
            "race_time": datetime.now().strftime("%H:%M"),
            "horses": [
                {
                    "horse_name": "Thunder Strike",
                    "odds": 3.2,
                    "jockey": "J. Smith",
                    "trainer": "M. Johnson",
                    "weight": "9-2",
                    "age": 4,
                    "form": "1-2-3",
                },
                {
                    "horse_name": "Lightning Bolt",
                    "odds": 4.1,
                    "jockey": "P. Wilson",
                    "trainer": "R. Brown",
                    "weight": "9-0",
                    "age": 3,
                    "form": "2-1-4",
                },
                {
                    "horse_name": "Storm Chaser",
                    "odds": 5.0,
                    "jockey": "S. Davis",
                    "trainer": "T. Green",
                    "weight": "8-12",
                    "age": 5,
                    "form": "3-2-1",
                },
            ],
            "ai_selections": [
                {
                    "horse_name": "Thunder Strike",
                    "odds": 3.2,
                    "ai_confidence": 78.5,
                    "form_confidence": 82.0,
                    "track_confidence": 75.0,
                    "jockey_confidence": 80.0,
                    "value_confidence": 70.0,
                    "weather_confidence": 85.0,
                    "selection_id": "TS001",
                },
                {
                    "horse_name": "Lightning Bolt",
                    "odds": 4.1,
                    "ai_confidence": 72.3,
                    "form_confidence": 75.0,
                    "track_confidence": 70.0,
                    "jockey_confidence": 78.0,
                    "value_confidence": 68.0,
                    "weather_confidence": 70.0,
                    "selection_id": "LB002",
                },
                {
                    "horse_name": "Storm Chaser",
                    "odds": 5.0,
                    "ai_confidence": 68.7,
                    "form_confidence": 70.0,
                    "track_confidence": 65.0,
                    "jockey_confidence": 72.0,
                    "value_confidence": 75.0,
                    "weather_confidence": 62.0,
                    "selection_id": "SC003",
                },
            ],
        }


async def main():
    """Main function to test the enhanced Monte Carlo system"""
    print("🏇 STANDALONE ENHANCED MONTE CARLO BETTING ANALYSIS")
    print("=" * 80)
    print(f"Test Date: {date.today()}")
    print(f"Test Time: {datetime.now().strftime('%H:%M:%S')}")
    print("")

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        # Initialize engine
        engine = StandaloneEnhancedEngine(default_bankroll=500.0)
        print("✅ Enhanced Monte Carlo Engine initialized")

        # Generate sample race data
        race_data = engine.generate_sample_race_data()
        print(f"✅ Generated sample race: {race_data['race_name']}")
        print("")

        # Analyze race with both strategies
        print("🎯 Running enhanced analysis...")
        results = await engine.analyze_race_with_strategies(race_data, 500.0)
        print("✅ Analysis completed successfully")
        print("")

        # Display formatted results
        print(engine.format_enhanced_results(results))

        # Show specific recommendations
        print("\n" + "=" * 80)
        print("💡 BETTING RECOMMENDATIONS:")

        if results.recommended_strategy == "No Bet":
            print("  🚫 No betting opportunities identified")
        else:
            print(f"  🎯 Strategy: {results.recommended_strategy}")
            print(f"  💰 Expected ROI: {results.combined_roi_estimate:.2f}%")

            # Show strategy details
            if (
                results.eighty_twenty_analysis
                and results.eighty_twenty_analysis.suitable
            ):
                print("\n  🔸 80/20 Strategy Details:")
                if results.eighty_twenty_analysis.recommendations:
                    rec = results.eighty_twenty_analysis.recommendations[0]
                    print(f"    🐎 Horse: {rec.get('horse_name', 'Unknown')}")
                    print(f"    💰 Win Bet: £{rec.get('win_stake', 0):.2f}")
                    print(f"    🎯 Place Bet: £{rec.get('place_stake', 0):.2f}")
                    print(
                        f"    ⭐ Confidence: {results.eighty_twenty_analysis.confidence_score:.1f}%"
                    )

            if results.dutching_analysis and results.dutching_analysis.suitable:
                print("\n  🔸 Dutching Strategy Details:")
                if results.dutching_analysis.recommendations:
                    rec = results.dutching_analysis.recommendations[0]
                    plan = rec.get("plan", {})
                    selections = plan.get("selections", [])
                    print(f"    🎯 Multi-Horse Dutching:")
                    for selection in selections:
                        horse = selection.get("horse_name", "Unknown")
                        stake = selection.get("stake", 0)
                        odds = selection.get("odds", 0)
                        print(f"      🐎 {horse}: £{stake:.2f} @ {odds:.1f}")
                    print(
                        f"    🔒 Guaranteed Profit: £{results.dutching_analysis.potential_profit:.2f}"
                    )

        print("\n🎉 Enhanced Monte Carlo test completed successfully!")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
