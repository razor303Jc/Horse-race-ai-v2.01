#!/usr/bin/env python3
"""
Complete Horse Racing Data Summary
=================================

Provides a comprehensive overview of all downloaded horse racing data including:
- Date ranges and coverage
- Data types and record counts
- Sample data from each file type
- Data quality assessment
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def convert_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to readable date."""
    try:
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return "Invalid"


def get_sample_record(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get the first valid JSON record from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return None


def count_records_with_dates(file_path: Path) -> Dict[str, Any]:
    """Count records and extract date information."""
    total_records = 0
    dates = set()
    has_date_field = False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                    total_records += 1

                    if isinstance(record, dict) and "Date" in record:
                        has_date_field = True
                        date_val = record["Date"]
                        if isinstance(date_val, int):
                            dates.add(convert_timestamp(date_val))

                except json.JSONDecodeError:
                    continue

    except Exception:
        pass

    return {
        "total_records": total_records,
        "has_dates": has_date_field,
        "unique_dates": sorted(dates),
        "date_count": len(dates),
    }


def analyze_data_directory():
    """Analyze all data in the horse racing database directory."""

    data_dir = Path("data/horseracedatabase")

    if not data_dir.exists():
        console.print("[red]❌ Data directory not found[/red]")
        return

    console.print(Panel("🐴 Complete Horse Racing Data Summary", style="bold blue"))

    # Overview table
    overview_table = Table(title="📊 Data Overview")
    overview_table.add_column("Data Type", style="cyan")
    overview_table.add_column("File", style="blue")
    overview_table.add_column("Records", justify="right")
    overview_table.add_column("Has Dates", justify="center")
    overview_table.add_column("Date Range", style="green")

    total_records = 0
    all_dates = set()

    # Analyze each data type
    for data_type in ["results_data", "cards_data"]:
        type_dir = data_dir / data_type

        if not type_dir.exists():
            continue

        # Find all JSON files
        for json_file in sorted(type_dir.rglob("*.json")):
            rel_path = json_file.relative_to(type_dir)

            info = count_records_with_dates(json_file)
            total_records += info["total_records"]
            all_dates.update(info["unique_dates"])

            # Format date range
            if info["unique_dates"]:
                if len(info["unique_dates"]) == 1:
                    date_range = info["unique_dates"][0]
                else:
                    date_range = (
                        f"{info['unique_dates'][0]} → {info['unique_dates'][-1]}"
                    )
            else:
                date_range = "N/A"

            # Has dates indicator
            date_indicator = "✅" if info["has_dates"] else "❌"

            overview_table.add_row(
                data_type.replace("_", " ").title(),
                str(rel_path),
                f"{info['total_records']:,}",
                date_indicator,
                date_range,
            )

    console.print(overview_table)

    # Summary stats
    console.print(f"\n[green]📈 Total Records: {total_records:,}[/green]")
    console.print(f"[blue]📅 Date Coverage: {len(all_dates)} unique dates[/blue]")

    if all_dates:
        sorted_dates = sorted(all_dates)
        console.print(
            f"[cyan]📆 Date Range: {sorted_dates[0]} → {sorted_dates[-1]}[/cyan]"
        )

    # Sample data from each file type
    console.print(f"\n[cyan]🔍 Sample Data Structures[/cyan]")

    for data_type in ["results_data", "cards_data"]:
        type_dir = data_dir / data_type

        if not type_dir.exists():
            continue

        console.print(f"\n[yellow]📁 {data_type.replace('_', ' ').title()}[/yellow]")

        for json_file in sorted(type_dir.rglob("*.json")):
            rel_path = json_file.relative_to(type_dir)
            sample = get_sample_record(json_file)

            if sample:
                tree = Tree(f"📄 {rel_path}")

                # Show key fields (limit to first 10 for readability)
                keys = list(sample.keys())[:10]
                for key in keys:
                    value = sample[key]

                    # Special handling for Date field
                    if key == "Date" and isinstance(value, int):
                        readable_date = convert_timestamp(value)
                        tree.add(f"[blue]{key}:[/blue] {value} → {readable_date}")
                    else:
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 50:
                            str_value = str_value[:47] + "..."
                        tree.add(f"[blue]{key}:[/blue] {str_value}")

                if len(sample.keys()) > 10:
                    tree.add(
                        f"[dim]... and {len(sample.keys()) - 10} more fields[/dim]"
                    )

                console.print(tree)
            else:
                console.print(f"[red]❌ Could not read sample from {rel_path}[/red]")

    # Data quality summary
    console.print(f"\n[cyan]📋 Data Quality Summary[/cyan]")

    # Check results vs cards data
    results_races_file = data_dir / "results_data" / "races" / "races.json"
    cards_races_file = data_dir / "cards_data" / "races" / "races.json"

    if results_races_file.exists() and cards_races_file.exists():
        results_info = count_records_with_dates(results_races_file)
        cards_info = count_records_with_dates(cards_races_file)

        console.print(
            f"[green]✅ Results Data: {results_info['total_records']} races on {results_info['date_count']} dates[/green]"
        )
        console.print(
            f"[green]✅ Cards Data: {cards_info['total_records']} races on {cards_info['date_count']} dates[/green]"
        )

        # Show what dates we have data for
        all_race_dates = set(results_info["unique_dates"] + cards_info["unique_dates"])
        console.print(
            f"[blue]📅 Race dates available: {', '.join(sorted(all_race_dates))}[/blue]"
        )

        # Check if we have both results and cards for same dates
        common_dates = set(results_info["unique_dates"]) & set(
            cards_info["unique_dates"]
        )
        if common_dates:
            console.print(
                f"[yellow]⚠️ Overlapping dates (both results & cards): {', '.join(sorted(common_dates))}[/yellow]"
            )

        # Suggest what this means
        console.print(f"\n[cyan]💡 Data Interpretation:[/cyan]")
        console.print(
            "[blue]• Results Data: Past race results with actual outcomes[/blue]"
        )
        console.print("[blue]• Cards Data: Future race cards (upcoming races)[/blue]")
        console.print(
            "[blue]• Different dates suggest results are historical, cards are upcoming[/blue]"
        )


if __name__ == "__main__":
    analyze_data_directory()
