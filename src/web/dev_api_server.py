#!/usr/bin/env python3
"""
Development API Server for AI Selections Results
===============================================

Simple FastAPI server to test the AI Selections Results page
during development.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add the web directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from performance_api import performance_api
except ImportError as e:
    print(f"Error importing performance_api: {e}")
    performance_api = None

app = FastAPI(title="AI Selections Development API", version="1.0.0")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AI Selections Development API", "status": "running"}


@app.get("/api/ai_selections/performance")
async def get_ai_selections_performance(days_back: int = 30):
    """Get AI selections performance analytics from PostgreSQL"""
    try:
        if not performance_api:
            raise HTTPException(status_code=500, detail="Performance API not available")

        # Get comprehensive performance data
        result = performance_api.get_performance_summary(days_back=days_back)

        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        print(f"Error fetching AI selections performance: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch performance data: {str(e)}",
            "data": {
                "summary": {
                    "total_predictions": 0,
                    "accuracy_rate": 0.0,
                    "roi_percentage": 0.0,
                    "total_profit_loss": 0.0,
                }
            },
        }


@app.get("/api/ai_selections/recent")
async def get_recent_ai_selections(limit: int = 50, offset: int = 0):
    """Get recent AI selections with P&L results and pagination support"""
    try:
        if not performance_api:
            raise HTTPException(status_code=500, detail="Performance API not available")

        result = performance_api.get_recent_selections(limit=limit, offset=offset)

        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        print(f"Error fetching recent AI selections: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch recent selections: {str(e)}",
            "data": {"selections": [], "count": 0, "total_count": 0},
        }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        if performance_api:
            test_result = performance_api.get_recent_selections(limit=1)
            db_status = "connected" if test_result["status"] == "success" else "error"
        else:
            db_status = "unavailable"

        return {
            "status": "healthy",
            "database": db_status,
            "api_version": "1.0.0",
            "endpoints": [
                "/api/ai_selections/performance",
                "/api/ai_selections/recent",
                "/api/health",
            ],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    print("🚀 Starting AI Selections Development API Server...")
    print("📊 Available endpoints:")
    print("  - GET /api/ai_selections/performance?days_back=30")
    print("  - GET /api/ai_selections/recent?limit=50&offset=0")
    print("  - GET /api/health")
    print("  - GET /")
    print("🌐 CORS enabled for frontend development")
    print("💻 Server will be available at: http://localhost:8001")

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True, log_level="info")
