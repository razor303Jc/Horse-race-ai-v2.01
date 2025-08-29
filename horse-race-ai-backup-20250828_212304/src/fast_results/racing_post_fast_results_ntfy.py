#!/usr/bin/env python3
"""
Racing Post Fast Results Collector with NTFY Integration
=======================================================

Collects real-time race results from Racing Post and sends notifications
for AI selections using NTFY integration.

Features:
- Racing Post fast results scraping
- AI selection result tracking
- NTFY notifications for AI wins/losses
- Real-time monitoring system
- Performance analytics integration
"""

import asyncio
import logging
import json
from datetime import datetime, date
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

import aiohttp
from playwright.async_api import async_playwright, Page, BrowserContext

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class RaceResult:
    """Racing result data structure"""

    race_id: str = ""
    race_time: str = ""
    course: str = ""
    race_name: str = ""
    distance: str = ""
    going: str = ""
    class_type: str = ""
    winner: str = ""
    second: str = ""
    third: str = ""
    fourth: str = ""
    winning_margin: str = ""
    winning_time: str = ""
    starting_price: str = ""
    result_timestamp: datetime = None
    ai_prediction_match: bool = False
    ai_confidence: float = 0.0


@dataclass
class AISelectionResult:
    """AI selection result tracking"""

    selection_id: str = ""
    race_id: str = ""
    horse_name: str = ""
    predicted_position: int = 0
    actual_position: int = 0
    confidence_score: float = 0.0
    win_probability: float = 0.0
    betting_value: float = 0.0
    selection_correct: bool = False
    profit_loss: float = 0.0
    result_type: str = ""  # WIN, PLACE, LOSE
    notification_sent: bool = False


