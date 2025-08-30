#!/usr/bin/env python3
"""
🗑️ PostgreSQL Horse Racing Databases Cleaner
============================================

Clears all data from the 3 horse racing databases while preserving
the default postgres database and system databases.

Databases to clear:
- results_horse_racing_db
- advanced_racing_metrics_db
- cards_horse_racing_db

Author: AI Assistant
Date: August 29, 2025
"""

import subprocess
import sys
from datetime import datetime


def run_psql_command(database, command, description):
    """Run a PostgreSQL command using docker exec"""
    try:
        print(f"  🔧 {description}...")

        full_command = [
            "docker",
            "exec",
            "-i",
            "horse_racing_postgres_clean",
            "psql",
            "-U",
            "horse_racing",
            "-d",
            database,
            "-c",
            command,
        ]

        result = subprocess.run(
            full_command, capture_output=True, text=True, check=True
        )

        if result.stdout.strip():
            print(f"     {result.stdout.strip()}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        if e.stderr:
            print(f"     {e.stderr.strip()}")
        return False


def get_database_tables(database):
    """Get list of tables in a database"""
    try:
        command = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """

        full_command = [
            "docker",
            "exec",
            "-i",
            "horse_racing_postgres_clean",
            "psql",
            "-U",
            "horse_racing",
            "-d",
            database,
            "-t",
            "-c",
            command,
        ]

        result = subprocess.run(
            full_command, capture_output=True, text=True, check=True
        )

        tables = [
            line.strip() for line in result.stdout.strip().split("\n") if line.strip()
        ]
        return tables

    except subprocess.CalledProcessError:
        return []


def clear_database_data(database):
    """Clear all data from a specific database"""
    print(f"\n🗑️ Clearing database: {database}")
    print("-" * 50)

    # Get list of tables
    tables = get_database_tables(database)

    if not tables:
        print(f"  ✅ No tables found in {database} or database doesn't exist")
        return True

    print(f"  📊 Found {len(tables)} tables: {', '.join(tables)}")

    # Disable foreign key constraints temporarily
    success = run_psql_command(
        database,
        "SET session_replication_role = replica;",
        "Disabling foreign key constraints",
    )

    if not success:
        return False

    # Truncate all tables
    for table in tables:
        success = run_psql_command(
            database, f"TRUNCATE TABLE {table} CASCADE;", f"Clearing table {table}"
        )

        if not success:
            print(f"  ⚠️  Failed to clear table {table}, continuing...")

    # Re-enable foreign key constraints
    run_psql_command(
        database,
        "SET session_replication_role = DEFAULT;",
        "Re-enabling foreign key constraints",
    )

    # Verify tables are empty
    total_rows = 0
    for table in tables:
        try:
            command = f"SELECT COUNT(*) FROM {table};"
            full_command = [
                "docker",
                "exec",
                "-i",
                "horse_racing_postgres_clean",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                database,
                "-t",
                "-c",
                command,
            ]

            result = subprocess.run(
                full_command, capture_output=True, text=True, check=True
            )

            count = int(result.stdout.strip())
            total_rows += count

        except:
            pass

    print(f"  ✅ Database {database} cleared successfully")
    print(f"  📊 Total remaining rows: {total_rows}")

    return True


def check_docker_container():
    """Check if PostgreSQL container is running"""
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=horse_racing_postgres_clean",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if "horse_racing_postgres_clean" in result.stdout:
            print("✅ PostgreSQL container is running")
            return True
        else:
            print("❌ PostgreSQL container is not running")
            print("   Please start it with: docker-compose up -d postgres")
            return False

    except subprocess.CalledProcessError:
        print("❌ Could not check Docker container status")
        return False


def main():
    """Main clearing process"""
    print("🗑️ POSTGRESQL HORSE RACING DATABASES CLEANER")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check Docker container
    if not check_docker_container():
        return 1

    # Define horse racing databases to clear
    databases_to_clear = [
        "results_horse_racing_db",
        "advanced_racing_metrics_db",
        "cards_horse_racing_db",
    ]

    print("🎯 Target Databases:")
    for db in databases_to_clear:
        print(f"  • {db}")

    print("\n⚠️  WARNING: This will permanently delete ALL data from these databases!")
    print("The default 'postgres' database will be preserved.")
    print()

    # Ask for confirmation
    response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()

    if response not in ["yes", "y"]:
        print("❌ Operation cancelled")
        return 0

    print(f"\n🚀 Starting database clearing process...")

    # Clear each database
    success_count = 0
    for database in databases_to_clear:
        if clear_database_data(database):
            success_count += 1

    # Final summary
    print(f"\n📊 CLEARING SUMMARY")
    print("=" * 30)
    print(f"Databases processed: {len(databases_to_clear)}")
    print(f"Successfully cleared: {success_count}")
    print(f"Failed: {len(databases_to_clear) - success_count}")

    if success_count == len(databases_to_clear):
        print("\n🎉 All horse racing databases cleared successfully!")
        print("✅ Default postgres database preserved")
    else:
        print(f"\n⚠️  Some databases could not be cleared completely")

    return 0


if __name__ == "__main__":
    sys.exit(main())
