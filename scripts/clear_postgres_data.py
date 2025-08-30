#!/usr/bin/env python3
"""
🗑️ PostgreSQL Database Data Cleaner
====================================

Safely clears all data from PostgreSQL databases in Docker container
while preserving database structures and schemas.

Author: AI Assistant
Date: August 29, 2025
"""

import subprocess
import sys
from pathlib import Path


class PostgreSQLCleaner:
    def __init__(self, container_name="horse_racing_postgres_clean"):
        self.container_name = container_name
        self.username = "horse_racing"
        self.databases_to_clear = [
            "results_horse_racing_db",
            "advanced_racing_metrics_db",
            "cards_horse_racing_db",
        ]

    def run_psql_command(self, database, command):
        """Execute a psql command in the container"""
        cmd = [
            "docker",
            "exec",
            "-it",
            self.container_name,
            "psql",
            "-U",
            self.username,
            "-d",
            database,
            "-c",
            command,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing command: {e}")
            print(f"   Stderr: {e.stderr}")
            return None

    def get_all_tables(self, database):
        """Get list of all tables in a database"""
        query = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
        """

        result = self.run_psql_command(database, query)
        if result:
            tables = []
            for line in result.strip().split("\n"):
                line = line.strip()
                if (
                    line
                    and not line.startswith("tablename")
                    and not line.startswith("-")
                ):
                    if line != "(0 rows)":
                        tables.append(line)
            return tables
        return []

    def get_all_sequences(self, database):
        """Get list of all sequences in a database"""
        query = """
        SELECT sequencename 
        FROM pg_sequences 
        WHERE schemaname = 'public'
        ORDER BY sequencename;
        """

        result = self.run_psql_command(database, query)
        if result:
            sequences = []
            for line in result.strip().split("\n"):
                line = line.strip()
                if (
                    line
                    and not line.startswith("sequencename")
                    and not line.startswith("-")
                ):
                    if line != "(0 rows)":
                        sequences.append(line)
            return sequences
        return []

    def clear_database_data(self, database):
        """Clear all data from a specific database"""
        print(f"\n🗑️ Clearing data from database: {database}")
        print("=" * 50)

        # Get all tables
        tables = self.get_all_tables(database)
        if not tables:
            print(f"✅ No tables found in {database}")
            return True

        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")

        # Disable foreign key checks and truncate all tables
        truncate_commands = []

        # First, disable triggers temporarily
        truncate_commands.append("SET session_replication_role = replica;")

        # Truncate all tables
        for table in tables:
            truncate_commands.append(
                f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"
            )

        # Re-enable triggers
        truncate_commands.append("SET session_replication_role = DEFAULT;")

        # Execute all commands in a single transaction
        full_command = " ".join(truncate_commands)

        print("🔄 Executing TRUNCATE commands...")
        result = self.run_psql_command(database, full_command)

        if result is not None:
            print(f"✅ Successfully cleared all data from {database}")

            # Reset sequences
            sequences = self.get_all_sequences(database)
            if sequences:
                print(f"🔢 Resetting {len(sequences)} sequences...")
                for sequence in sequences:
                    reset_cmd = f"ALTER SEQUENCE {sequence} RESTART WITH 1;"
                    self.run_psql_command(database, reset_cmd)
                print("✅ Sequences reset to start from 1")

            return True
        else:
            print(f"❌ Failed to clear data from {database}")
            return False

    def verify_data_cleared(self, database):
        """Verify that data has been cleared"""
        print(f"\n🔍 Verifying data cleared from {database}...")

        tables = self.get_all_tables(database)
        total_rows = 0

        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table};"
            result = self.run_psql_command(database, count_query)

            if result:
                # Extract count from result
                lines = result.strip().split("\n")
                for line in lines:
                    if line.strip().isdigit():
                        count = int(line.strip())
                        total_rows += count
                        if count > 0:
                            print(f"  ⚠️ Table {table} still has {count} rows")
                        else:
                            print(f"  ✅ Table {table} is empty")

        if total_rows == 0:
            print(f"✅ All tables in {database} are empty")
            return True
        else:
            print(f"⚠️ {database} still has {total_rows} total rows")
            return False

    def clear_all_databases(self):
        """Clear data from all specified databases"""
        print("🗑️ POSTGRESQL DATABASE DATA CLEANER")
        print("=" * 50)
        print(f"Container: {self.container_name}")
        print(f"Username: {self.username}")
        print(f"Databases to clear: {', '.join(self.databases_to_clear)}")
        print()

        # Ask for confirmation
        response = (
            input("⚠️ This will DELETE ALL DATA from the databases. Continue? (y/N): ")
            .strip()
            .lower()
        )
        if response != "y":
            print("❌ Operation cancelled")
            return False

        success_count = 0

        for database in self.databases_to_clear:
            try:
                if self.clear_database_data(database):
                    if self.verify_data_cleared(database):
                        success_count += 1
                    else:
                        print(f"⚠️ Verification failed for {database}")
                else:
                    print(f"❌ Failed to clear {database}")
            except Exception as e:
                print(f"❌ Error processing {database}: {e}")

        print(f"\n📊 SUMMARY")
        print("=" * 50)
        print(f"Databases processed: {len(self.databases_to_clear)}")
        print(f"Successfully cleared: {success_count}")
        print(f"Failed: {len(self.databases_to_clear) - success_count}")

        if success_count == len(self.databases_to_clear):
            print("🎉 ALL DATABASES CLEARED SUCCESSFULLY!")
            return True
        else:
            print("⚠️ Some databases could not be cleared completely")
            return False


def main():
    """Main execution function"""
    cleaner = PostgreSQLCleaner()

    # Check if container is running
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name={cleaner.container_name}",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if cleaner.container_name not in result.stdout:
            print(f"❌ Container {cleaner.container_name} is not running")
            print("   Start the container first with: docker-compose up -d postgres")
            return False
    except subprocess.CalledProcessError:
        print("❌ Docker is not available or not running")
        return False

    return cleaner.clear_all_databases()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
