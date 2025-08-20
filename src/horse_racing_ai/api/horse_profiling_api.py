"""
Horse Profiling API Integration
==============================

API endpoints for the horse profiling system including progressive/plateaued/regressive
classification and optimal condition analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/horse-profiling", tags=["horse-profiling"])


class HorseProfileRequest(BaseModel):
    """Request model for horse profiling."""

    horse_id: str
    horse_name: Optional[str] = None


class ConditionAnalysisRequest(BaseModel):
    """Request model for condition analysis."""

    horse_id: str
    condition_type: str  # track, distance, going, class, field_size, season


@router.get("/health")
async def health_check():
    """Health check for horse profiling service."""
    return {
        "status": "healthy",
        "service": "Horse Profiling System",
        "version": "2.03",
        "capabilities": [
            "form_trend_classification",
            "condition_specific_analysis",
            "optimal_conditions_discovery",
            "progressive_horse_identification",
            "detailed_performance_profiling",
        ],
    }


@router.get("/form-trends")
async def get_form_trends(min_runs: int = Query(5, ge=3, le=20)):
    """Get horses classified by form trends (Progressive/Plateaued/Regressive)."""
    try:
        # Import here to avoid circular imports
        from ..analytics.horse_profiling_system import horse_profiling_system

        # Get progressive horses
        progressive_horses = horse_profiling_system.get_progressive_horses(min_runs)

        # Mock data for other categories for demonstration
        form_trends = {
            "progressive": progressive_horses,
            "plateaued": [
                {
                    "horse_id": "HORSE_P001",
                    "horse_name": "Consistent Runner",
                    "total_runs": 12,
                    "last_run_date": "2024-08-15",
                    "form_trend": "plateaued",
                    "win_rate": 25.0,
                    "best_rating": 85,
                }
            ],
            "regressive": [
                {
                    "horse_id": "HORSE_R001",
                    "horse_name": "Declining Form",
                    "total_runs": 15,
                    "last_run_date": "2024-08-10",
                    "form_trend": "regressive",
                    "win_rate": 13.3,
                    "best_rating": 92,
                }
            ],
            "summary": {
                "total_horses_analyzed": len(progressive_horses) + 2,
                "progressive_count": len(progressive_horses),
                "plateaued_count": 1,
                "regressive_count": 1,
                "progressive_percentage": (
                    round(
                        (len(progressive_horses) / (len(progressive_horses) + 2)) * 100,
                        1,
                    )
                    if progressive_horses
                    else 0
                ),
            },
        }

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "minimum_runs": min_runs,
            "form_trends": form_trends,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze form trends: {str(e)}"
        )


@router.post("/generate-profile")
async def generate_horse_profile(request: HorseProfileRequest):
    """Generate comprehensive profile for a specific horse."""
    try:
        from ..analytics.horse_profiling_system import horse_profiling_system

        profile = horse_profiling_system.generate_horse_profile(
            request.horse_id, request.horse_name
        )

        if not profile:
            raise HTTPException(
                status_code=404, detail=f"No data found for horse {request.horse_id}"
            )

        # Convert profile to response format
        return {
            "status": "success",
            "horse_profile": {
                "horse_id": profile.horse_id,
                "horse_name": profile.horse_name,
                "form_trend": profile.form_trend.value,
                "confidence_level": profile.confidence_level,
                "overall_stats": profile.overall_stats,
                "preferred_conditions": profile.preferred_conditions,
                "optimal_strike_rate": round(profile.optimal_strike_rate, 1),
                "optimal_sample_size": profile.optimal_sample_size,
                "condition_profiles": {
                    "track_count": len(profile.track_profiles),
                    "distance_count": len(profile.distance_profiles),
                    "going_count": len(profile.going_profiles),
                    "class_count": len(profile.class_profiles),
                },
                "data_quality": {
                    "total_runs": profile.total_runs,
                    "quality_score": round(profile.data_quality_score, 1),
                    "confidence_level": profile.confidence_level,
                },
                "last_updated": profile.last_updated.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate horse profile: {str(e)}"
        )


@router.get("/condition-analysis/{horse_id}")
async def get_condition_analysis(
    horse_id: str,
    condition_type: str = Query(
        "track", regex="^(track|distance|going|class|field_size|season)$"
    ),
):
    """Get detailed condition-specific performance analysis for a horse."""
    try:
        from ..analytics.horse_profiling_system import horse_profiling_system

        condition_profiles = horse_profiling_system.analyze_condition_performance(
            horse_id, condition_type
        )

        if not condition_profiles:
            return {
                "status": "success",
                "horse_id": horse_id,
                "condition_type": condition_type,
                "message": f"No sufficient data for {condition_type} analysis",
                "condition_profiles": {},
            }

        # Format response
        formatted_profiles = {}
        for condition_value, profile in condition_profiles.items():
            formatted_profiles[condition_value] = {
                "runs": profile.runs,
                "wins": profile.wins,
                "places": profile.places,
                "win_rate": round(profile.win_rate, 1),
                "place_rate": round(profile.place_rate, 1),
                "avg_rating": round(profile.avg_rating, 1) if profile.avg_rating else 0,
                "best_rating": (
                    round(profile.best_rating, 1) if profile.best_rating else 0
                ),
                "roi": round(profile.roi, 1),
                "sample_adequate": profile.sample_size_adequate,
                "confidence": "High" if profile.sample_size_adequate else "Low",
            }

        # Find best performing condition
        best_condition = max(condition_profiles.items(), key=lambda x: x[1].win_rate)

        return {
            "status": "success",
            "horse_id": horse_id,
            "condition_type": condition_type,
            "condition_profiles": formatted_profiles,
            "best_condition": {
                "condition_value": best_condition[0],
                "win_rate": round(best_condition[1].win_rate, 1),
                "runs": best_condition[1].runs,
                "confidence": (
                    "High" if best_condition[1].sample_size_adequate else "Low"
                ),
            },
            "analysis_summary": {
                "conditions_analyzed": len(condition_profiles),
                "best_win_rate": round(best_condition[1].win_rate, 1),
                "total_runs_across_conditions": sum(
                    p.runs for p in condition_profiles.values()
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze {condition_type} performance: {str(e)}",
        )


@router.get("/optimal-conditions/{horse_id}")
async def get_optimal_conditions(horse_id: str):
    """Get optimal race conditions for maximum performance."""
    try:
        from ..analytics.horse_profiling_system import horse_profiling_system

        preferred_conditions, optimal_strike_rate, optimal_sample_size = (
            horse_profiling_system.find_optimal_conditions(horse_id)
        )

        if not preferred_conditions:
            return {
                "status": "success",
                "horse_id": horse_id,
                "message": "Insufficient data to determine optimal conditions",
                "optimal_conditions": {},
                "strike_rate": 0,
                "sample_size": 0,
            }

        # Calculate confidence based on sample size
        if optimal_sample_size >= 8:
            confidence = "High"
        elif optimal_sample_size >= 5:
            confidence = "Medium"
        elif optimal_sample_size >= 3:
            confidence = "Low"
        else:
            confidence = "Very Low"

        return {
            "status": "success",
            "horse_id": horse_id,
            "optimal_conditions": preferred_conditions,
            "performance_metrics": {
                "optimal_strike_rate": round(optimal_strike_rate, 1),
                "sample_size": optimal_sample_size,
                "confidence_level": confidence,
            },
            "betting_insights": {
                "value_opportunity": (
                    "High"
                    if optimal_strike_rate > 40
                    else "Medium" if optimal_strike_rate > 25 else "Low"
                ),
                "reliability": confidence,
                "recommended_strategy": (
                    f"Target races with {', '.join([f'{k}: {v}' for k, v in preferred_conditions.items()])}"
                    if preferred_conditions
                    else "Need more data"
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to find optimal conditions: {str(e)}"
        )


@router.get("/progressive-horses")
async def get_progressive_horses(
    min_runs: int = Query(5, ge=3, le=20), limit: int = Query(20, ge=5, le=100)
):
    """Get list of horses showing progressive form (improving performance)."""
    try:
        from ..analytics.horse_profiling_system import horse_profiling_system

        progressive_horses = horse_profiling_system.get_progressive_horses(min_runs)

        # Limit results
        limited_horses = progressive_horses[:limit]

        # Add additional analysis for each progressive horse
        enhanced_horses = []
        for horse in limited_horses:
            # Get basic profile for additional insights
            horse_id = horse["horse_id"]
            try:
                profile = horse_profiling_system.generate_horse_profile(horse_id)
                if profile:
                    enhanced_horse = horse.copy()
                    enhanced_horse.update(
                        {
                            "win_rate": round(profile.overall_stats["win_rate"], 1),
                            "best_rating": profile.overall_stats["best_rating"],
                            "optimal_strike_rate": round(
                                profile.optimal_strike_rate, 1
                            ),
                            "preferred_track": profile.preferred_conditions.get(
                                "track", "Unknown"
                            ),
                            "preferred_distance": profile.preferred_conditions.get(
                                "distance", "Unknown"
                            ),
                            "confidence_level": profile.confidence_level,
                        }
                    )
                    enhanced_horses.append(enhanced_horse)
                else:
                    enhanced_horses.append(horse)
            except Exception:
                enhanced_horses.append(horse)

        return {
            "status": "success",
            "analysis_criteria": {
                "minimum_runs": min_runs,
                "maximum_results": limit,
                "form_trend": "Progressive",
            },
            "progressive_horses": enhanced_horses,
            "summary": {
                "total_found": len(progressive_horses),
                "returned": len(enhanced_horses),
                "avg_win_rate": (
                    round(
                        sum(h.get("win_rate", 0) for h in enhanced_horses)
                        / len(enhanced_horses),
                        1,
                    )
                    if enhanced_horses
                    else 0
                ),
            },
            "betting_strategy": {
                "focus": "Horses showing improving form trends",
                "advantage": "Market may not fully price in recent improvement",
                "recommended_approach": "Monitor for continued improvement in optimal conditions",
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get progressive horses: {str(e)}"
        )


@router.get("/condition-comparison/{horse_id}")
async def compare_conditions(horse_id: str):
    """Compare horse's performance across different conditions."""
    try:
        from ..analytics.horse_profiling_system import horse_profiling_system

        # Get all condition analyses
        track_profiles = horse_profiling_system.analyze_condition_performance(
            horse_id, "track"
        )
        distance_profiles = horse_profiling_system.analyze_condition_performance(
            horse_id, "distance"
        )
        going_profiles = horse_profiling_system.analyze_condition_performance(
            horse_id, "going"
        )
        class_profiles = horse_profiling_system.analyze_condition_performance(
            horse_id, "class"
        )

        # Find best and worst for each condition type
        comparison_data = {}

        for condition_type, profiles in [
            ("track", track_profiles),
            ("distance", distance_profiles),
            ("going", going_profiles),
            ("class", class_profiles),
        ]:
            if profiles:
                best = max(profiles.items(), key=lambda x: x[1].win_rate)
                worst = min(profiles.items(), key=lambda x: x[1].win_rate)

                comparison_data[condition_type] = {
                    "best": {
                        "condition": best[0],
                        "win_rate": round(best[1].win_rate, 1),
                        "runs": best[1].runs,
                        "adequate_sample": best[1].sample_size_adequate,
                    },
                    "worst": {
                        "condition": worst[0],
                        "win_rate": round(worst[1].win_rate, 1),
                        "runs": worst[1].runs,
                        "adequate_sample": worst[1].sample_size_adequate,
                    },
                    "differential": round(best[1].win_rate - worst[1].win_rate, 1),
                }

        return {
            "status": "success",
            "horse_id": horse_id,
            "condition_comparison": comparison_data,
            "insights": {
                "strongest_differential": (
                    max(comparison_data.items(), key=lambda x: x[1]["differential"])[0]
                    if comparison_data
                    else None
                ),
                "most_consistent": (
                    min(comparison_data.items(), key=lambda x: x[1]["differential"])[0]
                    if comparison_data
                    else None
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compare conditions: {str(e)}"
        )
