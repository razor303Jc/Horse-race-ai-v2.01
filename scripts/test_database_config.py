#!/usr/bin/env python3
"""
Test Database Configuration
===========================

Test the new centralized database configuration to ensure all connections work properly.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from config.database_config import db_config


def main():
    print("🔧 Testing Database Configuration")
    print("=" * 50)

    # Display configuration
    config_info = db_config.get_environment_info()
    print("\n📋 Current Configuration:")
    for key, value in config_info.items():
        print(f"  {key}: {value}")

    # Test connections
    print("\n🔗 Testing Database Connections:")
    all_connected = True

    for db_type in db_config.databases.keys():
        if db_config.validate_connection(db_type):
            print(f"  ✅ {db_type}: Connected ({db_config.databases[db_type]})")
        else:
            print(f"  ❌ {db_type}: Failed ({db_config.databases[db_type]})")
            all_connected = False

    # List available databases
    print("\n📋 Available Databases:")
    databases = db_config.list_databases()
    if databases:
        for db in databases:
            print(f"  - {db}")
    else:
        print("  Could not retrieve database list")

    # Test entity tables
    print("\n🗃️ Testing Entity Tables:")
    entity_tables = ["horses_entity", "jockeys_entity", "trainers_entity"]

    for table in entity_tables:
        try:
            cmd = db_config.get_docker_exec_command(
                "results", f"SELECT COUNT(*) FROM {table};"
            )
            import subprocess

            result = subprocess.run(
                cmd + ["-t"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                count = int(result.stdout.strip())
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: Query failed")
        except Exception as e:
            print(f"  ❌ {table}: Error - {e}")

    # Final status
    print("\n" + "=" * 50)
    if all_connected:
        print("🎉 All database connections successful!")
        print("✅ Database configuration is working properly")
        return 0
    else:
        print("⚠️  Some database connections failed")
        print("❌ Please check your environment configuration")
        return 1


if __name__ == "__main__":
    exit(main())
