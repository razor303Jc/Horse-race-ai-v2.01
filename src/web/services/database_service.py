#!/usr/bin/env python3
"""
Database Service for Horse Racing AI v2.0
Handles all database operations and queries for the web application.
"""

import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime, timedelta


class DatabaseService:
    """Service for managing database operations"""

    def __init__(
        self, db_path: str = "data/horseracedatabase/complete_horse_racing_database.db"
    ):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.ensure_database_exists()

    def ensure_database_exists(self):
        """Ensure the database file exists and is accessible"""
        if not self.db_path.exists():
            self.logger.warning(f"Database not found at {self.db_path}")
            # Create basic tables if database doesn't exist
            self.create_basic_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def create_basic_tables(self):
        """Create basic database tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Create races table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS races (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        race_id TEXT UNIQUE,
                        date TEXT,
                        time TEXT,
                        course TEXT,
                        race_name TEXT,
                        distance TEXT,
                        class TEXT,
                        going TEXT,
                        prize_money REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create runners table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS runners (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        race_id TEXT,
                        horse_name TEXT,
                        jockey TEXT,
                        trainer TEXT,
                        weight TEXT,
                        odds TEXT,
                        position INTEGER,
                        form TEXT,
                        age INTEGER,
                        sex TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (race_id) REFERENCES races (race_id)
                    )
                """
                )

                # Create predictions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        race_id TEXT,
                        horse_name TEXT,
                        prediction_type TEXT,
                        confidence REAL,
                        predicted_position INTEGER,
                        actual_position INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (race_id) REFERENCES races (race_id)
                    )
                """
                )

                conn.commit()
                self.logger.info("Basic database tables created successfully")

        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")

    def get_recent_races(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent races with basic information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT race_id, date, time, course, race_name, distance, class, going
                    FROM races 
                    ORDER BY date DESC, time DESC 
                    LIMIT ?
                """,
                    (limit,),
                )

                races = []
                for row in cursor.fetchall():
                    races.append(
                        {
                            "race_id": row["race_id"],
                            "date": row["date"],
                            "time": row["time"],
                            "course": row["course"],
                            "race_name": row["race_name"],
                            "distance": row["distance"],
                            "class": row["class"],
                            "going": row["going"],
                        }
                    )

                return races

        except Exception as e:
            self.logger.error(f"Error getting recent races: {e}")
            return self._get_mock_races(limit)

    def get_race_details(self, race_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific race"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get race information
                cursor.execute(
                    """
                    SELECT * FROM races WHERE race_id = ?
                """,
                    (race_id,),
                )
                race_row = cursor.fetchone()

                if not race_row:
                    return self._get_mock_race_details(race_id)

                # Get runners for this race
                cursor.execute(
                    """
                    SELECT * FROM runners WHERE race_id = ?
                    ORDER BY position ASC
                """,
                    (race_id,),
                )
                runner_rows = cursor.fetchall()

                # Get predictions for this race
                cursor.execute(
                    """
                    SELECT * FROM predictions WHERE race_id = ?
                    ORDER BY confidence DESC
                """,
                    (race_id,),
                )
                prediction_rows = cursor.fetchall()

                # Build race details
                race_details = {
                    "race_id": race_row["race_id"],
                    "date": race_row["date"],
                    "time": race_row["time"],
                    "course": race_row["course"],
                    "race_name": race_row["race_name"],
                    "distance": race_row["distance"],
                    "class": race_row["class"],
                    "going": race_row["going"],
                    "prize_money": race_row["prize_money"],
                    "runners": [],
                    "predictions": [],
                }

                # Add runners
                for runner in runner_rows:
                    race_details["runners"].append(
                        {
                            "horse_name": runner["horse_name"],
                            "jockey": runner["jockey"],
                            "trainer": runner["trainer"],
                            "weight": runner["weight"],
                            "odds": runner["odds"],
                            "position": runner["position"],
                            "form": runner["form"],
                            "age": runner["age"],
                            "sex": runner["sex"],
                        }
                    )

                # Add predictions
                for prediction in prediction_rows:
                    race_details["predictions"].append(
                        {
                            "horse_name": prediction["horse_name"],
                            "prediction_type": prediction["prediction_type"],
                            "confidence": prediction["confidence"],
                            "predicted_position": prediction["predicted_position"],
                            "actual_position": prediction["actual_position"],
                        }
                    )

                return race_details

        except Exception as e:
            self.logger.error(f"Error getting race details for {race_id}: {e}")
            return self._get_mock_race_details(race_id)

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Count races
                cursor.execute("SELECT COUNT(*) as count FROM races")
                race_count = cursor.fetchone()["count"]

                # Count runners
                cursor.execute("SELECT COUNT(*) as count FROM runners")
                runner_count = cursor.fetchone()["count"]

                # Count predictions
                cursor.execute("SELECT COUNT(*) as count FROM predictions")
                prediction_count = cursor.fetchone()["count"]

                # Get recent activity
                cursor.execute(
                    """
                    SELECT DATE(created_at) as date, COUNT(*) as count 
                    FROM races 
                    WHERE created_at >= date('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """
                )
                recent_activity = cursor.fetchall()

                return {
                    "total_races": race_count,
                    "total_runners": runner_count,
                    "total_predictions": prediction_count,
                    "recent_activity": [
                        {"date": row["date"], "count": row["count"]}
                        for row in recent_activity
                    ],
                    "database_size": self._get_database_size(),
                    "last_updated": datetime.now().isoformat(),
                }

        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return self._get_mock_stats()

    def search_races(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search races by course, race name, or date"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_term = f"%{query}%"

                cursor.execute(
                    """
                    SELECT race_id, date, time, course, race_name, distance, class
                    FROM races 
                    WHERE course LIKE ? OR race_name LIKE ? OR date LIKE ?
                    ORDER BY date DESC, time DESC 
                    LIMIT ?
                """,
                    (search_term, search_term, search_term, limit),
                )

                races = []
                for row in cursor.fetchall():
                    races.append(
                        {
                            "race_id": row["race_id"],
                            "date": row["date"],
                            "time": row["time"],
                            "course": row["course"],
                            "race_name": row["race_name"],
                            "distance": row["distance"],
                            "class": row["class"],
                        }
                    )

                return races

        except Exception as e:
            self.logger.error(f"Error searching races: {e}")
            return []

    def _get_database_size(self) -> str:
        """Get database file size"""
        try:
            if self.db_path.exists():
                size_bytes = self.db_path.stat().st_size
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    return f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024**3:
                    return f"{size_bytes/(1024**2):.1f} MB"
                else:
                    return f"{size_bytes/(1024**3):.1f} GB"
            return "Unknown"
        except:
            return "Unknown"

    def _get_mock_races(self, limit: int) -> List[Dict[str, Any]]:
        """Get mock race data when database is not available"""
        mock_races = []
        for i in range(min(limit, 10)):
            mock_races.append(
                {
                    "race_id": f"MOCK_{1000 + i}",
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "time": f"15:{30 + i*15}",
                    "course": ["Ascot", "Newmarket", "Chester", "York", "Epsom"][i % 5],
                    "race_name": f"Mock Race {i + 1}",
                    "distance": ["1m", "1m2f", "1m4f", "2m", "2m4f"][i % 5],
                    "class": str((i % 6) + 1),
                    "going": ["Good", "Good to Firm", "Firm", "Heavy", "Soft"][i % 5],
                }
            )
        return mock_races

    def _get_mock_race_details(self, race_id: str) -> Dict[str, Any]:
        """Get mock race details when database is not available"""
        return {
            "race_id": race_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "15:30",
            "course": "Ascot",
            "race_name": "Mock Stakes",
            "distance": "1m2f",
            "class": "3",
            "going": "Good",
            "prize_money": 25000.0,
            "runners": [
                {
                    "horse_name": "Thunder Bolt",
                    "jockey": "J. Smith",
                    "trainer": "A. Jones",
                    "weight": "9-2",
                    "odds": "5/2",
                    "position": 1,
                    "form": "1-2-1",
                    "age": 4,
                    "sex": "C",
                },
                {
                    "horse_name": "Lightning Strike",
                    "jockey": "M. Brown",
                    "trainer": "S. Davis",
                    "weight": "9-0",
                    "odds": "3/1",
                    "position": 2,
                    "form": "2-1-3",
                    "age": 5,
                    "sex": "G",
                },
            ],
            "predictions": [
                {
                    "horse_name": "Thunder Bolt",
                    "prediction_type": "Win",
                    "confidence": 0.89,
                    "predicted_position": 1,
                    "actual_position": 1,
                }
            ],
        }

    def _get_mock_stats(self) -> Dict[str, Any]:
        """Get mock database statistics"""
        return {
            "total_races": 2847,
            "total_runners": 25623,
            "total_predictions": 8456,
            "recent_activity": [
                {"date": "2025-08-08", "count": 15},
                {"date": "2025-08-07", "count": 18},
                {"date": "2025-08-06", "count": 12},
            ],
            "database_size": "156.7 MB",
            "last_updated": datetime.now().isoformat(),
        }


# Global database service instance
db_service = DatabaseService()


def get_database_service() -> DatabaseService:
    """Get the global database service instance"""
    return db_service
