"""
BETDAQ Paper Trading and Live Betting Demo
Demonstrates the complete betting system functionality
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from betdaq_betting_coordinator import BettingCoordinator, TradingMode
from betdaq_client import BetdaqClient, BetdaqConfig, BetOrder, BettingSide, MarketInfo
from betdaq_live_betting import RiskLimits
from betdaq_paper_trading import PaperTradingConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BettingSystemDemo:
    """Demo class for BETDAQ betting system"""

    def __init__(self):
        self.coordinator = None
        self.demo_markets = []
        self.demo_predictions = []

    async def setup_demo_environment(self):
        """Setup demo environment with mock data"""

        logger.info("🚀 Setting up BETDAQ Betting System Demo")

        # Initialize BETDAQ client in demo mode
        config = BetdaqConfig(
            username="demo_user",
            password="demo_pass",
            paper_trading=True,
            enabled=True,
            max_stake_per_bet=25.0,
            max_daily_loss=200.0,
        )

        client = BetdaqClient(config)

        # Initialize coordinator in paper trading mode
        paper_config = PaperTradingConfig(
            starting_balance=1000.0,
            realistic_matching=True,
            save_to_database=True,
            database_path="demo_paper_trading.db",
        )

        self.coordinator = BettingCoordinator(
            betdaq_client=client,
            trading_mode=TradingMode.PAPER,
            paper_config=paper_config,
        )

        # Create demo markets
        self.demo_markets = [
            MarketInfo(
                market_id=100001,
                market_name="2:30 Newmarket - Win",
                start_time=datetime.now() + timedelta(minutes=30),
                status="active",
                runners=[
                    {"selection_id": 1001, "horse_name": "Thunder Strike", "odds": 3.5},
                    {"selection_id": 1002, "horse_name": "Lightning Bolt", "odds": 4.2},
                    {"selection_id": 1003, "horse_name": "Storm Chaser", "odds": 6.0},
                    {"selection_id": 1004, "horse_name": "Wind Runner", "odds": 8.5},
                ],
            ),
            MarketInfo(
                market_id=100002,
                market_name="3:15 Ascot - Win",
                start_time=datetime.now() + timedelta(minutes=75),
                status="active",
                runners=[
                    {"selection_id": 2001, "horse_name": "Golden Arrow", "odds": 2.8},
                    {"selection_id": 2002, "horse_name": "Silver Bullet", "odds": 5.5},
                    {"selection_id": 2003, "horse_name": "Bronze Medal", "odds": 7.2},
                    {"selection_id": 2004, "horse_name": "Iron Will", "odds": 12.0},
                ],
            ),
        ]

        # Create demo AI predictions
        self.demo_predictions = [
            {
                "horse_name": "Thunder Strike",
                "selection_id": 1001,
                "market_id": 100001,
                "confidence": 0.85,
                "predicted_odds": 2.8,
                "current_odds": 3.5,
                "model_features": {
                    "form_score": 0.92,
                    "jockey_rating": 0.88,
                    "track_suitability": 0.84,
                },
            },
            {
                "horse_name": "Lightning Bolt",
                "selection_id": 1002,
                "market_id": 100001,
                "confidence": 0.72,
                "predicted_odds": 3.8,
                "current_odds": 4.2,
                "model_features": {
                    "form_score": 0.78,
                    "jockey_rating": 0.85,
                    "track_suitability": 0.76,
                },
            },
            {
                "horse_name": "Golden Arrow",
                "selection_id": 2001,
                "market_id": 100002,
                "confidence": 0.91,
                "predicted_odds": 2.2,
                "current_odds": 2.8,
                "model_features": {
                    "form_score": 0.95,
                    "jockey_rating": 0.92,
                    "track_suitability": 0.89,
                },
            },
        ]

        logger.info("✅ Demo environment setup complete")

    async def demonstrate_paper_trading(self):
        """Demonstrate paper trading functionality"""

        logger.info("\n📊 === PAPER TRADING DEMONSTRATION ===")

        # Process AI predictions and place paper bets
        placed_bets = []

        for prediction in self.demo_predictions:
            market_info = next(
                (
                    m
                    for m in self.demo_markets
                    if m.market_id == prediction["market_id"]
                ),
                None,
            )

            if market_info:
                logger.info(f"🔍 Processing prediction for {prediction['horse_name']}")
                logger.info(f"   Confidence: {prediction['confidence']:.1%}")
                logger.info(f"   Predicted odds: {prediction['predicted_odds']:.2f}")
                logger.info(f"   Current odds: {prediction['current_odds']:.2f}")

                # Calculate value
                value = (
                    (1 / prediction["predicted_odds"]) * prediction["current_odds"] - 1
                ) / (prediction["current_odds"] - 1)
                logger.info(f"   Betting value: {value:.1%}")

                if value > 0.05:  # 5% minimum edge
                    bet = await self.coordinator.process_ai_prediction(
                        prediction, market_info
                    )
                    if bet:
                        placed_bets.append((bet, prediction["market_id"]))
                        logger.info(
                            f"✅ Paper bet placed: £{bet.stake:.2f} on {bet.horse_name}"
                        )
                    else:
                        logger.info("❌ Bet rejected by system")
                else:
                    logger.info("🚫 Insufficient value - bet skipped")

        # Show account status
        summary = self.coordinator.get_performance_summary()
        paper_summary = summary.get("paper_trading", {})
        account = paper_summary.get("account", {})

        logger.info(f"\n💰 Paper Trading Account Status:")
        logger.info(f"   Balance: £{account.get('balance', 0):.2f}")
        logger.info(f"   Total staked: £{account.get('total_staked', 0):.2f}")
        logger.info(f"   Bets placed: {account.get('bets_placed', 0)}")

        # Simulate race results
        logger.info(f"\n🏁 Simulating race results...")

        for bet, market_id in placed_bets:
            # Simulate race result (sometimes winner, sometimes not)
            import random

            winning_selection = (
                bet.selection_id
                if random.random() > 0.4
                else random.choice([1001, 1002, 1003, 1004, 2001, 2002, 2003, 2004])
            )

            logger.info(f"   Race {market_id}: Winner selection {winning_selection}")
            await self.coordinator.simulate_race_result(market_id, winning_selection)

        # Final account status
        final_summary = self.coordinator.get_performance_summary()
        final_paper = final_summary.get("paper_trading", {})
        final_account = final_paper.get("account", {})

        logger.info(f"\n📈 Final Paper Trading Results:")
        logger.info(f"   Final balance: £{final_account.get('balance', 0):.2f}")
        logger.info(f"   Total P&L: £{final_account.get('daily_pnl', 0):.2f}")
        logger.info(f"   Win rate: {final_account.get('win_rate', 0):.1f}%")
        logger.info(f"   ROI: {final_account.get('roi', 0):.1f}%")

        return final_account.get("roi", 0) > 5.0  # Return True if profitable

    async def demonstrate_mode_switching(self):
        """Demonstrate switching between trading modes"""

        logger.info("\n🔄 === MODE SWITCHING DEMONSTRATION ===")

        # Current mode
        current_summary = self.coordinator.get_performance_summary()
        logger.info(f"Current mode: {current_summary['trading_mode']}")

        # Switch to disabled mode
        logger.info("Switching to DISABLED mode...")
        success = await self.coordinator.switch_mode(TradingMode.DISABLED)
        logger.info(f"Switch successful: {success}")

        # Try to place bet in disabled mode (should fail)
        test_prediction = self.demo_predictions[0]
        test_market = self.demo_markets[0]

        bet = await self.coordinator.process_ai_prediction(test_prediction, test_market)
        logger.info(
            f"Bet in disabled mode: {'Rejected as expected' if not bet else 'ERROR: Should have been rejected'}"
        )

        # Switch back to paper trading
        logger.info("Switching back to PAPER trading mode...")
        success = await self.coordinator.switch_mode(TradingMode.PAPER)
        logger.info(f"Switch successful: {success}")

        # Show mode switch history
        final_summary = self.coordinator.get_performance_summary()
        switches = final_summary.get("mode_switch_history", [])
        logger.info(f"Mode switches performed: {len(switches)}")

    async def demonstrate_live_betting_setup(self):
        """Demonstrate live betting configuration (without real money)"""

        logger.info("\n💸 === LIVE BETTING CONFIGURATION DEMO ===")
        logger.info("⚠️  NOTE: This is demo mode - no real money involved")

        # Setup conservative risk limits for live trading
        risk_limits = RiskLimits(
            max_stake_per_bet=5.0,  # Very conservative
            max_total_exposure=25.0,  # Low exposure
            max_daily_loss=15.0,  # Strict loss limit
            max_orders_per_race=1,  # One bet per race
            min_odds=1.5,
            max_odds=10.0,
            stop_loss_percentage=5.0,  # Very tight stop loss
            max_bet_frequency=5,  # Max 5 bets per hour
        )

        logger.info("Risk limits configured:")
        logger.info(f"   Max stake per bet: £{risk_limits.max_stake_per_bet}")
        logger.info(f"   Max total exposure: £{risk_limits.max_total_exposure}")
        logger.info(f"   Max daily loss: £{risk_limits.max_daily_loss}")
        logger.info(f"   Stop loss threshold: {risk_limits.stop_loss_percentage}%")

        # In a real system, this would switch to live mode
        # For demo, we'll just show the configuration
        logger.info("\n🔒 Live betting mode configuration complete")
        logger.info("⚠️  To enable live betting:")
        logger.info("   1. Set BETDAQ_ENABLED=true")
        logger.info("   2. Configure BETDAQ_USERNAME and BETDAQ_PASSWORD")
        logger.info("   3. Set BETDAQ_PAPER_TRADING=false")
        logger.info("   4. Start with very small stakes")
        logger.info("   5. Monitor performance closely")

    async def demonstrate_performance_monitoring(self):
        """Demonstrate performance monitoring and reporting"""

        logger.info("\n📊 === PERFORMANCE MONITORING DEMO ===")

        # Get comprehensive performance summary
        summary = self.coordinator.get_performance_summary()

        logger.info("Session Summary:")
        logger.info(
            f"   Session duration: {(datetime.now() - datetime.fromisoformat(summary['session_start'])).total_seconds():.0f} seconds"
        )
        logger.info(f"   Total bets placed: {summary['total_bets_placed']}")
        logger.info(f"   Mode switches: {summary['mode_switches']}")

        if "paper_trading" in summary:
            paper_data = summary["paper_trading"]
            account = paper_data.get("account", {})

            logger.info("\nPaper Trading Performance:")
            logger.info(f"   Win rate: {account.get('win_rate', 0):.1f}%")
            logger.info(f"   ROI: {account.get('roi', 0):.1f}%")
            logger.info(
                f"   Profit factor: {account.get('total_won', 0) / max(account.get('total_lost', 1), 1):.2f}"
            )

            # Export session data
            export_filename = (
                f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            await self.coordinator.export_session_data(export_filename)
            logger.info(f"Session data exported to: {export_filename}")

    async def run_complete_demo(self):
        """Run the complete betting system demonstration"""

        logger.info("🎯 Starting BETDAQ Betting System Complete Demo")
        logger.info("=" * 60)

        try:
            # Setup
            await self.setup_demo_environment()

            # Demonstrate paper trading
            profitable = await self.demonstrate_paper_trading()

            # Demonstrate mode switching
            await self.demonstrate_mode_switching()

            # Demonstrate live betting setup
            await self.demonstrate_live_betting_setup()

            # Demonstrate monitoring
            await self.demonstrate_performance_monitoring()

            # Final summary
            logger.info("\n🎉 === DEMO COMPLETE ===")
            logger.info("Key Features Demonstrated:")
            logger.info("✅ Paper trading with realistic simulation")
            logger.info("✅ AI prediction processing and value betting")
            logger.info("✅ Risk management and position sizing")
            logger.info("✅ Mode switching capabilities")
            logger.info("✅ Performance monitoring and export")
            logger.info("✅ Live betting configuration (demo mode)")

            if profitable:
                logger.info(
                    "🚀 Paper trading was profitable - ready for live deployment!"
                )
            else:
                logger.info("⚠️  Paper trading results mixed - needs more optimization")

            logger.info("\nNext Steps:")
            logger.info("1. Review paper trading results")
            logger.info("2. Optimize AI model parameters")
            logger.info("3. Configure BETDAQ credentials for live trading")
            logger.info("4. Start with minimal stakes")
            logger.info("5. Monitor performance closely")

        except Exception as e:
            logger.error(f"Demo error: {e}")
            raise


async def main():
    """Run the betting system demo"""

    demo = BettingSystemDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    print("🎯 BETDAQ Paper Trading & Live Betting Demo")
    print("=" * 50)
    print("This demo showcases the complete betting system functionality:")
    print("• Paper trading simulation")
    print("• AI prediction processing")
    print("• Risk management")
    print("• Mode switching")
    print("• Performance monitoring")
    print("• Live betting configuration")
    print("=" * 50)

    asyncio.run(main())
