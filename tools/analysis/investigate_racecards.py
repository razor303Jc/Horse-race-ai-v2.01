#!/usr/bin/env python3
"""
Detailed Race Cards Data Investigation
"""

import psycopg2


def connect_to_database():
    """Connect to PostgreSQL database"""
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


def investigate_data(conn):
    """Detailed investigation of the actual data"""

    print("🔍 DETAILED RACE CARDS DATA INVESTIGATION")
    print("=" * 60)

    cursor = conn.cursor()

    # 1. Check for real horse names vs "0" entries
    print("\n🐎 HORSE NAME INVESTIGATION:")
    cursor.execute(
        """
        SELECT 
            horse_name,
            COUNT(*) as count
        FROM racecard_details 
        GROUP BY horse_name 
        ORDER BY count DESC 
        LIMIT 15;
    """
    )
    horse_names = cursor.fetchall()
    print("  Most Common Horse Names/Values:")
    for name, count in horse_names:
        print(f"    • '{name}': {count} entries")

    # 2. Check for real jockey names
    print("\n🏇 JOCKEY NAME INVESTIGATION:")
    cursor.execute(
        """
        SELECT 
            jockey_name,
            COUNT(*) as count
        FROM racecard_details 
        GROUP BY jockey_name 
        ORDER BY count DESC 
        LIMIT 15;
    """
    )
    jockey_names = cursor.fetchall()
    print("  Most Common Jockey Names/Values:")
    for name, count in jockey_names:
        print(f"    • '{name}': {count} entries")

    # 3. Check for entries with actual odds data
    print("\n💰 ODDS DATA INVESTIGATION:")
    cursor.execute(
        """
        SELECT 
            win_odds,
            place_odds,
            COUNT(*) as count
        FROM racecard_details 
        WHERE win_odds IS NOT NULL OR place_odds IS NOT NULL
        GROUP BY win_odds, place_odds 
        ORDER BY count DESC 
        LIMIT 10;
    """
    )
    odds_data = cursor.fetchall()
    print("  Odds Data (Win, Place, Count):")
    for win_odds, place_odds, count in odds_data:
        print(f"    • Win: {win_odds}, Place: {place_odds} | {count} entries")

    # 4. Check for form data
    print("\n📈 FORM DATA INVESTIGATION:")
    cursor.execute(
        """
        SELECT 
            form,
            COUNT(*) as count
        FROM racecard_details 
        WHERE form IS NOT NULL AND form != '' AND form != '0'
        GROUP BY form 
        ORDER BY count DESC 
        LIMIT 10;
    """
    )
    form_data = cursor.fetchall()
    if form_data:
        print("  Form Patterns Found:")
        for form, count in form_data:
            print(f"    • '{form}': {count} entries")
    else:
        print("  ❌ No meaningful form data found")

    # 5. Check races_cards table for real data
    print("\n🏁 RACES CARDS TABLE INVESTIGATION:")
    cursor.execute(
        """
        SELECT 
            race_time,
            course,
            race_type,
            date,
            race_name,
            distance,
            prize_money,
            field_size
        FROM races_cards 
        WHERE course != '0' OR race_name != '0'
        LIMIT 5;
    """
    )
    real_races = cursor.fetchall()

    if real_races:
        print("  Real Race Data Found:")
        for race in real_races:
            time, course, race_type, date, name, distance, prize, field = race
            print(f"    • {date} {time} | Course: {course} | {name}")
            print(f"      Distance: {distance} | Prize: £{prize} | Field: {field}")
    else:
        print("  ❌ No races with real course or race name data found")

        # Check all races to see what data we have
        print("\n  Checking all race data structure:")
        cursor.execute("SELECT * FROM races_cards LIMIT 3;")
        all_races = cursor.fetchall()
        for i, race in enumerate(all_races, 1):
            print(f"    Race {i}: {race}")

    # 6. Check for any entries with non-zero/non-null meaningful data
    print("\n✅ MEANINGFUL DATA SUMMARY:")

    # Count entries with real horse names (not "0")
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM racecard_details 
        WHERE horse_name != '0' AND horse_name IS NOT NULL;
    """
    )
    real_horses = cursor.fetchone()[0]

    # Count entries with odds
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM racecard_details 
        WHERE (win_odds IS NOT NULL AND win_odds != '') 
        OR (place_odds IS NOT NULL AND place_odds != '');
    """
    )
    with_odds = cursor.fetchone()[0]

    # Count entries with form
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM racecard_details 
        WHERE form IS NOT NULL AND form != '' AND form != '0';
    """
    )
    with_form = cursor.fetchone()[0]

    total_entries = 2477  # We know this from previous query

    print(f"  • Total Entries: {total_entries:,}")
    print(
        f"  • Real Horse Names: {real_horses:,} ({real_horses/total_entries*100:.1f}%)"
    )
    print(f"  • With Odds Data: {with_odds:,} ({with_odds/total_entries*100:.1f}%)")
    print(f"  • With Form Data: {with_form:,} ({with_form/total_entries*100:.1f}%)")

    # 7. Check age distribution
    print(f"\n🎂 AGE DISTRIBUTION:")
    cursor.execute(
        """
        SELECT 
            horse_age,
            COUNT(*) as count
        FROM racecard_details 
        WHERE horse_age IS NOT NULL
        GROUP BY horse_age 
        ORDER BY horse_age;
    """
    )
    age_dist = cursor.fetchall()
    for age, count in age_dist:
        print(f"    • Age {age}: {count} horses")


def main():
    """Main execution"""
    conn = connect_to_database()
    if not conn:
        return

    try:
        investigate_data(conn)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
