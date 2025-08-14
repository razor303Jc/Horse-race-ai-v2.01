#!/usr/bin/env python3
"""
Daily Racing News Analyzer
Automatically scrapes and analyzes Racing Post news using Ollama models
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import ntfy client for notifications
try:
    from horse_racing_ai.notifications.ntfy_client import (
        NotificationMessage,
        ntfy_client,
    )

    NTFY_AVAILABLE = True
except ImportError:
    logging.warning("NTFY client not available - notifications disabled")
    NTFY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("news_analyzer.log"), logging.StreamHandler()],
)


class OllamaNewsAnalyzer:
    def __init__(
        self,
        model_name="llama3.1:8b",
        db_path="news_analysis.db",
        config_path="news_analyzer_config.json",
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
                    "news_sources": {
                        "racing_post": {
                            "url": "https://www.racingpost.com/news/",
                            "name": "Racing Post",
                            "selectors": {
                                "article_links": "a[href*='/news/']",
                                "content": [
                                    "article",
                                    ".article-content",
                                    ".story-content",
                                ],
                            },
                        }
                    }
                }
            }

    def setup_database(self):
        """Initialize the news analysis database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                source TEXT,
                published_date TEXT,
                scraped_date TEXT,
                analysis TEXT,
                sentiment_score REAL,
                key_topics TEXT,
                horse_names TEXT,
                jockey_names TEXT,
                trainer_names TEXT,
                race_meetings TEXT,
                market_insights TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT UNIQUE,
                summary TEXT,
                key_stories TEXT,
                market_trends TEXT,
                upcoming_races TEXT,
                sentiment_overview TEXT,
                created_at TEXT
            )
        """
        )

        conn.commit()
        conn.close()
        logging.info("Database initialized successfully")

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
                        f"❌ Model {self.model_name} not found. Available: {model_names}"
                    )
                    return False
            else:
                logging.error(f"❌ Ollama API returned status: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Failed to connect to Ollama: {e}")
            return False

    async def send_notification(self, title, message, priority="default", tags=None):
        """Send notification via NTFY"""
        if not NTFY_AVAILABLE:
            logging.debug("NTFY not available, skipping notification")
            return False

        try:
            notification = NotificationMessage(
                title=title,
                message=message,
                priority=priority,
                tags=tags or ["📰", "news"],
            )
            return await ntfy_client.send_notification(notification)
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")
            return False

    async def send_analysis_summary(self, articles_analyzed, sentiment_avg):
        """Send summary notification of daily analysis"""
        if articles_analyzed == 0:
            return False

        # Determine emoji and priority based on sentiment
        if sentiment_avg > 0.6:
            emoji = "📈"
            sentiment_desc = "Positive"
            priority = "default"
        elif sentiment_avg < 0.4:
            emoji = "📉"
            sentiment_desc = "Negative"
            priority = "high"
        else:
            emoji = "📊"
            sentiment_desc = "Neutral"
            priority = "default"

        title = f"{emoji} Daily Racing News Analysis Complete"
        message = (
            f"Analyzed {articles_analyzed} articles\n"
            f"Average Sentiment: {sentiment_desc} ({sentiment_avg:.2f})\n"
            f"Report available in dashboard"
        )

        return await self.send_notification(
            title, message, priority, ["📰", "daily-summary"]
        )

    async def send_article_alert(self, article_data, analysis_data):
        """Send notification for high-impact articles"""
        try:
            sentiment = analysis_data.get("sentiment_score", 0.5)
            horses = analysis_data.get("horse_names", [])

            # Only send alerts for significant news
            if sentiment > 0.8 or sentiment < 0.2 or len(horses) > 2:
                priority = "high" if sentiment > 0.8 or sentiment < 0.2 else "default"

                title = f"🏇 Racing News Alert: {article_data.get('source', 'Unknown')}"
                message = f"{article_data.get('title', 'No title')}\n"

                if horses:
                    message += f"Horses: {', '.join(horses[:3])}\n"
                message += f"Sentiment: {sentiment:.2f}"

                return await self.send_notification(
                    title, message, priority, ["🏇", "breaking", "high-impact"]
                )
        except Exception as e:
            logging.error(f"Failed to send article alert: {e}")
        return False

    def _run_async_notification(self, coro):
        """Helper to run async notifications in sync context"""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(coro)
            else:
                # If no loop or not running, run directly
                loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(coro)

    def scrape_news_sources(self):
        """Scrape latest news from multiple sources"""
        all_articles = []
        sources = self.config.get("scraping_config", {}).get("news_sources", {})
        max_per_source = self.config.get("scraping_config", {}).get(
            "max_articles_per_source", 5
        )

        for source_key, source_config in sources.items():
            try:
                logging.info(f"Scraping {source_config['name']}...")
                articles = self.scrape_single_source(
                    source_key, source_config, max_per_source
                )
                all_articles.extend(articles)

                # Rate limiting between sources
                time.sleep(2)

            except Exception as e:
                logging.error(f"Failed to scrape {source_config['name']}: {e}")
                continue

        logging.info(
            f"Found {len(all_articles)} total articles from {len(sources)} sources"
        )
        return all_articles

    def scrape_single_source(self, source_key, source_config, max_articles):
        """Scrape articles from a single news source"""
        try:
            headers = {
                "User-Agent": self.config.get("scraping_config", {}).get(
                    "user_agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                )
            }

            response = requests.get(source_config["url"], headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Get article links using source-specific selector
            link_selector = source_config["selectors"]["article_links"]
            news_links = soup.select(link_selector)

            for link in news_links[:max_articles]:
                try:
                    url = link.get("href")
                    if not url:
                        continue

                    # Handle relative URLs
                    if url.startswith("/"):
                        from urllib.parse import urljoin

                        url = urljoin(source_config["url"], url)
                    elif not url.startswith("http"):
                        continue

                    title = link.get_text(strip=True)
                    if len(title) > 10:  # Filter out short/empty titles
                        articles.append(
                            {
                                "url": url,
                                "title": title,
                                "source": source_config["name"],
                                "source_key": source_key,
                                "scraped_date": datetime.now().isoformat(),
                            }
                        )

                except Exception as e:
                    logging.warning(
                        f"Error processing link from {source_config['name']}: {e}"
                    )
                    continue

            logging.info(f"Found {len(articles)} articles from {source_config['name']}")
            return articles

        except Exception as e:
            logging.error(f"Failed to scrape {source_config['name']}: {e}")
            return []

    def scrape_article_content(self, url, source_key=None):
        """Scrape full content of a specific article"""
        try:
            headers = {
                "User-Agent": self.config.get("scraping_config", {}).get(
                    "user_agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                )
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            content = ""

            # Try source-specific selectors first
            if source_key and source_key in self.config.get("scraping_config", {}).get(
                "news_sources", {}
            ):
                source_config = self.config["scraping_config"]["news_sources"][
                    source_key
                ]
                content_selectors = source_config["selectors"]["content"]

                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        break

            # Fallback to generic selectors
            if not content:
                fallback_selectors = [
                    "article",
                    ".article-content",
                    ".story-content",
                    ".news-content",
                    ".article-body",
                    ".story-body",
                    '[data-testid="article-content"]',
                    ".content-body",
                    ".post-content",
                ]

                for selector in fallback_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        break

            # Final fallback: get all paragraph text
            if not content:
                paragraphs = soup.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs])

            # Limit content length
            max_length = self.config.get("analyzer_config", {}).get(
                "content_max_length", 5000
            )
            return content[:max_length]

        except Exception as e:
            logging.error(f"Failed to scrape article content from {url}: {e}")
            return ""

    def analyze_with_ollama(self, text, analysis_type="general"):
        """Analyze text using Ollama model"""
        try:
            prompts = {
                "general": f"""Analyze this horse racing news article and extract key information:

