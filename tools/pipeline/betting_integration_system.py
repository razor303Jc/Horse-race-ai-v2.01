#!/usr/bin/env python3
"""
Automated Betting Integration System - V2.03
==========================================

Comprehensive betting system integration with:
- Automated strategy selection and risk management
- Multi-strategy portfolio management
- Live odds comparison and arbitrage detection
- Automated bet placement with comprehensive safeguards
- Real-time performance monitoring and bankroll optimization

This integrates all existing betting components into an automated pipeline.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Import existing betting components
from src.horse_racing_ai.betting.advanced_strategies import AdvancedBettingStrategies
from src.horse_racing_ai.integration.ai_betting_integration import (
    AIBettingIntegrationSystem,
)
from src.betdaq.betdaq_live_betting import LiveBettingEngine, AILiveBettingInterface
from src.horse_racing_ai.ml.v2_01_ensemble_predictor import V201EnsemblePredictor
from src.horse_racing_ai.ml.v2_01_consensus_rating import V201ConsensusRating

logger = logging.getLogger(__name__)


class BettingIntegrationSystem:
    """
    Automated Betting Integration System for V2.03

    Coordinates all betting components into an intelligent automated system:
    - Strategy selection based on market conditions
    - Risk management and bankroll optimization
    - Multi-strategy portfolio management
    - Live odds monitoring and arbitrage detection
    - Automated bet placement with comprehensive safeguards
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the betting integration system."""
        self.config = config or self._load_default_config()
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.advanced_strategies = AdvancedBettingStrategies(
            initial_bankroll=self.config.get("initial_bankroll", 1000.0)
        )

        self.ai_betting_integration = AIBettingIntegrationSystem(
            initial_bankroll=self.config.get("initial_bankroll", 1000.0),
            ai_confidence_threshold=self.config.get("ai_confidence_threshold", 0.7),
            value_threshold=self.config.get("value_threshold", 0.1),
        )

        # Strategy selection parameters
        self.strategy_weights = self.config.get(
            "strategy_weights",
            {
                "value_betting": 0.4,
                "twenty_eighty": 0.3,
                "each_way": 0.2,
                "arbitrage": 0.1,
            },
        )

        # Risk management parameters
        self.max_daily_risk = self.config.get("max_daily_risk", 0.15)  # 15%
        self.max_race_exposure = self.config.get("max_race_exposure", 0.08)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.65)

        # Portfolio management
        self.active_bets = []
        self.daily_performance = {}
        self.strategy_performance = {}

        # Odds monitoring
        self.odds_sources = self.config.get(
            "odds_sources", ["betdaq", "bet365", "william_hill"]
        )
        self.arbitrage_threshold = self.config.get("arbitrage_threshold", 0.02)

        self.logger.info("Betting Integration System initialized")

    def _load_default_config(self) -> Dict:
        """Load default configuration."""
        return {
            "initial_bankroll": 1000.0,
            "ai_confidence_threshold": 0.7,
            "value_threshold": 0.1,
            "max_daily_risk": 0.15,
            "max_race_exposure": 0.08,
            "confidence_threshold": 0.65,
            "strategy_weights": {
                "value_betting": 0.4,
                "twenty_eighty": 0.3,
                "each_way": 0.2,
                "arbitrage": 0.1,
            },
            "odds_sources": ["betdaq", "bet365", "william_hill"],
            "arbitrage_threshold": 0.02,
            "automated_betting_enabled": False,  # Safety default
            "max_bet_frequency": 10,  # Max bets per hour
            "emergency_stop_loss": 0.25,  # Stop if 25% of bankroll lost
        }

    async def run_automated_betting_integration(
        self, race_data: Dict, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Main betting integration pipeline.

        Args:
            race_data: Race information
            horses_data: Horse predictions and data

        Returns:
            Comprehensive betting analysis and recommendations
        """
        try:
            self.logger.info("Starting automated betting integration")

            # Step 1: Generate AI predictions with ensemble
            ai_predictions = await self._generate_enhanced_predictions(
                race_data, horses_data
            )

            # Step 2: Collect and compare odds from multiple sources
            odds_comparison = await self._collect_odds_comparison(
                race_data, horses_data
            )

            # Step 3: Identify arbitrage opportunities
            arbitrage_opportunities = await self._detect_arbitrage_opportunities(
                odds_comparison
            )

            # Step 4: Generate multi-strategy recommendations
            strategy_recommendations = (
                await (
                    self._generate_multi_strategy_recommendations(
                        ai_predictions, odds_comparison
                    )
                )
            )

            # Step 5: Apply portfolio risk management
            risk_managed_strategies = await self._apply_portfolio_risk_management(
                strategy_recommendations
            )

            # Step 6: Select optimal betting strategy mix
            optimal_strategy_mix = await self._select_optimal_strategy_mix(
                risk_managed_strategies, arbitrage_opportunities
            )

            # Step 7: Calculate bankroll allocation
            bankroll_allocation = await self._calculate_bankroll_allocation(
                optimal_strategy_mix
            )

            # Step 8: Execute automated bet placement (if enabled)
            execution_results = await self._execute_automated_betting(
                bankroll_allocation, race_data
            )

            # Step 9: Update performance tracking
            performance_update = await self._update_performance_tracking(
                execution_results
            )

            # Compile comprehensive results
            results = {
                "timestamp": datetime.now().isoformat(),
                "race_id": race_data.get("race_id", "unknown"),
                "ai_predictions": ai_predictions,
                "odds_comparison": odds_comparison,
                "arbitrage_opportunities": arbitrage_opportunities,
                "strategy_recommendations": strategy_recommendations,
                "risk_managed_strategies": risk_managed_strategies,
                "optimal_strategy_mix": optimal_strategy_mix,
                "bankroll_allocation": bankroll_allocation,
                "execution_results": execution_results,
                "performance_update": performance_update,
                "system_status": self._get_system_status(),
            }

            # Save results for tracking
            await self._save_betting_analysis(results)

            self.logger.info(
                f"Betting integration completed - {len(execution_results.get('placed_bets', []))} bets placed"
            )

            return results

        except Exception as e:
            self.logger.error(f"Error in automated betting integration: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "system_status": self._get_system_status(),
            }

    async def _generate_enhanced_predictions(
        self, race_data: Dict, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """Generate enhanced AI predictions using ensemble methods."""
        try:
            # Use AI betting integration for enhanced predictions
            betting_odds = self._extract_current_odds(horses_data)

            ai_result = self.ai_betting_integration.analyze_race_with_ai_betting(
                race_data, horses_data, betting_odds
            )

            return {
                "ensemble_predictions": ai_result.ai_predictions,
                "confidence_scores": self._extract_confidence_scores(ai_result),
                "value_assessments": self._extract_value_assessments(ai_result),
                "consensus_ratings": self._generate_consensus_ratings(horses_data),
            }

        except Exception as e:
            self.logger.error(f"Error generating enhanced predictions: {e}")
            return {}

    async def _collect_odds_comparison(
        self, race_data: Dict, horses_data: List[Dict]
    ) -> Dict[str, Any]:
        """Collect and compare odds from multiple sources."""
        try:
            odds_comparison = {}

            for horse in horses_data:
                horse_name = horse.get("horse_name", "Unknown")
                odds_comparison[horse_name] = {
                    "current_odds": horse.get("odds", 0),
                    "sources": {},
                    "best_odds": 0,
                    "best_source": "",
                    "odds_movement": self._calculate_odds_movement(horse),
                    "value_rating": 0,
                }

                # Simulate odds from multiple sources (in production, would connect to APIs)
                for source in self.odds_sources:
                    simulated_odds = self._simulate_odds_from_source(horse, source)
                    odds_comparison[horse_name]["sources"][source] = simulated_odds

                    # Track best odds
                    if simulated_odds > odds_comparison[horse_name]["best_odds"]:
                        odds_comparison[horse_name]["best_odds"] = simulated_odds
                        odds_comparison[horse_name]["best_source"] = source

                # Calculate value rating
                odds_comparison[horse_name]["value_rating"] = (
                    self._calculate_value_rating(horse, odds_comparison[horse_name])
                )

            return {
                "odds_by_horse": odds_comparison,
                "market_summary": self._generate_market_summary(odds_comparison),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error collecting odds comparison: {e}")
            return {}

    async def _detect_arbitrage_opportunities(
        self, odds_comparison: Dict
    ) -> List[Dict]:
        """Detect arbitrage opportunities across different bookmakers."""
        try:
            arbitrage_opportunities = []

            for horse_name, odds_data in odds_comparison.get(
                "odds_by_horse", {}
            ).items():
                sources = odds_data.get("sources", {})

                if len(sources) < 2:
                    continue

                # Find best odds for back and lay (simulated)
                best_back_odds = max(sources.values())
                best_back_source = max(sources, key=sources.get)

                # Calculate arbitrage potential
                for source, odds in sources.items():
                    if source != best_back_source and odds > 0:
                        # Calculate if arbitrage exists
                        back_prob = 1 / best_back_odds
                        lay_prob = 1 / odds
                        total_prob = back_prob + lay_prob

                        if total_prob < (1 - self.arbitrage_threshold):
                            arbitrage_margin = (1 - total_prob) * 100

                            opportunity = {
                                "horse_name": horse_name,
                                "arbitrage_margin": arbitrage_margin,
                                "back_bet": {
                                    "source": best_back_source,
                                    "odds": best_back_odds,
                                    "stake_percentage": lay_prob / (1 - total_prob),
                                },
                                "lay_bet": {
                                    "source": source,
                                    "odds": odds,
                                    "stake_percentage": back_prob / (1 - total_prob),
                                },
                                "profit_margin": arbitrage_margin,
                                "risk_rating": (
                                    "LOW" if arbitrage_margin > 3 else "MEDIUM"
                                ),
                            }

                            arbitrage_opportunities.append(opportunity)

            # Sort by profit margin
            arbitrage_opportunities.sort(
                key=lambda x: x["arbitrage_margin"], reverse=True
            )

            self.logger.info(
                f"Found {len(arbitrage_opportunities)} arbitrage opportunities"
            )
            return arbitrage_opportunities

        except Exception as e:
            self.logger.error(f"Error detecting arbitrage opportunities: {e}")
            return []

    async def _generate_multi_strategy_recommendations(
        self, ai_predictions: Dict, odds_comparison: Dict
    ) -> Dict[str, Any]:
        """Generate recommendations for multiple betting strategies."""
        try:
            recommendations = {
                "value_bets": [],
                "twenty_eighty_strategies": [],
                "each_way_opportunities": [],
                "arbitrage_plays": [],
                "strategy_scores": {},
            }

            # Extract prediction data
            horses_predictions = ai_predictions.get("ensemble_predictions", {}).get(
                "horses", []
            )

            # Convert to format expected by advanced strategies
            race_predictions = [
                {
                    "race_id": ai_predictions.get("ensemble_predictions", {}).get(
                        "race_id", "unknown"
                    ),
                    "horses": horses_predictions,
                }
            ]

            # Generate value betting opportunities
            value_bets = self.advanced_strategies.get_betting_recommendations(
                race_predictions
            )
            recommendations["value_bets"] = value_bets.get("value_bets", [])

            # Generate 20/80 strategies
            twenty_eighty = (
                self.advanced_strategies.get_top_three_twenty_eighty_selections(
                    race_predictions,
                    total_daily_bankroll=self.advanced_strategies.current_bankroll
                    * 0.1,
                )
            )
            recommendations["twenty_eighty_strategies"] = [
                self._convert_twenty_eighty_to_dict(strategy)
                for strategy in twenty_eighty
            ]

            # Generate each-way opportunities
            for horse in horses_predictions:
                win_prob = horse.get("prediction", {}).get("win_probability", 0)
                place_prob = horse.get("prediction", {}).get("place_probability", 0)

                if win_prob > 0 and place_prob > 0:
                    win_odds = horse.get(
                        "win_odds", 1.0 / win_prob if win_prob > 0 else 10.0
                    )
                    place_odds = win_odds * 0.25  # Approximate place odds

                    ew_opportunity = self.advanced_strategies.calculate_each_way_value(
                        win_odds, place_odds, win_prob, place_prob
                    )

                    if ew_opportunity["win"].value > self.config.get(
                        "value_threshold", 0.1
                    ):
                        recommendations["each_way_opportunities"].append(
                            {
                                "horse_name": horse.get("horse_name", "Unknown"),
                                "win_bet": self._convert_betting_opportunity_to_dict(
                                    ew_opportunity["win"]
                                ),
                                "place_bet": self._convert_betting_opportunity_to_dict(
                                    ew_opportunity["place"]
                                ),
                            }
                        )

            # Calculate strategy effectiveness scores
            recommendations["strategy_scores"] = self._calculate_strategy_scores(
                recommendations
            )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating multi-strategy recommendations: {e}")
            return {}

    async def _apply_portfolio_risk_management(
        self, strategy_recommendations: Dict
    ) -> Dict[str, Any]:
        """Apply portfolio-level risk management to strategy recommendations."""
        try:
            current_bankroll = self.advanced_strategies.current_bankroll
            max_daily_exposure = current_bankroll * self.max_daily_risk
            max_race_exposure = current_bankroll * self.max_race_exposure

            risk_managed = {
                "filtered_strategies": {},
                "risk_allocations": {},
                "rejected_strategies": [],
                "risk_metrics": {},
            }

            total_recommended_stake = 0

            # Apply risk filters to each strategy type
            for strategy_type, strategies in strategy_recommendations.items():
                if strategy_type == "strategy_scores":
                    continue

                filtered_strategies = []

                for strategy in strategies:
                    # Extract stake information
                    stake = self._extract_strategy_stake(strategy)

                    # Check individual bet limits
                    if stake > current_bankroll * 0.05:  # Max 5% per bet
                        risk_managed["rejected_strategies"].append(
                            {
                                "strategy": strategy,
                                "reason": "Stake exceeds 5% of bankroll",
                                "stake": stake,
                            }
                        )
                        continue

                    # Check total exposure
                    if total_recommended_stake + stake > max_race_exposure:
                        risk_managed["rejected_strategies"].append(
                            {
                                "strategy": strategy,
                                "reason": "Would exceed race exposure limit",
                                "stake": stake,
                            }
                        )
                        continue

                    # Apply Kelly scaling if needed
                    risk_adjusted_stake = self._apply_kelly_scaling(strategy, stake)
                    strategy["risk_adjusted_stake"] = risk_adjusted_stake

                    filtered_strategies.append(strategy)
                    total_recommended_stake += risk_adjusted_stake

                risk_managed["filtered_strategies"][strategy_type] = filtered_strategies

            # Calculate risk allocations
            risk_managed["risk_allocations"] = {
                "total_allocated": total_recommended_stake,
                "percentage_of_bankroll": (total_recommended_stake / current_bankroll)
                * 100,
                "remaining_capacity": max_race_exposure - total_recommended_stake,
                "risk_level": self._assess_portfolio_risk_level(
                    total_recommended_stake, current_bankroll
                ),
            }

            # Generate risk metrics
            risk_managed["risk_metrics"] = self._calculate_portfolio_risk_metrics(
                risk_managed["filtered_strategies"]
            )

            return risk_managed

        except Exception as e:
            self.logger.error(f"Error applying portfolio risk management: {e}")
            return {}

    async def _select_optimal_strategy_mix(
        self, risk_managed_strategies: Dict, arbitrage_opportunities: List
    ) -> Dict[str, Any]:
        """Select optimal mix of betting strategies based on current conditions."""
        try:
            strategy_mix = {
                "selected_strategies": [],
                "strategy_allocation": {},
                "total_stake": 0,
                "expected_roi": 0,
                "risk_score": 0,
            }

            # Prioritize arbitrage opportunities (guaranteed profit)
            for arb_opp in arbitrage_opportunities[:2]:  # Limit to top 2
                if arb_opp["arbitrage_margin"] > self.arbitrage_threshold * 100:
                    strategy_mix["selected_strategies"].append(
                        {
                            "type": "arbitrage",
                            "strategy": arb_opp,
                            "priority": 1,
                            "allocation_weight": 0.3,
                        }
                    )

            # Select best value bets
            value_bets = risk_managed_strategies.get("filtered_strategies", {}).get(
                "value_bets", []
            )
            for value_bet in sorted(
                value_bets, key=lambda x: x.get("value", 0), reverse=True
            )[:3]:
                if value_bet.get("value", 0) > self.config.get("value_threshold", 0.1):
                    strategy_mix["selected_strategies"].append(
                        {
                            "type": "value_betting",
                            "strategy": value_bet,
                            "priority": 2,
                            "allocation_weight": self.strategy_weights.get(
                                "value_betting", 0.4
                            ),
                        }
                    )

            # Select best 20/80 strategies
            twenty_eighty = risk_managed_strategies.get("filtered_strategies", {}).get(
                "twenty_eighty_strategies", []
            )
            for te_strategy in twenty_eighty[:2]:  # Top 2
                if te_strategy.get("expected_value", 0) > 0:
                    strategy_mix["selected_strategies"].append(
                        {
                            "type": "twenty_eighty",
                            "strategy": te_strategy,
                            "priority": 3,
                            "allocation_weight": self.strategy_weights.get(
                                "twenty_eighty", 0.3
                            ),
                        }
                    )

            # Calculate total allocation
            total_weight = sum(
                s["allocation_weight"] for s in strategy_mix["selected_strategies"]
            )
            if total_weight > 0:
                # Normalize weights
                for strategy in strategy_mix["selected_strategies"]:
                    strategy["normalized_weight"] = (
                        strategy["allocation_weight"] / total_weight
                    )
                    stake = self._extract_strategy_stake(strategy["strategy"])
                    strategy["allocated_stake"] = stake * strategy["normalized_weight"]
                    strategy_mix["total_stake"] += strategy["allocated_stake"]

            # Calculate expected ROI and risk
            strategy_mix["expected_roi"] = self._calculate_expected_portfolio_roi(
                strategy_mix["selected_strategies"]
            )
            strategy_mix["risk_score"] = self._calculate_portfolio_risk_score(
                strategy_mix["selected_strategies"]
            )

            self.logger.info(
                f"Selected {len(strategy_mix['selected_strategies'])} strategies for execution"
            )

            return strategy_mix

        except Exception as e:
            self.logger.error(f"Error selecting optimal strategy mix: {e}")
            return {}

    async def _calculate_bankroll_allocation(
        self, optimal_strategy_mix: Dict
    ) -> Dict[str, Any]:
        """Calculate optimal bankroll allocation across selected strategies."""
        try:
            current_bankroll = self.advanced_strategies.current_bankroll

            allocation = {
                "total_bankroll": current_bankroll,
                "available_for_betting": current_bankroll * 0.85,  # Keep 15% reserve
                "strategy_allocations": [],
                "risk_allocation": {},
                "performance_projections": {},
            }

            available_amount = allocation["available_for_betting"]

            # Allocate funds to each selected strategy
            for strategy in optimal_strategy_mix.get("selected_strategies", []):
                stake = strategy.get("allocated_stake", 0)

                # Apply bankroll percentage limits
                max_allowed = available_amount * 0.15  # Max 15% to any single strategy
                final_stake = min(stake, max_allowed)

                strategy_allocation = {
                    "strategy_type": strategy["type"],
                    "allocated_amount": final_stake,
                    "percentage_of_bankroll": (final_stake / current_bankroll) * 100,
                    "expected_return": final_stake
                    * self._get_strategy_expected_multiplier(strategy),
                    "risk_level": self._assess_strategy_risk(strategy),
                    "confidence_score": self._get_strategy_confidence(strategy),
                }

                allocation["strategy_allocations"].append(strategy_allocation)

            # Calculate overall risk allocation
            total_allocated = sum(
                s["allocated_amount"] for s in allocation["strategy_allocations"]
            )
            allocation["risk_allocation"] = {
                "total_allocated": total_allocated,
                "percentage_allocated": (total_allocated / current_bankroll) * 100,
                "cash_reserve": current_bankroll - total_allocated,
                "reserve_percentage": (
                    (current_bankroll - total_allocated) / current_bankroll
                )
                * 100,
            }

            # Generate performance projections
            allocation["performance_projections"] = (
                self._generate_performance_projections(
                    allocation["strategy_allocations"]
                )
            )

            return allocation

        except Exception as e:
            self.logger.error(f"Error calculating bankroll allocation: {e}")
            return {}

    async def _execute_automated_betting(
        self, bankroll_allocation: Dict, race_data: Dict
    ) -> Dict[str, Any]:
        """Execute automated bet placement with comprehensive safeguards."""
        try:
            execution_results = {
                "placed_bets": [],
                "rejected_bets": [],
                "execution_summary": {},
                "safeguard_checks": {},
            }

            # Safety check: Only execute if explicitly enabled
            if not self.config.get("automated_betting_enabled", False):
                execution_results["execution_summary"] = {
                    "status": "DISABLED",
                    "reason": "Automated betting not enabled in configuration",
                    "bets_simulated": len(
                        bankroll_allocation.get("strategy_allocations", [])
                    ),
                }
                return execution_results

            # Pre-execution safety checks
            safety_checks = await self._perform_pre_execution_safety_checks()
            execution_results["safeguard_checks"] = safety_checks

            if not safety_checks.get("all_checks_passed", False):
                execution_results["execution_summary"] = {
                    "status": "BLOCKED",
                    "reason": "Failed safety checks",
                    "failed_checks": safety_checks.get("failed_checks", []),
                }
                return execution_results

            # Execute each strategy allocation
            for allocation in bankroll_allocation.get("strategy_allocations", []):
                try:
                    bet_result = await self._execute_individual_bet(
                        allocation, race_data
                    )

                    if bet_result.get("success", False):
                        execution_results["placed_bets"].append(bet_result)
                    else:
                        execution_results["rejected_bets"].append(bet_result)

                except Exception as e:
                    self.logger.error(f"Error executing individual bet: {e}")
                    execution_results["rejected_bets"].append(
                        {
                            "allocation": allocation,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # Generate execution summary
            execution_results["execution_summary"] = {
                "status": "COMPLETED",
                "total_bets_attempted": len(
                    bankroll_allocation.get("strategy_allocations", [])
                ),
                "successful_placements": len(execution_results["placed_bets"]),
                "rejected_placements": len(execution_results["rejected_bets"]),
                "total_stake_placed": sum(
                    bet.get("stake", 0) for bet in execution_results["placed_bets"]
                ),
                "execution_timestamp": datetime.now().isoformat(),
            }

            return execution_results

        except Exception as e:
            self.logger.error(f"Error in automated betting execution: {e}")
            return {
                "error": str(e),
                "execution_summary": {"status": "ERROR"},
                "timestamp": datetime.now().isoformat(),
            }

    async def _perform_pre_execution_safety_checks(self) -> Dict[str, Any]:
        """Perform comprehensive safety checks before bet execution."""
        try:
            checks = {
                "bankroll_check": False,
                "frequency_check": False,
                "loss_limit_check": False,
                "system_health_check": False,
                "market_condition_check": False,
                "all_checks_passed": False,
                "failed_checks": [],
            }

            # Check bankroll health
            current_bankroll = self.advanced_strategies.current_bankroll
            if current_bankroll > self.config.get("minimum_bankroll", 100):
                checks["bankroll_check"] = True
            else:
                checks["failed_checks"].append("Insufficient bankroll")

            # Check betting frequency
            if len(self.active_bets) < self.config.get("max_bet_frequency", 10):
                checks["frequency_check"] = True
            else:
                checks["failed_checks"].append("Betting frequency limit exceeded")

            # Check daily loss limits
            daily_pnl = self.daily_performance.get("net_profit", 0)
            max_loss = self.config.get("initial_bankroll", 1000) * self.config.get(
                "emergency_stop_loss", 0.25
            )
            if abs(daily_pnl) < max_loss:
                checks["loss_limit_check"] = True
            else:
                checks["failed_checks"].append("Daily loss limit approached")

            # System health check (basic)
            checks["system_health_check"] = True

            # Market condition check (basic)
            checks["market_condition_check"] = True

            # Overall assessment
            checks["all_checks_passed"] = len(checks["failed_checks"]) == 0

            return checks

        except Exception as e:
            self.logger.error(f"Error in safety checks: {e}")
            return {
                "all_checks_passed": False,
                "failed_checks": [f"Safety check error: {e}"],
            }

    async def _execute_individual_bet(
        self, allocation: Dict, race_data: Dict
    ) -> Dict[str, Any]:
        """Execute an individual bet based on allocation."""
        try:
            # This would integrate with actual betting APIs
            # For now, simulate bet placement

            result = {
                "success": True,
                "allocation": allocation,
                "stake": allocation.get("allocated_amount", 0),
                "bet_type": allocation.get("strategy_type", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "bet_id": f"sim_{int(datetime.now().timestamp())}",
                "status": "PLACED",
            }

            # Add to active bets tracking
            self.active_bets.append(result)

            return result

        except Exception as e:
            return {
                "success": False,
                "allocation": allocation,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _update_performance_tracking(
        self, execution_results: Dict
    ) -> Dict[str, Any]:
        """Update performance tracking with latest results."""
        try:
            performance_update = {
                "timestamp": datetime.now().isoformat(),
                "daily_stats": {},
                "strategy_performance": {},
                "bankroll_update": {},
            }

            # Update daily statistics
            total_stake = execution_results.get("execution_summary", {}).get(
                "total_stake_placed", 0
            )
            successful_bets = len(execution_results.get("placed_bets", []))

            if datetime.now().date().isoformat() not in self.daily_performance:
                self.daily_performance[datetime.now().date().isoformat()] = {
                    "total_stake": 0,
                    "total_bets": 0,
                    "net_profit": 0,
                    "win_rate": 0,
                }

            daily_stats = self.daily_performance[datetime.now().date().isoformat()]
            daily_stats["total_stake"] += total_stake
            daily_stats["total_bets"] += successful_bets

            performance_update["daily_stats"] = daily_stats

            # Update strategy performance tracking
            for bet in execution_results.get("placed_bets", []):
                strategy_type = bet.get("bet_type", "unknown")
                if strategy_type not in self.strategy_performance:
                    self.strategy_performance[strategy_type] = {
                        "total_bets": 0,
                        "total_stake": 0,
                        "wins": 0,
                        "net_profit": 0,
                    }

                self.strategy_performance[strategy_type]["total_bets"] += 1
                self.strategy_performance[strategy_type]["total_stake"] += bet.get(
                    "stake", 0
                )

            performance_update["strategy_performance"] = self.strategy_performance

            # Update bankroll information
            performance_update["bankroll_update"] = {
                "current_bankroll": self.advanced_strategies.current_bankroll,
                "total_exposure": sum(bet.get("stake", 0) for bet in self.active_bets),
                "available_balance": self.advanced_strategies.current_bankroll
                - sum(bet.get("stake", 0) for bet in self.active_bets),
            }

            return performance_update

        except Exception as e:
            self.logger.error(f"Error updating performance tracking: {e}")
            return {}

    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "automated_betting_enabled": self.config.get(
                "automated_betting_enabled", False
            ),
            "current_bankroll": self.advanced_strategies.current_bankroll,
            "active_bets": len(self.active_bets),
            "daily_performance": self.daily_performance.get(
                datetime.now().date().isoformat(), {}
            ),
            "system_health": "OPERATIONAL",
            "last_update": datetime.now().isoformat(),
        }

    async def _save_betting_analysis(self, results: Dict):
        """Save betting analysis results."""
        try:
            os.makedirs("reports/betting_analysis", exist_ok=True)

            filename = (
                f"betting_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            filepath = f"reports/betting_analysis/{filename}"

            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            self.logger.info(f"Betting analysis saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving betting analysis: {e}")

    # Helper methods for data conversion and calculation
    def _extract_current_odds(self, horses_data: List[Dict]) -> Dict[str, float]:
        """Extract current odds from horses data."""
        return {
            horse.get("horse_name", "Unknown"): horse.get("odds", 0)
            for horse in horses_data
        }

    def _extract_confidence_scores(self, ai_result) -> Dict[str, float]:
        """Extract confidence scores from AI result."""
        return {
            "overall_confidence": ai_result.confidence_score,
            "prediction_confidence": getattr(ai_result, "prediction_confidence", 0.8),
        }

    def _extract_value_assessments(self, ai_result) -> Dict[str, Any]:
        """Extract value assessments from AI result."""
        return {
            "betting_recommendations": ai_result.betting_recommendations,
            "bankroll_impact": ai_result.bankroll_impact,
        }

    def _generate_consensus_ratings(self, horses_data: List[Dict]) -> Dict[str, float]:
        """Generate consensus ratings for horses."""
        return {
            horse.get("horse_name", "Unknown"): horse.get("prediction", {}).get(
                "consensus_rating", 0.5
            )
            for horse in horses_data
        }

    def _calculate_odds_movement(self, horse: Dict) -> float:
        """Calculate odds movement (simulated)."""
        return np.random.uniform(-0.1, 0.1)  # Simulate ±10% movement

    def _simulate_odds_from_source(self, horse: Dict, source: str) -> float:
        """Simulate odds from a specific source."""
        base_odds = horse.get("odds", 2.0)
        # Add source-specific variation
        variation = np.random.uniform(0.95, 1.05)
        return round(base_odds * variation, 2)

    def _calculate_value_rating(self, horse: Dict, odds_data: Dict) -> float:
        """Calculate value rating for a horse."""
        best_odds = odds_data.get("best_odds", 0)
        win_prob = horse.get("prediction", {}).get("win_probability", 0)

        if best_odds > 0 and win_prob > 0:
            implied_prob = 1 / best_odds
            return max(0, (win_prob - implied_prob) / implied_prob)

        return 0

    def _generate_market_summary(self, odds_comparison: Dict) -> Dict[str, Any]:
        """Generate market summary from odds comparison."""
        all_odds = []
        for horse_data in odds_comparison.values():
            all_odds.extend(horse_data.get("sources", {}).values())

        return {
            "average_odds": np.mean(all_odds) if all_odds else 0,
            "odds_range": [min(all_odds), max(all_odds)] if all_odds else [0, 0],
            "market_liquidity": len(all_odds),
            "volatility": np.std(all_odds) if len(all_odds) > 1 else 0,
        }

    def _convert_twenty_eighty_to_dict(self, strategy) -> Dict:
        """Convert TwentyEightyStrategy to dictionary."""
        return {
            "horse_name": strategy.horse_name,
            "total_stake": strategy.total_stake,
            "win_stake": strategy.win_stake,
            "place_stake": strategy.place_stake,
            "expected_value": strategy.expected_value,
            "risk_rating": strategy.risk_rating,
        }

    def _convert_betting_opportunity_to_dict(self, opportunity) -> Dict:
        """Convert BettingOpportunity to dictionary."""
        return {
            "horse_name": opportunity.horse_name,
            "odds": opportunity.odds,
            "value": opportunity.value,
            "recommended_stake": opportunity.recommended_stake,
            "risk_rating": opportunity.risk_rating,
        }

    def _calculate_strategy_scores(self, recommendations: Dict) -> Dict[str, float]:
        """Calculate effectiveness scores for each strategy type."""
        scores = {}

        # Value betting score
        value_bets = recommendations.get("value_bets", [])
        if value_bets:
            avg_value = np.mean([bet.get("value", 0) for bet in value_bets])
            scores["value_betting"] = min(1.0, avg_value * 2)  # Scale to 0-1

        # 20/80 strategy score
        te_strategies = recommendations.get("twenty_eighty_strategies", [])
        if te_strategies:
            avg_ev = np.mean(
                [strategy.get("expected_value", 0) for strategy in te_strategies]
            )
            scores["twenty_eighty"] = min(1.0, max(0, avg_ev / 10))  # Scale to 0-1

        # Each-way score
        ew_opportunities = recommendations.get("each_way_opportunities", [])
        scores["each_way"] = len(ew_opportunities) / 10  # Simple count-based score

        return scores

    def _extract_strategy_stake(self, strategy: Dict) -> float:
        """Extract stake amount from strategy."""
        if "recommended_stake" in strategy:
            return strategy["recommended_stake"]
        elif "total_stake" in strategy:
            return strategy["total_stake"]
        elif "allocated_amount" in strategy:
            return strategy["allocated_amount"]
        else:
            return 10.0  # Default stake

    def _apply_kelly_scaling(self, strategy: Dict, original_stake: float) -> float:
        """Apply Kelly criterion scaling to stake."""
        # Simplified Kelly scaling
        confidence = strategy.get("confidence_score", 0.8)
        value = strategy.get("value", 0.1)

        kelly_multiplier = min(1.0, confidence * value * 2)
        return original_stake * kelly_multiplier

    def _assess_portfolio_risk_level(self, total_stake: float, bankroll: float) -> str:
        """Assess overall portfolio risk level."""
        risk_percentage = (total_stake / bankroll) * 100

        if risk_percentage > 15:
            return "HIGH"
        elif risk_percentage > 8:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_portfolio_risk_metrics(
        self, filtered_strategies: Dict
    ) -> Dict[str, float]:
        """Calculate portfolio-level risk metrics."""
        total_strategies = sum(
            len(strategies) for strategies in filtered_strategies.values()
        )

        return {
            "strategy_diversification": min(1.0, len(filtered_strategies) / 4),
            "total_positions": total_strategies,
            "concentration_risk": 1.0 / max(1, total_strategies),  # Lower is better
        }

    def _calculate_expected_portfolio_roi(
        self, selected_strategies: List[Dict]
    ) -> float:
        """Calculate expected ROI for portfolio."""
        if not selected_strategies:
            return 0.0

        total_expected_return = 0
        total_stake = 0

        for strategy in selected_strategies:
            stake = strategy.get("allocated_stake", 0)
            expected_multiplier = self._get_strategy_expected_multiplier(strategy)

            total_expected_return += stake * expected_multiplier
            total_stake += stake

        return (
            (total_expected_return - total_stake) / total_stake
            if total_stake > 0
            else 0
        )

    def _calculate_portfolio_risk_score(self, selected_strategies: List[Dict]) -> float:
        """Calculate portfolio risk score (0-1, lower is safer)."""
        if not selected_strategies:
            return 0.0

        risk_scores = []
        for strategy in selected_strategies:
            strategy_risk = self._assess_strategy_risk(strategy)
            if strategy_risk == "LOW":
                risk_scores.append(0.2)
            elif strategy_risk == "MEDIUM":
                risk_scores.append(0.5)
            else:
                risk_scores.append(0.8)

        return np.mean(risk_scores)

    def _get_strategy_expected_multiplier(self, strategy: Dict) -> float:
        """Get expected return multiplier for strategy."""
        strategy_type = strategy.get("type", "unknown")

        multipliers = {
            "arbitrage": 1.05,  # 5% guaranteed return
            "value_betting": 1.15,  # 15% expected return
            "twenty_eighty": 1.10,  # 10% expected return
            "each_way": 1.08,  # 8% expected return
        }

        return multipliers.get(strategy_type, 1.0)

    def _assess_strategy_risk(self, strategy: Dict) -> str:
        """Assess risk level of individual strategy."""
        strategy_data = strategy.get("strategy", {})

        if "risk_rating" in strategy_data:
            return strategy_data["risk_rating"]

        # Default assessment
        strategy_type = strategy.get("type", "unknown")
        if strategy_type == "arbitrage":
            return "LOW"
        elif strategy_type in ["value_betting", "twenty_eighty"]:
            return "MEDIUM"
        else:
            return "HIGH"

    def _get_strategy_confidence(self, strategy: Dict) -> float:
        """Get confidence score for strategy."""
        strategy_data = strategy.get("strategy", {})
        return strategy_data.get(
            "confidence", strategy_data.get("confidence_score", 0.8)
        )

    def _generate_performance_projections(
        self, strategy_allocations: List[Dict]
    ) -> Dict[str, float]:
        """Generate performance projections."""
        total_allocation = sum(s["allocated_amount"] for s in strategy_allocations)
        total_expected_return = sum(s["expected_return"] for s in strategy_allocations)

        return {
            "total_stake": total_allocation,
            "expected_gross_return": total_expected_return,
            "expected_net_profit": total_expected_return - total_allocation,
            "expected_roi_percentage": (
                ((total_expected_return - total_allocation) / total_allocation * 100)
                if total_allocation > 0
                else 0
            ),
            "break_even_win_rate": (
                (total_allocation / total_expected_return)
                if total_expected_return > 0
                else 1.0
            ),
        }


async def main():
    """Main function for testing the betting integration system."""
    # Initialize system
    betting_system = BettingIntegrationSystem()

    # Sample race data for testing
    race_data = {
        "race_id": "test_race_001",
        "race_time": "14:30",
        "track": "Cheltenham",
        "race_type": "Handicap",
        "distance": "2m4f",
    }

    # Sample horses data
    horses_data = [
        {
            "horse_name": "Thunder Bay",
            "odds": 3.5,
            "prediction": {
                "win_probability": 0.35,
                "place_probability": 0.65,
                "consensus_rating": 0.75,
                "confidence": 0.8,
            },
            "win_odds": 3.5,
            "place_odds": 1.8,
        },
        {
            "horse_name": "Silver Star",
            "odds": 5.0,
            "prediction": {
                "win_probability": 0.25,
                "place_probability": 0.55,
                "consensus_rating": 0.65,
                "confidence": 0.7,
            },
            "win_odds": 5.0,
            "place_odds": 2.2,
        },
        {
            "horse_name": "Golden Arrow",
            "odds": 2.8,
            "prediction": {
                "win_probability": 0.42,
                "place_probability": 0.70,
                "consensus_rating": 0.82,
                "confidence": 0.85,
            },
            "win_odds": 2.8,
            "place_odds": 1.6,
        },
    ]

    # Run betting integration
    results = await betting_system.run_automated_betting_integration(
        race_data, horses_data
    )

    print("\n=== BETTING INTEGRATION RESULTS ===")
    print(f"Race ID: {results.get('race_id', 'Unknown')}")
    print(f"Timestamp: {results.get('timestamp', 'Unknown')}")

    # Print strategy recommendations
    strategy_recs = results.get("strategy_recommendations", {})
    print(f"\nValue Bets Found: {len(strategy_recs.get('value_bets', []))}")
    print(f"20/80 Strategies: {len(strategy_recs.get('twenty_eighty_strategies', []))}")
    print(f"Arbitrage Opportunities: {len(results.get('arbitrage_opportunities', []))}")

    # Print execution results
    execution = results.get("execution_results", {})
    print(
        f"\nExecution Status: {execution.get('execution_summary', {}).get('status', 'Unknown')}"
    )
    print(f"Bets Placed: {len(execution.get('placed_bets', []))}")
    print(
        f"Total Stake: £{execution.get('execution_summary', {}).get('total_stake_placed', 0):.2f}"
    )

    print("\n=== INTEGRATION COMPLETE ===")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Run the main function
    asyncio.run(main())
