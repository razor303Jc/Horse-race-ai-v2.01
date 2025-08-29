#!/usr/bin/env python3
"""
Live Feed Integration System
Horse Racing AI v2.0

Replaces auto-downloaders with live feed integration for real racing data.
Supports multiple data sources and real-time processing.
"""

import os
import logging
import asyncio
import aiohttp
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.database.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RaceData:
    """Standardized race data structure"""

    race_id: str
    course: str
    race_name: str
    race_time: str
    date: date
    distance: str
    race_type: str
    class_level: str
    prize_money: str
    participants: List[Dict[str, Any]]
    surface: str = "Turf"
    runners_count: int = 0


@dataclass
class FeedConfig:
    """Configuration for a live feed source"""

    name: str
    base_url: str
    api_key: Optional[str] = None
    headers: Dict[str, str] = None
    rate_limit: float = 1.0  # Requests per second
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority


class LiveFeedSource(ABC):
    """Abstract base class for live feed sources"""

    def __init__(self, config: FeedConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0.0

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Initialize connection to the feed"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = self.config.headers or {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        logger.info(f"✅ Connected to {self.config.name}")

    async def disconnect(self):
        """Close connection to the feed"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info(f"🔌 Disconnected from {self.config.name}")

    async def _rate_limit(self):
        """Implement rate limiting"""
        if self.config.rate_limit > 0:
            min_interval = 1.0 / self.config.rate_limit
            time_since_last = asyncio.get_event_loop().time() - self.last_request_time

            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)

            self.last_request_time = asyncio.get_event_loop().time()

    @abstractmethod
    async def get_races_for_date(self, target_date: date) -> List[RaceData]:
        """Get races for a specific date"""
        pass

    @abstractmethod
    async def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific race"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the feed is healthy and accessible"""
        pass


class RacingPostFeed(LiveFeedSource):
    """Racing Post live feed integration"""

    async def get_races_for_date(self, target_date: date) -> List[RaceData]:
        """Get races for a specific date from Racing Post"""
        await self._rate_limit()

        try:
            # Simulated Racing Post API call
            # In production, this would be the actual Racing Post API
            url = f"{self.config.base_url}/races/{target_date.isoformat()}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_racing_post_data(data, target_date)
                else:
                    logger.warning(f"Racing Post API returned {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching Racing Post data: {e}")
            return []

    def _parse_racing_post_data(self, data: Dict, target_date: date) -> List[RaceData]:
        """Parse Racing Post API response"""
        races = []

        # This is a simulation - in production, parse actual API response
        for race_data in data.get("races", []):
            participants = []
            for runner in race_data.get("runners", []):
                participants.append(
                    {
                        "name": runner.get("horse_name"),
                        "jockey": runner.get("jockey_name"),
                        "trainer": runner.get("trainer_name"),
                        "weight": runner.get("weight"),
                        "odds": runner.get("odds"),
                        "draw": runner.get("draw_number"),
                    }
                )

            race = RaceData(
                race_id=race_data.get("race_id"),
                course=race_data.get("course"),
                race_name=race_data.get("race_name"),
                race_time=race_data.get("off_time"),
                date=target_date,
                distance=race_data.get("distance"),
                race_type=race_data.get("race_type"),
                class_level=race_data.get("class"),
                prize_money=race_data.get("prize"),
                participants=participants,
                runners_count=len(participants),
            )
            races.append(race)

        return races

    async def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific race"""
        await self._rate_limit()

        try:
            url = f"{self.config.base_url}/results/{race_id}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"No results found for race {race_id}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching race results: {e}")
            return None

    async def health_check(self) -> bool:
        """Check Racing Post feed health"""
        try:
            url = f"{self.config.base_url}/health"
            async with self.session.get(url) as response:
                return response.status == 200
        except:
            return False


class TimeformFeed(LiveFeedSource):
    """Timeform live feed integration"""

    async def get_races_for_date(self, target_date: date) -> List[RaceData]:
        """Get races for a specific date from Timeform"""
        await self._rate_limit()

        try:
            # Simulated Timeform API call
            url = f"{self.config.base_url}/racing/{target_date.strftime('%Y%m%d')}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_timeform_data(data, target_date)
                else:
                    logger.warning(f"Timeform API returned {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching Timeform data: {e}")
            return []

    def _parse_timeform_data(self, data: Dict, target_date: date) -> List[RaceData]:
        """Parse Timeform API response"""
        races = []

        # Simulation - in production, parse actual Timeform response
        for meeting in data.get("meetings", []):
            for race in meeting.get("races", []):
                participants = []
                for runner in race.get("runners", []):
                    participants.append(
                        {
                            "name": runner.get("name"),
                            "jockey": runner.get("jockey"),
                            "trainer": runner.get("trainer"),
                            "weight": runner.get("weight"),
                            "odds": runner.get("starting_price"),
                            "draw": runner.get("stall"),
                        }
                    )

                race_data = RaceData(
                    race_id=f"tf_{race.get('id')}",
                    course=meeting.get("course"),
                    race_name=race.get("title"),
                    race_time=race.get("scheduled_time"),
                    date=target_date,
                    distance=race.get("distance"),
                    race_type=race.get("type"),
                    class_level=race.get("class"),
                    prize_money=race.get("prize_money"),
                    participants=participants,
                    runners_count=len(participants),
                )
                races.append(race_data)

        return races

    async def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific race"""
        await self._rate_limit()

        try:
            url = f"{self.config.base_url}/results/{race_id.replace('tf_', '')}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

        except Exception as e:
            logger.error(f"Error fetching Timeform results: {e}")
            return None

    async def health_check(self) -> bool:
        """Check Timeform feed health"""
        try:
            url = f"{self.config.base_url}/status"
            async with self.session.get(url) as response:
                return response.status == 200
        except:
            return False


class LiveFeedManager:
    """Manages multiple live feed sources with failover and aggregation"""

    def __init__(self):
        self.feeds: List[LiveFeedSource] = []
        self.db_manager = None
        self.is_running = False

    def add_feed(self, feed: LiveFeedSource):
        """Add a feed source"""
        self.feeds.append(feed)
        # Sort by priority (lower number = higher priority)
        self.feeds.sort(key=lambda f: f.config.priority)
        logger.info(f"✅ Added feed: {feed.config.name}")

    async def initialize(self):
        """Initialize the feed manager and database connection"""
        try:
            self.db_manager = DatabaseManager()
            logger.info("✅ Database manager initialized")

            # Connect to all enabled feeds
            for feed in self.feeds:
                if feed.config.enabled:
                    await feed.connect()

        except Exception as e:
            logger.error(f"❌ Failed to initialize feed manager: {e}")
            raise

    async def health_check_all_feeds(self) -> Dict[str, bool]:
        """Check health of all feeds"""
        results = {}

        for feed in self.feeds:
            if feed.config.enabled:
                try:
                    is_healthy = await feed.health_check()
                    results[feed.config.name] = is_healthy
                    logger.info(
                        f"🏥 {feed.config.name}: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}"
                    )
                except Exception as e:
                    results[feed.config.name] = False
                    logger.error(f"🏥 {feed.config.name}: ❌ Health check failed: {e}")

        return results

    async def fetch_races_for_date(self, target_date: date) -> List[RaceData]:
        """Fetch races from all available feeds with intelligent fallback"""
        all_races = []
        successful_feeds = []

        for feed in self.feeds:
            if not feed.config.enabled:
                continue

            try:
                logger.info(
                    f"📡 Fetching races from {feed.config.name} for {target_date}"
                )
                races = await feed.get_races_for_date(target_date)

                if races:
                    all_races.extend(races)
                    successful_feeds.append(feed.config.name)
                    logger.info(f"✅ Got {len(races)} races from {feed.config.name}")
                else:
                    logger.warning(f"⚠️ No races from {feed.config.name}")

            except Exception as e:
                logger.error(f"❌ Failed to fetch from {feed.config.name}: {e}")
                continue

        # Remove duplicates based on race_id and course/time
        unique_races = self._deduplicate_races(all_races)

        logger.info(
            f"📊 Fetched {len(unique_races)} unique races from {len(successful_feeds)} feeds"
        )
        return unique_races

    def _deduplicate_races(self, races: List[RaceData]) -> List[RaceData]:
        """Remove duplicate races from multiple feeds"""
        seen = set()
        unique_races = []

        for race in races:
            # Create a unique key based on course, time, and date
            key = f"{race.course}_{race.race_time}_{race.date}"

            if key not in seen:
                seen.add(key)
                unique_races.append(race)
            else:
                logger.debug(
                    f"🔄 Skipping duplicate race: {race.race_name} at {race.course}"
                )

        return unique_races

    async def process_live_data(self, target_date: date = None) -> Dict[str, Any]:
        """Process live racing data for a given date"""
        if target_date is None:
            target_date = date.today()

        logger.info(f"🚀 Processing live racing data for {target_date}")

        try:
            # Health check first
            health_status = await self.health_check_all_feeds()
            healthy_feeds = sum(1 for status in health_status.values() if status)

            if healthy_feeds == 0:
                raise Exception("No healthy feeds available")

            logger.info(f"💚 {healthy_feeds}/{len(health_status)} feeds are healthy")

            # Fetch races
            races = await self.fetch_races_for_date(target_date)

            if not races:
                logger.warning(f"⚠️ No races found for {target_date}")
                return {
                    "status": "no_data",
                    "date": target_date,
                    "races_count": 0,
                    "feed_health": health_status,
                }

            # Process and store races (would integrate with existing database schema)
            processed_count = await self._store_races_in_database(races)

            result = {
                "status": "success",
                "date": target_date,
                "races_count": len(races),
                "processed_count": processed_count,
                "feed_health": health_status,
                "feeds_used": healthy_feeds,
            }

            logger.info(
                f"✅ Successfully processed {processed_count} races for {target_date}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Failed to process live data: {e}")
            return {
                "status": "error",
                "date": target_date,
                "error": str(e),
                "feed_health": health_status if "health_status" in locals() else {},
            }

    async def _store_races_in_database(self, races: List[RaceData]) -> int:
        """Store races in the database (integration with existing schema)"""
        processed_count = 0

        for race in races:
            try:
                # This would integrate with the existing database schema
                # For now, just log the race data
                logger.info(
                    f"📝 Storing: {race.course} - {race.race_name} "
                    f"({race.runners_count} runners)"
                )
                processed_count += 1

            except Exception as e:
                logger.error(f"❌ Failed to store race {race.race_id}: {e}")

        return processed_count

    async def start_live_monitoring(self, interval_minutes: int = 15):
        """Start continuous live data monitoring"""
        self.is_running = True
        logger.info(f"🔄 Starting live monitoring (every {interval_minutes} minutes)")

        while self.is_running:
            try:
                # Process today's data
                result = await self.process_live_data(date.today())

                # Also check tomorrow's data if it's late in the day
                current_hour = datetime.now().hour
                if current_hour >= 18:  # After 6 PM, also check tomorrow
                    tomorrow = date.today() + timedelta(days=1)
                    await self.process_live_data(tomorrow)

                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"❌ Error in live monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    def stop_live_monitoring(self):
        """Stop live data monitoring"""
        self.is_running = False
        logger.info("🛑 Stopping live monitoring")

    async def cleanup(self):
        """Clean up resources"""
        # Stop monitoring
        self.stop_live_monitoring()

        # Disconnect all feeds
        for feed in self.feeds:
            await feed.disconnect()

        # Close database connection
        if self.db_manager:
            self.db_manager.close()

        logger.info("🧹 Live feed manager cleanup complete")


async def create_default_feed_manager() -> LiveFeedManager:
    """Create a feed manager with default configurations"""
    manager = LiveFeedManager()

    # Racing Post feed configuration
    racing_post_config = FeedConfig(
        name="Racing Post",
        base_url="https://api.racingpost.com/v1",
        api_key=os.getenv("RACING_POST_API_KEY"),
        rate_limit=2.0,  # 2 requests per second
        priority=1,  # Highest priority
        enabled=True,
    )

    # Timeform feed configuration
    timeform_config = FeedConfig(
        name="Timeform",
        base_url="https://api.timeform.com/v2",
        api_key=os.getenv("TIMEFORM_API_KEY"),
        rate_limit=1.5,  # 1.5 requests per second
        priority=2,  # Second priority
        enabled=True,
    )

    # Add feeds to manager
    manager.add_feed(RacingPostFeed(racing_post_config))
    manager.add_feed(TimeformFeed(timeform_config))

    return manager


async def main():
    """Test the live feed system"""
    logger.info("🚀 Testing Live Feed Integration System")

    # Create feed manager
    manager = await create_default_feed_manager()

    try:
        # Initialize
        await manager.initialize()

        # Health check
        health = await manager.health_check_all_feeds()
        print(f"📊 Feed Health: {health}")

        # Process today's data
        result = await manager.process_live_data()
        print(f"📈 Processing Result: {json.dumps(result, indent=2, default=str)}")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
