#!/usr/bin/env python3
"""
Enhanced CSV Data Comparison Tool
=================================

Advanced comparison tool for race data that provides detailed insights into:
- What data is the same vs different between race cards and results
- Content overlap analysis by various keys (horse names, race IDs, etc.)
- Data freshness and update patterns
- Specific differences in race information
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd


class EnhancedCSVComparator:
    """Enhanced CSV data comparison with detailed race data analysis"""

    def __init__(self, data_dir: str = "data/daily_downloads"):
        self.data_dir = Path(data_dir)
        self.results_dir = self.data_dir / "results_data"
        self.cards_dir = self.data_dir / "cards_data"
        self.today = datetime.now().date()

        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "detailed_comparisons": {},
            "race_analysis": {},
            "horse_analysis": {},
            "data_insights": [],
        }

    def run_detailed_analysis(self) -> Dict:
        """Run comprehensive data analysis"""
        print(f"\n🏇 Enhanced Race Data Analysis - {self.today}")
        print("=" * 60)

        # 1. Analyze race files
        self._analyze_race_data()

        # 2. Analyze horse data
        self._analyze_horse_data()

        # 3. Cross-reference analysis
        self._cross_reference_analysis()

        # 4. Generate insights
        self._generate_detailed_insights()

        # 5. Save detailed report
        self._save_enhanced_report()

        return self.analysis_results

    def _analyze_race_data(self):
        """Detailed analysis of race data differences"""
        print("\n📊 Analyzing Race Data...")

        results_race_file = self.results_dir / "races" / "races.csv"
        cards_race_file = self.cards_dir / "races" / "races.csv"

        if not (results_race_file.exists() and cards_race_file.exists()):
            print("❌ Race files not found")
            return

        # Load race data
        df_results = pd.read_csv(results_race_file)
        df_cards = pd.read_csv(cards_race_file)

        print(f"   Results races: {len(df_results)} | Cards races: {len(df_cards)}")

        # Compare by Race_ID
        results_race_ids = set(df_results["Race_ID"].astype(str))
        cards_race_ids = set(df_cards["Race_ID"].astype(str))

        common_races = results_race_ids & cards_race_ids
        results_only = results_race_ids - cards_race_ids
        cards_only = cards_race_ids - results_race_ids

        print(f"   Common races: {len(common_races)}")
        print(f"   Results only: {len(results_only)}")
        print(f"   Cards only: {len(cards_only)}")

        # Analyze differences in common races
        race_differences = []
        if common_races:
            print("\n   🔍 Analyzing differences in common races...")

            for race_id in list(common_races)[:5]:  # Check first 5
                results_race = df_results[df_results["Race_ID"] == int(race_id)].iloc[0]
                cards_race = df_cards[df_cards["Race_ID"] == int(race_id)].iloc[0]

                differences = self._compare_race_records(
                    results_race, cards_race, race_id
                )
                if differences:
                    race_differences.append(differences)

        self.analysis_results["race_analysis"] = {
            "total_results_races": len(df_results),
            "total_cards_races": len(df_cards),
            "common_race_ids": len(common_races),
            "results_only_races": len(results_only),
            "cards_only_races": len(cards_only),
            "sample_common_races": list(common_races)[:10],
            "sample_results_only": list(results_only)[:5],
            "sample_cards_only": list(cards_only)[:5],
            "race_differences": race_differences[:3],  # First 3 differences
        }

    def _compare_race_records(self, results_race, cards_race, race_id: str) -> Dict:
        """Compare two race records and find differences"""
        differences = {"race_id": race_id, "field_differences": []}

        # Key fields to compare
        key_fields = [
            "Runners_racecard",
            "Runners",
            "EW_racecard",
            "EW",
            "Places_EW_racecard",
            "Places_EW",
        ]

        for field in key_fields:
            if field in results_race.index and field in cards_race.index:
                results_val = results_race[field]
                cards_val = cards_race[field]

                if str(results_val) != str(cards_val):
                    differences["field_differences"].append(
                        {
                            "field": field,
                            "results_value": str(results_val),
                            "cards_value": str(cards_val),
                        }
                    )

        return differences if differences["field_differences"] else None

    def _analyze_horse_data(self):
        """Detailed analysis of horse data"""
        print("\n🐎 Analyzing Horse Data...")

        results_horse_file = self.results_dir / "horses" / "horses.csv"
        cards_horse_file = self.cards_dir / "horses" / "horses.csv"

        if not (results_horse_file.exists() and cards_horse_file.exists()):
            print("❌ Horse files not found")
            return

        # Load horse data
        df_results = pd.read_csv(results_horse_file)
        df_cards = pd.read_csv(cards_horse_file)

        print(f"   Results horses: {len(df_results)} | Cards horses: {len(df_cards)}")

        # Compare by horse ID
        results_horse_ids = set(df_results["id"].astype(str))
        cards_horse_ids = set(df_cards["id"].astype(str))

        common_horse_ids = results_horse_ids & cards_horse_ids

        # Compare by horse name (more meaningful for racing)
        results_horse_names = set(df_results["name"].str.strip().str.upper())
        cards_horse_names = set(df_cards["name"].str.strip().str.upper())

        common_horse_names = results_horse_names & cards_horse_names
        results_only_names = results_horse_names - cards_horse_names
        cards_only_names = cards_horse_names - results_horse_names

        print(f"   Common horse IDs: {len(common_horse_ids)}")
        print(f"   Common horse names: {len(common_horse_names)}")
        print(f"   Results only names: {len(results_only_names)}")
        print(f"   Cards only names: {len(cards_only_names)}")

        # Analyze last race dates
        results_last_races = df_results["date_last_race"].value_counts().head()
        cards_last_races = df_cards["date_last_race"].value_counts().head()

        print(
            f"\n   🗓️ Most recent race dates in results: {list(results_last_races.index)[:3]}"
        )
        print(
            f"   🗓️ Most recent race dates in cards: {list(cards_last_races.index)[:3]}"
        )

        # Sample horses for detailed comparison
        sample_comparisons = []
        for horse_name in list(common_horse_names)[:3]:
            results_horse = df_results[
                df_results["name"].str.upper() == horse_name
            ].iloc[0]
            cards_horse = df_cards[df_cards["name"].str.upper() == horse_name].iloc[0]

            comparison = self._compare_horse_records(
                results_horse, cards_horse, horse_name
            )
            sample_comparisons.append(comparison)

        self.analysis_results["horse_analysis"] = {
            "total_results_horses": len(df_results),
            "total_cards_horses": len(df_cards),
            "common_horse_ids": len(common_horse_ids),
            "common_horse_names": len(common_horse_names),
            "results_only_names": len(results_only_names),
            "cards_only_names": len(cards_only_names),
            "results_date_distribution": dict(results_last_races.head()),
            "cards_date_distribution": dict(cards_last_races.head()),
            "sample_horse_comparisons": sample_comparisons,
            "name_overlap_percentage": (
                (
                    len(common_horse_names)
                    / len(results_horse_names | cards_horse_names)
                    * 100
                )
                if (results_horse_names | cards_horse_names)
                else 0
            ),
        }

    def _compare_horse_records(
        self, results_horse, cards_horse, horse_name: str
    ) -> Dict:
        """Compare two horse records"""
        comparison = {
            "horse_name": horse_name,
            "results_id": str(results_horse["id"]),
            "cards_id": str(cards_horse["id"]),
            "differences": [],
        }

        # Key fields to compare
        key_fields = [
            "uptodate",
            "state",
            "race_id_last_race",
            "date_last_race",
            "Total_races",
            "Wins",
        ]

        for field in key_fields:
            if field in results_horse.index and field in cards_horse.index:
                results_val = results_horse[field]
                cards_val = cards_horse[field]

                if str(results_val) != str(cards_val):
                    comparison["differences"].append(
                        {
                            "field": field,
                            "results_value": str(results_val),
                            "cards_value": str(cards_val),
                        }
                    )

        return comparison

    def _cross_reference_analysis(self):
        """Cross-reference races and horses to understand data relationships"""
        print("\n🔗 Cross-Reference Analysis...")

        # Load both race files to get race IDs
        results_race_file = self.results_dir / "races" / "races.csv"
        cards_race_file = self.cards_dir / "races" / "races.csv"

        if not (results_race_file.exists() and cards_race_file.exists()):
            return

        df_results_races = pd.read_csv(results_race_file)
        df_cards_races = pd.read_csv(cards_race_file)

        # Get today's race IDs from cards (these are the races happening today)
        todays_race_ids = set(df_cards_races["Race_ID"].astype(str))

        # Load horse data
        results_horse_file = self.results_dir / "horses" / "horses.csv"
        cards_horse_file = self.cards_dir / "horses" / "horses.csv"

        if results_horse_file.exists() and cards_horse_file.exists():
            df_results_horses = pd.read_csv(results_horse_file)
            df_cards_horses = pd.read_csv(cards_horse_file)

            # Check which horses in cards data are running in today's races
            cards_horses_in_todays_races = df_cards_horses[
                df_cards_horses["race_id_last_race"].astype(str).isin(todays_race_ids)
            ]

            print(
                f"   Horses in cards running in today's races: {len(cards_horses_in_todays_races)}"
            )

            # Check data freshness
            today_str = self.today.strftime("%Y-%m-%d")
            cards_horses_updated_today = df_cards_horses[
                df_cards_horses["uptodate"] == today_str
            ]
            results_horses_updated_today = df_results_horses[
                df_results_horses["uptodate"] == today_str
            ]

            print(f"   Cards horses updated today: {len(cards_horses_updated_today)}")
            print(
                f"   Results horses updated today: {len(results_horses_updated_today)}"
            )

    def _generate_detailed_insights(self):
        """Generate detailed insights from the analysis"""
        print("\n💡 Generating Insights...")

        insights = []
        race_analysis = self.analysis_results.get("race_analysis", {})
        horse_analysis = self.analysis_results.get("horse_analysis", {})

        # Race insights
        if race_analysis:
            total_races = race_analysis.get("total_results_races", 0)
            common_races = race_analysis.get("common_race_ids", 0)

            if common_races == total_races and total_races > 0:
                insights.append(
                    "🎯 All races are present in both files - complete data consistency"
                )
            elif common_races > 0:
                insights.append(
                    f"📊 {common_races}/{total_races} races are common between files"
                )

                if race_analysis.get("race_differences"):
                    insights.append(
                        "⚠️ Some race details differ between files (likely results updates)"
                    )
                else:
                    insights.append("✅ Common races have identical details")

        # Horse insights
        if horse_analysis:
            name_overlap = horse_analysis.get("name_overlap_percentage", 0)

            if name_overlap >= 80:
                insights.append(
                    f"🐎 High horse overlap ({name_overlap:.1f}%) - mostly same horses"
                )
            elif name_overlap >= 50:
                insights.append(
                    f"🐎 Moderate horse overlap ({name_overlap:.1f}%) - some different horses"
                )
            elif name_overlap >= 20:
                insights.append(
                    f"🐎 Low horse overlap ({name_overlap:.1f}%) - mostly different horses"
                )
            else:
                insights.append(
                    f"🐎 Minimal horse overlap ({name_overlap:.1f}%) - almost entirely different horses"
                )

            # Date analysis
            results_dates = horse_analysis.get("results_date_distribution", {})
            cards_dates = horse_analysis.get("cards_date_distribution", {})

            if results_dates and cards_dates:
                latest_results = (
                    max(results_dates.keys()) if results_dates else "Unknown"
                )
                latest_cards = max(cards_dates.keys()) if cards_dates else "Unknown"

                insights.append(
                    f"📅 Latest data - Results: {latest_results}, Cards: {latest_cards}"
                )

        # Data purpose insights
        if horse_analysis.get("cards_only_names", 0) > horse_analysis.get(
            "results_only_names", 0
        ):
            insights.append(
                "📋 Cards data contains more unique horses - likely today's runners"
            )
        elif horse_analysis.get("results_only_names", 0) > horse_analysis.get(
            "cards_only_names", 0
        ):
            insights.append(
                "📈 Results data contains more unique horses - historical race data"
            )

        self.analysis_results["data_insights"] = insights

        print("\n🎯 Key Insights:")
        for insight in insights:
            print(f"   {insight}")

    def _save_enhanced_report(self):
        """Save detailed analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create summary
        self.analysis_results["summary"] = {
            "analysis_date": self.today.isoformat(),
            "analysis_time": datetime.now().strftime("%H:%M:%S"),
            "total_insights": len(self.analysis_results["data_insights"]),
            "race_files_analyzed": bool(self.analysis_results.get("race_analysis")),
            "horse_files_analyzed": bool(self.analysis_results.get("horse_analysis")),
        }

        # Save JSON report
        json_file = self.data_dir / f"detailed_comparison_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.analysis_results, f, indent=2, default=str)

        # Save human-readable report
        txt_file = self.data_dir / f"detailed_comparison_{timestamp}.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("DETAILED CSV DATA COMPARISON REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {self.today}\n")
            f.write(f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n")

            # Race analysis
            if self.analysis_results.get("race_analysis"):
                f.write("RACE DATA ANALYSIS:\n")
                race_data = self.analysis_results["race_analysis"]
                f.write(
                    f"  Total Results Races: {race_data.get('total_results_races', 0)}\n"
                )
                f.write(
                    f"  Total Cards Races: {race_data.get('total_cards_races', 0)}\n"
                )
                f.write(f"  Common Race IDs: {race_data.get('common_race_ids', 0)}\n")
                f.write(f"  Results Only: {race_data.get('results_only_races', 0)}\n")
                f.write(f"  Cards Only: {race_data.get('cards_only_races', 0)}\n\n")

            # Horse analysis
            if self.analysis_results.get("horse_analysis"):
                f.write("HORSE DATA ANALYSIS:\n")
                horse_data = self.analysis_results["horse_analysis"]
                f.write(
                    f"  Total Results Horses: {horse_data.get('total_results_horses', 0)}\n"
                )
                f.write(
                    f"  Total Cards Horses: {horse_data.get('total_cards_horses', 0)}\n"
                )
                f.write(
                    f"  Common Horse Names: {horse_data.get('common_horse_names', 0)}\n"
                )
                f.write(
                    f"  Name Overlap: {horse_data.get('name_overlap_percentage', 0):.1f}%\n\n"
                )

            # Insights
            f.write("KEY INSIGHTS:\n")
            for insight in self.analysis_results.get("data_insights", []):
                f.write(f"  {insight}\n")

        print(f"\n💾 Detailed reports saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📄 Summary: {txt_file}")


def main():
    """Run the enhanced CSV comparison tool"""
    print("🚀 Enhanced CSV Data Comparison Tool")

    comparator = EnhancedCSVComparator()
    results = comparator.run_detailed_analysis()

    print("\n🎉 Enhanced analysis complete!")
    return results


if __name__ == "__main__":
    main()
