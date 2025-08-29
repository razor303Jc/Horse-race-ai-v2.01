#!/usr/bin/env python3
"""
Race Card Data Fetcher
Horse Racing AI v2.02

Automatically fetches today's race cards to determine:
- First race time for pipeline scheduling
- Total number of races for workload estimation
- Track conditions and race types for model preparation

Integrates with pipeline timing system for optimal schedule calculation.
"""

import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/race_card_fetcher.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RaceCardFetcher:
    """
    Fetches race card data for automatic pipeline scheduling
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("data/race_cards").mkdir(parents=True, exist_ok=True)
        Path("results/scheduling").mkdir(parents=True, exist_ok=True)

    def fetch_racing_post_cards(self, date: str = None) -> List[Dict]:
        """
        Fetch race cards from Racing Post (example implementation)
        In production, this would use official APIs
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"🏇 Fetching race cards for {date}")

        # Mock data for demonstration - in production use real API
        mock_races = [
            {
                "course": "Newmarket",
                "first_race_time": "14:00",
                "last_race_time": "17:30",
                "race_count": 7,
                "surface": "turf",
                "distance_range": "5f-2m",
                "prize_total": "£125,000",
            },
            {
                "course": "Cheltenham",
                "first_race_time": "13:45",
                "last_race_time": "17:15",
                "race_count": 6,
                "surface": "turf",
                "distance_range": "2m-3m2f",
                "prize_total": "£98,500",
            },
            {
                "course": "Lingfield",
                "first_race_time": "15:30",
                "last_race_time": "18:45",
                "race_count": 8,
                "surface": "all_weather",
                "distance_range": "5f-1m6f",
                "prize_total": "£67,200",
            },
        ]

        logger.info(f"✅ Found {len(mock_races)} race meetings")
        return mock_races

    def calculate_first_race_time(self, race_cards: List[Dict]) -> str:
        """Calculate the earliest first race time across all courses"""
        if not race_cards:
            default_time = "14:00"
            logger.warning(f"⚠️ No race cards found, using default: {default_time}")
            return default_time

        first_times = []
        for card in race_cards:
            first_time = card.get("first_race_time", "14:00")
            first_times.append(datetime.strptime(first_time, "%H:%M").time())

        earliest = min(first_times)
        earliest_str = earliest.strftime("%H:%M")

        logger.info(f"🕐 Earliest race time today: {earliest_str}")
        return earliest_str

    def estimate_data_workload(self, race_cards: List[Dict]) -> Dict:
        """Estimate data processing workload from race cards"""
        total_races = sum(card.get("race_count", 0) for card in race_cards)
        total_runners_estimate = total_races * 12  # Average runners per race

        # Estimate processing complexity
        complexity_factors = {"turf": 1.0, "all_weather": 0.8, "national_hunt": 1.3}

        weighted_complexity = sum(
            complexity_factors.get(card.get("surface", "turf"), 1.0)
            * card.get("race_count", 0)
            for card in race_cards
        ) / max(total_races, 1)

        workload = {
            "total_races": total_races,
            "estimated_runners": total_runners_estimate,
            "complexity_factor": weighted_complexity,
            "processing_time_estimate": total_races * 2.5,  # minutes
            "data_volume_category": self._categorize_volume(total_races),
        }

        logger.info(
            f"📊 Workload estimate: {total_races} races, "
            f"~{total_runners_estimate} runners, "
            f"complexity {weighted_complexity:.2f}"
        )

        return workload

    def _categorize_volume(self, total_races: int) -> str:
        """Categorize data volume for processing optimization"""
        if total_races <= 20:
            return "light"
        elif total_races <= 40:
            return "moderate"
        elif total_races <= 60:
            return "heavy"
        else:
            return "very_heavy"

    def save_race_card_data(
        self, race_cards: List[Dict], workload: Dict, first_race_time: str
    ) -> str:
        """Save race card data for pipeline integration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = {
            "fetch_timestamp": datetime.now().isoformat(),
            "race_date": datetime.now().strftime("%Y-%m-%d"),
            "first_race_time": first_race_time,
            "race_cards": race_cards,
            "workload_analysis": workload,
            "pipeline_recommendations": {
                "suggested_start_time": self._suggest_pipeline_start(first_race_time),
                "buffer_recommendation": self._recommend_buffer(workload),
                "ml_training_priority": self._assess_ml_priority(workload),
            },
        }

        filename = f"data/race_cards/race_cards_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"💾 Race card data saved: {filename}")
        return filename

    def _suggest_pipeline_start(self, first_race_time: str) -> str:
        """Suggest pipeline start time based on first race"""
        first_race = datetime.strptime(first_race_time, "%H:%M").time()

        # Pipeline should complete well before first race
        # Aim for 2-3 hours buffer
        target_completion = datetime.combine(datetime.today(), first_race)
        target_completion -= timedelta(hours=2, minutes=30)

        # Pipeline takes ~8-9 hours, so work backwards
        suggested_start = target_completion - timedelta(hours=8, minutes=30)

        # Don't start before 5:00 AM
        earliest_start = datetime.combine(
            datetime.today(), datetime.strptime("05:00", "%H:%M").time()
        )

        if suggested_start < earliest_start:
            suggested_start = earliest_start

        return suggested_start.strftime("%H:%M")

    def _recommend_buffer(self, workload: Dict) -> int:
        """Recommend buffer time based on workload"""
        base_buffer = 60  # minutes

        volume_buffers = {"light": 0, "moderate": 30, "heavy": 60, "very_heavy": 120}

        complexity_buffer = int((workload.get("complexity_factor", 1.0) - 1.0) * 30)
        volume_buffer = volume_buffers.get(
            workload.get("data_volume_category", "moderate"), 30
        )

        total_buffer = base_buffer + volume_buffer + complexity_buffer
        return max(60, min(240, total_buffer))  # 1-4 hours

    def _assess_ml_priority(self, workload: Dict) -> str:
        """Assess ML training priority based on workload"""
        if workload.get("data_volume_category") in ["heavy", "very_heavy"]:
            return "high"  # More data = more training value
        elif workload.get("complexity_factor", 1.0) > 1.2:
            return "high"  # Complex races need better models
        else:
            return "normal"

    def get_today_schedule_data(self) -> Dict:
        """Get complete schedule data for today"""
        logger.info("🚀 Fetching today's racing schedule data")

        # Fetch race cards
        race_cards = self.fetch_racing_post_cards()

        # Calculate key timing data
        first_race_time = self.calculate_first_race_time(race_cards)
        workload = self.estimate_data_workload(race_cards)

        # Save data
        data_file = self.save_race_card_data(race_cards, workload, first_race_time)

        return {
            "first_race_time": first_race_time,
            "workload": workload,
            "race_cards": race_cards,
            "data_file": data_file,
            "recommendations": {
                "pipeline_start": self._suggest_pipeline_start(first_race_time),
                "buffer_minutes": self._recommend_buffer(workload),
                "ml_priority": self._assess_ml_priority(workload),
            },
        }


def main():
    """Main execution"""
    fetcher = RaceCardFetcher()

    try:
        schedule_data = fetcher.get_today_schedule_data()

        print("\n🏇 Today's Racing Schedule Analysis")
        print(f"   First Race Time: {schedule_data['first_race_time']}")
        print(f"   Total Races: {schedule_data['workload']['total_races']}")
        print(f"   Data Volume: {schedule_data['workload']['data_volume_category']}")
        print(f"   Complexity: {schedule_data['workload']['complexity_factor']:.2f}")

        print("\n⚙️ Pipeline Recommendations")
        recs = schedule_data["recommendations"]
        print(f"   Suggested Start: {recs['pipeline_start']}")
        print(f"   Buffer Time: {recs['buffer_minutes']} minutes")
        print(f"   ML Priority: {recs['ml_priority']}")

        print(f"\n💾 Data saved: {schedule_data['data_file']}")

    except Exception as e:
        logger.error(f"❌ Error fetching race schedule: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
