"""
Health check endpoints for monitoring and status.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "horse-race-handicapping-ai",
        "version": "0.1.0"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with system information."""
    from ...services.data_provider import get_data_provider
    
    # Get data provider for health checks
    data_provider = get_data_provider()
    
    # Check data provider health
    data_health = await data_provider.health_check()
    source_info = data_provider.get_data_source_info()
    
    # Initialize component status
    components = {
        "database": "unknown",
        "redis": "unknown", 
        "data_provider": data_health["status"],
        "data_source": source_info["current_source"],
        "test_data": "healthy" if data_health.get("test_data_available") else "unavailable",
        "live_data": "healthy" if data_health.get("live_data_available") else "unavailable",
        "ml_models": "unknown"
    }
    
    # Add test data summary if available
    if data_health.get("test_data_summary"):
        components["test_data_summary"] = {
            "race_cards": data_health["test_data_summary"]["race_cards"],
            "total_races": data_health["test_data_summary"]["total_races"],
            "horses": data_health["test_data_summary"]["total_horses"]
        }
    
    # TODO: Add database connectivity check
    # TODO: Add Redis connectivity check
    # TODO: Add ML model availability checks
    
    # Determine overall status based on data provider
    if data_health["status"] == "healthy":
        overall_status = "healthy"
    elif data_health["status"] == "degraded":
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    if any(status.startswith("error") or status == "unhealthy" for status in components.values()):
        overall_status = "degraded"
    if all(status.startswith("error") or status == "unhealthy" for status in components.values()):
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "horse-race-handicapping-ai",
        "version": "0.1.0",
        "components": components
    }
