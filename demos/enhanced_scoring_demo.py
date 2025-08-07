#!/usr/bin/env python3
"""
Enhanced Horse Racing AI Scoring Systems Demo
============================================

Demonstrates the improved form analysis and power rating systems
with comprehensive scoring capabilities.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from horse_racing_ai.scoring.composite_scorer import CompositeScorer
from horse_racing_ai.scoring.form_analyzer import (
    EnhancedFormAnalyzer,
    RaceClass,
    RacePerformance,
    SurfaceType,
)
from horse_racing_ai.scoring.power_ratings import PowerRatingSystem

console = Console()


def generate_sample_race_data() -> Dict[str, List[RacePerformance]]:
    """Generate realistic sample race data for demonstration."""

    # Sample horses with different profiles
    horses_data = {}

    # Horse 1: Consistent form horse
    horses_data["Thunder Strike"] = [
        RacePerformance(
            date=datetime.now() - timedelta(days=14),
            track="Belmont Park",
            distance=8.0,  # 1 mile
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=10,
            finish_position=2,
            beaten_lengths=0.5,
            time=96.2,
            speed_figure=95,
            pace_figures={"early": 22, "middle": 45, "late": 29},
            weight_carried=118,
            jockey="J. Rodriguez",
            trainer="M. Smith",
            odds=3.2,
            purse=75000,
            conditions="Fast Track",
            comments="Good trip, strong finish",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=35),
            track="Saratoga",
            distance=8.0,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=9,
            finish_position=1,
            beaten_lengths=0.0,
            time=95.8,
            speed_figure=98,
            pace_figures={"early": 23, "middle": 46, "late": 27},
            weight_carried=116,
            jockey="J. Rodriguez",
            trainer="M. Smith",
            odds=2.8,
            purse=80000,
            conditions="Fast Track",
            comments="Dominant wire-to-wire win",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=63),
            track="Belmont Park",
            distance=9.0,  # 1 1/8 miles
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=8,
            finish_position=3,
            beaten_lengths=2.0,
            time=108.5,
            speed_figure=92,
            pace_figures={"early": 24, "middle": 48, "late": 37},
            weight_carried=120,
            jockey="J. Rodriguez",
            trainer="M. Smith",
            odds=4.1,
            purse=70000,
            conditions="Fast Track",
            comments="Stayed on well at longer distance",
        ),
    ]

    # Horse 2: Speed horse with inconsistency
    horses_data["Lightning Bolt"] = [
        RacePerformance(
            date=datetime.now() - timedelta(days=21),
            track="Gulfstream Park",
            distance=6.0,  # 6 furlongs
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=12,
            finish_position=1,
            beaten_lengths=0.0,
            time=69.8,
            speed_figure=105,
            pace_figures={"early": 21, "middle": 44, "late": 24},
            weight_carried=115,
            jockey="A. Garcia",
            trainer="R. Wilson",
            odds=1.9,
            purse=60000,
            conditions="Fast Track",
            comments="Explosive early speed, held on gamely",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=42),
            track="Gulfstream Park",
            distance=7.0,  # 7 furlongs
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=10,
            finish_position=6,
            beaten_lengths=8.5,
            time=81.2,
            speed_figure=88,
            pace_figures={"early": 22, "middle": 45, "late": 24},
            weight_carried=118,
            jockey="A. Garcia",
            trainer="R. Wilson",
            odds=3.5,
            purse=65000,
            conditions="Fast Track",
            comments="Faded badly in stretch",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=70),
            track="Tampa Bay Downs",
            distance=6.0,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.CLAIMING,
            field_size=8,
            finish_position=2,
            beaten_lengths=1.2,
            time=70.1,
            speed_figure=102,
            pace_figures={"early": 21, "middle": 43, "late": 26},
            weight_carried=116,
            jockey="A. Garcia",
            trainer="R. Wilson",
            odds=2.2,
            purse=40000,
            conditions="Fast Track",
            comments="Strong effort, just missed",
        ),
    ]

    # Horse 3: Class dropper with potential
    horses_data["Royal Heritage"] = [
        RacePerformance(
            date=datetime.now() - timedelta(days=28),
            track="Keeneland",
            distance=8.5,  # 1 1/16 miles
            surface=SurfaceType.DIRT,
            race_class=RaceClass.STAKES,
            field_size=14,
            finish_position=8,
            beaten_lengths=12.0,
            time=102.8,
            speed_figure=89,
            pace_figures={"early": 23, "middle": 47, "late": 33},
            weight_carried=122,
            jockey="L. Saez",
            trainer="C. Brown",
            odds=8.5,
            purse=200000,
            conditions="Fast Track",
            comments="Outclassed but showed some late interest",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=56),
            track="Churchill Downs",
            distance=8.5,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.GRADED_STAKES,
            field_size=12,
            finish_position=7,
            beaten_lengths=9.0,
            time=101.9,
            speed_figure=94,
            pace_figures={"early": 22, "middle": 45, "late": 35},
            weight_carried=118,
            jockey="L. Saez",
            trainer="C. Brown",
            odds=12.0,
            purse=500000,
            conditions="Fast Track",
            comments="Respectable effort in Grade 1 company",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=84),
            track="Saratoga",
            distance=8.0,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.ALLOWANCE,
            field_size=9,
            finish_position=1,
            beaten_lengths=0.0,
            time=95.2,
            speed_figure=101,
            pace_figures={"early": 22, "middle": 45, "late": 28},
            weight_carried=115,
            jockey="L. Saez",
            trainer="C. Brown",
            odds=3.8,
            purse=85000,
            conditions="Fast Track",
            comments="Impressive gate-to-wire victory",
        ),
    ]

    # Horse 4: Longshot with hidden form
    horses_data["Desert Wind"] = [
        RacePerformance(
            date=datetime.now() - timedelta(days=45),
            track="Santa Anita",
            distance=8.0,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.CLAIMING,
            field_size=11,
            finish_position=4,
            beaten_lengths=4.5,
            time=97.1,
            speed_figure=86,
            pace_figures={"early": 23, "middle": 47, "late": 27},
            weight_carried=114,
            jockey="F. Prat",
            trainer="J. Miller",
            odds=15.0,
            purse=50000,
            conditions="Fast Track",
            comments="Steady improvement, gaining ground late",
        ),
        RacePerformance(
            date=datetime.now() - timedelta(days=75),
            track="Santa Anita",
            distance=7.0,
            surface=SurfaceType.DIRT,
            race_class=RaceClass.CLAIMING,
            field_size=10,
            finish_position=7,
            beaten_lengths=9.0,
            time=82.3,
            speed_figure=79,
            pace_figures={"early": 22, "middle": 46, "late": 24},
            weight_carried=116,
            jockey="T. Baze",
            trainer="J. Miller",
            odds=25.0,
            purse=40000,
            conditions="Fast Track",
            comments="No factor, seemed outclassed",
        ),
    ]

    return horses_data


def create_target_race_conditions() -> Dict[str, any]:
    """Create sample target race conditions."""
    return {
        "race_id": "BEL_R7_20241203",
        "track": "Belmont Park",
        "distance": 8.0,  # 1 mile
        "surface": "dirt",
        "race_class": RaceClass.ALLOWANCE.value,
        "field_size": 10,
        "purse": 75000,
        "conditions": "Fast Track",
        "post_time": datetime.now() + timedelta(hours=2),
    }


def display_form_analysis_demo():
    """Demonstrate the enhanced form analysis system."""
    console.print()
    console.print(
        Panel(
            "[bold blue]Enhanced Form Analysis System Demo[/bold blue]",
            border_style="blue",
        )
    )

    form_analyzer = EnhancedFormAnalyzer()
    horses_data = generate_sample_race_data()
    race_conditions = create_target_race_conditions()

    # Create a table for form analysis results
    table = Table(
        title="🏇 Form Analysis Results",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
    )

    table.add_column("Horse", style="cyan", width=15)
    table.add_column("Recent Form", justify="center", width=12)
    table.add_column("Speed Rating", justify="center", width=12)
    table.add_column("Consistency", justify="center", width=12)
    table.add_column("Conditions", justify="center", width=12)
    table.add_column("Power Rating", justify="center", width=12)
    table.add_column("Confidence", justify="center", width=12)

    for horse_name, performances in horses_data.items():
        form_metrics = form_analyzer.analyze_horse_form(
            horse_name, performances, race_conditions
        )

        # Format scores with color coding
        def format_score(score, is_percentage=False):
            if is_percentage:
                score_val = score * 100
                if score_val >= 70:
                    return f"[green]{score_val:.1f}%[/green]"
                elif score_val >= 50:
                    return f"[yellow]{score_val:.1f}%[/yellow]"
                else:
                    return f"[red]{score_val:.1f}%[/red]"
            else:
                if score >= 70:
                    return f"[green]{score:.1f}[/green]"
                elif score >= 50:
                    return f"[yellow]{score:.1f}[/yellow]"
                else:
                    return f"[red]{score:.1f}[/red]"

        table.add_row(
            horse_name,
            format_score(form_metrics.recent_form_score, True),
            format_score(form_metrics.speed_rating),
            format_score(form_metrics.consistency_index, True),
            format_score(form_metrics.condition_suitability, True),
            format_score(form_metrics.power_rating),
            format_score(form_metrics.confidence_level, True),
        )

    console.print(table)
    console.print()


def display_power_ratings_demo():
    """Demonstrate the power rating system."""
    console.print(
        Panel("[bold green]Power Rating System Demo[/bold green]", border_style="green")
    )

    power_rating_system = PowerRatingSystem()
    horses_data = generate_sample_race_data()
    race_conditions = create_target_race_conditions()

    # Create table for power ratings
    table = Table(
        title="⚡ Power Ratings Breakdown",
        show_header=True,
        header_style="bold green",
        box=box.ROUNDED,
    )

    table.add_column("Horse", style="cyan", width=15)
    table.add_column("Base Rating", justify="center", width=12)
    table.add_column("Adjustments", justify="center", width=12)
    table.add_column("Final Rating", justify="center", width=12)
    table.add_column("Speed", justify="center", width=10)
    table.add_column("Class", justify="center", width=10)
    table.add_column("Form", justify="center", width=10)
    table.add_column("Consistency", justify="center", width=12)

    power_ratings = []

    for horse_name, performances in horses_data.items():
        power_rating = power_rating_system.calculate_power_rating(
            horse_name, performances, race_conditions
        )
        power_ratings.append(power_rating)

        # Format ratings with color coding
        def format_rating(rating):
            if rating >= 100:
                return f"[green]{rating:.1f}[/green]"
            elif rating >= 75:
                return f"[yellow]{rating:.1f}[/yellow]"
            else:
                return f"[red]{rating:.1f}[/red]"

        def format_adjustment(adj):
            if adj > 0:
                return f"[green]+{adj:.1f}[/green]"
            elif adj < 0:
                return f"[red]{adj:.1f}[/red]"
            else:
                return "0.0"

        table.add_row(
            horse_name,
            format_rating(power_rating.base_rating),
            format_adjustment(power_rating.conditions_adjustment),
            format_rating(power_rating.adjusted_rating),
            format_rating(power_rating.speed_component),
            format_rating(power_rating.class_component),
            format_rating(power_rating.form_component),
            format_rating(power_rating.consistency_component),
        )

    console.print(table)

    # Show top horse's detailed breakdown
    top_horse = max(power_ratings, key=lambda x: x.adjusted_rating)

    console.print()
    console.print(
        Panel(
            f"[bold]Detailed Breakdown - {top_horse.horse_name}[/bold]\n\n"
            f"Base Rating: {top_horse.base_rating:.1f}\n"
            f"Conditions Adjustment: {top_horse.conditions_adjustment:+.1f}\n"
            f"Final Rating: {top_horse.adjusted_rating:.1f}\n\n"
            f"Component Scores:\n"
            f"• Speed: {top_horse.speed_component:.1f}\n"
            f"• Class: {top_horse.class_component:.1f}\n"
            f"• Form: {top_horse.form_component:.1f}\n"
            f"• Consistency: {top_horse.consistency_component:.1f}\n\n"
            f"Confidence Level: {top_horse.confidence_level:.1%}",
            title="🏆 Top Rated Horse",
            border_style="gold1",
        )
    )
    console.print()


def display_composite_scoring_demo():
    """Demonstrate the comprehensive composite scoring system."""
    console.print(
        Panel(
            "[bold yellow]Composite Scoring System Demo[/bold yellow]",
            border_style="yellow",
        )
    )

    composite_scorer = CompositeScorer()
    horses_data = generate_sample_race_data()
    race_conditions = create_target_race_conditions()

    # Sample betting odds
    betting_odds = {
        "Thunder Strike": 3.2,
        "Lightning Bolt": 2.8,
        "Royal Heritage": 5.5,
        "Desert Wind": 12.0,
    }

    # Score the entire race
    race_analysis = composite_scorer.score_race(
        race_data=race_conditions, horses_data=horses_data, betting_odds=betting_odds
    )

    # Main results table
    table = Table(
        title="🎯 Complete Race Analysis",
        show_header=True,
        header_style="bold yellow",
        box=box.ROUNDED,
    )

    table.add_column("Rank", justify="center", width=6)
    table.add_column("Horse", style="cyan", width=15)
    table.add_column("Composite Score", justify="center", width=14)
    table.add_column("Win Prob", justify="center", width=10)
    table.add_column("Odds", justify="center", width=8)
    table.add_column("Value", justify="center", width=10)
    table.add_column("Key Factors", width=25)

    for i, score in enumerate(race_analysis.horse_scores):
        # Format probabilities and value
        win_prob = f"{score.win_probability:.1%}"

        if score.betting_value > 0.2:
            value_str = f"[green]{score.betting_value:+.1%}[/green]"
        elif score.betting_value < -0.2:
            value_str = f"[red]{score.betting_value:+.1%}[/red]"
        else:
            value_str = f"{score.betting_value:+.1%}"

        # Top key factors
        key_factors = ", ".join(score.key_factors[:2]) if score.key_factors else "None"

        table.add_row(
            str(i + 1),
            score.horse_name,
            f"{score.composite_score:.1f}",
            win_prob,
            f"{betting_odds.get(score.horse_name, 0):.1f}",
            value_str,
            key_factors,
        )

    console.print(table)

    # Race insights
    console.print()
    insights_panel = Panel(
        f"[bold]Race Insights[/bold]\n\n"
        f"• Pace Scenario: {race_analysis.pace_scenario}\n"
        f"• Track Bias: {race_analysis.track_bias}\n"
        f"• Competitiveness: {race_analysis.race_insights.get('competitiveness', 'N/A')}\n\n"
        f"[bold]Key Angles:[/bold]\n"
        + "\n".join(f"• {angle}" for angle in race_analysis.key_angles),
        title="📊 Race Analysis",
        border_style="bright_blue",
    )
    console.print(insights_panel)

    # Detailed breakdown for top 2 horses
    console.print()
    top_horses = race_analysis.horse_scores[:2]

    details_panels = []
    for i, score in enumerate(top_horses):
        concerns_text = (
            ", ".join(score.concerns) if score.concerns else "None identified"
        )

        panel_content = (
            f"[bold]Composite Score: {score.composite_score:.1f}[/bold]\n\n"
            f"Components:\n"
            f"• Speed Score: {score.speed_score:.1f}\n"
            f"• Class Score: {score.class_score:.1f}\n"
            f"• Form Score: {score.form_score:.1f}\n"
            f"• Consistency: {score.consistency_score:.1f}\n"
            f"• Conditions: {score.conditions_score:.1f}\n\n"
            f"Probabilities:\n"
            f"• Win: {score.win_probability:.1%}\n"
            f"• Place: {score.place_probability:.1%}\n"
            f"• Show: {score.show_probability:.1%}\n\n"
            f"[red]Concerns: {concerns_text}[/red]"
        )

        style = "green" if i == 0 else "blue"
        details_panels.append(
            Panel(panel_content, title=f"#{i+1} {score.horse_name}", border_style=style)
        )

    console.print(Columns(details_panels))
    console.print()


async def main():
    """Run the enhanced scoring systems demonstration."""
    console.print()
    console.print(
        Panel(
            "[bold white]🏇 Horse Racing AI v2.0 - Enhanced Scoring Systems[/bold white]\n\n"
            "[cyan]Demonstrating improved form analysis, power ratings, and composite scoring[/cyan]\n"
            "[yellow]with comprehensive handicapping factors and dynamic adjustments[/yellow]",
            title="Horse Racing AI Demo",
            border_style="bright_magenta",
            padding=(1, 2),
        )
    )

    try:
        # Run the demonstrations
        display_form_analysis_demo()
        display_power_ratings_demo()
        display_composite_scoring_demo()

        console.print(
            Panel(
                "[bold green]✅ Demo completed successfully![/bold green]\n\n"
                "[cyan]Key Improvements in v2.0:[/cyan]\n"
                "• Multi-layered form analysis with recency weighting\n"
                "• Dynamic power ratings with condition adjustments\n"
                "• Comprehensive composite scoring system\n"
                "• Advanced pace and trip analysis\n"
                "• Confidence-weighted predictions\n"
                "• Value assessment vs betting odds\n"
                "• Detailed factor breakdowns and insights",
                title="🎯 System Summary",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]Error during demo: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())
