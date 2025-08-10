#!/usr/bin/env python3
"""
Race Cards Analysis Tool
Examines the racecards table to understand upcoming races and betting data
"""

import sys
from datetime import datetime, timedelta

import pandas as pd
import psycopg2


def connect_to_database():
    """Connect to PostgreSQL database with correct credentials"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def analyze_racecards(conn):
    """Comprehensive analysis of racecard_details data"""

    print("🏇 RACE CARDS ANALYSIS")
    print("=" * 60)

    # 1. Basic table structure
    print("\n📋 TABLE STRUCTURE:")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'racecard_details' 
        ORDER BY ordinal_position;
    """
    )
    columns = cursor.fetchall()
    for col_name, data_type, nullable in columns:
        print(
            f"  • {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})"
        )

    # 2. Total records
    cursor.execute("SELECT COUNT(*) FROM racecard_details;")
    total_records = cursor.fetchone()[0]
    print(f"\n📊 TOTAL RACE CARDS: {total_records:,}")

    # 3. Date range analysis
    print("\n📅 DATE RANGE ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            MIN(race_date) as earliest_race,
            MAX(race_date) as latest_race,
            COUNT(DISTINCT race_date) as unique_dates
        FROM racecard_details;
    """
    )
    date_stats = cursor.fetchone()
    print(f"  • Earliest Race: {date_stats[0]}")
    print(f"  • Latest Race: {date_stats[1]}")
    print(f"  • Unique Race Days: {date_stats[2]}")

    # 4. Track/Course analysis
    print("\n🏟️ TRACK/COURSE ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            course_name,
            COUNT(*) as race_count,
            COUNT(DISTINCT race_date) as race_days
        FROM racecard_details 
        WHERE course_name IS NOT NULL
        GROUP BY course_name 
        ORDER BY race_count DESC 
        LIMIT 10;
    """
    )
    tracks = cursor.fetchall()
    print("  Top 10 Tracks by Race Count:")
    for track, count, days in tracks:
        print(f"    • {track}: {count} races ({days} days)")

    # 5. Race type/class analysis
    print("\n🏆 RACE CLASS ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            race_class,
            COUNT(*) as count,
            ROUND(AVG(CAST(prize_money AS NUMERIC)), 2) as avg_prize
        FROM racecard_details 
        WHERE race_class IS NOT NULL
        GROUP BY race_class 
        ORDER BY count DESC;
    """
    )
    classes = cursor.fetchall()
    for race_class, count, avg_prize in classes:
        prize_str = f"£{avg_prize:,.2f}" if avg_prize else "N/A"
        print(f"  • {race_class}: {count} races (Avg Prize: {prize_str})")

    # 6. Distance analysis
    print("\n📏 DISTANCE ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            distance,
            COUNT(*) as race_count
        FROM racecard_details 
        WHERE distance IS NOT NULL
        GROUP BY distance 
        ORDER BY race_count DESC 
        LIMIT 10;
    """
    )
    distances = cursor.fetchall()
    print("  Most Common Distances:")
    for distance, count in distances:
        print(f"    • {distance}: {count} races")

    # 7. Prize money analysis
    print("\n💰 PRIZE MONEY ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_races,
            COUNT(CASE WHEN prize_money IS NOT NULL THEN 1 END) as races_with_prize,
            MIN(CAST(prize_money AS NUMERIC)) as min_prize,
            MAX(CAST(prize_money AS NUMERIC)) as max_prize,
            ROUND(AVG(CAST(prize_money AS NUMERIC)), 2) as avg_prize
        FROM racecard_details 
        WHERE prize_money ~ '^[0-9]+\\.?[0-9]*$';
    """
    )
    prize_stats = cursor.fetchone()
    total, with_prize, min_prize, max_prize, avg_prize = prize_stats
    print(f"  • Total Races: {total}")
    print(f"  • Races with Prize Data: {with_prize}")
    if min_prize and max_prize and avg_prize:
        print(f"  • Prize Range: £{min_prize:,.2f} - £{max_prize:,.2f}")
        print(f"  • Average Prize: £{avg_prize:,.2f}")

    # 8. Recent races sample
    print("\n🕐 RECENT RACE CARDS SAMPLE:")
    cursor.execute(
        """
        SELECT 
            race_date,
            race_time,
            course_name,
            race_title,
            distance,
            race_class,
            prize_money
        FROM racecard_details 
        WHERE race_date IS NOT NULL
        ORDER BY race_date DESC, race_time DESC 
        LIMIT 10;
    """
    )
    recent_races = cursor.fetchall()
    print("  Latest 10 Race Cards:")
    for race in recent_races:
        date, time, course, title, distance, class_name, prize = race
        time_str = time.strftime("%H:%M") if time else "TBA"
        title_short = (
            title[:40] + "..." if title and len(title) > 40 else title or "N/A"
        )
        print(f"    • {date} {time_str} | {course} | {title_short}")
        print(
            f"      Distance: {distance or 'N/A'} | Class: {class_name or 'N/A'} | Prize: £{prize or 'N/A'}"
        )

    # 9. Betting odds analysis (if available)
    print("\n📊 BETTING DATA ANALYSIS:")
    cursor.execute(
        """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'racecard_details' 
        AND column_name LIKE '%odds%' 
        OR column_name LIKE '%bet%'
        OR column_name LIKE '%favorite%'
        OR column_name LIKE '%price%';
    """
    )
    betting_columns = [row[0] for row in cursor.fetchall()]

    if betting_columns:
        print(f"  Betting columns found: {', '.join(betting_columns)}")
        # Sample betting data
        for col in betting_columns[:3]:  # Limit to first 3 betting columns
            cursor.execute(
                f"""
                SELECT {col}, COUNT(*) 
                FROM racecard_details 
                WHERE {col} IS NOT NULL 
                GROUP BY {col} 
                ORDER BY COUNT(*) DESC 
                LIMIT 5;
            """
            )
            betting_data = cursor.fetchall()
            if betting_data:
                print(f"  • {col} (top 5 values):")
                for value, count in betting_data:
                    print(f"    - {value}: {count} occurrences")
    else:
        print("  • No obvious betting columns found")

    # 10. Data quality summary
    print("\n✅ DATA QUALITY SUMMARY:")
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN race_date IS NOT NULL THEN 1 END) as has_date,
            COUNT(CASE WHEN course_name IS NOT NULL THEN 1 END) as has_course,
            COUNT(CASE WHEN race_title IS NOT NULL THEN 1 END) as has_title,
            COUNT(CASE WHEN distance IS NOT NULL THEN 1 END) as has_distance,
            COUNT(CASE WHEN race_class IS NOT NULL THEN 1 END) as has_class
        FROM racecard_details;
    """
    )
    quality = cursor.fetchone()
    total = quality[0]

    print(f"  • Total Records: {total:,}")
    print(f"  • Date Coverage: {quality[1]:,} ({quality[1]/total*100:.1f}%)")
    print(f"  • Course Coverage: {quality[2]:,} ({quality[2]/total*100:.1f}%)")
    print(f"  • Title Coverage: {quality[3]:,} ({quality[3]/total*100:.1f}%)")
    print(f"  • Distance Coverage: {quality[4]:,} ({quality[4]/total*100:.1f}%)")
    print(f"  • Class Coverage: {quality[5]:,} ({quality[5]/total*100:.1f}%)")


def main():
    """Main execution function"""
    print("🏇 Starting Race Cards Analysis...")

    # Connect to database
    conn = connect_to_database()
    if not conn:
        sys.exit(1)

    try:
        # Run analysis
        analyze_racecards(conn)

        print("\n" + "=" * 60)
        print("✅ Race Cards Analysis Complete!")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
