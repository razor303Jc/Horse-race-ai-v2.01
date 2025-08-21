#!/usr/bin/env python3
"""
Enhanced Monte Carlo Strategy Backtest using Real Results
=========================================================

Backtests the integrated 80/20 and Dutching strategies using actual race results
to validate performance and ROI calculations with real-world data.

Features:
- Real race results parsing and analysis
- Actual winning horse identification
- Precise profit/loss calculation based on real outcomes
- Strategy performance validation
- Comprehensive ROI and success rate analysis

Usage: python enhanced_monte_carlo_backtest.py [--bankroll AMOUNT]
"""

import pandas as pd
import asyncio
import logging
import sys
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from decimal import Decimal

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"backtest_results_{date.today()}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class RaceResultsParser:
    """Parser for real race results data"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.races_df = None
        self.records_df = None
        self.horses_df = None

    def load_data(self):
        """Load race results data from CSV files"""
        try:
            # Load race data
            races_file = self.data_path / "results_data/races/races.csv"
            self.races_df = pd.read_csv(races_file)
            logger.info(f"Loaded {len(self.races_df)} races")

            # Load race records (individual horse results)
            records_file = self.data_path / "results_data/records/records.csv"
            self.records_df = pd.read_csv(records_file)
            logger.info(f"Loaded {len(self.records_df)} race records")

            # Load horse data if available
            horses_file = self.data_path / "results_data/horses/horses.csv"
            if horses_file.exists():
                self.horses_df = pd.read_csv(horses_file)
                logger.info(f"Loaded {len(self.horses_df)} horse records")

            return True

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False

    def get_race_results(self, race_id: str) -> Dict:
        """Get complete race results for a specific race"""
        try:
            # Get race information
            race_info = self.races_df[self.races_df["Race_ID"] == int(race_id)].iloc[0]

            # Get all horses in this race
            race_records = self.records_df[
                self.records_df["Race_ID"] == int(race_id)
            ].copy()
            race_records = race_records.sort_values("Place")

            # Build race result structure
            race_result = {
                "race_id": race_id,
                "race_name": race_info["Race_name"],
                "course": race_info["Course"],
                "date": race_info["Date"],
                "race_time": race_info["race_time"],
                "distance": race_info["Distance"],
                "class": race_info["Class"],
                "prize": race_info["Prize"],
                "going": race_info["Surface"],
                "runners": int(race_info["Runners"]),
                "horses": [],
            }

            # Add horse details
            for _, record in race_records.iterrows():
                horse_data = {
                    "horse_name": record["Name"],
                    "place": int(record["Place"]),
                    "draw": record["Draw"] if pd.notna(record["Draw"]) else None,
                    "age": int(record["Age"]),
                    "weight": record["weight_uk"],
                    "jockey": record["jockey"],
                    "trainer": record["trainer"],
                    "sp_odds": float(record["SP"]) if pd.notna(record["SP"]) else None,
                    "favourite": record["fav"] if pd.notna(record["fav"]) else None,
                    "distance_beaten": (
                        record["Distance_btn"]
                        if pd.notna(record["Distance_btn"])
                        else 0
                    ),
                }
                race_result["horses"].append(horse_data)

            return race_result

        except Exception as e:
            logger.error(f"Error getting race results for {race_id}: {str(e)}")
            return None

    def get_all_races(self) -> List[str]:
        """Get list of all available race IDs"""
        return [str(race_id) for race_id in self.races_df["Race_ID"].unique()]


class StrategyBacktester:
    """Backtester for betting strategies using real results"""

    def __init__(self, bankroll: float = 1000.0):
        self.initial_bankroll = bankroll
        self.current_bankroll = bankroll

        # Strategy results tracking
        self.results = {
            "eighty_twenty": {
                "total_races": 0,
                "successful_races": 0,
                "total_stakes": Decimal("0"),
                "total_returns": Decimal("0"),
                "net_profit": Decimal("0"),
                "roi_percentage": 0.0,
                "win_rate": 0.0,
                "place_rate": 0.0,
                "bets": [],
            },
            "dutching": {
                "total_races": 0,
                "successful_races": 0,
                "total_stakes": Decimal("0"),
                "total_returns": Decimal("0"),
                "net_profit": Decimal("0"),
                "roi_percentage": 0.0,
                "success_rate": 0.0,
                "bets": [],
            },
            "overall": {
                "total_races": 0,
                "profitable_races": 0,
                "total_stakes": Decimal("0"),
                "total_returns": Decimal("0"),
                "net_profit": Decimal("0"),
                "roi_percentage": 0.0,
                "success_rate": 0.0,
            },
        }

    def simulate_eighty_twenty_bet(
        self, race_result: Dict, confidence: float = 75.0
    ) -> Dict:
        """Simulate an 80/20 bet on the best horse based on odds and calculate real returns"""
        horses = race_result["horses"]

        # Find the favourite (lowest odds) as our selection
        valid_horses = [
            h for h in horses if h["sp_odds"] is not None and h["sp_odds"] > 0
        ]
        if not valid_horses:
            return None

        # Select horse with best odds (favourite)
        selected_horse = min(valid_horses, key=lambda x: x["sp_odds"])

        # Calculate stake (conservative approach)
        base_stake = min(50.0, self.current_bankroll * 0.05)  # 5% of bankroll, max £50
        win_stake = base_stake * 0.2  # 20% on win
        place_stake = base_stake * 0.8  # 80% on place
        total_stake = win_stake + place_stake

        # Get actual results
        horse_place = selected_horse["place"]
        win_odds = selected_horse["sp_odds"]

        # Estimate place odds (typically 1/4 to 1/5 of win odds for favourites)
        if win_odds <= 3.0:
            place_odds = 1.0 + (
                (win_odds - 1.0) * 0.25
            )  # 1/4 odds for short-priced favourites
        else:
            place_odds = 1.0 + ((win_odds - 1.0) * 0.2)  # 1/5 odds for longer prices

        # Calculate returns
        win_return = 0.0
        place_return = 0.0

        if horse_place == 1:  # Won
            win_return = win_stake * win_odds
            place_return = place_stake * place_odds
        elif horse_place <= 3:  # Placed (assuming 3 places for most races)
            place_return = place_stake * place_odds

        total_return = win_return + place_return
        net_profit = total_return - total_stake

        bet_result = {
            "strategy": "80/20",
            "race_id": race_result["race_id"],
            "horse_name": selected_horse["horse_name"],
            "confidence": confidence,
            "win_stake": win_stake,
            "place_stake": place_stake,
            "total_stake": total_stake,
            "win_odds": win_odds,
            "place_odds": place_odds,
            "actual_place": horse_place,
            "win_return": win_return,
            "place_return": place_return,
            "total_return": total_return,
            "net_profit": net_profit,
            "successful": net_profit > 0,
            "roi": (net_profit / total_stake * 100) if total_stake > 0 else 0,
        }

        return bet_result

    def simulate_dutching_bet(self, race_result: Dict, max_selections: int = 3) -> Dict:
        """Simulate a dutching bet using the top 3 horses by odds"""
        horses = race_result["horses"]

        # Get valid horses with odds
        valid_horses = [
            h for h in horses if h["sp_odds"] is not None and h["sp_odds"] > 0
        ]
        if len(valid_horses) < 2:
            return None

        # Select top horses by odds (favourites)
        selected_horses = sorted(valid_horses, key=lambda x: x["sp_odds"])[
            :max_selections
        ]

        # Calculate dutching stakes
        total_stake = min(75.0, self.current_bankroll * 0.1)  # 10% of bankroll, max £75

        # Basic dutching calculation
        odds_list = [h["sp_odds"] for h in selected_horses]
        inv_odds_sum = sum(1 / odd for odd in odds_list)

        # Check if dutching is profitable (sum of inverse odds < 1)
        if inv_odds_sum >= 0.98:  # Not profitable enough
            return None

        # Calculate individual stakes
        stakes = [(total_stake / odd) / inv_odds_sum for odd in odds_list]
        actual_total_stake = sum(stakes)

        # Determine winning selection
        winning_horse = None
        winning_stake = 0
        winning_odds = 0

        for i, horse in enumerate(selected_horses):
            if horse["place"] == 1:  # This horse won
                winning_horse = horse
                winning_stake = stakes[i]
                winning_odds = horse["sp_odds"]
                break

        # Calculate returns
        if winning_horse:
            total_return = winning_stake * winning_odds
            net_profit = total_return - actual_total_stake
        else:
            total_return = 0
            net_profit = -actual_total_stake

        bet_result = {
            "strategy": "Dutching",
            "race_id": race_result["race_id"],
            "selections": [
                {
                    "horse_name": horse["horse_name"],
                    "odds": horse["sp_odds"],
                    "stake": stakes[i],
                    "place": horse["place"],
                }
                for i, horse in enumerate(selected_horses)
            ],
            "total_stake": actual_total_stake,
            "winning_horse": winning_horse["horse_name"] if winning_horse else None,
            "total_return": total_return,
            "net_profit": net_profit,
            "successful": net_profit > 0,
            "roi": (
                (net_profit / actual_total_stake * 100) if actual_total_stake > 0 else 0
            ),
        }

        return bet_result

    def process_race(self, race_result: Dict):
        """Process a single race with both strategies"""
        if not race_result or len(race_result["horses"]) < 2:
            return

        logger.info(
            f"Processing race {race_result['race_id']}: {race_result['race_name']}"
        )

        # Test 80/20 strategy
        eighty_twenty_bet = self.simulate_eighty_twenty_bet(race_result)
        if eighty_twenty_bet:
            self.results["eighty_twenty"]["bets"].append(eighty_twenty_bet)
            self.results["eighty_twenty"]["total_races"] += 1
            self.results["eighty_twenty"]["total_stakes"] += Decimal(
                str(eighty_twenty_bet["total_stake"])
            )
            self.results["eighty_twenty"]["total_returns"] += Decimal(
                str(eighty_twenty_bet["total_return"])
            )

            if eighty_twenty_bet["successful"]:
                self.results["eighty_twenty"]["successful_races"] += 1

        # Test Dutching strategy
        dutching_bet = self.simulate_dutching_bet(race_result)
        if dutching_bet:
            self.results["dutching"]["bets"].append(dutching_bet)
            self.results["dutching"]["total_races"] += 1
            self.results["dutching"]["total_stakes"] += Decimal(
                str(dutching_bet["total_stake"])
            )
            self.results["dutching"]["total_returns"] += Decimal(
                str(dutching_bet["total_return"])
            )

            if dutching_bet["successful"]:
                self.results["dutching"]["successful_races"] += 1

        # Update overall stats
        if eighty_twenty_bet or dutching_bet:
            self.results["overall"]["total_races"] += 1

            # Choose best strategy for this race
            best_profit = 0
            if eighty_twenty_bet and dutching_bet:
                if eighty_twenty_bet["net_profit"] > dutching_bet["net_profit"]:
                    best_profit = eighty_twenty_bet["net_profit"]
                else:
                    best_profit = dutching_bet["net_profit"]
            elif eighty_twenty_bet:
                best_profit = eighty_twenty_bet["net_profit"]
            elif dutching_bet:
                best_profit = dutching_bet["net_profit"]

            if best_profit > 0:
                self.results["overall"]["profitable_races"] += 1

    def calculate_final_stats(self):
        """Calculate final performance statistics"""
        # 80/20 strategy stats
        if self.results["eighty_twenty"]["total_races"] > 0:
            eighty_twenty = self.results["eighty_twenty"]
            eighty_twenty["net_profit"] = (
                eighty_twenty["total_returns"] - eighty_twenty["total_stakes"]
            )
            eighty_twenty["roi_percentage"] = float(
                eighty_twenty["net_profit"] / eighty_twenty["total_stakes"] * 100
            )
            eighty_twenty["win_rate"] = (
                eighty_twenty["successful_races"] / eighty_twenty["total_races"]
            ) * 100

        # Dutching strategy stats
        if self.results["dutching"]["total_races"] > 0:
            dutching = self.results["dutching"]
            dutching["net_profit"] = (
                dutching["total_returns"] - dutching["total_stakes"]
            )
            dutching["roi_percentage"] = float(
                dutching["net_profit"] / dutching["total_stakes"] * 100
            )
            dutching["success_rate"] = (
                dutching["successful_races"] / dutching["total_races"]
            ) * 100

        # Overall stats
        if self.results["overall"]["total_races"] > 0:
            overall = self.results["overall"]
            overall["total_stakes"] = (
                self.results["eighty_twenty"]["total_stakes"]
                + self.results["dutching"]["total_stakes"]
            )
            overall["total_returns"] = (
                self.results["eighty_twenty"]["total_returns"]
                + self.results["dutching"]["total_returns"]
            )
            overall["net_profit"] = overall["total_returns"] - overall["total_stakes"]
            overall["roi_percentage"] = float(
                overall["net_profit"] / overall["total_stakes"] * 100
            )
            overall["success_rate"] = (
                overall["profitable_races"] / overall["total_races"]
            ) * 100

    def generate_report(self) -> str:
        """Generate comprehensive backtest report"""
        report = []
        report.append("🏇 ENHANCED MONTE CARLO STRATEGY BACKTEST RESULTS")
        report.append("=" * 80)
        report.append(f"Backtest Date: {date.today()}")
        report.append(f"Initial Bankroll: £{self.initial_bankroll:.2f}")
        report.append("")

        # 80/20 Strategy Results
        eighty_twenty = self.results["eighty_twenty"]
        if eighty_twenty["total_races"] > 0:
            report.append("💰 80/20 STRATEGY RESULTS:")
            report.append(f"  Races Analyzed: {eighty_twenty['total_races']}")
            report.append(f"  Successful Bets: {eighty_twenty['successful_races']}")
            report.append(f"  Win Rate: {eighty_twenty['win_rate']:.1f}%")
            report.append(
                f"  Total Stakes: £{float(eighty_twenty['total_stakes']):.2f}"
            )
            report.append(
                f"  Total Returns: £{float(eighty_twenty['total_returns']):.2f}"
            )
            report.append(f"  Net Profit: £{float(eighty_twenty['net_profit']):.2f}")
            report.append(f"  ROI: {eighty_twenty['roi_percentage']:.2f}%")
            report.append("")

        # Dutching Strategy Results
        dutching = self.results["dutching"]
        if dutching["total_races"] > 0:
            report.append("🎯 DUTCHING STRATEGY RESULTS:")
            report.append(f"  Races Analyzed: {dutching['total_races']}")
            report.append(f"  Successful Bets: {dutching['successful_races']}")
            report.append(f"  Success Rate: {dutching['success_rate']:.1f}%")
            report.append(f"  Total Stakes: £{float(dutching['total_stakes']):.2f}")
            report.append(f"  Total Returns: £{float(dutching['total_returns']):.2f}")
            report.append(f"  Net Profit: £{float(dutching['net_profit']):.2f}")
            report.append(f"  ROI: {dutching['roi_percentage']:.2f}%")
            report.append("")

        # Overall Results
        overall = self.results["overall"]
        if overall["total_races"] > 0:
            report.append("📊 OVERALL BACKTEST RESULTS:")
            report.append(f"  Total Races: {overall['total_races']}")
            report.append(f"  Profitable Races: {overall['profitable_races']}")
            report.append(f"  Success Rate: {overall['success_rate']:.1f}%")
            report.append(f"  Combined Stakes: £{float(overall['total_stakes']):.2f}")
            report.append(f"  Combined Returns: £{float(overall['total_returns']):.2f}")
            report.append(f"  Combined Profit: £{float(overall['net_profit']):.2f}")
            report.append(f"  Combined ROI: {overall['roi_percentage']:.2f}%")
            report.append("")

        # Best and worst bets
        all_bets = eighty_twenty["bets"] + dutching["bets"]
        if all_bets:
            best_bet = max(all_bets, key=lambda x: x["net_profit"])
            worst_bet = min(all_bets, key=lambda x: x["net_profit"])

            report.append("🏆 BEST BET:")
            report.append(
                f"  Race: {best_bet['race_id']} | Strategy: {best_bet['strategy']}"
            )
            if best_bet["strategy"] == "80/20":
                report.append(
                    f"  Horse: {best_bet['horse_name']} (Place: {best_bet['actual_place']})"
                )
            else:
                winner = best_bet.get("winning_horse", "None")
                report.append(f"  Winning Horse: {winner}")
            report.append(
                f"  Profit: £{best_bet['net_profit']:.2f} | ROI: {best_bet['roi']:.1f}%"
            )
            report.append("")

            report.append("📉 WORST BET:")
            report.append(
                f"  Race: {worst_bet['race_id']} | Strategy: {worst_bet['strategy']}"
            )
            if worst_bet["strategy"] == "80/20":
                report.append(
                    f"  Horse: {worst_bet['horse_name']} (Place: {worst_bet['actual_place']})"
                )
            else:
                winner = worst_bet.get("winning_horse", "None")
                report.append(f"  Winning Horse: {winner}")
            report.append(
                f"  Loss: £{worst_bet['net_profit']:.2f} | ROI: {worst_bet['roi']:.1f}%"
            )

        return "\n".join(report)


async def main():
    """Main backtest function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Monte Carlo Strategy Backtest"
    )
    parser.add_argument(
        "--bankroll",
        type=float,
        default=1000.0,
        help="Starting bankroll (default: £1000)",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads",
        help="Path to race data",
    )

    args = parser.parse_args()

    print("🏇 ENHANCED MONTE CARLO STRATEGY BACKTEST")
    print("=" * 80)
    print(f"Starting Bankroll: £{args.bankroll:.2f}")
    print(f"Data Source: {args.data_path}")
    print("")

    try:
        # Initialize components
        parser = RaceResultsParser(args.data_path)
        backtester = StrategyBacktester(bankroll=args.bankroll)

        # Load data
        print("📊 Loading race results data...")
        if not parser.load_data():
            print("❌ Failed to load race data")
            return

        # Get all available races
        race_ids = parser.get_all_races()
        print(f"✅ Found {len(race_ids)} races to analyze")
        print("")

        # Process each race
        processed_count = 0
        for race_id in race_ids:
            race_result = parser.get_race_results(race_id)
            if race_result:
                backtester.process_race(race_result)
                processed_count += 1

        print(f"✅ Processed {processed_count} races")
        print("")

        # Calculate final statistics
        backtester.calculate_final_stats()

        # Generate and display report
        report = backtester.generate_report()
        print(report)

        # Save detailed results
        results_file = f"backtest_results_{date.today()}.json"
        with open(results_file, "w") as f:
            # Convert Decimal to float for JSON serialization
            serializable_results = {}
            for strategy, data in backtester.results.items():
                serializable_results[strategy] = {}
                for key, value in data.items():
                    if isinstance(value, Decimal):
                        serializable_results[strategy][key] = float(value)
                    else:
                        serializable_results[strategy][key] = value

            json.dump(serializable_results, f, indent=2, default=str)

        print(f"\n💾 Detailed results saved to {results_file}")

    except Exception as e:
        logger.error(f"Backtest failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
