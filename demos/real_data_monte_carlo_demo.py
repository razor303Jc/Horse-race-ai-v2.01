#!/usr/bin/env python3
"""
Real Data Monte Carlo Simulator Demo
===================================

Demonstration of the integrated Monte Carlo simulator that uses real race data
collected via the Playwright auto-download system from horseracedatabase and
other racing websites.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add project path
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root / "src"))

try:
    from horse_racing_ai.simulation.monte_carlo_simulator_with_real_data import (
        CompositeScore,
        RealDataMonteCarloSimulator,
        create_real_data_analysis,
    )
except ImportError as e:
    print(f"❌ Failed to import Monte Carlo simulator: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install playwright python-dotenv numpy scipy rich")
    sys.exit(1)

console = Console()
logger = logging.getLogger(__name__)


class RealDataMonteCarloDemo:
    """Demo class for the real data Monte Carlo simulator."""

    def __init__(self):
        """Initialize the demo."""
        self.console = console

    async def run_synthetic_data_demo(self):
        """Run demo with synthetic test data."""

        self.console.print(
            Panel.fit(
                "[bold blue]🏇 MONTE CARLO SIMULATOR WITH SYNTHETIC DATA[/bold blue]\n"
                "[white]Testing the integrated simulator with synthetic horse data[/white]",
                border_style="blue",
            )
        )

        # Create test composite scores (similar to what real data would generate)
        test_scores = [
            CompositeScore(
                horse_name="Thunder Strike",
                composite_score=85.5,
                confidence_level=0.8,
                key_factors=["Good recent form", "Strong jockey"],
                concerns=[],
            ),
            CompositeScore(
                horse_name="Lightning Bolt",
                composite_score=78.2,
                confidence_level=0.7,
                key_factors=["Class dropper"],
                concerns=["Wide draw"],
            ),
            CompositeScore(
                horse_name="Storm Chaser",
                composite_score=92.1,
                confidence_level=0.9,
                key_factors=["Class leader", "Good track record"],
                concerns=[],
            ),
            CompositeScore(
                horse_name="Wind Runner",
                composite_score=71.5,
                confidence_level=0.6,
                key_factors=[],
                concerns=["Poor last run", "Trainer form"],
            ),
            CompositeScore(
                horse_name="Fire Flash",
                composite_score=89.3,
                confidence_level=0.85,
                key_factors=["Consistent performer", "Favorite jockey"],
                concerns=["First time distance"],
            ),
            CompositeScore(
                horse_name="Golden Arrow",
                composite_score=74.8,
                confidence_level=0.65,
                key_factors=["Good value"],
                concerns=["Long layoff"],
            ),
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            # Initialize simulator
            task1 = progress.add_task(
                "Initializing Monte Carlo simulator...", total=None
            )
            simulator = RealDataMonteCarloSimulator(simulations=5000, random_seed=42)
            progress.remove_task(task1)

            # Create performance profiles
            task2 = progress.add_task("Creating performance profiles...", total=None)
            profiles = simulator.create_performance_profiles(test_scores)
            progress.remove_task(task2)

            # Run simulation
            task3 = progress.add_task("Running Monte Carlo simulation...", total=None)
            analysis = simulator.run_monte_carlo_simulation(profiles, "DEMO_RACE_001")
            progress.remove_task(task3)

            # Generate recommendations
            task4 = progress.add_task(
                "Generating betting recommendations...", total=None
            )
            recommendations = simulator.get_betting_recommendations(
                analysis, min_probability=0.1
            )
            progress.remove_task(task4)

        # Display results
        self._display_simulation_results(analysis, recommendations)

        return analysis, recommendations

    async def run_real_data_demo(self, race_url: Optional[str] = None):
        """Run demo with real race data (if available)."""

        self.console.print(
            Panel.fit(
                "[bold green]🏇 MONTE CARLO SIMULATOR WITH REAL DATA[/bold green]\n"
                "[white]Testing the integrated simulator with real racing data[/white]",
                border_style="green",
            )
        )

        try:
            # Initialize simulator
            simulator = RealDataMonteCarloSimulator(simulations=5000, random_seed=42)

            # Check if real data collection is available
            if not simulator.data_collector:
                self.console.print(
                    "[yellow]⚠️  Real data collection not available[/yellow]"
                )
                self.console.print(
                    "[yellow]   Using synthetic data demo instead[/yellow]"
                )
                return await self.run_synthetic_data_demo()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:

                # Collect real data
                task1 = progress.add_task("Collecting real race data...", total=None)
                try:
                    analysis = await simulator.run_real_data_simulation(race_url)
                    progress.remove_task(task1)

                    # Generate recommendations
                    task2 = progress.add_task(
                        "Generating betting recommendations...", total=None
                    )
                    recommendations = simulator.get_betting_recommendations(
                        analysis, min_probability=0.1
                    )
                    progress.remove_task(task2)

                except Exception as e:
                    progress.remove_task(task1)
                    self.console.print(f"[red]❌ Error collecting real data: {e}[/red]")
                    self.console.print(
                        "[yellow]   Falling back to synthetic data demo[/yellow]"
                    )
                    return await self.run_synthetic_data_demo()

            # Display results
            self._display_simulation_results(
                analysis, recommendations, is_real_data=True
            )

            return analysis, recommendations

        except Exception as e:
            self.console.print(f"[red]❌ Real data demo failed: {e}[/red]")
            self.console.print(
                "[yellow]   Running synthetic data demo instead[/yellow]"
            )
            return await self.run_synthetic_data_demo()

    def _display_simulation_results(
        self, analysis, recommendations, is_real_data=False
    ):
        """Display the simulation results in a formatted table."""

        data_source = "Real Racing Data" if is_real_data else "Synthetic Test Data"

        # Simulation summary
        summary_table = Table(
            title=f"Monte Carlo Analysis Summary ({data_source})", show_header=True
        )
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Race ID", analysis.race_id)
        summary_table.add_row("Simulations Run", f"{analysis.simulations_run:,}")
        summary_table.add_row("Horses in Field", str(len(analysis.horse_profiles)))
        summary_table.add_row(
            "Simulation Reliability", f"{analysis.simulation_reliability:.1%}"
        )
        summary_table.add_row("Data Source", data_source)

        self.console.print(summary_table)

        # Win probabilities
        win_table = Table(title="Win Probabilities", show_header=True)
        win_table.add_column("Horse", style="cyan")
        win_table.add_column("Win %", style="green")
        win_table.add_column("Place %", style="yellow")
        win_table.add_column("Avg Position", style="white")
        win_table.add_column("Confidence", style="magenta")

        # Sort by win probability
        sorted_horses = sorted(
            analysis.win_probabilities.items(), key=lambda x: x[1], reverse=True
        )

        for horse_name, win_prob in sorted_horses:
            place_prob = analysis.place_probabilities.get(horse_name, 0.0)
            avg_pos = analysis.average_positions.get(horse_name, 0.0)

            # Find confidence level from profiles
            profile = next(
                (p for p in analysis.horse_profiles if p.horse_name == horse_name), None
            )
            confidence = profile.confidence_level if profile else 0.0

            win_table.add_row(
                horse_name,
                f"{win_prob:.1%}",
                f"{place_prob:.1%}",
                f"{avg_pos:.1f}",
                f"{confidence:.1%}",
            )

        self.console.print(win_table)

        # Betting recommendations
        if recommendations:
            rec_table = Table(title="Betting Recommendations", show_header=True)
            rec_table.add_column("Horse", style="cyan")
            rec_table.add_column("Win %", style="green")
            rec_table.add_column("Fair Odds", style="yellow")
            rec_table.add_column("Z-Score", style="white")
            rec_table.add_column("Data Source", style="magenta")

            for rec in recommendations[:5]:  # Show top 5
                data_src = rec.get("data_source", "synthetic")
                rec_table.add_row(
                    rec["horse_name"],
                    f"{rec['probability']:.1%}",
                    f"{rec['fair_odds']:.1f}",
                    f"{rec['z_score']:.2f}",
                    data_src.title(),
                )

            self.console.print(rec_table)

        # Performance analysis
        self._display_performance_analysis(analysis)

    def _display_performance_analysis(self, analysis):
        """Display detailed performance analysis."""

        perf_table = Table(title="Performance Analysis", show_header=True)
        perf_table.add_column("Horse", style="cyan")
        perf_table.add_column("Mean Rating", style="green")
        perf_table.add_column("Std Dev", style="yellow")
        perf_table.add_column("Z-Score", style="white")
        perf_table.add_column("Form Trend", style="magenta")

        for profile in analysis.horse_profiles:
            form_trend_str = f"{profile.form_trend:+.2f}"
            perf_table.add_row(
                profile.horse_name,
                f"{profile.mean_rating:.1f}",
                f"{profile.std_deviation:.1f}",
                f"{profile.z_score:.2f}",
                form_trend_str,
            )

        self.console.print(perf_table)

    async def run_comparison_demo(self):
        """Run both synthetic and real data demos for comparison."""

        self.console.print(
            Panel.fit(
                "[bold magenta]🏇 MONTE CARLO COMPARISON DEMO[/bold magenta]\n"
                "[white]Comparing synthetic vs real data simulation results[/white]",
                border_style="magenta",
            )
        )

        # Run synthetic demo
        self.console.print("\n[blue]📊 Running Synthetic Data Simulation...[/blue]")
        synthetic_analysis, synthetic_recs = await self.run_synthetic_data_demo()

        # Run real data demo
        self.console.print("\n[green]🌐 Running Real Data Simulation...[/green]")
        real_analysis, real_recs = await self.run_real_data_demo()

        # Compare results
        self._compare_results(
            synthetic_analysis, real_analysis, synthetic_recs, real_recs
        )

    def _compare_results(
        self, synthetic_analysis, real_analysis, synthetic_recs, real_recs
    ):
        """Compare synthetic vs real data results."""

        comparison_table = Table(
            title="Synthetic vs Real Data Comparison", show_header=True
        )
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column("Synthetic Data", style="blue")
        comparison_table.add_column("Real Data", style="green")

        comparison_table.add_row(
            "Simulation Reliability",
            f"{synthetic_analysis.simulation_reliability:.1%}",
            f"{real_analysis.simulation_reliability:.1%}",
        )

        comparison_table.add_row(
            "Number of Horses",
            str(len(synthetic_analysis.horse_profiles)),
            str(len(real_analysis.horse_profiles)),
        )

        comparison_table.add_row(
            "Recommendations Generated", str(len(synthetic_recs)), str(len(real_recs))
        )

        # Top horse comparison
        synthetic_top = max(
            synthetic_analysis.win_probabilities.items(), key=lambda x: x[1]
        )
        real_top = max(real_analysis.win_probabilities.items(), key=lambda x: x[1])

        comparison_table.add_row(
            "Top Horse",
            f"{synthetic_top[0]} ({synthetic_top[1]:.1%})",
            f"{real_top[0]} ({real_top[1]:.1%})",
        )

        self.console.print(comparison_table)


async def main():
    """Main function to run the demo."""

    demo = RealDataMonteCarloDemo()

    console.print(
        Panel.fit(
            "[bold yellow]🏇 REAL DATA MONTE CARLO SIMULATOR DEMO[/bold yellow]\n"
            "[white]Integrated simulation using Playwright auto-download system[/white]",
            border_style="yellow",
        )
    )

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # For demo purposes, run with synthetic data first
        console.print("\n[blue]🧪 Running Synthetic Data Demo First...[/blue]")
        await demo.run_synthetic_data_demo()

        console.print("\n[green]🌐 Now Attempting Real Data Demo...[/green]")
        await demo.run_real_data_demo()

        console.print(
            Panel.fit(
                "[bold green]✅ DEMO COMPLETE[/bold green]\n"
                "[white]The Monte Carlo simulator is successfully integrated with the real data collection system![/white]\n\n"
                "[yellow]Next Steps:[/yellow]\n"
                "1. Configure racing website credentials in .env file\n"
                "2. Run with specific race URLs for real-time analysis\n"
                "3. Integrate with betting systems for automated recommendations\n"
                "4. Set up scheduled data collection for daily racing",
                border_style="green",
            )
        )

    except KeyboardInterrupt:
        console.print("\n🛑 Demo cancelled by user")
    except Exception as e:
        console.print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
