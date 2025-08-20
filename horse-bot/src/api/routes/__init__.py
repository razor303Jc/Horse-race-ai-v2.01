"""
API routes for the Horse Race Handicapping AI system.
Main router that includes all sub-routers.
"""

from fastapi import APIRouter

from .health import router as health_router
from .races import router as races_router
from .participants import router as participants_router
from .betting import router as betting_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(races_router, prefix="/races", tags=["races"])
api_router.include_router(participants_router, prefix="/participants", tags=["participants"])
api_router.include_router(betting_router, prefix="/betting", tags=["betting"])

# TODO: Add these routers when implemented
# from .predictions import router as predictions_router
# from .simulations import router as simulations_router
# from .analytics import router as analytics_router
# api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
# api_router.include_router(simulations_router, prefix="/simulations", tags=["simulations"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
