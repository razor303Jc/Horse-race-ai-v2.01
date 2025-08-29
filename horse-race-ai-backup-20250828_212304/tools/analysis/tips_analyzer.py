#!/usr/bin/env python3
"""
Daily Racing Tips Analyzer
Automatically scrapes and analyzes horse racing tips using Ollama models
"""

import json
import logging
import os
import re
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("tips_analyzer.log"), logging.StreamHandler()],
)


class OllamaTipsAnalyzer:
    def __init__(
        self,
        model_name="llama3.1:8b",
        db_path="tips_analysis.db",
        config_path="tips_analyzer_config.json",
    ):
        self.model_name = model_name
        self.db_path = db_path
        self.base_url = "http://localhost:11434"
        self.config = self.load_config(config_path)
        self.setup_database()

    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load config: {e}. Using defaults.")
            return {
                "scraping_config": {
                    "tips_sources": {
                        "racing_post_tips": {
                            "url": "https://www.racingpost.com/horse-racing-tips/",
                            "name": "Racing Post Tips",
                            "selectors": {
                                "tip_cards": ".tip-card, .race-card, .selection-card",
                                "horse_name": ".horse-name, .selection-name, h3, h4",
                                "tipster": ".tipster-name, .author, .expert",
                                "race_info": ".race-time, .course, .race-details",
                                "odds": ".odds, .price, .sp",
                                "reasoning": ".tip-reason, .comment, .analysis",
                            },
                        }
                    }
                }
            }

    def setup_database(self):
        """Initialize the tips analysis database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS racing_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horse_name TEXT,
                race_meeting TEXT,
                race_time TEXT,
                race_date TEXT,
                tipster_name TEXT,
                source TEXT,
                tip_type TEXT,
                odds TEXT,
                reasoning TEXT,
                confidence_score REAL,
                scraped_date TEXT,
                analysis TEXT,
                ai_assessment TEXT,
                value_rating REAL,
                risk_level TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_tips_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT UNIQUE,
                summary TEXT,
                best_value_tips TEXT,
                high_confidence_tips TEXT,
                tipster_performance TEXT,
                market_overview TEXT,
                created_at TEXT
            )
        """
        )

        conn.commit()
        conn.close()
        logging.info("Tips database initialized successfully")

    def check_ollama_status(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                if self.model_name in model_names:
                    logging.info(f"✅ Ollama is running with {self.model_name}")
                    return True
                else:
                    logging.error(
                        f"❌ Model {self.model_name} not found. "
                        f"Available: {model_names}"
                    )
                    return False
            else:
                logging.error(f"❌ Ollama API returned status: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Failed to connect to Ollama: {e}")
            return False

    def scrape_tips_sources(self):
        """Scrape racing tips from multiple sources"""
        all_tips = []
        sources = self.config.get("scraping_config", {}).get("tips_sources", {})

        for source_key, source_config in sources.items():
            try:
                logging.info(f"Scraping {source_config['name']}...")
                tips = self.scrape_single_tips_source(source_key, source_config)
                all_tips.extend(tips)

                # Rate limiting between sources
                time.sleep(3)

            except Exception as e:
                logging.error(f"Failed to scrape {source_config['name']}: {e}")
                continue

        logging.info(f"Found {len(all_tips)} total tips from {len(sources)} sources")
        return all_tips

    def scrape_racing_post_with_playwright(self, url):
        """Use Playwright to scrape Racing Post tips with 'Show More' functionality"""
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Set user agent to avoid detection
                page.set_extra_http_headers(
                    {
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                )

                # Navigate to the page
                page.goto(url, wait_until="networkidle")

                # Handle cookie consent banners
                try:
                    # Wait for potential cookie banners and dismiss them
                    page.wait_for_timeout(2000)

                    # First, try to remove cookie banner elements with JavaScript
                    page.evaluate(
                        """
                        const bannersToRemove = [
                            'consent_blackbar',
                            'trustarc-banner-overlay',
                            'trustarc-banner',
                            'cookie-banner',
                            'consent-banner'
                        ];
                        bannersToRemove.forEach(id => {
                            const elem = document.getElementById(id);
                            if (elem) elem.remove();
                        });
                        
                        // Also remove by class
                        const classesToRemove = [
                            'trustarc-banner',
                            'cookie-banner',
                            'consent-banner'
                        ];
                        classesToRemove.forEach(className => {
                            const elems = document.getElementsByClassName(className);
                            Array.from(elems).forEach(elem => elem.remove());
                        });
                    """
                    )

                    # Common cookie banner selectors
                    cookie_selectors = [
                        "#consent_blackbar",
                        "#trustarc-banner-overlay",
                        "[data-testid*='cookie']",
                        "[data-testid*='consent']",
                        ".cookie-banner",
                        ".consent-banner",
                        "button:has-text('Accept')",
                        "button:has-text('OK')",
                        "button:has-text('Continue')",
                        ".trustarc-banner-footer button",
                    ]

                    for selector in cookie_selectors:
                        if page.locator(selector).count() > 0:
                            try:
                                element = page.locator(selector).first
                                if element.is_visible():
                                    logging.info(
                                        f"Found cookie banner, dismissing with: "
                                        f"{selector}"
                                    )
                                    element.click()
                                    page.wait_for_timeout(1000)
                                    break
                            except Exception:
                                continue

                except Exception as e:
                    logging.warning(f"Error handling cookie banner: {e}")

                # Wait for content to load
                page.wait_for_timeout(3000)

                # Look for the "Show More" button and click it multiple times
                show_more_attempts = 0
                max_attempts = 5

                while show_more_attempts < max_attempts:
                    try:
                        # Wait for page to be fully loaded
                        page.wait_for_load_state("networkidle")

                        # Scroll down to make sure the button is visible
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2000)

                        # Try different possible selectors for the show more button
                        show_more_selectors = [
                            "button:has-text('Show more')",
                            "button:has-text('Load more')",
                            "button:has-text('View more')",
                            ".show-more-button",
                            ".load-more",
                            "[data-testid*='show-more']",
                            "[data-testid*='load-more']",
                            "[data-testid='Button__FreeShowMoreButton']",
                        ]

                        button_found = False

                        # First try regular clicking
                        for selector in show_more_selectors:
                            buttons = page.locator(selector)
                            if buttons.count() > 0:
                                for i in range(buttons.count()):
                                    button = buttons.nth(i)
                                    if button.is_visible():
                                        try:
                                            logging.info(
                                                f"Found visible 'Show More' button "
                                                f"with selector: {selector}"
                                            )
                                            button.scroll_into_view_if_needed()
                                            page.wait_for_timeout(1000)
                                            button.click()
                                            # Wait for content to load
                                            page.wait_for_timeout(3000)
                                            button_found = True
                                            break
                                        except Exception as click_error:
                                            logging.warning(
                                                f"Click failed: {click_error}"
                                            )
                                            # Try JavaScript click as fallback
                                            try:
                                                page.evaluate(
                                                    f"""
                                                    const button = (
                                                        document.querySelector(
                                                            '{selector}'
                                                        )
                                                    );
                                                    if (button) button.click();
                                                """
                                                )
                                                page.wait_for_timeout(3000)
                                                button_found = True
                                                logging.info(
                                                    f"Successfully clicked button with "
                                                    f"JavaScript: {selector}"
                                                )
                                                break
                                            except Exception as js_error:
                                                logging.warning(
                                                    f"JS click also failed: {js_error}"
                                                )
                                                continue
                                if button_found:
                                    break

                        if not button_found:
                            # Try the specific XPath provided by user
                            xpath_button = page.locator(
                                "xpath=/html/body/div[1]/div/div[2]/div/div[3]/"
                                "div[2]/div/div[1]/div[1]/div[18]/button"
                            )
                            if xpath_button.count() > 0 and xpath_button.is_visible():
                                try:
                                    logging.info(
                                        "Found visible 'Show More' button using "
                                        "provided XPath"
                                    )
                                    xpath_button.scroll_into_view_if_needed()
                                    page.wait_for_timeout(1000)
                                    xpath_button.click()
                                    page.wait_for_timeout(3000)
                                    button_found = True
                                except Exception:
                                    # Try JavaScript click with XPath
                                    try:
                                        page.evaluate(
                                            """
                                            const xpath = '/html/body/div[1]/' +
                                                'div/div[2]/div/div[3]/div[2]/' +
                                                'div/div[1]/div[1]/div[18]/button';
                                            const button = document.evaluate(
                                                xpath, document, null,
                                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                                null
                                            ).singleNodeValue;
                                            if (button) button.click();
                                        """
                                        )
                                        page.wait_for_timeout(3000)
                                        button_found = True
                                        logging.info(
                                            "Successfully clicked button with "
                                            "JavaScript XPath"
                                        )
                                    except Exception as js_xpath_error:
                                        logging.warning(
                                            f"JS XPath click failed: {js_xpath_error}"
                                        )

                        if not button_found:
                            logging.info("No more visible 'Show More' buttons found")
                            break

                        show_more_attempts += 1

                    except Exception as e:
                        logging.warning(f"Error clicking 'Show More' button: {e}")
                        break

                # Extract the tips data from div elements
                tips_data = []

                # Racing Post uses div elements, not tables
                # Look for the main container with tips
                container_selectors = [
                    (
                        "#__next > div > div:nth-child(2) > div > "
                        + "div:nth-child(3) > div:nth-child(2) > div > "
                        + "div:nth-child(1) > div:nth-child(1)"
                    ),
                    (
                        "//*[@id='__next']/div/div[2]/div/div[3]/div[2]/"
                        + "div/div[1]/div[1]"
                    ),
                    (
                        "xpath=//*[@id='__next']/div/div[2]/div/div[3]/"
                        + "div[2]/div/div[1]/div[1]"
                    ),
                ]

                tips_found = False

                # Try to find the container with tips
                for selector in container_selectors:
                    try:
                        if selector.startswith("xpath="):
                            container = page.locator(selector)
                        else:
                            container = page.locator(selector)

                        if container.count() > 0:
                            logging.info(
                                f"Found tips container with selector: {selector}"
                            )

                            # Look for divs from index 5 to 62 (where tips are)
                            for div_index in range(5, 63):  # div[5] to div[62]
                                try:
                                    tip_div = container.locator(
                                        f"> div:nth-child({div_index})"
                                    )

                                    if tip_div.count() > 0:
                                        # Extract the tip data from this div
                                        tip_element = tip_div.first

                                        # Look for horse name (link or strong element)
                                        horse_selectors = (
                                            "a, strong, .horse-name, "
                                            + "[data-testid*='horse']"
                                        )
                                        horse_element = tip_element.locator(
                                            horse_selectors
                                        ).first
                                        horse_name = "Unknown"
                                        if horse_element.count() > 0:
                                            horse_name = (
                                                horse_element.inner_text().strip()
                                            )

                                        # Look for race location and time
                                        race_selectors = (
                                            ".race-location, .track, "
                                            + "[data-testid*='race']"
                                        )
                                        race_element = tip_element.locator(
                                            race_selectors
                                        ).first
                                        race_location = "Unknown"
                                        race_time = "Unknown"
                                        if race_element.count() > 0:
                                            race_text = (
                                                race_element.inner_text().strip()
                                            )
                                            if " " in race_text and ":" in race_text:
                                                parts = race_text.split()
                                                if ":" in parts[0]:
                                                    race_time = parts[0]
                                                    race_location = " ".join(parts[1:])
                                                else:
                                                    race_location = race_text
                                            else:
                                                race_location = race_text

                                        # Look for tipster info
                                        tipster_selectors = (
                                            ".tipster, .expert, "
                                            + "[data-testid*='tipster']"
                                        )
                                        tipster_element = tip_element.locator(
                                            tipster_selectors
                                        ).first
                                        tipster_name = "Unknown"
                                        confidence = "Unknown"
                                        if tipster_element.count() > 0:
                                            tipster_text = (
                                                tipster_element.inner_text().strip()
                                            )
                                            if "," in tipster_text:
                                                parts = tipster_text.split(",", 1)
                                                tipster_name = parts[0].strip()
                                                confidence = parts[1].strip()
                                            else:
                                                tipster_name = tipster_text

                                        # Look for odds
                                        odds_selectors = (
                                            ".odds, .price, " + "[data-testid*='odds']"
                                        )
                                        odds_element = tip_element.locator(
                                            odds_selectors
                                        ).first
                                        odds = "Unknown"
                                        if odds_element.count() > 0:
                                            odds = odds_element.inner_text().strip()

                                        # If we found at least a horse name, add tip
                                        if horse_name != "Unknown" and horse_name:
                                            tips_data.append(
                                                {
                                                    "horse_name": horse_name,
                                                    "race_location": race_location,
                                                    "race_time": race_time,
                                                    "tipster_name": tipster_name,
                                                    "confidence_rating": confidence,
                                                    "odds": odds,
                                                    "source": "Racing Post",
                                                }
                                            )

                                except Exception as e:
                                    logging.debug(f"Error parsing div {div_index}: {e}")
                                    continue

                            tips_found = True
                            break

                    except Exception as e:
                        logging.warning(f"Error with selector {selector}: {e}")
                        continue

                if not tips_found:
                    # Fallback: try to extract from any div that looks like tips
                    logging.warning(
                        "No tips container found, trying generic div extraction"
                    )

                    # Look for any div that contains racing data
                    all_divs = page.locator("div")
                    for i in range(min(all_divs.count(), 100)):  # Limit search
                        try:
                            div_element = all_divs.nth(i)
                            div_text = div_element.inner_text().strip()

                            # Check if this div contains what looks like racing data
                            keywords = ["odds", "racing", "horse", "tipster"]
                            if (
                                any(keyword in div_text.lower() for keyword in keywords)
                                and len(div_text) > 10
                                and len(div_text) < 500
                            ):

                                # Try to extract structured data from this div
                                lines = div_text.split("\n")
                                if len(lines) >= 2:
                                    horse_name = (
                                        lines[0].strip() if lines[0] else "Unknown"
                                    )
                                    race_info = (
                                        lines[1].strip()
                                        if len(lines) > 1
                                        else "Unknown"
                                    )

                                    tips_data.append(
                                        {
                                            "horse_name": horse_name,
                                            "race_location": race_info,
                                            "race_time": "Unknown",
                                            "tipster_name": "Racing Post",
                                            "confidence_rating": "Unknown",
                                            "odds": "Unknown",
                                            "source": "Racing Post",
                                        }
                                    )

                        except Exception as e:
                            logging.debug(f"Error parsing fallback div {i}: {e}")
                            continue

                browser.close()

                logging.info(
                    f"Successfully extracted {len(tips_data)} tips from Racing Post "
                    f"with {show_more_attempts} 'Show More' clicks"
                )
                return tips_data

        except Exception as e:
            logging.error(f"Failed to scrape Racing Post with Playwright: {e}")
            return None

    def scrape_single_tips_source(self, source_key, source_config):
        """Scrape tips from a single source"""
        try:
            # Use Playwright for Racing Post to handle "Show More" button
            if "racing_post" in source_key.lower():
                logging.info(f"Using Playwright for {source_config['name']}")
                tips_data = self.scrape_racing_post_with_playwright(
                    source_config["url"]
                )
                if tips_data and isinstance(tips_data, list):
                    # Return the structured data directly from Playwright
                    return tips_data
                else:
                    # Fallback to regular requests if Playwright fails
                    logging.warning("Playwright failed, falling back to requests")
                    user_agent = self.config.get("scraping_config", {}).get(
                        "user_agent",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                    )
                    headers = {"User-Agent": str(user_agent)}
                    response = requests.get(
                        source_config["url"], headers=headers, timeout=30
                    )
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
            else:
                # Use regular requests for other sources
                user_agent = self.config.get("scraping_config", {}).get(
                    "user_agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                )
                headers = {"User-Agent": str(user_agent)}
                response = requests.get(
                    source_config["url"], headers=headers, timeout=30
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

            tips = []

            # Look for tip cards or selections
            selectors = source_config["selectors"]
            tip_cards = soup.select(selectors.get("tip_cards", ".tip-card"))

            for card in tip_cards[:20]:  # Limit per source
                try:
                    tip_data = self.extract_tip_data(card, selectors, source_config)
                    if tip_data and tip_data.get("horse_name"):
                        tips.append(tip_data)

                except Exception as e:
                    logging.warning(f"Error processing tip card: {e}")
                    continue

            # If no structured cards, look for general content
            if not tips:
                tips = self.extract_general_tips(soup, source_config)

            logging.info(f"Found {len(tips)} tips from {source_config['name']}")
            return tips

        except Exception as e:
            logging.error(f"Failed to scrape {source_config['name']}: {e}")
            return []

    def extract_tip_data(self, card, selectors, source_config):
        """Extract structured tip data from a card element"""
        tip_data = {
            "source": source_config["name"],
            "scraped_date": datetime.now().isoformat(),
        }

        # Extract horse name
        horse_elem = card.select_one(selectors.get("horse_name", ".horse-name"))
        if horse_elem:
            tip_data["horse_name"] = horse_elem.get_text(strip=True)

        # Extract tipster name
        tipster_elem = card.select_one(selectors.get("tipster", ".tipster"))
        if tipster_elem:
            tip_data["tipster_name"] = tipster_elem.get_text(strip=True)

        # Extract race info
        race_elem = card.select_one(selectors.get("race_info", ".race-info"))
        if race_elem:
            race_text = race_elem.get_text(strip=True)
            tip_data["race_meeting"] = self.extract_race_meeting(race_text)
            tip_data["race_time"] = self.extract_race_time(race_text)

        # Extract odds
        odds_elem = card.select_one(selectors.get("odds", ".odds"))
        if odds_elem:
            tip_data["odds"] = odds_elem.get_text(strip=True)

        # Extract reasoning
        reason_elem = card.select_one(selectors.get("reasoning", ".reasoning"))
        if reason_elem:
            tip_data["reasoning"] = reason_elem.get_text(strip=True)

        # Set today's date for race date
        tip_data["race_date"] = datetime.now().strftime("%Y-%m-%d")

        return tip_data

    def extract_general_tips(self, soup, source_config):
        """Extract tips from general page content when no structured cards"""
        tips = []

        # Look for horse names in various contexts
        text_content = soup.get_text()

        # Simple pattern matching for tips
        horse_patterns = [
            r"(\w+(?:\s+\w+){0,2})\s+(?:at|@)\s+(\d+[\/\-]\d+|\d+\.\d+)",
            r"TIP[:\s]+(\w+(?:\s+\w+){0,2})",
            r"SELECTION[:\s]+(\w+(?:\s+\w+){0,2})",
            r"NAP[:\s]+(\w+(?:\s+\w+){0,2})",
        ]

        for pattern in horse_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                horse_name = match.group(1).strip()
                if len(horse_name) > 3 and len(horse_name) < 30:
                    # Reasonable horse name length
                    tips.append(
                        {
                            "horse_name": horse_name,
                            "source": source_config["name"],
                            "scraped_date": datetime.now().isoformat(),
                            "race_date": datetime.now().strftime("%Y-%m-%d"),
                            "tip_type": "General",
                        }
                    )

        return tips[:10]  # Limit general extractions

    def extract_race_meeting(self, race_text):
        """Extract race meeting from race info text"""
        # Common race course patterns
        courses = [
            "Ascot",
            "Cheltenham",
            "Newmarket",
            "York",
            "Goodwood",
            "Epsom",
            "Doncaster",
            "Chester",
            "Sandown",
            "Kempton",
            "Lingfield",
            "Windsor",
            "Bath",
            "Brighton",
            "Catterick",
            "Ffos Las",
            "Haydock",
            "Leicester",
            "Market Rasen",
            "Newcastle",
            "Nottingham",
            "Ripon",
            "Salisbury",
            "Southwell",
            "Thirsk",
            "Uttoxeter",
            "Warwick",
            "Wetherby",
            "Wolverhampton",
            "Worcester",
        ]

        for course in courses:
            if course.lower() in race_text.lower():
                return course

        return "Unknown"

    def extract_race_time(self, race_text):
        """Extract race time from race info text"""
        time_pattern = r"(\d{1,2}):(\d{2})"
        match = re.search(time_pattern, race_text)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        return "Unknown"

    def analyze_tip_with_ollama(self, tip_data):
        """Analyze a racing tip using Ollama"""
        try:
            prompt = f"""Analyze this horse racing tip and provide assessment:

Horse: {tip_data.get('horse_name', 'Unknown')}
Meeting: {tip_data.get('race_meeting', 'Unknown')}
Time: {tip_data.get('race_time', 'Unknown')}
Tipster: {tip_data.get('tipster_name', 'Unknown')}
Odds: {tip_data.get('odds', 'Unknown')}
Reasoning: {tip_data.get('reasoning', 'No reasoning provided')}

Please provide analysis in this JSON format:
{{
    "confidence_score": <float between 0 and 1>,
    "value_rating": <float between 0 and 1>,
    "risk_level": "Low|Medium|High",
    "ai_assessment": "Brief assessment of the tip quality and reasoning",
    "key_factors": ["factor1", "factor2", "factor3"],
    "recommendation": "Strong|Moderate|Weak|Avoid"
}}"""

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "top_p": 0.9},
            }

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get("response", "")

                # Try to extract JSON from response
                try:
                    json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        return {"ai_assessment": analysis_text, "confidence_score": 0.5}
                except json.JSONDecodeError:
                    return {"ai_assessment": analysis_text, "confidence_score": 0.5}
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Failed to analyze tip with Ollama: {e}")
            return None

    def store_tip_analysis(self, tip_data, analysis):
        """Store tip and analysis in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO racing_tips
                (horse_name, race_meeting, race_time, race_date, tipster_name,
                 source, tip_type, odds, reasoning, confidence_score, scraped_date,
                 analysis, ai_assessment, value_rating, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    tip_data.get("horse_name", ""),
                    tip_data.get("race_meeting", ""),
                    tip_data.get("race_time", ""),
                    tip_data.get("race_date", ""),
                    tip_data.get("tipster_name", ""),
                    tip_data.get("source", ""),
                    tip_data.get("tip_type", "Standard"),
                    tip_data.get("odds", ""),
                    tip_data.get("reasoning", ""),
                    analysis.get("confidence_score", 0.5),
                    tip_data.get("scraped_date", ""),
                    json.dumps(analysis),
                    analysis.get("ai_assessment", ""),
                    analysis.get("value_rating", 0.5),
                    analysis.get("risk_level", "Medium"),
                ),
            )

            conn.commit()
            conn.close()
            horse_name = tip_data.get("horse_name", "Unknown")
            logging.info(f"Stored tip analysis for: {horse_name}")

        except Exception as e:
            logging.error(f"Failed to store tip analysis: {e}")

    def generate_daily_tips_report(self):
        """Generate comprehensive daily tips report"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get today's tips
            cursor.execute(
                """
                SELECT horse_name, race_meeting, race_time, tipster_name,
                       confidence_score, value_rating, risk_level, ai_assessment, odds
                FROM racing_tips
                WHERE DATE(scraped_date) = ?
                ORDER BY confidence_score DESC, value_rating DESC
            """,
                (today,),
            )

            tips = cursor.fetchall()

            if not tips:
                logging.info("No tips found for today")
                return None

            # Generate AI summary
            summary_analysis = self.analyze_daily_tips_summary(tips)

            if summary_analysis:
                # Store daily report
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_tips_reports
                    (report_date, summary, best_value_tips, high_confidence_tips,
                     tipster_performance, market_overview, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        today,
                        summary_analysis.get("summary", ""),
                        json.dumps(summary_analysis.get("best_value_tips", [])),
                        json.dumps(summary_analysis.get("high_confidence_tips", [])),
                        summary_analysis.get("tipster_performance", ""),
                        summary_analysis.get("market_overview", ""),
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()

                # Generate report file
                self.create_daily_tips_report_file(today, summary_analysis, len(tips))

            conn.close()
            return summary_analysis

        except Exception as e:
            logging.error(f"Failed to generate daily tips report: {e}")
            return None

    def create_tips_report_content(self, tips, date):
        """Create formatted tips report content"""
        content = f"# Daily Racing Tips Report - {date}\n\n"

        # High confidence tips
        high_conf_tips = [tip for tip in tips if tip[4] > 0.7]  # confidence > 0.7
        if high_conf_tips:
            content += "## 🎯 High Confidence Tips\n\n"
            for tip in high_conf_tips[:5]:
                content += f"**{tip[0]}** - {tip[1]} {tip[2]}\n"
                content += f"- Tipster: {tip[3]}\n"
                confidence = f"Confidence: {tip[4]:.2f}"
                value = f"Value: {tip[5]:.2f}"
                risk = f"Risk: {tip[6]}"
                content += f"- {confidence} | {value} | {risk}\n"
                content += f"- Assessment: {tip[7]}\n\n"

        # Best value tips
        value_tips = sorted(
            [tip for tip in tips if tip[5] > 0.6], key=lambda x: x[5], reverse=True
        )
        if value_tips:
            content += "## 💰 Best Value Tips\n\n"
            for tip in value_tips[:5]:
                content += f"**{tip[0]}** - {tip[1]} {tip[2]}\n"
                content += f"- Odds: {tip[8]} | Value Rating: {tip[5]:.2f}\n\n"

        return content

    def analyze_daily_tips_summary(self, tips):
        """Generate AI summary of daily tips"""
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            tips_summary = f"Daily Tips Summary for {today_str}:\n\n"

            for tip in tips[:10]:  # Top 10 tips
                confidence_str = f"Confidence: {tip[4]:.2f}"
                tip_line = f"- {tip[0]} at {tip[1]} ({tip[2]}) - {confidence_str}\n"
                tips_summary += tip_line

            prompt = f"""Analyze these daily racing tips and provide summary:

{tips_summary}

Please provide analysis in this JSON format:
{{
    "summary": "Overall summary of today's tips",
    "best_value_tips": ["tip1", "tip2", "tip3"],
    "high_confidence_tips": ["tip1", "tip2"],
    "tipster_performance": "Analysis of tipster quality",
    "market_overview": "Overall market assessment"
}}"""

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3},
            }

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get("response", "")

                try:
                    json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

                return {"summary": analysis_text}

        except Exception as e:
            logging.error(f"Failed to analyze daily tips summary: {e}")

        return None

    def create_daily_tips_report_file(self, date, analysis, tip_count):
        """Create a formatted daily tips report file"""
        try:
            reports_dir = Path("reports/daily_tips")
            reports_dir.mkdir(parents=True, exist_ok=True)

            report_file = reports_dir / f"racing_tips_report_{date}.md"

            report_content = f"""# Daily Racing Tips Report - {date}

## Executive Summary
{analysis.get('summary', 'No summary available')}

## Key Statistics
- **Tips Analyzed**: {tip_count}
- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Best Value Tips
"""

            for i, tip in enumerate(analysis.get("best_value_tips", []), 1):
                report_content += f"{i}. {tip}\n"

            report_content += """

## High Confidence Tips
"""
            for i, tip in enumerate(analysis.get("high_confidence_tips", []), 1):
                report_content += f"{i}. {tip}\n"

            report_content += f"""

## Tipster Performance Analysis
{analysis.get('tipster_performance', 'No performance analysis available')}

## Market Overview
{analysis.get('market_overview', 'No market overview available')}

---
*Report generated automatically by Racing Tips Analyzer using {self.model_name}*
"""

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            logging.info(f"Daily tips report saved to: {report_file}")
            return str(report_file)

        except Exception as e:
            logging.error(f"Failed to create daily tips report file: {e}")
            return None

    def run_daily_tips_analysis(self):
        """Run the complete daily tips analysis process"""
        logging.info("🏇 Starting Daily Racing Tips Analysis")

        # Check Ollama status
        if not self.check_ollama_status():
            logging.error("Cannot proceed without Ollama. Exiting.")
            return False

        # Scrape tips from all sources
        tips = self.scrape_tips_sources()
        if not tips:
            logging.warning("No tips found to analyze")
            return False

        analyzed_count = 0

        # Analyze each tip
        for tip in tips:
            try:
                # Check if already analyzed today
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM racing_tips WHERE horse_name = ? AND race_date = ?",
                    (tip.get("horse_name", ""), tip.get("race_date", "")),
                )
                existing = cursor.fetchone()
                conn.close()

                if existing:
                    logging.info(
                        f"Tip already analyzed: {tip.get('horse_name', 'Unknown')}"
                    )
                    continue

                # Analyze with Ollama
                analysis = self.analyze_tip_with_ollama(tip)
                if analysis:
                    self.store_tip_analysis(tip, analysis)
                    analyzed_count += 1
                    logging.info(
                        f"✅ Analyzed tip: {tip.get('horse_name', 'Unknown')} "
                        f"({tip.get('source', 'Unknown')})"
                    )
                else:
                    logging.warning(
                        f"Failed to analyze tip: {tip.get('horse_name', 'Unknown')}"
                    )

                # Rate limiting
                analyzer_config = self.config.get("analyzer_config", {})
                rate_limit = analyzer_config.get("rate_limit_seconds", 3)
                if isinstance(rate_limit, (int, float)):
                    time.sleep(rate_limit)
                else:
                    time.sleep(3)  # Default fallback

            except Exception as e:
                logging.error(
                    f"Error processing tip {tip.get('horse_name', 'Unknown')}: {e}"
                )
                continue

        # Generate daily report
        if analyzed_count > 0:
            daily_report = self.generate_daily_tips_report()
            if daily_report:
                logging.info("✅ Daily tips report generated successfully")
            else:
                logging.warning("Failed to generate daily tips report")

        logging.info(
            f"🏆 Daily tips analysis complete. Analyzed {analyzed_count} new tips."
        )
        return True


if __name__ == "__main__":
    analyzer = OllamaTipsAnalyzer()
    analyzer.run_daily_tips_analysis()
