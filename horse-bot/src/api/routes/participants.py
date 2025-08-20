"""
Horse, jockey, and trainer data endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...services.data_provider import get_data_provider

router = APIRouter()


class HorseProfileResponse(BaseModel):
    """Response model for horse profile data."""
    name: str
    horse_id: str
    age: int
    sex: str
    trainer: str
    career_record: dict
    preferred_distance: Optional[float]
    preferred_surface: Optional[str]


class JockeyStatsResponse(BaseModel):
    """Response model for jockey statistics."""
    name: str
    jockey_id: str
    stats_2024: dict
    career_stats: dict
    specialties: List[str]


class TrainerStatsResponse(BaseModel):
    """Response model for trainer statistics."""
    name: str
    trainer_id: str
    stable_size: int
    stats_2024: dict
    career_stats: dict
    specialties: List[str]


@router.get("/horses/{horse_name}", response_model=HorseProfileResponse)
async def get_horse_profile(horse_name: str):
    """Get horse profile by name."""
    try:
        data_provider = get_data_provider()
        horse = await data_provider.get_horse_profile(horse_name)
        
        if not horse:
            raise HTTPException(status_code=404, detail="Horse not found")
        
        return HorseProfileResponse(
            name=horse["name"],
            horse_id=horse["horse_id"],
            age=horse["age"],
            sex=horse["sex"],
            trainer=horse.get("trainer", "Unknown"),
            career_record=horse["career_record"],
            preferred_distance=horse.get("preferred_distance"),
            preferred_surface=horse.get("preferred_surface")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get horse profile: {str(e)}")


@router.get("/horses/search")
async def search_horses(q: str = Query(..., description="Search query for horse names")):
    """Search horses by name."""
    try:
        data_provider = get_data_provider()
        horses = await data_provider.search_horses(q)
        
        return {
            "query": q,
            "count": len(horses),
            "horses": [
                {
                    "name": horse["name"],
                    "horse_id": horse["horse_id"],
                    "age": horse["age"],
                    "trainer": horse.get("trainer", "Unknown"),
                    "wins": horse["career_record"]["wins"],
                    "starts": horse["career_record"]["starts"]
                }
                for horse in horses
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search horses: {str(e)}")


@router.get("/jockeys/{jockey_name}", response_model=JockeyStatsResponse)
async def get_jockey_stats(jockey_name: str):
    """Get jockey statistics by name."""
    try:
        data_provider = get_data_provider()
        jockey = await data_provider.get_jockey_stats(jockey_name)
        
        if not jockey:
            raise HTTPException(status_code=404, detail="Jockey not found")
        
        return JockeyStatsResponse(
            name=jockey["name"],
            jockey_id=jockey["jockey_id"],
            stats_2024=jockey["stats_2024"],
            career_stats=jockey["career_stats"],
            specialties=jockey.get("specialties", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jockey stats: {str(e)}")


@router.get("/trainers/{trainer_name}", response_model=TrainerStatsResponse)
async def get_trainer_stats(trainer_name: str):
    """Get trainer statistics by name."""
    try:
        data_provider = get_data_provider()
        trainer = await data_provider.get_trainer_stats(trainer_name)
        
        if not trainer:
            raise HTTPException(status_code=404, detail="Trainer not found")
        
        return TrainerStatsResponse(
            name=trainer["name"],
            trainer_id=trainer["trainer_id"],
            stable_size=trainer["stable_size"],
            stats_2024=trainer["stats_2024"],
            career_stats=trainer["career_stats"],
            specialties=trainer.get("specialties", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trainer stats: {str(e)}")


@router.get("/tracks/{track_code}")
async def get_track_info(track_code: str):
    """Get track information by code."""
    try:
        data_provider = get_data_provider()
        track = await data_provider.get_track_info(track_code.upper())
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        return track
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track info: {str(e)}")


@router.get("/participants/summary")
async def get_participants_summary():
    """Get summary of all participants (horses, jockeys, trainers)."""
    try:
        data_provider = get_data_provider()
        
        # Get health check which includes data summary
        health = await data_provider.health_check()
        test_summary = health.get("test_data_summary", {})
        
        return {
            "data_source": data_provider.get_data_source_info()["current_source"],
            "statistics": {
                "total_horses": test_summary.get("horses", 0),
                "total_jockeys": 20,  # From our generated data
                "total_trainers": 20,  # From our generated data
                "total_tracks": 10    # From our generated data
            },
            "endpoints": {
                "horse_profile": "/api/participants/horses/{horse_name}",
                "horse_search": "/api/participants/horses/search?q={query}",
                "jockey_stats": "/api/participants/jockeys/{jockey_name}",
                "trainer_stats": "/api/participants/trainers/{trainer_name}",
                "track_info": "/api/participants/tracks/{track_code}",
                "summary": "/api/participants/summary"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get participants summary: {str(e)}")
