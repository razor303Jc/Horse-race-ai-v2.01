#!/usr/bin/env python3
"""
API PostgreSQL Integration - V2.05
==================================

Connect existing REST API endpoints to PostgreSQL backend with:
- Connection pooling for optimal performance
- Realistic dataset validation using production-ready testing environment
- API response improvements with PostgreSQL performance
- Comprehensive endpoint testing and validation

This integrates the testing & simulation strategy PostgreSQL environment
with the existing API infrastructure for production-ready performance.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# PostgreSQL Configuration (Testing & Simulation Strategy Environment)
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "results",
    "user": "horse_racing",
    "password": "secure_password_123",
}


class APIPostgreSQLIntegration:
    """
    API PostgreSQL Integration Manager

    Connects existing API endpoints to the production-ready PostgreSQL
    testing environment with 11,328 complete records for realistic validation.
    """

    def __init__(self):
        """Initialize API PostgreSQL integration"""
        self.pool = None
        self.app = FastAPI(
            title="Horse Racing AI API - PostgreSQL Integrated",
            version="2.05",
            description="Production-ready API with PostgreSQL backend",
        )

        # Enable CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Performance metrics tracking
        self.performance_metrics = {
            "total_requests": 0,
            "avg_response_time": 0,
            "endpoint_stats": {},
            "database_stats": {
                "total_queries": 0,
                "avg_query_time": 0,
                "connection_pool_hits": 0,
            },
        }

        # Setup routes
        self._setup_routes()

        logger.info("🏇 API PostgreSQL Integration Manager initialized")

    async def initialize_connection_pool(self):
        """Initialize PostgreSQL connection pool for optimal performance"""
        try:
            # Test connection first
            test_conn = psycopg2.connect(**POSTGRES_CONFIG)
            test_conn.close()
            logger.info("✅ PostgreSQL connection test successful")

            # Initialize connection pool
            self.pool = SimpleConnectionPool(minconn=2, maxconn=20, **POSTGRES_CONFIG)

            logger.info("✅ PostgreSQL connection pool initialized (2-20 connections)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL connection pool: {e}")
            raise

    def get_connection(self):
        """Get connection from pool with performance tracking"""
        if not self.pool:
            raise HTTPException(status_code=500, detail="Database pool not initialized")

        try:
            conn = self.pool.getconn()
            self.performance_metrics["database_stats"]["connection_pool_hits"] += 1
            return conn
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise HTTPException(status_code=500, detail="Database connection failed")

    def return_connection(self, conn):
        """Return connection to pool"""
        if self.pool and conn:
            self.pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query with performance monitoring"""
        start_time = time.time()
        conn = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Convert to list of dicts
            results = [dict(row) for row in results]

            cursor.close()

            # Track performance
            query_time = (time.time() - start_time) * 1000  # Convert to ms
            self.performance_metrics["database_stats"]["total_queries"] += 1

            # Update average query time
            total_queries = self.performance_metrics["database_stats"]["total_queries"]
            current_avg = self.performance_metrics["database_stats"]["avg_query_time"]
            new_avg = ((current_avg * (total_queries - 1)) + query_time) / total_queries
            self.performance_metrics["database_stats"]["avg_query_time"] = new_avg

            logger.debug(f"Query executed in {query_time:.2f}ms")
            return results

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise HTTPException(
                status_code=500, detail=f"Database query failed: {str(e)}"
            )

        finally:
            if conn:
                self.return_connection(conn)

    def _setup_routes(self):
        """Setup all API routes with PostgreSQL integration"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint with database validation"""
            start_time = time.time()

            try:
                # Test database connection
                results = self.execute_query("SELECT 1 as test")

                response_time = (time.time() - start_time) * 1000

                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": "connected",
                    "response_time_ms": round(response_time, 2),
                    "environment": "PostgreSQL Testing & Simulation",
                    "version": "v2.05",
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.app.get("/api/database/status")
        async def database_status():
            """Get comprehensive database status and metrics"""
            try:
                # Get entity counts
                entity_counts = {}

                tables = [
                    "horses_entity",
                    "jockeys_entity",
                    "trainers_entity",
                    "races_entity",
                ]
                for table in tables:
                    count_result = self.execute_query(
                        f"SELECT COUNT(*) as count FROM {table}"
                    )
                    entity_counts[table] = count_result[0]["count"]

                # Calculate total records
                total_records = sum(entity_counts.values())

                # Get database size
                size_result = self.execute_query(
                    """
                    SELECT pg_size_pretty(pg_database_size('results')) as db_size
                """
                )

                return {
                    "database_name": "results",
                    "status": "operational",
                    "entity_counts": entity_counts,
                    "total_records": total_records,
                    "database_size": size_result[0]["db_size"],
                    "performance_metrics": self.performance_metrics["database_stats"],
                    "connection_pool": {
                        "min_connections": 2,
                        "max_connections": 20,
                        "active": "monitoring",
                    },
                    "last_updated": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Database status check failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/horses")
        async def get_horses(
            limit: int = Query(50, le=500),
            offset: int = Query(0, ge=0),
            min_age: Optional[int] = Query(None, ge=1, le=15),
            max_age: Optional[int] = Query(None, ge=1, le=15),
            sex: Optional[str] = Query(None),
            country: Optional[str] = Query(None),
        ):
            """Get horses with filtering - PostgreSQL optimized"""
            start_time = time.time()

            try:
                # Build dynamic query with filters
                where_conditions = []
                params = []
                param_count = 1

                if min_age:
                    where_conditions.append(f"age >= ${param_count}")
                    params.append(min_age)
                    param_count += 1

                if max_age:
                    where_conditions.append(f"age <= ${param_count}")
                    params.append(max_age)
                    param_count += 1

                if sex:
                    where_conditions.append(f"sex = ${param_count}")
                    params.append(sex)
                    param_count += 1

                if country:
                    where_conditions.append(f"country ILIKE ${param_count}")
                    params.append(f"%{country}%")
                    param_count += 1

                where_clause = (
                    " WHERE " + " AND ".join(where_conditions)
                    if where_conditions
                    else ""
                )

                # Get total count for pagination
                count_query = f"""
                    SELECT COUNT(*) as total FROM horses_entity
                    {where_clause}
                """
                count_params = tuple(params) if params else None
                total_result = self.execute_query(count_query, count_params)
                total_count = total_result[0]["total"]

                # Get horses data
                horses_query = f"""
                    SELECT 
                        horse_id,
                        horse_name,
                        age,
                        sex,
                        country,
                        sire,
                        dam,
                        created_at,
                        updated_at
                    FROM horses_entity
                    {where_clause}
                    ORDER BY horse_name
                    LIMIT ${param_count} OFFSET ${param_count + 1}
                """

                horses_params = (
                    tuple(params + [limit, offset]) if params else (limit, offset)
                )
                horses = self.execute_query(horses_query, horses_params)

                response_time = (time.time() - start_time) * 1000

                # Track endpoint performance
                endpoint = "get_horses"
                self._track_endpoint_performance(endpoint, response_time)

                return {
                    "horses": horses,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "pages": (total_count + limit - 1) // limit,
                    },
                    "filters_applied": {
                        "min_age": min_age,
                        "max_age": max_age,
                        "sex": sex,
                        "country": country,
                    },
                    "performance": {
                        "response_time_ms": round(response_time, 2),
                        "total_records": len(horses),
                    },
                }

            except Exception as e:
                logger.error(f"Get horses failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/jockeys")
        async def get_jockeys(
            limit: int = Query(50, le=500),
            offset: int = Query(0, ge=0),
            min_win_rate: Optional[float] = Query(None, ge=0, le=100),
            min_runs: Optional[int] = Query(None, ge=1),
        ):
            """Get jockeys with performance filtering"""
            start_time = time.time()

            try:
                where_conditions = []
                params = []
                param_count = 1

                if min_runs:
                    where_conditions.append(f"runs >= ${param_count}")
                    params.append(min_runs)
                    param_count += 1

                if min_win_rate:
                    where_conditions.append(
                        f"(wins::float / NULLIF(runs, 0) * 100) >= ${param_count}"
                    )
                    params.append(min_win_rate)
                    param_count += 1

                where_clause = (
                    " WHERE " + " AND ".join(where_conditions)
                    if where_conditions
                    else ""
                )

                # Get jockeys with calculated win rate
                jockeys_query = f"""
                    SELECT 
                        jockey_id,
                        jockey_name,
                        runs,
                        wins,
                        win_rate,
                        (wins::float / NULLIF(runs, 0) * 100) as calculated_win_rate,
                        placed,
                        place_rate,
                        created_at,
                        updated_at
                    FROM jockeys_entity
                    {where_clause}
                    ORDER BY calculated_win_rate DESC NULLS LAST, runs DESC
                    LIMIT ${param_count} OFFSET ${param_count + 1}
                """

                jockeys_params = (
                    tuple(params + [limit, offset]) if params else (limit, offset)
                )
                jockeys = self.execute_query(jockeys_query, jockeys_params)

                # Get total count
                count_query = f"""
                    SELECT COUNT(*) as total FROM jockeys_entity
                    {where_clause}
                """
                count_params = tuple(params) if params else None
                total_result = self.execute_query(count_query, count_params)
                total_count = total_result[0]["total"]

                response_time = (time.time() - start_time) * 1000
                self._track_endpoint_performance("get_jockeys", response_time)

                return {
                    "jockeys": jockeys,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "pages": (total_count + limit - 1) // limit,
                    },
                    "filters_applied": {
                        "min_win_rate": min_win_rate,
                        "min_runs": min_runs,
                    },
                    "performance": {
                        "response_time_ms": round(response_time, 2),
                        "total_records": len(jockeys),
                    },
                }

            except Exception as e:
                logger.error(f"Get jockeys failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/trainers")
        async def get_trainers(
            limit: int = Query(50, le=500),
            offset: int = Query(0, ge=0),
            min_win_rate: Optional[float] = Query(None, ge=0, le=100),
            min_races: Optional[int] = Query(None, ge=1),
        ):
            """Get trainers with performance filtering"""
            start_time = time.time()

            try:
                where_conditions = []
                params = []
                param_count = 1

                if min_races:
                    where_conditions.append(f"total_races >= ${param_count}")
                    params.append(min_races)
                    param_count += 1

                if min_win_rate:
                    where_conditions.append(
                        f"(wins::float / NULLIF(total_races, 0) * 100) >= ${param_count}"
                    )
                    params.append(min_win_rate)
                    param_count += 1

                where_clause = (
                    " WHERE " + " AND ".join(where_conditions)
                    if where_conditions
                    else ""
                )

                trainers_query = f"""
                    SELECT 
                        trainer_id,
                        trainer_name,
                        total_races,
                        wins,
                        win_percentage,
                        (wins::float / NULLIF(total_races, 0) * 100) as calculated_win_rate,
                        placed,
                        place_percentage,
                        created_at,
                        updated_at
                    FROM trainers_entity
                    {where_clause}
                    ORDER BY calculated_win_rate DESC NULLS LAST, total_races DESC
                    LIMIT ${param_count} OFFSET ${param_count + 1}
                """

                trainers_params = (
                    tuple(params + [limit, offset]) if params else (limit, offset)
                )
                trainers = self.execute_query(trainers_query, trainers_params)

                # Get total count
                count_query = f"""
                    SELECT COUNT(*) as total FROM trainers_entity
                    {where_clause}
                """
                count_params = tuple(params) if params else None
                total_result = self.execute_query(count_query, count_params)
                total_count = total_result[0]["total"]

                response_time = (time.time() - start_time) * 1000
                self._track_endpoint_performance("get_trainers", response_time)

                return {
                    "trainers": trainers,
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "pages": (total_count + limit - 1) // limit,
                    },
                    "filters_applied": {
                        "min_win_rate": min_win_rate,
                        "min_races": min_races,
                    },
                    "performance": {
                        "response_time_ms": round(response_time, 2),
                        "total_records": len(trainers),
                    },
                }

            except Exception as e:
                logger.error(f"Get trainers failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/analytics/top-performers")
        async def get_top_performers(
            category: str = Query("jockeys", regex="^(jockeys|trainers|horses)$"),
            metric: str = Query(
                "win_rate", regex="^(win_rate|total_wins|total_races)$"
            ),
            limit: int = Query(10, le=50),
        ):
            """Get top performers across different categories"""
            start_time = time.time()

            try:
                if category == "jockeys":
                    query = f"""
                        SELECT 
                            jockey_name as name,
                            runs as total_races,
                            wins as total_wins,
                            (wins::float / NULLIF(runs, 0) * 100) as win_rate,
                            placed,
                            (placed::float / NULLIF(runs, 0) * 100) as place_rate
                        FROM jockeys_entity
                        WHERE runs > 0
                        ORDER BY {metric.replace('total_races', 'runs')} DESC
                        LIMIT ${1}
                    """
                elif category == "trainers":
                    query = f"""
                        SELECT 
                            trainer_name as name,
                            total_races,
                            wins as total_wins,
                            (wins::float / NULLIF(total_races, 0) * 100) as win_rate,
                            placed,
                            (placed::float / NULLIF(total_races, 0) * 100) as place_rate
                        FROM trainers_entity
                        WHERE total_races > 0
                        ORDER BY {metric} DESC
                        LIMIT ${1}
                    """
                else:  # horses
                    query = f"""
                        SELECT 
                            horse_name as name,
                            age,
                            sex,
                            country,
                            sire,
                            dam
                        FROM horses_entity
                        ORDER BY horse_name
                        LIMIT ${1}
                    """

                results = self.execute_query(query, (limit,))

                response_time = (time.time() - start_time) * 1000
                self._track_endpoint_performance("get_top_performers", response_time)

                return {
                    "category": category,
                    "metric": metric,
                    "top_performers": results,
                    "performance": {
                        "response_time_ms": round(response_time, 2),
                        "total_records": len(results),
                    },
                }

            except Exception as e:
                logger.error(f"Get top performers failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/analytics/statistics")
        async def get_analytics_statistics():
            """Get comprehensive analytics statistics"""
            start_time = time.time()

            try:
                # Get comprehensive statistics
                stats_query = """
                    SELECT 
                        'horses' as entity_type,
                        COUNT(*) as total_count,
                        CAST(ROUND(CAST(AVG(age) AS numeric), 2) AS text) as avg_metric
                    FROM horses_entity
                    WHERE age > 0
                    
                    UNION ALL
                    
                    SELECT 
                        'jockeys',
                        COUNT(*),
                        CAST(ROUND(CAST(AVG(wins::float / NULLIF(runs, 0) * 100) AS numeric), 2) AS text)
                    FROM jockeys_entity
                    WHERE runs > 0
                    
                    UNION ALL
                    
                    SELECT 
                        'trainers',
                        COUNT(*),
                        CAST(ROUND(CAST(AVG(wins::float / NULLIF(total_races, 0) * 100) AS numeric), 2) AS text)
                    FROM trainers_entity
                    WHERE total_races > 0
                """

                stats = self.execute_query(stats_query)

                # Additional detailed statistics
                detailed_stats = {}
                for stat in stats:
                    entity_type = stat["entity_type"]
                    detailed_stats[entity_type] = {
                        "total_count": stat["total_count"],
                        "avg_metric": stat["avg_metric"],
                    }

                # Performance analytics
                response_time = (time.time() - start_time) * 1000
                self._track_endpoint_performance(
                    "get_analytics_statistics", response_time
                )

                return {
                    "statistics": detailed_stats,
                    "system_performance": {
                        "database_avg_query_time_ms": round(
                            self.performance_metrics["database_stats"][
                                "avg_query_time"
                            ],
                            2,
                        ),
                        "total_database_queries": self.performance_metrics[
                            "database_stats"
                        ]["total_queries"],
                        "connection_pool_hits": self.performance_metrics[
                            "database_stats"
                        ]["connection_pool_hits"],
                    },
                    "timestamp": datetime.now().isoformat(),
                    "performance": {"response_time_ms": round(response_time, 2)},
                }

            except Exception as e:
                logger.error(f"Get analytics statistics failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/performance/metrics")
        async def get_performance_metrics():
            """Get comprehensive API and database performance metrics"""
            return {
                "api_metrics": self.performance_metrics,
                "database_environment": {
                    "type": "PostgreSQL",
                    "version": "15.14",
                    "container": "horse_racing_postgres_clean",
                    "database": "results",
                    "total_records": "11,328",
                    "testing_status": "Production Ready",
                },
                "connection_pool": {
                    "min_connections": 2,
                    "max_connections": 20,
                    "current_hits": self.performance_metrics["database_stats"][
                        "connection_pool_hits"
                    ],
                },
                "performance_targets": {
                    "avg_query_time_target": "< 5ms",
                    "api_response_target": "< 100ms",
                    "current_avg_query_time": round(
                        self.performance_metrics["database_stats"]["avg_query_time"], 2
                    ),
                    "current_api_avg_response": round(
                        self.performance_metrics["avg_response_time"], 2
                    ),
                },
                "timestamp": datetime.now().isoformat(),
            }

    def _track_endpoint_performance(self, endpoint: str, response_time: float):
        """Track endpoint performance metrics"""
        self.performance_metrics["total_requests"] += 1

        # Update overall average response time
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["avg_response_time"]
        new_avg = (
            (current_avg * (total_requests - 1)) + response_time
        ) / total_requests
        self.performance_metrics["avg_response_time"] = new_avg

        # Track endpoint-specific metrics
        if endpoint not in self.performance_metrics["endpoint_stats"]:
            self.performance_metrics["endpoint_stats"][endpoint] = {
                "total_requests": 0,
                "avg_response_time": 0,
            }

        endpoint_stats = self.performance_metrics["endpoint_stats"][endpoint]
        endpoint_stats["total_requests"] += 1

        endpoint_total = endpoint_stats["total_requests"]
        endpoint_avg = endpoint_stats["avg_response_time"]
        endpoint_new_avg = (
            (endpoint_avg * (endpoint_total - 1)) + response_time
        ) / endpoint_total
        endpoint_stats["avg_response_time"] = endpoint_new_avg


