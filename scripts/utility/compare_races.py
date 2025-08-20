#!/usr/bin/env python3
"""
Compare two races.csv files
"""

import csv
import pandas as pd


def compare_race_files():
    print("🔍 COMPARISON: races.csv files")
    print("=" * 60)

    cards_file = "/home/jc/Documents/Horse-race-ai-v2.03/data/preprocessed/cards_data/races/races.csv"
    results_file = "/home/jc/Documents/Horse-race-ai-v2.03/data/preprocessed/results_data/races/races.csv"

    # Load both files
    try:
        cards_df = pd.read_csv(cards_file)
        results_df = pd.read_csv(results_file)

        print(f"📊 FILE SIZES:")
        print(f"   Cards Data:   {len(cards_df)} races")
        print(f"   Results Data: {len(results_df)} races")
        print(
            f"   Difference:   {len(results_df) - len(cards_df)} more races in results"
        )
        print()

        print(f"📋 COLUMN COMPARISON:")
        cards_cols = set(cards_df.columns)
        results_cols = set(results_df.columns)

        if cards_cols == results_cols:
            print("   ✅ Both files have identical column structure")
            print(f"   📝 Columns: {list(cards_df.columns)}")
        else:
            print("   ❌ Column structures differ")
            print(f"   Cards only:   {cards_cols - results_cols}")
            print(f"   Results only: {results_cols - cards_cols}")
        print()

        print(f"🏁 RACE COVERAGE:")

        # Get unique courses
        cards_courses = set(cards_df["Course"].unique())
        results_courses = set(results_df["Course"].unique())

        print(f"   Cards courses:   {sorted(cards_courses)}")
        print(f"   Results courses: {sorted(results_courses)}")

        common_courses = cards_courses & results_courses
        cards_only = cards_courses - results_courses
        results_only = results_courses - cards_courses

        if common_courses:
            print(f"   ✅ Common:       {sorted(common_courses)}")
        if cards_only:
            print(f"   📋 Cards only:   {sorted(cards_only)}")
        if results_only:
            print(f"   🏆 Results only: {sorted(results_only)}")
        print()

        print(f"🆔 RACE ID RANGES:")
        cards_ids = cards_df["Race_ID"].tolist()
        results_ids = results_df["Race_ID"].tolist()

        print(f"   Cards:   {min(cards_ids)} - {max(cards_ids)}")
        print(f"   Results: {min(results_ids)} - {max(results_ids)}")

        # Check for overlap
        common_ids = set(cards_ids) & set(results_ids)
        cards_unique = set(cards_ids) - set(results_ids)
        results_unique = set(results_ids) - set(cards_ids)

        print(f"   Common races:      {len(common_ids)}")
        print(f"   Cards unique:      {len(cards_unique)}")
        print(f"   Results unique:    {len(results_unique)}")
        print()

        print(f"⏰ TIME ANALYSIS:")

        # Check race times
        if "race_time" in cards_df.columns:
            cards_times = sorted(cards_df["race_time"].dropna().unique())
            results_times = sorted(results_df["race_time"].dropna().unique())

            print(
                f"   Cards time range:   {cards_times[0] if cards_times else 'N/A'} - {cards_times[-1] if cards_times else 'N/A'}"
            )
            print(
                f"   Results time range: {results_times[0] if results_times else 'N/A'} - {results_times[-1] if results_times else 'N/A'}"
            )
        print()

        print(f"📈 DATA COMPLETENESS:")

        # Check for missing data in key columns
        key_columns = ["Course", "Race_name", "race_time", "Distance"]

        print("   Missing data comparison:")
        for col in key_columns:
            if col in cards_df.columns and col in results_df.columns:
                cards_missing = cards_df[col].isna().sum()
                results_missing = results_df[col].isna().sum()
                print(
                    f"     {col:12}: Cards={cards_missing:2d}, Results={results_missing:2d}"
                )
        print()

        print(f"🎯 KEY INSIGHTS:")

        if len(results_df) > len(cards_df):
            print(
                f"   • Results file has {len(results_df) - len(cards_df)} more races than cards"
            )
            print("   • This suggests results data contains additional/completed races")

        if results_only:
            print(
                f"   • Results file contains courses not in cards: {sorted(results_only)}"
            )
            print("   • These might be completed races vs. upcoming race cards")

        if cards_only:
            print(
                f"   • Cards file contains courses not in results: {sorted(cards_only)}"
            )
            print("   • These might be upcoming races without results yet")

        # Show some example differences
        if results_unique:
            print(f"\n📋 SAMPLE RESULTS-ONLY RACES:")
            sample_results = results_df[
                results_df["Race_ID"].isin(list(results_unique)[:5])
            ]
            for _, race in sample_results.iterrows():
                print(
                    f"   🏁 {race['Race_ID']}: {race['Race_name']} at {race['Course']} ({race['race_time']})"
                )

        if cards_unique:
            print(f"\n📋 SAMPLE CARDS-ONLY RACES:")
            sample_cards = cards_df[cards_df["Race_ID"].isin(list(cards_unique)[:5])]
            for _, race in sample_cards.iterrows():
                print(
                    f"   🏁 {race['Race_ID']}: {race['Race_name']} at {race['Course']} ({race['race_time']})"
                )

    except Exception as e:
        print(f"❌ Error comparing files: {e}")


if __name__ == "__main__":
    compare_race_files()
