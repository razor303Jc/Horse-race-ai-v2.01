"""
Race simulation engine for Monte Carlo simulations and scenario modeling.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import time

from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HorseSimulationData:
    """Data structure for horse simulation parameters."""
    horse_id: int
    name: str
    win_probability: float
    place_probability: float
    show_probability: float
    speed_rating: float
    form_rating: float
    weight_carried: float
    jockey_skill: float
    trainer_skill: float


@dataclass
class SimulationParameters:
    """Parameters for race simulation."""
    num_runs: int = 10000
    race_distance: int = 1600  # meters
    track_condition: str = "good"
    weather_factor: float = 1.0
    pace_factor: float = 1.0
    random_seed: Optional[int] = None


@dataclass
class SimulationResult:
    """Result of a single simulation run."""
    positions: List[int]  # Final positions for each horse
    times: List[float]    # Race times for each horse
    margins: List[float]  # Winning margins


@dataclass
class AggregatedResults:
    """Aggregated results from multiple simulation runs."""
    horse_results: Dict[int, Dict[str, float]]
    position_distributions: Dict[int, List[float]]
    average_winning_margins: List[float]
    execution_time_ms: int


class RaceSimulator:
    """Monte Carlo race simulation engine."""
    
    def __init__(self):
        self.rng = np.random.default_rng()
    
    def simulate_single_race(
        self, 
        horses: List[HorseSimulationData], 
        params: SimulationParameters
    ) -> SimulationResult:
        """
        Simulate a single race run.
        
        Args:
            horses: List of horses with simulation data
            params: Simulation parameters
            
        Returns:
            Result of the single simulation
        """
        num_horses = len(horses)
        
        # Calculate base times for each horse based on ratings
        base_times = []
        for horse in horses:
            # Base time calculation using speed rating and other factors
            base_time = self._calculate_base_time(horse, params)
            base_times.append(base_time)
        
        # Add random variance to simulate race unpredictability
        variance_factor = 0.05  # 5% variance
        random_factors = self.rng.normal(1.0, variance_factor, num_horses)
        
        # Apply track condition and weather effects
        condition_factor = self._get_condition_factor(params.track_condition)
        weather_factor = params.weather_factor
        
        # Calculate final times
        final_times = []
        for i, (base_time, random_factor) in enumerate(zip(base_times, random_factors)):
            final_time = base_time * random_factor * condition_factor * weather_factor
            final_times.append(final_time)
        
        # Determine positions based on times (faster time = better position)
        time_indices = list(enumerate(final_times))
        time_indices.sort(key=lambda x: x[1])  # Sort by time
        
        positions = [0] * num_horses
        for position, (horse_index, _) in enumerate(time_indices):
            positions[horse_index] = position + 1  # 1-based positions
        
        # Calculate winning margins
        sorted_times = [time for _, time in time_indices]
        margins = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times)-1)]
        margins.append(0.0)  # Last horse has no margin
        
        return SimulationResult(
            positions=positions,
            times=final_times,
            margins=margins
        )
    
    def run_monte_carlo_simulation(
        self,
        horses: List[HorseSimulationData],
        params: SimulationParameters
    ) -> AggregatedResults:
        """
        Run Monte Carlo simulation with multiple iterations.
        
        Args:
            horses: List of horses with simulation data
            params: Simulation parameters
            
        Returns:
            Aggregated simulation results
        """
        start_time = time.time()
        
        if params.random_seed:
            self.rng = np.random.default_rng(params.random_seed)
        
        num_horses = len(horses)
        all_positions = []
        all_times = []
        all_margins = []
        
        logger.info(f"Starting Monte Carlo simulation with {params.num_runs} runs")
        
        # Run simulations
        for run in range(params.num_runs):
            result = self.simulate_single_race(horses, params)
            all_positions.append(result.positions)
            all_times.append(result.times)
            all_margins.append(result.margins)
            
            # Log progress every 1000 runs
            if (run + 1) % 1000 == 0:
                logger.debug(f"Completed {run + 1}/{params.num_runs} simulation runs")
        
        # Aggregate results
        aggregated = self._aggregate_results(horses, all_positions, all_times, all_margins)
        
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        aggregated.execution_time_ms = execution_time_ms
        
        logger.info(f"Monte Carlo simulation completed in {execution_time_ms}ms")
        
        return aggregated
    
    def run_scenario_simulation(
        self,
        horses: List[HorseSimulationData],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, AggregatedResults]:
        """
        Run simulations for multiple scenarios.
        
        Args:
            horses: List of horses with simulation data
            scenarios: List of scenario parameters
            
        Returns:
            Results for each scenario
        """
        results = {}
        
        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get('name', f'scenario_{i}')
            params = SimulationParameters(**scenario.get('parameters', {}))
            
            logger.info(f"Running scenario simulation: {scenario_name}")
            scenario_results = self.run_monte_carlo_simulation(horses, params)
            results[scenario_name] = scenario_results
        
        return results
    
    def _calculate_base_time(
        self, 
        horse: HorseSimulationData, 
        params: SimulationParameters
    ) -> float:
        """Calculate base race time for a horse."""
        # Base time calculation logic
        # This is a simplified model - in reality would be much more complex
        
        distance_factor = params.race_distance / 1600  # Normalize to 1600m
        speed_factor = horse.speed_rating / 100  # Normalize speed rating
        form_factor = horse.form_rating / 100    # Normalize form rating
        weight_factor = 1 + ((horse.weight_carried - 60) * 0.002)  # Weight penalty
        jockey_factor = horse.jockey_skill / 100
        trainer_factor = horse.trainer_skill / 100
        
        # Base time for average horse at 1600m
        base_time = 100.0  # seconds
        
        # Apply factors
        adjusted_time = (
            base_time * distance_factor / speed_factor / form_factor * 
            weight_factor / jockey_factor / trainer_factor
        )
        
        return adjusted_time
    
    def _get_condition_factor(self, track_condition: str) -> float:
        """Get track condition factor."""
        condition_factors = {
            "firm": 0.98,
            "good": 1.00,
            "good_to_soft": 1.02,
            "soft": 1.05,
            "heavy": 1.10
        }
        return condition_factors.get(track_condition, 1.00)
    
    def _aggregate_results(
        self,
        horses: List[HorseSimulationData],
        all_positions: List[List[int]],
        all_times: List[List[float]],
        all_margins: List[List[float]]
    ) -> AggregatedResults:
        """Aggregate simulation results."""
        num_horses = len(horses)
        num_runs = len(all_positions)
        
        # Initialize results structure
        horse_results = {}
        position_distributions = {}
        
        for i, horse in enumerate(horses):
            horse_id = horse.horse_id
            
            # Count positions for this horse
            position_counts = [0] * num_horses
            for run_positions in all_positions:
                position = run_positions[i] - 1  # Convert to 0-based
                position_counts[position] += 1
            
            # Calculate percentages
            position_percentages = [count / num_runs * 100 for count in position_counts]
            
            horse_results[horse_id] = {
                "win_percentage": position_percentages[0],
                "place_percentage": sum(position_percentages[:2]),
                "show_percentage": sum(position_percentages[:3]),
                "average_position": np.mean([pos[i] for pos in all_positions]),
                "average_time": np.mean([times[i] for times in all_times])
            }
            
            position_distributions[horse_id] = position_percentages
        
        # Calculate average winning margins
        average_margins = []
        for margin_idx in range(num_horses - 1):
            margin_sum = sum(margins[margin_idx] for margins in all_margins)
            average_margins.append(margin_sum / num_runs)
        
        return AggregatedResults(
            horse_results=horse_results,
            position_distributions=position_distributions,
            average_winning_margins=average_margins,
            execution_time_ms=0  # Will be set by caller
        )


# Global simulator instance
race_simulator = RaceSimulator()