Article: {text}

Please provide analysis in this JSON format:
{{
    "sentiment_score": <float between -1 and 1>,
    "key_topics": ["topic1", "topic2", "topic3"],
    "horse_names": ["horse1", "horse2"],
    "jockey_names": ["jockey1", "jockey2"],
    "trainer_names": ["trainer1", "trainer2"],
    "race_meetings": ["meeting1", "meeting2"],
    "market_insights": ["insight1", "insight2"],
    "summary": "Brief summary of the article"
}}""",
                "daily_summary": f"""Create a comprehensive daily summary of these horse racing news articles:

{text}

Please provide analysis in this JSON format:
{{
    "summary": "Overall summary of the day's news",
    "key_stories": ["story1", "story2", "story3"],
    "market_trends": ["trend1", "trend2"],
    "upcoming_races": ["race1", "race2"],
    "sentiment_overview": "Overall market sentiment"
}}""",
            }

            prompt = prompts.get(analysis_type, prompts["general"])

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
                    # Look for JSON in the response
                    json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        return {"summary": analysis_text, "raw_response": analysis_text}
                except json.JSONDecodeError:
                    return {"summary": analysis_text, "raw_response": analysis_text}
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Failed to analyze with Ollama: {e}")
            return None

    def store_article_analysis(self, article, analysis):
        """Store article and analysis in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO news_articles 
                (url, title, content, source, published_date, scraped_date, analysis, 
                 sentiment_score, key_topics, horse_names, jockey_names, 
                 trainer_names, race_meetings, market_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    article["url"],
                    article["title"],
                    article.get("content", ""),
                    article.get("source", "Unknown"),
                    article.get("published_date", ""),
                    article["scraped_date"],
                    json.dumps(analysis),
                    analysis.get("sentiment_score", 0.0),
                    json.dumps(analysis.get("key_topics", [])),
                    json.dumps(analysis.get("horse_names", [])),
                    json.dumps(analysis.get("jockey_names", [])),
                    json.dumps(analysis.get("trainer_names", [])),
                    json.dumps(analysis.get("race_meetings", [])),
                    json.dumps(analysis.get("market_insights", [])),
                ),
            )

            conn.commit()
            conn.close()
            logging.info(f"Stored analysis for: {article['title']}")

        except Exception as e:
            logging.error(f"Failed to store article analysis: {e}")

    def generate_daily_report(self):
        """Generate comprehensive daily report"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get today's articles
            cursor.execute(
                """
                SELECT title, analysis, sentiment_score 
                FROM news_articles 
                WHERE DATE(scraped_date) = ?
                ORDER BY scraped_date DESC
            """,
                (today,),
            )

            articles = cursor.fetchall()

            if not articles:
                logging.info("No articles found for today")
                return None

            # Combine all article content for daily summary
            combined_content = f"Daily Racing News Summary for {today}:\n\n"
            total_sentiment = 0

            for title, analysis_json, sentiment in articles:
                try:
                    analysis = json.loads(analysis_json) if analysis_json else {}
                    combined_content += f"- {title}\n"
                    combined_content += (
                        f"  Summary: {analysis.get('summary', 'No summary')}\n\n"
                    )
                    total_sentiment += sentiment or 0
                except:
                    combined_content += f"- {title}\n\n"

            # Generate comprehensive analysis
            daily_analysis = self.analyze_with_ollama(combined_content, "daily_summary")

            if daily_analysis:
                # Store daily report
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_reports 
                    (report_date, summary, key_stories, market_trends, 
                     upcoming_races, sentiment_overview, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        today,
                        daily_analysis.get("summary", ""),
                        json.dumps(daily_analysis.get("key_stories", [])),
                        json.dumps(daily_analysis.get("market_trends", [])),
                        json.dumps(daily_analysis.get("upcoming_races", [])),
                        daily_analysis.get("sentiment_overview", ""),
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()

                # Generate report file
                self.create_daily_report_file(
                    today,
                    daily_analysis,
                    len(articles),
                    total_sentiment / len(articles),
                )

            conn.close()
            return daily_analysis

        except Exception as e:
            logging.error(f"Failed to generate daily report: {e}")
            return None

    def create_daily_report_file(self, date, analysis, article_count, avg_sentiment):
        """Create a formatted daily report file"""
        try:
            reports_dir = Path("reports/daily_news")
            reports_dir.mkdir(parents=True, exist_ok=True)

            report_file = reports_dir / f"racing_news_report_{date}.md"

            report_content = f"""# Daily Racing News Report - {date}

