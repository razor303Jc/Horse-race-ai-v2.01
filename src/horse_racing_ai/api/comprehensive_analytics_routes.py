"""
Comprehensive Analytics API Integration
=====================================

REST API endpoints for the comprehensive analytics system with win rates,
accuracy metrics, ROI tracking, weight optimization, and detailed reporting.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from ..analytics.comprehensive_analytics_engine import (
    comprehensive_analytics,
    PerformanceMetrics,
    ModelWeightOptimization,
    ValidationResults,
    ComprehensiveReport,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["comprehensive-analytics"])


class AnalyticsRequest(BaseModel):
    """Request model for analytics generation."""

    start_date: datetime
    end_date: datetime
    include_validation: bool = True
    include_optimization: bool = True
    segments: List[str] = ["track", "distance", "race_type", "month"]


class QuickMetricsRequest(BaseModel):
    """Request model for quick metrics."""

    period_days: int = 30
    metric_types: List[str] = ["accuracy", "roi", "risk"]


@router.get("/health")
async def health_check():
    """Health check for comprehensive analytics service."""
    return {
        "status": "healthy",
        "service": "Comprehensive Analytics Engine",
        "version": "2.03",
        "capabilities": [
            "performance_metrics",
            "roi_tracking",
            "accuracy_analysis",
            "weight_optimization",
            "real_world_validation",
            "detailed_reporting",
        ],
    }


@router.post("/generate-comprehensive-report")
async def generate_comprehensive_report(
    request: AnalyticsRequest, background_tasks: BackgroundTasks
):
    """
    Generate a comprehensive analytics report with all metrics.

    **Features:**
    - Complete performance metrics (accuracy, precision, recall, F1)
    - Financial analysis (ROI, Sharpe ratio, max drawdown)
    - Risk assessment (volatility, VaR, Sortino ratio)
    - Segmented analysis (by track, distance, race type, month)
    - ML weight optimization recommendations
    - Real-world validation against historical results
    - Professional visualizations and exports
    """
    try:
        # Generate comprehensive report
        report = comprehensive_analytics.generate_comprehensive_report(
            start_date=request.start_date,
            end_date=request.end_date,
            include_validation=request.include_validation,
            include_optimization=request.include_optimization,
        )

        # Convert to response format
        return {
            "status": "success",
            "report_id": report.report_id,
            "generated_at": report.generated_at.isoformat(),
            "period_analyzed": report.period_analyzed,
            "summary": {
                "overall_accuracy": report.performance_metrics.overall_accuracy,
                "roi_percentage": report.performance_metrics.roi_percentage,
                "hit_rate": report.performance_metrics.hit_rate,
                "total_predictions": report.performance_metrics.total_predictions,
                "profit_loss": report.performance_metrics.profit_loss,
                "sharpe_ratio": report.performance_metrics.sharpe_ratio,
                "max_drawdown": report.performance_metrics.max_drawdown,
            },
            "segments_analyzed": {
                "tracks": len(report.performance_by_track),
                "distances": len(report.performance_by_distance),
                "race_types": len(report.performance_by_race_type),
                "months": len(report.performance_by_month),
            },
            "optimization_recommendations": len(report.weight_optimization),
            "validation_included": report.validation_results is not None,
            "charts_generated": report.charts_generated,
            "export_paths": report.export_paths,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate comprehensive report: {str(e)}"
        )


@router.get("/quick-metrics")
async def get_quick_metrics(
    period_days: int = Query(30, ge=1, le=365), include_segments: bool = Query(False)
):
    """
    Get quick performance metrics for dashboard display.

    **Returns:**
    - Key accuracy metrics
    - Financial performance indicators
    - Risk assessment summary
    - Optional segmented breakdown
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        # Calculate core metrics
        performance_metrics = comprehensive_analytics._calculate_performance_metrics(
            start_date, end_date
        )

        quick_metrics = {
            "period": (
                f"{start_date.strftime('%Y-%m-%d')} to "
                f"{end_date.strftime('%Y-%m-%d')}"
            ),
            "accuracy_metrics": {
                "overall_accuracy": round(
                    performance_metrics.overall_accuracy * 100, 1
                ),
                "win_prediction_accuracy": round(
                    performance_metrics.win_prediction_accuracy * 100, 1
                ),
                "place_prediction_accuracy": round(
                    performance_metrics.place_prediction_accuracy * 100, 1
                ),
                "f1_score": round(performance_metrics.f1_score, 3),
                "auc_roc": round(performance_metrics.auc_roc, 3),
            },
            "financial_metrics": {
                "total_bets": performance_metrics.total_bets,
                "hit_rate": round(performance_metrics.hit_rate * 100, 1),
                "roi_percentage": round(performance_metrics.roi_percentage, 1),
                "profit_loss": round(performance_metrics.profit_loss, 2),
                "total_staked": round(performance_metrics.total_staked, 2),
                "sharpe_ratio": round(performance_metrics.sharpe_ratio, 2),
            },
            "risk_metrics": {
                "volatility": round(performance_metrics.volatility, 3),
                "max_drawdown": round(performance_metrics.max_drawdown * 100, 1),
                "value_at_risk": round(performance_metrics.value_at_risk * 100, 1),
                "sortino_ratio": round(performance_metrics.sortino_ratio, 2),
            },
            "prediction_quality": {
                "total_predictions": performance_metrics.total_predictions,
                "correct_predictions": performance_metrics.correct_predictions,
                "mean_absolute_error": round(
                    performance_metrics.mean_absolute_error, 2
                ),
                "confidence_correlation": round(
                    performance_metrics.confidence_correlation, 3
                ),
            },
        }

        # Add segmented data if requested
        if include_segments:
            performance_by_track = (
                comprehensive_analytics._analyze_performance_by_track(
                    start_date, end_date
                )
            )

            quick_metrics["segments"] = {
                "by_track": {
                    track: {
                        "accuracy": round(metrics.overall_accuracy * 100, 1),
                        "roi": round(metrics.roi_percentage, 1),
                        "predictions": metrics.total_predictions,
                    }
                    for track, metrics in performance_by_track.items()
                }
            }

        return {
            "status": "success",
            "data": quick_metrics,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quick metrics: {str(e)}"
        )


