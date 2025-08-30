#!/usr/bin/env python3
"""
Simple API PostgreSQL Integration Test - V2.05
=============================================

Direct API integration test with PostgreSQL backend using psycopg2
for connection pooling and performance validation.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "results",
    "user": "horse_racing",
    "password": "horse_racing_password"
}

class SimpleAPIPostgreSQL:
    """Simple API with PostgreSQL integration"""
    
    def __init__(self):
        self.pool = None
        self.app = FastAPI(title="Horse Racing API - PostgreSQL", version="2.05")
        
        # Enable CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.performance_metrics = {
            "total_requests": 0,
            "avg_response_time": 0,
            "total_queries": 0,
            "avg_query_time": 0
        }
        
        self._setup_routes()
    
    def initialize_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            # Test connection first
            test_conn = psycopg2.connect(**POSTGRES_CONFIG)
            test_conn.close()
            logger.info("✅ PostgreSQL connection test successful")
            
            # Initialize pool
            self.pool = SimpleConnectionPool(
                minconn=2,
                maxconn=10,
                **POSTGRES_CONFIG
            )
            
            logger.info("✅ PostgreSQL connection pool initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL pool: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query with performance tracking"""
        start_time = time.time()
        conn = None
        
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            results = [dict(row) for row in results]
            
            cursor.close()
            
            # Track performance
            query_time = (time.time() - start_time) * 1000
            self.performance_metrics["total_queries"] += 1
            
            # Update average
            total = self.performance_metrics["total_queries"]
            current_avg = self.performance_metrics["avg_query_time"]
            new_avg = ((current_avg * (total - 1)) + query_time) / total
            self.performance_metrics["avg_query_time"] = new_avg
            
            return results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        def health_check():
            """Health check with database validation"""
            start_time = time.time()
            
            try:
                results = self.execute_query("SELECT 1 as test")
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "status": "healthy",
                    "database": "connected",
                    "response_time_ms": round(response_time, 2),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.get("/api/database/status")
        def database_status():
            """Get database status and metrics"""
            try:
                # Get entity counts
                horses = self.execute_query("SELECT COUNT(*) as count FROM horses_entity")
                jockeys = self.execute_query("SELECT COUNT(*) as count FROM jockeys_entity")
                trainers = self.execute_query("SELECT COUNT(*) as count FROM trainers_entity")
                
                total_records = horses[0]["count"] + jockeys[0]["count"] + trainers[0]["count"]
                
                return {
                    "database": "results",
                    "status": "operational",
                    "entity_counts": {
                        "horses": horses[0]["count"],
                        "jockeys": jockeys[0]["count"],
                        "trainers": trainers[0]["count"],
                        "total": total_records
                    },
                    "performance": self.performance_metrics,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/horses")
        def get_horses(limit: int = Query(10, le=100)):
            """Get horses from PostgreSQL"""
            start_time = time.time()
            
            try:
                query = """
                    SELECT 
                        horse_id,
                        horse_name,
                        age,
                        sex,
                        country,
                        sire,
                        dam
                    FROM horses_entity
                    ORDER BY horse_name
                    LIMIT %s
                """
                
                horses = self.execute_query(query, (limit,))
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "horses": horses,
                    "total_returned": len(horses),
                    "response_time_ms": round(response_time, 2)
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/jockeys")
        def get_jockeys(limit: int = Query(10, le=100)):
            """Get jockeys with performance data"""
            start_time = time.time()
            
            try:
                query = """
                    SELECT 
                        jockey_id,
                        jockey_name,
                        runs,
                        wins,
                        (wins::float / NULLIF(runs, 0) * 100) as calculated_win_rate
                    FROM jockeys_entity
                    WHERE runs > 0
                    ORDER BY calculated_win_rate DESC
                    LIMIT %s
                """
                
                jockeys = self.execute_query(query, (limit,))
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "jockeys": jockeys,
                    "total_returned": len(jockeys),
                    "response_time_ms": round(response_time, 2)
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/performance")
        def get_performance():
            """Get API and database performance metrics"""
            return {
                "api_metrics": self.performance_metrics,
                "database_info": {
                    "type": "PostgreSQL",
                    "version": "15.14",
                    "container": "horse_racing_postgres_clean"
                },
                "timestamp": datetime.now().isoformat()
            }

def run_simple_integration_test():
    """Run simple API integration test"""
    
    print("🧪 Simple API PostgreSQL Integration Test")
    print("=" * 50)
    
    # Initialize API
    api = SimpleAPIPostgreSQL()
    api.initialize_pool()
    
    # Start server in thread
    def start_server():
        uvicorn.run(api.app, host="127.0.0.1", port=8002, log_level="warning")
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Test endpoints
    test_endpoints = [
        "/health",
        "/api/database/status", 
        "/api/horses?limit=5",
        "/api/jockeys?limit=5",
        "/api/performance"
    ]
    
    print(f"\n📋 Testing {len(test_endpoints)} endpoints...")
    
    base_url = "http://127.0.0.1:8002"
    test_results = []
    
    for endpoint in test_endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                test_results.append({
                    "endpoint": endpoint,
                    "status": "✅ SUCCESS",
                    "response_time_ms": round(response_time, 2),
                    "data_preview": str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                })
                
                print(f"  ✅ {endpoint}: {response_time:.2f}ms")
                
                # Show interesting data
                if "horses" in data:
                    print(f"    📊 Returned {len(data['horses'])} horses")
                elif "jockeys" in data:
                    print(f"    📊 Returned {len(data['jockeys'])} jockeys")
                elif "entity_counts" in data:
                    counts = data["entity_counts"]
                    print(f"    📊 Total records: {counts['total']} (H:{counts['horses']}, J:{counts['jockeys']}, T:{counts['trainers']})")
                
            else:
                test_results.append({
                    "endpoint": endpoint,
                    "status": "❌ FAILED",
                    "status_code": response.status_code,
                    "error": response.text[:100]
                })
                
                print(f"  ❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            test_results.append({
                "endpoint": endpoint,
                "status": "❌ ERROR",
                "error": str(e)[:100]
            })
            print(f"  ❌ {endpoint}: {str(e)[:50]}")
    
    # Get final performance metrics
    try:
        response = requests.get(f"{base_url}/api/performance")
        if response.status_code == 200:
            metrics = response.json()["api_metrics"]
            
            print(f"\n⚡ Performance Summary:")
            print(f"  Total Queries: {metrics['total_queries']}")
            print(f"  Avg Query Time: {metrics['avg_query_time']:.2f}ms")
            print(f"  Total Requests: {metrics['total_requests']}")
            
    except Exception as e:
        print(f"  ❌ Could not retrieve performance metrics: {e}")
    
    # Summary
    successful = len([r for r in test_results if "SUCCESS" in r["status"]])
    
    print(f"\n📊 Test Results:")
    print(f"  Total Endpoints: {len(test_endpoints)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(test_endpoints) - successful}")
    print(f"  Success Rate: {(successful/len(test_endpoints)*100):.1f}%")
    
    if successful == len(test_endpoints):
        print(f"\n✅ All API endpoints working with PostgreSQL!")
        print(f"🚀 PostgreSQL API integration successful!")
    else:
        print(f"\n⚠️  Some endpoints need attention")
    
    return test_results

if __name__ == "__main__":
    run_simple_integration_test()
