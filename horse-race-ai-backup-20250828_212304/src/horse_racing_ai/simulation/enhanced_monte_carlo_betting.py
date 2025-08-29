"""
Enhanced Monte Carlo Integration with Betting Strategies
=======================================================

Integrates 80/20 and Dutching betting strategies with the Monte Carlo simulation
system to provide comprehensive betting analysis and recommendations.

Features:
- 80/20 Strategy integration for single-horse selections
- Dutching Strategy integration for multi-horse opportunities
- Real-time race data processing
- Performance tracking and ROI analysis
- Risk assessment and bankroll management

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, date
from decimal import Decimal
import numpy as np

# Import existing Monte Carlo components
from .monte_carlo_integration import MonteCarloIntegration
from .monte_carlo_simulator_with_real_data import RealDataMonteCarloSimulator

# Import betting strategies
from horse_racing_ai.betting.eighty_twenty_strategy import (
    EightyTwentyStrategy,
    EightyTwentyBet,
    StakeAllocation,
)
from horse_racing_ai.betting.reduced_stake_dutching import (
    ReducedStakeDutching,
    DutchingResult,
    DutchingPlan,
)
from horse_racing_ai.integration.eighty_twenty_ai_integration import (
    EightyTwentyAIIntegration,
)
from horse_racing_ai.integration.dutching_ai_integration import DutchingAIIntegration

# Import database components
from horse_racing_ai.database.monte_carlo_database_manager import (
    MonteCarloDbManager,
    MonteCarloBettingRecommendation,
)

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

    # Standard Monte Carlo results
    monte_carlo_analysis: Dict

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


class EnhancedMonteCarloEngine:
    """
    Enhanced Monte Carlo engine with integrated betting strategies.

    Combines Monte Carlo simulation with 80/20 and Dutching strategies
    to provide comprehensive race analysis and betting recommendations.
    """

    def __init__(self, default_bankroll: float = 1000.0, enable_real_data: bool = True):
        """
        Initialize enhanced Monte Carlo engine

        Args:
            default_bankroll: Default bankroll for betting calculations
            enable_real_data: Whether to enable real data collection
        """
        self.default_bankroll = default_bankroll
        self.enable_real_data = enable_real_data

        # Initialize core components
        self.monte_carlo = MonteCarloIntegration()
        self.real_data_simulator = RealDataMonteCarloSimulator(
            simulations=10000, random_seed=42
        )

        # Initialize betting strategies
        self.eighty_twenty_strategy = EightyTwentyStrategy(
            min_confidence=70.0, allocation_mode=StakeAllocation.CONSERVATIVE
        )
        self.dutching_strategy = ReducedStakeDutching(
            min_profit_margin=8.0, min_ai_confidence=65.0
        )

        # Initialize AI integrations
        self.eighty_twenty_ai = EightyTwentyAIIntegration(
            min_confidence=70.0, value_threshold=15.0
        )
        self.dutching_ai = DutchingAIIntegration(
            min_ai_confidence=65.0, min_profit_margin=8.0
        )

        # Initialize database manager
        self.db_manager = MonteCarloDbManager()

        # Performance tracking
        self.performance_stats = {
            "total_races": 0,
            "successful_eighty_twenty": 0,
            "successful_dutching": 0,
            "total_profit": Decimal("0"),
            "total_stakes": Decimal("0"),
            "cumulative_roi": 0.0,
        }

        logger.info("Enhanced Monte Carlo Engine initialized with betting strategies")

    async def analyze_race_with_strategies(
        self, race_data: Dict, bankroll: Optional[float] = None
    ) -> EnhancedMonteCarloResults:
        """
        Perform comprehensive race analysis with Monte Carlo simulation
        and betting strategy recommendations

        Args:
            race_data: Complete race data including horses and AI selections
            bankroll: Available bankroll for betting (uses default if None)

        Returns:
            Enhanced results with strategy recommendations
        """
        start_time = datetime.now()
        race_id = race_data.get(
            "race_id", f"RACE_{start_time.strftime('%Y%m%d_%H%M%S')}"
        )

        if bankroll is None:
            bankroll = self.default_bankroll

        logger.info(f"Starting enhanced analysis for race {race_id}")

        try:
            # Step 1: Run Monte Carlo simulation
            horses = race_data.get("horses", [])
            monte_carlo_results = await self.monte_carlo.run_simulation(
                horses, mode="advanced"
            )

            # Step 2: Analyze 80/20 strategy opportunities
            eighty_twenty_result = await self._analyze_eighty_twenty_strategy(
                race_data, bankroll
            )

            # Step 3: Analyze Dutching strategy opportunities
            dutching_result = await self._analyze_dutching_strategy(race_data, bankroll)

            # Step 4: Combine analyses and create recommendations
            combined_analysis = self._combine_strategy_analyses(
                monte_carlo_results, eighty_twenty_result, dutching_result
            )

            # Step 5: Create enhanced results
            enhanced_results = EnhancedMonteCarloResults(
                race_id=race_id,
                simulation_timestamp=start_time,
                monte_carlo_analysis=monte_carlo_results,
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

            # Step 6: Store results in database
            await self._store_enhanced_results(enhanced_results)

            # Step 7: Update performance tracking
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
                return None

            # Use AI integration to analyze opportunities
            recommendations = self.eighty_twenty_ai.analyze_race_for_eighty_twenty(
                race_data, Decimal(str(bankroll))
            )

            if not recommendations:
                return BettingStrategyResult(
                    strategy_type="80/20",
                    suitable=False,
                    confidence_score=0.0,
                    expected_roi=0.0,
                    total_stake=0.0,
                    potential_profit=0.0,
                    risk_level="N/A",
                    recommendations=[],
                    reasoning="No suitable 80/20 opportunities found",
                )

            # Get best recommendation
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

        except Exception as e:
            logger.error(f"Error in 80/20 strategy analysis: {str(e)}")
            return None

    async def _analyze_dutching_strategy(
        self, race_data: Dict, bankroll: float
    ) -> Optional[BettingStrategyResult]:
        """Analyze Dutching strategy opportunities"""
        try:
            # Use AI integration to analyze opportunities
            recommendations = self.dutching_ai.identify_dutching_opportunities(
                race_data
            )

            if not recommendations:
                return BettingStrategyResult(
                    strategy_type="Dutching",
                    suitable=False,
                    confidence_score=0.0,
                    expected_roi=0.0,
                    total_stake=0.0,
                    potential_profit=0.0,
                    risk_level="N/A",
                    recommendations=[],
                    reasoning="No suitable dutching opportunities found",
                )

            # Get best recommendation
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

        except Exception as e:
            logger.error(f"Error in dutching strategy analysis: {str(e)}")
            return None

    def _combine_strategy_analyses(
        self,
        monte_carlo: Dict,
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

    async def _store_enhanced_results(self, results: EnhancedMonteCarloResults):
        """Store enhanced results in database"""
        try:
            # Store Monte Carlo simulation results
            simulation_id = await self.db_manager.store_simulation_analysis(
                simulation_id=0,  # Will be generated
                analysis_data=results.monte_carlo_analysis,
            )

            # Create betting recommendations
            recommendations = []

            # Add 80/20 recommendations
            if (
                results.eighty_twenty_analysis
                and results.eighty_twenty_analysis.suitable
            ):

                for rec_data in results.eighty_twenty_analysis.recommendations:
                    recommendation = MonteCarloBettingRecommendation(
                        simulation_id=simulation_id,
                        race_id=results.race_id,
                        horse_name=rec_data.get("horse_name", ""),
                        bet_type="80/20",
                        recommended_stake=results.eighty_twenty_analysis.total_stake,
                        recommended_odds=rec_data.get("win_odds", 0.0),
                        expected_value=results.eighty_twenty_analysis.expected_roi,
                        confidence_score=results.eighty_twenty_analysis.confidence_score,
                        risk_rating=results.eighty_twenty_analysis.risk_level,
                        betting_value=results.eighty_twenty_analysis.potential_profit,
                        recommendation_strength=(
                            "STRONG"
                            if results.eighty_twenty_analysis.confidence_score > 80
                            else "MODERATE"
                        ),
                    )
                    recommendations.append(recommendation)

            # Add Dutching recommendations
            if results.dutching_analysis and results.dutching_analysis.suitable:

                for rec_data in results.dutching_analysis.recommendations:
                    plan_data = rec_data.get("plan", {})
                    selections = plan_data.get("selections", [])

                    for selection in selections:
                        recommendation = MonteCarloBettingRecommendation(
                            simulation_id=simulation_id,
                            race_id=results.race_id,
                            horse_name=selection.get("horse_name", ""),
                            bet_type="Dutching",
                            recommended_stake=selection.get("stake", 0.0),
                            recommended_odds=selection.get("odds", 0.0),
                            expected_value=results.dutching_analysis.expected_roi,
                            confidence_score=results.dutching_analysis.confidence_score,
                            risk_rating=results.dutching_analysis.risk_level,
                            betting_value=results.dutching_analysis.potential_profit,
                            recommendation_strength=(
                                "STRONG"
                                if results.dutching_analysis.confidence_score > 75
                                else "MODERATE"
                            ),
                        )
                        recommendations.append(recommendation)

            # Store recommendations
            if recommendations:
                await self.db_manager.store_betting_recommendations(recommendations)
                logger.info(f"Stored {len(recommendations)} betting recommendations")

        except Exception as e:
            logger.error(f"Error storing enhanced results: {str(e)}")

    def _count_successful_recommendations(self) -> int:
        """Count successful recommendations from performance stats"""
        return (
            self.performance_stats["successful_eighty_twenty"]
            + self.performance_stats["successful_dutching"]
        )

    def _update_performance_stats(self, results: EnhancedMonteCarloResults):
        """Update performance tracking statistics"""
        self.performance_stats["total_races"] += 1

        # Update successful strategy counts (simplified tracking)
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

    async def get_todays_races(self) -> List[Dict]:
        """Get today's race data for analysis"""
        try:
            if self.enable_real_data and self.real_data_simulator.data_collector:
                # Use real data collector to get today's races
                races = await self.real_data_simulator.collect_race_data()
                return races
            else:
                # Return sample data for testing
                return self._generate_sample_race_data()
        except Exception as e:
            logger.error(f"Error getting today's races: {str(e)}")
            return self._generate_sample_race_data()

    def _generate_sample_race_data(self) -> List[Dict]:
        """Generate sample race data for testing"""
        return [
            {
                "race_id": f'SAMPLE_RACE_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                "race_name": "Test Race",
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
        ]