class RacingPostFastResultsCollector:
    """Fast results collector for Racing Post with NTFY integration"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.results_cache = {}
        self.ai_selections = {}
        self.setup_data_directory()

    def setup_data_directory(self):
        """Setup data directories"""
        Path("data/fast_results").mkdir(parents=True, exist_ok=True)
        Path("data/ai_selections").mkdir(parents=True, exist_ok=True)

    async def start_browser(self):
        """Start Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
            ],
        )

        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        self.page = await self.context.new_page()

        # Set up request/response monitoring
        self.page.on("response", self._handle_response)

        logger.info("Browser started for fast results collection")

    async def _handle_response(self, response):
        """Handle browser responses for API data"""
        if "racingpost.com" in response.url and "api" in response.url:
            try:
                if response.status == 200:
                    data = await response.json()
                    await self._process_api_response(response.url, data)
            except Exception as e:
                logger.debug(f"Error processing response: {e}")

    async def _process_api_response(self, url: str, data: dict):
        """Process Racing Post API responses"""
        try:
            if "results" in url:
                await self._process_results_data(data)
            elif "race" in url:
                await self._process_race_data(data)
        except Exception as e:
            logger.error(f"Error processing API response: {e}")

    async def _process_results_data(self, data: dict):
        """Process race results data"""
        if not isinstance(data, dict):
            return

        # Extract race results
        races = data.get("races", [])
        if isinstance(races, list):
            for race in races:
                await self._extract_race_result(race)

    async def _extract_race_result(self, race_data: dict):
        """Extract individual race result"""
        try:
            race_id = race_data.get("raceId", "")
            if not race_id:
                return

            # Basic race information
            result = RaceResult(
                race_id=race_id,
                race_time=race_data.get("raceTime", ""),
                course=race_data.get("course", {}).get("name", ""),
                race_name=race_data.get("raceName", ""),
                distance=race_data.get("distance", ""),
                going=race_data.get("going", ""),
                result_timestamp=datetime.now(),
            )

            # Extract finishing positions
            runners = race_data.get("runners", [])
            if runners:
                positions = sorted(runners, key=lambda x: x.get("finishPosition", 999))

                if len(positions) >= 1:
                    result.winner = positions[0].get("horseName", "")
                    result.starting_price = positions[0].get("startingPrice", "")
                    result.winning_time = positions[0].get("finishTime", "")

                if len(positions) >= 2:
                    result.second = positions[1].get("horseName", "")

                if len(positions) >= 3:
                    result.third = positions[2].get("horseName", "")

                if len(positions) >= 4:
                    result.fourth = positions[3].get("horseName", "")

            # Store result
            self.results_cache[race_id] = result

            # Check AI predictions
            await self._check_ai_predictions(result)

            # Save to file
            await self._save_result(result)

            logger.info(f"Processed result for race {race_id}: {result.winner}")

        except Exception as e:
            logger.error(f"Error extracting race result: {e}")

    async def _check_ai_predictions(self, result: RaceResult):
        """Check AI predictions against actual results"""
        race_id = result.race_id

        if race_id in self.ai_selections:
            selections = self.ai_selections[race_id]

            for selection in selections:
                await self._evaluate_ai_selection(selection, result)

    async def _evaluate_ai_selection(
        self, selection: AISelectionResult, result: RaceResult
    ):
        """Evaluate individual AI selection"""
        try:
            horse_name = selection.horse_name.lower().strip()

            # Check if horse won
            if result.winner.lower().strip() == horse_name:
                selection.actual_position = 1
                selection.selection_correct = True
                selection.result_type = "WIN"

            # Check if horse placed (top 3)
            elif (
                result.second.lower().strip() == horse_name
                or result.third.lower().strip() == horse_name
            ):
                if result.second.lower().strip() == horse_name:
                    selection.actual_position = 2
                else:
                    selection.actual_position = 3
                selection.result_type = "PLACE"

            # Check fourth place
            elif result.fourth.lower().strip() == horse_name:
                selection.actual_position = 4
                selection.result_type = "FOURTH"

            else:
                selection.actual_position = 5  # Assume unplaced
                selection.result_type = "LOSE"

            # Send NTFY notification
            await self._send_ai_result_notification(selection, result)

            # Save AI result
            await self._save_ai_result(selection)

        except Exception as e:
            logger.error(f"Error evaluating AI selection: {e}")

    async def _send_ai_result_notification(
        self, selection: AISelectionResult, result: RaceResult
    ):
        """Send NTFY notification for AI selection result"""
        try:
            from src.horse_racing_ai.notifications.ntfy_client import NTFYClient

            ntfy_client = NTFYClient()

            # Determine message type and title
            if selection.result_type == "WIN":
                message_type = "success"
                emoji = "🏆"
                title_prefix = "AI WIN!"

            elif selection.result_type == "PLACE":
                message_type = "info"
                emoji = "🥈"
                title_prefix = "AI Place"

            else:
                message_type = "info"
                emoji = "❌"
                title_prefix = "AI Loss"

            # Create race data for NTFY client
            race_data = {
                "track": result.course,
                "race_time": result.race_time,
                "race_name": result.race_name,
                "distance": result.distance,
                "horses": [
                    {"name": result.winner, "position": 1},
                    {"name": result.second, "position": 2},
                    {"name": result.third, "position": 3},
                ],
                "ai_selection": {
                    "horse": selection.horse_name,
                    "position": selection.actual_position,
                    "confidence": selection.confidence_score,
                    "win_probability": selection.win_probability,
                    "result_type": selection.result_type,
                },
            }

            # Send notification using correct interface
            await ntfy_client.send_race_alert(race_data, message_type)

            selection.notification_sent = True
            logger.info(
                f"Sent AI result notification: {title_prefix} {selection.horse_name}"
            )

        except Exception as e:
            logger.error(f"Error sending NTFY notification: {e}")
            # Create fallback simple notification
            try:
                title = f"{emoji} {title_prefix} {selection.horse_name}"
                message = (
                    f"Race: {result.course} {result.race_time}\n"
                    f"Position: {selection.actual_position}\n"
                    f"Confidence: {selection.confidence_score:.1%}"
                )

                logger.info(f"Fallback notification created: {title}")

            except Exception as fallback_error:
                logger.error(f"Error creating fallback notification: {fallback_error}")

    async def _save_result(self, result: RaceResult):
        """Save race result to file"""
        try:
            filename = f"data/fast_results/{result.race_id}_{date.today()}.json"

            result_data = {
                "race_id": result.race_id,
                "race_time": result.race_time,
                "course": result.course,
                "race_name": result.race_name,
                "distance": result.distance,
                "going": result.going,
                "winner": result.winner,
                "second": result.second,
                "third": result.third,
                "fourth": result.fourth,
                "winning_margin": result.winning_margin,
                "winning_time": result.winning_time,
                "starting_price": result.starting_price,
                "result_timestamp": result.result_timestamp.isoformat(),
                "ai_prediction_match": result.ai_prediction_match,
            }

            with open(filename, "w") as f:
                json.dump(result_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving result: {e}")

    async def _save_ai_result(self, selection: AISelectionResult):
        """Save AI selection result"""
        try:
            filename = f"data/ai_selections/{selection.selection_id}.json"

            selection_data = {
                "selection_id": selection.selection_id,
                "race_id": selection.race_id,
                "horse_name": selection.horse_name,
                "predicted_position": selection.predicted_position,
                "actual_position": selection.actual_position,
                "confidence_score": selection.confidence_score,
                "win_probability": selection.win_probability,
                "betting_value": selection.betting_value,
                "selection_correct": selection.selection_correct,
                "profit_loss": selection.profit_loss,
                "result_type": selection.result_type,
                "notification_sent": selection.notification_sent,
                "timestamp": datetime.now().isoformat(),
            }

            with open(filename, "w") as f:
                json.dump(selection_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving AI result: {e}")

    async def add_ai_selection(
        self, race_id: str, horse_name: str, confidence: float, win_probability: float
    ):
        """Add AI selection for tracking"""
        selection_id = f"{race_id}_{horse_name}_{datetime.now().strftime('%H%M%S')}"

        selection = AISelectionResult(
            selection_id=selection_id,
            race_id=race_id,
            horse_name=horse_name,
            predicted_position=1,  # Assuming win prediction
            confidence_score=confidence,
            win_probability=win_probability,
        )

        if race_id not in self.ai_selections:
            self.ai_selections[race_id] = []

        self.ai_selections[race_id].append(selection)

        logger.info(f"Added AI selection: {horse_name} in race {race_id}")

    async def start_monitoring(self, duration_hours: int = 12):
        """Start monitoring Racing Post fast results"""
        try:
            await self.start_browser()

            # Navigate to fast results page
            racing_post_url = "https://www.racingpost.com/fast-results/"
            logger.info(f"Navigating to Racing Post fast results: {racing_post_url}")
            await self.page.goto(racing_post_url)

            # Wait for page load
            await self.page.wait_for_timeout(5000)

            logger.info(f"Started monitoring fast results for {duration_hours} hours")

            # Monitor for specified duration
            end_time = datetime.now().timestamp() + (duration_hours * 3600)

            while datetime.now().timestamp() < end_time:
                try:
                    # Check for new results by looking for result elements
                    await self._check_for_new_results()

                    # Refresh page periodically
                    await self.page.reload()
                    await self.page.wait_for_timeout(30000)  # 30 second intervals

                except Exception as e:
                    logger.error(f"Error during monitoring: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retry

        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
        finally:
            await self.stop_browser()

    async def _check_for_new_results(self):
        """Check for new race results on the page"""
        try:
            # Look for result elements on Racing Post fast results page
            # This will need to be customized based on the actual page structure

            # Example selectors (will need to be updated based on actual page)
            result_selectors = [
                ".race-result",
                ".result-item",
                "[data-race-id]",
                ".race-card-result",
            ]

            for selector in result_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        logger.info(
                            f"Found {len(elements)} potential results "
                            f"with selector {selector}"
                        )
                        for element in elements:
                            await self._extract_result_from_element(element)
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {e}")

        except Exception as e:
            logger.error(f"Error checking for new results: {e}")

    async def _extract_result_from_element(self, element):
        """Extract race result from page element"""
        try:
            # Extract race data from element
            # This will need to be customized based on Racing Post's HTML structure

            # Get text content
            text_content = await element.text_content()
            if not text_content:
                return

            logger.debug(f"Processing result element: {text_content[:100]}...")

            # Try to extract structured data if available
            race_data = await element.get_attribute("data-race")
            if race_data:
                try:
                    race_info = json.loads(race_data)
                    await self._process_extracted_result(race_info)
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.debug(f"Error extracting result from element: {e}")

    async def _process_extracted_result(self, race_info: dict):
        """Process extracted race result information"""
        try:
            # Create RaceResult from extracted data
            result = RaceResult(
                race_id=race_info.get("race_id", ""),
                race_time=race_info.get("time", ""),
                course=race_info.get("course", ""),
                race_name=race_info.get("name", ""),
                winner=race_info.get("winner", ""),
                result_timestamp=datetime.now(),
            )

            # Store and check against AI predictions
            if result.race_id and result.race_id not in self.results_cache:
                self.results_cache[result.race_id] = result
                await self._check_ai_predictions(result)
                await self._save_result(result)

        except Exception as e:
            logger.error(f"Error processing extracted result: {e}")

    async def stop_browser(self):
        """Stop Playwright browser"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "playwright"):
                await self.playwright.stop()

            logger.info("Browser stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of collected results"""
        total_results = len(self.results_cache)
        ai_selections = sum(
            len(selections) for selections in self.ai_selections.values()
        )

        ai_wins = 0
        ai_places = 0
        ai_losses = 0

        for selections in self.ai_selections.values():
            for selection in selections:
                if selection.result_type == "WIN":
                    ai_wins += 1
                elif selection.result_type == "PLACE":
                    ai_places += 1
                elif selection.result_type == "LOSE":
                    ai_losses += 1

        return {
            "total_results_collected": total_results,
            "ai_selections_tracked": ai_selections,
            "ai_performance": {
                "wins": ai_wins,
                "places": ai_places,
                "losses": ai_losses,
                "win_rate": ai_wins / ai_selections if ai_selections > 0 else 0.0,
                "place_rate": (
                    (ai_wins + ai_places) / ai_selections if ai_selections > 0 else 0.0
                ),
            },
        }


# NTFY Integration Manager
# =======================


class FastResultsNTFYManager:
    """Manager for NTFY notifications with fast results"""

    def __init__(self):
        self.collector = RacingPostFastResultsCollector()

    async def setup_ai_tracking(self, monte_carlo_picks: List[Dict[str, Any]]):
        """Setup AI selection tracking from Monte Carlo picks"""
        for pick in monte_carlo_picks:
            await self.collector.add_ai_selection(
                race_id=pick["race_id"],
                horse_name=pick["horse_name"],
                confidence=pick.get("confidence_level", 0.0),
                win_probability=pick.get("win_probability", 0.0),
            )

    async def start_real_time_monitoring(self, duration_hours: int = 12):
        """Start real-time monitoring with NTFY notifications"""
        await self.collector.start_monitoring(duration_hours)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get AI performance summary"""
        return self.collector.get_results_summary()


# Demo and Testing
# ================


async def demo_fast_results_with_ntfy():
    """Demo fast results collection with NTFY integration"""
    print("🏇 Starting Fast Results + NTFY Demo")
    print("=" * 50)

    # Initialize manager
    manager = FastResultsNTFYManager()

    # Add sample AI selections for testing
    sample_picks = [
        {
            "race_id": "test_race_001",
            "horse_name": "AI Champion",
            "confidence_level": 0.85,
            "win_probability": 0.65,
        },
        {
            "race_id": "test_race_002",
            "horse_name": "Monte Carlo Star",
            "confidence_level": 0.78,
            "win_probability": 0.58,
        },
    ]

    # Setup tracking
    await manager.setup_ai_tracking(sample_picks)

    print(f"Setup tracking for {len(sample_picks)} AI selections")

    # Start monitoring (demo - short duration)
    print("Starting real-time monitoring...")
    # await manager.start_real_time_monitoring(0.1)  # 6 minutes for demo

    # Get summary
    summary = manager.get_performance_summary()
    print(f"Performance Summary: {summary}")

    print("✅ Fast Results + NTFY demo completed!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_fast_results_with_ntfy())