@router.get("/weight-optimization-recommendations")
async def get_weight_optimization_recommendations(
    period_days: int = Query(90, ge=30, le=365)
):
    """
    Get ML model weight optimization recommendations.

    **Features:**
    - Current vs recommended model weights
    - Expected performance improvement
    - Feature importance analysis
    - Risk assessment for weight changes
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        recommendations = (
            comprehensive_analytics._generate_weight_optimization_recommendations(
                start_date, end_date
            )
        )

        return {
            "status": "success",
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "recommendations": [
                {
                    "model_name": rec.model_name,
                    "current_weights": rec.current_weights,
                    "recommended_weights": rec.recommended_weights,
                    "improvement_potential": f"{rec.improvement_potential * 100:.1f}%",
                    "confidence_score": f"{rec.confidence_score * 100:.1f}%",
                    "validation_period": rec.validation_period,
                    "feature_importance": rec.feature_importance,
                    "risk_assessment": rec.risk_assessment,
                }
                for rec in recommendations
            ],
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate weight optimization recommendations: {str(e)}",
        )


@router.get("/validation-results")
async def get_validation_results(period_days: int = Query(90, ge=30, le=365)):
    """
    Get real-world validation results against historical race data.

    **Features:**
    - Historical vs forward-testing accuracy
    - Consistency analysis across time periods
    - Market efficiency assessment
    - Bias detection and analysis
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        validation = comprehensive_analytics._perform_real_world_validation(
            start_date, end_date
        )

        return {
            "status": "success",
            "validation_results": {
                "validation_period": validation.validation_period,
                "races_analyzed": validation.races_analyzed,
                "historical_accuracy": f"{validation.historical_accuracy * 100:.1f}%",
                "forward_testing_accuracy": f"{validation.forward_testing_accuracy * 100:.1f}%",
                "consistency_score": f"{validation.consistency_score * 100:.1f}%",
                "market_efficiency_score": f"{validation.market_efficiency_score * 100:.1f}%",
                "bias_analysis": {
                    bias_type: f"{value * 100:+.1f}%"
                    for bias_type, value in validation.bias_analysis.items()
                },
                "recommendation": validation.recommendation,
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate validation results: {str(e)}"
        )


@router.get("/performance-attribution")
async def get_performance_attribution(
    period_days: int = Query(90, ge=30, le=365),
    attribution_type: str = Query(
        "all", regex="^(track|distance|race_type|month|all)$"
    ),
):
    """
    Get detailed performance attribution analysis.

    **Features:**
    - Performance breakdown by track, distance, race type, month
    - Comparative analysis across segments
    - Statistical significance testing
    - Best/worst performing categories
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        attribution_data = {}

        if attribution_type in ["track", "all"]:
            performance_by_track = (
                comprehensive_analytics._analyze_performance_by_track(
                    start_date, end_date
                )
            )
            attribution_data["track"] = {
                track: {
                    "accuracy": f"{metrics.overall_accuracy * 100:.1f}%",
                    "roi": f"{metrics.roi_percentage:.1f}%",
                    "hit_rate": f"{metrics.hit_rate * 100:.1f}%",
                    "predictions": metrics.total_predictions,
                    "profit_loss": round(metrics.profit_loss, 2),
                }
                for track, metrics in performance_by_track.items()
            }

        if attribution_type in ["distance", "all"]:
            performance_by_distance = (
                comprehensive_analytics._analyze_performance_by_distance(
                    start_date, end_date
                )
            )
            attribution_data["distance"] = {
                distance: {
                    "accuracy": f"{metrics.overall_accuracy * 100:.1f}%",
                    "roi": f"{metrics.roi_percentage:.1f}%",
                    "hit_rate": f"{metrics.hit_rate * 100:.1f}%",
                    "predictions": metrics.total_predictions,
                    "profit_loss": round(metrics.profit_loss, 2),
                }
                for distance, metrics in performance_by_distance.items()
            }

        if attribution_type in ["race_type", "all"]:
            performance_by_race_type = (
                comprehensive_analytics._analyze_performance_by_race_type(
                    start_date, end_date
                )
            )
            attribution_data["race_type"] = {
                race_type: {
                    "accuracy": f"{metrics.overall_accuracy * 100:.1f}%",
                    "roi": f"{metrics.roi_percentage:.1f}%",
                    "hit_rate": f"{metrics.hit_rate * 100:.1f}%",
                    "predictions": metrics.total_predictions,
                    "profit_loss": round(metrics.profit_loss, 2),
                }
                for race_type, metrics in performance_by_race_type.items()
            }

        if attribution_type in ["month", "all"]:
            performance_by_month = (
                comprehensive_analytics._analyze_performance_by_month(
                    start_date, end_date
                )
            )
            attribution_data["month"] = {
                month: {
                    "accuracy": f"{metrics.overall_accuracy * 100:.1f}%",
                    "roi": f"{metrics.roi_percentage:.1f}%",
                    "hit_rate": f"{metrics.hit_rate * 100:.1f}%",
                    "predictions": metrics.total_predictions,
                    "profit_loss": round(metrics.profit_loss, 2),
                }
                for month, metrics in performance_by_month.items()
            }

        return {
            "status": "success",
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "attribution_type": attribution_type,
            "performance_attribution": attribution_data,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate performance attribution: {str(e)}",
        )


@router.get("/feature-importance")
async def get_feature_importance(period_days: int = Query(90, ge=30, le=365)):
    """
    Get feature importance analysis for ML models.

    **Features:**
    - Feature attribution scores
    - Impact on prediction accuracy
    - Recommended feature weights
    - Feature interaction analysis
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        feature_attribution = comprehensive_analytics._calculate_feature_attribution(
            start_date, end_date
        )

        # Sort features by importance
        sorted_features = sorted(
            feature_attribution.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "status": "success",
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "feature_importance": {
                "ranked_features": [
                    {
                        "feature": feature,
                        "importance_score": round(score, 3),
                        "importance_percentage": f"{score * 100:.1f}%",
                        "rank": idx + 1,
                    }
                    for idx, (feature, score) in enumerate(sorted_features)
                ],
                "top_3_features": sorted_features[:3],
                "total_features_analyzed": len(feature_attribution),
            },
            "recommendations": {
                "focus_areas": [feature for feature, _ in sorted_features[:3]],
                "optimization_potential": (
                    "High" if sorted_features[0][1] > 0.25 else "Medium"
                ),
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate feature importance analysis: {str(e)}",
        )


@router.get("/confidence-analysis")
async def get_confidence_analysis(period_days: int = Query(90, ge=30, le=365)):
    """
    Get prediction confidence analysis and calibration assessment.

    **Features:**
    - Confidence-accuracy correlation
    - High vs low confidence performance
    - Confidence distribution analysis
    - Model calibration scoring
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        confidence_analysis = comprehensive_analytics._analyze_prediction_confidence(
            start_date, end_date
        )

        return {
            "status": "success",
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "confidence_analysis": {
                "confidence_accuracy_correlation": round(
                    confidence_analysis["confidence_accuracy_correlation"], 3
                ),
                "high_confidence_accuracy": f"{confidence_analysis['high_confidence_accuracy'] * 100:.1f}%",
                "low_confidence_accuracy": f"{confidence_analysis['low_confidence_accuracy'] * 100:.1f}%",
                "calibration_score": f"{confidence_analysis['calibration_score'] * 100:.1f}%",
                "confidence_distribution": confidence_analysis[
                    "confidence_distribution"
                ],
            },
            "insights": {
                "correlation_strength": (
                    "Strong"
                    if confidence_analysis["confidence_accuracy_correlation"] > 0.7
                    else (
                        "Moderate"
                        if confidence_analysis["confidence_accuracy_correlation"] > 0.4
                        else "Weak"
                    )
                ),
                "calibration_quality": (
                    "Excellent"
                    if confidence_analysis["calibration_score"] > 0.8
                    else (
                        "Good"
                        if confidence_analysis["calibration_score"] > 0.6
                        else "Needs Improvement"
                    )
                ),
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate confidence analysis: {str(e)}"
        )


@router.get("/roi-analysis")
async def get_roi_analysis(
    period_days: int = Query(90, ge=30, le=365),
    include_risk_metrics: bool = Query(True),
):
    """
    Get detailed ROI analysis with risk-adjusted returns.

    **Features:**
    - ROI calculation and trends
    - Risk-adjusted performance (Sharpe, Sortino ratios)
    - Maximum drawdown analysis
    - Value at Risk assessment
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        performance_metrics = comprehensive_analytics._calculate_performance_metrics(
            start_date, end_date
        )

        roi_analysis = {
            "roi_metrics": {
                "roi_percentage": round(performance_metrics.roi_percentage, 2),
                "profit_loss": round(performance_metrics.profit_loss, 2),
                "total_staked": round(performance_metrics.total_staked, 2),
                "total_returns": round(performance_metrics.total_returns, 2),
                "hit_rate": f"{performance_metrics.hit_rate * 100:.1f}%",
                "average_bet_size": round(
                    (
                        performance_metrics.total_staked
                        / performance_metrics.total_bets
                        if performance_metrics.total_bets > 0
                        else 0
                    ),
                    2,
                ),
            }
        }

        if include_risk_metrics:
            roi_analysis["risk_adjusted_metrics"] = {
                "sharpe_ratio": round(performance_metrics.sharpe_ratio, 3),
                "sortino_ratio": round(performance_metrics.sortino_ratio, 3),
                "volatility": round(performance_metrics.volatility, 3),
                "max_drawdown": f"{performance_metrics.max_drawdown * 100:.1f}%",
                "value_at_risk_95": f"{performance_metrics.value_at_risk * 100:.1f}%",
            }

            roi_analysis["risk_assessment"] = {
                "risk_level": (
                    "High"
                    if performance_metrics.volatility > 0.3
                    else "Medium" if performance_metrics.volatility > 0.15 else "Low"
                ),
                "drawdown_severity": (
                    "Severe"
                    if abs(performance_metrics.max_drawdown) > 0.2
                    else (
                        "Moderate"
                        if abs(performance_metrics.max_drawdown) > 0.1
                        else "Mild"
                    )
                ),
                "overall_rating": (
                    "Excellent"
                    if performance_metrics.sharpe_ratio > 2.0
                    else (
                        "Good"
                        if performance_metrics.sharpe_ratio > 1.0
                        else (
                            "Fair" if performance_metrics.sharpe_ratio > 0.5 else "Poor"
                        )
                    )
                ),
            }

        return {
            "status": "success",
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "roi_analysis": roi_analysis,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate ROI analysis: {str(e)}"
        )


@router.get("/available-reports")
async def get_available_reports():
    """Get list of available comprehensive reports."""
    try:
        metadata_dir = comprehensive_analytics.output_dir / "metadata"

        if not metadata_dir.exists():
            return {"status": "success", "available_reports": [], "total_reports": 0}

        reports = []
        for metadata_file in metadata_dir.glob("*_metadata.json"):
            try:
                import json

                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                reports.append(metadata)
            except Exception:
                continue

        # Sort by generation date (newest first)
        reports.sort(key=lambda x: x["generated_at"], reverse=True)

        return {
            "status": "success",
            "available_reports": reports,
            "total_reports": len(reports),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve available reports: {str(e)}"
        )
