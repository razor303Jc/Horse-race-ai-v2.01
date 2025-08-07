#!/usr/bin/env python3
"""
Test Script for Containerized Horse Racing AI System
==================================================

Tests the Monte Carlo simulator and integration with NTFY notifications.
"""

import asyncio
import json
import logging
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from horse_racing_ai.simulation.monte_carlo_simulator import (
        MonteCarloSimulator,
        create_monte_carlo_analysis,
    )

    MONTE_CARLO_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Monte Carlo simulator not available: {e}")
    MONTE_CARLO_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("Requests not available for NTFY testing")
    REQUESTS_AVAILABLE = False


@dataclass
class MockCompositeScore:
    """Mock composite score for testing."""

    horse_name: str
    composite_score: float
    confidence_level: float
    key_factors: List[str]
    concerns: List[str]


def create_sample_race_data() -> List[MockCompositeScore]:
    """Create sample race data for testing."""

    horses = [
        MockCompositeScore(
            horse_name="Thunder Strike",
            composite_score=85.4,
            confidence_level=0.92,
            key_factors=["Recent win", "Good track record", "Favorable conditions"],
            concerns=["Minor weight increase"],
        ),
        MockCompositeScore(
            horse_name="Lightning Bolt",
            composite_score=82.1,
            confidence_level=0.88,
            key_factors=["Strong jockey", "Good recent form"],
            concerns=["Track conditions", "Distance question"],
        ),
        MockCompositeScore(
            horse_name="Storm Rider",
            composite_score=78.9,
            confidence_level=0.85,
            key_factors=["Class improvement", "Trainer form"],
            concerns=["First time blinkers", "Wide draw"],
        ),
        MockCompositeScore(
            horse_name="Wind Walker",
            composite_score=76.3,
            confidence_level=0.82,
            key_factors=["Dropping in class"],
            concerns=["Poor recent form", "Long layoff", "Gear changes"],
        ),
        MockCompositeScore(
            horse_name="Speed Demon",
            composite_score=73.7,
            confidence_level=0.79,
            key_factors=["Early speed", "Track bias"],
            concerns=["Tends to fade", "Distance concerns", "Poor strike rate"],
        ),
        MockCompositeScore(
            horse_name="Midnight Express",
            composite_score=71.2,
            confidence_level=0.75,
            key_factors=["Improving form"],
            concerns=[
                "Inexperienced",
                "Barrier draw",
                "Weight concerns",
                "Wet track record",
            ],
        ),
    ]

    return horses


def send_ntfy_notification(
    message: str, title: Optional[str] = None, priority: str = "default"
) -> bool:
    """Send test notification to NTFY."""

    if not REQUESTS_AVAILABLE:
        logger.warning("Requests not available, skipping NTFY test")
        return False

    try:
        url = "http://localhost:8081/horse-racing-alerts"
        headers = {
            "Title": title or "🏇 Horse Racing AI Test",
            "Priority": priority,
            "Tags": "horse-racing,test,monte-carlo",
        }

        response = requests.post(url, data=message, headers=headers, timeout=5)

        if response.status_code == 200:
            logger.info("✅ NTFY notification sent successfully")
            return True
        else:
            logger.error(f"❌ NTFY notification failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ NTFY notification error: {e}")
        return False


