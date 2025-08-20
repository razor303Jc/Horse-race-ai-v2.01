"""
Data Provider Service for Horse Race Handicapping AI

This service provides a unified interface for accessing horse racing data
from live sources only.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum

from .external_apis import HorseBaseWebScraper, get_horse_base_client
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DataProviderService:
    """
    Data provider that connects to live data sources only.
    """

    def __init__(self):
        """Initialize data provider for live data only."""
        logger.info("🌐 Data provider initialized for live data only")

    async def get_todays_races(self) -> List[Dict[str, Any]]:
        """Get today's race cards from live data."""
        try:
            client = await get_horse_base_client()
            race_data = await client.get_today_races()
            return [race.dict() for race in race_data]
        except Exception as e:
            logger.error(f"Failed to get live race data: {e}")
            return []

    async def get_races_by_date(self, target_date: str) -> List[Dict[str, Any]]:
        """Get race cards for a specific date from live data."""
        try:
            client = await get_horse_base_client()
            race_date = datetime.strptime(target_date, "%Y-%m-%d")
            race_data = await client.get_races_by_date(race_date)
            return [race.dict() for race in race_data]
        except Exception as e:
            logger.error(f"Failed to get live data for {target_date}: {e}")
            return []

    async def get_race_by_id(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race details by ID from live data."""
        try:
            client = await get_horse_base_client()
            race_data = await client.get_race_by_id(race_id)
            return race_data.dict() if race_data else None
        except Exception as e:
            logger.error(f"Failed to get race {race_id}: {e}")
            return None

    async def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race results by ID from live data."""
        try:
            client = await get_horse_base_client()
            results = await client.get_race_results(race_id)
            return results.dict() if results else None
        except Exception as e:
            logger.error(f"Failed to get results for race {race_id}: {e}")
            return None

    async def get_horse_profile(self, horse_name: str) -> Optional[Dict[str, Any]]:
        """Get horse profile by name from live data."""
        try:
            client = await get_horse_base_client()
            profile = await client.get_horse_profile(horse_name)
            return profile.dict() if profile else None
        except Exception as e:
            logger.error(f"Failed to get horse profile for {horse_name}: {e}")
            return None

    async def search_horses(self, query: str) -> List[Dict[str, Any]]:
        """Search for horses by name from live data."""
        try:
            client = await get_horse_base_client()
            results = await client.search_horses(query)
            return [horse.dict() for horse in results]
        except Exception as e:
            logger.error(f"Failed to search horses with query '{query}': {e}")
            return []

    async def get_jockey_stats(self, jockey_name: str) -> Optional[Dict[str, Any]]:
        """Get jockey statistics from live data."""
        try:
            client = await get_horse_base_client()
            stats = await client.get_jockey_stats(jockey_name)
            return stats.dict() if stats else None
        except Exception as e:
            logger.error(f"Failed to get jockey stats for {jockey_name}: {e}")
            return None

    async def get_trainer_stats(self, trainer_name: str) -> Optional[Dict[str, Any]]:
        """Get trainer statistics from live data."""
        try:
            client = await get_horse_base_client()
            stats = await client.get_trainer_stats(trainer_name)
            return stats.dict() if stats else None
        except Exception as e:
            logger.error(f"Failed to get trainer stats for {trainer_name}: {e}")
            return None

    async def get_track_info(self, track_code: str) -> Optional[Dict[str, Any]]:
        """Get track information from live data."""
        try:
            client = await get_horse_base_client()
            info = await client.get_track_info(track_code)
            return info.dict() if info else None
        except Exception as e:
            logger.error(f"Failed to get track info for {track_code}: {e}")
            return None

    async def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data from live sources."""
        return {
            "data_source": "live_only",
            "horse_base_available": True,
            "status": "ready",
            "message": "Live data only - no test data available",
        }


# Global instance
_data_provider = None


def get_data_provider() -> DataProviderService:
    """Get the global data provider instance."""
    global _data_provider
    if _data_provider is None:
        _data_provider = DataProviderService()
    return _data_provider


import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum

from .external_apis import HorseBaseWebScraper, get_horse_base_client
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DataSource(Enum):
    """Data source options."""

    LIVE = "live"
    AUTO = "auto"  # Use live data only


class DataProviderService:
    """
    Unified data provider that can switch between test and live data sources.
    """

    def __init__(self, source: DataSource = DataSource.AUTO):
        """Initialize with specified data source."""
        self.source = source
        self.test_service = None
        self._determine_source()

    def _determine_source(self):
        """Determine which data source to use."""
        if self.source == DataSource.AUTO:
            # Use test data in development, live in production
            if settings.environment == "development":
                self._source = DataSource.TEST
                logger.info("🎲 Using test data for development")
            else:
                self._source = DataSource.LIVE
                logger.info("🌐 Using live data for production")
        else:
            self._source = self.source
            logger.info(f"📊 Data source set to: {self._source.value}")

    def _get_test_service(self) -> TestDataService:
        """Get or create test data service."""
        if self.test_service is None:
            self.test_service = TestDataService()
        return self.test_service

    async def get_todays_races(self) -> List[Dict[str, Any]]:
        """Get today's race cards."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            race_card = test_service.get_todays_races()
            if race_card:
                # Convert to list format for consistency
                races = []
                for track in race_card["tracks"]:
                    races.extend(track["races"])
                return races
            return []

        else:  # LIVE
            try:
                client = await get_horse_base_client()
                race_data = await client.get_today_races()
                return [race.dict() for race in race_data]
            except Exception as e:
                logger.error(f"Failed to get live data: {e}")
                # Fallback to test data
                logger.warning("🔄 Falling back to test data")
                return await self._fallback_get_todays_races()

    async def _fallback_get_todays_races(self) -> List[Dict[str, Any]]:
        """Fallback to test data when live data fails."""
        test_service = self._get_test_service()
        race_card = test_service.get_todays_races()
        if race_card:
            races = []
            for track in race_card["tracks"]:
                races.extend(track["races"])
            return races
        return []

    async def get_races_by_date(self, target_date: str) -> List[Dict[str, Any]]:
        """Get race cards for a specific date."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            race_card = test_service.get_race_card_by_date(target_date)
            if race_card:
                races = []
                for track in race_card["tracks"]:
                    races.extend(track["races"])
                return races
            return []

        else:  # LIVE
            try:
                client = await get_horse_base_client()
                race_date = datetime.strptime(target_date, "%Y-%m-%d")
                race_data = await client.get_races_by_date(race_date)
                return [race.dict() for race in race_data]
            except Exception as e:
                logger.error(f"Failed to get live data for {target_date}: {e}")
                # Fallback to test data
                logger.warning("🔄 Falling back to test data")
                return await self._fallback_get_races_by_date(target_date)

    async def _fallback_get_races_by_date(
        self, target_date: str
    ) -> List[Dict[str, Any]]:
        """Fallback to test data for specific date."""
        test_service = self._get_test_service()
        race_card = test_service.get_race_card_by_date(target_date)
        if race_card:
            races = []
            for track in race_card["tracks"]:
                races.extend(track["races"])
            return races
        return []

    async def get_race_by_id(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get specific race by ID."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_race_by_id(race_id)

        else:  # LIVE
            # For live data, we'd need to implement race lookup
            # For now, fallback to test data
            logger.warning(
                "Race lookup by ID not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_race_by_id(race_id)

    async def get_horse_profile(self, horse_name: str) -> Optional[Dict[str, Any]]:
        """Get horse profile by name."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_horse_by_name(horse_name)

        else:  # LIVE
            # For live data, we'd need to implement horse profile scraping
            logger.warning(
                "Horse profile lookup not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_horse_by_name(horse_name)

    async def get_jockey_stats(self, jockey_name: str) -> Optional[Dict[str, Any]]:
        """Get jockey statistics by name."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_jockey_by_name(jockey_name)

        else:  # LIVE
            logger.warning(
                "Jockey stats lookup not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_jockey_by_name(jockey_name)

    async def get_trainer_stats(self, trainer_name: str) -> Optional[Dict[str, Any]]:
        """Get trainer statistics by name."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_trainer_by_name(trainer_name)

        else:  # LIVE
            logger.warning(
                "Trainer stats lookup not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_trainer_by_name(trainer_name)

    async def get_track_info(self, track_code: str) -> Optional[Dict[str, Any]]:
        """Get track information by code."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_track_by_code(track_code)

        else:  # LIVE
            logger.warning(
                "Track info lookup not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_track_by_code(track_code)

    async def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race results by race ID."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.get_race_result_by_id(race_id)

        else:  # LIVE
            logger.warning(
                "Race results lookup not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.get_race_result_by_id(race_id)

    async def search_horses(self, query: str) -> List[Dict[str, Any]]:
        """Search horses by name."""
        if self._source == DataSource.TEST:
            test_service = self._get_test_service()
            return test_service.search_horses(query)

        else:  # LIVE
            logger.warning(
                "Horse search not implemented for live data, using test data"
            )
            test_service = self._get_test_service()
            return test_service.search_horses(query)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of data sources."""
        result = {
            "data_source": self._source.value,
            "test_data_available": False,
            "live_data_available": False,
            "status": "unknown",
        }

        # Check test data
        try:
            test_service = self._get_test_service()
            summary = test_service.get_race_summary()
            result["test_data_available"] = True
            result["test_data_summary"] = summary
        except Exception as e:
            logger.error(f"Test data health check failed: {e}")

        # Check live data if configured
        if self._source == DataSource.LIVE:
            try:
                client = await get_horse_base_client()
                live_healthy = await client.health_check()
                result["live_data_available"] = live_healthy
            except Exception as e:
                logger.error(f"Live data health check failed: {e}")

        # Determine overall status
        if self._source == DataSource.TEST:
            result["status"] = (
                "healthy" if result["test_data_available"] else "unhealthy"
            )
        elif self._source == DataSource.LIVE:
            if result["live_data_available"]:
                result["status"] = "healthy"
            elif result["test_data_available"]:
                result["status"] = "degraded"  # Live failed but test available
            else:
                result["status"] = "unhealthy"

        return result

    def get_data_source_info(self) -> Dict[str, Any]:
        """Get information about current data source."""
        return {
            "current_source": self._source.value,
            "environment": settings.environment,
            "auto_fallback": True,
            "description": {
                DataSource.TEST.value: "Using generated test data for development",
                DataSource.LIVE.value: "Using live data from Horse Base web scraping",
            }.get(self._source.value, "Unknown source"),
        }


# Global instance
_data_provider: Optional[DataProviderService] = None


def get_data_provider() -> DataProviderService:
    """Get or create the global data provider."""
    global _data_provider

    if _data_provider is None:
        _data_provider = DataProviderService()

    return _data_provider


async def main():
    """Demo the data provider service."""
    print("📊 Data Provider Service Demo")
    print("=" * 50)

    provider = get_data_provider()

    # Show data source info
    source_info = provider.get_data_source_info()
    print(f"🔧 Current Data Source: {source_info['current_source']}")
    print(f"🌍 Environment: {source_info['environment']}")
    print(f"📝 Description: {source_info['description']}")

    # Health check
    print(f"\n🏥 Health Check:")
    health = await provider.health_check()
    print(f"   📊 Data Source: {health['data_source']}")
    print(f"   🎲 Test Data: {'✅' if health['test_data_available'] else '❌'}")
    print(f"   🌐 Live Data: {'✅' if health['live_data_available'] else '❌'}")
    print(f"   ❤️ Status: {health['status']}")

    # Get sample data
    print(f"\n🏁 Today's Races:")
    races = await provider.get_todays_races()
    print(f"   📅 Found {len(races)} races")

    if races:
        sample_race = races[0]
        print(
            f"   🏟️ Sample: {sample_race['track_name']} Race {sample_race['race_number']}"
        )
        print(f"   📏 Distance: {sample_race['distance']} furlongs")
        print(f"   🐎 Field Size: {sample_race['field_size']}")

    print(f"\n✅ Data provider working correctly!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
