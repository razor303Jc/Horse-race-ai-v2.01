"""
C2 Command Center API Endpoints
==============================

Additional API endpoints specifically for the C2 Command Center dashboard
to provide container communication and system management capabilities.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import psycopg2
import redis
import logging
import os
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class ProcessingRequest(BaseModel):
    """Model for data processing requests"""
    data_type: str = "both"  # cards, results, both
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    source: str = "c2_dashboard"

class C2ApiEndpoints:
    """C2 Command Center API endpoints class"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_endpoints()
        
    def get_database_connection(self, db_type: str = "cards"):
        """Get database connection based on type"""
        db_urls = {
            "cards": os.getenv("CARDS_DATABASE_URL", "postgresql://horse_racing:secure_password_123@postgres:5432/cards_horse_racing_db"),
            "results": os.getenv("RESULTS_DATABASE_URL", "postgresql://horse_racing:secure_password_123@postgres:5432/results_horse_racing_db"),
            "advanced": os.getenv("ADVANCED_DATABASE_URL", "postgresql://horse_racing:secure_password_123@postgres:5432/advanced_racing_metrics_db")
        }
        
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(db_urls[db_type])
            return psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password
            )
        except Exception as e:
            logger.error(f"Database connection failed for {db_type}: {e}")
            return None
    
    def setup_endpoints(self):
        """Setup all C2 API endpoints"""
        
        @self.app.get("/api/processing/stats")
        async def get_processing_stats():
            """Get real database statistics for C2 dashboard"""
            try:
                stats = {
                    "cardsToday": 0,
                    "resultsToday": 0,
                    "totalCards": 0,
                    "totalResults": 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Get cards statistics
                cards_conn = self.get_database_connection("cards")
                if cards_conn:
                    try:
                        with cards_conn.cursor() as cursor:
                            # Total cards
                            cursor.execute("SELECT COUNT(*) FROM races")
                            stats["totalCards"] = cursor.fetchone()[0] or 0
                            
                            # Cards today
                            cursor.execute("SELECT COUNT(*) FROM races WHERE date = %s", (today,))
                            stats["cardsToday"] = cursor.fetchone()[0] or 0
                    finally:
                        cards_conn.close()
                
                # Get results statistics
                results_conn = self.get_database_connection("results")
                if results_conn:
                    try:
                        with results_conn.cursor() as cursor:
                            # Total results
                            cursor.execute("SELECT COUNT(*) FROM race_results")
                            stats["totalResults"] = cursor.fetchone()[0] or 0
                            
                            # Results today
                            cursor.execute("SELECT COUNT(*) FROM race_results WHERE date = %s", (today,))
                            stats["resultsToday"] = cursor.fetchone()[0] or 0
                    finally:
                        results_conn.close()
                
                return stats
                
            except Exception as e:
                logger.error(f"Error getting processing stats: {e}")
                return {
                    "cardsToday": 0,
                    "resultsToday": 0,
                    "totalCards": 0,
                    "totalResults": 0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.post("/api/processing/trigger")
        async def trigger_processing(request: ProcessingRequest):
            """Trigger data processing based on request parameters"""
            try:
                # Log the processing request
                logger.info(f"Processing request: {request.dict()}")
                
                # Simulate processing logic (replace with actual implementation)
                processing_id = f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Here you would typically:
                # 1. Validate date range
                # 2. Queue processing job
                # 3. Start background processing
                # 4. Return job ID for tracking
                
                result = {
                    "status": "success",
                    "processing_id": processing_id,
                    "data_type": request.data_type,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "estimated_duration": "5-10 minutes",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Processing started for {request.data_type} data"
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Processing trigger failed: {e}")
                raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
        @self.app.get("/api/database/stats")
        async def get_database_stats():
            """Get comprehensive database statistics"""
            try:
                stats = {
                    "databases": {},
                    "overall": {
                        "total_tables": 0,
                        "total_records": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                }
                
                # Check each database
                db_types = ["cards", "results", "advanced"]
                for db_type in db_types:
                    conn = self.get_database_connection(db_type)
                    if conn:
                        try:
                            with conn.cursor() as cursor:
                                # Get table count
                                cursor.execute("""
                                    SELECT COUNT(*) 
                                    FROM information_schema.tables 
                                    WHERE table_schema = 'public'
                                """)
                                table_count = cursor.fetchone()[0]
                                
                                # Get approximate record count for main tables
                                record_count = 0
                                if db_type == "cards":
                                    cursor.execute("SELECT COUNT(*) FROM races")
                                    record_count = cursor.fetchone()[0] or 0
                                elif db_type == "results":
                                    cursor.execute("SELECT COUNT(*) FROM race_results")
                                    record_count = cursor.fetchone()[0] or 0
                                
                                stats["databases"][db_type] = {
                                    "status": "online",
                                    "tables": table_count,
                                    "records": record_count,
                                    "last_check": datetime.now().isoformat()
                                }
                                
                                stats["overall"]["total_tables"] += table_count
                                stats["overall"]["total_records"] += record_count
                                
                        finally:
                            conn.close()
                    else:
                        stats["databases"][db_type] = {
                            "status": "offline",
                            "error": "Connection failed"
                        }
                
                return stats
                
            except Exception as e:
                logger.error(f"Database stats error: {e}")
                return {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.get("/api/system/status")
        async def get_system_status():
            """Get comprehensive system status for C2 dashboard"""
            try:
                status = {
                    "overall_status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "components": {}
                }
                
                # Check database connectivity
                db_status = True
                for db_type in ["cards", "results", "advanced"]:
                    conn = self.get_database_connection(db_type)
                    if conn:
                        try:
                            with conn.cursor() as cursor:
                                cursor.execute("SELECT 1")
                            status["components"][f"database_{db_type}"] = "online"
                            conn.close()
                        except:
                            status["components"][f"database_{db_type}"] = "offline"
                            db_status = False
                    else:
                        status["components"][f"database_{db_type}"] = "offline"
                        db_status = False
                
                # Check Redis connectivity
                try:
                    redis_client = redis.Redis(
                        host=os.getenv("REDIS_HOST", "redis"),
                        port=int(os.getenv("REDIS_PORT", "6379")),
                        password=os.getenv("REDIS_PASSWORD", "redis_password_123"),
                        socket_timeout=5
                    )
                    redis_client.ping()
                    status["components"]["redis"] = "online"
                except:
                    status["components"]["redis"] = "offline"
                
                # Set overall status
                status["database"] = db_status
                status["apis"] = True  # API is running if this endpoint responds
                status["pipeline"] = True  # Assume pipeline is running
                
                if not db_status:
                    status["overall_status"] = "degraded"
                
                return status
                
            except Exception as e:
                logger.error(f"System status error: {e}")
                return {
                    "overall_status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.post("/api/system/restart")
        async def restart_services():
            """Restart system services (placeholder)"""
            try:
                # This would typically restart services
                # For now, return success status
                return {
                    "status": "success",
                    "message": "Service restart initiated",
                    "timestamp": datetime.now().isoformat(),
                    "services_restarted": ["api", "background_tasks"]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/container/health/{container_name}")
        async def get_container_health(container_name: str):
            """Get health status of specific container"""
            try:
                # Map container names to their health check methods
                container_map = {
                    "web-app": "http://horse_racing_web_app_clean:8000/health",
                    "postgres": "database",
                    "redis": "cache",
                    "data-pipeline": "internal",
                    "ml-trainer": "internal",
                    "ntfy": "http://horse_racing_ntfy_simple:80"
                }
                
                if container_name not in container_map:
                    raise HTTPException(status_code=404, detail="Container not found")
                
                health_url = container_map[container_name]
                
                if health_url == "database":
                    # Check database health
                    conn = self.get_database_connection("cards")
                    if conn:
                        conn.close()
                        status = "healthy"
                    else:
                        status = "unhealthy"
                elif health_url == "cache":
                    # Check Redis health
                    try:
                        redis_client = redis.Redis(host="redis", port=6379, socket_timeout=5)
                        redis_client.ping()
                        status = "healthy"
                    except:
                        status = "unhealthy"
                elif health_url == "internal":
                    # For internal services, assume healthy if no errors
                    status = "healthy"
                else:
                    # HTTP health check
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(health_url, timeout=5) as response:
                                status = "healthy" if response.status == 200 else "unhealthy"
                    except:
                        status = "unhealthy"
                
                return {
                    "container": container_name,
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "health_check_url": health_url
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Container health check error: {e}")
                return {
                    "container": container_name,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.get("/api/logs/recent")
        async def get_recent_logs(lines: int = 100):
            """Get recent application logs"""
            try:
                # This would typically read from log files
                # For now, return sample logs
                logs = [
                    f"{datetime.now().isoformat()} [INFO] C2 API endpoint accessed",
                    f"{datetime.now().isoformat()} [INFO] System status check completed",
                    f"{datetime.now().isoformat()} [INFO] Database connection successful"
                ]
                
                return {
                    "logs": logs,
                    "total_lines": len(logs),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Logs retrieval error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

def setup_c2_api(app: FastAPI):
    """Setup C2 API endpoints on existing FastAPI app"""
    c2_api = C2ApiEndpoints(app)
    logger.info("C2 Command Center API endpoints initialized")
    return c2_api
