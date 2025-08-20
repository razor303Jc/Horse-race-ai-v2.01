#!/usr/bin/env python3
"""
Complete Live System Integration
===============================

Comprehensive integration of 80/20 and Dutching strategies with live racing
system, including performance monitoring, opportunity detection, and automated
strategy execution.

This script provides:
- Live race data integration
- Real-time strategy opportunity detection
- Performance monitoring and tracking
- Automated strategy execution (simulation)
- Web dashboard for monitoring
- Alert system for exceptional performance
- Historical performance analysis

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import asyncio
import threading
import time
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.monitoring.live_strategy_monitor import (
    LiveStrategyMonitor,
    LiveStrategyOpportunity,
    StrategyPerformanceMetrics,
)
from src.horse_racing_ai.monitoring.dashboard_app import app
from src.horse_racing_ai.integration.strategy_aware_ml_hub import (
    StrategyAwareMLIntegrationHub,
)
from src.database.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.03/logs/live_system_integration.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class LiveSystemIntegrator:
    """Complete live system integration for strategy-aware betting"""

    def __init__(self):
        self.monitor = LiveStrategyMonitor()
        self.strategy_hub = StrategyAwareMLIntegrationHub()
        self.db_manager = DatabaseManager()

        # System status
        self.system_active = False
        self.dashboard_process = None

        # Integration configuration
        self.config = {
            "monitoring_interval": 30,  # seconds
            "dashboard_port": 5000,
            "auto_execute": False,  # Set to True for live execution
            "min_confidence_threshold": 0.6,
            "max_daily_stake": 200.0,
            "risk_management": {
                "max_drawdown_stop": -20.0,  # Stop if 20% drawdown
                "consecutive_losses_stop": 5,
                "daily_loss_limit": -50.0,
            },
        }

        # Performance tracking
        self.daily_stats = {
            "opportunities_found": 0,
            "opportunities_executed": 0,
            "total_stake": 0.0,
            "total_return": 0.0,
            "net_profit": 0.0,
        }

        logger.info("Live System Integrator initialized")

    async def start_complete_system(self):
        """Start the complete live system integration"""
        logger.info("🚀 Starting Complete Live System Integration")

        try:
            # Start performance monitoring
            self.monitor.start_monitoring()
            logger.info("✅ Performance monitoring started")

            # Start web dashboard
            await self._start_dashboard()
            logger.info("✅ Web dashboard started")

            # Start main integration loop
            self.system_active = True
            integration_task = asyncio.create_task(self._integration_loop())

            # Start daily reporting
            reporting_task = asyncio.create_task(self._daily_reporting_loop())

            logger.info("🎯 Live System Integration is now active")
            logger.info(
                f"📊 Dashboard available at: http://localhost:{self.config['dashboard_port']}"
            )
            logger.info("🔄 Monitoring for strategy opportunities...")

            # Wait for tasks to complete
            await asyncio.gather(integration_task, reporting_task)

        except Exception as e:
            logger.error(f"Error starting system: {e}")
            await self.stop_complete_system()

    async def _start_dashboard(self):
        """Start the web dashboard in a separate process"""
        try:
            # Start Flask app in subprocess
            dashboard_script = (
                project_root / "src/horse_racing_ai/monitoring/dashboard_app.py"
            )

            self.dashboard_process = subprocess.Popen(
                [sys.executable, str(dashboard_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Give it time to start
            await asyncio.sleep(3)

            if self.dashboard_process.poll() is None:
                logger.info(
                    f"Dashboard started successfully on port {self.config['dashboard_port']}"
                )
            else:
                logger.error("Dashboard failed to start")

        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")

    async def _integration_loop(self):
        """Main integration loop for live system"""
        while self.system_active:
            try:
                # Scan for opportunities
                opportunities = await self._scan_for_live_opportunities()

                # Process opportunities
                for opportunity in opportunities:
                    await self._process_opportunity(opportunity)

                # Check risk management
                if await self._check_risk_limits():
                    logger.warning("⚠️ Risk limits reached, pausing system")
                    await asyncio.sleep(300)  # Pause for 5 minutes
                    continue

                # Update daily statistics
                await self._update_daily_stats()

                # Wait before next scan
                await asyncio.sleep(self.config["monitoring_interval"])

            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _scan_for_live_opportunities(self) -> List[LiveStrategyOpportunity]:
        """Scan for live strategy opportunities"""
        opportunities = []

        try:
            # Get upcoming races
            now = datetime.now()
            cutoff_time = now + timedelta(hours=2)  # Look 2 hours ahead

            query = """
            SELECT DISTINCT r.race_id, r.course, r.race_time, r.race_class,
                   r.going, r.distance_yards, COUNT(rr.horse_name) as field_size
            FROM races r
            LEFT JOIN race_results rr ON r.race_id = rr.race_id
            WHERE r.race_date = date('now')
            AND r.race_time > time('now')
            AND r.race_time < ?
            GROUP BY r.race_id
            HAVING field_size >= 6
            ORDER BY r.race_time
            LIMIT 10
            """

            races = self.db_manager.execute_query(
                query, (cutoff_time.strftime("%H:%M:%S"),)
            )

            for race in races:
                race_dict = dict(race)

                # Analyze for 80/20 opportunities
                eighty_twenty_opp = await self._analyze_eighty_twenty_opportunity(
                    race_dict
                )
                if eighty_twenty_opp:
                    opportunities.append(eighty_twenty_opp)

                # Analyze for dutching opportunities
                dutching_opp = await self._analyze_dutching_opportunity(race_dict)
                if dutching_opp:
                    opportunities.append(dutching_opp)

            if opportunities:
                logger.info(f"🎯 Found {len(opportunities)} strategy opportunities")

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")

        return opportunities

    async def _analyze_eighty_twenty_opportunity(
        self, race: Dict
    ) -> Optional[LiveStrategyOpportunity]:
        """Analyze race for 80/20 strategy opportunity"""
        try:
            race_id = race["race_id"]

            # Get runners with current odds
            runners_query = """
            SELECT horse_name, jockey_name, official_rating, starting_price_decimal,
                   jockey_claim, weight_carried
            FROM race_results 
            WHERE race_id = ?
            ORDER BY official_rating DESC
            """

            runners = self.db_manager.execute_query(runners_query, (race_id,))
            if not runners or len(runners) < 6:
                return None

            # Use strategy hub for analysis
            race_analysis = await self._get_strategy_analysis(race, list(runners))

            # Find suitable 80/20 candidates
            for horse_analysis in race_analysis.get("horse_analyses", []):
                strategy_features = horse_analysis.get("strategy_features", {})
                eighty_twenty_value = strategy_features.get(
                    "eighty_twenty_win_value", 0
                )
                confidence = horse_analysis.get("confidence_score", 0)

                if (
                    eighty_twenty_value > 0.05
                    and confidence > self.config["min_confidence_threshold"]
                ):

                    # Calculate expected ROI
                    odds = horse_analysis.get("starting_price", 5.0)
                    place_probability = confidence * 0.7
                    place_odds = odds / 3
                    expected_roi = (place_probability * place_odds - 1) * 100

                    if expected_roi > 8.0:  # Minimum 8% expected ROI
                        return LiveStrategyOpportunity(
                            race_id=race_id,
                            course=race["course"],
                            race_time=datetime.strptime(
                                f"{datetime.now().date()} {race['race_time']}",
                                "%Y-%m-%d %H:%M:%S",
                            ),
                            strategy_type="80/20",
                            horse_selections=[horse_analysis["horse_name"]],
                            recommended_stakes=[15.0],  # Standard 80/20 stake
                            expected_roi=expected_roi,
                            confidence_score=confidence,
                            risk_level="medium",
                            market_conditions={
                                "field_size": race.get("field_size", 0),
                                "race_class": race.get("race_class", ""),
                                "going": race.get("going", ""),
                                "eighty_twenty_value": eighty_twenty_value,
                            },
                            created_at=datetime.now(),
                        )

            return None

        except Exception as e:
            logger.error(
                f"Error analyzing 80/20 opportunity for race {race.get('race_id')}: {e}"
            )
            return None

    async def _analyze_dutching_opportunity(
        self, race: Dict
    ) -> Optional[LiveStrategyOpportunity]:
        """Analyze race for dutching strategy opportunity"""
        try:
            race_id = race["race_id"]

            # Get runners
            runners_query = """
            SELECT horse_name, jockey_name, official_rating, starting_price_decimal,
                   jockey_claim, weight_carried
            FROM race_results 
            WHERE race_id = ?
            AND starting_price_decimal > 0
            ORDER BY official_rating DESC
            LIMIT 6
            """

            runners = self.db_manager.execute_query(runners_query, (race_id,))
            if not runners or len(runners) < 4:
                return None

            # Get strategy analysis
            race_analysis = await self._get_strategy_analysis(race, list(runners))

            # Select top candidates for dutching
            suitable_horses = []
            for horse_analysis in race_analysis.get("horse_analyses", []):
                strategy_features = horse_analysis.get("strategy_features", {})
                dutching_potential = strategy_features.get(
                    "dutching_profit_potential", 0
                )
                confidence = horse_analysis.get("confidence_score", 0)

                if (
                    dutching_potential > 0.2 and confidence > 0.5
                ):  # Lower threshold for dutching
                    suitable_horses.append(horse_analysis)

            if len(suitable_horses) >= 3:
                # Calculate dutching stakes
                total_inverse_odds = sum(
                    1.0 / h.get("starting_price", 5.0) for h in suitable_horses
                )

                if total_inverse_odds < 0.85:  # Profitable dutching threshold
                    total_stake = 40.0
                    stakes = []
                    selections = []

                    for horse in suitable_horses[:4]:  # Max 4 horses
                        odds = horse.get("starting_price", 5.0)
                        stake = (total_stake / odds) / total_inverse_odds
                        stakes.append(round(stake, 2))
                        selections.append(horse["horse_name"])

                    avg_confidence = sum(
                        h.get("confidence_score", 0) for h in suitable_horses[:4]
                    ) / len(suitable_horses[:4])
                    expected_roi = (
                        ((1.0 - total_inverse_odds) / total_inverse_odds)
                        * avg_confidence
                        * 100
                    )

                    if expected_roi > 5.0:  # Minimum 5% expected ROI
                        return LiveStrategyOpportunity(
                            race_id=race_id,
                            course=race["course"],
                            race_time=datetime.strptime(
                                f"{datetime.now().date()} {race['race_time']}",
                                "%Y-%m-%d %H:%M:%S",
                            ),
                            strategy_type="dutching",
                            horse_selections=selections,
                            recommended_stakes=stakes,
                            expected_roi=expected_roi,
                            confidence_score=avg_confidence,
                            risk_level="low",
                            market_conditions={
                                "field_size": race.get("field_size", 0),
                                "total_inverse_odds": total_inverse_odds,
                                "race_class": race.get("race_class", ""),
                                "going": race.get("going", ""),
                            },
                            created_at=datetime.now(),
                        )

            return None

        except Exception as e:
            logger.error(
                f"Error analyzing dutching opportunity for race {race.get('race_id')}: {e}"
            )
            return None

    async def _get_strategy_analysis(self, race: Dict, runners: List) -> Dict:
        """Get strategy-aware analysis for race"""
        try:
            # Create simplified analysis using available data
            horse_analyses = []

            for runner in runners:
                runner_dict = dict(runner)

                # Calculate basic confidence score
                rating = runner_dict.get("official_rating", 70)
                odds = runner_dict.get("starting_price_decimal", 5.0)
                jockey_claim = runner_dict.get("jockey_claim", 0)

                # Simple confidence calculation
                base_confidence = min(1.0, rating / 100.0)
                odds_adjustment = min(1.0, 10.0 / odds)  # Favor shorter odds
                jockey_adjustment = 1.0 - (jockey_claim * 0.02)

                confidence = base_confidence * odds_adjustment * jockey_adjustment
                confidence = min(1.0, max(0.1, confidence))

                # Mock strategy features (would use actual strategy hub in production)
                strategy_features = {
                    "eighty_twenty_win_value": (
                        max(0, confidence - (1.0 / odds)) if odds >= 4.0 else 0
                    ),
                    "dutching_profit_potential": (
                        confidence * 0.5 if rating >= 70 else 0.2
                    ),
                    "market_efficiency": confidence,
                    "confidence_edge": confidence,
                }

                horse_analyses.append(
                    {
                        "horse_name": runner_dict["horse_name"],
                        "confidence_score": confidence,
                        "starting_price": odds,
                        "official_rating": rating,
                        "strategy_features": strategy_features,
                    }
                )

            return {"race_id": race["race_id"], "horse_analyses": horse_analyses}

        except Exception as e:
            logger.error(f"Error getting strategy analysis: {e}")
            return {"race_id": race.get("race_id", ""), "horse_analyses": []}

    async def _process_opportunity(self, opportunity: LiveStrategyOpportunity):
        """Process a strategy opportunity"""
        try:
            logger.info(
                f"🎯 Processing {opportunity.strategy_type} opportunity for race {opportunity.race_id}"
            )

            # Record opportunity
            self.monitor.db.record_live_opportunity(opportunity)
            self.daily_stats["opportunities_found"] += 1

            # Check if we should execute
            if self._should_execute_opportunity(opportunity):
                await self._execute_opportunity(opportunity)
            else:
                logger.info(
                    f"⏭️ Skipping execution for {opportunity.strategy_type} (criteria not met)"
                )

        except Exception as e:
            logger.error(f"Error processing opportunity: {e}")

    def _should_execute_opportunity(self, opportunity: LiveStrategyOpportunity) -> bool:
        """Determine if opportunity should be executed"""
        # Check confidence threshold
        if opportunity.confidence_score < self.config["min_confidence_threshold"]:
            return False

        # Check expected ROI
        if opportunity.expected_roi < 8.0:  # Minimum 8% expected ROI
            return False

        # Check daily stake limit
        total_stake = sum(opportunity.recommended_stakes)
        if (
            self.daily_stats["total_stake"] + total_stake
            > self.config["max_daily_stake"]
        ):
            return False

        # Check auto execution setting
        if not self.config["auto_execute"]:
            return False

        return True

    async def _execute_opportunity(self, opportunity: LiveStrategyOpportunity):
        """Execute a strategy opportunity (simulation)"""
        try:
            logger.info(f"🚀 Executing {opportunity.strategy_type} opportunity")

            total_stake = sum(opportunity.recommended_stakes)

            # Simulate execution result (replace with actual betting API in production)
            # For simulation, use confidence score to determine outcome
            win_probability = opportunity.confidence_score

            if opportunity.strategy_type == "80/20":
                # Simulate place betting outcome
                place_win = win_probability > 0.6 and (
                    hash(opportunity.race_id) % 100
                ) < (win_probability * 70)
                if place_win:
                    # Estimate place odds as 1/3 of win odds
                    avg_odds = 4.5  # Typical 80/20 odds
                    place_odds = avg_odds / 3
                    total_return = total_stake * place_odds
                    result = "win"
                else:
                    total_return = 0.0
                    result = "lose"
            else:
                # Simulate dutching outcome
                dutching_win = win_probability > 0.5 and (
                    hash(opportunity.race_id) % 100
                ) < (win_probability * 60)
                if dutching_win:
                    total_return = total_stake * 1.2  # Modest dutching return
                    result = "win"
                else:
                    total_return = 0.0
                    result = "lose"

            # Record execution
            execution_result = {
                "result": result,
                "total_return": total_return,
                "odds": [4.5] * len(opportunity.horse_selections),  # Mock odds
                "execution_time": datetime.now().isoformat(),
            }

            success = self.monitor.execute_opportunity(opportunity, execution_result)

            if success:
                # Update daily stats
                self.daily_stats["opportunities_executed"] += 1
                self.daily_stats["total_stake"] += total_stake
                self.daily_stats["total_return"] += total_return
                self.daily_stats["net_profit"] += total_return - total_stake

                profit_loss = total_return - total_stake
                logger.info(
                    f"✅ Execution completed: {result.upper()} - P&L: £{profit_loss:.2f}"
                )
            else:
                logger.error("❌ Failed to record execution")

        except Exception as e:
            logger.error(f"Error executing opportunity: {e}")

    async def _check_risk_limits(self) -> bool:
        """Check if risk management limits have been reached"""
        try:
            # Check daily loss limit
            if (
                self.daily_stats["net_profit"]
                < self.config["risk_management"]["daily_loss_limit"]
            ):
                logger.warning("⚠️ Daily loss limit reached")
                return True

            # Check drawdown (simplified)
            if self.daily_stats["total_stake"] > 0:
                current_roi = (
                    self.daily_stats["net_profit"] / self.daily_stats["total_stake"]
                ) * 100
                if current_roi < self.config["risk_management"]["max_drawdown_stop"]:
                    logger.warning(f"⚠️ Maximum drawdown reached: {current_roi:.2f}%")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return False

    async def _update_daily_stats(self):
        """Update daily statistics"""
        try:
            # Calculate current performance
            roi = 0.0
            if self.daily_stats["total_stake"] > 0:
                roi = (
                    self.daily_stats["net_profit"] / self.daily_stats["total_stake"]
                ) * 100

            # Log periodic updates
            if self.daily_stats["opportunities_found"] > 0:
                logger.info(
                    f"📊 Daily Stats: {self.daily_stats['opportunities_found']} opportunities, "
                    f"{self.daily_stats['opportunities_executed']} executed, "
                    f"ROI: {roi:.2f}%, P&L: £{self.daily_stats['net_profit']:.2f}"
                )

        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")

    async def _daily_reporting_loop(self):
        """Generate daily performance reports"""
        while self.system_active:
            try:
                # Wait until end of day or next morning
                now = datetime.now()
                next_report = now.replace(hour=23, minute=59, second=0, microsecond=0)
                if now > next_report:
                    next_report += timedelta(days=1)

                sleep_seconds = (next_report - now).total_seconds()
                await asyncio.sleep(min(sleep_seconds, 3600))  # Check at least hourly

                if now.hour == 23 and now.minute >= 59:
                    await self._generate_daily_report()

            except Exception as e:
                logger.error(f"Error in daily reporting loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def _generate_daily_report(self):
        """Generate daily performance report"""
        try:
            logger.info("📊 Generating daily performance report")

            # Get performance metrics
            eighty_twenty_metrics = self.monitor.db.get_strategy_performance(
                "80/20", days=1
            )
            dutching_metrics = self.monitor.db.get_strategy_performance(
                "dutching", days=1
            )

            report = {
                "date": datetime.now().date().isoformat(),
                "daily_stats": self.daily_stats.copy(),
                "strategy_performance": {
                    "80/20": eighty_twenty_metrics.to_dict(),
                    "dutching": dutching_metrics.to_dict(),
                },
                "system_uptime": "Active" if self.system_active else "Inactive",
            }

            # Save report
            report_path = f"/home/jc/Documents/Horse-race-ai-v2.03/data/daily_reports/report_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"📄 Daily report saved to {report_path}")

            # Reset daily stats for next day
            self.daily_stats = {
                "opportunities_found": 0,
                "opportunities_executed": 0,
                "total_stake": 0.0,
                "total_return": 0.0,
                "net_profit": 0.0,
            }

        except Exception as e:
            logger.error(f"Error generating daily report: {e}")

    async def stop_complete_system(self):
        """Stop the complete live system"""
        logger.info("⏹️ Stopping Complete Live System Integration")

        self.system_active = False

        # Stop monitoring
        self.monitor.stop_monitoring()

        # Stop dashboard
        if self.dashboard_process:
            self.dashboard_process.terminate()
            self.dashboard_process.wait()

        logger.info("✅ System stopped successfully")


async def main():
    """Main function for live system integration"""
    integrator = LiveSystemIntegrator()

    try:
        logger.info(
            "🏇 Starting Complete Live System Integration for 80/20 and Dutching Strategies"
        )
        logger.info("=" * 80)

        await integrator.start_complete_system()

    except KeyboardInterrupt:
        logger.info("⚡ System interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await integrator.stop_complete_system()


if __name__ == "__main__":
    asyncio.run(main())