async def run_api_integration_tests():
    """Run comprehensive API integration tests with PostgreSQL"""

    print("🧪 API PostgreSQL Integration Testing")
    print("=" * 50)

    # Initialize integration manager
    api_manager = APIPostgreSQLIntegration()
    await api_manager.initialize_connection_pool()

    # Test all endpoints
    test_endpoints = [
        "/health",
        "/api/database/status",
        "/api/horses?limit=10",
        "/api/horses?min_age=3&max_age=6&limit=5",
        "/api/jockeys?limit=10&min_runs=50",
        "/api/jockeys?min_win_rate=10&limit=5",
        "/api/trainers?limit=10&min_races=20",
        "/api/trainers?min_win_rate=15&limit=5",
        "/api/analytics/top-performers?category=jockeys&metric=win_rate&limit=5",
        "/api/analytics/top-performers?category=trainers&metric=total_wins&limit=5",
        "/api/analytics/statistics",
        "/api/performance/metrics",
    ]

    print(f"\n📋 Testing {len(test_endpoints)} API endpoints...")

    # Start the API server in background for testing
    import multiprocessing
    import time

    def start_api_server():
        uvicorn.run(api_manager.app, host="127.0.0.1", port=8001, log_level="warning")

    # Start server in separate process
    server_process = multiprocessing.Process(target=start_api_server)
    server_process.start()

    # Wait for server to start
    time.sleep(3)

    try:
        test_results = []
        base_url = "http://127.0.0.1:8001"

        for endpoint in test_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()

                    test_results.append(
                        {
                            "endpoint": endpoint,
                            "status": "✅ SUCCESS",
                            "response_time_ms": round(response_time, 2),
                            "status_code": response.status_code,
                            "data_type": type(data).__name__,
                        }
                    )

                    print(f"  ✅ {endpoint}: {response_time:.2f}ms")

                else:
                    test_results.append(
                        {
                            "endpoint": endpoint,
                            "status": "❌ FAILED",
                            "response_time_ms": round(response_time, 2),
                            "status_code": response.status_code,
                            "error": response.text[:100],
                        }
                    )

                    print(f"  ❌ {endpoint}: {response.status_code}")

            except Exception as e:
                test_results.append(
                    {"endpoint": endpoint, "status": "❌ ERROR", "error": str(e)[:100]}
                )
                print(f"  ❌ {endpoint}: {str(e)[:50]}")

        # Calculate test summary
        successful_tests = len([r for r in test_results if r["status"] == "✅ SUCCESS"])
        avg_response_time = sum(
            [
                r.get("response_time_ms", 0)
                for r in test_results
                if "response_time_ms" in r
            ]
        ) / len([r for r in test_results if "response_time_ms" in r])

        print(f"\n📊 Test Results Summary:")
        print(f"  Total Endpoints: {len(test_endpoints)}")
        print(f"  Successful: {successful_tests}")
        print(f"  Failed: {len(test_endpoints) - successful_tests}")
        print(f"  Success Rate: {(successful_tests/len(test_endpoints)*100):.1f}%")
        print(f"  Average Response Time: {avg_response_time:.2f}ms")

        # Test database performance
        print(f"\n⚡ Database Performance Validation:")

        # Get performance metrics
        try:
            response = requests.get(f"{base_url}/api/performance/metrics")
            if response.status_code == 200:
                metrics = response.json()
                db_avg_time = metrics["performance_targets"]["current_avg_query_time"]
                api_avg_time = metrics["performance_targets"][
                    "current_api_avg_response"
                ]

                print(f"  Database Avg Query Time: {db_avg_time}ms")
                print(f"  API Avg Response Time: {api_avg_time}ms")
                print(
                    f"  Connection Pool Hits: {metrics['connection_pool']['current_hits']}"
                )

                # Validate performance targets
                if db_avg_time < 5:
                    print(f"  ✅ Database performance target met (< 5ms)")
                else:
                    print(f"  ⚠️  Database performance above target: {db_avg_time}ms")

                if api_avg_time < 100:
                    print(f"  ✅ API performance target met (< 100ms)")
                else:
                    print(f"  ⚠️  API performance above target: {api_avg_time}ms")

        except Exception as e:
            print(f"  ❌ Performance metrics unavailable: {e}")

        print(f"\n🎯 API PostgreSQL Integration Test Completed!")

        if successful_tests == len(test_endpoints):
            print(f"✅ All endpoints working with PostgreSQL backend!")
            print(f"🚀 Ready for production API integration!")
        else:
            print(f"⚠️  Some endpoints need attention before production")

        return test_results

    finally:
        # Clean up server process
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.kill()


