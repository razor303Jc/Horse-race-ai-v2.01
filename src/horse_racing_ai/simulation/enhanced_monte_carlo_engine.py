"""
Enhanced Monte Carlo Simulation Engine
====================================

Integrates the sophisticated horse-bot Monte Carlo engine with v2.03 system.
Provides both Basic and Advanced simulation modes with professional-grade
variance modeling, environmental factors, and statistical rigor.
"""

import numpy as np
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SimulationMode(Enum):
    """Simulation complexity levels."""

    BASIC = "basic"
    ADVANCED = "advanced"


@dataclass
class HorseSimulationData:
    """Advanced horse simulation parameters from horse-bot engine."""

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
    odds: Optional[float] = None
    recent_form: Optional[List[int]] = None


@dataclass
class AdvancedSimulationParameters:
    """Advanced simulation parameters with environmental factors."""

    num_runs: int = 10000
    race_distance: int = 1600  # meters
    track_condition: str = "good"
    weather_factor: float = 1.0
    pace_factor: float = 1.0
    field_size_factor: float = 1.0
    class_level: str = "standard"  # maiden, claiming, allowance, stakes
    random_seed: Optional[int] = None
    variance_factor: float = 0.05  # 5% base variance
    enable_margins: bool = True
    enable_environmental_modeling: bool = True


@dataclass
class AdvancedSimulationResult:
    """Result of a single advanced simulation run."""

    positions: List[int]  # Final positions for each horse
    times: List[float]  # Race times for each horse
    margins: List[float]  # Winning margins
    weather_impact: float  # Weather impact factor
    track_impact: float  # Track condition impact


@dataclass
class EnhancedAnalysisResults:
    """Enhanced analysis results with confidence intervals and betting."""

    race_id: str
    simulation_mode: SimulationMode
    simulations_run: int
    execution_time_ms: int

    # Core probabilities
    win_probabilities: Dict[str, float]
    place_probabilities: Dict[str, float]
    show_probabilities: Dict[str, float]

    # Advanced statistics
    average_positions: Dict[str, float]
    position_distributions: Dict[str, List[float]]
    confidence_intervals: Dict[str, Tuple[float, float]]
    winning_margins: List[float]

    # Environmental analysis
    track_condition_impact: Dict[str, float]
    weather_impact: Dict[str, float]

    # Betting intelligence
    value_bets: List[Dict[str, Any]]
    risk_assessment: Dict[str, str]
    simulation_reliability: float


