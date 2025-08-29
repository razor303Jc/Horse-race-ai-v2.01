"""
BETDAQ Integration with Horse Racing AI System
Complete integration bridge for AI predictions and betting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .betdaq_betting_coordinator import BettingCoordinator, TradingMode

# Import BETDAQ components
from .betdaq_client import BetdaqClient, BetdaqConfig
from .betdaq_live_betting import RiskLimits
from .betdaq_paper_trading import PaperTradingConfig

# Import existing AI components (these would be your existing modules)
# from ai_trainer import HorseRacingAI
# from data_processor import RaceDataProcessor
# from form_analyzer import FormAnalyzer


class BetdaqAIIntegration:
    """Integration bridge between Horse Racing AI and BETDAQ betting"""

    def __init__(self, config_file: str = "betdaq_config.json"):
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.coordinator = None
        self.ai_model = None
        self.betting_enabled = False

        # Performance tracking
        self.session_stats = {
            "predictions_processed": 0,
            "bets_placed": 0,
            "successful_predictions": 0,
            "total_profit": 0.0,
        }

    async def initialize(self):
        """Initialize the complete AI + BETDAQ system"""

        self.logger.info("🚀 Initializing BETDAQ AI Integration")

        # Load configuration
        config = await self._load_configuration()

        # Initialize BETDAQ client
        betdaq_config = BetdaqConfig(
            username=config.get("betdaq_username", ""),
            password=config.get("betdaq_password", ""),
            paper_trading=config.get("paper_trading", True),
            enabled=config.get("betting_enabled", False),
            max_stake_per_bet=config.get("max_stake_per_bet", 10.0),
            max_daily_loss=config.get("max_daily_loss", 100.0),
        )

        client = BetdaqClient(betdaq_config)

        # Initialize betting coordinator
        if config.get("paper_trading", True):
            paper_config = PaperTradingConfig(
                starting_balance=config.get("starting_balance", 1000.0),
                realistic_matching=True,
                save_to_database=True,
            )

            self.coordinator = BettingCoordinator(
                betdaq_client=client,
                trading_mode=TradingMode.PAPER,
                paper_config=paper_config,
            )
        else:
            risk_limits = RiskLimits(
                max_stake_per_bet=config.get("max_stake_per_bet", 10.0),
                max_total_exposure=config.get("max_total_exposure", 100.0),
                max_daily_loss=config.get("max_daily_loss", 100.0),
                max_orders_per_race=config.get("max_orders_per_race", 2),
                min_odds=config.get("min_odds", 1.5),
                max_odds=config.get("max_odds", 20.0),
            )

            self.coordinator = BettingCoordinator(
                betdaq_client=client,
                trading_mode=TradingMode.LIVE,
                risk_limits=risk_limits,
            )

        self.betting_enabled = config.get("betting_enabled", False)

        # Initialize AI model (placeholder - use your existing AI system)
        # self.ai_model = HorseRacingAI()
        # await self.ai_model.load_model("latest_model.pkl")

        self.logger.info(
            f"✅ Integration initialized - Mode: {self.coordinator.trading_mode.value}"
        )

    async def _load_configuration(self) -> Dict:
        """Load configuration from file or environment"""

        default_config = {
            "betdaq_username": "",
            "betdaq_password": "",
            "paper_trading": True,
            "betting_enabled": False,
            "starting_balance": 1000.0,
            "max_stake_per_bet": 10.0,
            "max_daily_loss": 100.0,
            "max_total_exposure": 200.0,
            "max_orders_per_race": 2,
            "min_odds": 1.5,
            "max_odds": 20.0,
            "min_confidence_threshold": 0.75,
            "min_value_threshold": 0.10,
            "kelly_multiplier": 0.25,
        }

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
        except FileNotFoundError:
            self.logger.info(
                f"Config file not found, creating default: {self.config_file}"
            )
            await self._save_configuration(default_config)
            return default_config

    async def _save_configuration(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    async def process_race_data(self, race_data: Dict) -> Optional[Dict]:
        """Process race data and generate AI predictions"""

        # This would integrate with your existing AI system
        # For demo purposes, we'll simulate AI predictions

        # Example integration:
        # predictions = await self.ai_model.predict_race(race_data)

        # Simulated AI prediction
        mock_prediction = {
            "race_id": race_data.get("race_id"),
            "market_id": race_data.get("market_id"),
            "predictions": [
                {
                    "horse_name": "Thunder Strike",
                    "selection_id": race_data.get("runners", [{}])[0].get(
                        "selection_id", 1001
                    ),
                    "confidence": 0.82,
                    "predicted_odds": 2.8,
                    "current_odds": 3.5,
                    "model_features": {
                        "form_score": 0.91,
                        "jockey_rating": 0.88,
                        "track_suitability": 0.85,
                        "pace_rating": 0.79,
                    },
                }
            ],
        }

        self.session_stats["predictions_processed"] += 1
        return mock_prediction

    async def evaluate_betting_opportunity(
        self, prediction: Dict, market_info: Dict
    ) -> bool:
        """Evaluate if a prediction meets betting criteria"""

        confidence = prediction.get("confidence", 0.0)
        predicted_odds = prediction.get("predicted_odds", 0.0)
        current_odds = prediction.get("current_odds", 0.0)

        # Load thresholds from config
        config = await self._load_configuration()
        min_confidence = config.get("min_confidence_threshold", 0.75)
        min_value = config.get("min_value_threshold", 0.10)

        # Check confidence threshold
        if confidence < min_confidence:
            self.logger.debug(
                f"Confidence {confidence:.2%} below threshold {min_confidence:.2%}"
            )
            return False

        # Calculate value
        if predicted_odds <= 1.0 or current_odds <= 1.0:
            return False

        implied_prob = 1.0 / predicted_odds
        market_prob = 1.0 / current_odds
        value = (implied_prob * current_odds - 1) / (current_odds - 1)

        if value < min_value:
            self.logger.debug(f"Value {value:.2%} below threshold {min_value:.2%}")
            return False

        self.logger.info(
            f"✅ Betting opportunity: {prediction['horse_name']} - "
            f"Confidence: {confidence:.2%}, Value: {value:.2%}"
        )
        return True

    async def process_betting_decision(self, race_data: Dict) -> List[Dict]:
        """Process complete betting decision pipeline"""

        if not self.betting_enabled:
            self.logger.debug("Betting disabled - skipping")
            return []

        # Generate AI predictions
        predictions = await self.process_race_data(race_data)
        if not predictions:
            return []

        betting_results = []

        # Create market info
        market_info = {
            "market_id": race_data.get("market_id"),
            "market_name": race_data.get("race_name"),
            "start_time": datetime.fromisoformat(
                race_data.get("start_time", datetime.now().isoformat())
            ),
            "status": "active",
        }

        # Process each prediction
        for prediction in predictions.get("predictions", []):

            # Evaluate betting opportunity
            should_bet = await self.evaluate_betting_opportunity(
                prediction, market_info
            )

            if should_bet:
                # Place bet through coordinator
                try:
                    bet_result = await self.coordinator.process_ai_prediction(
                        prediction, market_info
                    )

                    if bet_result:
                        self.session_stats["bets_placed"] += 1
                        betting_results.append(
                            {
                                "prediction": prediction,
                                "bet_result": bet_result,
                                "status": "placed",
                            }
                        )

                        self.logger.info(
                            f"🎯 Bet placed: {prediction['horse_name']} - "
                            f"Stake: £{bet_result.stake if hasattr(bet_result, 'stake') else 'N/A'}"
                        )
                    else:
                        betting_results.append(
                            {
                                "prediction": prediction,
                                "bet_result": None,
                                "status": "rejected",
                            }
                        )

                except Exception as e:
                    self.logger.error(f"Betting error: {e}")
                    betting_results.append(
                        {
                            "prediction": prediction,
                            "bet_result": None,
                            "status": "error",
                            "error": str(e),
                        }
                    )

        return betting_results

    async def handle_race_result(self, race_result: Dict):
        """Handle race result and settle bets"""

        market_id = race_result.get("market_id")
        winning_selection_id = race_result.get("winner_selection_id")

        if not market_id or not winning_selection_id:
            self.logger.warning("Invalid race result data")
            return

        self.logger.info(
            f"🏁 Race result: Market {market_id}, Winner: {winning_selection_id}"
        )

        # Settle race through coordinator
        await self.coordinator.settle_race(market_id, race_result)

        # Update session stats
        # This would need integration with actual bet tracking

    async def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""

        # Get coordinator performance
        coordinator_summary = self.coordinator.get_performance_summary()

        # Combine with session stats
        report = {
            "session_stats": self.session_stats,
            "betting_summary": coordinator_summary,
            "timestamp": datetime.now().isoformat(),
        }

        return report

    async def export_session_data(self, filename: str = None):
        """Export complete session data"""

        if not filename:
            filename = (
                f"ai_betting_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        report = await self.get_performance_report()

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Session data exported to: {filename}")

        except Exception as e:
            self.logger.error(f"Failed to export session data: {e}")

    async def run_automated_session(self, duration_hours: float = 1.0):
        """Run automated AI + betting session"""

        self.logger.info(f"🤖 Starting automated session for {duration_hours} hours")

        session_end = datetime.now() + timedelta(hours=duration_hours)

        # Example race data (in real system, this would come from your scraper)
        example_races = [
            {
                "race_id": "race_001",
                "market_id": 100001,
                "race_name": "2:30 Newmarket - Win",
                "start_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "runners": [
                    {"selection_id": 1001, "horse_name": "Thunder Strike", "odds": 3.5},
                    {"selection_id": 1002, "horse_name": "Lightning Bolt", "odds": 4.2},
                ],
            }
        ]

        while datetime.now() < session_end:
            try:
                for race_data in example_races:
                    # Process betting decisions
                    betting_results = await self.process_betting_decision(race_data)

                    if betting_results:
                        self.logger.info(
                            f"Processed {len(betting_results)} betting decisions"
                        )

                # Wait before next cycle
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Session error: {e}")
                await asyncio.sleep(60)

        # Export final results
        await self.export_session_data()

        final_report = await self.get_performance_report()
        self.logger.info(f"🏁 Session complete: {final_report}")


# Example configuration file creation
async def create_example_config():
    """Create an example configuration file"""

    example_config = {
        "betdaq_username": "",
        "betdaq_password": "",
        "paper_trading": True,
        "betting_enabled": False,
        "starting_balance": 1000.0,
        "max_stake_per_bet": 10.0,
        "max_daily_loss": 100.0,
        "max_total_exposure": 200.0,
        "max_orders_per_race": 2,
        "min_odds": 1.5,
        "max_odds": 20.0,
        "min_confidence_threshold": 0.75,
        "min_value_threshold": 0.10,
        "kelly_multiplier": 0.25,
        "_comments": {
            "paper_trading": "Set to false for live betting",
            "betting_enabled": "Master switch for all betting",
            "min_confidence_threshold": "Minimum AI confidence to place bet",
            "min_value_threshold": "Minimum betting edge required",
            "kelly_multiplier": "Conservative Kelly Criterion multiplier",
        },
    }

    with open("betdaq_config.json", "w") as f:
        json.dump(example_config, f, indent=2)

    print("✅ Example configuration created: betdaq_config.json")


async def main():
    """Example usage of AI integration"""

    # Create example config if it doesn't exist
    import os

    if not os.path.exists("betdaq_config.json"):
        await create_example_config()

    # Initialize integration
    integration = BetdaqAIIntegration()
    await integration.initialize()

    # Run a short demo session
    await integration.run_automated_session(duration_hours=0.1)  # 6 minutes


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("🎯 BETDAQ AI Integration System")
    print("=" * 40)
    print("This system integrates AI predictions with BETDAQ betting")
    print("Features:")
    print("• AI prediction processing")
    print("• Automated betting decisions")
    print("• Risk management")
    print("• Performance tracking")
    print("• Paper trading & live betting")
    print("=" * 40)

    asyncio.run(main())
