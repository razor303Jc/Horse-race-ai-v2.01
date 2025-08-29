#!/usr/bin/env python3
"""
Live Strategy Execution System
==============================

Complete live execution system that integrates all components:
- Live race data feeds
- Strategy opportunity detection
- Automated bet placement
- Risk management
- Performance monitoring
- Alert notifications

This is the main production system that coordinates all betting activities.

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import asyncio
import json
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all required components
from src.horse_racing_ai.data_feeds.live_race_data_api import (
    LiveRaceDataAPI,
    RaceDataIntegrator,
)
from src.horse_racing_ai.betting.betting_exchange_api import BettingExchangeIntegrator
from src.horse_racing_ai.monitoring.live_strategy_monitor import LiveStrategyMonitor
from src.horse_racing_ai.alerts.alert_system import AlertManager
from src.horse_racing_ai.betting.eighty_twenty_strategy import EightyTwentyStrategy
from src.horse_racing_ai.betting.reduced_stake_dutching import ReducedStakeDutching

logger = logging.getLogger(__name__)


@dataclass
class LiveExecutionConfig:
    """Configuration for live execution system"""

    execution_mode: str = "simulation"  # "simulation", "live"
    monitoring_interval: int = 30  # seconds
    opportunity_scan_interval: int = 60  # seconds
    max_concurrent_positions: int = 5
    max_daily_stake: float = 200.0
    max_single_stake: float = 50.0
    min_confidence_threshold: float = 0.65
    enable_80_20_strategy: bool = True
    enable_dutching_strategy: bool = True
    auto_place_bets: bool = False
    require_manual_approval: bool = True
    alert_on_opportunities: bool = True
    alert_on_performance: bool = True


@dataclass
class LiveOpportunity:
    """Live betting opportunity"""

    opportunity_id: str
    race_id: str
    market_id: str
    strategy_type: str
    selections: List[Dict[str, Any]]
    total_stake: float
    expected_roi: float
    confidence_score: float
    risk_assessment: str
    created_at: datetime
    status: str = (
        "detected"  # "detected", "approved", "rejected", "placed", "cancelled"
    )
    approval_deadline: Optional[datetime] = None


class LiveStrategyExecutor:
    """Main live strategy execution system"""

    def __init__(self, config_path: str = "config/live_execution_config.json"):
        self.config = self._load_config(config_path)

        # Initialize all components
        self._init_components()

        # Execution state
        self.active = False
        self.current_opportunities = {}
        self.active_positions = {}
        self.daily_stats = {
            "total_stake": 0.0,
            "opportunities_found": 0,
            "bets_placed": 0,
            "positions_active": 0,
        }

        # Threading
        self.execution_thread = None
        self.monitoring_thread = None

        logger.info("Live Strategy Executor initialized")

    def _load_config(self, config_path: str) -> LiveExecutionConfig:
        """Load execution configuration"""
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
                return LiveExecutionConfig(**config_data)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return LiveExecutionConfig()

    def _init_components(self):
        """Initialize all system components"""
        try:
            # Race data integration
            self.race_api = LiveRaceDataAPI()
            self.race_integrator = RaceDataIntegrator(self.race_api)

            # Betting exchange integration
            self.betting_integrator = BettingExchangeIntegrator()

            # Strategy systems
            self.eighty_twenty = EightyTwentyStrategy()
            self.dutching = ReducedStakeDutching()

            # Monitoring and alerts
            self.monitor = LiveStrategyMonitor()
            self.alert_manager = AlertManager()

            logger.info("All system components initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise

    def start_execution(self):
        """Start live strategy execution"""
        if self.active:
            logger.warning("Execution already active")
            return

        self.active = True

        # Start data feeds
        self.race_integrator.start_monitoring()

        # Start monitoring
        self.monitor.start_monitoring()

        # Start execution thread
        self.execution_thread = threading.Thread(target=self._execution_loop)
        self.execution_thread.daemon = True
        self.execution_thread.start()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        logger.info("🚀 Live strategy execution started")

        # Send system alert
        self.alert_manager.send_system_alert(
            system_name="Live Strategy Executor",
            status="STARTED",
            message="Live strategy execution system is now active",
            execution_mode=self.config.execution_mode,
            monitoring_interval=self.config.monitoring_interval,
        )

    def stop_execution(self):
        """Stop live strategy execution"""
        if not self.active:
            logger.warning("Execution not active")
            return

        self.active = False

        # Stop data feeds
        self.race_integrator.stop_monitoring()

        # Stop monitoring
        self.monitor.stop_monitoring()

        # Wait for threads
        if self.execution_thread:
            self.execution_thread.join(timeout=10)

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)

        logger.info("🛑 Live strategy execution stopped")

        # Send system alert
        self.alert_manager.send_system_alert(
            system_name="Live Strategy Executor",
            status="STOPPED",
            message="Live strategy execution system has been stopped",
            final_stats=self.daily_stats,
        )

    def _execution_loop(self):
        """Main execution loop"""
        logger.info("Starting execution loop")

        while self.active:
            try:
                # Scan for opportunities
                self._scan_for_opportunities()

                # Process pending opportunities
                self._process_opportunities()

                # Update positions
                self._update_positions()

                # Check risk limits
                self._check_risk_limits()

                # Sleep until next scan
                time.sleep(self.config.opportunity_scan_interval)

            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                time.sleep(60)  # Wait 1 minute on error

    def _monitoring_loop(self):
        """Monitoring and performance tracking loop"""
        logger.info("Starting monitoring loop")

        while self.active:
            try:
                # Update performance metrics
                self._update_performance_metrics()

                # Check for performance alerts
                self._check_performance_alerts()

                # Clean up old opportunities
                self._cleanup_old_opportunities()

                # Sleep until next monitoring cycle
                time.sleep(self.config.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait 30 seconds on error

    def _scan_for_opportunities(self):
        """Scan for betting opportunities"""
        try:
            # Get upcoming races (next 2 hours)
            upcoming_races = self.race_integrator.api.get_upcoming_races(hours_ahead=2)

            for race in upcoming_races:
                # Skip if race too soon (less than 10 minutes)
                if race.race_time - datetime.now() < timedelta(minutes=10):
                    continue

                # Skip if already processed
                if race.race_id in self.current_opportunities:
                    continue

                # Analyze race for opportunities
                self._analyze_race_for_opportunities(race)

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")

    def _analyze_race_for_opportunities(self, race):
        """Analyze a race for betting opportunities"""
        try:
            # Get live odds
            market_data = self.race_integrator.api.get_live_odds(race.race_id)
            if not market_data:
                return

            opportunities = []

            # Check 80/20 strategy
            if self.config.enable_80_20_strategy:
                eighty_twenty_opp = self._check_80_20_opportunity(race, market_data)
                if eighty_twenty_opp:
                    opportunities.append(eighty_twenty_opp)

            # Check dutching strategy
            if self.config.enable_dutching_strategy:
                dutching_opp = self._check_dutching_opportunity(race, market_data)
                if dutching_opp:
                    opportunities.append(dutching_opp)

            # Process found opportunities
            for opportunity in opportunities:
                self._handle_new_opportunity(opportunity)

        except Exception as e:
            logger.error(f"Error analyzing race {race.race_id}: {e}")

    def _check_80_20_opportunity(self, race, market_data) -> Optional[LiveOpportunity]:
        """Check for 80/20 strategy opportunity"""
        try:
            # Prepare race data for strategy
            race_data = {
                "race_id": race.race_id,
                "runners": race.runners,
                "market_data": market_data,
                "going": race.going,
                "distance": race.distance,
                "field_size": race.field_size,
            }

            # Get 80/20 analysis
            analysis = self.eighty_twenty.analyze_race(race_data)

            if (
                analysis.get("has_opportunity", False)
                and analysis.get("confidence", 0)
                >= self.config.min_confidence_threshold
            ):

                selection = analysis.get("selection", {})
                stake = min(
                    analysis.get("recommended_stake", 15.0),
                    self.config.max_single_stake,
                )

                opportunity = LiveOpportunity(
                    opportunity_id=f"80_20_{race.race_id}_{int(time.time())}",
                    race_id=race.race_id,
                    market_id=market_data.market_id,
                    strategy_type="80/20",
                    selections=[
                        {
                            "runner_id": selection.get("runner_id"),
                            "horse_name": selection.get("horse_name"),
                            "odds": selection.get("odds"),
                            "stake": stake,
                        }
                    ],
                    total_stake=stake,
                    expected_roi=analysis.get("expected_roi", 0),
                    confidence_score=analysis.get("confidence", 0),
                    risk_assessment=self._assess_risk(analysis),
                    created_at=datetime.now(),
                    approval_deadline=race.race_time - timedelta(minutes=5),
                )

                return opportunity

        except Exception as e:
            logger.error(f"Error checking 80/20 opportunity: {e}")

        return None

    def _check_dutching_opportunity(
        self, race, market_data
    ) -> Optional[LiveOpportunity]:
        """Check for dutching strategy opportunity"""
        try:
            # Prepare race data for strategy
            race_data = {
                "race_id": race.race_id,
                "runners": race.runners,
                "market_data": market_data,
                "going": race.going,
                "distance": race.distance,
                "field_size": race.field_size,
            }

            # Get dutching analysis
            analysis = self.dutching.analyze_race(race_data)

            if (
                analysis.get("has_opportunity", False)
                and analysis.get("confidence", 0)
                >= self.config.min_confidence_threshold
            ):

                selections = analysis.get("selections", [])
                total_stake = min(
                    sum(s.get("stake", 0) for s in selections),
                    self.config.max_single_stake,
                )

                # Adjust stakes proportionally if needed
                if sum(s.get("stake", 0) for s in selections) > total_stake:
                    scale_factor = total_stake / sum(
                        s.get("stake", 0) for s in selections
                    )
                    for selection in selections:
                        selection["stake"] *= scale_factor

                opportunity = LiveOpportunity(
                    opportunity_id=f"dutching_{race.race_id}_{int(time.time())}",
                    race_id=race.race_id,
                    market_id=market_data.market_id,
                    strategy_type="dutching",
                    selections=selections,
                    total_stake=total_stake,
                    expected_roi=analysis.get("expected_roi", 0),
                    confidence_score=analysis.get("confidence", 0),
                    risk_assessment=self._assess_risk(analysis),
                    created_at=datetime.now(),
                    approval_deadline=race.race_time - timedelta(minutes=5),
                )

                return opportunity

        except Exception as e:
            logger.error(f"Error checking dutching opportunity: {e}")

        return None

    def _assess_risk(self, analysis: Dict[str, Any]) -> str:
        """Assess risk level for opportunity"""
        confidence = analysis.get("confidence", 0)
        expected_roi = analysis.get("expected_roi", 0)

        if confidence >= 0.8 and expected_roi >= 10:
            return "LOW"
        elif confidence >= 0.65 and expected_roi >= 5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _handle_new_opportunity(self, opportunity: LiveOpportunity):
        """Handle a newly detected opportunity"""
        try:
            # Add to current opportunities
            self.current_opportunities[opportunity.opportunity_id] = opportunity
            self.daily_stats["opportunities_found"] += 1

            logger.info(
                f"New {opportunity.strategy_type} opportunity detected: {opportunity.race_id}"
            )

            # Send alert if enabled
            if self.config.alert_on_opportunities:
                self._send_opportunity_alert(opportunity)

            # Auto-approve if configured
            if self.config.auto_place_bets and not self.config.require_manual_approval:
                self._approve_opportunity(opportunity.opportunity_id)

        except Exception as e:
            logger.error(f"Error handling new opportunity: {e}")

    def _send_opportunity_alert(self, opportunity: LiveOpportunity):
        """Send opportunity alert"""
        try:
            # Get race details
            race = self.race_integrator.get_race_for_strategy(opportunity.race_id)

            if opportunity.strategy_type == "80/20":
                selection = opportunity.selections[0]
                self.alert_manager.send_opportunity_alert(
                    strategy_type=opportunity.strategy_type,
                    horse_name=selection.get("horse_name", "Unknown"),
                    course=race.course if race else "Unknown",
                    race_time=race.race_time.strftime("%H:%M") if race else "Unknown",
                    expected_roi=opportunity.expected_roi,
                    confidence=opportunity.confidence_score * 100,
                    stake=opportunity.total_stake,
                    odds=selection.get("odds", 0),
                    field_size=race.field_size if race else 0,
                    going=race.going if race else "Unknown",
                    race_class=race.race_class if race else "Unknown",
                )
            else:  # dutching
                horse_names = [
                    s.get("horse_name", "Unknown") for s in opportunity.selections
                ]
                self.alert_manager.send_opportunity_alert(
                    strategy_type=opportunity.strategy_type,
                    horse_name=", ".join(horse_names),
                    course=race.course if race else "Unknown",
                    race_time=race.race_time.strftime("%H:%M") if race else "Unknown",
                    expected_roi=opportunity.expected_roi,
                    confidence=opportunity.confidence_score * 100,
                    stake=opportunity.total_stake,
                    odds="Multiple",
                    field_size=race.field_size if race else 0,
                    going=race.going if race else "Unknown",
                    race_class=race.race_class if race else "Unknown",
                )

        except Exception as e:
            logger.error(f"Error sending opportunity alert: {e}")

    def _process_opportunities(self):
        """Process pending opportunities"""
        try:
            current_time = datetime.now()

            for opp_id, opportunity in list(self.current_opportunities.items()):
                # Check if deadline passed
                if (
                    opportunity.approval_deadline
                    and current_time > opportunity.approval_deadline
                ):
                    opportunity.status = "expired"
                    logger.info(f"Opportunity {opp_id} expired")
                    continue

                # Process approved opportunities
                if opportunity.status == "approved":
                    self._execute_opportunity(opportunity)

        except Exception as e:
            logger.error(f"Error processing opportunities: {e}")

    def _execute_opportunity(self, opportunity: LiveOpportunity):
        """Execute an approved opportunity"""
        try:
            # Check daily limits
            if (
                self.daily_stats["total_stake"] + opportunity.total_stake
                > self.config.max_daily_stake
            ):
                logger.warning(
                    f"Daily stake limit would be exceeded for {opportunity.opportunity_id}"
                )
                opportunity.status = "rejected"
                return

            # Check concurrent positions
            if len(self.active_positions) >= self.config.max_concurrent_positions:
                logger.warning(
                    f"Maximum concurrent positions reached for {opportunity.opportunity_id}"
                )
                opportunity.status = "rejected"
                return

            if self.config.execution_mode == "live":
                # Place actual bets
                position = self.betting_integrator.place_strategy_bets(
                    strategy_type=opportunity.strategy_type,
                    race_id=opportunity.race_id,
                    market_id=opportunity.market_id,
                    selections=opportunity.selections,
                )

                if position:
                    self.active_positions[opportunity.market_id] = position
                    opportunity.status = "placed"
                    self.daily_stats["bets_placed"] += 1
                    self.daily_stats["total_stake"] += opportunity.total_stake
                    self.daily_stats["positions_active"] = len(self.active_positions)

                    logger.info(
                        f"Bets placed for opportunity {opportunity.opportunity_id}"
                    )
                else:
                    opportunity.status = "failed"
                    logger.error(
                        f"Failed to place bets for opportunity {opportunity.opportunity_id}"
                    )

            else:  # simulation mode
                # Simulate bet placement
                opportunity.status = "simulated"
                self.daily_stats["bets_placed"] += 1
                self.daily_stats["total_stake"] += opportunity.total_stake

                logger.info(
                    f"Simulated bet placement for opportunity {opportunity.opportunity_id}"
                )

        except Exception as e:
            logger.error(
                f"Error executing opportunity {opportunity.opportunity_id}: {e}"
            )
            opportunity.status = "failed"

    def _update_positions(self):
        """Update active betting positions"""
        try:
            for market_id, position in list(self.active_positions.items()):
                # Update bet status
                self.betting_integrator.update_bet_status(market_id)

                # Check if race finished
                race = self.race_integrator.get_race_for_strategy(position.race_id)
                if race and race.status == "finished":
                    # Get results and settle position
                    results = self.race_integrator.api.get_race_results(
                        position.race_id
                    )
                    if results:
                        self._settle_position(position, results)
                        del self.active_positions[market_id]
                        self.daily_stats["positions_active"] = len(
                            self.active_positions
                        )

        except Exception as e:
            logger.error(f"Error updating positions: {e}")

    def _settle_position(self, position, results: Dict[str, Any]):
        """Settle a completed position"""
        try:
            # Record results in monitoring system
            winning_selections = results.get("winners", [])

            for bet in position.bets:
                result = "win" if bet.runner_id in winning_selections else "lose"
                return_amount = (
                    bet.matched_amount * bet.odds if result == "win" else 0.0
                )

                self.monitor.db.record_strategy_result(
                    race_id=position.race_id,
                    strategy_name=position.strategy_type,
                    selections=[bet.horse_name],
                    stakes=[bet.stake],
                    odds=[bet.odds],
                    result=result,
                    stake_amount=bet.stake,
                    return_amount=return_amount,
                    race_date=datetime.now().date(),
                    course="Unknown",  # Could be enhanced
                    confidence_score=0.7,  # Could be stored with position
                    risk_level="medium",
                )

            logger.info(f"Position settled for race {position.race_id}")

        except Exception as e:
            logger.error(f"Error settling position: {e}")

    def _check_risk_limits(self):
        """Check risk management limits"""
        try:
            # Check daily stake limit
            if self.daily_stats["total_stake"] >= self.config.max_daily_stake * 0.9:
                self.alert_manager.send_risk_alert(
                    alert_title="Daily Stake Limit Warning",
                    alert_message=f"Daily stake usage at {self.daily_stats['total_stake']:.2f} of {self.config.max_daily_stake:.2f} limit",
                    daily_stake_used=self.daily_stats["total_stake"],
                    daily_limit=self.config.max_daily_stake,
                    drawdown=0.0,  # Would calculate actual drawdown
                    risk_level="MEDIUM",
                    recommended_action="Monitor remaining stake allocation carefully",
                )

            # Additional risk checks could be added here

        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")

    def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get performance for both strategies
            eighty_twenty_perf = self.monitor.db.get_strategy_performance(
                "80/20", days=1
            )
            dutching_perf = self.monitor.db.get_strategy_performance("dutching", days=1)

            # Update daily stats
            self.daily_stats.update(
                {
                    "80_20_roi": eighty_twenty_perf.roi_percentage,
                    "dutching_roi": dutching_perf.roi_percentage,
                    "total_profit": eighty_twenty_perf.net_profit
                    + dutching_perf.net_profit,
                }
            )

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    def _check_performance_alerts(self):
        """Check for performance-based alerts"""
        try:
            # Only send alerts every hour
            if datetime.now().minute != 0:
                return

            # Get hourly performance
            eighty_twenty_perf = self.monitor.db.get_strategy_performance(
                "80/20", days=1
            )

            if eighty_twenty_perf.total_bets > 0:
                self.alert_manager.send_performance_alert(
                    strategy_type="80/20",
                    roi=eighty_twenty_perf.roi_percentage,
                    strike_rate=eighty_twenty_perf.strike_rate,
                    total_bets=eighty_twenty_perf.total_bets,
                    net_profit=eighty_twenty_perf.net_profit,
                    period="Today",
                )

        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")

    def _cleanup_old_opportunities(self):
        """Clean up old opportunities"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)

            for opp_id, opportunity in list(self.current_opportunities.items()):
                if opportunity.created_at < cutoff_time:
                    del self.current_opportunities[opp_id]

        except Exception as e:
            logger.error(f"Error cleaning up opportunities: {e}")

    def approve_opportunity(self, opportunity_id: str) -> bool:
        """Manually approve an opportunity"""
        if opportunity_id in self.current_opportunities:
            opportunity = self.current_opportunities[opportunity_id]
            if opportunity.status == "detected":
                opportunity.status = "approved"
                logger.info(f"Opportunity {opportunity_id} approved manually")
                return True

        return False

    def reject_opportunity(self, opportunity_id: str) -> bool:
        """Manually reject an opportunity"""
        if opportunity_id in self.current_opportunities:
            opportunity = self.current_opportunities[opportunity_id]
            if opportunity.status == "detected":
                opportunity.status = "rejected"
                logger.info(f"Opportunity {opportunity_id} rejected manually")
                return True

        return False

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "active": self.active,
            "execution_mode": self.config.execution_mode,
            "daily_stats": self.daily_stats,
            "current_opportunities": len(self.current_opportunities),
            "active_positions": len(self.active_positions),
            "config": asdict(self.config),
        }


