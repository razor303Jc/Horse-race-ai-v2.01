#!/usr/bin/env python3
"""
Race Cards Analysis Tool - Corrected for actual table structure
"""

from datetime import datetime

import psycopg2


def connect_to_database():
    """Connect to PostgreSQL database with correct credentials"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def analyze_race_cards(conn):
    """Comprehensive analysis of race cards data"""

    print("🏇 RACE CARDS COMPREHENSIVE ANALYSIS")
    print("=" * 70)

    cursor = conn.cursor()

    # 1. Analyze racecard_details (individual horse entries)
    print("\n📋 RACECARD DETAILS (Individual Horse Entries):")
    cursor.execute("SELECT COUNT(*) FROM racecard_details;")
    total_entries = cursor.fetchone()[0]
    print(f"  • Total Horse Entries: {total_entries:,}")

    # Sample of horse entries
    print("\n🐎 SAMPLE HORSE ENTRIES:")
    cursor.execute(
        """
        SELECT 
            horse_name,
            jockey_name,
            trainer_name,
            horse_age,
            horse_weight_kg,
            win_odds,
            place_odds,
            form,
            career_wins,
            career_runs
        FROM racecard_details 
        WHERE horse_name IS NOT NULL
        LIMIT 10;
    """
    )
    entries = cursor.fetchall()
    for entry in entries:
        horse, jockey, trainer, age, weight, win_odds, place_odds, form, wins, runs = (
            entry
        )
        win_rate = f"{wins}/{runs}" if wins and runs else "N/A"
        print(f"    • {horse} | Age: {age} | Weight: {weight}kg | Jockey: {jockey}")
        print(
            f"      Odds: Win {win_odds}, Place {place_odds} | Form: {form} | Record: {win_rate}"
        )

    # 2. Age analysis
    print("\n🎂 HORSE AGE ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            horse_age,
            COUNT(*) as count,
            ROUND(AVG(CAST(win_odds AS NUMERIC)), 2) as avg_win_odds
        FROM racecard_details 
        WHERE horse_age IS NOT NULL 
        AND win_odds ~ '^[0-9]+\\.?[0-9]*$'
        GROUP BY horse_age 
        ORDER BY horse_age;
    """
    )
    age_stats = cursor.fetchall()
    for age, count, avg_odds in age_stats:
        print(f"    • Age {age}: {count} horses (Avg Win Odds: {avg_odds})")

    # 3. Weight analysis
    print("\n⚖️ WEIGHT ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            CASE 
                WHEN horse_weight_kg < 55 THEN 'Light (<55kg)'
                WHEN horse_weight_kg BETWEEN 55 AND 60 THEN 'Medium (55-60kg)'
                WHEN horse_weight_kg > 60 THEN 'Heavy (>60kg)'
                ELSE 'Unknown'
            END as weight_category,
            COUNT(*) as count,
            ROUND(AVG(horse_weight_kg), 2) as avg_weight
        FROM racecard_details 
        WHERE horse_weight_kg IS NOT NULL
        GROUP BY weight_category 
        ORDER BY avg_weight;
    """
    )
    weight_stats = cursor.fetchall()
    for category, count, avg_weight in weight_stats:
        print(f"    • {category}: {count} horses (Avg: {avg_weight}kg)")

    # 4. Odds analysis
    print("\n💰 BETTING ODDS ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            CASE 
                WHEN CAST(win_odds AS NUMERIC) < 2.0 THEN 'Favorites (<2.0)'
                WHEN CAST(win_odds AS NUMERIC) BETWEEN 2.0 AND 5.0 THEN 'Short Odds (2.0-5.0)'
                WHEN CAST(win_odds AS NUMERIC) BETWEEN 5.0 AND 10.0 THEN 'Medium Odds (5.0-10.0)'
                WHEN CAST(win_odds AS NUMERIC) > 10.0 THEN 'Long Odds (>10.0)'
                ELSE 'Unknown'
            END as odds_category,
            COUNT(*) as count,
            ROUND(AVG(CAST(win_odds AS NUMERIC)), 2) as avg_odds
        FROM racecard_details 
        WHERE win_odds ~ '^[0-9]+\\.?[0-9]*$'
        GROUP BY odds_category 
        ORDER BY avg_odds;
    """
    )
    odds_stats = cursor.fetchall()
    for category, count, avg_odds in odds_stats:
        print(f"    • {category}: {count} horses (Avg: {avg_odds})")

    # 5. Form analysis
    print("\n📈 FORM ANALYSIS:")
    cursor.execute(
        """
        SELECT 
            form,
            COUNT(*) as count
        FROM racecard_details 
        WHERE form IS NOT NULL AND form != ''
        GROUP BY form 
        ORDER BY count DESC 
        LIMIT 15;
    """
    )
    form_stats = cursor.fetchall()
    print("  Most Common Form Patterns:")
    for form, count in form_stats:
        print(f"    • {form}: {count} horses")

    # 6. Jockey performance
    print("\n🏇 TOP JOCKEYS (by entries):")
    cursor.execute(
        """
        SELECT 
            jockey_name,
            COUNT(*) as entries,
            ROUND(AVG(CAST(win_odds AS NUMERIC)), 2) as avg_odds
        FROM racecard_details 
        WHERE jockey_name IS NOT NULL 
        AND win_odds ~ '^[0-9]+\\.?[0-9]*$'
        GROUP BY jockey_name 
        ORDER BY entries DESC 
        LIMIT 10;
    """
    )
    jockey_stats = cursor.fetchall()
    for jockey, entries, avg_odds in jockey_stats:
        print(f"    • {jockey}: {entries} entries (Avg Odds: {avg_odds})")

    # 7. Trainer performance
    print("\n👨‍🏫 TOP TRAINERS (by entries):")
    cursor.execute(
        """
        SELECT 
            trainer_name,
            COUNT(*) as entries,
            ROUND(AVG(CAST(win_odds AS NUMERIC)), 2) as avg_odds
        FROM racecard_details 
        WHERE trainer_name IS NOT NULL 
        AND win_odds ~ '^[0-9]+\\.?[0-9]*$'
        GROUP BY trainer_name 
        ORDER BY entries DESC 
        LIMIT 10;
    """
    )
    trainer_stats = cursor.fetchall()
    for trainer, entries, avg_odds in trainer_stats:
        print(f"    • {trainer}: {entries} entries (Avg Odds: {avg_odds})")

    # 8. Now check races_cards table for race information
    print("\n" + "=" * 70)
    print("🏁 RACE INFORMATION (from races_cards table):")

    cursor.execute("SELECT COUNT(*) FROM races_cards;")
    race_count = cursor.fetchone()[0]
    print(f"  • Total Races: {race_count:,}")

    # Check structure of races_cards
    cursor.execute(
        """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'races_cards' 
        ORDER BY ordinal_position;
    """
    )
    race_columns = [row[0] for row in cursor.fetchall()]
    print(f"  • Columns: {', '.join(race_columns)}")

    # Sample race data
    print("\n🏁 SAMPLE RACE DATA:")
    cursor.execute(
        """
        SELECT *
        FROM races_cards 
        LIMIT 5;
    """
    )
    races = cursor.fetchall()
    for i, race in enumerate(races, 1):
        print(f"    Race {i}: {race}")

    # 9. Data quality summary
    print("\n✅ OVERALL DATA QUALITY:")
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_entries,
            COUNT(CASE WHEN horse_name IS NOT NULL THEN 1 END) as has_horse,
            COUNT(CASE WHEN jockey_name IS NOT NULL THEN 1 END) as has_jockey,
            COUNT(CASE WHEN trainer_name IS NOT NULL THEN 1 END) as has_trainer,
            COUNT(CASE WHEN win_odds IS NOT NULL THEN 1 END) as has_odds,
            COUNT(CASE WHEN form IS NOT NULL THEN 1 END) as has_form
        FROM racecard_details;
    """
    )
    quality = cursor.fetchone()
    total = quality[0]

    print(f"  • Total Entries: {total:,}")
    print(f"  • Horse Names: {quality[1]:,} ({quality[1]/total*100:.1f}%)")
    print(f"  • Jockey Names: {quality[2]:,} ({quality[2]/total*100:.1f}%)")
    print(f"  • Trainer Names: {quality[3]:,} ({quality[3]/total*100:.1f}%)")
    print(f"  • Win Odds: {quality[4]:,} ({quality[4]/total*100:.1f}%)")
    print(f"  • Form Data: {quality[5]:,} ({quality[5]/total*100:.1f}%)")


def main():
    """Main execution function"""
    print("🏇 Starting Comprehensive Race Cards Analysis...")

    # Connect to database
    conn = connect_to_database()
    if not conn:
        return

    try:
        # Run analysis
        analyze_race_cards(conn)

        print("\n" + "=" * 70)
        print("✅ Race Cards Analysis Complete!")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