class EnhancedMonteCarloEngine:
    """Enhanced Monte Carlo simulation engine with basic and advanced modes."""

    def __init__(self, mode: SimulationMode = SimulationMode.BASIC):
        """Initialize the enhanced Monte Carlo engine."""
        self.mode = mode
        self.rng = np.random.default_rng()
        logger.info(f"🎯 Enhanced Monte Carlo Engine initialized in {mode.value} mode")

    def convert_v2_to_simulation_data(
        self, horses: List[Dict[str, Any]]
    ) -> List[HorseSimulationData]:
        """Convert v2.03 horse data to simulation format."""
        simulation_horses = []

        for i, horse in enumerate(horses):
            # Extract or estimate required fields
            horse_data = HorseSimulationData(
                horse_id=i,
                name=horse.get("name", f"Horse_{i}"),
                win_probability=horse.get("win_probability", 1.0 / len(horses)),
                place_probability=horse.get("place_probability", 3.0 / len(horses)),
                show_probability=horse.get("show_probability", 4.0 / len(horses)),
                speed_rating=horse.get("speed_rating", 75.0),
                form_rating=horse.get("form_rating", 75.0),
                weight_carried=horse.get("weight_carried", 60.0),
                jockey_skill=horse.get("jockey_skill", 75.0),
                trainer_skill=horse.get("trainer_skill", 75.0),
                odds=horse.get("odds"),
                recent_form=horse.get("recent_form", []),
            )
            simulation_horses.append(horse_data)

        return simulation_horses

    async def run_basic_simulation(
        self, horses: List[HorseSimulationData], num_runs: int = 1000
    ) -> EnhancedAnalysisResults:
        """Run basic Monte Carlo simulation (simplified, faster)."""
        start_time = time.time()

        logger.info(f"🎯 Running BASIC Monte Carlo simulation ({num_runs} runs)")

        # Initialize tracking
        win_counts = {horse.name: 0 for horse in horses}
        place_counts = {horse.name: 0 for horse in horses}
        show_counts = {horse.name: 0 for horse in horses}
        position_sums = {horse.name: 0 for horse in horses}

        # Run basic simulations
        for run in range(num_runs):
            # Simple probability-based simulation
            positions = self._simulate_basic_race(horses)

            # Record results
            for i, horse in enumerate(horses):
                position = positions[i]
                position_sums[horse.name] += position

                if position == 1:
                    win_counts[horse.name] += 1
                if position <= 3:
                    place_counts[horse.name] += 1
                if position <= 4:
                    show_counts[horse.name] += 1

        # Calculate probabilities
        win_probabilities = {
            name: count / num_runs for name, count in win_counts.items()
        }
        place_probabilities = {
            name: count / num_runs for name, count in place_counts.items()
        }
        show_probabilities = {
            name: count / num_runs for name, count in show_counts.items()
        }
        average_positions = {
            name: pos_sum / num_runs for name, pos_sum in position_sums.items()
        }

        execution_time = int((time.time() - start_time) * 1000)

        return EnhancedAnalysisResults(
            race_id="BASIC_SIMULATION",
            simulation_mode=SimulationMode.BASIC,
            simulations_run=num_runs,
            execution_time_ms=execution_time,
            win_probabilities=win_probabilities,
            place_probabilities=place_probabilities,
            show_probabilities=show_probabilities,
            average_positions=average_positions,
            position_distributions={},
            confidence_intervals={},
            winning_margins=[],
            track_condition_impact={},
            weather_impact={},
            value_bets=[],
            risk_assessment={},
            simulation_reliability=0.7,
        )

    async def run_advanced_simulation(
        self, horses: List[HorseSimulationData], params: AdvancedSimulationParameters
    ) -> EnhancedAnalysisResults:
        """Run advanced Monte Carlo simulation with environmental modeling."""
        start_time = time.time()

        logger.info(
            f"🎯 Running ADVANCED Monte Carlo simulation ({params.num_runs} runs)"
        )

        if params.random_seed:
            self.rng = np.random.default_rng(params.random_seed)

        # Initialize advanced tracking
        win_counts = {horse.name: 0 for horse in horses}
        place_counts = {horse.name: 0 for horse in horses}
        show_counts = {horse.name: 0 for horse in horses}
        position_sums = {horse.name: 0 for horse in horses}
        performance_records = {horse.name: [] for horse in horses}
        all_margins = []
        track_impacts = []
        weather_impacts = []

        # Run advanced simulations
        for run in range(params.num_runs):
            if run % 1000 == 0:
                logger.debug(f"Advanced simulation {run}/{params.num_runs}")

            # Run sophisticated simulation
            result = self._simulate_advanced_race(horses, params)

            # Record detailed results
            for i, horse in enumerate(horses):
                position = result.positions[i]
                performance = result.times[i]

                position_sums[horse.name] += position
                performance_records[horse.name].append(performance)

                if position == 1:
                    win_counts[horse.name] += 1
                if position <= 3:
                    place_counts[horse.name] += 1
                if position <= 4:
                    show_counts[horse.name] += 1

            all_margins.extend(result.margins)
            track_impacts.append(result.track_impact)
            weather_impacts.append(result.weather_impact)

        # Calculate advanced statistics
        num_runs = params.num_runs
        win_probabilities = {
            name: count / num_runs for name, count in win_counts.items()
        }
        place_probabilities = {
            name: count / num_runs for name, count in place_counts.items()
        }
        show_probabilities = {
            name: count / num_runs for name, count in show_counts.items()
        }
        average_positions = {
            name: pos_sum / num_runs for name, pos_sum in position_sums.items()
        }

        # Calculate confidence intervals
        confidence_intervals = {}
        for name, performances in performance_records.items():
            if performances:
                ci_lower = float(np.percentile(performances, 2.5))
                ci_upper = float(np.percentile(performances, 97.5))
                confidence_intervals[name] = (ci_lower, ci_upper)
            else:
                confidence_intervals[name] = (0.0, 0.0)

        # Environmental impact analysis
        track_condition_impact = {
            horse.name: np.mean(track_impacts) for horse in horses
        }
        weather_impact = {horse.name: np.mean(weather_impacts) for horse in horses}

        # Generate value bets
        value_bets = self._generate_value_bets(horses, win_probabilities)

        # Calculate reliability
        reliability = self._calculate_advanced_reliability(
            performance_records, params.num_runs
        )

        execution_time = int((time.time() - start_time) * 1000)

        return EnhancedAnalysisResults(
            race_id="ADVANCED_SIMULATION",
            simulation_mode=SimulationMode.ADVANCED,
            simulations_run=params.num_runs,
            execution_time_ms=execution_time,
            win_probabilities=win_probabilities,
            place_probabilities=place_probabilities,
            show_probabilities=show_probabilities,
            average_positions=average_positions,
            position_distributions=performance_records,
            confidence_intervals=confidence_intervals,
            winning_margins=all_margins[:100],  # Sample of margins
            track_condition_impact=track_condition_impact,
            weather_impact=weather_impact,
            value_bets=value_bets,
            risk_assessment=self._assess_race_risk(horses, win_probabilities),
            simulation_reliability=reliability,
        )

    def _simulate_basic_race(self, horses: List[HorseSimulationData]) -> List[int]:
        """Simulate a basic race using simple probability weighting."""
        # Create weighted random selection based on win probabilities
        weights = [horse.win_probability for horse in horses]

        # Add some randomness
        random_factors = self.rng.normal(1.0, 0.1, len(horses))
        adjusted_weights = [w * r for w, r in zip(weights, random_factors)]

        # Sort by adjusted weights (highest first)
        horse_indices = list(range(len(horses)))
        horse_indices.sort(key=lambda i: adjusted_weights[i], reverse=True)

        # Assign positions
        positions = [0] * len(horses)
        for pos, horse_idx in enumerate(horse_indices):
            positions[horse_idx] = pos + 1

        return positions

    def _simulate_advanced_race(
        self, horses: List[HorseSimulationData], params: AdvancedSimulationParameters
    ) -> AdvancedSimulationResult:
        """Simulate an advanced race with environmental modeling."""
        num_horses = len(horses)

        # Calculate base times using horse-bot sophisticated modeling
        base_times = []
        for horse in horses:
            base_time = self._calculate_sophisticated_base_time(horse, params)
            base_times.append(base_time)

        # Apply variance factors
        random_factors = self.rng.normal(1.0, params.variance_factor, num_horses)

        # Environmental factors
        track_factor = self._get_track_condition_factor(params.track_condition)
        weather_factor = params.weather_factor
        pace_factor = params.pace_factor

        # Calculate final times with all factors
        final_times = []
        for i, (base_time, random_factor) in enumerate(zip(base_times, random_factors)):
            # Apply all environmental factors
            adjusted_time = (
                base_time * random_factor * track_factor * weather_factor * pace_factor
            )
            final_times.append(adjusted_time)

        # Determine positions (faster time = better position)
        time_indices = list(enumerate(final_times))
        time_indices.sort(key=lambda x: x[1])

        positions = [0] * num_horses
        for position, (horse_index, _) in enumerate(time_indices):
            positions[horse_index] = position + 1

        # Calculate winning margins
        sorted_times = [time for _, time in time_indices]
        margins = []
        for i in range(len(sorted_times) - 1):
            margin = sorted_times[i + 1] - sorted_times[i]
            margins.append(margin)
        margins.append(0.0)  # Last horse has no margin

        return AdvancedSimulationResult(
            positions=positions,
            times=final_times,
            margins=margins,
            weather_impact=weather_factor,
            track_impact=track_factor,
        )

    def _calculate_sophisticated_base_time(
        self, horse: HorseSimulationData, params: AdvancedSimulationParameters
    ) -> float:
        """Calculate sophisticated base time using horse-bot model."""
        # Distance scaling
        distance_factor = params.race_distance / 1600  # Normalize to 1600m

        # Core horse factors
        speed_factor = horse.speed_rating / 100
        form_factor = horse.form_rating / 100
        weight_factor = 1 + ((horse.weight_carried - 60) * 0.002)  # 2kg per lb penalty
        jockey_factor = horse.jockey_skill / 100
        trainer_factor = horse.trainer_skill / 100

        # Recent form adjustment
        form_trend = self._calculate_form_trend(horse.recent_form or [])

        # Base time for average horse at 1600m
        base_time = 100.0  # seconds

        # Sophisticated time calculation
        adjusted_time = (
            base_time
            * distance_factor
            / speed_factor
            / form_factor
            * weight_factor
            / jockey_factor
            / trainer_factor
            * (1 - form_trend * 0.02)
        )

        return max(80.0, adjusted_time)  # Minimum reasonable time

    def _get_track_condition_factor(self, track_condition: str) -> float:
        """Get track condition factor using horse-bot model."""
        condition_factors = {
            "firm": 0.98,
            "good": 1.00,
            "good_to_soft": 1.02,
            "soft": 1.05,
            "heavy": 1.10,
            "very_soft": 1.15,
        }
        return condition_factors.get(track_condition.lower(), 1.00)

    def _calculate_form_trend(self, recent_positions: List[int]) -> float:
        """Calculate form trend from recent positions."""
        if not recent_positions or len(recent_positions) < 2:
            return 0.0

        # Simple trend calculation (improvement = positive, decline = negative)
        recent_3 = recent_positions[:3]
        if len(recent_3) >= 2:
            trend = (recent_3[-1] - recent_3[0]) / len(recent_3)
            return max(-1.0, min(1.0, -trend * 0.1))  # Invert (lower position = better)

        return 0.0

    def _generate_value_bets(
        self, horses: List[HorseSimulationData], win_probabilities: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate value betting recommendations."""
        value_bets = []

        for horse in horses:
            win_prob = win_probabilities.get(horse.name, 0.0)

            if horse.odds and win_prob > 0.15:  # Minimum 15% chance
                implied_prob = 1.0 / horse.odds if horse.odds > 1.0 else 0.01
                edge = win_prob - implied_prob

                if edge > 0.05:  # 5% minimum edge
                    value_bet = {
                        "horse_name": horse.name,
                        "win_probability": win_prob,
                        "odds": horse.odds,
                        "implied_probability": implied_prob,
                        "edge": edge,
                        "confidence": "high" if edge > 0.15 else "medium",
                        "recommended_stake": min(edge * 10, 5.0),  # Kelly-like sizing
                    }
                    value_bets.append(value_bet)

        return sorted(value_bets, key=lambda x: x["edge"], reverse=True)

    def _assess_race_risk(
        self, horses: List[HorseSimulationData], win_probabilities: Dict[str, float]
    ) -> Dict[str, str]:
        """Assess overall race risk characteristics."""
        probs = list(win_probabilities.values())

        # Calculate probability distribution metrics
        max_prob = max(probs)
        entropy = -sum(p * np.log(p) for p in probs if p > 0)

        if max_prob > 0.6:
            competitiveness = "low"
        elif max_prob < 0.3:
            competitiveness = "high"
        else:
            competitiveness = "medium"

        if entropy > 2.0:
            predictability = "low"
        elif entropy < 1.5:
            predictability = "high"
        else:
            predictability = "medium"

        return {
            "competitiveness": competitiveness,
            "predictability": predictability,
            "field_strength": "strong" if len(horses) >= 12 else "moderate",
            "betting_strategy": (
                "value" if competitiveness == "high" else "conservative"
            ),
        }

    def _calculate_advanced_reliability(
        self, performance_records: Dict[str, List[float]], num_runs: int
    ) -> float:
        """Calculate simulation reliability score."""
        if num_runs < 1000:
            return 0.6
        elif num_runs < 5000:
            return 0.8
        else:
            return 0.95


# Factory function for easy integration
def create_monte_carlo_engine(mode: str = "basic") -> EnhancedMonteCarloEngine:
    """Create Monte Carlo engine with specified mode."""
    simulation_mode = (
        SimulationMode.ADVANCED if mode.lower() == "advanced" else SimulationMode.BASIC
    )
    return EnhancedMonteCarloEngine(simulation_mode)


# Global instances for easy access
basic_engine = EnhancedMonteCarloEngine(SimulationMode.BASIC)
advanced_engine = EnhancedMonteCarloEngine(SimulationMode.ADVANCED)
