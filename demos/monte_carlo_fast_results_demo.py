#!/usr/bin/env python3
"""
Monte Carlo + Fast Results + NTFY Demo
=====================================

Simplified demo showing Monte Carlo database integration
and fast results collection with NTFY notifications.
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_monte_carlo_fast_results():
    """Demo Monte Carlo + Fast Results + NTFY integration"""
    print("🎲 Monte Carlo + Fast Results + NTFY Demo")
    print("=" * 50)

    # 1. Test Monte Carlo Database Setup
    print("\n1️⃣ Testing Monte Carlo Database Setup...")
    try:
        from src.database.monte_carlo_database_manager import (
            MonteCarloIntegrationManager,
        )

        # Initialize with test database
        manager = MonteCarloIntegrationManager("data/demo_monte_carlo.db")

        # Generate mock performance report
        report = manager.generate_performance_report(30)
        print("   ✅ Monte Carlo database initialized")
        print(f"   📊 Performance report generated: {report}")

    except Exception as e:
        print(f"   ❌ Monte Carlo database setup failed: {e}")

    # 2. Test Fast Results Collection Setup
    print("\n2️⃣ Testing Fast Results Collection Setup...")
    try:
        from src.fast_results.racing_post_fast_results_ntfy import (
            FastResultsNTFYManager,
        )

        # Initialize fast results manager
        fast_results = FastResultsNTFYManager()

        # Add sample AI selections
        sample_picks = [
            {
                "race_id": "DEMO_RACE_001",
                "horse_name": "AI Champion",
                "confidence_level": 0.85,
                "win_probability": 0.65,
            },
            {
                "race_id": "DEMO_RACE_002",
                "horse_name": "Monte Carlo Star",
                "confidence_level": 0.78,
                "win_probability": 0.58,
            },
        ]

        await fast_results.setup_ai_tracking(sample_picks)
        summary = fast_results.get_performance_summary()

        print("   ✅ Fast results collection initialized")
        print(f"   🏇 AI selections tracked: {summary['ai_selections_tracked']}")

    except Exception as e:
        print(f"   ❌ Fast results setup failed: {e}")

    # 3. Test NTFY Notifications
    print("\n3️⃣ Testing NTFY Notifications...")
    try:
        from src.horse_racing_ai.notifications.ntfy_client import NTFYClient

        ntfy_client = NTFYClient()

        # Test race alert
        test_race_data = {
            "track": "Demo Track",
            "race_time": "15:30",
            "race_name": "Monte Carlo Demo Race",
            "distance": "1m 2f",
            "horses": [
                {"name": "AI Champion", "position": 1},
                {"name": "Monte Carlo Star", "position": 2},
            ],
        }

        await ntfy_client.send_race_alert(test_race_data, "success")
        print("   ✅ NTFY notifications working")
        print("   📱 Test race alert sent")

    except Exception as e:
        print(f"   ❌ NTFY notifications failed: {e}")
        print("   💡 This is expected if NTFY server is not configured")

    # 4. Integration Summary
    print("\n4️⃣ Integration Summary")
    print("   🎯 Key Features Implemented:")
    print("   • Monte Carlo simulation database storage")
    print("   • Fast results collection from Racing Post")
    print("   • NTFY notifications for AI selections")
    print("   • Real-time performance tracking")

    print("\n📋 Next Steps:")
    print("   1. Configure NTFY server for notifications")
    print("   2. Set up Racing Post monitoring schedule")
    print("   3. Integrate with existing Monte Carlo simulations")
    print("   4. Add betting recommendation tracking")

    print("\n🔗 Racing Post Fast Results URL:")
    print("   https://www.racingpost.com/fast-results/")

    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(demo_monte_carlo_fast_results())
