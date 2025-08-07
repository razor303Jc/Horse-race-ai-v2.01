#!/usr/bin/env python3
"""
Test Database Connection and Launch Web GUI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))


def test_database():
    """Test database connection"""
    try:
        from src.database.database_manager import DatabaseManager

        print("🔍 Testing database connection...")
        db = DatabaseManager()

        # Get summary statistics
        summary = db.get_database_summary()
        print("✅ Database connection successful!")

        print("\n📊 Database Summary:")
        print(f"  • Races Cards: {summary.get('tables', {}).get('races_cards', 0):,}")
        print(
            f"  • Races Results: {summary.get('tables', {}).get('races_results', 0):,}"
        )
        print(f"  • Horses Cards: {summary.get('tables', {}).get('horses_cards', 0):,}")
        print(
            f"  • Horses Results: {summary.get('tables', {}).get('horses_results', 0):,}"
        )
        print(f"  • Jockeys: {summary.get('tables', {}).get('jockeys_stats', 0):,}")
        print(f"  • Trainers: {summary.get('tables', {}).get('trainers_stats', 0):,}")
        print(
            f"  • Racecard Details: {summary.get('tables', {}).get('racecard_details', 0):,}"
        )
        print(f"  • Records: {summary.get('tables', {}).get('records', 0):,}")
        print(
            f"  • Latest Race: {summary.get('latest_data', {}).get('latest_race_date', 'N/A')}"
        )
        print(
            f"  • Total Courses: {summary.get('statistics', {}).get('total_courses', 0):,}"
        )

        db.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def launch_web_gui():
    """Launch the enhanced web GUI"""
    try:
        print("\n🚀 Launching enhanced web GUI with database integration...")

        # Import and run the web GUI
        from src.web.web_gui import app

        print("🌐 Web GUI available at: http://localhost:5000")
        print("🗄️  Database Dashboard: http://localhost:5000/database")
        print("\nPress Ctrl+C to stop the server")

        app.run(host="0.0.0.0", port=5000, debug=True)

    except Exception as e:
        print(f"❌ Failed to launch web GUI: {e}")


if __name__ == "__main__":
    print("🐴 Horse Racing AI v2.0 - Database & Web GUI Test")
    print("=" * 50)

    # Test database connection first
    if test_database():
        # Launch web GUI if database is working
        launch_web_gui()
    else:
        print("\n⚠️  Database connection failed. Please check:")
        print("  1. PostgreSQL container is running")
        print("  2. DATABASE_URL in .env file is correct")
        print("  3. Database has been populated with data")

        print(f"\nCurrent DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
