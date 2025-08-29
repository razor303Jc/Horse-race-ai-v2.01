"""
Enhanced Monte Carlo Betting Analysis - Today's Races
====================================================

Main script to run enhanced Monte Carlo analysis with integrated betting strategies
on today's race data. Combines 80/20 and Dutching strategies with real data.

Usage:
    python enhanced_monte_carlo_analysis.py [--bankroll AMOUNT] [--debug]

Features:
- Real-time race data collection
- Integrated 80/20 and Dutching analysis
- Monte Carlo simulation with 10,000 iterations
- Comprehensive ROI and risk assessment
- Performance tracking and reporting

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from horse_racing_ai.simulation.enhanced_monte_carlo_betting import (
    EnhancedMonteCarloEngine,
    EnhancedMonteCarloResults,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"monte_carlo_analysis_{date.today()}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class TodaysRaceAnalyzer:
    """Main class for analyzing today's races with enhanced Monte Carlo system"""

    def __init__(self, bankroll: float = 1000.0, debug: bool = False):
        """
        Initialize race analyzer

        Args:
            bankroll: Available bankroll for betting analysis
            debug: Enable debug logging
        """
        self.bankroll = bankroll
        self.debug = debug

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize enhanced Monte Carlo engine
        self.engine = EnhancedMonteCarloEngine(
            default_bankroll=bankroll, enable_real_data=True
        )

        # Results storage
        self.analysis_results = []

        logger.info(f"Initialized race analyzer with £{bankroll:.2f} bankroll")

    async def analyze_todays_races(self) -> None:
        """Analyze all of today's races with enhanced Monte Carlo system"""
        start_time = datetime.now()

        print("🏇 ENHANCED MONTE CARLO BETTING ANALYSIS")
        print("=" * 80)
        print(f"Analysis Date: {date.today()}")
        print(f"Available Bankroll: £{self.bankroll:.2f}")
        print(f"Start Time: {start_time.strftime('%H:%M:%S')}")
        print("")

        try:
            # Get today's races
            print("📊 Collecting today's race data...")
            races = await self.engine.get_todays_races()

            if not races:
                print("❌ No races found for today")
                return

            print(f"✅ Found {len(races)} races to analyze")
            print("")

            # Analyze each race
            for i, race_data in enumerate(races, 1):
                race_id = race_data.get("race_id", f"RACE_{i}")
                race_name = race_data.get("race_name", f"Race {i}")

                print(f"🎯 ANALYZING RACE {i}/{len(races)}: {race_name}")
                print("-" * 60)

                try:
                    # Run enhanced analysis
                    results = await self.engine.analyze_race_with_strategies(
                        race_data, self.bankroll
                    )

                    # Store results
                    self.analysis_results.append(results)

                    # Display results
                    print(self.engine.format_enhanced_results(results))
                    print("")

                    # Show betting recommendations
                    self._display_betting_recommendations(results)
                    print("")

                except Exception as e:
                    logger.error(f"Error analyzing race {race_id}: {str(e)}")
                    print(f"❌ Error analyzing race {race_id}: {str(e)}")
                    print("")

            # Generate overall summary
            await self._generate_overall_summary()

        except Exception as e:
            logger.error(f"Error in today's race analysis: {str(e)}")
            print(f"❌ Error in analysis: {str(e)}")

    def _display_betting_recommendations(self, results: EnhancedMonteCarloResults):
        """Display specific betting recommendations"""
        print("💡 BETTING RECOMMENDATIONS:")

        if results.recommended_strategy == "No Bet":
            print("  🚫 No betting opportunities identified")
            print("  💡 Reason: No strategies meet minimum confidence/ROI thresholds")
            return

        print(f"  🎯 Strategy: {results.recommended_strategy}")
        print(f"  💰 Expected ROI: {results.combined_roi_estimate:.2f}%")

        # Show specific recommendations
        if results.recommended_strategy == "80/20" and results.eighty_twenty_analysis:
            self._show_eighty_twenty_recommendations(results.eighty_twenty_analysis)

        elif results.recommended_strategy == "Dutching" and results.dutching_analysis:
            self._show_dutching_recommendations(results.dutching_analysis)

        elif results.recommended_strategy == "Combined":
            print("  📊 Combined Strategy Allocation:")
            for strategy, allocation in results.bankroll_allocation.items():
                print(f"    {strategy}: £{allocation:.2f}")

            if (
                results.eighty_twenty_analysis
                and results.eighty_twenty_analysis.suitable
            ):
                print("\n  🔸 80/20 Component:")
                self._show_eighty_twenty_recommendations(
                    results.eighty_twenty_analysis, indent="    "
                )

            if results.dutching_analysis and results.dutching_analysis.suitable:
                print("\n  🔸 Dutching Component:")
                self._show_dutching_recommendations(
                    results.dutching_analysis, indent="    "
                )

    def _show_eighty_twenty_recommendations(self, analysis, indent="  "):
        """Show 80/20 betting recommendations"""
        if not analysis.recommendations:
            return

        rec = analysis.recommendations[0]
        print(f"{indent}🐎 Horse: {rec.get('horse_name', 'Unknown')}")
        print(
            f"{indent}💰 Win Bet: £{rec.get('win_stake', 0):.2f} @ {rec.get('win_odds', 0):.1f}"
        )
        print(
            f"{indent}🎯 Place Bet: £{rec.get('place_stake', 0):.2f} @ {rec.get('place_odds', 0):.1f}"
        )
        print(f"{indent}📊 Total Stake: £{analysis.total_stake:.2f}")
        print(f"{indent}⭐ Confidence: {analysis.confidence_score:.1f}%")

    def _show_dutching_recommendations(self, analysis, indent="  "):
        """Show Dutching betting recommendations"""
        if not analysis.recommendations:
            return

        rec = analysis.recommendations[0]
        plan = rec.get("plan", {})
        selections = plan.get("selections", [])

        print(f"{indent}🎯 Multi-Horse Dutching:")
        for selection in selections:
            horse = selection.get("horse_name", "Unknown")
            stake = selection.get("stake", 0)
            odds = selection.get("odds", 0)
            print(f"{indent}  🐎 {horse}: £{stake:.2f} @ {odds:.1f}")

        print(f"{indent}💰 Total Stake: £{analysis.total_stake:.2f}")
        print(f"{indent}🔒 Guaranteed Profit: £{analysis.potential_profit:.2f}")
        print(f"{indent}⭐ Confidence: {analysis.confidence_score:.1f}%")

    async def _generate_overall_summary(self):
        """Generate overall analysis summary"""
        if not self.analysis_results:
            print("❌ No results to summarize")
            return

        print("📈 OVERALL ANALYSIS SUMMARY")
        print("=" * 80)

        # Calculate summary statistics
        total_races = len(self.analysis_results)
        profitable_strategies = 0
        total_potential_profit = 0.0
        total_required_stakes = 0.0
        strategy_counts = {}

        for result in self.analysis_results:
            if result.recommended_strategy != "No Bet":
                profitable_strategies += 1

                # Count strategy types
                strategy = result.recommended_strategy
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

                # Calculate potential profits
                if (
                    result.eighty_twenty_analysis
                    and result.eighty_twenty_analysis.suitable
                ):
                    total_potential_profit += (
                        result.eighty_twenty_analysis.potential_profit
                    )
                    total_required_stakes += result.eighty_twenty_analysis.total_stake

                if result.dutching_analysis and result.dutching_analysis.suitable:
                    total_potential_profit += result.dutching_analysis.potential_profit
                    total_required_stakes += result.dutching_analysis.total_stake

        # Display summary
        print(f"📊 Races Analyzed: {total_races}")
        print(f"💰 Profitable Opportunities: {profitable_strategies}")
        print(f"📈 Success Rate: {(profitable_strategies/total_races)*100:.1f}%")
        print("")

        print("🎯 Strategy Distribution:")
        for strategy, count in strategy_counts.items():
            percentage = (count / total_races) * 100
            print(f"  {strategy}: {count} races ({percentage:.1f}%)")
        print("")

        if total_required_stakes > 0:
            overall_roi = (total_potential_profit / total_required_stakes) * 100
            print(f"💵 Total Required Stakes: £{total_required_stakes:.2f}")
            print(f"💰 Total Potential Profit: £{total_potential_profit:.2f}")
            print(f"📈 Overall ROI Estimate: {overall_roi:.2f}%")
            print("")

            # Bankroll utilization
            bankroll_usage = (total_required_stakes / self.bankroll) * 100
            print(f"🏦 Bankroll Utilization: {bankroll_usage:.1f}%")

            if bankroll_usage > 100:
                print("⚠️  WARNING: Required stakes exceed available bankroll!")
                print("💡 Consider reducing position sizes or selecting fewer races")

        print("")
        print("⏰ Analysis completed at", datetime.now().strftime("%H:%M:%S"))


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Enhanced Monte Carlo Betting Analysis for Today's Races"
    )
    parser.add_argument(
        "--bankroll",
        type=float,
        default=1000.0,
        help="Available bankroll for betting (default: £1000)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    try:
        # Create analyzer
        analyzer = TodaysRaceAnalyzer(bankroll=args.bankroll, debug=args.debug)

        # Run analysis
        await analyzer.analyze_todays_races()

    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print(f"❌ Fatal error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
