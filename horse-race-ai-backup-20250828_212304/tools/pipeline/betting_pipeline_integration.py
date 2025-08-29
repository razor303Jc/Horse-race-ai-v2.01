#!/usr/bin/env python3
"""
Betting Integration Pipeline - V2.03
==================================

Pipeline integration for the automated betting system.
Connects the betting integration system to the main pipeline orchestrator.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from tools.pipeline.betting_integration_system import BettingIntegrationSystem

logger = logging.getLogger(__name__)


class BettingPipelineIntegration:
    """Pipeline integration for automated betting system."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize betting pipeline integration."""
        self.config = self._load_config(config_path)
        self.betting_system = BettingIntegrationSystem(self.config)
        self.logger = logging.getLogger(__name__)

        # Results tracking
        self.integration_results = []

        self.logger.info("Betting Pipeline Integration initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}, using defaults")

        return {
            "betting_integration": {
                "enabled": True,
                "initial_bankroll": 1000.0,
                "automated_betting_enabled": False,  # Safety default
                "risk_management": {
                    "max_daily_risk": 0.15,
                    "max_race_exposure": 0.08,
                    "confidence_threshold": 0.65,
                    "emergency_stop_loss": 0.25,
                },
                "strategy_weights": {
                    "value_betting": 0.4,
                    "twenty_eighty": 0.3,
                    "each_way": 0.2,
                    "arbitrage": 0.1,
                },
                "odds_monitoring": {
                    "sources": ["betdaq", "bet365", "william_hill"],
                    "arbitrage_threshold": 0.02,
                    "refresh_interval": 30,
                },
            }
        }

    async def run_betting_integration_stage(
        self, race_data: Dict, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run the betting integration stage of the pipeline.

        Args:
            race_data: Race information from previous pipeline stages
            horses_data: Horse data with predictions from ML ensemble

        Returns:
            Betting integration results and recommendations
        """
        try:
            stage_start = datetime.now()
            self.logger.info("Starting betting integration pipeline stage")

            # Validate input data
            validation_result = self._validate_input_data(race_data, horses_data)
            if not validation_result["valid"]:
                return {
                    "status": "FAILED",
                    "error": f"Input validation failed: {validation_result['errors']}",
                    "timestamp": datetime.now().isoformat(),
                }

            # Check if betting integration is enabled
            if not self.config.get("betting_integration", {}).get("enabled", True):
                return {
                    "status": "SKIPPED",
                    "reason": "Betting integration disabled in configuration",
                    "timestamp": datetime.now().isoformat(),
                }

            # Run comprehensive betting integration
            integration_results = (
                await self.betting_system.run_automated_betting_integration(
                    race_data, horses_data
                )
            )

            # Process and enhance results
            processed_results = self._process_integration_results(integration_results)

            # Generate stage summary
            stage_duration = (datetime.now() - stage_start).total_seconds()

            pipeline_result = {
                "status": "SUCCESS",
                "stage": "betting_integration",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": stage_duration,
                "race_id": race_data.get("race_id", "unknown"),
                "integration_results": processed_results,
                "pipeline_metadata": {
                    "betting_system_version": "2.03",
                    "strategies_evaluated": len(
                        processed_results.get("strategy_recommendations", {})
                    ),
                    "bets_placed": len(
                        processed_results.get("execution_results", {}).get(
                            "placed_bets", []
                        )
                    ),
                    "total_stake": processed_results.get("bankroll_allocation", {})
                    .get("risk_allocation", {})
                    .get("total_allocated", 0),
                },
            }

            # Store results for tracking
            self.integration_results.append(pipeline_result)

            # Save detailed results
            await self._save_stage_results(pipeline_result)

            self.logger.info(
                f"Betting integration completed in {stage_duration:.2f}s - "
                f"{pipeline_result['pipeline_metadata']['bets_placed']} bets placed"
            )

            return pipeline_result

        except Exception as e:
            self.logger.error(f"Error in betting integration pipeline stage: {e}")
            return {
                "status": "ERROR",
                "stage": "betting_integration",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _validate_input_data(
        self, race_data: Dict, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """Validate input data for betting integration."""
        errors = []

        # Validate race data
        if not race_data:
            errors.append("Race data is empty")
        elif not race_data.get("race_id"):
            errors.append("Race ID missing from race data")

        # Validate horses data
        if not horses_data:
            errors.append("Horses data is empty")
        elif not isinstance(horses_data, list):
            errors.append("Horses data must be a list")
        else:
            # Check each horse has required data
            for i, horse in enumerate(horses_data):
                if not horse.get("horse_name"):
                    errors.append(f"Horse {i} missing name")

                prediction = horse.get("prediction", {})
                if not prediction:
                    errors.append(
                        f"Horse {horse.get('horse_name', i)} missing prediction data"
                    )
                elif not all(
                    key in prediction
                    for key in ["win_probability", "place_probability"]
                ):
                    errors.append(
                        f"Horse {horse.get('horse_name', i)} missing probability predictions"
                    )

        return {"valid": len(errors) == 0, "errors": errors}

    def _process_integration_results(self, integration_results: Dict) -> Dict[str, Any]:
        """Process and enhance integration results."""
        try:
            processed = {
                "betting_analysis": {
                    "timestamp": integration_results.get("timestamp"),
                    "race_id": integration_results.get("race_id"),
                    "analysis_complete": True,
                },
                "ai_predictions": integration_results.get("ai_predictions", {}),
                "odds_comparison": integration_results.get("odds_comparison", {}),
                "arbitrage_opportunities": integration_results.get(
                    "arbitrage_opportunities", []
                ),
                "strategy_recommendations": integration_results.get(
                    "strategy_recommendations", {}
                ),
                "bankroll_allocation": integration_results.get(
                    "bankroll_allocation", {}
                ),
                "execution_results": integration_results.get("execution_results", {}),
                "performance_tracking": integration_results.get(
                    "performance_update", {}
                ),
                "system_status": integration_results.get("system_status", {}),
            }

            # Add summary statistics
            processed["summary_statistics"] = self._generate_summary_statistics(
                processed
            )

            # Add recommendations summary
            processed["recommendations_summary"] = (
                self._generate_recommendations_summary(processed)
            )

            return processed

        except Exception as e:
            self.logger.error(f"Error processing integration results: {e}")
            return integration_results  # Return original if processing fails

    def _generate_summary_statistics(self, processed_results: Dict) -> Dict[str, Any]:
        """Generate summary statistics from processed results."""
        try:
            summary = {
                "total_strategies_evaluated": 0,
                "arbitrage_opportunities_found": len(
                    processed_results.get("arbitrage_opportunities", [])
                ),
                "betting_recommendations_generated": 0,
                "total_potential_stake": 0,
                "expected_roi": 0,
                "risk_level": "UNKNOWN",
            }

            # Count strategy recommendations
            strategy_recs = processed_results.get("strategy_recommendations", {})
            for strategy_type, strategies in strategy_recs.items():
                if isinstance(strategies, list):
                    summary["total_strategies_evaluated"] += len(strategies)
                    summary["betting_recommendations_generated"] += len(strategies)

            # Extract financial metrics
            bankroll_allocation = processed_results.get("bankroll_allocation", {})
            risk_allocation = bankroll_allocation.get("risk_allocation", {})

            summary["total_potential_stake"] = risk_allocation.get("total_allocated", 0)

            # Extract performance projections
            projections = bankroll_allocation.get("performance_projections", {})
            summary["expected_roi"] = projections.get("expected_roi_percentage", 0)

            # Determine overall risk level
            risk_percentage = risk_allocation.get("percentage_of_bankroll", 0)
            if risk_percentage > 15:
                summary["risk_level"] = "HIGH"
            elif risk_percentage > 8:
                summary["risk_level"] = "MEDIUM"
            else:
                summary["risk_level"] = "LOW"

            return summary

        except Exception as e:
            self.logger.error(f"Error generating summary statistics: {e}")
            return {}

    def _generate_recommendations_summary(
        self, processed_results: Dict
    ) -> Dict[str, Any]:
        """Generate summary of betting recommendations."""
        try:
            recommendations = {
                "top_value_bets": [],
                "best_arbitrage_opportunities": [],
                "recommended_actions": [],
                "risk_warnings": [],
            }

            # Extract top value bets
            strategy_recs = processed_results.get("strategy_recommendations", {})
            value_bets = strategy_recs.get("value_bets", [])

            # Sort by value and take top 3
            sorted_value_bets = sorted(
                value_bets, key=lambda x: x.get("value", 0), reverse=True
            )[:3]

            for bet in sorted_value_bets:
                recommendations["top_value_bets"].append(
                    {
                        "horse_name": bet.get("horse_name", "Unknown"),
                        "value_percentage": round(bet.get("value", 0) * 100, 1),
                        "recommended_stake": bet.get("recommended_stake", 0),
                        "odds": bet.get("odds", 0),
                        "risk_rating": bet.get("risk_rating", "UNKNOWN"),
                    }
                )

            # Extract best arbitrage opportunities
            arbitrage_opps = processed_results.get("arbitrage_opportunities", [])
            for opp in arbitrage_opps[:2]:  # Top 2
                recommendations["best_arbitrage_opportunities"].append(
                    {
                        "horse_name": opp.get("horse_name", "Unknown"),
                        "profit_margin": round(opp.get("arbitrage_margin", 0), 2),
                        "back_odds": opp.get("back_bet", {}).get("odds", 0),
                        "lay_odds": opp.get("lay_bet", {}).get("odds", 0),
                        "risk_rating": opp.get("risk_rating", "UNKNOWN"),
                    }
                )

            # Generate recommended actions
            if recommendations["top_value_bets"]:
                recommendations["recommended_actions"].append(
                    f"Consider value bet on {recommendations['top_value_bets'][0]['horse_name']} "
                    f"({recommendations['top_value_bets'][0]['value_percentage']}% value)"
                )

            if recommendations["best_arbitrage_opportunities"]:
                recommendations["recommended_actions"].append(
                    f"Arbitrage opportunity available on {recommendations['best_arbitrage_opportunities'][0]['horse_name']} "
                    f"({recommendations['best_arbitrage_opportunities'][0]['profit_margin']}% margin)"
                )

            # Check for risk warnings
            summary_stats = processed_results.get("summary_statistics", {})
            if summary_stats.get("risk_level") == "HIGH":
                recommendations["risk_warnings"].append(
                    f"High risk exposure: {summary_stats.get('total_potential_stake', 0):.2f} stake recommended"
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations summary: {e}")
            return {}

    async def _save_stage_results(self, pipeline_result: Dict):
        """Save stage results to file."""
        try:
            # Create results directory
            results_dir = "reports/betting_integration"
            os.makedirs(results_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            race_id = pipeline_result.get("race_id", "unknown")
            filename = f"betting_integration_{race_id}_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)

            # Save results
            with open(filepath, "w") as f:
                json.dump(pipeline_result, f, indent=2, default=str)

            self.logger.info(f"Betting integration results saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving stage results: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of all integration runs."""
        if not self.integration_results:
            return {"total_runs": 0, "status": "No integration runs completed"}

        successful_runs = [
            r for r in self.integration_results if r.get("status") == "SUCCESS"
        ]

        summary = {
            "total_runs": len(self.integration_results),
            "successful_runs": len(successful_runs),
            "success_rate": len(successful_runs) / len(self.integration_results) * 100,
            "total_bets_placed": sum(
                r.get("pipeline_metadata", {}).get("bets_placed", 0)
                for r in successful_runs
            ),
            "total_stake_allocated": sum(
                r.get("pipeline_metadata", {}).get("total_stake", 0)
                for r in successful_runs
            ),
            "last_run": (
                self.integration_results[-1].get("timestamp")
                if self.integration_results
                else None
            ),
        }

        return summary


async def main():
    """Main function for testing betting pipeline integration."""
    # Initialize integration
    betting_pipeline = BettingPipelineIntegration()

    # Sample data for testing
    race_data = {
        "race_id": "test_race_betting_001",
        "race_time": "15:30",
        "track": "Newmarket",
        "race_type": "Stakes",
        "distance": "1m2f",
        "going": "Good",
    }

    horses_data = [
        {
            "horse_name": "Fast Track",
            "odds": 4.0,
            "prediction": {
                "win_probability": 0.32,
                "place_probability": 0.68,
                "consensus_rating": 0.72,
                "confidence": 0.85,
            },
        },
        {
            "horse_name": "Lightning Bolt",
            "odds": 2.5,
            "prediction": {
                "win_probability": 0.45,
                "place_probability": 0.75,
                "consensus_rating": 0.82,
                "confidence": 0.88,
            },
        },
        {
            "horse_name": "Storm Chaser",
            "odds": 6.0,
            "prediction": {
                "win_probability": 0.22,
                "place_probability": 0.52,
                "consensus_rating": 0.58,
                "confidence": 0.72,
            },
        },
    ]

    # Run betting integration pipeline stage
    result = await betting_pipeline.run_betting_integration_stage(
        race_data, horses_data
    )

    print("\n=== BETTING PIPELINE INTEGRATION RESULTS ===")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f}s")

    if result.get("status") == "SUCCESS":
        metadata = result.get("pipeline_metadata", {})
        print(f"Strategies Evaluated: {metadata.get('strategies_evaluated', 0)}")
        print(f"Bets Placed: {metadata.get('bets_placed', 0)}")
        print(f"Total Stake: £{metadata.get('total_stake', 0):.2f}")

        # Show recommendations summary
        integration_results = result.get("integration_results", {})
        recommendations = integration_results.get("recommendations_summary", {})

        if recommendations.get("top_value_bets"):
            print("\nTop Value Bets:")
            for bet in recommendations["top_value_bets"]:
                print(
                    f"  - {bet['horse_name']}: {bet['value_percentage']}% value @ {bet['odds']}"
                )

        if recommendations.get("best_arbitrage_opportunities"):
            print("\nArbitrage Opportunities:")
            for opp in recommendations["best_arbitrage_opportunities"]:
                print(f"  - {opp['horse_name']}: {opp['profit_margin']}% profit margin")

    print("\n=== INTEGRATION SUMMARY ===")
    summary = betting_pipeline.get_integration_summary()
    print(f"Total Runs: {summary.get('total_runs', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"Total Bets Placed: {summary.get('total_bets_placed', 0)}")

    print("\n=== BETTING PIPELINE INTEGRATION COMPLETE ===")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Run the main function
    asyncio.run(main())
