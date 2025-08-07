#!/usr/bin/env python3
"""
Detailed Race Data Content Analysis
===================================

Analyzes the content of downloaded race data files to show:
- Number of races per date
- Types of data available
- Sample race information
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def convert_timestamp_to_date(timestamp: int) -> str:
    """Convert Unix timestamp (milliseconds) to readable date."""
    try:
        timestamp_seconds = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp_seconds)
        return dt.strftime("%Y-%m-%d (%A)")
    except (ValueError, OSError):
        return f"Invalid: {timestamp}"


def analyze_races_file(file_path: Path) -> Dict:
    """Analyze a races.json file and extract detailed information."""

    races_by_date = defaultdict(list)
    courses = set()
    race_types = set()
    total_races = 0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    race = json.loads(line)
                    if isinstance(race, dict):
                        total_races += 1

                        # Extract key information
                        date_ts = race.get("Date")
                        course = race.get("Course", "Unknown")
                        race_type = race.get("Race_type", "Unknown")
                        race_name = race.get("Race_name", "Unnamed")
                        race_time = race.get("race_time", "Unknown")
                        runners = race.get("Runners", "Unknown")

                        courses.add(course)
                        race_types.add(race_type)

                        if date_ts:
                            date_str = convert_timestamp_to_date(date_ts)
                            races_by_date[date_str].append(
                                {
                                    "course": course,
                                    "type": race_type,
                                    "name": race_name,
                                    "time": race_time,
                                    "runners": runners,
                                    "race_id": race.get("Race_ID", "Unknown"),
                                }
                            )

                except json.JSONDecodeError as e:
                    console.print(
                        f"[yellow]JSON error at line {line_num}: {e}[/yellow]"
                    )
                    continue

    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return {}

    return {
        "races_by_date": dict(races_by_date),
        "courses": sorted(courses),
        "race_types": sorted(race_types),
        "total_races": total_races,
    }


def analyze_all_race_data():
    """Analyze all race data and provide detailed breakdown."""

    data_dir = Path("data/horseracedatabase")

    if not data_dir.exists():
        console.print(f"[red]❌ Data directory not found: {data_dir}[/red]")
        return

    console.print(Panel("🐴 Detailed Race Data Analysis", style="bold blue"))

    # Analyze both data types
    for data_type in ["results_data", "cards_data"]:
        type_dir = data_dir / data_type
        races_file = type_dir / "races" / "races.json"

        if not races_file.exists():
            console.print(f"[yellow]⚠️ No races.json found in {data_type}[/yellow]")
            continue

        console.print(
            f"\n[cyan]📊 Analyzing {data_type.replace('_', ' ').title()}[/cyan]"
        )

        analysis = analyze_races_file(races_file)

        if not analysis:
            console.print("[red]❌ Failed to analyze data[/red]")
            continue

        # Summary stats
        console.print(f"[green]✅ Total races: {analysis['total_races']}[/green]")
        console.print(f"[blue]📍 Courses: {len(analysis['courses'])}[/blue]")
        console.print(f"[blue]🏁 Race types: {len(analysis['race_types'])}[/blue]")

        # Show courses
        if analysis["courses"]:
            console.print("[cyan]📍 Courses found:[/cyan]")
            for i, course in enumerate(analysis["courses"]):
                if i < 10:  # Show first 10
                    console.print(f"   • {course}")
                elif i == 10:
                    console.print(f"   ... and {len(analysis['courses']) - 10} more")
                    break

        # Show race types
        if analysis["race_types"]:
            console.print("[cyan]🏁 Race types found:[/cyan]")
            for race_type in analysis["race_types"]:
                console.print(f"   • {race_type}")

        # Detailed breakdown by date
        races_by_date = analysis["races_by_date"]

        if races_by_date:
            console.print(f"\n[cyan]📅 Races by Date[/cyan]")

            for date, races in races_by_date.items():
                console.print(f"\n[green]📅 {date}[/green]")
                console.print(f"[blue]   Total races: {len(races)}[/blue]")

                # Group by course
                races_by_course = defaultdict(list)
                for race in races:
                    races_by_course[race["course"]].append(race)

                # Show races by course
                for course, course_races in races_by_course.items():
                    console.print(
                        f"[cyan]   📍 {course} ({len(course_races)} races)[/cyan]"
                    )

                    # Show first few races as examples
                    for i, race in enumerate(course_races[:3]):
                        time_str = race["time"]
                        runners_str = race["runners"]
                        console.print(
                            f"     {time_str}: {race['name']} "
                            f"({race['type']}, {runners_str} runners)"
                        )

                    if len(course_races) > 3:
                        console.print(
                            f"     ... and {len(course_races) - 3} more races"
                        )

        console.print(f"\n{'='*60}")


def show_sample_race_data():
    """Show sample race data structure."""

    data_dir = Path("data/horseracedatabase")

    # Try to get a sample race from cards data
    cards_races = data_dir / "cards_data" / "races" / "races.json"

    if cards_races.exists():
        console.print(f"\n[cyan]📋 Sample Race Data Structure[/cyan]")

        try:
            with open(cards_races, "r") as f:
                first_line = f.readline().strip()
                if first_line:
                    race_data = json.loads(first_line)

                    # Create a tree structure to show the data
                    tree = Tree("🏁 Sample Race Record")

                    for key, value in race_data.items():
                        if key == "Date":
                            readable_date = convert_timestamp_to_date(value)
                            tree.add(f"[blue]{key}:[/blue] {value} → {readable_date}")
                        else:
                            tree.add(f"[blue]{key}:[/blue] {value}")

                    console.print(tree)

        except Exception as e:
            console.print(f"[red]Error showing sample: {e}[/red]")


if __name__ == "__main__":
    analyze_all_race_data()
    show_sample_race_data()
