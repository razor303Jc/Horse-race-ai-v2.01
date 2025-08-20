"""
Race data endpoints for the Horse Race Handicapping AI.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...services.data_provider import get_data_provider

router = APIRouter()


class RaceResponse(BaseModel):
    """Response model for race data."""
    race_id: str
    track_name: str
    race_number: int
    race_date: str
    post_time: Optional[str]
    distance: Optional[float]
    surface: Optional[str]
    condition: Optional[str]
    race_type: Optional[str]
    purse: Optional[int]
    field_size: int
    horses: List[dict]


class RaceCardResponse(BaseModel):
    """Response model for race card data."""
    date: str
    total_races: int
    races: List[RaceResponse]


@router.get("/today", response_model=List[RaceResponse])
async def get_todays_races():
    """Get today's race cards."""
    try:
        data_provider = get_data_provider()
        races = await data_provider.get_todays_races()
        
        return [
            RaceResponse(
                race_id=race["race_id"],
                track_name=race["track_name"],
                race_number=race["race_number"],
                race_date=race["race_date"],
                post_time=race.get("post_time"),
                distance=race.get("distance"),
                surface=race.get("surface"),
                condition=race.get("condition"),
                race_type=race.get("race_type"),
                purse=race.get("purse"),
                field_size=race["field_size"],
                horses=race["horses"]
            )
            for race in races
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get today's races: {str(e)}")


@router.get("/date/{race_date}", response_model=List[RaceResponse])
async def get_races_by_date(race_date: str):
    """Get race cards for a specific date (YYYY-MM-DD format)."""
    try:
        # Validate date format
        date.fromisoformat(race_date)
        
        data_provider = get_data_provider()
        races = await data_provider.get_races_by_date(race_date)
        
        return [
            RaceResponse(
                race_id=race["race_id"],
                track_name=race["track_name"],
                race_number=race["race_number"],
                race_date=race["race_date"],
                post_time=race.get("post_time"),
                distance=race.get("distance"),
                surface=race.get("surface"),
                condition=race.get("condition"),
                race_type=race.get("race_type"),
                purse=race.get("purse"),
                field_size=race["field_size"],
                horses=race["horses"]
            )
            for race in races
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get races: {str(e)}")


@router.get("/{race_id}", response_model=RaceResponse)
async def get_race_by_id(race_id: str):
    """Get specific race by ID."""
    try:
        data_provider = get_data_provider()
        race = await data_provider.get_race_by_id(race_id)
        
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")
        
        return RaceResponse(
            race_id=race["race_id"],
            track_name=race["track_name"],
            race_number=race["race_number"],
            race_date=race["race_date"],
            post_time=race.get("post_time"),
            distance=race.get("distance"),
            surface=race.get("surface"),
            condition=race.get("condition"),
            race_type=race.get("race_type"),
            purse=race.get("purse"),
            field_size=race["field_size"],
            horses=race["horses"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get race: {str(e)}")


@router.get("/{race_id}/results")
async def get_race_results(race_id: str):
    """Get race results by race ID."""
    try:
        data_provider = get_data_provider()
        results = await data_provider.get_race_results(race_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Race results not found")
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get race results: {str(e)}")


@router.get("/track/{track_code}")
async def get_track_races(track_code: str):
    """Get all races for a specific track."""
    try:
        data_provider = get_data_provider()
        
        # Get track info first
        track_info = await data_provider.get_track_info(track_code.upper())
        if not track_info:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # For now, we'll return today's races for this track
        # In a real implementation, you'd filter races by track
        races = await data_provider.get_todays_races()
        track_races = [race for race in races if race.get("track_code") == track_code.upper()]
        
        return {
            "track_info": track_info,
            "races": track_races
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track races: {str(e)}")


@router.get("/search/horses")
async def search_horses(q: str = Query(..., description="Search query for horse names")):
    """Search horses by name."""
    try:
        data_provider = get_data_provider()
        horses = await data_provider.search_horses(q)
        
        return {
            "query": q,
            "count": len(horses),
            "horses": horses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search horses: {str(e)}")


@router.get("/data/summary")
async def get_data_summary():
    """Get summary of available data."""
    try:
        data_provider = get_data_provider()
        
        # Get data source info
        source_info = data_provider.get_data_source_info()
        
        # Get health check (includes test data summary)
        health = await data_provider.health_check()
        
        return {
            "data_source": source_info,
            "health": health,
            "endpoints": {
                "today_races": "/api/races/today",
                "races_by_date": "/api/races/date/{YYYY-MM-DD}",
                "race_by_id": "/api/races/{race_id}",
                "race_results": "/api/races/{race_id}/results",
                "track_races": "/api/races/track/{track_code}",
                "search_horses": "/api/races/search/horses?q={query}",
                "data_summary": "/api/races/data/summary"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data summary: {str(e)}")
