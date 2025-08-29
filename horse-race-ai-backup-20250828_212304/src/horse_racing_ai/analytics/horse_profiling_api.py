"""
Horse Profiling API endpoints for PostgreSQL-based horse analysis.
Provides REST API access to horse profiling system capabilities.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import asyncio
import functools

from .postgres_horse_profiling import (
    PostgreSQLHorseProfilingSystem,
    HorseProfile,
    HorseFormTrend,
    ConditionProfile,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Horse Profiling API", version="1.0.0")


# Pydantic models for API responses
class HorseProfileResponse(BaseModel):
    """Response model for horse profile data."""

    horse_id: str
    horse_name: str
    form_trend: str
    trend_confidence: float
    preferred_conditions: Dict[str, str]
    performance_metrics: Dict[str, float]
    last_updated: datetime
    confidence_level: float


class ConditionProfileResponse(BaseModel):
    """Response model for condition-specific performance data."""

    condition_name: str
    runs: int
    wins: int
    places: int
    win_rate: float
    place_rate: float
    avg_rating: float
    best_rating: float
    roi: float
    sample_size_adequate: bool


class ProgressiveHorseResponse(BaseModel):
    """Response model for progressive horses list."""

    horse_id: str
    horse_name: str
    form_trend: str


class HorseFormTrendResponse(BaseModel):
    """Response model for form trend classification."""

    horse_id: str
    form_trend: str


# Database dependency
def get_profiling_system() -> PostgreSQLHorseProfilingSystem:
    """Get PostgreSQL horse profiling system instance."""
    return PostgreSQLHorseProfilingSystem()


def run_async(func):
    """Decorator to run async functions in sync context."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Horse Profiling API",
        "version": "1.0.0",
        "description": "PostgreSQL-based horse profiling and analysis system",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        profiling_system = get_profiling_system()
        # Test database connection
        profiling_system.get_db_connection().close()
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/horses/{horse_id}/profile", response_model=HorseProfileResponse)
async def get_horse_profile(
    horse_id: str,
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Get comprehensive profile for a specific horse."""
    try:
        profile = profiling_system.generate_horse_profile(horse_id)

        if not profile:
            raise HTTPException(
                status_code=404, detail=f"Horse profile not found for ID: {horse_id}"
            )

        return HorseProfileResponse(
            horse_id=profile.horse_id,
            horse_name=profile.horse_name,
            form_trend=profile.form_trend.value,
            trend_confidence=profile.trend_confidence,
            preferred_conditions=profile.preferred_conditions,
            performance_metrics=profile.performance_metrics,
            last_updated=profile.last_updated,
            confidence_level=profile.confidence_level,
        )

    except Exception as e:
        logger.error("Failed to get horse profile for %s: %s", horse_id, e)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate horse profile: {str(e)}"
        )


@app.get("/horses/{horse_id}/form-trend", response_model=HorseFormTrendResponse)
async def get_horse_form_trend(
    horse_id: str,
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Get form trend classification for a specific horse."""
    try:
        form_trend = profiling_system.classify_form_trend(horse_id)

        return HorseFormTrendResponse(horse_id=horse_id, form_trend=form_trend.value)

    except Exception as e:
        logger.error("Failed to get form trend for %s: %s", horse_id, e)
        raise HTTPException(
            status_code=500, detail=f"Failed to classify form trend: {str(e)}"
        )


@app.get(
    "/horses/{horse_id}/conditions/{condition_type}",
    response_model=List[ConditionProfileResponse],
)
async def get_condition_profiles(
    horse_id: str,
    condition_type: str,
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Get condition-specific performance profiles for a horse."""
    if condition_type not in ["track", "distance", "going", "class"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid condition type. Must be: track, distance, going, class",
        )

    try:
        profiles = profiling_system.analyze_condition_profiles(horse_id, condition_type)

        response_data = []
        for condition_name, profile in profiles.items():
            response_data.append(
                ConditionProfileResponse(
                    condition_name=condition_name,
                    runs=profile.runs,
                    wins=profile.wins,
                    places=profile.places,
                    win_rate=profile.win_rate,
                    place_rate=profile.place_rate,
                    avg_rating=profile.avg_rating,
                    best_rating=profile.best_rating,
                    roi=profile.roi,
                    sample_size_adequate=profile.sample_size_adequate,
                )
            )

        return response_data

    except Exception as e:
        logger.error(
            "Failed to get %s profiles for %s: %s", condition_type, horse_id, e
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze condition profiles: {str(e)}"
        )


@app.get("/horses/progressive", response_model=List[ProgressiveHorseResponse])
async def get_progressive_horses(
    min_runs: int = Query(5, description="Minimum number of runs required"),
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Get list of horses currently showing progressive form."""
    try:
        progressive_horses = profiling_system.get_progressive_horses(min_runs)

        return [
            ProgressiveHorseResponse(
                horse_id=horse["horse_id"],
                horse_name=horse["horse_name"],
                form_trend=horse["form_trend"],
            )
            for horse in progressive_horses
        ]

    except Exception as e:
        logger.error("Failed to get progressive horses: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to get progressive horses: {str(e)}"
        )


@app.post("/horses/{horse_id}/profile/save")
async def save_horse_profile(
    horse_id: str,
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Generate and save horse profile to database."""
    try:
        profile = profiling_system.generate_horse_profile(horse_id)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to generate profile for horse ID: {horse_id}",
            )

        profiling_system.save_horse_profile(profile)

        return {
            "message": f"Profile saved successfully for horse {horse_id}",
            "horse_id": horse_id,
            "profile_confidence": profile.confidence_level,
            "timestamp": datetime.now(),
        }

    except Exception as e:
        logger.error("Failed to save profile for %s: %s", horse_id, e)
        raise HTTPException(
            status_code=500, detail=f"Failed to save horse profile: {str(e)}"
        )


@app.post("/system/initialize")
async def initialize_profiling_system(
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Initialize the horse profiling system and create required tables."""
    try:
        profiling_system.create_profiling_tables()

        return {
            "message": "Horse profiling system initialized successfully",
            "timestamp": datetime.now(),
            "status": "ready",
        }

    except Exception as e:
        logger.error("Failed to initialize profiling system: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize system: {str(e)}"
        )


@app.get("/system/status")
async def get_system_status(
    profiling_system: PostgreSQLHorseProfilingSystem = Depends(get_profiling_system),
):
    """Get system status and configuration information."""
    try:
        with profiling_system.get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Check if tables exist
                cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'horse_form_trends', 
                        'horse_optimal_conditions'
                    )
                """
                )
                existing_tables = [row[0] for row in cursor.fetchall()]

                # Get table counts
                table_counts = {}
                for table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]

        return {
            "status": "operational",
            "database_connection": "active",
            "tables_created": existing_tables,
            "table_counts": table_counts,
            "timestamp": datetime.now(),
            "configuration": {
                "min_runs_for_trend": profiling_system.min_runs_for_trend,
                "min_runs_for_condition": profiling_system.min_runs_for_condition,
                "adequate_sample_size": profiling_system.adequate_sample_size,
            },
        }

    except Exception as e:
        logger.error("Failed to get system status: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to get system status: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
