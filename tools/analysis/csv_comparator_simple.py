#!/usr/bin/env python3
"""
Simple CSV Data Comparison Tool
===============================

Compares race cards vs results data in daily downloads folder.
Identifies what's the same and what's different between files.
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


class SimpleCSVComparator:
    """Simple CSV data comparison tool"""

    def __init__(self, data_dir: str = "data/daily_downloads"):
        self.data_dir = Path(data_dir)
        self.results_dir = self.data_dir / "results_data"
        self.cards_dir = self.data_dir / "cards_data"
        self.today = datetime.now().date()

        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "file_comparisons": {},
            "insights": [],
        }

    def compare_all_files(self) -> Dict:
        """Compare all CSV files between results and cards directories"""
        print(f"\n🔍 CSV Data Comparison - {self.today}")
        print(f"📁 Comparing: {self.results_dir} vs {self.cards_dir}")

        # Find matching files
        file_pairs = self._find_file_pairs()

        if not file_pairs:
            print("❌ No matching files found to compare")
            return self.results

        print(f"✅ Found {len(file_pairs)} file pairs to compare")

        # Compare each pair
        for file_type, (file1, file2) in file_pairs.items():
            print(f"\n📊 Comparing {file_type}...")
            comparison = self._compare_files(file1, file2, file_type)
            self.results["file_comparisons"][file_type] = comparison

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

        return self.results

    def _find_file_pairs(self) -> Dict[str, Tuple[Path, Path]]:
        """Find matching CSV files between directories"""
        file_pairs = {}

        # Common file patterns to look for
        patterns = [
            "races.csv",
            "records.csv",
            "horses.csv",
            "jockeys_stats.csv",
            "trainers_stats.csv",
            "racecard_details.csv",
        ]

        for pattern in patterns:
            # Find files matching pattern in both directories
            results_files = list(self.results_dir.rglob(pattern))
            cards_files = list(self.cards_dir.rglob(pattern))

            if results_files and cards_files:
                # Use the first match from each directory
                file_type = pattern.replace(".csv", "")
                file_pairs[file_type] = (results_files[0], cards_files[0])
                print(f"  ✅ {file_type}: Found pair")
            elif results_files:
                print(f"  ⚠️ {pattern}: Only in results")
            elif cards_files:
                print(f"  ⚠️ {pattern}: Only in cards")

        return file_pairs

    def _compare_files(self, file1: Path, file2: Path, file_type: str) -> Dict:
        """Compare two CSV files"""
        comparison = {
            "file1": str(file1),
            "file2": str(file2),
            "file1_name": file1.name,
            "file2_name": file2.name,
            "identical": False,
            "schema_match": False,
            "row_counts": {},
            "column_info": {},
            "data_overlap": {},
            "errors": [],
        }

        try:
            # Load CSV files
            print(f"    📖 Loading {file1.name}...")
            df1 = pd.read_csv(file1)
            print(f"    📖 Loading {file2.name}...")
            df2 = pd.read_csv(file2)

            # Basic info
            comparison["row_counts"] = {
                "file1_rows": len(df1),
                "file2_rows": len(df2),
                "difference": abs(len(df1) - len(df2)),
            }

            comparison["column_info"] = {
                "file1_columns": list(df1.columns),
                "file2_columns": list(df2.columns),
                "common_columns": list(set(df1.columns) & set(df2.columns)),
                "file1_only": list(set(df1.columns) - set(df2.columns)),
                "file2_only": list(set(df2.columns) - set(df1.columns)),
            }

            # Schema comparison
            comparison["schema_match"] = list(df1.columns) == list(df2.columns)

            # Data comparison if schemas match
            if comparison["schema_match"]:
                comparison["identical"] = df1.equals(df2)

                # Analyze data overlap if not identical
                if not comparison["identical"]:
                    overlap_info = self._analyze_data_overlap(df1, df2, file_type)
                    comparison["data_overlap"] = overlap_info

            # Display results
            self._display_comparison_result(file_type, comparison)

        except Exception as e:
            error_msg = f"Error comparing files: {str(e)}"
            comparison["errors"].append(error_msg)
            print(f"    ❌ {error_msg}")

        return comparison

    def _analyze_data_overlap(
        self, df1: pd.DataFrame, df2: pd.DataFrame, file_type: str
    ) -> Dict:
        """Analyze data overlap between two dataframes"""
        overlap = {
            "analysis_method": "simple",
            "overlap_percentage": 0,
            "common_records": 0,
            "unique_to_file1": 0,
            "unique_to_file2": 0,
        }

        try:
            # Try to find a key column for comparison
            key_col = None
            possible_keys = ["Race_ID", "Record_ID", "Horse_ID", "Jockey_ID"]

            for possible_key in possible_keys:
                if possible_key in df1.columns and possible_key in df2.columns:
                    key_col = possible_key
                    break

            if key_col:
                # Compare by key column
                keys1 = set(df1[key_col].astype(str))
                keys2 = set(df2[key_col].astype(str))

                common_keys = keys1 & keys2
                unique1 = keys1 - keys2
                unique2 = keys2 - keys1

                total_unique = len(keys1 | keys2)

                overlap.update(
                    {
                        "key_column": key_col,
                        "overlap_percentage": (
                            (len(common_keys) / total_unique * 100)
                            if total_unique > 0
                            else 0
                        ),
                        "common_records": len(common_keys),
                        "unique_to_file1": len(unique1),
                        "unique_to_file2": len(unique2),
                        "sample_common": list(common_keys)[:5],
                        "sample_unique1": list(unique1)[:5],
                        "sample_unique2": list(unique2)[:5],
                    }
                )
            else:
                # Fallback to row-by-row comparison for small files
                if len(df1) <= 100 and len(df2) <= 100:
                    # Convert to string representation for comparison
                    rows1 = set(df1.to_string(index=False).split("\n"))
                    rows2 = set(df2.to_string(index=False).split("\n"))

                    common_rows = rows1 & rows2
                    total_unique = len(rows1 | rows2)

                    overlap.update(
                        {
                            "overlap_percentage": (
                                (len(common_rows) / total_unique * 100)
                                if total_unique > 0
                                else 0
                            ),
                            "common_records": len(common_rows),
                            "unique_to_file1": len(rows1 - rows2),
                            "unique_to_file2": len(rows2 - rows1),
                        }
                    )

        except Exception as e:
            overlap["error"] = str(e)

        return overlap

    def _display_comparison_result(self, file_type: str, comparison: Dict):
        """Display comparison result in a readable format"""
        print(f"    📊 {file_type.upper()} Results:")

        # Schema info
        schema_status = "✅ Match" if comparison["schema_match"] else "❌ Different"
        print(f"      Schema: {schema_status}")

        # Row counts
        rows = comparison["row_counts"]
        print(
            f"      Rows: {rows['file1_rows']} vs {rows['file2_rows']} (diff: {rows['difference']})"
        )

        # Data identical check
        if comparison["schema_match"]:
            identical_status = (
                "✅ Identical" if comparison["identical"] else "❌ Different"
            )
            print(f"      Data: {identical_status}")

            # Show overlap info if not identical
            if not comparison["identical"] and comparison["data_overlap"]:
                overlap = comparison["data_overlap"]
                if "overlap_percentage" in overlap:
                    print(f"      Overlap: {overlap['overlap_percentage']:.1f}%")
                    if "key_column" in overlap:
                        print(f"      Key: {overlap['key_column']}")
                        print(f"      Common: {overlap['common_records']}")
        else:
            # Show column differences
            col_info = comparison["column_info"]
            if col_info["file1_only"]:
                print(
                    f"      Only in {comparison['file1_name']}: {col_info['file1_only']}"
                )
            if col_info["file2_only"]:
                print(
                    f"      Only in {comparison['file2_name']}: {col_info['file2_only']}"
                )

    def _generate_summary(self):
        """Generate overall summary of comparisons"""
        comparisons = self.results["file_comparisons"]

        total_files = len(comparisons)
        identical_files = sum(
            1 for c in comparisons.values() if c.get("identical", False)
        )
        schema_matches = sum(
            1 for c in comparisons.values() if c.get("schema_match", False)
        )

        self.results["summary"] = {
            "total_comparisons": total_files,
            "identical_files": identical_files,
            "schema_matches": schema_matches,
            "analysis_date": self.today.isoformat(),
        }

        # Generate insights
        if identical_files == total_files and total_files > 0:
            self.results["insights"].append(
                "🎯 All files are identical - no differences found"
            )
        elif identical_files > total_files / 2:
            self.results["insights"].append(
                "✅ Most files are identical - good data consistency"
            )
        elif schema_matches == total_files:
            self.results["insights"].append(
                "📋 All schemas match but data differs - check for updates"
            )
        elif schema_matches < total_files / 2:
            self.results["insights"].append(
                "⚠️ Schema mismatches found - data structure differences"
            )
        else:
            self.results["insights"].append(
                "🔍 Mixed results - detailed analysis recommended"
            )

        # Print summary
        print(f"\n📈 SUMMARY")
        print(f"  Total comparisons: {total_files}")
        print(f"  Identical files: {identical_files}")
        print(f"  Schema matches: {schema_matches}")

        print(f"\n💡 INSIGHTS")
        for insight in self.results["insights"]:
            print(f"  {insight}")

    def _save_results(self):
        """Save comparison results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_file = self.data_dir / f"comparison_report_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved: {json_file}")

        # Save simple text summary
        txt_file = self.data_dir / f"comparison_summary_{timestamp}.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(f"CSV Data Comparison Report\n")
            f.write(f"Date: {self.today}\n")
            f.write(f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n")

            f.write("SUMMARY:\n")
            summary = self.results["summary"]
            f.write(f"  Total Comparisons: {summary['total_comparisons']}\n")
            f.write(f"  Identical Files: {summary['identical_files']}\n")
            f.write(f"  Schema Matches: {summary['schema_matches']}\n\n")

            f.write("FILE COMPARISONS:\n")
            for file_type, comparison in self.results["file_comparisons"].items():
                f.write(f"  {file_type.upper()}:\n")
                f.write(
                    f"    Schema Match: {'Yes' if comparison['schema_match'] else 'No'}\n"
                )
                f.write(
                    f"    Data Identical: {'Yes' if comparison['identical'] else 'No'}\n"
                )
                rows = comparison["row_counts"]
                f.write(f"    Rows: {rows['file1_rows']} vs {rows['file2_rows']}\n")
                if (
                    comparison.get("data_overlap")
                    and "overlap_percentage" in comparison["data_overlap"]
                ):
                    overlap_pct = comparison["data_overlap"]["overlap_percentage"]
                    f.write(f"    Data Overlap: {overlap_pct:.1f}%\n")
                f.write("\n")

            f.write("INSIGHTS:\n")
            for insight in self.results["insights"]:
                f.write(f"  {insight}\n")

        print(f"💾 Summary saved: {txt_file}")


def main():
    """Run the CSV comparison tool"""
    print("🚀 Starting CSV Data Comparison Tool")

    comparator = SimpleCSVComparator()
    results = comparator.compare_all_files()

    if results.get("file_comparisons"):
        print("\n🎉 Comparison complete! Check the saved reports for details.")
    else:
        print("\n⚠️ No files were compared. Check your data directories.")

    return results


if __name__ == "__main__":
    main()