def start_integrated_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the PostgreSQL-integrated API server"""

    print("🏇 Starting PostgreSQL-Integrated API Server")
    print("=" * 50)

    async def startup():
        api_manager = APIPostgreSQLIntegration()
        await api_manager.initialize_connection_pool()
        return api_manager

    # Create and run the server
    api_manager = APIPostgreSQLIntegration()

    # Initialize connection pool synchronously for startup
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(api_manager.initialize_connection_pool())

    print(f"🌐 API Server starting on http://{host}:{port}")
    print(f"📊 Endpoints available:")
    print(f"  - Health Check: http://{host}:{port}/health")
    print(f"  - Database Status: http://{host}:{port}/api/database/status")
    print(f"  - Horses API: http://{host}:{port}/api/horses")
    print(f"  - Jockeys API: http://{host}:{port}/api/jockeys")
    print(f"  - Trainers API: http://{host}:{port}/api/trainers")
    print(f"  - Analytics: http://{host}:{port}/api/analytics/statistics")
    print(f"  - Performance: http://{host}:{port}/api/performance/metrics")

    # Start the server
    uvicorn.run(api_manager.app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run integration tests
            import asyncio

            asyncio.run(run_api_integration_tests())
        elif sys.argv[1] == "server":
            # Start the integrated API server
            start_integrated_api_server()
        else:
            print("Usage: python api_postgresql_integration_v2_05.py [test|server]")
    else:
        # Default: run tests
        import asyncio

        asyncio.run(run_api_integration_tests())
