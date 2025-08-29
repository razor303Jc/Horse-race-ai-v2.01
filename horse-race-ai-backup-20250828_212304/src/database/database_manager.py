#!/usr/bin/env python3
"""
Comprehensive Database Manager for Horse Racing AI v2.0

This module provides a complete database interface for all racing data including:
- Races, horses, jockeys, trainers
- Statistics and performance metrics
- Data filtering, searching, and analysis
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Setup logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Comprehensive database manager for horse racing data"""

    def __init__(self, database_url: str = None):
        """Initialize database manager with connection pooling"""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")

        # Parse database URL
        self._parse_database_url()

        # Initialize connection pool
        self.pool = None
        self._init_connection_pool()

    def _parse_database_url(self):
        """Parse DATABASE_URL into connection parameters"""
        import urllib.parse as urlparse

        url = urlparse.urlparse(self.database_url)
        self.db_config = {
            "host": url.hostname,
            "port": url.port,
            "database": url.path[1:],  # Remove leading slash
            "user": url.username,
            "password": url.password,
        }

    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pool = SimpleConnectionPool(minconn=1, maxconn=10, **self.db_config)
            logger.info("✅ Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                self.pool.putconn(connection)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]

    def execute_single(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute a query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None

    def execute_count(self, query: str, params: tuple = None) -> int:
        """Execute a COUNT query and return the count"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0

    # =================== SUMMARY STATISTICS ===================

    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        summary = {"tables": {}, "latest_data": {}, "statistics": {}}

        # Table counts
        tables = [
            "races_cards",
            "races_results",
            "horses_cards",
            "horses_results",
            "jockeys_stats",
            "trainers_stats",
            "racecard_details",
            "records",
        ]
        for table in tables:
            try:
                count = self.execute_count(f"SELECT COUNT(*) FROM {table}")
                summary["tables"][table] = count
            except Exception as e:
                logger.warning(f"Failed to count {table}: {e}")
                summary["tables"][table] = 0

        # Latest race date
        try:
            latest_race = self.execute_single(
                "SELECT MAX(date) as latest_date FROM races_cards"
            )
            summary["latest_data"]["latest_race_date"] = (
                latest_race["latest_date"] if latest_race else None
            )
        except Exception:
            summary["latest_data"]["latest_race_date"] = None

        # Course statistics
        try:
            courses = self.execute_count(
                "SELECT COUNT(DISTINCT course) FROM races_cards"
            )
            summary["statistics"]["total_courses"] = courses
        except Exception:
            summary["statistics"]["total_courses"] = 0

        return summary

    # =================== RACE QUERIES ===================

    def get_races(
        self,
        limit: int = 100,
        offset: int = 0,
        date_from: date = None,
        date_to: date = None,
        course: str = None,
    ) -> List[Dict[str, Any]]:
        """Get races with optional filtering"""
        conditions = []
        params = []

        if date_from:
            conditions.append("date >= %s")
            params.append(date_from)

        if date_to:
            conditions.append("date <= %s")
            params.append(date_to)

        if course:
            conditions.append("course ILIKE %s")
            params.append(f"%{course}%")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.extend([limit, offset])

        query = f"""
            SELECT race_id, race_number, race_time, course, race_type, date,
                   race_name, class, years, distance, surface, prize,
                   runners_racecard, runners, draw
            FROM races_cards
            {where_clause}
            ORDER BY date DESC, race_time ASC
            LIMIT %s OFFSET %s
        """

        return self.execute_query(query, tuple(params))

    def get_race_details(self, race_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific race"""
        race_query = """
            SELECT * FROM races_cards WHERE race_id = %s
        """

        race = self.execute_single(race_query, (race_id,))
        if not race:
            return None

        # Get race participants
        participants_query = """
            SELECT * FROM racecard_details
            WHERE race_id = %s
            ORDER BY draw ASC
        """
        participants = self.execute_query(participants_query, (race_id,))

        # Get race results if available
        results_query = """
            SELECT * FROM records
            WHERE race_id = %s
            ORDER BY place ASC
        """
        results = self.execute_query(results_query, (race_id,))

        race["participants"] = participants
        race["results"] = results

        return race

    def get_races_by_course(self, course: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent races for a specific course"""
        query = """
            SELECT * FROM races_cards
            WHERE course ILIKE %s
            ORDER BY date DESC, race_time ASC
            LIMIT %s
        """
        return self.execute_query(query, (f"%{course}%", limit))

    def get_todays_races(self) -> List[Dict[str, Any]]:
        """Get today's scheduled races"""
        today = date.today()
        return self.get_races(date_from=today, date_to=today, limit=50)

    # =================== HORSE QUERIES ===================

    def get_horses(
        self, limit: int = 100, offset: int = 0, search: str = None
    ) -> List[Dict[str, Any]]:
        """Get horses with optional search"""
        conditions = []
        params = []

        if search:
            conditions.append("name ILIKE %s")
            params.append(f"%{search}%")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.extend([limit, offset])

        query = f"""
            SELECT DISTINCT name, country, age, color, owner, sire, dam, sex,
                   total_races, wins, percentage_wins, placed, percentage_placed,
                   flat_turf_races, flat_turf_wins, flat_turf_rate
            FROM (
                SELECT name, country, age, color, owner, sire, dam, sex,
                       total_races, wins, percentage_wins, placed, percentage_placed,
                       flat_turf_races, flat_turf_wins, flat_turf_rate
                FROM horses_cards
                UNION ALL
                SELECT name, country, age, color, owner, sire, dam, sex,
                       total_races, wins, percentage_wins, placed, percentage_placed,
                       flat_turf_races, flat_turf_wins, flat_turf_rate
                FROM horses_results
            ) as combined_horses
            {where_clause}
            ORDER BY name ASC
            LIMIT %s OFFSET %s
        """

        return self.execute_query(query, tuple(params))

    def get_horse_details(self, horse_name: str) -> Dict[str, Any]:
        """Get detailed information for a specific horse by name"""
        horse_query = """
            SELECT * FROM horses_cards WHERE name ILIKE %s
            UNION ALL
            SELECT * FROM horses_results WHERE name ILIKE %s
            LIMIT 1
        """

        horse = self.execute_single(horse_query, (horse_name, horse_name))
        if not horse:
            return None

        # Get horse's recent race entries
        recent_races_query = """
            SELECT rc.*, rd.jockey, rd.trainer, rd.weight, rd.odds
            FROM races_cards rc
            JOIN racecard_details rd ON rc.race_id = rd.race_id
            WHERE rd.name ILIKE %s
            ORDER BY rc.date DESC
            LIMIT 10
        """
        recent_races = self.execute_query(recent_races_query, (horse_name,))

        # Get horse's results
        results_query = """
            SELECT rec.*, rr.course, rr.date, rr.race_name
            FROM records rec
            JOIN races_results rr ON rec.race_id = rr.race_id
            WHERE rec.name ILIKE %s
            ORDER BY rr.date DESC
            LIMIT 10
        """
        results = self.execute_query(results_query, (horse_name,))

        horse["recent_races"] = recent_races
        horse["results"] = results

        return horse

    def search_horses(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search horses by name"""
        query = """
            SELECT DISTINCT name, country, age, owner, total_races, wins, percentage_wins
            FROM (
                SELECT name, country, age, owner, total_races, wins, percentage_wins
                FROM horses_cards
                UNION ALL
                SELECT name, country, age, owner, total_races, wins, percentage_wins
                FROM horses_results
            ) as combined_horses
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        return self.execute_query(query, (f"%{search_term}%", limit))

    # =================== JOCKEY QUERIES ===================

    def get_jockeys(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get jockeys with statistics"""
        query = """
            SELECT * FROM jockeys_stats
            ORDER BY percentage_wins DESC, total_races DESC
            LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset))

    def get_jockey_details(self, jockey_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific jockey"""
        jockey_query = """
            SELECT * FROM jockeys_stats WHERE jockey_id = %s
        """

        jockey = self.execute_single(jockey_query, (jockey_id,))
        if not jockey:
            return None

        # Get recent rides
        recent_rides_query = """
            SELECT rd.*, rc.date, rc.course, rc.race_name
            FROM racecard_details rd
            JOIN races_cards rc ON rd.race_id = rc.race_id
            WHERE rd.jockey_id = %s
            ORDER BY rc.date DESC
            LIMIT 20
        """
        recent_rides = self.execute_query(recent_rides_query, (jockey_id,))

        jockey["recent_rides"] = recent_rides
        return jockey

    def search_jockeys(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search jockeys by name"""
        query = """
            SELECT * FROM jockeys_stats
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        return self.execute_query(query, (f"%{search_term}%", limit))

    # =================== TRAINER QUERIES ===================

    def get_trainers(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get trainers with statistics"""
        query = """
            SELECT * FROM trainers_stats
            ORDER BY percentage_wins DESC, total_races DESC
            LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limit, offset))

    def get_trainer_details(self, trainer_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific trainer"""
        trainer_query = """
            SELECT * FROM trainers_stats WHERE trainer_id = %s
        """

        trainer = self.execute_single(trainer_query, (trainer_id,))
        if not trainer:
            return None

        # Get recent horses
        recent_horses_query = """
            SELECT rd.*, rc.date, rc.course, rc.race_name
            FROM racecard_details rd
            JOIN races_cards rc ON rd.race_id = rc.race_id
            WHERE rd.trainer_id = %s
            ORDER BY rc.date DESC
            LIMIT 20
        """
        recent_horses = self.execute_query(recent_horses_query, (trainer_id,))

        trainer["recent_horses"] = recent_horses
        return trainer

    def search_trainers(
        self, search_term: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search trainers by name"""
        query = """
            SELECT * FROM trainers_stats
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        return self.execute_query(query, (f"%{search_term}%", limit))

    # =================== ANALYTICS QUERIES ===================

    def get_course_statistics(self, course: str = None) -> List[Dict[str, Any]]:
        """Get statistics for courses"""
        if course:
            query = """
                SELECT course, COUNT(*) as total_races,
                       COUNT(DISTINCT date) as race_days,
                       AVG(runners) as avg_runners,
                       SUM(CAST(REPLACE(prize, '£', '') AS NUMERIC)) as total_prize_money
                FROM races_cards
                WHERE course ILIKE %s
                GROUP BY course
            """
            return self.execute_query(query, (f"%{course}%",))
        else:
            query = """
                SELECT course, COUNT(*) as total_races,
                       COUNT(DISTINCT date) as race_days,
                       AVG(runners) as avg_runners
                FROM races_cards
                GROUP BY course
                ORDER BY total_races DESC
                LIMIT 20
            """
            return self.execute_query(query)

    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over specified days"""
        query = """
            SELECT date, COUNT(*) as races_count,
                   AVG(runners) as avg_runners
            FROM races_cards
            WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY date
            ORDER BY date DESC
        """

        daily_stats = self.execute_query(query, (days,))

        # Top performing jockeys in period
        jockey_query = """
            SELECT j.name, j.wins, j.percentage_wins
            FROM jockeys_stats j
            ORDER BY j.wins DESC, j.percentage_wins DESC
            LIMIT 10
        """
        top_jockeys = self.execute_query(jockey_query)

        # Top performing trainers in period
        trainer_query = """
            SELECT t.name, t.wins, t.percentage_wins
            FROM trainers_stats t
            ORDER BY t.wins DESC, t.percentage_wins DESC
            LIMIT 10
        """
        top_trainers = self.execute_query(trainer_query)

        return {
            "daily_stats": daily_stats,
            "top_jockeys": top_jockeys,
            "top_trainers": top_trainers,
        }

    def get_search_suggestions(
        self, search_term: str, limit: int = 5
    ) -> Dict[str, List[str]]:
        """Get search suggestions for horses, jockeys, trainers, and courses"""
        suggestions = {"horses": [], "jockeys": [], "trainers": [], "courses": []}

        # Horse suggestions
        horse_query = """
            SELECT DISTINCT name FROM (
                SELECT name FROM horses_cards
                UNION ALL
                SELECT name FROM horses_results
            ) as combined_horses
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        horses = self.execute_query(horse_query, (f"%{search_term}%", limit))
        suggestions["horses"] = [h["name"] for h in horses]

        # Jockey suggestions
        jockey_query = """
            SELECT name FROM jockeys_stats
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        jockeys = self.execute_query(jockey_query, (f"%{search_term}%", limit))
        suggestions["jockeys"] = [j["name"] for j in jockeys]

        # Trainer suggestions
        trainer_query = """
            SELECT name FROM trainers_stats
            WHERE name ILIKE %s
            ORDER BY name ASC
            LIMIT %s
        """
        trainers = self.execute_query(trainer_query, (f"%{search_term}%", limit))
        suggestions["trainers"] = [t["name"] for t in trainers]

        # Course suggestions
        course_query = """
            SELECT DISTINCT course FROM races_cards
            WHERE course ILIKE %s
            ORDER BY course ASC
            LIMIT %s
        """
        courses = self.execute_query(course_query, (f"%{search_term}%", limit))
        suggestions["courses"] = [c["course"] for c in courses]

        return suggestions

    def close(self):
        """Close all database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")


# Singleton instance
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # Test the database manager
    import asyncio

    async def test_db():
        db = DatabaseManager()

        print("=== Testing Database Manager ===")

        # Test summary
        summary = db.get_database_summary()
        print(f"Database Summary: {summary}")

        # Test races
        races = db.get_races(limit=5)
        print(f"Recent races: {len(races)}")

        # Test horses
        horses = db.get_horses(limit=5)
        print(f"Horses: {len(horses)}")

        # Test jockeys
        jockeys = db.get_jockeys(limit=5)
        print(f"Jockeys: {len(jockeys)}")

        # Test trainers
        trainers = db.get_trainers(limit=5)
        print(f"Trainers: {len(trainers)}")

        db.close()

    asyncio.run(test_db())