# Configuration file creation
def create_live_execution_config():
    """Create live execution configuration"""
    config = {
        "execution_mode": "simulation",
        "monitoring_interval": 30,
        "opportunity_scan_interval": 60,
        "max_concurrent_positions": 5,
        "max_daily_stake": 200.0,
        "max_single_stake": 50.0,
        "min_confidence_threshold": 0.65,
        "enable_80_20_strategy": True,
        "enable_dutching_strategy": True,
        "auto_place_bets": False,
        "require_manual_approval": True,
        "alert_on_opportunities": True,
        "alert_on_performance": True,
    }

    config_path = "config/live_execution_config.json"
    os.makedirs("config", exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"Created live execution config: {config_path}")
    return config_path


async def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)

    # Create config if not exists
    create_live_execution_config()

    # Initialize executor
    executor = LiveStrategyExecutor()

    try:
        print("🚀 Starting Live Strategy Execution System")
        print("=" * 50)
        print(f"Execution Mode: {executor.config.execution_mode}")
        print(f"Max Daily Stake: £{executor.config.max_daily_stake}")
        print(f"Monitoring Interval: {executor.config.monitoring_interval}s")
        print(
            f"80/20 Strategy: {'ENABLED' if executor.config.enable_80_20_strategy else 'DISABLED'}"
        )
        print(
            f"Dutching Strategy: {'ENABLED' if executor.config.enable_dutching_strategy else 'DISABLED'}"
        )
        print("=" * 50)

        # Start execution
        executor.start_execution()

        print("✅ Live execution started successfully")
        print("📊 Monitor dashboard at: http://localhost:5000")
        print("⚠️ Press Ctrl+C to stop execution")

        # Keep running
        while True:
            await asyncio.sleep(10)

            # Print status every minute
            if datetime.now().second == 0:
                status = executor.get_status()
                print(
                    f"Status: {status['current_opportunities']} opportunities, "
                    f"{status['active_positions']} positions, "
                    f"£{status['daily_stats']['total_stake']:.2f} staked today"
                )

    except KeyboardInterrupt:
        print("\n🛑 Stopping live execution...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        executor.stop_execution()
        print("✅ Live execution stopped")


if __name__ == "__main__":
    asyncio.run(main())
