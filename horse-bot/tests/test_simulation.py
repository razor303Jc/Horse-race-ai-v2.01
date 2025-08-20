"""
Unit tests for the race simulation module.
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from src.simulation.monte_carlo import (
    RaceSimulator, 
    HorseSimulationData, 
    SimulationParameters,
    SimulationResult,
    AggregatedResults
)


class TestRaceSimulator:
    """Test cases for RaceSimulator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simulator = RaceSimulator()
    
    def test_calculate_base_time(self, sample_horse_data, sample_simulation_params):
        """Test base time calculation for horses."""
        horse = sample_horse_data[0]
        params = sample_simulation_params
        
        base_time = self.simulator._calculate_base_time(horse, params)
        
        assert isinstance(base_time, float)
        assert base_time > 0
        assert 50 < base_time < 200  # Reasonable range for race times
    
    def test_get_condition_factor(self):
        """Test track condition factor calculation."""
        # Test known conditions
        assert self.simulator._get_condition_factor("firm") == 0.98
        assert self.simulator._get_condition_factor("good") == 1.00
        assert self.simulator._get_condition_factor("soft") == 1.05
        assert self.simulator._get_condition_factor("heavy") == 1.10
        
        # Test unknown condition defaults to 1.00
        assert self.simulator._get_condition_factor("unknown") == 1.00
    
    def test_simulate_single_race(self, sample_horse_data, sample_simulation_params):
        """Test single race simulation."""
        result = self.simulator.simulate_single_race(sample_horse_data, sample_simulation_params)
        
        assert isinstance(result, SimulationResult)
        assert len(result.positions) == len(sample_horse_data)
        assert len(result.times) == len(sample_horse_data)
        assert len(result.margins) == len(sample_horse_data)
        
        # Check positions are valid (1 to num_horses)
        positions = result.positions
        assert set(positions) == set(range(1, len(sample_horse_data) + 1))
        
        # Check times are positive
        assert all(time > 0 for time in result.times)
        
        # Check margins are non-negative
        assert all(margin >= 0 for margin in result.margins)
    
    def test_monte_carlo_simulation(self, sample_horse_data, sample_simulation_params):
        """Test Monte Carlo simulation with multiple runs."""
        # Use fewer runs for faster testing
        sample_simulation_params.num_runs = 50
        
        result = self.simulator.run_monte_carlo_simulation(
            sample_horse_data, 
            sample_simulation_params
        )
        
        assert isinstance(result, AggregatedResults)
        assert len(result.horse_results) == len(sample_horse_data)
        assert len(result.position_distributions) == len(sample_horse_data)
        assert result.execution_time_ms > 0
        
        # Check each horse has complete results
        for horse in sample_horse_data:
            horse_id = horse.horse_id
            assert horse_id in result.horse_results
            
            horse_result = result.horse_results[horse_id]
            assert "win_percentage" in horse_result
            assert "place_percentage" in horse_result
            assert "show_percentage" in horse_result
            assert "average_position" in horse_result
            assert "average_time" in horse_result
            
            # Check percentages are valid
            assert 0 <= horse_result["win_percentage"] <= 100
            assert 0 <= horse_result["place_percentage"] <= 100
            assert 0 <= horse_result["show_percentage"] <= 100
            
            # Check logical ordering of percentages
            assert horse_result["win_percentage"] <= horse_result["place_percentage"]
            assert horse_result["place_percentage"] <= horse_result["show_percentage"]
    
    def test_scenario_simulation(self, sample_horse_data):
        """Test scenario-based simulation."""
        scenarios = [
            {
                "name": "good_conditions",
                "parameters": {
                    "num_runs": 20,
                    "track_condition": "good",
                    "weather_factor": 1.0
                }
            },
            {
                "name": "heavy_conditions",
                "parameters": {
                    "num_runs": 20,
                    "track_condition": "heavy",
                    "weather_factor": 1.1
                }
            }
        ]
        
        results = self.simulator.run_scenario_simulation(sample_horse_data, scenarios)
        
        assert len(results) == 2
        assert "good_conditions" in results
        assert "heavy_conditions" in results
        
        for scenario_name, scenario_result in results.items():
            assert isinstance(scenario_result, AggregatedResults)
            assert len(scenario_result.horse_results) == len(sample_horse_data)
    
    def test_simulation_with_random_seed(self, sample_horse_data):
        """Test that random seed produces reproducible results."""
        params1 = SimulationParameters(num_runs=10, random_seed=42)
        params2 = SimulationParameters(num_runs=10, random_seed=42)
        
        result1 = self.simulator.run_monte_carlo_simulation(sample_horse_data, params1)
        
        # Create new simulator instance to ensure clean state
        simulator2 = RaceSimulator()
        result2 = simulator2.run_monte_carlo_simulation(sample_horse_data, params2)
        
        # Results should be identical with same seed
        for horse in sample_horse_data:
            horse_id = horse.horse_id
            assert result1.horse_results[horse_id]["win_percentage"] == \
                   result2.horse_results[horse_id]["win_percentage"]
    
    @pytest.mark.slow
    def test_large_simulation(self, sample_horse_data):
        """Test simulation with large number of runs."""
        params = SimulationParameters(num_runs=10000, random_seed=42)
        
        result = self.simulator.run_monte_carlo_simulation(sample_horse_data, params)
        
        # With large number of runs, results should be more stable
        total_win_percentage = sum(
            horse_result["win_percentage"] 
            for horse_result in result.horse_results.values()
        )
        
        # Total win percentage should be close to 100%
        assert 99.0 <= total_win_percentage <= 101.0
    
    def test_simulation_parameters_validation(self, sample_horse_data):
        """Test simulation with various parameter combinations."""
        # Test different track conditions
        for condition in ["firm", "good", "soft", "heavy"]:
            params = SimulationParameters(
                num_runs=10,
                track_condition=condition,
                random_seed=42
            )
            result = self.simulator.run_monte_carlo_simulation(sample_horse_data, params)
            assert len(result.horse_results) == len(sample_horse_data)
        
        # Test different weather factors
        for weather_factor in [0.8, 1.0, 1.2]:
            params = SimulationParameters(
                num_runs=10,
                weather_factor=weather_factor,
                random_seed=42
            )
            result = self.simulator.run_monte_carlo_simulation(sample_horse_data, params)
            assert len(result.horse_results) == len(sample_horse_data)
    
    def test_empty_horse_list(self):
        """Test simulation with empty horse list."""
        empty_horses = []
        params = SimulationParameters(num_runs=10)
        
        result = self.simulator.run_monte_carlo_simulation(empty_horses, params)
        
        assert len(result.horse_results) == 0
        assert len(result.position_distributions) == 0
        assert len(result.average_winning_margins) == 0
    
    def test_single_horse_simulation(self):
        """Test simulation with single horse."""
        single_horse = [
            HorseSimulationData(
                horse_id=1,
                name="Solo Runner",
                win_probability=1.0,
                place_probability=1.0,
                show_probability=1.0,
                speed_rating=95.0,
                form_rating=90.0,
                weight_carried=58.0,
                jockey_skill=90.0,
                trainer_skill=85.0
            )
        ]
        
        params = SimulationParameters(num_runs=10, random_seed=42)
        result = self.simulator.run_monte_carlo_simulation(single_horse, params)
        
        # Single horse should always win
        horse_result = result.horse_results[1]
        assert horse_result["win_percentage"] == 100.0
        assert horse_result["average_position"] == 1.0
