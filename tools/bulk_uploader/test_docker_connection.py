#!/usr/bin/env python3
"""
Docker Network Test Script
Test connection to PostgreSQL via Docker network
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for bulk_uploader import
sys.path.insert(0, str(Path(__file__).parent))


def test_docker_network_connection():
    """Test connection using Docker network"""
    try:
        import psycopg2

        # Docker network configuration
        config = {
            "host": "postgres",  # Container alias on horse_racing_network
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        print("🔌 Testing Docker network connection to PostgreSQL...")
        print(f"   Host: {config['host']}")
        print(f"   Database: {config['database']}")

        # Test connection
        conn = psycopg2.connect(**config)

        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"   PostgreSQL version: {version}")

            # Test database access
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            print(f"   Current database: {db_name}")

            # Test table access
            cur.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """
            )
            tables = [row[0] for row in cur.fetchall()]
            print(f"   Available tables: {', '.join(tables)}")

        conn.close()
        return True

    except ImportError:
        print("❌ psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_environment_detection():
    """Test Docker environment detection"""
    print("\n🔍 Environment Detection Test:")

    # Check Docker indicators
    docker_env = os.path.exists("/.dockerenv")
    docker_container_var = os.environ.get("DOCKER_CONTAINER")

    print(f"   /.dockerenv exists: {docker_env}")
    print(f"   DOCKER_CONTAINER env var: {docker_container_var}")

    if docker_env or docker_container_var:
        print("   ✅ Docker container environment detected")
        return "container"
    else:
        print("   ℹ️  Local development environment detected")
        return "local"


def main():
    """Main test function"""
    print("🧪 Docker Network Connection Test")
    print("=" * 50)

    # Detect environment
    env_type = test_environment_detection()

    # Test connection
    if test_docker_network_connection():
        print("\n🎉 All tests passed!")

        if env_type == "local":
            print("\n💡 Running locally but can access Docker network!")
            print("   This means you can use the bulk uploader directly")
            print("   without needing to run it inside a container.")

        return 0
    else:
        print("\n❌ Connection test failed!")

        if env_type == "local":
            print("\n💡 Solutions:")
            print("   1. Run bulk uploader in Docker container:")
            print("      docker-compose -f tools/bulk_uploader/docker-compose.yml up")
            print("   2. Or use docker exec to run inside existing container:")
            print(
                "      docker exec -it horse_racing_ml_trainer_clean python /app/tools/bulk_uploader/cli.py test-connection"
            )

        return 1


if __name__ == "__main__":
    sys.exit(main())
