#!/usr/bin/env python3
"""
Live Race Data API Integration
=============================

Connects to live racing data feeds and provides real-time race information
for the 80/20 and Dutching strategy systems.

Features:
- Live race data from multiple sources
- Real-time odds updates
- Market depth monitoring
- Race result feeds
- Historical data access

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import requests
import asyncio
import websockets
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RaceData:
    """Complete race data structure"""

    race_id: str
    course: str
    race_time: datetime
    race_name: str
    race_class: str
    distance: str
    going: str
    field_size: int
    runners: List[Dict[str, Any]]
    market_id: str
    status: str  # "upcoming", "live", "finished"
    created_at: datetime


@dataclass
class RunnerData:
    """Individual runner data"""

    runner_id: str
    horse_name: str
    jockey: str
    trainer: str
    weight: str
    draw: int
    age: int
    form: str
    odds: float
    back_price: float
    lay_price: float
    volume: float
    last_traded: float
    reduction_factor: float = 1.0


@dataclass
class MarketData:
    """Market data for a race"""

    market_id: str
    race_id: str
    market_type: str  # "WIN", "PLACE", "EACH_WAY"
    status: str
    runners: List[RunnerData]
    total_matched: float
    last_update: datetime


class LiveRaceDataAPI:
    """Live race data API integration"""

    def __init__(self, config_path: str = "config/race_data_api_config.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.websocket_clients = {}
        self.data_cache = {}
        self.callbacks = []

        # API endpoints
        self.base_url = self.config.get("base_url", "https://api.theracingapi.com")
        self.api_key = self.config.get("api_key", "")

        # Set up session headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "HorseRacingAI-V2.03",
            }
        )

        logger.info("Live Race Data API initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load API configuration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {
                "base_url": "https://api.theracingapi.com",
                "api_key": "",
                "betfair_app_key": "",
                "betfair_username": "",
                "betfair_password": "",
                "update_interval": 30,
                "max_retries": 3,
            }

    def get_todays_races(self, country: str = "GB") -> List[RaceData]:
        """Get today's race schedule"""
        try:
            endpoint = f"{self.base_url}/v1/races/today"
            params = {"country": country, "include_runners": True, "include_odds": True}

            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            races_data = response.json()
            races = []

            for race_info in races_data.get("races", []):
                race = self._parse_race_data(race_info)
                if race:
                    races.append(race)
                    self.data_cache[race.race_id] = race

            logger.info(f"Retrieved {len(races)} races for today")
            return races

        except Exception as e:
            logger.error(f"Error fetching today's races: {e}")
            return []

    def get_race_details(self, race_id: str) -> Optional[RaceData]:
        """Get detailed race information"""
        try:
            endpoint = f"{self.base_url}/v1/races/{race_id}"
            params = {
                "include_runners": True,
                "include_odds": True,
                "include_form": True,
            }

            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            race_data = response.json()
            race = self._parse_race_data(race_data)

            if race:
                self.data_cache[race_id] = race

            return race

        except Exception as e:
            logger.error(f"Error fetching race details for {race_id}: {e}")
            return None

    def get_live_odds(self, race_id: str) -> Optional[MarketData]:
        """Get live odds for a race"""
        try:
            endpoint = f"{self.base_url}/v1/markets/{race_id}/odds"

            response = self.session.get(endpoint)
            response.raise_for_status()

            odds_data = response.json()
            market = self._parse_market_data(odds_data)

            return market

        except Exception as e:
            logger.error(f"Error fetching live odds for {race_id}: {e}")
            return None

    def _parse_race_data(self, race_info: Dict[str, Any]) -> Optional[RaceData]:
        """Parse race data from API response"""
        try:
            runners = []
            for runner_info in race_info.get("runners", []):
                runner = RunnerData(
                    runner_id=runner_info.get("runner_id", ""),
                    horse_name=runner_info.get("horse_name", ""),
                    jockey=runner_info.get("jockey", ""),
                    trainer=runner_info.get("trainer", ""),
                    weight=runner_info.get("weight", ""),
                    draw=runner_info.get("draw", 0),
                    age=runner_info.get("age", 0),
                    form=runner_info.get("form", ""),
                    odds=float(runner_info.get("odds", 0.0)),
                    back_price=float(runner_info.get("back_price", 0.0)),
                    lay_price=float(runner_info.get("lay_price", 0.0)),
                    volume=float(runner_info.get("volume", 0.0)),
                    last_traded=float(runner_info.get("last_traded", 0.0)),
                )
                runners.append(runner)

            race = RaceData(
                race_id=race_info.get("race_id", ""),
                course=race_info.get("course", ""),
                race_time=datetime.fromisoformat(race_info.get("race_time", "")),
                race_name=race_info.get("race_name", ""),
                race_class=race_info.get("race_class", ""),
                distance=race_info.get("distance", ""),
                going=race_info.get("going", ""),
                field_size=len(runners),
                runners=[asdict(r) for r in runners],
                market_id=race_info.get("market_id", ""),
                status=race_info.get("status", "upcoming"),
                created_at=datetime.now(),
            )

            return race

        except Exception as e:
            logger.error(f"Error parsing race data: {e}")
            return None

    def _parse_market_data(self, market_info: Dict[str, Any]) -> Optional[MarketData]:
        """Parse market data from API response"""
        try:
            runners = []
            for runner_info in market_info.get("runners", []):
                runner = RunnerData(
                    runner_id=runner_info.get("runner_id", ""),
                    horse_name=runner_info.get("horse_name", ""),
                    jockey="",
                    trainer="",
                    weight="",
                    draw=0,
                    age=0,
                    form="",
                    odds=float(runner_info.get("odds", 0.0)),
                    back_price=float(runner_info.get("back_price", 0.0)),
                    lay_price=float(runner_info.get("lay_price", 0.0)),
                    volume=float(runner_info.get("volume", 0.0)),
                    last_traded=float(runner_info.get("last_traded", 0.0)),
                )
                runners.append(runner)

            market = MarketData(
                market_id=market_info.get("market_id", ""),
                race_id=market_info.get("race_id", ""),
                market_type=market_info.get("market_type", "WIN"),
                status=market_info.get("status", "active"),
                runners=runners,
                total_matched=float(market_info.get("total_matched", 0.0)),
                last_update=datetime.now(),
            )

            return market

        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            return None

    async def start_live_feed(self, race_ids: List[str]):
        """Start live data feed for specified races"""
        try:
            for race_id in race_ids:
                await self._connect_websocket(race_id)

            logger.info(f"Started live feed for {len(race_ids)} races")

        except Exception as e:
            logger.error(f"Error starting live feed: {e}")

    async def _connect_websocket(self, race_id: str):
        """Connect to websocket for live updates"""
        try:
            ws_url = f"wss://stream.theracingapi.com/v1/races/{race_id}/odds"

            async with websockets.connect(ws_url) as websocket:
                self.websocket_clients[race_id] = websocket

                async for message in websocket:
                    data = json.loads(message)
                    await self._handle_live_update(race_id, data)

        except Exception as e:
            logger.error(f"WebSocket error for race {race_id}: {e}")

    async def _handle_live_update(self, race_id: str, data: Dict[str, Any]):
        """Handle live data updates"""
        try:
            # Update cached data
            if race_id in self.data_cache:
                # Update odds and market data
                for runner_update in data.get("runners", []):
                    self._update_runner_odds(race_id, runner_update)

            # Notify callbacks
            for callback in self.callbacks:
                await callback(race_id, data)

        except Exception as e:
            logger.error(f"Error handling live update: {e}")

    def _update_runner_odds(self, race_id: str, runner_update: Dict[str, Any]):
        """Update runner odds in cache"""
        try:
            race = self.data_cache.get(race_id)
            if not race:
                return

            runner_id = runner_update.get("runner_id")
            for runner in race.runners:
                if runner.get("runner_id") == runner_id:
                    runner.update(
                        {
                            "odds": float(
                                runner_update.get("odds", runner.get("odds", 0.0))
                            ),
                            "back_price": float(
                                runner_update.get(
                                    "back_price", runner.get("back_price", 0.0)
                                )
                            ),
                            "lay_price": float(
                                runner_update.get(
                                    "lay_price", runner.get("lay_price", 0.0)
                                )
                            ),
                            "volume": float(
                                runner_update.get("volume", runner.get("volume", 0.0))
                            ),
                            "last_traded": float(
                                runner_update.get(
                                    "last_traded", runner.get("last_traded", 0.0)
                                )
                            ),
                        }
                    )
                    break

        except Exception as e:
            logger.error(f"Error updating runner odds: {e}")

    def register_callback(self, callback):
        """Register callback for live updates"""
        self.callbacks.append(callback)

    def get_upcoming_races(self, hours_ahead: int = 4) -> List[RaceData]:
        """Get races in the next N hours"""
        try:
            now = datetime.now()
            cutoff = now + timedelta(hours=hours_ahead)

            races = []
            for race in self.data_cache.values():
                if now <= race.race_time <= cutoff:
                    races.append(race)

            # Sort by race time
            races.sort(key=lambda x: x.race_time)

            return races

        except Exception as e:
            logger.error(f"Error getting upcoming races: {e}")
            return []

    def get_race_results(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race results"""
        try:
            endpoint = f"{self.base_url}/v1/races/{race_id}/results"

            response = self.session.get(endpoint)
            response.raise_for_status()

            results = response.json()
            return results

        except Exception as e:
            logger.error(f"Error fetching race results for {race_id}: {e}")
            return None

    def close_connections(self):
        """Close all connections"""
        for race_id, websocket in self.websocket_clients.items():
            try:
                asyncio.create_task(websocket.close())
            except:
                pass

        self.websocket_clients.clear()
        logger.info("Closed all race data connections")


class RaceDataIntegrator:
    """Integrates race data with strategy systems"""

    def __init__(self, api: LiveRaceDataAPI):
        self.api = api
        self.active_races = {}
        self.monitoring_thread = None
        self.monitoring_active = False

        # Register for live updates
        self.api.register_callback(self._handle_race_update)

        logger.info("Race Data Integrator initialized")

    def start_monitoring(self):
        """Start race data monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        logger.info("Race data monitoring started")

    def stop_monitoring(self):
        """Stop race data monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        self.api.close_connections()
        logger.info("Race data monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Refresh today's races every 5 minutes
                races = self.api.get_todays_races()

                # Update active races
                for race in races:
                    if race.status in ["upcoming", "live"]:
                        self.active_races[race.race_id] = race

                # Start live feeds for races starting in next 2 hours
                upcoming_races = self.api.get_upcoming_races(hours_ahead=2)
                race_ids = [race.race_id for race in upcoming_races]

                if race_ids:
                    asyncio.run(self.api.start_live_feed(race_ids))

                time.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute on error

    async def _handle_race_update(self, race_id: str, data: Dict[str, Any]):
        """Handle live race updates"""
        try:
            logger.debug(f"Live update for race {race_id}: {data}")

            # Update active races cache
            if race_id in self.active_races:
                race = self.active_races[race_id]
                # Update race status and odds
                race.status = data.get("status", race.status)

            # Additional processing can be added here
            # e.g., trigger strategy calculations, send alerts

        except Exception as e:
            logger.error(f"Error handling race update: {e}")

    def get_race_for_strategy(self, race_id: str) -> Optional[RaceData]:
        """Get race data formatted for strategy systems"""
        try:
            race = self.active_races.get(race_id)
            if not race:
                race = self.api.get_race_details(race_id)

            return race

        except Exception as e:
            logger.error(f"Error getting race for strategy: {e}")
            return None

    def get_available_races(self) -> List[Dict[str, Any]]:
        """Get summary of available races"""
        races_summary = []

        for race in self.active_races.values():
            summary = {
                "race_id": race.race_id,
                "course": race.course,
                "race_time": race.race_time.isoformat(),
                "race_name": race.race_name,
                "field_size": race.field_size,
                "status": race.status,
                "going": race.going,
                "distance": race.distance,
            }
            races_summary.append(summary)

        # Sort by race time
        races_summary.sort(key=lambda x: x["race_time"])

        return races_summary


# Example configuration file creation
def create_race_data_config():
    """Create example race data API configuration"""
    config = {
        "base_url": "https://api.theracingapi.com",
        "api_key": "YOUR_API_KEY_HERE",
        "betfair_app_key": "YOUR_BETFAIR_APP_KEY",
        "betfair_username": "YOUR_BETFAIR_USERNAME",
        "betfair_password": "YOUR_BETFAIR_PASSWORD",
        "update_interval": 30,
        "max_retries": 3,
        "sources": {
            "primary": "racing_api",
            "secondary": "betfair",
            "backup": "oddschecker",
        },
        "race_filters": {
            "countries": ["GB", "IRE"],
            "race_types": ["FLAT", "JUMPS"],
            "min_field_size": 4,
            "max_field_size": 40,
        },
    }

    config_path = "config/race_data_api_config.json"
    os.makedirs("config", exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"Created race data API config: {config_path}")
    return config_path


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)

    # Create config if not exists
    create_race_data_config()

    # Initialize API
    api = LiveRaceDataAPI()
    integrator = RaceDataIntegrator(api)

    # Start monitoring
    integrator.start_monitoring()

    try:
        # Get today's races
        races = api.get_todays_races()
        print(f"Found {len(races)} races today")

        for race in races[:3]:  # Show first 3
            print(f"Race: {race.course} - {race.race_name} at {race.race_time}")
            print(f"Field size: {race.field_size}, Going: {race.going}")
            print()

        # Keep running for demo
        print("Monitoring live... Press Ctrl+C to stop")
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        integrator.stop_monitoring()
