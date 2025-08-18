#!/usr/bin/env python3
"""
🎲 Stage 10: Monte Carlo Simulations
Horse Racing AI v2.02 - Production Pipeline Stage

Purpose: Run comprehensive Monte Carlo simulations using Stage 9 speed analysis
Duration: 30 minutes
Dependencies: Stage 9 Speed Analysis, ML Model outputs
Output: Win/Place/Show probabilities, betting recommendations
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

try:
    from src.horse_racing_ai.scoring.composite_scorer import CompositeScorer
    from src.horse_racing_ai.simulation.monte_carlo_simulator import (
        MonteCarloAnalysis,
        MonteCarloSimulator,
        PerformanceProfile,
    )
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("📁 Running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Stage10MonteCarloEngine:
    """
    🎲 Stage 10: Monte Carlo Simulations Engine

    Integrates with Stage 9 speed analysis to generate comprehensive
    probabilistic race predictions using Monte Carlo methods.
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.data_dir = self.project_root / "data" / "daily_analysis"
        self.output_dir = self.project_root / "data" / "monte_carlo_results"
        self.output_dir.mkdir(exist_ok=True)

        # Monte Carlo configuration
        self.simulations_per_race = 5000
        self.confidence_threshold = 0.80
        self.value_bet_threshold = 0.15

        # Initialize simulator
        self.monte_carlo_simulator = MonteCarloSimulator(
            simulations=self.simulations_per_race, random_seed=42
        )

        logger.info("🎲 Stage 10 Monte Carlo Engine initialized")

    def run_monte_carlo_analysis(self) -> Dict[str, Any]:
        """
        🚀 Main execution method for Stage 10 Monte Carlo Simulations

        Returns comprehensive analysis results including:
        - Win/Place/Show probabilities for all horses
        - Betting recommendations with value analysis
        - Statistical confidence intervals
        - Race simulation summaries
        """
        start_time = time.time()
        logger.info("🎲 Starting Stage 10: Monte Carlo Simulations")

        results = {
            "stage": "stage10_monte_carlo",
            "start_time": datetime.now().isoformat(),
            "success": False,
            "races_processed": 0,
            "total_simulations": 0,
            "horses_analyzed": 0,
            "betting_opportunities": 0,
            "high_confidence_picks": 0,
            "race_analyses": [],
            "summary_stats": {},
            "performance_metrics": {},
            "errors": [],
        }

        try:
            # Load Stage 9 speed analysis results
            speed_analysis_data = self._load_stage9_results()
            if not speed_analysis_data:
                logger.error("❌ No Stage 9 speed analysis data found")
                results["errors"].append("Missing Stage 9 dependencies")
                return results

            logger.info(
                f"📊 Loaded speed analysis for {len(speed_analysis_data)} races"
            )

            # Process each race
            for race_index, race_data in enumerate(speed_analysis_data):
                try:
                    race_analysis = self._process_race_monte_carlo(
                        race_data, race_index
                    )

                    if race_analysis["success"]:
                        results["race_analyses"].append(race_analysis)
                        results["races_processed"] += 1
                        results["total_simulations"] += race_analysis["simulations_run"]
                        results["horses_analyzed"] += race_analysis["horses_analyzed"]

                        # Count betting opportunities
                        betting_count = len(race_analysis["betting_recommendations"])
                        results["betting_opportunities"] += betting_count

                        # Count high confidence picks
                        high_conf_picks = [
                            r
                            for r in race_analysis["betting_recommendations"]
                            if r.get("confidence", 0) > self.confidence_threshold
                        ]
                        results["high_confidence_picks"] += len(high_conf_picks)

                        sim_count = race_analysis["simulations_run"]
                        msg = f"✅ Race {race_index + 1}: {sim_count} simulations completed"
                        logger.info(msg)
                    else:
                        logger.warning(f"⚠️ Race {race_index + 1} analysis failed")
                        error_msg = race_analysis.get("error", "Unknown")
                        error_text = f"Race {race_index + 1} failed: {error_msg}"
                        results["errors"].append(error_text)

                except Exception as e:
                    error_msg = f"Race {race_index + 1} processing error: {e}"
                    logger.error(f"❌ {error_msg}")
                    results["errors"].append(error_msg)

            # Generate summary statistics
            results["summary_stats"] = self._generate_summary_statistics(
                results["race_analyses"]
            )

            # Calculate performance metrics
            execution_time = time.time() - start_time
            sims_per_sec = (
                round(results["total_simulations"] / execution_time, 0)
                if execution_time > 0
                else 0
            )
            races_per_min = (
                round((results["races_processed"] / execution_time) * 60, 1)
                if execution_time > 0
                else 0
            )
            avg_horses = round(
                results["horses_analyzed"] / max(results["races_processed"], 1), 1
            )

            results["performance_metrics"] = {
                "execution_time_seconds": round(execution_time, 2),
                "simulations_per_second": sims_per_sec,
                "races_per_minute": races_per_min,
                "average_horses_per_race": avg_horses,
            }

            # Save comprehensive results
            self._save_monte_carlo_results(results)

            # Set success based on performance
            error_rate = len(results["errors"]) < results["races_processed"] * 0.3
            time_ok = execution_time < 1800  # <30 minutes
            results["success"] = (
                results["races_processed"] > 0
                and error_rate  # <30% error rate
                and time_ok
            )

            results["end_time"] = datetime.now().isoformat()

            if results["success"]:
                race_count = results["races_processed"]
                sim_count = results["total_simulations"]
                completion_msg = (
                    f"🎉 Stage 10 COMPLETED: {race_count} races, "
                    f"{sim_count:,} simulations, {execution_time:.1f}s execution time"
                )
                logger.info(completion_msg)
            else:
                error_count = len(results["errors"])
                warning_msg = f"⚠️ Stage 10 completed with issues: {error_count} errors"
                logger.warning(warning_msg)

            return results

        except Exception as e:
            logger.error(f"❌ Stage 10 failed: {e}")
            results["errors"].append(f"Critical error: {e}")
            results["end_time"] = datetime.now().isoformat()
            return results

    def _load_stage9_results(self) -> List[Dict]:
        """Load Stage 9 speed analysis results from file system"""
        try:
            # Look for recent Stage 9 results
            stage9_files = [
                self.data_dir / "stage9_speed_analysis_results.json",
                self.project_root / "data" / "daily_downloads" / "stage9_results.json",
                self.project_root / "stage9_results.json",
            ]

            for file_path in stage9_files:
                if file_path.exists():
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    if isinstance(data, dict) and "race_analyses" in data:
                        return data["race_analyses"]
                    elif isinstance(data, list):
                        return data

                    logger.info(f"📁 Loaded Stage 9 results from {file_path}")
                    break

            # Fallback: Generate synthetic race data for testing
            logger.warning("⚠️ No Stage 9 results found, generating synthetic data")
            return self._generate_synthetic_race_data()

        except Exception as e:
            logger.error(f"❌ Failed to load Stage 9 results: {e}")
            return []

    def _process_race_monte_carlo(
        self, race_data: Dict, race_index: int
    ) -> Dict[str, Any]:
        """
        🎲 Process Monte Carlo simulation for a single race

        Uses Stage 9 speed analysis data to create performance profiles
        and run comprehensive Monte Carlo simulations.
        """
        analysis_start = time.time()

        race_analysis = {
            "race_index": race_index,
            "race_id": race_data.get("race_id", f"R{race_index + 1}"),
            "success": False,
            "simulations_run": 0,
            "horses_analyzed": 0,
            "betting_recommendations": [],
            "win_probabilities": {},
            "place_probabilities": {},
            "show_probabilities": {},
            "performance_profiles": [],
            "monte_carlo_analysis": None,
            "error": None,
        }

        try:
            # Extract horse data from Stage 9 results
            horses = race_data.get("horses", [])
            if not horses:
                race_analysis["error"] = "No horse data available"
                return race_analysis

            logger.info(
                f"🏇 Processing race {race_index + 1} with {len(horses)} horses"
            )

            # Create performance profiles from Stage 9 speed analysis
            performance_profiles = []
            for horse in horses:
                profile = self._create_performance_profile(horse, race_data)
                if profile:
                    performance_profiles.append(profile)

            if not performance_profiles:
                race_analysis["error"] = "No valid performance profiles created"
                return race_analysis

            race_analysis["horses_analyzed"] = len(performance_profiles)

            # Run Monte Carlo simulation
            monte_carlo_analysis = (
                self.monte_carlo_simulator.run_monte_carlo_simulation(
                    profiles=performance_profiles, race_id=race_analysis["race_id"]
                )
            )

            race_analysis["monte_carlo_analysis"] = {
                "race_id": monte_carlo_analysis.race_id,
                "simulations_run": monte_carlo_analysis.simulations_run,
                "simulation_reliability": monte_carlo_analysis.simulation_reliability,
                "win_probabilities": monte_carlo_analysis.win_probabilities,
                "place_probabilities": monte_carlo_analysis.place_probabilities,
                "show_probabilities": monte_carlo_analysis.show_probabilities,
                "average_positions": monte_carlo_analysis.average_positions,
                "confidence_intervals": {
                    horse: {"lower": ci[0], "upper": ci[1]}
                    for horse, ci in monte_carlo_analysis.confidence_intervals.items()
                },
            }

            race_analysis["simulations_run"] = monte_carlo_analysis.simulations_run
            race_analysis["win_probabilities"] = monte_carlo_analysis.win_probabilities
            race_analysis["place_probabilities"] = (
                monte_carlo_analysis.place_probabilities
            )
            race_analysis["show_probabilities"] = (
                monte_carlo_analysis.show_probabilities
            )

            # Generate betting recommendations
            betting_recommendations = (
                self.monte_carlo_simulator.get_betting_recommendations(
                    analysis=monte_carlo_analysis,
                    min_probability=self.value_bet_threshold,
                    min_value=0.10,
                )
            )

            race_analysis["betting_recommendations"] = [
                {
                    "horse_name": rec["horse_name"],
                    "bet_type": rec["bet_type"],
                    "probability": rec["probability"],
                    "fair_odds": rec["fair_odds"],
                    "confidence": rec["confidence"],
                    "z_score": rec["z_score"],
                    "expected_position": rec["average_position"],
                    "value_rating": self._calculate_value_rating(rec),
                }
                for rec in betting_recommendations
            ]

            # Store performance profiles for analysis
            race_analysis["performance_profiles"] = [
                {
                    "horse_name": profile.horse_name,
                    "mean_rating": profile.mean_rating,
                    "std_deviation": profile.std_deviation,
                    "confidence_level": profile.confidence_level,
                    "z_score": profile.z_score,
                    "performance_range": profile.performance_range,
                }
                for profile in performance_profiles
            ]

            execution_time = time.time() - analysis_start
            race_analysis["execution_time"] = round(execution_time, 3)
            race_analysis["success"] = True

            logger.info(
                f"✅ Race {race_index + 1} Monte Carlo completed: "
                f"{monte_carlo_analysis.simulations_run:,} simulations, "
                f"{len(betting_recommendations)} betting opportunities"
            )

            return race_analysis

        except Exception as e:
            race_analysis["error"] = str(e)
            logger.error(f"❌ Race {race_index + 1} Monte Carlo failed: {e}")
            return race_analysis

    def _create_performance_profile(
        self, horse_data: Dict, race_data: Dict
    ) -> Optional[PerformanceProfile]:
        """
        🐎 Create Monte Carlo performance profile from Stage 9 speed analysis data

        Converts Stage 9 speed ratings, pace analysis, and running style
        into Monte Carlo performance parameters.
        """
        try:
            horse_name = horse_data.get("horse_name", "Unknown")

            # Extract Stage 9 speed analysis metrics
            speed_figure = horse_data.get("speed_figure", 50.0)
            pace_rating = horse_data.get("pace_rating", 50.0)
            running_style_score = horse_data.get("running_style_score", 50.0)
            class_rating = horse_data.get("class_rating", 50.0)
            consistency = horse_data.get("consistency", 0.5)

            # Calculate composite performance rating
            mean_rating = (
                speed_figure * 0.35
                + pace_rating * 0.25
                + running_style_score * 0.20
                + class_rating * 0.20
            )

            # Calculate standard deviation based on consistency
            # Lower consistency = higher variance
            base_std = 15.0  # Base standard deviation
            consistency_factor = max(0.3, min(1.0, consistency))
            std_deviation = base_std * (1.5 - consistency_factor)

            # Form trend based on recent performance consistency
            form_trend = max(-1.0, min(1.0, (consistency - 0.5) * 2))

            # Confidence level based on data quality
            confidence_level = min(0.95, max(0.5, consistency * 1.2))

            # Performance range (±1 std dev)
            performance_range = (
                max(0.0, mean_rating - std_deviation),
                min(100.0, mean_rating + std_deviation),
            )

            # Calculate z-score relative to field
            race_horses = race_data.get("horses", [])
            if len(race_horses) > 1:
                field_ratings = [
                    h.get("speed_figure", 50.0) * 0.35
                    + h.get("pace_rating", 50.0) * 0.25
                    + h.get("running_style_score", 50.0) * 0.20
                    + h.get("class_rating", 50.0) * 0.20
                    for h in race_horses
                ]
                field_mean = np.mean(field_ratings)
                field_std = max(1.0, np.std(field_ratings))
                z_score = (mean_rating - field_mean) / field_std
            else:
                z_score = 0.0

            return PerformanceProfile(
                horse_name=horse_name,
                mean_rating=float(mean_rating),
                std_deviation=float(std_deviation),
                z_score=float(z_score),
                consistency_factor=float(consistency_factor),
                form_trend=float(form_trend),
                confidence_level=float(confidence_level),
                performance_range=performance_range,
            )

        except Exception as e:
            horse_name = horse_data.get("horse_name", "Unknown")
            error_msg = f"❌ Failed to create performance profile for {horse_name}: {e}"
            logger.error(error_msg)
            return None

    def _calculate_value_rating(self, recommendation: Dict) -> str:
        """Calculate value rating for betting recommendation"""
        probability = recommendation.get("probability", 0)

        # Simple value calculation based on probability vs typical market odds
        if probability > 0.30:
            return "🔥 Strong Value"
        elif probability > 0.20:
            return "⚡ Good Value"
        elif probability > 0.15:
            return "✨ Some Value"
        else:
            return "⚠️ Low Value"

    def _generate_summary_statistics(self, race_analyses: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics across all races"""
        if not race_analyses:
            return {}

        total_horses = sum(r.get("horses_analyzed", 0) for r in race_analyses)
        total_betting_opportunities = sum(
            len(r.get("betting_recommendations", [])) for r in race_analyses
        )

        # Calculate average win probabilities
        all_win_probs = []
        for race in race_analyses:
            win_probs = race.get("win_probabilities", {})
            all_win_probs.extend(win_probs.values())

        # High confidence picks analysis
        high_confidence_picks = []
        for race in race_analyses:
            high_conf = [
                r
                for r in race.get("betting_recommendations", [])
                if r.get("confidence", 0) > self.confidence_threshold
            ]
            high_confidence_picks.extend(high_conf)

        return {
            "total_races": len(race_analyses),
            "total_horses_analyzed": total_horses,
            "average_horses_per_race": (
                round(total_horses / len(race_analyses), 1) if race_analyses else 0
            ),
            "total_betting_opportunities": total_betting_opportunities,
            "betting_opportunities_per_race": (
                round(total_betting_opportunities / len(race_analyses), 1)
                if race_analyses
                else 0
            ),
            "high_confidence_picks": len(high_confidence_picks),
            "average_win_probability": (
                round(np.mean(all_win_probs), 3) if all_win_probs else 0
            ),
            "win_probability_std": (
                round(np.std(all_win_probs), 3) if all_win_probs else 0
            ),
            "probability_distribution": {
                "min": round(min(all_win_probs), 3) if all_win_probs else 0,
                "max": round(max(all_win_probs), 3) if all_win_probs else 0,
                "median": round(np.median(all_win_probs), 3) if all_win_probs else 0,
                "75th_percentile": (
                    round(np.percentile(all_win_probs, 75), 3) if all_win_probs else 0
                ),
            },
        }

    def _save_monte_carlo_results(self, results: Dict[str, Any]) -> Path:
        """Save Monte Carlo analysis results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stage10_monte_carlo_results_{timestamp}.json"
        output_file = self.output_dir / filename

        try:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            # Also save as latest results
            latest_file = self.output_dir / "stage10_monte_carlo_latest.json"
            with open(latest_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"💾 Monte Carlo results saved to {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"❌ Failed to save Monte Carlo results: {e}")
            return output_file

    def _generate_synthetic_race_data(self) -> List[Dict]:
        """Generate synthetic race data for testing when Stage 9 results unavailable"""
        logger.info("🔧 Generating synthetic race data for Monte Carlo testing")

        synthetic_races = []
        for race_idx in range(3):  # Generate 3 test races
            horses = []
            for horse_idx in range(8):  # 8 horses per race
                horse_data = {
                    "horse_name": f"Test Horse {horse_idx + 1}",
                    "number": horse_idx + 1,
                    "speed_figure": np.random.normal(55, 12),
                    "pace_rating": np.random.normal(52, 10),
                    "running_style_score": np.random.normal(50, 8),
                    "class_rating": np.random.normal(48, 15),
                    "consistency": np.random.uniform(0.4, 0.9),
                    "odds": f"{np.random.randint(2, 20)}/1",
                }
                horses.append(horse_data)

            race_data = {
                "race_id": f"TEST_R{race_idx + 1}",
                "race_number": race_idx + 1,
                "track": "Synthetic Track",
                "distance": "1600m",
                "horses": horses,
            }
            synthetic_races.append(race_data)

        return synthetic_races


def main():
    """🚀 Main execution for Stage 10 Monte Carlo Simulations"""
    print("🎲 Stage 10: Monte Carlo Simulations")
    print("=" * 60)

    # Initialize engine
    engine = Stage10MonteCarloEngine()

    # Run Monte Carlo analysis
    results = engine.run_monte_carlo_analysis()

    # Display summary
    print("\n📊 STAGE 10 RESULTS SUMMARY")
    print(f"Success: {'✅' if results['success'] else '❌'}")
    print(f"Races Processed: {results['races_processed']}")
    print(f"Total Simulations: {results['total_simulations']:,}")
    print(f"Horses Analyzed: {results['horses_analyzed']}")
    print(f"Betting Opportunities: {results['betting_opportunities']}")
    print(f"High Confidence Picks: {results['high_confidence_picks']}")

    if results["performance_metrics"]:
        print("\n⚡ PERFORMANCE METRICS")
        exec_time = results["performance_metrics"]["execution_time_seconds"]
        print(f"Execution Time: {exec_time}s")

        sims_per_sec = results["performance_metrics"]["simulations_per_second"]
        print(f"Simulations/sec: {sims_per_sec:,}")

        races_per_min = results["performance_metrics"]["races_per_minute"]
        print(f"Races/min: {races_per_min}")

    if results["errors"]:
        print(f"\nERRORS ({len(results['errors'])}):")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"   • {error}")

    return results


if __name__ == "__main__":
    try:
        results = main()
        exit_code = 0 if results.get("success", False) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Stage 10 interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Stage 10 failed: {e}")
        sys.exit(1)
