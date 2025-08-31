#!/usr/bin/env python3
"""
Database Configuration Module
============================

Centralized database configuration using environment variables.
This module provides consistent database connection parameters across all scripts.
"""

import os
from typing import Dict, Optional
from urllib.parse import urlparse


class DatabaseConfig:
    """Centralized database configuration management"""

    def __init__(self):
        # Load environment variables with defaults
        self.postgres_user = os.getenv("POSTGRES_USER", "horse_racing")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "horse_racing_password")
        self.postgres_host = os.getenv("POSTGRES_HOST", "postgres")
        self.postgres_port = os.getenv("POSTGRES_PORT", "5432")

        # Docker container names for exec commands
        self.containers = {
            "postgres": "horse_racing_postgres_clean",
            "data_pipeline": "horse_racing_data_pipeline_clean",
            "ml_trainer": "horse_racing_ml_trainer_clean",
            "web_app": "horse_racing_web_app_clean",
        }

        # Database names
        self.databases = {
            "results": "results_horse_racing_db",
            "cards": "cards_horse_racing_db",
            "advanced": "advanced_horse_racing_db",
            "postgres": "postgres",  # Default database for admin operations
        }

    def get_database_url(self, database_type: str) -> str:
        """
        Get database URL for a specific database type

        Args:
            database_type: One of 'results', 'cards', 'advanced', 'postgres'

        Returns:
            Complete PostgreSQL URL
        """
        if database_type not in self.databases:
            raise ValueError(
                f"Unknown database type: {database_type}. Use one of: {list(self.databases.keys())}"
            )

        db_name = self.databases[database_type]
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{db_name}"

    def get_psql_params(self, database_type: str) -> Dict[str, str]:
        """
        Get psql connection parameters for docker exec commands

        Args:
            database_type: One of 'results', 'cards', 'advanced', 'postgres'

        Returns:
            Dictionary with connection parameters
        """
        if database_type not in self.databases:
            raise ValueError(
                f"Unknown database type: {database_type}. Use one of: {list(self.databases.keys())}"
            )

        return {
            "host": self.postgres_host,
            "port": self.postgres_port,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "database": self.databases[database_type],
            "container": self.containers["postgres"],
        }

    def get_docker_exec_command(self, database_type: str, sql_command: str) -> list:
        """
        Generate docker exec command for running SQL

        Args:
            database_type: One of 'results', 'cards', 'advanced', 'postgres'
            sql_command: SQL command to execute

        Returns:
            List of command arguments for subprocess
        """
        params = self.get_psql_params(database_type)

        return [
            "docker",
            "exec",
            params["container"],
            "psql",
            "-U",
            params["user"],
            "-d",
            params["database"],
            "-c",
            sql_command,
        ]

    def validate_connection(self, database_type: str = "postgres") -> bool:
        """
        Test database connection

        Args:
            database_type: Database to test connection to

        Returns:
            True if connection successful, False otherwise
        """
        import subprocess

        try:
            cmd = self.get_docker_exec_command(database_type, "SELECT 1;")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def list_databases(self) -> Optional[list]:
        """
        List all databases on the PostgreSQL server

        Returns:
            List of database names or None if error
        """
        import subprocess

        try:
            cmd = self.get_docker_exec_command("postgres", "\\l")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse the output to extract database names
                lines = result.stdout.strip().split("\n")
                databases = []
                for line in lines:
                    if "|" in line and not line.startswith(" Name"):
                        db_name = line.split("|")[0].strip()
                        if db_name and not db_name.startswith("-"):
                            databases.append(db_name)
                return databases
            return None
        except Exception:
            return None

    def get_environment_info(self) -> Dict[str, str]:
        """Get current environment configuration info"""
        return {
            "postgres_user": self.postgres_user,
            "postgres_host": self.postgres_host,
            "postgres_port": self.postgres_port,
            "available_databases": list(self.databases.keys()),
            "containers": self.containers,
            "password_set": "***" if self.postgres_password else "NOT SET",
        }


# Global configuration instance
db_config = DatabaseConfig()


# Convenience functions for backward compatibility
def get_database_url(database_type: str = "results") -> str:
    """Get database URL for specified type"""
    return db_config.get_database_url(database_type)


def get_psql_params(database_type: str = "results") -> Dict[str, str]:
    """Get psql parameters for specified database"""
    return db_config.get_psql_params(database_type)


def execute_sql_command(database_type: str, sql_command: str) -> bool:
    """Execute SQL command via docker exec"""
    import subprocess
    import logging

    try:
        cmd = db_config.get_docker_exec_command(database_type, sql_command)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error(f"SQL execution failed: {e.stderr.strip()}")
        return False
    except Exception as e:
        logging.error(f"Failed to execute SQL: {e}")
        return False


if __name__ == "__main__":
    # Test the configuration
    print("🔧 Database Configuration Test")
    print("=" * 40)

    config_info = db_config.get_environment_info()
    for key, value in config_info.items():
        print(f"{key}: {value}")

    print("\n🔗 Testing database connections...")
    for db_type in db_config.databases.keys():
        if db_config.validate_connection(db_type):
            print(f"✅ {db_type}: Connected")
        else:
            print(f"❌ {db_type}: Failed")

    print("\n📋 Available databases:")
    databases = db_config.list_databases()
    if databases:
        for db in databases:
            print(f"  - {db}")
    else:
        print("  Could not retrieve database list")
