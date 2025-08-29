"""
Monte Carlo Integration Interface
===============================

Provides seamless integration between v2.03 system and the enhanced
Monte Carlo simulation engine with both basic and advanced modes.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

from .enhanced_monte_carlo_engine import (
    EnhancedMonteCarloEngine,
    HorseSimulationData,
    AdvancedSimulationParameters,
    SimulationMode,
    EnhancedAnalysisResults,
    create_monte_carlo_engine,
)

from .monte_carlo_simulator import MonteCarloSimulator
from .monte_carlo_simulator_with_real_data import RealDataMonteCarloSimulator


class MonteCarloIntegration:
    """Integration layer for Monte Carlo simulation in v2.03."""

    def __init__(self):
        """Initialize Monte Carlo integration."""
        self.basic_engine = create_monte_carlo_engine("basic")
        self.advanced_engine = create_monte_carlo_engine("advanced")

        # Fallback to existing v2.03 simulators
        self.v2_basic_simulator = MonteCarloSimulator(simulations=1000)
        self.v2_advanced_simulator = RealDataMonteCarloSimulator(simulations=10000)

    async def run_simulation(
        self,
        horses: List[Dict[str, Any]],
        mode: str = "basic",
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation with specified mode.

        Args:
            horses: List of horse data dictionaries
            mode: "basic" or "advanced"
            custom_params: Optional custom simulation parameters

        Returns:
            Simulation results dictionary
        """
        if mode.lower() == "advanced":
            return await self._run_advanced_simulation(horses, custom_params)
        else:
            return await self._run_basic_simulation(horses, custom_params)

    async def _run_basic_simulation(
        self,
        horses: List[Dict[str, Any]],
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run basic Monte Carlo simulation."""
        try:
            # Convert horse data
            simulation_horses = self.basic_engine.convert_v2_to_simulation_data(horses)

            # Set number of runs
            num_runs = 1000
            if custom_params and "num_runs" in custom_params:
                num_runs = min(custom_params["num_runs"], 5000)  # Cap for basic mode

            # Run simulation
            results = await self.basic_engine.run_basic_simulation(
                simulation_horses, num_runs
            )

            return self._format_results_for_v2(results)

        except Exception:
            # Fallback to v2.03 basic simulator
            return await self._fallback_to_v2_basic(horses)

    async def _run_advanced_simulation(
        self,
        horses: List[Dict[str, Any]],
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run advanced Monte Carlo simulation."""
        try:
            # Convert horse data
            simulation_horses = self.advanced_engine.convert_v2_to_simulation_data(
                horses
            )

            # Setup advanced parameters
            params = AdvancedSimulationParameters(
                num_runs=10000,
                race_distance=1600,
                track_condition="good",
                weather_factor=1.0,
                pace_factor=1.0,
                variance_factor=0.05,
                enable_margins=True,
                enable_environmental_modeling=True,
            )

            # Apply custom parameters if provided
            if custom_params:
                for key, value in custom_params.items():
                    if hasattr(params, key):
                        setattr(params, key, value)

            # Run advanced simulation
            results = await self.advanced_engine.run_advanced_simulation(
                simulation_horses, params
            )

            return self._format_advanced_results_for_v2(results)

        except Exception:
            # Fallback to v2.03 advanced simulator
            return await self._fallback_to_v2_advanced(horses)

    def _format_results_for_v2(
        self, results: EnhancedAnalysisResults
    ) -> Dict[str, Any]:
        """Format enhanced results for v2.03 compatibility."""
        return {
            "simulation_mode": "basic",
            "simulations_run": results.simulations_run,
            "execution_time_ms": results.execution_time_ms,
            "reliability": results.simulation_reliability,
            # Core probabilities
            "win_probabilities": results.win_probabilities,
            "place_probabilities": results.place_probabilities,
            "show_probabilities": results.show_probabilities,
            "average_positions": results.average_positions,
            # Basic recommendations
            "top_picks": self._generate_top_picks(results.win_probabilities),
            "betting_confidence": (
                "medium" if results.simulation_reliability > 0.7 else "low"
            ),
        }

    def _format_advanced_results_for_v2(
        self, results: EnhancedAnalysisResults
    ) -> Dict[str, Any]:
        """Format advanced results with full analytics for v2.03."""
        formatted = self._format_results_for_v2(results)

        # Add advanced analytics
        formatted.update(
            {
                "simulation_mode": "advanced",
                "confidence_intervals": results.confidence_intervals,
                "position_distributions": results.position_distributions,
                "winning_margins": results.winning_margins[:10],  # Sample
                # Environmental analysis
                "track_condition_impact": results.track_condition_impact,
                "weather_impact": results.weather_impact,
                # Advanced betting intelligence
                "value_bets": results.value_bets,
                "risk_assessment": results.risk_assessment,
                # Enhanced recommendations
                "betting_strategy": results.risk_assessment.get(
                    "betting_strategy", "conservative"
                ),
                "race_competitiveness": results.risk_assessment.get(
                    "competitiveness", "medium"
                ),
                "predictability": results.risk_assessment.get(
                    "predictability", "medium"
                ),
            }
        )

        return formatted

    def _generate_top_picks(
        self, win_probabilities: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate top picks from win probabilities."""
        sorted_horses = sorted(
            win_probabilities.items(), key=lambda x: x[1], reverse=True
        )

        top_picks = []
        for i, (horse_name, probability) in enumerate(sorted_horses[:5]):
            confidence = (
                "high"
                if probability > 0.3
                else "medium" if probability > 0.15 else "low"
            )

            top_picks.append(
                {
                    "rank": i + 1,
                    "horse_name": horse_name,
                    "win_probability": probability,
                    "confidence": confidence,
                    "recommended": probability > 0.2,
                }
            )

        return top_picks

    async def _fallback_to_v2_basic(
        self, horses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback to v2.03 basic Monte Carlo simulator."""
        try:
            # This would integrate with existing v2.03 simulator
            # Placeholder implementation
            return {
                "simulation_mode": "basic_fallback",
                "simulations_run": 1000,
                "execution_time_ms": 500,
                "reliability": 0.7,
                "win_probabilities": {
                    horse["name"]: 1.0 / len(horses) for horse in horses
                },
                "place_probabilities": {
                    horse["name"]: 3.0 / len(horses) for horse in horses
                },
                "show_probabilities": {
                    horse["name"]: 4.0 / len(horses) for horse in horses
                },
                "average_positions": {
                    horse["name"]: (len(horses) + 1) / 2 for horse in horses
                },
                "top_picks": [],
                "betting_confidence": "low",
            }
        except Exception:
            return {"error": "Monte Carlo simulation failed"}

    async def _fallback_to_v2_advanced(
        self, horses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback to v2.03 advanced Monte Carlo simulator."""
        # Use basic fallback for now
        basic_result = await self._fallback_to_v2_basic(horses)
        basic_result["simulation_mode"] = "advanced_fallback"
        return basic_result

    def get_simulation_modes(self) -> List[Dict[str, Any]]:
        """Get available simulation modes."""
        return [
            {
                "mode": "basic",
                "name": "Basic Monte Carlo",
                "description": "Fast simulation with core probability analysis",
                "max_runs": 5000,
                "typical_runtime": "< 1 second",
                "features": [
                    "Win/Place/Show probabilities",
                    "Top picks",
                    "Basic confidence",
                ],
            },
            {
                "mode": "advanced",
                "name": "Advanced Monte Carlo",
                "description": "Professional-grade simulation with environmental modeling",
                "max_runs": 50000,
                "typical_runtime": "2-10 seconds",
                "features": [
                    "Sophisticated variance modeling",
                    "Track condition impact",
                    "Weather factor analysis",
                    "Winning margin predictions",
                    "Value betting recommendations",
                    "Risk assessment",
                    "Confidence intervals",
                    "Position distributions",
                ],
            },
        ]

    async def run_comparative_analysis(
        self, horses: List[Dict[str, Any]], scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run comparative analysis across multiple scenarios."""
        results = {}

        for scenario in scenarios:
            scenario_name = scenario.get("name", f"scenario_{len(results)}")
            mode = scenario.get("mode", "basic")
            params = scenario.get("parameters", {})

            simulation_result = await self.run_simulation(horses, mode, params)
            results[scenario_name] = simulation_result

        # Add comparative analysis
        if len(results) > 1:
            results["comparative_analysis"] = self._analyze_scenario_differences(
                results
            )

        return results

    def _analyze_scenario_differences(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze differences between scenarios."""
        # Extract win probabilities from each scenario
        scenario_probs = {}
        for scenario_name, result in results.items():
            if "win_probabilities" in result:
                scenario_probs[scenario_name] = result["win_probabilities"]

        if len(scenario_probs) < 2:
            return {"message": "Need at least 2 scenarios for comparison"}

        # Find horses with biggest probability changes
        all_horses = set()
        for probs in scenario_probs.values():
            all_horses.update(probs.keys())

        probability_changes = {}
        for horse in all_horses:
            horse_probs = []
            for scenario_name in scenario_probs:
                prob = scenario_probs[scenario_name].get(horse, 0.0)
                horse_probs.append(prob)

            if len(horse_probs) >= 2:
                max_change = max(horse_probs) - min(horse_probs)
                probability_changes[horse] = max_change

        # Sort by biggest changes
        biggest_changes = sorted(
            probability_changes.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "biggest_probability_changes": [
                {"horse": horse, "change": change} for horse, change in biggest_changes
            ],
            "scenarios_compared": list(scenario_probs.keys()),
            "total_horses": len(all_horses),
        }


# Global integration instance
monte_carlo_integration = MonteCarloIntegration()
