#!/usr/bin/env python3
"""
Web GUI Integration for Race Trends Analysis
Adds race trends endpoints to the existing web interface.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import jsonify, request

# Add src to path for imports
sys.path.append("/home/jc/Documents/Horse-race-handicaping-ai/Horse-race-ai-v2.0/src")

from horse_racing_ai.analysis.race_trends_analyzer import (
    HorseTrendScore,
    RaceAnalysisTrends,
    RaceTrendsAnalyzer,
)


class RaceTrendsWebIntegration:
    """Web integration for race trends analysis."""

    def __init__(self, flask_app):
        """Initialize with Flask app."""
        self.app = flask_app
        self.trends_analyzer = RaceTrendsAnalyzer()
        self._register_routes()

    def _register_routes(self):
        """Register race trends API routes."""

        @self.app.route("/api/race-trends/analyze", methods=["POST"])
        def analyze_race_trends():
            """Analyze race trends for a specific race."""
            try:
                data = request.get_json()
                race_data = data.get("race_data", {})
                historical_races = data.get("historical_races", [])

                if not race_data:
                    return jsonify({"error": "Missing race data"}), 400

                # Analyze trends
                trends = self.trends_analyzer.analyze_race_trends(
                    race_data, historical_races
                )

                # Export for web display
                trends_export = self.trends_analyzer.export_trends_analysis(trends)

                return jsonify(
                    {
                        "success": True,
                        "trends_analysis": trends_export,
                        "summary": {
                            "overall_edge_score": trends.overall_edge_score,
                            "total_patterns": trends.total_patterns_found,
                            "confidence_level": self._get_confidence_level(trends),
                            "recommendation": self._get_race_recommendation(trends),
                        },
                    }
                )

            except Exception as e:
                return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

        @self.app.route("/api/race-trends/score-horse", methods=["POST"])
        def score_horse_trends():
            """Score individual horse against race trends."""
            try:
                data = request.get_json()
                horse_data = data.get("horse_data", {})
                race_trends_data = data.get("race_trends", {})

                if not horse_data or not race_trends_data:
                    return jsonify({"error": "Missing horse or trends data"}), 400

                # Reconstruct race trends object
                race_trends = self._reconstruct_race_trends(race_trends_data)

                # Score horse
                horse_score = self.trends_analyzer.score_horse_trends(
                    horse_data, race_trends
                )

                return jsonify(
                    {
                        "success": True,
                        "horse_name": horse_score.horse_name,
                        "trend_scores": horse_score.trend_scores,
                        "overall_score": horse_score.overall_trend_score,
                        "matching_patterns": horse_score.matching_patterns,
                        "edge_factors": horse_score.edge_factors,
                        "confidence": horse_score.confidence,
                        "recommendation": horse_score.recommendation,
                    }
                )

            except Exception as e:
                return jsonify({"error": f"Scoring failed: {str(e)}"}), 500

        @self.app.route("/api/race-trends/combined-analysis", methods=["POST"])
        def combined_trends_ai_analysis():
            """Combined AI + trends analysis for race."""
            try:
                data = request.get_json()
                race_data = data.get("race_data", {})
                historical_races = data.get("historical_races", [])
                ai_predictions = data.get("ai_predictions", {})

                # Analyze race trends
                race_trends = self.trends_analyzer.analyze_race_trends(
                    race_data, historical_races
                )

                # Analyze each horse with combined approach
                enhanced_horses = []
                for horse in race_data.get("horses", []):
                    horse_name = horse.get("name", "Unknown")

                    # Get trends score
                    trend_score = self.trends_analyzer.score_horse_trends(
                        horse, race_trends
                    )

                    # Get AI prediction if available
                    ai_score = ai_predictions.get(
                        horse_name, {"rating": 0.5, "confidence": 0.5}
                    )

                    # Calculate combined score
                    combined_score = self._calculate_combined_score(
                        ai_score, trend_score
                    )

                    enhanced_horses.append(
                        {
                            "horse_name": horse_name,
                            "ai_score": ai_score,
                            "trends_score": {
                                "overall_score": trend_score.overall_trend_score,
                                "category_scores": trend_score.trend_scores,
                                "matching_patterns": trend_score.matching_patterns,
                                "recommendation": trend_score.recommendation,
                            },
                            "combined_score": combined_score,
                            "betting_recommendation": self._get_betting_recommendation(
                                combined_score, trend_score
                            ),
                        }
                    )

                # Sort by combined score
                enhanced_horses.sort(
                    key=lambda x: x["combined_score"]["overall"], reverse=True
                )

                return jsonify(
                    {
                        "success": True,
                        "race_trends": self.trends_analyzer.export_trends_analysis(
                            race_trends
                        ),
                        "enhanced_horses": enhanced_horses,
                        "race_summary": {
                            "trends_edge": race_trends.overall_edge_score,
                            "patterns_found": race_trends.total_patterns_found,
                            "top_pick": (
                                enhanced_horses[0]["horse_name"]
                                if enhanced_horses
                                else None
                            ),
                            "confidence_level": self._get_confidence_level(race_trends),
                        },
                    }
                )

            except Exception as e:
                return jsonify({"error": f"Combined analysis failed: {str(e)}"}), 500

        @self.app.route("/api/race-trends/dashboard", methods=["GET"])
        def race_trends_dashboard():
            """Get race trends dashboard data."""
            try:
                # Return dashboard configuration and sample data
                return jsonify(
                    {
                        "success": True,
                        "dashboard_config": {
                            "trend_categories": [
                                "age_trends",
                                "weight_trends",
                                "draw_trends",
                                "form_trends",
                                "price_trends",
                                "course_form_trends",
                                "distance_form_trends",
                            ],
                            "confidence_thresholds": {
                                "high": 0.8,
                                "medium": 0.6,
                                "low": 0.4,
                            },
                            "edge_thresholds": {
                                "strong": 0.2,
                                "moderate": 0.1,
                                "weak": 0.05,
                            },
                        },
                        "sample_trends": self._get_sample_trends_data(),
                    }
                )

            except Exception as e:
                return jsonify({"error": f"Dashboard data failed: {str(e)}"}), 500

        @self.app.route("/api/race-trends/export", methods=["POST"])
        def export_trends_analysis():
            """Export trends analysis in various formats."""
            try:
                data = request.get_json()
                trends_data = data.get("trends_data", {})
                export_format = data.get("format", "json")

                if export_format == "json":
                    return jsonify(
                        {
                            "success": True,
                            "export_data": trends_data,
                            "exported_at": datetime.now().isoformat(),
                        }
                    )
                elif export_format == "csv":
                    # Convert to CSV format
                    csv_data = self._convert_trends_to_csv(trends_data)
                    return jsonify(
                        {
                            "success": True,
                            "csv_data": csv_data,
                            "exported_at": datetime.now().isoformat(),
                        }
                    )
                else:
                    return jsonify({"error": "Unsupported export format"}), 400

            except Exception as e:
                return jsonify({"error": f"Export failed: {str(e)}"}), 500

    def _get_confidence_level(self, trends: RaceAnalysisTrends) -> str:
        """Get confidence level description."""
        if trends.overall_edge_score >= 0.3:
            return "HIGH"
        elif trends.overall_edge_score >= 0.15:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_race_recommendation(self, trends: RaceAnalysisTrends) -> str:
        """Get race recommendation."""
        if trends.overall_edge_score >= 0.25 and trends.total_patterns_found >= 3:
            return "STRONG_BETTING_RACE"
        elif trends.overall_edge_score >= 0.15:
            return "MODERATE_BETTING_RACE"
        elif trends.total_patterns_found >= 2:
            return "SOME_PATTERNS_IDENTIFIED"
        else:
            return "LIMITED_EDGE_AVAILABLE"

    def _reconstruct_race_trends(
        self, trends_data: Dict[str, Any]
    ) -> RaceAnalysisTrends:
        """Reconstruct RaceAnalysisTrends from API data."""
        # This is a simplified reconstruction
        # In a real implementation, you'd properly deserialize the data
        race_info = trends_data.get("race_info", {})
        trends_summary = trends_data.get("trends_summary", {})

        return RaceAnalysisTrends(
            race_name=race_info.get("name", "Unknown"),
            race_type=race_info.get("type", "handicap"),
            distance=race_info.get("distance", "1m"),
            course=race_info.get("course", "Unknown"),
            surface=race_info.get("surface", "turf"),
            age_trends=[],
            weight_trends=[],
            draw_trends=[],
            form_trends=[],
            price_trends=[],
            seasonal_trends=[],
            course_form_trends=[],
            distance_form_trends=[],
            overall_edge_score=trends_summary.get("overall_edge_score", 0.0),
            total_patterns_found=trends_summary.get("total_patterns_found", 0),
            analysis_date=trends_summary.get(
                "analysis_date", datetime.now().isoformat()
            ),
        )

    def _calculate_combined_score(
        self, ai_score: Dict[str, float], trend_score: HorseTrendScore
    ) -> Dict[str, float]:
        """Calculate combined AI + trends score."""
        ai_weight = 0.6
        trends_weight = 0.4

        overall = (
            ai_score.get("rating", 0.5) * ai_weight
            + trend_score.overall_trend_score * trends_weight
        )

        confidence = (
            ai_score.get("confidence", 0.5) * ai_weight
            + trend_score.confidence * trends_weight
        )

        return {
            "overall": overall,
            "confidence": confidence,
            "ai_component": ai_score.get("rating", 0.5),
            "trends_component": trend_score.overall_trend_score,
            "edge_value": max(0, overall - 0.5) * 2,  # Normalize edge
        }

    def _get_betting_recommendation(
        self, combined_score: Dict[str, float], trend_score: HorseTrendScore
    ) -> str:
        """Get betting recommendation."""
        overall = combined_score["overall"]
        confidence = combined_score["confidence"]
        edge = combined_score["edge_value"]

        if overall >= 0.8 and confidence >= 0.7 and edge >= 0.3:
            return "STRONG_BET"
        elif overall >= 0.7 and confidence >= 0.6:
            return "MODERATE_BET"
        elif overall >= 0.6:
            return "WEAK_BET"
        elif trend_score.recommendation == "AVOID":
            return "AVOID"
        else:
            return "NO_BET"

    def _get_sample_trends_data(self) -> Dict[str, Any]:
        """Get sample trends data for dashboard."""
        return {
            "recent_analysis": [
                {
                    "race": "Chesterfield Cup",
                    "course": "Goodwood",
                    "edge_score": 0.35,
                    "patterns_found": 4,
                    "date": datetime.now().isoformat(),
                },
                {
                    "race": "Stewards Cup",
                    "course": "Goodwood",
                    "edge_score": 0.28,
                    "patterns_found": 3,
                    "date": (datetime.now()).isoformat(),
                },
            ],
            "trend_statistics": {
                "age_bias_frequency": 0.75,
                "weight_bias_frequency": 0.60,
                "draw_bias_frequency": 0.45,
                "form_pattern_frequency": 0.80,
            },
            "top_patterns": [
                "Winners aged 4-5 years (78% frequency)",
                "Light weights under 9st 2lbs (65% frequency)",
                "High draws 10+ (55% frequency)",
                "Non-winners last time out (85% frequency)",
            ],
        }

    def _convert_trends_to_csv(self, trends_data: Dict[str, Any]) -> str:
        """Convert trends data to CSV format."""
        # Simple CSV conversion - could be enhanced
        csv_lines = []
        csv_lines.append("Trend_Type,Pattern,Percentage,Confidence,Edge_Value")

        trend_categories = trends_data.get("trend_categories", {})
        for category, trends in trend_categories.items():
            for trend in trends:
                csv_lines.append(
                    f"{trend.get('trend_type', '')},"
                    f"{trend.get('pattern', '')},"
                    f"{trend.get('percentage', 0)},"
                    f"{trend.get('confidence', 0)},"
                    f"{trend.get('edge_value', 0)}"
                )

        return "\n".join(csv_lines)


# HTML template for race trends dashboard
RACE_TRENDS_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Race Trends Analysis Dashboard</title>
    <style>
        .trends-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .trend-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 10px 0; }
        .edge-score { font-size: 24px; font-weight: bold; color: #28a745; }
        .confidence-high { color: #28a745; }
        .confidence-medium { color: #ffc107; }
        .confidence-low { color: #dc3545; }
        .pattern-list { list-style-type: none; padding: 0; }
        .pattern-item { background: #e9ecef; padding: 8px; margin: 5px 0; border-radius: 4px; }
        .horse-analysis { border-left: 4px solid #007bff; padding-left: 15px; }
    </style>
</head>
<body>
    <div class="trends-container">
        <h1>🏇 Race Trends Analysis Dashboard</h1>
        
        <div class="trend-card">
            <h2>📊 Current Race Analysis</h2>
            <div id="race-summary">
                <p><strong>Race:</strong> <span id="race-name">Loading...</span></p>
                <p><strong>Course:</strong> <span id="race-course">Loading...</span></p>
                <p><strong>Edge Score:</strong> <span id="edge-score" class="edge-score">Loading...</span></p>
                <p><strong>Patterns Found:</strong> <span id="patterns-count">Loading...</span></p>
            </div>
        </div>
        
        <div class="trend-card">
            <h2>🎯 Identified Patterns</h2>
            <ul id="patterns-list" class="pattern-list">
                <li class="pattern-item">Loading patterns...</li>
            </ul>
        </div>
        
        <div class="trend-card">
            <h2>🐎 Horse Analysis</h2>
            <div id="horses-analysis">
                <p>Loading horse analysis...</p>
            </div>
        </div>
        
        <div class="trend-card">
            <h2>💰 Betting Recommendations</h2>
            <div id="betting-recommendations">
                <p>Loading recommendations...</p>
            </div>
        </div>
    </div>
    
    <script>
        // JavaScript for dynamic dashboard updates
        async function loadRaceTrends() {
            try {
                // Sample data - in real implementation, this would fetch from API
                const sampleData = {
                    race_name: 'Chesterfield Cup',
                    course: 'Goodwood',
                    edge_score: 0.35,
                    patterns_found: 4,
                    patterns: [
                        'Age Trends: 8/12 winners aged 4-5 years (67%)',
                        'Weight Trends: 9/12 winners carried 9st 2lbs or less (75%)',
                        'Draw Trends: 8/10 winners from stall 10+ (80%)',
                        'Form Trends: 12/12 winners did not win last run (100%)'
                    ],
                    horses: [
                        { name: 'Thunder Strike', combined_score: 0.78, recommendation: 'STRONG_BET' },
                        { name: 'Desert Lightning', combined_score: 0.72, recommendation: 'MODERATE_BET' },
                        { name: 'Celtic Storm', combined_score: 0.65, recommendation: 'WEAK_BET' }
                    ]
                };
                
                // Update DOM elements
                document.getElementById('race-name').textContent = sampleData.race_name;
                document.getElementById('race-course').textContent = sampleData.course;
                document.getElementById('edge-score').textContent = (sampleData.edge_score * 100).toFixed(1) + '%';
                document.getElementById('patterns-count').textContent = sampleData.patterns_found;
                
                // Update patterns list
                const patternsList = document.getElementById('patterns-list');
                patternsList.innerHTML = '';
                sampleData.patterns.forEach(pattern => {
                    const li = document.createElement('li');
                    li.className = 'pattern-item';
                    li.textContent = pattern;
                    patternsList.appendChild(li);
                });
                
                // Update horses analysis
                const horsesDiv = document.getElementById('horses-analysis');
                horsesDiv.innerHTML = '';
                sampleData.horses.forEach((horse, index) => {
                    const div = document.createElement('div');
                    div.className = 'horse-analysis';
                    div.innerHTML = `
                        <h4>${index + 1}. ${horse.name}</h4>
                        <p>Combined Score: ${(horse.combined_score * 100).toFixed(1)}%</p>
                        <p>Recommendation: <strong>${horse.recommendation}</strong></p>
                    `;
                    horsesDiv.appendChild(div);
                });
                
            } catch (error) {
                console.error('Error loading race trends:', error);
            }
        }
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadRaceTrends);
    </script>
</body>
</html>
"""


def integrate_race_trends_with_web_gui(flask_app):
    """Integrate race trends analysis with existing web GUI."""

    # Initialize the integration
    trends_integration = RaceTrendsWebIntegration(flask_app)

    # Add dashboard route
    @flask_app.route("/race-trends-dashboard")
    def race_trends_dashboard_page():
        """Serve the race trends dashboard page."""
        return RACE_TRENDS_DASHBOARD_HTML

    print("✅ Race Trends Analysis integrated with Web GUI")
    print("📊 Dashboard available at: /race-trends-dashboard")
    print("🔗 API endpoints:")
    print("   • POST /api/race-trends/analyze")
    print("   • POST /api/race-trends/score-horse")
    print("   • POST /api/race-trends/combined-analysis")
    print("   • GET /api/race-trends/dashboard")
    print("   • POST /api/race-trends/export")

    return trends_integration


if __name__ == "__main__":
    print("Race Trends Web Integration module ready for import.")
    print(
        "Use integrate_race_trends_with_web_gui(flask_app) to add to existing web GUI."
    )
