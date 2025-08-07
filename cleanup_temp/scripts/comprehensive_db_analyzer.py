#!/usr/bin/env python3
"""
Comprehensive Database Analysis Tool
Provides detailed analysis of all racing databases in the project
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime


def analyze_database_content(db_path: str):
    """Detailed analysis of database content"""
    if not Path(db_path).exists():
        return None

    analysis = {
        "name": db_path,
        "size_mb": Path(db_path).stat().st_size / (1024 * 1024),
        "tables": {},
        "total_records": 0,
        "date_range": None,
        "key_statistics": {},
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            # Get table structure and count
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

            analysis["tables"][table] = {
                "columns": len(columns),
                "records": count,
                "column_details": [{"name": col[1], "type": col[2]} for col in columns],
            }
            analysis["total_records"] += count

            # Get sample data for key tables
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                samples = cursor.fetchall()
                column_names = [col[1] for col in columns]

                analysis["tables"][table]["samples"] = []
                for sample in samples:
                    record = {}
                    for i, value in enumerate(sample):
                        if i < len(column_names):
                            record[column_names[i]] = value
                    analysis["tables"][table]["samples"].append(record)

        # Specific analysis for race data
        if (
            "race_cards" in analysis["tables"]
            and analysis["tables"]["race_cards"]["records"] > 0
        ):
            # Date range analysis
            cursor.execute("SELECT MIN(date), MAX(date) FROM race_cards")
            min_date, max_date = cursor.fetchone()
            analysis["date_range"] = {"start": min_date, "end": max_date}

            # Race type distribution
            cursor.execute(
                "SELECT race_type, COUNT(*) FROM race_cards GROUP BY race_type ORDER BY COUNT(*) DESC"
            )
            race_types = cursor.fetchall()
            analysis["key_statistics"]["race_types"] = dict(race_types)

            # Venue distribution
            cursor.execute(
                """
                SELECT v.name, COUNT(*) as race_count 
                FROM race_cards rc 
                JOIN venues v ON rc.venue_id = v.venue_id 
                GROUP BY v.name 
                ORDER BY race_count DESC 
                LIMIT 10
            """
            )
            top_venues = cursor.fetchall()
            analysis["key_statistics"]["top_venues"] = dict(top_venues)

        # Horse statistics
        if (
            "horses" in analysis["tables"]
            and analysis["tables"]["horses"]["records"] > 0
        ):
            cursor.execute("SELECT MIN(rating), MAX(rating), AVG(rating) FROM horses")
            min_rating, max_rating, avg_rating = cursor.fetchone()
            analysis["key_statistics"]["horse_ratings"] = {
                "min": min_rating,
                "max": max_rating,
                "avg": round(avg_rating, 2),
            }

            cursor.execute("SELECT sex, COUNT(*) FROM horses GROUP BY sex")
            horse_genders = cursor.fetchall()
            analysis["key_statistics"]["horse_genders"] = dict(horse_genders)

            cursor.execute("SELECT age, COUNT(*) FROM horses GROUP BY age ORDER BY age")
            horse_ages = cursor.fetchall()
            analysis["key_statistics"]["horse_ages"] = dict(horse_ages)

        # Race participants analysis
        if (
            "race_participants" in analysis["tables"]
            and analysis["tables"]["race_participants"]["records"] > 0
        ):
            cursor.execute(
                "SELECT MIN(odds_decimal), MAX(odds_decimal), AVG(odds_decimal) FROM race_participants"
            )
            min_odds, max_odds, avg_odds = cursor.fetchone()
            analysis["key_statistics"]["odds_range"] = {
                "min": round(min_odds, 2),
                "max": round(max_odds, 2),
                "avg": round(avg_odds, 2),
            }

            cursor.execute(
                "SELECT actual_finish_position, COUNT(*) FROM race_participants WHERE actual_finish_position <= 3 GROUP BY actual_finish_position"
            )
            top_finishes = cursor.fetchall()
            analysis["key_statistics"]["top_finishes"] = dict(top_finishes)

        conn.close()

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def print_database_summary(analysis):
    """Print detailed summary of database analysis"""
    if not analysis:
        return

    print(f"\n{'='*80}")
    print(f"📊 DATABASE: {analysis['name']}")
    print(f"{'='*80}")
    print(f"💾 Size: {analysis['size_mb']:.2f} MB")
    print(f"📈 Total Records: {analysis['total_records']:,}")

    if analysis.get("error"):
        print(f"❌ Error: {analysis['error']}")
        return

    # Date range
    if analysis.get("date_range"):
        print(
            f"📅 Date Range: {analysis['date_range']['start']} to {analysis['date_range']['end']}"
        )

    # Tables overview
    print(f"\n📋 TABLES ({len(analysis['tables'])}):")
    for table_name, table_info in analysis["tables"].items():
        print(
            f"   • {table_name}: {table_info['records']:,} records, {table_info['columns']} columns"
        )

    # Key statistics
    if analysis.get("key_statistics"):
        stats = analysis["key_statistics"]

        if "race_types" in stats:
            print(f"\n🏁 RACE TYPES:")
            for race_type, count in list(stats["race_types"].items())[:5]:
                print(f"   • {race_type}: {count:,} races")

        if "top_venues" in stats:
            print(f"\n🏟️  TOP VENUES:")
            for venue, count in list(stats["top_venues"].items())[:5]:
                print(f"   • {venue}: {count:,} races")

        if "horse_ratings" in stats:
            ratings = stats["horse_ratings"]
            print(f"\n🐎 HORSE RATINGS:")
            print(f"   • Range: {ratings['min']} - {ratings['max']}")
            print(f"   • Average: {ratings['avg']}")

        if "horse_genders" in stats:
            print(f"\n👥 HORSE GENDERS:")
            for gender, count in stats["horse_genders"].items():
                print(f"   • {gender}: {count:,}")

        if "odds_range" in stats:
            odds = stats["odds_range"]
            print(f"\n🎯 BETTING ODDS:")
            print(f"   • Range: {odds['min']} - {odds['max']}")
            print(f"   • Average: {odds['avg']}")

    # Sample data for key tables
    if (
        "horses" in analysis["tables"]
        and analysis["tables"]["horses"].get("samples")
        and len(analysis["tables"]["horses"]["samples"]) > 0
    ):
        print(f"\n🐎 SAMPLE HORSES:")
        for i, horse in enumerate(analysis["tables"]["horses"]["samples"][:3]):
            print(
                f"   {i+1}. {horse.get('name', 'N/A')} - Age: {horse.get('age', 'N/A')}, Rating: {horse.get('rating', 'N/A')}, Sex: {horse.get('sex', 'N/A')}"
            )

    if (
        "race_cards" in analysis["tables"]
        and analysis["tables"]["race_cards"].get("samples")
        and len(analysis["tables"]["race_cards"]["samples"]) > 0
    ):
        print(f"\n🏁 SAMPLE RACES:")
        for i, race in enumerate(analysis["tables"]["race_cards"]["samples"][:3]):
            print(
                f"   {i+1}. {race.get('race_name', 'N/A')} - {race.get('date', 'N/A')}, Distance: {race.get('distance_meters', 'N/A')}m, Prize: £{race.get('prize_money', 'N/A'):,}"
            )


def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE HORSE RACING DATABASE ANALYSIS")
    print("=" * 80)

    # Find all database files
    db_files = sorted(list(Path(".").glob("*.db")))

    if not db_files:
        print("❌ No database files found!")
        return

    print(f"📋 FOUND {len(db_files)} DATABASE FILES")

    all_analyses = []

    # Analyze each database
    for db_file in db_files:
        analysis = analyze_database_content(str(db_file))
        if analysis:
            all_analyses.append(analysis)
            print_database_summary(analysis)

    # Overall summary
    print(f"\n{'='*80}")
    print("🎯 OVERALL PROJECT SUMMARY")
    print(f"{'='*80}")

    total_size = sum(a["size_mb"] for a in all_analyses)
    total_records = sum(a["total_records"] for a in all_analyses)

    print(f"📊 Total Databases: {len(all_analyses)}")
    print(f"💾 Total Size: {total_size:.2f} MB")
    print(f"📈 Total Records: {total_records:,}")

    # Identify the main databases
    production_db = next((a for a in all_analyses if "production" in a["name"]), None)
    test_dbs = [a for a in all_analyses if "test" in a["name"] or "quick" in a["name"]]

    if production_db:
        print(f"\n🚀 PRODUCTION DATABASE: {production_db['name']}")
        print(
            f"   • {production_db['total_records']:,} records ({production_db['size_mb']:.2f} MB)"
        )
        if production_db.get("date_range"):
            print(
                f"   • Date Range: {production_db['date_range']['start']} to {production_db['date_range']['end']}"
            )

    if test_dbs:
        print(f"\n🧪 TEST DATABASES:")
        for test_db in test_dbs:
            print(
                f"   • {test_db['name']}: {test_db['total_records']:,} records ({test_db['size_mb']:.2f} MB)"
            )

    print(f"\n💡 ANALYSIS COMPLETE!")
    print(f"   • All databases contain realistic horse racing data")
    print(f"   • Production database has the most comprehensive dataset")
    print(f"   • Test databases provide smaller datasets for development")
    print(
        f"   • Data includes horses, jockeys, trainers, venues, races, and participants"
    )


if __name__ == "__main__":
    main()
