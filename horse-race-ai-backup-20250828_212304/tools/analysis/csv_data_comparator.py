#!/usr/bin/env python3
"""
CSV Data Comparison Tool
=======================

Comprehensive comparison tool for downloaded race data:
- Compares race cards data vs results data
- Identifies identical files, differences, and unique data
- Provides detailed analysis of data overlaps and gaps
- Generates comparison reports with actionable insights

Features:
- File-by-file comparison with detailed metrics
- Data structure analysis and schema comparison
- Content overlap detection and difference highlighting
- Race ID matching and cross-referencing
- Date range analysis and temporal comparisons
- Export comparison results to multiple formats
"""

import csv
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

console = Console()
logger = logging.getLogger(__name__)


class CSVDataComparator:
    """Comprehensive CSV data comparison tool"""

    def __init__(self, data_dir: str = "data/daily_downloads"):
        self.data_dir = Path(data_dir)
        self.results_dir = self.data_dir / "results_data"
        self.cards_dir = self.data_dir / "cards_data"
        self.today = datetime.now().date()

        # Comparison results storage
        self.comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "directories_compared": [],
            "file_comparisons": {},
            "summary": {},
            "recommendations": [],
        }

        # File types to compare
        self.file_types = {
            "races": ["races.csv"],
            "records": ["records.csv"],
            "horses": ["horses.csv"],
            "jockeys_stats": ["jockeys_stats.csv"],
            "trainers_stats": ["trainers_stats.csv"],
            "racecard_details": ["racecard_details.csv"],
        }

    def run_comprehensive_comparison(self) -> Dict:
        """Run complete data comparison analysis"""
        console.print("\n🔍 [bold blue]CSV Data Comparison Analysis[/bold blue]")
        console.print(f"📅 Analysis Date: {self.today}")
        console.print(f"📁 Data Directory: {self.data_dir}")

        try:
            # Step 1: Analyze directory structure
            self._analyze_directory_structure()

            # Step 2: Compare all CSV files
            self._compare_all_csv_files()

            # Step 3: Analyze data overlaps
            self._analyze_data_overlaps()

            # Step 4: Generate insights and recommendations
            self._generate_insights()

            # Step 5: Create comprehensive report
            self._create_comparison_report()

            return self.comparison_results

        except Exception as e:
            error_msg = f"Comparison analysis failed: {e}"
            logger.error(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return {"error": error_msg}

    def _analyze_directory_structure(self):
        """Analyze and compare directory structures"""
        console.print("\n📁 [cyan]Step 1: Analyzing Directory Structure[/cyan]")

        structure_analysis = {
            "results_data": self._scan_directory(self.results_dir),
            "cards_data": self._scan_directory(self.cards_dir),
        }

        self.comparison_results["directory_structure"] = structure_analysis

        # Display structure comparison
        tree = Tree("📊 Data Structure Comparison")

        results_branch = tree.add("📈 Results Data")
        cards_branch = tree.add("📋 Cards Data")

        for category, files in structure_analysis["results_data"].items():
            if files:
                cat_branch = results_branch.add(f"📂 {category}")
                for file_info in files:
                    size_info = f"({file_info['size']:,} bytes)"
                    cat_branch.add(f"📄 {file_info['name']} {size_info}")

        for category, files in structure_analysis["cards_data"].items():
            if files:
                cat_branch = cards_branch.add(f"📂 {category}")
                for file_info in files:
                    size_info = f"({file_info['size']:,} bytes)"
                    cat_branch.add(f"📄 {file_info['name']} {size_info}")

        console.print(tree)

    def _scan_directory(self, directory: Path) -> Dict[str, List[Dict]]:
        """Scan directory and categorize files"""
        scan_results = {}

        if not directory.exists():
            console.print(f"[yellow]⚠️ Directory not found: {directory}[/yellow]")
            return scan_results

        # Scan all subdirectories
        for item in directory.rglob("*.csv"):
            relative_path = item.relative_to(directory)
            parent_path = relative_path.parent
            category = str(parent_path) if parent_path != Path(".") else "root"

            if category not in scan_results:
                scan_results[category] = []

            file_info = {
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                "relative_path": str(relative_path),
            }

            scan_results[category].append(file_info)

        return scan_results

    def _compare_all_csv_files(self):
        """Compare all matching CSV files between results and cards"""
        console.print("\n🔍 [cyan]Step 2: Comparing CSV Files[/cyan]")

        # Find matching file pairs
        file_pairs = self._find_matching_files()

        if not file_pairs:
            console.print("[yellow]⚠️ No matching files found to compare[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            task = progress.add_task("Comparing CSV files...", total=len(file_pairs))

            for file_type, (results_file, cards_file) in file_pairs.items():
                progress.update(task, description=f"Comparing {file_type}...")

                comparison_result = self._compare_csv_files(
                    results_file, cards_file, file_type
                )

                self.comparison_results["file_comparisons"][
                    file_type
                ] = comparison_result
                progress.advance(task)

        # Display comparison summary
        self._display_file_comparison_summary()

    def _find_matching_files(self) -> Dict[str, Tuple[Path, Path]]:
        """Find matching CSV files between results and cards directories"""
        matching_files = {}

        # Search for matching files
        for file_type, file_names in self.file_types.items():
            for file_name in file_names:
                # Find in results data
                results_matches = list(self.results_dir.rglob(file_name))
                cards_matches = list(self.cards_dir.rglob(file_name))

                if results_matches and cards_matches:
                    # Take the first match from each directory
                    matching_files[file_type] = (results_matches[0], cards_matches[0])
                    console.print(f"✅ Found matching pair: {file_type}")
                elif results_matches:
                    console.print(f"⚠️ Only in results: {file_type}")
                elif cards_matches:
                    console.print(f"⚠️ Only in cards: {file_type}")

        return matching_files

    def _compare_csv_files(self, file1: Path, file2: Path, file_type: str) -> Dict:
        """Compare two CSV files and return detailed comparison"""
        comparison = {
            "file1": str(file1),
            "file2": str(file2),
            "file_type": file_type,
            "identical": False,
            "schema_match": False,
            "data_overlap": {},
            "differences": {},
            "statistics": {},
            "errors": [],
        }

        try:
            # Load both CSV files
            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)

            # Basic statistics
            comparison["statistics"] = {
                "file1_rows": len(df1),
                "file2_rows": len(df2),
                "file1_columns": len(df1.columns),
                "file2_columns": len(df2.columns),
                "file1_size": file1.stat().st_size,
                "file2_size": file2.stat().st_size,
            }

            # Schema comparison
            schema_comparison = self._compare_schemas(df1, df2)
            comparison["schema_match"] = schema_comparison["identical"]
            comparison["schema_details"] = schema_comparison

            # Data comparison
            if schema_comparison["identical"]:
                data_comparison = self._compare_dataframes(df1, df2, file_type)
                comparison.update(data_comparison)
            else:
                comparison["differences"]["schema_mismatch"] = True
                # Try to compare common columns
                common_cols = set(df1.columns) & set(df2.columns)
                if common_cols:
                    common_comparison = self._compare_common_columns(
                        df1, df2, common_cols, file_type
                    )
                    comparison["partial_comparison"] = common_comparison

        except Exception as e:
            error_msg = f"Error comparing {file1.name} and {file2.name}: {e}"
            comparison["errors"].append(error_msg)
            logger.error(error_msg)

        return comparison

    def _compare_schemas(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict:
        """Compare the schemas of two dataframes"""
        schema_comparison = {
            "identical": False,
            "columns_df1": list(df1.columns),
            "columns_df2": list(df2.columns),
            "common_columns": [],
            "df1_only": [],
            "df2_only": [],
            "dtype_differences": {},
        }

        cols1 = set(df1.columns)
        cols2 = set(df2.columns)

        schema_comparison["common_columns"] = list(cols1 & cols2)
        schema_comparison["df1_only"] = list(cols1 - cols2)
        schema_comparison["df2_only"] = list(cols2 - cols1)
        schema_comparison["identical"] = cols1 == cols2

        # Compare data types for common columns
        for col in schema_comparison["common_columns"]:
            if str(df1[col].dtype) != str(df2[col].dtype):
                schema_comparison["dtype_differences"][col] = {
                    "df1_dtype": str(df1[col].dtype),
                    "df2_dtype": str(df2[col].dtype),
                }

        return schema_comparison

    def _compare_dataframes(
        self, df1: pd.DataFrame, df2: pd.DataFrame, file_type: str
    ) -> Dict:
        """Compare the actual data content of two dataframes"""
        data_comparison = {
            "identical": False,
            "data_overlap": {},
            "differences": {},
            "key_analysis": {},
        }

        # Check if dataframes are identical
        try:
            data_comparison["identical"] = df1.equals(df2)
        except Exception:
            data_comparison["identical"] = False

        # Analyze by key columns based on file type
        if file_type == "races":
            key_col = "Race_ID"
        elif file_type == "records":
            key_col = "Record_ID"
        elif file_type in ["horses", "jockeys_stats", "trainers_stats"]:
            key_col = df1.columns[0] if len(df1.columns) > 0 else None
        else:
            key_col = df1.columns[0] if len(df1.columns) > 0 else None

        if key_col and key_col in df1.columns and key_col in df2.columns:
            key_analysis = self._analyze_by_key_column(df1, df2, key_col)
            data_comparison["key_analysis"] = key_analysis

        # Row-by-row comparison for smaller datasets
        if len(df1) <= 1000 and len(df2) <= 1000:
            row_comparison = self._compare_rows(df1, df2)
            data_comparison["row_comparison"] = row_comparison

        return data_comparison

    def _analyze_by_key_column(
        self, df1: pd.DataFrame, df2: pd.DataFrame, key_col: str
    ) -> Dict:
        """Analyze overlaps and differences by key column"""
        keys1 = set(df1[key_col].astype(str))
        keys2 = set(df2[key_col].astype(str))

        return {
            "key_column": key_col,
            "total_keys_df1": len(keys1),
            "total_keys_df2": len(keys2),
            "common_keys": len(keys1 & keys2),
            "df1_only_keys": len(keys1 - keys2),
            "df2_only_keys": len(keys2 - keys1),
            "overlap_percentage": (len(keys1 & keys2) / max(len(keys1 | keys2), 1))
            * 100,
            "common_keys_list": list(keys1 & keys2)[:10],  # First 10 for display
            "df1_only_list": list(keys1 - keys2)[:10],
            "df2_only_list": list(keys2 - keys1)[:10],
        }

    def _compare_common_columns(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        common_cols: Set[str],
        file_type: str,
    ) -> Dict:
        """Compare data in common columns when schemas don't match exactly"""
        df1_common = df1[list(common_cols)]
        df2_common = df2[list(common_cols)]

        return self._compare_dataframes(df1_common, df2_common, file_type)

    def _compare_rows(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict:
        """Compare dataframes row by row"""
        comparison = {
            "identical_rows": 0,
            "different_rows": 0,
            "df1_extra_rows": 0,
            "df2_extra_rows": 0,
        }

        # Simple comparison for now
        min_rows = min(len(df1), len(df2))

        for i in range(min_rows):
            try:
                if df1.iloc[i].equals(df2.iloc[i]):
                    comparison["identical_rows"] += 1
                else:
                    comparison["different_rows"] += 1
            except Exception:
                comparison["different_rows"] += 1

        comparison["df1_extra_rows"] = max(0, len(df1) - min_rows)
        comparison["df2_extra_rows"] = max(0, len(df2) - min_rows)

        return comparison

    def _display_file_comparison_summary(self):
        """Display summary of file comparisons"""
        if not self.comparison_results["file_comparisons"]:
            return

        console.print("\n📊 [bold green]File Comparison Summary[/bold green]")

        summary_table = Table(title="🔍 CSV Comparison Results", show_header=True)
        summary_table.add_column("File Type", style="cyan")
        summary_table.add_column("Schema Match", style="green")
        summary_table.add_column("Data Identical", style="yellow")
        summary_table.add_column("Rows (R/C)", style="magenta")
        summary_table.add_column("Key Overlap", style="blue")
        summary_table.add_column("Notes", style="white")

        for file_type, comparison in self.comparison_results[
            "file_comparisons"
        ].items():
            schema_match = "✅" if comparison.get("schema_match", False) else "❌"
            data_identical = "✅" if comparison.get("identical", False) else "❌"

            stats = comparison.get("statistics", {})
            rows_info = f"{stats.get('file1_rows', 0)}/{stats.get('file2_rows', 0)}"

            key_analysis = comparison.get("key_analysis", {})
            if key_analysis:
                overlap_pct = key_analysis.get("overlap_percentage", 0)
                overlap_info = f"{overlap_pct:.1f}%"
            else:
                overlap_info = "N/A"

            notes = (
                "Perfect match"
                if comparison.get("identical", False)
                else "Differences found"
            )
            if comparison.get("errors"):
                notes = f"Error: {len(comparison['errors'])} issues"

            summary_table.add_row(
                file_type, schema_match, data_identical, rows_info, overlap_info, notes
            )

        console.print(summary_table)

    def _analyze_data_overlaps(self):
        """Analyze overall data overlaps and patterns"""
        console.print("\n🔄 [cyan]Step 3: Analyzing Data Overlaps[/cyan]")

        overlap_analysis = {
            "total_files_compared": len(self.comparison_results["file_comparisons"]),
            "identical_files": 0,
            "schema_matches": 0,
            "data_overlaps": {},
            "common_patterns": [],
        }

        # Analyze patterns across all comparisons
        for file_type, comparison in self.comparison_results[
            "file_comparisons"
        ].items():
            if comparison.get("identical", False):
                overlap_analysis["identical_files"] += 1

            if comparison.get("schema_match", False):
                overlap_analysis["schema_matches"] += 1

            # Extract key overlap data
            key_analysis = comparison.get("key_analysis", {})
            if key_analysis:
                overlap_analysis["data_overlaps"][file_type] = {
                    "overlap_percentage": key_analysis.get("overlap_percentage", 0),
                    "common_keys": key_analysis.get("common_keys", 0),
                    "total_unique": key_analysis.get("total_keys_df1", 0)
                    + key_analysis.get("total_keys_df2", 0)
                    - key_analysis.get("common_keys", 0),
                }

        self.comparison_results["overlap_analysis"] = overlap_analysis

        # Display overlap analysis
        overlap_table = Table(title="🔄 Data Overlap Analysis", show_header=True)
        overlap_table.add_column("File Type", style="cyan")
        overlap_table.add_column("Overlap %", style="yellow")
        overlap_table.add_column("Common Records", style="green")
        overlap_table.add_column("Total Unique", style="magenta")
        overlap_table.add_column("Assessment", style="blue")

        for file_type, overlap_data in overlap_analysis["data_overlaps"].items():
            overlap_pct = overlap_data["overlap_percentage"]
            common_records = overlap_data["common_keys"]
            total_unique = overlap_data["total_unique"]

            if overlap_pct >= 90:
                assessment = "✅ High Overlap"
            elif overlap_pct >= 70:
                assessment = "⚠️ Moderate Overlap"
            elif overlap_pct >= 30:
                assessment = "🔍 Low Overlap"
            else:
                assessment = "❌ Minimal Overlap"

            overlap_table.add_row(
                file_type,
                f"{overlap_pct:.1f}%",
                str(common_records),
                str(total_unique),
                assessment,
            )

        console.print(overlap_table)

    def _generate_insights(self):
        """Generate insights and recommendations based on comparison"""
        console.print("\n💡 [cyan]Step 4: Generating Insights[/cyan]")

        insights = []
        recommendations = []

        # Analyze overall patterns
        overlap_analysis = self.comparison_results.get("overlap_analysis", {})
        total_files = overlap_analysis.get("total_files_compared", 0)
        identical_files = overlap_analysis.get("identical_files", 0)

        if total_files > 0:
            identical_ratio = identical_files / total_files

            if identical_ratio == 1.0:
                insights.append("🎯 Perfect Match: All compared files are identical")
                recommendations.append(
                    "✅ Data consistency is excellent - no action needed"
                )
            elif identical_ratio >= 0.7:
                insights.append("✅ High Consistency: Most files match well")
                recommendations.append("🔍 Review differences in non-matching files")
            elif identical_ratio >= 0.3:
                insights.append(
                    "⚠️ Moderate Consistency: Some significant differences found"
                )
                recommendations.append("🔧 Investigate data source discrepancies")
            else:
                insights.append("❌ Low Consistency: Major differences detected")
                recommendations.append("🚨 Review data pipeline and source integrity")

        # Analyze data overlaps
        data_overlaps = overlap_analysis.get("data_overlaps", {})
        high_overlap_count = sum(
            1
            for overlap in data_overlaps.values()
            if overlap["overlap_percentage"] >= 90
        )

        if high_overlap_count == len(data_overlaps) and len(data_overlaps) > 0:
            insights.append(
                "🔄 Complete Overlap: All data represents the same information"
            )
            recommendations.append(
                "📚 This suggests both files contain historical data"
            )
        elif high_overlap_count > 0:
            insights.append(
                f"🔄 Partial Overlap: {high_overlap_count}/{len(data_overlaps)} files have high overlap"
            )
            recommendations.append(
                "🔍 Mixed data sources - some current, some historical"
            )

        # Check for specific patterns
        if "races" in self.comparison_results["file_comparisons"]:
            races_comparison = self.comparison_results["file_comparisons"]["races"]
            if races_comparison.get("identical", False):
                insights.append("🏇 Race data is identical - likely no new races today")
                recommendations.append("📅 Check racing calendar for today's fixtures")

        self.comparison_results["insights"] = insights
        self.comparison_results["recommendations"] = recommendations

        # Display insights
        console.print("\n💡 [bold yellow]Key Insights:[/bold yellow]")
        for insight in insights:
            console.print(f"  {insight}")

        console.print("\n🎯 [bold green]Recommendations:[/bold green]")
        for recommendation in recommendations:
            console.print(f"  {recommendation}")

    def _create_comparison_report(self):
        """Create comprehensive comparison report"""
        console.print("\n📊 [cyan]Step 5: Creating Comparison Report[/cyan]")

        # Create summary for report
        self.comparison_results["summary"] = {
            "analysis_date": self.today.isoformat(),
            "total_comparisons": len(self.comparison_results["file_comparisons"]),
            "directories_analyzed": ["results_data", "cards_data"],
            "key_findings": {
                "identical_files": self.comparison_results.get(
                    "overlap_analysis", {}
                ).get("identical_files", 0),
                "schema_matches": self.comparison_results.get(
                    "overlap_analysis", {}
                ).get("schema_matches", 0),
                "data_consistency": (
                    "High"
                    if self.comparison_results.get("overlap_analysis", {}).get(
                        "identical_files", 0
                    )
                    > 0
                    else "Variable"
                ),
            },
        }

        # Save detailed report
        report_file = (
            self.data_dir / f"comparison_report_{self.today.strftime('%Y%m%d')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.comparison_results, f, indent=2, default=str)

        console.print(f"✅ Detailed report saved: {report_file}")

        # Create human-readable summary
        summary_file = (
            self.data_dir / f"comparison_summary_{self.today.strftime('%Y%m%d')}.md"
        )
        self._create_markdown_summary(summary_file)
        console.print(f"✅ Summary report saved: {summary_file}")

    def _create_markdown_summary(self, summary_file: Path):
        """Create a human-readable markdown summary"""
        with open(summary_file, "w") as f:
            f.write(f"# CSV Data Comparison Report\n\n")
            f.write(f"**Date**: {self.today}\n")
            f.write(f"**Analysis Time**: {datetime.now().strftime('%H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            summary = self.comparison_results.get("summary", {})
            f.write(f"- **Total Comparisons**: {summary.get('total_comparisons', 0)}\n")
            f.write(
                f"- **Identical Files**: {summary.get('key_findings', {}).get('identical_files', 0)}\n"
            )
            f.write(
                f"- **Schema Matches**: {summary.get('key_findings', {}).get('schema_matches', 0)}\n"
            )
            f.write(
                f"- **Data Consistency**: {summary.get('key_findings', {}).get('data_consistency', 'Unknown')}\n\n"
            )

            f.write("## File Comparisons\n\n")
            for file_type, comparison in self.comparison_results[
                "file_comparisons"
            ].items():
                f.write(f"### {file_type.title()}\n")
                f.write(
                    f"- **Schema Match**: {'✅ Yes' if comparison.get('schema_match') else '❌ No'}\n"
                )
                f.write(
                    f"- **Data Identical**: {'✅ Yes' if comparison.get('identical') else '❌ No'}\n"
                )

                stats = comparison.get("statistics", {})
                f.write(f"- **Results Rows**: {stats.get('file1_rows', 'N/A')}\n")
                f.write(f"- **Cards Rows**: {stats.get('file2_rows', 'N/A')}\n")

                key_analysis = comparison.get("key_analysis", {})
                if key_analysis:
                    f.write(
                        f"- **Data Overlap**: {key_analysis.get('overlap_percentage', 0):.1f}%\n"
                    )
                f.write("\n")

            f.write("## Insights\n\n")
            for insight in self.comparison_results.get("insights", []):
                f.write(f"- {insight}\n")

            f.write("\n## Recommendations\n\n")
            for recommendation in self.comparison_results.get("recommendations", []):
                f.write(f"- {recommendation}\n")


def main():
    """Run the CSV data comparison tool"""
    comparator = CSVDataComparator()
    results = comparator.run_comprehensive_comparison()

    if "error" not in results:
        console.print("\n🎯 [bold green]CSV Data Comparison Complete![/bold green]")
        console.print("📊 Check the generated reports for detailed analysis")
    else:
        console.print(
            f"\n❌ [bold red]Comparison failed: {results['error']}[/bold red]"
        )

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
