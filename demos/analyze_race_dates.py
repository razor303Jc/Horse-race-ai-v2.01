#!/usr/bin/env python3
"""
Race Data Date Analysis
======================

Analyzes the downloaded horse racing data to extract and display date ranges.
Converts Unix timestamps to readable dates and shows data coverage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def convert_timestamp_to_date(timestamp: int) -> str:
    """Convert Unix timestamp (milliseconds) to readable date."""
    try:
        # Convert milliseconds to seconds
        timestamp_seconds = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp_seconds)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return f"Invalid timestamp: {timestamp}"


def analyze_json_file(file_path: Path) -> Set[int]:
    """Extract all Date timestamps from a JSON file."""
    timestamps = set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and "Date" in data:
                        timestamps.add(data["Date"])
                except json.JSONDecodeError as e:
                    console.print(
                        f"[yellow]Warning: Invalid JSON at line {line_num} "
                        f"in {file_path.name}: {e}[/yellow]"
                    )
                    continue

    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")

    return timestamps


def analyze_race_data():
    """Analyze all race data files and extract date information."""

    # Data directories
    data_dir = Path("data/horseracedatabase")

    if not data_dir.exists():
        console.print(f"[red]❌ Data directory not found: {data_dir}[/red]")
        return

    console.print(Panel("🐴 Race Data Date Analysis", style="bold blue"))

    # Track all timestamps by data type
    all_timestamps = defaultdict(set)
    file_info = {}

    # Analyze both results and cards data
    for data_type in ["results_data", "cards_data"]:
        type_dir = data_dir / data_type

        if not type_dir.exists():
            console.print(f"[yellow]⚠️ {data_type} directory not found[/yellow]")
            continue

        console.print(f"\n[cyan]📁 Analyzing {data_type}...[/cyan]")

        # Find all JSON files recursively
        json_files = list(type_dir.rglob("*.json"))

        if not json_files:
            console.print(f"[yellow]⚠️ No JSON files found in {data_type}[/yellow]")
            continue

        for json_file in json_files:
            rel_path = json_file.relative_to(data_dir)
            console.print(f"[blue]   📄 Processing {rel_path}...[/blue]")

            timestamps = analyze_json_file(json_file)

            if timestamps:
                all_timestamps[data_type].update(timestamps)
                unique_dates_count = len(
                    set(convert_timestamp_to_date(ts) for ts in timestamps)
                )
                file_info[str(json_file.relative_to(data_dir))] = {
                    "timestamps": len(timestamps),
                    "unique_dates": unique_dates_count,
                }
                console.print(
                    f"[green]     ✅ Found {len(timestamps)} unique timestamps[/green]"
                )
            else:
                console.print(f"[yellow]     ⚠️ No date data found[/yellow]")

    # Display summary
    console.print(f"\n[cyan]📊 Date Analysis Summary[/cyan]")

    if not any(all_timestamps.values()):
        console.print("[red]❌ No timestamp data found in any files[/red]")
        return

    # Create summary table
    table = Table(title="Data Coverage Summary")
    table.add_column("Data Type", style="cyan")
    table.add_column("Unique Timestamps", justify="right")
    table.add_column("Date Range", style="green")
    table.add_column("Days Covered", justify="right")

    for data_type, timestamps in all_timestamps.items():
        if timestamps:
            min_ts = min(timestamps)
            max_ts = max(timestamps)

            min_date = convert_timestamp_to_date(min_ts)
            max_date = convert_timestamp_to_date(max_ts)

            # Calculate unique dates
            unique_dates = set(convert_timestamp_to_date(ts) for ts in timestamps)

            date_range = (
                f"{min_date} → {max_date}" if min_date != max_date else min_date
            )

            table.add_row(
                data_type.replace("_", " ").title(),
                str(len(timestamps)),
                date_range,
                str(len(unique_dates)),
            )

    console.print(table)

    # Show specific example timestamps
    console.print(f"\n[cyan]🔍 Example Timestamp Analysis[/cyan]")

    # Show the timestamp from the user's selection
    example_timestamp = 1754352000000
    example_date = convert_timestamp_to_date(example_timestamp)

    console.print(f"[blue]Timestamp: {example_timestamp}[/blue]")
    console.print(f"[green]Converts to: {example_date}[/green]")

    # Check if this is a future date
    current_date = datetime.now()
    timestamp_date = datetime.fromtimestamp(example_timestamp / 1000)

    if timestamp_date > current_date:
        days_future = (timestamp_date - current_date).days
        console.print(f"[yellow]⚠️ This is {days_future} days in the future![/yellow]")
    else:
        days_past = (current_date - timestamp_date).days
        console.print(f"[blue]This was {days_past} days ago[/blue]")

    # Show all unique dates found
    console.print(f"\n[cyan]📅 All Unique Dates Found[/cyan]")

    all_dates = set()
    for timestamps in all_timestamps.values():
        for ts in timestamps:
            all_dates.add(convert_timestamp_to_date(ts))

    sorted_dates = sorted(all_dates)

    if len(sorted_dates) <= 20:
        for date in sorted_dates:
            console.print(f"[green]  • {date}[/green]")
    else:
        console.print(
            f"[blue]Showing first 10 and last 10 of {len(sorted_dates)} dates:[/blue]"
        )
        for date in sorted_dates[:10]:
            console.print(f"[green]  • {date}[/green]")
        console.print(f"[blue]  ... ({len(sorted_dates) - 20} more dates) ...[/blue]")
        for date in sorted_dates[-10:]:
            console.print(f"[green]  • {date}[/green]")

    # File details
    console.print(f"\n[cyan]📋 File Details[/cyan]")
    for file_path, info in file_info.items():
        console.print(
            f"[blue]{file_path}:[/blue] {info['timestamps']} timestamps, {info['unique_dates']} unique dates"
        )


if __name__ == "__main__":
    analyze_race_data()
