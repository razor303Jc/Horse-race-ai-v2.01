#!/usr/bin/env python3
"""
PostgreSQL Entity Tables Setup Script
=====================================

Creates entity tables for horses, jockeys, and trainers in PostgreSQL.
Designed for Horse Racing AI v2.05 project.

Usage:
    python setup_entity_tables.py [--create-all] [--create-horses] [--create-jockeys] [--create-trainers]

Environment Variables:
    POSTGRES_HOST - PostgreSQL host (default: localhost)
    POSTGRES_PORT - PostgreSQL port (default: 5432)
    POSTGRES_USER - PostgreSQL username (default: horse_racing)
    POSTGRES_PASSWORD - PostgreSQL password (default: secure_password_123)
"""

import os
import sys
import psycopg2
import logging
from pathlib import Path
from typing import Optional, List
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PostgreSQLEntityManager:
    """Manages PostgreSQL entity table creation and operations."""

    def __init__(self):
        """Initialize with PostgreSQL connection parameters."""
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.user = os.getenv("POSTGRES_USER", "horse_racing")
        self.password = os.getenv("POSTGRES_PASSWORD", "secure_password_123")
        self.databases = ["results", "cards", "advanced_metrics"]

        # Schema file paths
        self.schema_dir = Path(__file__).parent.parent / "schemas"
        self.schema_files = {
            "horses": self.schema_dir / "horses_entity.sql",
            "jockeys": self.schema_dir / "jockeys_entity.sql",
            "trainers": self.schema_dir / "trainers_entity.sql",
        }

    def test_connection(self, database: str = "postgres") -> bool:
        """Test PostgreSQL connection."""
        try:
            logger.info(f"Testing connection to PostgreSQL database '{database}'...")

            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database,
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    logger.info(f"✅ Connected successfully!")
                    if version:
                        logger.info(f"PostgreSQL version: {version[0]}")
                    return True

        except psycopg2.Error as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False

    def list_databases(self) -> List[str]:
        """List available databases."""
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database="postgres",
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT datname FROM pg_database 
                        WHERE datistemplate = false 
                        ORDER BY datname;
                    """
                    )
                    databases = [row[0] for row in cursor.fetchall()]
                    logger.info(f"Available databases: {', '.join(databases)}")
                    return databases

        except psycopg2.Error as e:
            logger.error(f"Failed to list databases: {e}")
            return []

    def database_exists(self, database_name: str) -> bool:
        """Check if database exists."""
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database="postgres",
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s;",
                        (database_name,),
                    )
                    return cursor.fetchone() is not None

        except psycopg2.Error as e:
            logger.error(f"Error checking database existence: {e}")
            return False

    def create_database(self, database_name: str) -> bool:
        """Create database if it doesn't exist."""
        try:
            if self.database_exists(database_name):
                logger.info(f"Database '{database_name}' already exists")
                return True

            logger.info(f"Creating database '{database_name}'...")

            # Connect to postgres database to create new database
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database="postgres",
            ) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE {database_name};")
                    logger.info(f"✅ Database '{database_name}' created successfully")
                    return True

        except psycopg2.Error as e:
            logger.error(f"❌ Failed to create database '{database_name}': {e}")
            return False

    def execute_sql_file(self, database: str, sql_file: Path) -> bool:
        """Execute SQL file in specified database."""
        try:
            if not sql_file.exists():
                logger.error(f"SQL file not found: {sql_file}")
                return False

            logger.info(f"Executing {sql_file.name} in database '{database}'...")

            with sql_file.open("r") as f:
                sql_content = f.read()

            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database,
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_content)
                    conn.commit()
                    logger.info(f"✅ Successfully executed {sql_file.name}")
                    return True

        except psycopg2.Error as e:
            logger.error(f"❌ SQL execution failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False

    def create_entity_table(self, entity_type: str, database: str = "results") -> bool:
        """Create specific entity table."""
        if entity_type not in self.schema_files:
            logger.error(f"Unknown entity type: {entity_type}")
            return False

        # Create database if it doesn't exist
        if not self.create_database(database):
            return False

        sql_file = self.schema_files[entity_type]
        return self.execute_sql_file(database, sql_file)

    def create_all_entity_tables(self, database: str = "results") -> bool:
        """Create all entity tables."""
        logger.info(f"Creating all entity tables in database '{database}'...")

        # Create database if it doesn't exist
        if not self.create_database(database):
            return False

        success_count = 0
        for entity_type in self.schema_files.keys():
            if self.create_entity_table(entity_type, database):
                success_count += 1

        total_tables = len(self.schema_files)
        if success_count == total_tables:
            logger.info(f"✅ All {total_tables} entity tables created successfully!")
            return True
        else:
            logger.warning(f"⚠️ Created {success_count}/{total_tables} tables")
            return False

    def verify_tables(self, database: str = "results") -> bool:
        """Verify that entity tables exist and are properly structured."""
        try:
            logger.info(f"Verifying entity tables in database '{database}'...")

            if not self.database_exists(database):
                logger.error(f"Database '{database}' does not exist")
                return False

            with psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database,
            ) as conn:
                with conn.cursor() as cursor:
                    # Check table existence
                    expected_tables = [
                        "horses_entity",
                        "jockeys_entity",
                        "trainers_entity",
                    ]

                    for table in expected_tables:
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = %s
                            );
                        """,
                            (table,),
                        )

                        result = cursor.fetchone()
                        exists = result[0] if result else False

                        if exists:
                            # Get row count
                            cursor.execute(f"SELECT COUNT(*) FROM {table};")
                            count_result = cursor.fetchone()
                            count = count_result[0] if count_result else 0
                            logger.info(f"✅ Table {table}: exists ({count} rows)")
                        else:
                            logger.error(f"❌ Table {table}: missing")
                            return False

                    logger.info("✅ All entity tables verified successfully!")
                    return True

        except psycopg2.Error as e:
            logger.error(f"❌ Table verification failed: {e}")
            return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Setup PostgreSQL Entity Tables")
    parser.add_argument(
        "--create-all", action="store_true", help="Create all entity tables"
    )
    parser.add_argument(
        "--create-horses", action="store_true", help="Create horses entity table"
    )
    parser.add_argument(
        "--create-jockeys", action="store_true", help="Create jockeys entity table"
    )
    parser.add_argument(
        "--create-trainers", action="store_true", help="Create trainers entity table"
    )
    parser.add_argument(
        "--database", default="results", help="Target database (default: results)"
    )
    parser.add_argument("--verify", action="store_true", help="Verify existing tables")

    args = parser.parse_args()

    # Initialize manager
    manager = PostgreSQLEntityManager()

    # Test connection first
    if not manager.test_connection():
        logger.error("Cannot proceed - database connection failed")
        sys.exit(1)

    # List available databases
    manager.list_databases()

    # Execute requested operations
    success = True

    if args.verify:
        success &= manager.verify_tables(args.database)

    if args.create_all:
        success &= manager.create_all_entity_tables(args.database)
    else:
        if args.create_horses:
            success &= manager.create_entity_table("horses", args.database)
        if args.create_jockeys:
            success &= manager.create_entity_table("jockeys", args.database)
        if args.create_trainers:
            success &= manager.create_entity_table("trainers", args.database)

    # Verify tables after creation
    if success and (
        args.create_all
        or args.create_horses
        or args.create_jockeys
        or args.create_trainers
    ):
        manager.verify_tables(args.database)

    if success:
        logger.info("🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Operation completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
