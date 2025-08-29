"""
Enhanced Monte Carlo API Integration
===================================

FastAPI endpoints for the enhanced Monte Carlo simulation system.
Provides REST API access to both basic and advanced simulation modes.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio

from ..simulation.monte_carlo_integration import monte_carlo_integration

router = APIRouter(prefix="/api/v1/monte-carlo", tags=["monte-carlo"])


class HorseData(BaseModel):
    """Horse data for simulation."""

    name: str
    jockey: Optional[str] = None
    trainer: Optional[str] = None
    weight_carried: float = 60.0
    odds: Optional[float] = None
    speed_rating: float = 75.0
    form_rating: float = 75.0
    jockey_skill: float = 75.0
    trainer_skill: float = 75.0
    recent_form: List[int] = []
    win_probability: Optional[float] = None


class SimulationRequest(BaseModel):
    """Monte Carlo simulation request."""

    horses: List[HorseData]
    mode: str = "basic"  # "basic" or "advanced"
    custom_params: Optional[Dict[str, Any]] = None


class ScenarioRequest(BaseModel):
    """Scenario comparison request."""

    horses: List[HorseData]
    scenarios: List[Dict[str, Any]]


@router.get("/modes")
async def get_simulation_modes():
    """Get available simulation modes and their capabilities."""
    return {
        "status": "success",
        "modes": monte_carlo_integration.get_simulation_modes(),
    }


@router.post("/simulate")
async def run_monte_carlo_simulation(request: SimulationRequest):
    """
    Run Monte Carlo simulation with specified mode and parameters.

    **Basic Mode:**
    - Fast execution (< 1 second)
    - Core probability analysis
    - 1,000-5,000 simulations

    **Advanced Mode:**
    - Professional-grade modeling (2-10 seconds)
    - Environmental factors (track, weather)
    - Value betting recommendations
    - 10,000-50,000 simulations
    """
    try:
        # Convert Pydantic models to dictionaries
        horses_data = [horse.dict() for horse in request.horses]

        # Run simulation
        results = await monte_carlo_integration.run_simulation(
            horses=horses_data, mode=request.mode, custom_params=request.custom_params
        )

        return {"status": "success", "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/compare-scenarios")
async def compare_scenarios(request: ScenarioRequest):
    """
    Run comparative analysis across multiple scenarios.

    Useful for analyzing how different conditions affect race outcomes:
    - Track conditions (good, soft, heavy)
    - Weather factors
    - Distance variations
    - Field size impacts
    """
    try:
        horses_data = [horse.dict() for horse in request.horses]

        results = await monte_carlo_integration.run_comparative_analysis(
            horses=horses_data, scenarios=request.scenarios
        )

        return {"status": "success", "data": results}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Scenario comparison failed: {str(e)}"
        )


@router.get("/quick-analysis")
async def quick_race_analysis(
    num_horses: int = Query(6, ge=2, le=20),
    mode: str = Query("basic", regex="^(basic|advanced)$"),
    track_condition: str = Query("good", regex="^(firm|good|soft|heavy)$"),
):
    """
    Quick race analysis with generated sample data.
    Useful for testing and demonstration purposes.
    """
    try:
        # Generate sample horses
        sample_horses = []
        for i in range(num_horses):
            horse = {
                "name": f"Horse_{i+1}",
                "weight_carried": 58.0 + (i * 0.5),
                "odds": 3.0 + (i * 1.5),
                "speed_rating": 85 - (i * 2),
                "form_rating": 80 - (i * 1.5),
                "jockey_skill": 85 - (i * 1),
                "trainer_skill": 80 - (i * 1),
                "recent_form": [(i % 5) + 1, ((i + 1) % 5) + 1, ((i + 2) % 5) + 1],
            }
            sample_horses.append(horse)

        # Set custom parameters for track condition
        custom_params = {
            "track_condition": track_condition,
            "num_runs": 5000 if mode == "basic" else 15000,
        }

        results = await monte_carlo_integration.run_simulation(
            horses=sample_horses, mode=mode, custom_params=custom_params
        )

        return {
            "status": "success",
            "data": results,
            "meta": {
                "generated_horses": num_horses,
                "mode": mode,
                "track_condition": track_condition,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for Monte Carlo service."""
    return {
        "status": "healthy",
        "service": "Enhanced Monte Carlo Simulation",
        "version": "2.03",
        "capabilities": [
            "basic_simulation",
            "advanced_simulation",
            "scenario_comparison",
        ],
    }