## Executive Summary
{analysis.get('summary', 'No summary available')}

## Key Statistics
- **Articles Analyzed**: {article_count}
- **Average Sentiment**: {avg_sentiment:.2f} ({self.sentiment_label(avg_sentiment)})
- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Stories
"""

            for i, story in enumerate(analysis.get("key_stories", []), 1):
                report_content += f"{i}. {story}\n"

            report_content += f"""

## Market Trends
"""
            for i, trend in enumerate(analysis.get("market_trends", []), 1):
                report_content += f"{i}. {trend}\n"

            report_content += f"""

## Upcoming Races to Watch
"""
            for i, race in enumerate(analysis.get("upcoming_races", []), 1):
                report_content += f"{i}. {race}\n"

            report_content += f"""

## Market Sentiment Overview
{analysis.get('sentiment_overview', 'No sentiment overview available')}

---
*Report generated automatically by Racing News Analyzer using {self.model_name}*
"""

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            logging.info(f"Daily report saved to: {report_file}")
            return str(report_file)

        except Exception as e:
            logging.error(f"Failed to create daily report file: {e}")
            return None

    def sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score > 0.3:
            return "Positive"
        elif score < -0.3:
            return "Negative"
        else:
            return "Neutral"

    def run_daily_analysis(self):
        """Run the complete daily analysis process"""
        logging.info("🏇 Starting Daily Racing News Analysis")

        # Check Ollama status
        if not self.check_ollama_status():
            logging.error("Cannot proceed without Ollama. Exiting.")
            return False

        # Scrape news articles from all sources
        articles = self.scrape_news_sources()
        if not articles:
            logging.warning("No articles found to analyze")
            return False

        analyzed_count = 0

        # Analyze each article
        for article in articles:
            try:
                # Check if already analyzed today
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM news_articles WHERE url = ?", (article["url"],)
                )
                existing = cursor.fetchone()
                conn.close()

                if existing:
                    logging.info(f"Article already analyzed: {article['title']}")
                    continue

                # Scrape full content
                content = self.scrape_article_content(
                    article["url"], article.get("source_key")
                )
                if content:
                    article["content"] = content

                    # Analyze with Ollama
                    analysis = self.analyze_with_ollama(content)
                    if analysis:
                        self.store_article_analysis(article, analysis)
                        analyzed_count += 1
                        logging.info(
                            f"✅ Analyzed: {article['title']} ({article['source']})"
                        )

                        # Send notification for high-impact articles
                        self._run_async_notification(
                            self.send_article_alert(article, analysis)
                        )

                    else:
                        logging.warning(f"Failed to analyze: {article['title']}")

                # Rate limiting
                rate_limit = self.config.get("analyzer_config", {}).get(
                    "rate_limit_seconds", 2
                )
                time.sleep(rate_limit)

            except Exception as e:
                logging.error(
                    f"Error processing article {article.get('title', 'Unknown')}: {e}"
                )
                continue

        # Generate daily report
        if analyzed_count > 0:
            daily_report = self.generate_daily_report()
            if daily_report:
                logging.info("✅ Daily report generated successfully")

                # Calculate average sentiment for notification
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT AVG(sentiment_score) 
                        FROM news_articles 
                        WHERE scraped_date = ?
                        """,
                        (datetime.now().strftime("%Y-%m-%d"),),
                    )
                    avg_sentiment = cursor.fetchone()[0] or 0.5
                    conn.close()

                    # Send daily summary notification
                    self._run_async_notification(
                        self.send_analysis_summary(analyzed_count, avg_sentiment)
                    )
                except Exception as e:
                    logging.error(f"Failed to send summary notification: {e}")

            else:
                logging.warning("Failed to generate daily report")

        logging.info(
            f"🏆 Daily analysis complete. Analyzed {analyzed_count} new articles."
        )
        return True


if __name__ == "__main__":
    analyzer = OllamaNewsAnalyzer()
    analyzer.run_daily_analysis()
