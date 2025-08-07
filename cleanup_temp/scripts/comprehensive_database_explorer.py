#!/usr/bin/env python3
"""
Comprehensive Database Explorer
Explores all databases: SQLite files, Docker PostgreSQL, and any other databases
Provides complete summary of the Horse Racing AI v2.0 project data
"""

import sqlite3
import psycopg2
import pandas as pd
import sys
import os
from pathlib import Path
import subprocess
import json


class ComprehensiveDatabaseExplorer:
    def __init__(self):
        self.results = {}
        self.total_records = 0

    def explore_sqlite_database(self, db_path: str):
        """Explore a SQLite database"""
        if not Path(db_path).exists():
            return {"error": f"Database {db_path} not found"}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            db_info = {
                "type": "SQLite",
                "path": db_path,
                "size_mb": round(Path(db_path).stat().st_size / (1024 * 1024), 2),
                "tables": {},
                "total_records": 0,
            }

            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                db_info["total_records"] += count

                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                samples = cursor.fetchall()

                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                db_info["tables"][table_name] = {
                    "records": count,
                    "columns": len(columns),
                    "column_names": [col[1] for col in columns],
                    "sample_data": samples[:1] if samples else [],  # Just first row
                }

            conn.close()
            return db_info

        except Exception as e:
            return {"error": f"Error exploring {db_path}: {e}"}

    def explore_postgres_database(
        self,
        host="localhost",
        port=5433,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    ):
        """Explore PostgreSQL database"""
        try:
            conn = psycopg2.connect(
                host=host, port=port, database=database, user=user, password=password
            )
            cursor = conn.cursor()

            # Get tables
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            )
            tables = cursor.fetchall()

            db_info = {
                "type": "PostgreSQL",
                "host": f"{host}:{port}",
                "database": database,
                "tables": {},
                "total_records": 0,
            }

            for (table_name,) in tables:
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                db_info["total_records"] += count

                # Get column info
                cursor.execute(
                    f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """
                )
                columns = cursor.fetchall()

                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()

                db_info["tables"][table_name] = {
                    "records": count,
                    "columns": len(columns),
                    "column_info": columns,
                    "sample_data": sample,
                }

            conn.close()
            return db_info

        except Exception as e:
            return {"error": f"Error connecting to PostgreSQL: {e}"}

    def find_all_databases(self):
        """Find all databases in the project"""
        databases = []

        # Find SQLite databases
        for db_file in Path(".").rglob("*.db"):
            databases.append(("sqlite", str(db_file)))

        # Check for PostgreSQL containers
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if "horse_racing_postgres" in result.stdout:
                databases.append(("postgres_main", "horse_racing_postgres:5433"))
            if "horse_racing_postgres_test" in result.stdout:
                databases.append(("postgres_test", "horse_racing_postgres_test:5434"))
        except:
            pass

        return databases

    def generate_comprehensive_report(self):
        """Generate complete database report"""
        print("🔍 COMPREHENSIVE HORSE RACING AI v2.0 DATABASE EXPLORER")
        print("=" * 80)

        databases = self.find_all_databases()
        print(f"📋 FOUND {len(databases)} DATABASES:")

        for db_type, db_location in databases:
            print(f"   • {db_type}: {db_location}")

        print("\n" + "=" * 80)

        # Explore each database
        for db_type, db_location in databases:
            print(f"\n🗃️  EXPLORING: {db_type} - {db_location}")
            print("-" * 60)

            if db_type == "sqlite":
                db_info = self.explore_sqlite_database(db_location)
            elif db_type == "postgres_main":
                db_info = self.explore_postgres_database(port=5433)
            elif db_type == "postgres_test":
                db_info = self.explore_postgres_database(port=5434)
            else:
                db_info = {"error": "Unknown database type"}

            if "error" in db_info:
                print(f"❌ {db_info['error']}")
                continue

            self.results[db_location] = db_info
            self.total_records += db_info["total_records"]

            # Display database info
            print(f"📊 Type: {db_info['type']}")
            if "size_mb" in db_info:
                print(f"💾 Size: {db_info['size_mb']} MB")
            print(f"📋 Tables: {len(db_info['tables'])}")
            print(f"📊 Total Records: {db_info['total_records']:,}")

            # Show table details
            for table_name, table_info in db_info["tables"].items():
                print(f"\n   📋 TABLE: {table_name}")
                print(f"      📊 Records: {table_info['records']:,}")
                print(f"      📝 Columns: {table_info['columns']}")

                if "column_names" in table_info:
                    print(
                        f"      🏷️  Column Names: {', '.join(table_info['column_names'][:5])}{'...' if len(table_info['column_names']) > 5 else ''}"
                    )
                elif "column_info" in table_info:
                    cols = [
                        f"{col[0]}({col[1]})" for col in table_info["column_info"][:3]
                    ]
                    print(
                        f"      🏷️  Columns: {', '.join(cols)}{'...' if len(table_info['column_info']) > 3 else ''}"
                    )

        # Generate summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE SUMMARY")
        print("=" * 80)
        print(f"📊 Total Databases: {len(self.results)}")
        print(f"🔢 Total Records Across All Databases: {self.total_records:,}")

        # Categorize databases
        sqlite_dbs = len([db for db in self.results.values() if db["type"] == "SQLite"])
        postgres_dbs = len(
            [db for db in self.results.values() if db["type"] == "PostgreSQL"]
        )

        print(f"\n📋 Database Breakdown:")
        print(f"   • SQLite Databases: {sqlite_dbs}")
        print(f"   • PostgreSQL Databases: {postgres_dbs}")

        # Show largest databases
        sorted_dbs = sorted(
            self.results.items(), key=lambda x: x[1]["total_records"], reverse=True
        )
        print(f"\n🏆 Top Databases by Record Count:")
        for i, (db_name, db_info) in enumerate(sorted_dbs[:3]):
            print(f"   {i+1}. {db_name}: {db_info['total_records']:,} records")

        # Show database purposes
        print(f"\n🎯 Database Purposes:")
        for db_name, db_info in self.results.items():
            purpose = self.identify_database_purpose(db_name, db_info)
            print(f"   • {db_name}: {purpose}")

        print(f"\n💡 RECOMMENDATIONS:")
        if postgres_dbs > 0:
            print("   🐘 PostgreSQL databases detected - excellent for production!")
        if sqlite_dbs > 0:
            print("   📱 SQLite databases ideal for development and testing")
        print("   🚀 Rich dataset perfect for ML training and analysis")
        print("   📊 Ready for advanced horse racing AI applications")

    def identify_database_purpose(self, db_name, db_info):
        """Identify the purpose of each database"""
        if "production_training" in db_name:
            return "Production ML Training Dataset"
        elif "test" in db_name:
            return "Testing and Development Dataset"
        elif "quick" in db_name:
            return "Quick Testing Dataset"
        elif "monte_carlo" in db_name:
            return "Monte Carlo Simulation Dataset"
        elif "trends" in db_name:
            return "Race Trends Analysis Dataset"
        elif "horse_racing_postgres" in db_name:
            return "Primary PostgreSQL Production Database"
        elif "massive_racing" in db_name:
            return "Massive Dataset Generation Template"
        else:
            return "General Racing Dataset"


def main():
    explorer = ComprehensiveDatabaseExplorer()
    explorer.generate_comprehensive_report()


if __name__ == "__main__":
    main()
