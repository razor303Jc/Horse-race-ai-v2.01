#!/usr/bin/env python3
"""
External Data Integration System for Horse Racing AI V2.03
Provides integration with external data sources for enhanced predictions
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import feedparser
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
import re
import hashlib

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ExternalDataSource:
    """Configuration for external data sources"""

    source_id: str
    name: str
    source_type: str  # 'rss', 'api', 'weather', 'news', 'form'
    url: str
    update_frequency: int  # minutes
    enabled: bool
    auth_config: Optional[Dict[str, str]]
    data_mapping: Dict[str, str]
    last_updated: Optional[datetime]


@dataclass
class IntegratedDataRecord:
    """Standardized external data record"""

    record_id: str
    source_id: str
    data_type: str
    timestamp: datetime
    race_date: Optional[datetime]
    track_code: Optional[str]
    horse_name: Optional[str]
    content: Dict[str, Any]
    confidence_score: float
    processed: bool


class ExternalDataIntegrator:
    """
    External Data Integration System
    Integrates with various external data sources for enhanced predictions
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the External Data Integrator"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.cache_dir = Path(self.config.get("cache_directory", "cache/external_data"))

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize data sources
        self.data_sources = self._initialize_data_sources()

        # HTTP session for API calls
        self.session = None

        # Data processing statistics
        self.stats = {
            "records_processed": 0,
            "sources_updated": 0,
            "errors_encountered": 0,
            "last_update_cycle": None,
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "cache_directory": "cache/external_data",
            "update_interval": 300,  # 5 minutes
            "max_concurrent_requests": 5,
            "request_timeout": 30,
            "enabled_sources": [
                "racing_post_rss",
                "weather_api",
                "form_updates",
                "news_feeds",
            ],
            "data_quality": {
                "min_confidence_score": 0.7,
                "duplicate_detection": True,
                "content_validation": True,
            },
        }

    def _initialize_data_sources(self) -> List[ExternalDataSource]:
        """Initialize configured external data sources"""
        sources = []

        # Racing Post RSS Feed
        sources.append(
            ExternalDataSource(
                source_id="racing_post_rss",
                name="Racing Post RSS Feed",
                source_type="rss",
                url="https://www.racingpost.com/rss/news.xml",
                update_frequency=60,  # 1 hour
                enabled=True,
                auth_config=None,
                data_mapping={
                    "title": "headline",
                    "description": "summary",
                    "pubDate": "published_date",
                    "link": "article_url",
                },
                last_updated=None,
            )
        )

        # Weather API (OpenWeatherMap example)
        sources.append(
            ExternalDataSource(
                source_id="weather_api",
                name="Weather Data API",
                source_type="weather",
                url="https://api.openweathermap.org/data/2.5/weather",
                update_frequency=120,  # 2 hours
                enabled=self.config.get("weather_api_key") is not None,
                auth_config={"api_key": self.config.get("weather_api_key", "")},
                data_mapping={
                    "weather.main": "condition",
                    "main.temp": "temperature",
                    "main.humidity": "humidity",
                    "wind.speed": "wind_speed",
                },
                last_updated=None,
            )
        )

        # Form Updates RSS
        sources.append(
            ExternalDataSource(
                source_id="form_updates",
                name="Horse Form Updates",
                source_type="form",
                url="https://www.timeform.com/rss/news.xml",
                update_frequency=180,  # 3 hours
                enabled=True,
                auth_config=None,
                data_mapping={
                    "title": "form_update",
                    "description": "analysis",
                    "pubDate": "update_date",
                },
                last_updated=None,
            )
        )

        # News Feeds
        sources.append(
            ExternalDataSource(
                source_id="news_feeds",
                name="Racing News Aggregator",
                source_type="news",
                url="https://news.google.com/rss/search?q=horse+racing&hl=en-GB&gl=GB&ceid=GB:en",
                update_frequency=240,  # 4 hours
                enabled=True,
                auth_config=None,
                data_mapping={
                    "title": "headline",
                    "description": "content",
                    "pubDate": "news_date",
                    "source": "news_source",
                },
                last_updated=None,
            )
        )

        # Filter enabled sources
        enabled_source_ids = self.config.get("enabled_sources", [])
        return [s for s in sources if s.source_id in enabled_source_ids and s.enabled]

    async def initialize_database(self):
        """Initialize database tables for external data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # External data sources table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS external_data_sources (
                    source_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    update_frequency INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    last_updated TIMESTAMP,
                    records_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # External data records table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS external_data_records (
                    record_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    race_date DATE,
                    track_code TEXT,
                    horse_name TEXT,
                    content_json TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES external_data_sources(source_id)
                )
            """
            )

            # Indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_external_data_source ON external_data_records(source_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_external_data_timestamp ON external_data_records(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_external_data_race_date ON external_data_records(race_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_external_data_processed ON external_data_records(processed)"
            )

            conn.commit()
            conn.close()

            logger.info("External data database tables initialized")

        except Exception as e:
            logger.error(f"Error initializing external data database: {e}")
            raise

    async def start_session(self):
        """Start HTTP session for API calls"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(
                total=self.config.get("request_timeout", 30)
            )
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_rss_feed(
        self, source: ExternalDataSource
    ) -> List[IntegratedDataRecord]:
        """Fetch and parse RSS feed data"""
        records = []

        try:
            async with self.session.get(source.url) as response:
                if response.status == 200:
                    rss_content = await response.text()

                    # Parse RSS feed
                    feed = feedparser.parse(rss_content)

                    for entry in feed.entries:
                        # Extract data using mapping
                        content = {}
                        for rss_field, mapped_field in source.data_mapping.items():
                            if hasattr(entry, rss_field):
                                content[mapped_field] = getattr(entry, rss_field)

                        # Generate record ID
                        record_id = self._generate_record_id(source.source_id, content)

                        # Extract race information if possible
                        race_date, track_code, horse_name = self._extract_race_info(
                            content
                        )

                        # Calculate confidence score
                        confidence_score = self._calculate_confidence_score(
                            content, source.source_type
                        )

                        record = IntegratedDataRecord(
                            record_id=record_id,
                            source_id=source.source_id,
                            data_type=source.source_type,
                            timestamp=datetime.now(),
                            race_date=race_date,
                            track_code=track_code,
                            horse_name=horse_name,
                            content=content,
                            confidence_score=confidence_score,
                            processed=False,
                        )

                        records.append(record)

                    logger.info(
                        f"Fetched {len(records)} records from RSS feed: {source.name}"
                    )
                else:
                    logger.warning(
                        f"Failed to fetch RSS feed {source.name}: HTTP {response.status}"
                    )

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.name}: {e}")
            self.stats["errors_encountered"] += 1

        return records

    async def fetch_weather_data(
        self, source: ExternalDataSource
    ) -> List[IntegratedDataRecord]:
        """Fetch weather data for racing tracks"""
        records = []

        try:
            # Get list of tracks for weather data
            track_locations = await self._get_track_locations()

            for track_code, location in track_locations.items():
                params = {
                    "q": f"{location['city']},{location['country']}",
                    "appid": source.auth_config.get("api_key", ""),
                    "units": "metric",
                }

                try:
                    async with self.session.get(source.url, params=params) as response:
                        if response.status == 200:
                            weather_data = await response.json()

                            # Map weather data
                            content = {}
                            for api_field, mapped_field in source.data_mapping.items():
                                value = self._get_nested_value(weather_data, api_field)
                                if value is not None:
                                    content[mapped_field] = value

                            content["track_code"] = track_code
                            content["location"] = location

                            # Generate record ID
                            record_id = self._generate_record_id(
                                source.source_id,
                                {
                                    "track": track_code,
                                    "time": datetime.now().isoformat(),
                                },
                            )

                            # Calculate confidence score
                            confidence_score = self._calculate_confidence_score(
                                content, "weather"
                            )

                            record = IntegratedDataRecord(
                                record_id=record_id,
                                source_id=source.source_id,
                                data_type="weather",
                                timestamp=datetime.now(),
                                race_date=None,  # Weather is current, not race-specific
                                track_code=track_code,
                                horse_name=None,
                                content=content,
                                confidence_score=confidence_score,
                                processed=False,
                            )

                            records.append(record)

                        else:
                            logger.warning(
                                f"Failed to fetch weather for {track_code}: HTTP {response.status}"
                            )

                except Exception as e:
                    logger.warning(f"Error fetching weather for {track_code}: {e}")
                    continue

            logger.info(f"Fetched weather data for {len(records)} tracks")

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            self.stats["errors_encountered"] += 1

        return records

    async def fetch_api_data(
        self, source: ExternalDataSource
    ) -> List[IntegratedDataRecord]:
        """Fetch data from API sources"""
        if source.source_type == "weather":
            return await self.fetch_weather_data(source)
        elif source.source_type in ["rss", "news", "form"]:
            return await self.fetch_rss_feed(source)
        else:
            logger.warning(f"Unknown source type: {source.source_type}")
            return []

    def _generate_record_id(self, source_id: str, content: Dict[str, Any]) -> str:
        """Generate unique record ID based on source and content"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        hash_input = f"{source_id}:{content_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _extract_race_info(self, content: Dict[str, Any]) -> tuple:
        """Extract race information from content"""
        race_date = None
        track_code = None
        horse_name = None

        # Try to extract race date
        for date_field in ["published_date", "news_date", "update_date"]:
            if date_field in content and content[date_field]:
                try:
                    # Handle different date formats
                    date_str = str(content[date_field])
                    race_date = self._parse_date(date_str)
                    break
                except:
                    continue

        # Try to extract track and horse information from text content
        text_content = ""
        for field in ["headline", "summary", "content", "form_update"]:
            if field in content and content[field]:
                text_content += f" {content[field]}"

        if text_content:
            # Extract track codes (common UK track patterns)
            track_patterns = [
                r"\b(AYR|ASC|AIN|BAT|BEV|BRI|CAR|CHA|CHE|DAW|DON|EDI|EPS|EXE|FAK|FON|GOO|HAM|HEX|HUN|KEM|LEI|LIN|LUD|MUS|NEW|NOT|PER|PLU|PON|RED|RIP|SAL|SAN|SOU|STR|TAU|THI|UTE|WAR|WIN|WOL|YOR)\b",
                r"\b(Ascot|Aintree|Bath|Beverly|Brighton|Carlisle|Catterick|Cheltenham|Chepstow|Doncaster|Epsom|Exeter|Fakenham|Fontwell|Goodwood|Hamilton|Haydock|Hereford|Hexham|Huntingdon|Kempton|Leicester|Lingfield|Ludlow|Musselburgh|Newcastle|Newmarket|Nottingham|Perth|Plumpton|Pontefract|Redcar|Ripon|Salisbury|Sandown|Southwell|Stratford|Taunton|Thirsk|Uttoxeter|Warwick|Windsor|Wolverhampton|York)\b",
            ]

            for pattern in track_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    track_code = match.group(1).upper()[
                        :3
                    ]  # Standardize to 3-letter code
                    break

            # Extract horse names (capitalized words that might be horse names)
            horse_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b"
            horse_matches = re.findall(horse_pattern, text_content)
            if horse_matches:
                # Simple heuristic: longest match is likely a horse name
                horse_name = max(horse_matches, key=len)

        return race_date, track_code, horse_name

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RSS format
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue

        return None

    def _calculate_confidence_score(
        self, content: Dict[str, Any], data_type: str
    ) -> float:
        """Calculate confidence score for the data"""
        score = 0.5  # Base score

        # Content completeness
        if len(content) >= 3:
            score += 0.2

        # Data type specific scoring
        if data_type == "weather":
            if "temperature" in content and "condition" in content:
                score += 0.3
        elif data_type in ["rss", "news"]:
            if "headline" in content and len(content.get("headline", "")) > 20:
                score += 0.2
            if "summary" in content and len(content.get("summary", "")) > 50:
                score += 0.1

        # Race-specific content bonus
        text_content = " ".join(str(v) for v in content.values() if v)
        racing_keywords = [
            "race",
            "horse",
            "jockey",
            "trainer",
            "odds",
            "winner",
            "placed",
        ]
        keyword_count = sum(
            1 for keyword in racing_keywords if keyword in text_content.lower()
        )
        score += min(keyword_count * 0.05, 0.2)

        return min(score, 1.0)

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    async def _get_track_locations(self) -> Dict[str, Dict[str, str]]:
        """Get track locations for weather data"""
        # This would typically come from a database or configuration
        return {
            "ASC": {"city": "Ascot", "country": "GB"},
            "AIN": {"city": "Liverpool", "country": "GB"},
            "CHE": {"city": "Cheltenham", "country": "GB"},
            "DON": {"city": "Doncaster", "country": "GB"},
            "EPS": {"city": "Epsom", "country": "GB"},
            "GOO": {"city": "Goodwood", "country": "GB"},
            "NEW": {"city": "Newmarket", "country": "GB"},
            "YOR": {"city": "York", "country": "GB"},
        }

    async def save_records(self, records: List[IntegratedDataRecord]) -> int:
        """Save integrated data records to database"""
        if not records:
            return 0

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            saved_count = 0
            for record in records:
                # Check for duplicates
                cursor.execute(
                    "SELECT COUNT(*) FROM external_data_records WHERE record_id = ?",
                    (record.record_id,),
                )

                if cursor.fetchone()[0] == 0:
                    # Insert new record
                    cursor.execute(
                        """
                        INSERT INTO external_data_records 
                        (record_id, source_id, data_type, timestamp, race_date, track_code, 
                         horse_name, content_json, confidence_score, processed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            record.record_id,
                            record.source_id,
                            record.data_type,
                            record.timestamp,
                            record.race_date,
                            record.track_code,
                            record.horse_name,
                            json.dumps(record.content),
                            record.confidence_score,
                            record.processed,
                        ),
                    )
                    saved_count += 1

            conn.commit()
            conn.close()

            logger.info(f"Saved {saved_count} new external data records")
            self.stats["records_processed"] += saved_count

            return saved_count

        except Exception as e:
            logger.error(f"Error saving external data records: {e}")
            return 0

    async def update_source_status(
        self, source: ExternalDataSource, record_count: int, error_count: int = 0
    ):
        """Update source status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO external_data_sources 
                (source_id, name, source_type, url, update_frequency, enabled, 
                 last_updated, records_count, error_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    source.source_id,
                    source.name,
                    source.source_type,
                    source.url,
                    source.update_frequency,
                    source.enabled,
                    datetime.now(),
                    record_count,
                    error_count,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating source status: {e}")

    async def update_all_sources(self) -> Dict[str, Any]:
        """Update data from all configured sources"""
        results = {
            "sources_processed": 0,
            "total_records": 0,
            "errors": 0,
            "source_results": {},
        }

        try:
            await self.start_session()

            for source in self.data_sources:
                try:
                    logger.info(f"Updating data from source: {source.name}")

                    # Fetch data from source
                    records = await self.fetch_api_data(source)

                    # Filter by confidence score
                    min_confidence = self.config.get("data_quality", {}).get(
                        "min_confidence_score", 0.7
                    )
                    high_quality_records = [
                        r for r in records if r.confidence_score >= min_confidence
                    ]

                    # Save records
                    saved_count = await self.save_records(high_quality_records)

                    # Update source status
                    await self.update_source_status(source, saved_count)

                    # Track results
                    results["source_results"][source.source_id] = {
                        "fetched": len(records),
                        "high_quality": len(high_quality_records),
                        "saved": saved_count,
                    }

                    results["sources_processed"] += 1
                    results["total_records"] += saved_count
                    self.stats["sources_updated"] += 1

                    logger.info(f"Source {source.name}: {saved_count} records saved")

                except Exception as e:
                    logger.error(f"Error updating source {source.name}: {e}")
                    results["errors"] += 1
                    self.stats["errors_encountered"] += 1

            self.stats["last_update_cycle"] = datetime.now()

        finally:
            await self.close_session()

        return results

    async def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Source statistics
            cursor.execute(
                """
                SELECT source_id, name, records_count, error_count, last_updated
                FROM external_data_sources
                ORDER BY last_updated DESC
            """
            )
            sources_stats = [
                {
                    "source_id": row[0],
                    "name": row[1],
                    "records_count": row[2],
                    "error_count": row[3],
                    "last_updated": row[4],
                }
                for row in cursor.fetchall()
            ]

            # Record statistics
            cursor.execute(
                """
                SELECT data_type, COUNT(*) as count, AVG(confidence_score) as avg_confidence
                FROM external_data_records
                GROUP BY data_type
            """
            )
            data_type_stats = [
                {
                    "data_type": row[0],
                    "count": row[1],
                    "avg_confidence": round(row[2], 3),
                }
                for row in cursor.fetchall()
            ]

            # Recent records
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM external_data_records 
                WHERE timestamp >= datetime('now', '-24 hours')
            """
            )
            recent_records = cursor.fetchone()[0]

            conn.close()

            return {
                "system_stats": self.stats.copy(),
                "sources": sources_stats,
                "data_types": data_type_stats,
                "recent_records_24h": recent_records,
                "configured_sources": len(self.data_sources),
                "enabled_sources": len([s for s in self.data_sources if s.enabled]),
            }

        except Exception as e:
            logger.error(f"Error getting integration statistics: {e}")
            return {"error": str(e)}

    async def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """Clean up old external data records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            cursor.execute(
                """
                DELETE FROM external_data_records 
                WHERE timestamp < ? AND processed = TRUE
            """,
                (cutoff_date,),
            )

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted_count} old external data records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
            return 0


async def main():
    """Main function for testing the External Data Integrator"""

    print("🔗 External Data Integration System V2.03")
    print("=" * 50)

    try:
        # Initialize integrator
        integrator = ExternalDataIntegrator()

        # Initialize database
        print("📊 Initializing database...")
        await integrator.initialize_database()

        # Update from all sources
        print("🔄 Updating from external sources...")
        results = await integrator.update_all_sources()

        print(f"✅ Update completed:")
        print(f"   - Sources processed: {results['sources_processed']}")
        print(f"   - Total records: {results['total_records']}")
        print(f"   - Errors: {results['errors']}")

        # Show source-specific results
        for source_id, stats in results["source_results"].items():
            print(
                f"   - {source_id}: {stats['saved']} records saved ({stats['high_quality']} high-quality)"
            )

        # Get statistics
        print("\n📈 Integration Statistics:")
        stats = await integrator.get_integration_statistics()

        print(f"   - Configured sources: {stats['configured_sources']}")
        print(f"   - Enabled sources: {stats['enabled_sources']}")
        print(f"   - Recent records (24h): {stats['recent_records_24h']}")

        if stats["data_types"]:
            print("   - Data types:")
            for dt in stats["data_types"]:
                print(
                    f"     • {dt['data_type']}: {dt['count']} records (avg confidence: {dt['avg_confidence']})"
                )

        # Cleanup test
        print("\n🧹 Testing cleanup...")
        cleaned = await integrator.cleanup_old_records(days_to_keep=90)
        print(f"   - Cleaned up {cleaned} old records")

        print("\n✅ External Data Integration testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