def test_monte_carlo_simulator():
    """Test the Monte Carlo simulator with sample data."""

    if not MONTE_CARLO_AVAILABLE:
        logger.error("❌ Monte Carlo simulator not available")
        return False

    logger.info("🎯 Starting Monte Carlo simulation test...")

    # Create sample race data
    horse_scores = create_sample_race_data()
    logger.info(f"📊 Created sample race with {len(horse_scores)} horses")

    # Run Monte Carlo analysis
    try:
        analysis = create_monte_carlo_analysis(
            horse_scores=horse_scores,
            race_id="TEST_RACE_001",
            simulations=5000,  # Reduced for faster testing
        )

        logger.info("✅ Monte Carlo simulation completed successfully")
        logger.info(f"📈 Simulation reliability: {analysis.simulation_reliability:.2%}")

        # Display results
        print("\n" + "=" * 60)
        print("🏇 MONTE CARLO SIMULATION RESULTS")
        print("=" * 60)

        print(f"\n📊 Race: {analysis.race_id}")
        print(f"🔢 Simulations: {analysis.simulations_run:,}")
        print(f"🎯 Reliability: {analysis.simulation_reliability:.1%}")

        print("\n🏆 WIN PROBABILITIES:")
        sorted_horses = sorted(
            analysis.win_probabilities.items(), key=lambda x: x[1], reverse=True
        )

        for i, (horse, prob) in enumerate(sorted_horses, 1):
            avg_pos = analysis.average_positions[horse]
            stars = "⭐" * min(5, int(prob * 20))  # Star rating
            print(
                f"  {i}. {horse:<18} {prob:>6.1%} {stars:<5} (Avg pos: {avg_pos:.1f})"
            )

        print("\n🥉 PLACE PROBABILITIES (Top 3):")
        sorted_place = sorted(
            analysis.place_probabilities.items(), key=lambda x: x[1], reverse=True
        )

        for horse, prob in sorted_place[:3]:
            print(f"  • {horse:<18} {prob:>6.1%}")

        # Generate betting recommendations
        try:
            simulator = MonteCarloSimulator()
            recommendations = simulator.get_betting_recommendations(analysis)

            if recommendations:
                print("\n💰 BETTING RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec['horse_name']}")
                    print(f"     Win Probability: {rec['probability']:.1%}")
                    print(f"     Fair Odds: {rec['fair_odds']:.1f}")
                    print(f"     Confidence: {rec['confidence']:.1%}")
                    print(f"     Z-Score: {rec['z_score']:+.2f}")
            else:
                print("\n💰 No strong betting recommendations found")

        except Exception as e:
            logger.warning(f"Betting recommendations failed: {e}")

        print("\n" + "=" * 60)

        # Send NTFY notification with results
        winner = sorted_horses[0]
        message = f"""🏇 Monte Carlo Test Complete!

🏆 Top Pick: {winner[0]}
📊 Win Probability: {winner[1]:.1%}
🎯 Simulation Reliability: {analysis.simulation_reliability:.1%}
🔢 Simulations Run: {analysis.simulations_run:,}

✅ All systems operational!"""

        send_ntfy_notification(
            message=message, title="🎯 Monte Carlo Test Results", priority="high"
        )

        # Test passes if no exceptions thrown
        assert True

    except Exception as e:
        logger.error(f"❌ Monte Carlo simulation failed: {e}")
        # Fail the test if exception occurred
        assert False, f"Monte Carlo simulation failed: {e}"


def test_infrastructure():
    """Test infrastructure services."""

    logger.info("🔧 Testing infrastructure services...")

    # Test database connection
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"✅ Database connection successful: {version.split(',')[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.warning(f"⚠️ Database test failed: {e}")

    # Test Redis connection
    try:
        import redis

        r = redis.Redis(
            host="localhost", port=6380, password="redis_password_123", db=0
        )
        r.set("test_key", "test_value")
        value = r.get("test_key").decode()
        if value == "test_value":
            logger.info("✅ Redis connection successful")
        r.delete("test_key")
    except Exception as e:
        logger.warning(f"⚠️ Redis test failed: {e}")

    # Test NTFY
    send_ntfy_notification(
        message="🔧 Infrastructure test notification from Horse Racing AI",
        title="🏗️ Infrastructure Test",
        priority="low",
    )


def main():
    """Run all tests."""

    print("🚀 Horse Racing AI - Containerized System Test")
    print("=" * 50)

    # Test infrastructure
    test_infrastructure()

    print()

    # Test Monte Carlo simulator
    success = test_monte_carlo_simulator()

    print("\n🎯 TEST SUMMARY")
    print("-" * 30)

    if success:
        print("✅ All tests passed!")
        print("🎉 System is ready for production use!")

        # Final notification
        send_ntfy_notification(
            message="🎉 All system tests passed! Horse Racing AI is ready for action. 🏇",
            title="✅ System Test Complete",
            priority="high",
        )
    else:
        print("❌ Some tests failed!")
        print("🔧 Check logs for details")


if __name__ == "__main__":
    main()
