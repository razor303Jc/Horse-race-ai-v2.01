#!/usr/bin/env python3
"""
🔍 Database Relationship Explorer
=================================

Direct exploration of database relationships without pytest framework.
This will show us what's actually in the database!
"""

import psycopg2
from psycopg2.extras import DictCursor
import sys
from pathlib import Path

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "results_horse_racing_db",
    "user": "horse_racing",
    "password": "horse_racing_password",
    "port": "5432",
}


def explore_table_structure():
    """Explore the basic table structure"""
    print("🔍 Exploring Database Structure")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Get all tables
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        )

        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table}")

        cursor.close()
        conn.close()

        return tables

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def explore_foreign_keys():
    """Explore foreign key relationships"""
    print("\n🔗 Exploring Foreign Key Relationships")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        cursor.execute(
            """
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name;
        """
        )

        foreign_keys = cursor.fetchall()

        if foreign_keys:
            print(f"Found {len(foreign_keys)} foreign key relationships:")
            for fk in foreign_keys:
                print(
                    f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}"
                )
        else:
            print("⚠️  No foreign key constraints found!")

        cursor.close()
        conn.close()

        return foreign_keys

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def explore_primary_keys():
    """Explore primary key constraints"""
    print("\n🔑 Exploring Primary Keys")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        cursor.execute(
            """
            SELECT 
                tc.table_name,
                kcu.column_name,
                tc.constraint_name
            FROM 
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            ORDER BY tc.table_name;
        """
        )

        primary_keys = cursor.fetchall()

        if primary_keys:
            print(f"Found {len(primary_keys)} primary keys:")
            for pk in primary_keys:
                print(f"  {pk['table_name']}.{pk['column_name']}")
        else:
            print("⚠️  No primary keys found!")

        cursor.close()
        conn.close()

        return primary_keys

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def explore_table_details(table_name):
    """Explore details of a specific table"""
    print(f"\n📊 Table Details: {table_name}")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Get column information
        cursor.execute(
            f"""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """
        )

        columns = cursor.fetchall()

        print(f"Columns in {table_name}:")
        for col in columns:
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            max_len = (
                f"({col['character_maximum_length']})"
                if col["character_maximum_length"]
                else ""
            )
            default = (
                f" DEFAULT {col['column_default']}" if col["column_default"] else ""
            )
            print(
                f"  {col['column_name']}: {col['data_type']}{max_len} {nullable}{default}"
            )

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        print(f"Total rows: {row_count:,}")

        cursor.close()
        conn.close()

        return columns, row_count

    except Exception as e:
        print(f"❌ Error exploring {table_name}: {e}")
        return [], 0


def explore_data_relationships():
    """Explore actual data relationships"""
    print("\n🔍 Exploring Data Relationships")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Check race_results to races relationship
        cursor.execute(
            """
            SELECT COUNT(DISTINCT race_id) as unique_races
            FROM race_results;
        """
        )
        races_in_results = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) as total_races FROM races;")
        total_races = cursor.fetchone()[0]

        print(
            f"🏇 Races: {total_races} in races table, {races_in_results} referenced in race_results"
        )

        # Check horses
        cursor.execute(
            """
            SELECT COUNT(DISTINCT horse_id) as unique_horses
            FROM race_results;
        """
        )
        horses_in_results = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) as total_horses FROM horses_entity;")
        total_horses = cursor.fetchone()[0]

        print(
            f"🐎 Horses: {total_horses} in horses_entity, {horses_in_results} referenced in race_results"
        )

        # Check place codes
        cursor.execute(
            """
            SELECT place, COUNT(*) as count
            FROM race_results
            GROUP BY place
            ORDER BY count DESC
            LIMIT 10;
        """
        )

        place_codes = cursor.fetchall()
        print(f"\n🏁 Top 10 place codes:")
        for place, count in place_codes:
            print(f"  Place {place}: {count} times")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error exploring relationships: {e}")


def main():
    """Main exploration function"""
    print("🔍 Database Relationship Explorer v2.05")
    print("=" * 60)

    # Explore basic structure
    tables = explore_table_structure()

    if not tables:
        print("❌ Could not connect to database or no tables found!")
        return

    # Explore constraints
    foreign_keys = explore_foreign_keys()
    primary_keys = explore_primary_keys()

    # Explore key tables in detail
    key_tables = ["race_results", "races", "horses_entity", "horses_index"]
    for table in key_tables:
        if table in tables:
            explore_table_details(table)

    # Explore data relationships
    explore_data_relationships()

    print(f"\n🎯 Summary:")
    print(f"  Tables found: {len(tables)}")
    print(f"  Foreign keys: {len(foreign_keys)}")
    print(f"  Primary keys: {len(primary_keys)}")

    if len(foreign_keys) == 0:
        print(f"\n⚠️  No foreign key constraints found!")
        print(
            f"     This means the database might not have proper referential integrity."
        )
        print(f"     Data relationships exist but are not enforced by the database.")


if __name__ == "__main__":
    main()
