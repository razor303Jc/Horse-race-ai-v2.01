#!/usr/bin/env python3
"""
Contextual AI Pipeline Integration - V2.03
==========================================

Pipeline integration for the Contextual AI Enhancement System.
Integrates advanced contextual AI analysis as Stage 7 in the V2.03 pipeline.

This stage provides:
- Deep contextual analysis of race conditions
- AI-powered form insights and pattern recognition
- Automated race preview generation
- Intelligent alert system for value opportunities
- Market sentiment analysis and contextual factors
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Import contextual AI engine
try:
    from contextual_ai_enhancement import ContextualAIEngine
except ImportError:
    # Try absolute import if relative import fails
    from tools.pipeline.contextual_ai_enhancement import ContextualAIEngine

logger = logging.getLogger(__name__)


class ContextualAIPipelineIntegration:
    """
    Pipeline integration for Contextual AI Enhancement System.

    Processes race data through advanced contextual AI analysis
    and generates comprehensive insights for decision making.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the contextual AI pipeline integration."""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "config/contextual_ai_config.json"

        # Load configuration
        self.config = self._load_config()

        # Initialize contextual AI engine
        self.ai_engine = ContextualAIEngine(self.config.get("ai_engine", {}))

        # Pipeline settings
        self.enabled = self.config.get("enabled", True)
        self.require_market_data = self.config.get("require_market_data", False)
        self.min_horses_for_analysis = self.config.get("min_horses_for_analysis", 4)
        self.max_concurrent_races = self.config.get("max_concurrent_races", 3)

        # Output settings
        self.save_detailed_analysis = self.config.get("save_detailed_analysis", True)
        self.generate_summary_only = self.config.get("generate_summary_only", False)
        self.include_race_preview = self.config.get("include_race_preview", True)

        # Quality thresholds
        self.min_data_quality_score = self.config.get("min_data_quality_score", 0.6)
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.5)

        self.logger.info("Contextual AI Pipeline Integration initialized")

    def _load_config(self) -> Dict:
        """Load pipeline configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                self.logger.info(f"Loaded config from {self.config_path}")
                return config
            else:
                self.logger.info("Using default contextual AI configuration")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default pipeline configuration."""
        return {
            "enabled": True,
            "require_market_data": False,
            "min_horses_for_analysis": 4,
            "max_concurrent_races": 3,
            "save_detailed_analysis": True,
            "generate_summary_only": False,
            "include_race_preview": True,
            "min_data_quality_score": 0.6,
            "min_confidence_threshold": 0.5,
            "ai_engine": {
                "contextual_analysis": {
                    "enabled": True,
                    "deep_analysis_mode": True,
                    "weather_analysis": True,
                    "track_condition_analysis": True,
                    "form_pattern_recognition": True,
                    "market_sentiment_analysis": True,
                },
                "alert_system": {
                    "enabled": True,
                    "value_alert_threshold": 0.15,
                    "confidence_threshold": 0.75,
                    "market_movement_threshold": 0.1,
                    "pattern_significance_threshold": 0.8,
                },
                "preview_generation": {
                    "enabled": True,
                    "include_ai_insights": True,
                    "narrative_style": "comprehensive",
                    "include_risk_assessment": True,
                    "include_value_opportunities": True,
                },
                "performance_optimization": {
                    "use_caching": True,
                    "cache_ttl_minutes": 30,
                    "parallel_analysis": True,
                    "max_concurrent_analyses": 5,
                },
            },
            "output_settings": {
                "save_to_file": True,
                "output_directory": "data/contextual_ai_analysis",
                "filename_format": "contextual_ai_{race_id}_{timestamp}.json",
                "compress_output": False,
                "retention_days": 30,
            },
            "integration_settings": {
                "pass_to_next_stage": True,
                "enrich_predictions": True,
                "update_confidence_scores": True,
                "merge_with_existing_analysis": True,
            },
        }

    async def run_contextual_ai_stage(
        self, pipeline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the contextual AI enhancement stage.

        Args:
            pipeline_data: Data from previous pipeline stages

        Returns:
            Enhanced pipeline data with contextual AI analysis
        """
        stage_start = datetime.now()

        try:
            self.logger.info("Starting Contextual AI Enhancement Stage")

            # Input validation
            validation_result = self._validate_input_data(pipeline_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    validation_result["error"], pipeline_data
                )

            # Check if stage is enabled
            if not self.enabled:
                self.logger.info("Contextual AI stage disabled, skipping")
                return self._create_passthrough_result(pipeline_data)

            # Extract required data
            race_data = pipeline_data.get("race_data", {})
            horses_data = pipeline_data.get("horses_data", [])
            market_data = pipeline_data.get("market_data")
            predictions = pipeline_data.get("predictions", {})

            # Check minimum requirements
            if len(horses_data) < self.min_horses_for_analysis:
                self.logger.warning(
                    f"Insufficient horses ({len(horses_data)}) for contextual AI analysis"
                )
                return self._create_insufficient_data_result(pipeline_data)

            # Enrich horses data with predictions
            enriched_horses_data = self._enrich_horses_with_predictions(
                horses_data, predictions
            )

            # Run contextual AI analysis
            self.logger.info("Running comprehensive contextual AI analysis")
            contextual_analysis = await self.ai_engine.run_contextual_ai_analysis(
                race_data, enriched_horses_data, market_data
            )

            # Validate analysis results
            analysis_validation = self._validate_analysis_results(contextual_analysis)
            if not analysis_validation["valid"]:
                return self._create_analysis_error_result(
                    analysis_validation["error"], pipeline_data
                )

            # Process and enhance results
            processed_results = await self._process_contextual_results(
                contextual_analysis, pipeline_data
            )

            # Update confidence scores based on contextual analysis
            updated_predictions = self._update_prediction_confidence(
                predictions, contextual_analysis
            )

            # Generate alerts and recommendations
            alerts_and_recommendations = self._generate_alerts_and_recommendations(
                contextual_analysis, race_data
            )

            # Save detailed analysis if enabled
            if self.save_detailed_analysis:
                await self._save_detailed_analysis(contextual_analysis, race_data)

            # Create stage results
            stage_duration = (datetime.now() - stage_start).total_seconds()

            stage_results = {
                "stage_name": "contextual_ai_enhancement",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "processing_time_seconds": stage_duration,
                "race_id": race_data.get("race_id", "unknown"),
                "contextual_analysis": processed_results,
                "updated_predictions": updated_predictions,
                "alerts_and_recommendations": alerts_and_recommendations,
                "analysis_summary": self._create_analysis_summary(contextual_analysis),
                "stage_metadata": {
                    "horses_analyzed": len(enriched_horses_data),
                    "alerts_generated": len(
                        contextual_analysis.get("intelligent_alerts", [])
                    ),
                    "value_opportunities": len(
                        contextual_analysis.get("value_assessment", {}).get(
                            "value_horses", []
                        )
                    ),
                    "confidence_level": contextual_analysis.get(
                        "confidence_analysis", {}
                    ).get("overall_confidence", 0),
                    "contextual_factors_analyzed": self._count_contextual_factors(
                        contextual_analysis
                    ),
                },
            }

            # Merge with existing pipeline data
            enhanced_pipeline_data = self._merge_with_pipeline_data(
                pipeline_data, stage_results
            )

            self.logger.info(
                f"Contextual AI stage completed successfully in {stage_duration:.2f}s - "
                f"{len(contextual_analysis.get('intelligent_alerts', []))} alerts generated"
            )

            return enhanced_pipeline_data

        except Exception as e:
            error_duration = (datetime.now() - stage_start).total_seconds()
            self.logger.error(f"Error in contextual AI stage: {e}")

            return self._create_error_result(
                f"Contextual AI analysis failed: {str(e)}",
                pipeline_data,
                error_duration,
            )

    def _validate_input_data(self, pipeline_data: Dict) -> Dict[str, Any]:
        """Validate input data for contextual AI analysis."""
        try:
            # Check required keys
            required_keys = ["race_data", "horses_data"]
            missing_keys = [key for key in required_keys if key not in pipeline_data]

            if missing_keys:
                return {
                    "valid": False,
                    "error": f"Missing required data: {missing_keys}",
                }

            # Validate race data
            race_data = pipeline_data["race_data"]
            if not isinstance(race_data, dict) or not race_data:
                return {"valid": False, "error": "Invalid or empty race_data"}

            # Validate horses data
            horses_data = pipeline_data["horses_data"]
            if not isinstance(horses_data, list) or len(horses_data) == 0:
                return {"valid": False, "error": "Invalid or empty horses_data"}

            # Check for required race fields
            required_race_fields = ["race_id"]
            missing_race_fields = [
                field for field in required_race_fields if field not in race_data
            ]

            if missing_race_fields:
                self.logger.warning(
                    f"Missing race fields: {missing_race_fields} - using defaults"
                )

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": f"Input validation error: {str(e)}"}

    def _validate_analysis_results(self, analysis_results: Dict) -> Dict[str, Any]:
        """Validate contextual AI analysis results."""
        try:
            # Check for error in results
            if "error" in analysis_results:
                return {
                    "valid": False,
                    "error": f"Analysis error: {analysis_results['error']}",
                }

            # Check required result sections
            required_sections = [
                "race_conditions",
                "form_insights",
                "pattern_analysis",
                "intelligent_alerts",
                "confidence_analysis",
            ]

            missing_sections = [
                section
                for section in required_sections
                if section not in analysis_results
            ]

            if missing_sections:
                self.logger.warning(f"Missing analysis sections: {missing_sections}")

            # Check data quality
            confidence_analysis = analysis_results.get("confidence_analysis", {})
            data_quality_score = confidence_analysis.get("data_quality_score", 0)

            if data_quality_score < self.min_data_quality_score:
                self.logger.warning(f"Low data quality score: {data_quality_score}")

            # Check overall confidence
            overall_confidence = confidence_analysis.get("overall_confidence", 0)

            if overall_confidence < self.min_confidence_threshold:
                self.logger.warning(f"Low analysis confidence: {overall_confidence}")

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": f"Analysis validation error: {str(e)}"}

    def _enrich_horses_with_predictions(
        self, horses_data: List[Dict], predictions: Dict
    ) -> List[Dict]:
        """Enrich horses data with prediction results."""
        try:
            enriched_horses = []

            for horse in horses_data:
                horse_name = horse.get("horse_name", "")
                enriched_horse = horse.copy()

                # Add prediction data if available
                if horse_name in predictions:
                    horse_predictions = predictions[horse_name]
                    enriched_horse["prediction"] = horse_predictions

                    # Add derived metrics
                    enriched_horse["implied_odds"] = (
                        1.0 / horse_predictions.get("win_probability", 0.1)
                        if horse_predictions.get("win_probability", 0) > 0
                        else 10.0
                    )

                    enriched_horse["value_ratio"] = (
                        horse.get("odds", 5.0) / enriched_horse["implied_odds"]
                        if enriched_horse["implied_odds"] > 0
                        else 1.0
                    )

                enriched_horses.append(enriched_horse)

            return enriched_horses

        except Exception as e:
            self.logger.error(f"Error enriching horses data: {e}")
            return horses_data

    async def _process_contextual_results(
        self, contextual_analysis: Dict, pipeline_data: Dict
    ) -> Dict[str, Any]:
        """Process and format contextual analysis results."""
        try:
            processed_results = {
                "race_conditions": contextual_analysis.get("race_conditions", {}),
                "form_insights": contextual_analysis.get("form_insights", {}),
                "pattern_analysis": contextual_analysis.get("pattern_analysis", {}),
                "market_sentiment": contextual_analysis.get("market_sentiment", {}),
                "value_assessment": contextual_analysis.get("value_assessment", {}),
                "confidence_analysis": contextual_analysis.get(
                    "confidence_analysis", {}
                ),
                "contextual_summary": contextual_analysis.get("contextual_summary", {}),
            }

            # Add race preview if enabled
            if self.include_race_preview:
                processed_results["race_preview"] = contextual_analysis.get(
                    "race_preview", {}
                )

            # Add processing metadata
            processed_results["processing_metadata"] = {
                "analysis_timestamp": contextual_analysis.get("timestamp"),
                "analysis_duration": contextual_analysis.get(
                    "analysis_duration_seconds"
                ),
                "contextual_factors_count": len(
                    contextual_analysis.get("race_conditions", {})
                ),
                "insights_generated": len(
                    contextual_analysis.get("form_insights", {}).get(
                        "individual_insights", []
                    )
                ),
                "patterns_identified": len(
                    contextual_analysis.get("pattern_analysis", {}).get(
                        "emerging_patterns", []
                    )
                ),
            }

            return processed_results

        except Exception as e:
            self.logger.error(f"Error processing contextual results: {e}")
            return {"error": str(e)}

    def _update_prediction_confidence(
        self, predictions: Dict, contextual_analysis: Dict
    ) -> Dict:
        """Update prediction confidence based on contextual analysis."""
        try:
            updated_predictions = predictions.copy()

            # Get confidence factors from analysis
            confidence_analysis = contextual_analysis.get("confidence_analysis", {})
            overall_confidence = confidence_analysis.get("overall_confidence", 1.0)

            # Get contextual adjustments
            value_assessment = contextual_analysis.get("value_assessment", {})
            value_horses = {
                horse["horse_name"]: horse["contextual_value"]
                for horse in value_assessment.get("value_horses", [])
            }

            # Update each horse's prediction confidence
            for horse_name, prediction in updated_predictions.items():
                if isinstance(prediction, dict):
                    # Apply overall confidence adjustment
                    original_confidence = prediction.get("confidence", 0.8)
                    contextual_confidence = original_confidence * overall_confidence

                    # Apply value-based adjustment
                    if horse_name in value_horses:
                        value_boost = min(value_horses[horse_name] * 0.1, 0.15)
                        contextual_confidence += value_boost

                    # Ensure confidence stays within bounds
                    contextual_confidence = max(0.1, min(1.0, contextual_confidence))

                    # Update prediction
                    prediction["original_confidence"] = original_confidence
                    prediction["contextual_confidence"] = contextual_confidence
                    prediction["confidence"] = contextual_confidence
                    prediction["confidence_factors"] = {
                        "base_confidence": original_confidence,
                        "contextual_adjustment": overall_confidence,
                        "value_adjustment": value_horses.get(horse_name, 0),
                        "final_confidence": contextual_confidence,
                    }

            return updated_predictions

        except Exception as e:
            self.logger.error(f"Error updating prediction confidence: {e}")
            return predictions

    def _generate_alerts_and_recommendations(
        self, contextual_analysis: Dict, race_data: Dict
    ) -> Dict[str, Any]:
        """Generate alerts and recommendations from contextual analysis."""
        try:
            alerts_and_recs = {
                "intelligent_alerts": contextual_analysis.get("intelligent_alerts", []),
                "value_opportunities": [],
                "risk_warnings": [],
                "strategic_recommendations": [],
                "condition_alerts": [],
            }

            # Extract value opportunities
            value_assessment = contextual_analysis.get("value_assessment", {})
            for horse in value_assessment.get("value_horses", []):
                alerts_and_recs["value_opportunities"].append(
                    {
                        "horse_name": horse.get("horse_name"),
                        "value_score": horse.get("contextual_value", 0),
                        "recommendation": f"Strong value opportunity - {horse.get('horse_name')}",
                        "confidence": horse.get("context_multiplier", 1.0),
                    }
                )

            # Extract risk warnings from confidence analysis
            confidence_analysis = contextual_analysis.get("confidence_analysis", {})
            risk_factors = confidence_analysis.get("risk_factors", [])

            for risk in risk_factors:
                alerts_and_recs["risk_warnings"].append(
                    {
                        "risk_type": risk.get("type", "unknown"),
                        "description": risk.get("description", "Unknown risk"),
                        "severity": risk.get("severity", "medium"),
                        "mitigation": risk.get("mitigation", "Monitor closely"),
                    }
                )

            # Strategic recommendations from contextual summary
            contextual_summary = contextual_analysis.get("contextual_summary", {})

            alerts_and_recs["strategic_recommendations"] = [
                {
                    "approach": contextual_summary.get(
                        "recommended_approach", "Standard"
                    ),
                    "confidence_level": contextual_summary.get(
                        "confidence_level", "MEDIUM"
                    ),
                    "value_outlook": contextual_summary.get(
                        "value_outlook", "Moderate"
                    ),
                    "key_factors": contextual_summary.get("key_insights", []),
                }
            ]

            # Condition-specific alerts
            race_conditions = contextual_analysis.get("race_conditions", {})
            condition_impact = race_conditions.get("condition_impact_score", 0)

            if condition_impact > 0.7:
                alerts_and_recs["condition_alerts"].append(
                    {
                        "type": "high_impact_conditions",
                        "message": "Significant weather/track impact expected",
                        "recommendation": "Adjust strategies for conditions",
                    }
                )

            return alerts_and_recs

        except Exception as e:
            self.logger.error(f"Error generating alerts and recommendations: {e}")
            return {"error": str(e)}

    async def _save_detailed_analysis(
        self, contextual_analysis: Dict, race_data: Dict
    ) -> bool:
        """Save detailed contextual analysis to file."""
        try:
            output_dir = self.config.get("output_settings", {}).get(
                "output_directory", "data/contextual_ai_analysis"
            )

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename
            race_id = race_data.get("race_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contextual_ai_{race_id}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)

            # Save analysis
            with open(filepath, "w") as f:
                json.dump(contextual_analysis, f, indent=2, default=str)

            self.logger.info(f"Saved detailed analysis to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving detailed analysis: {e}")
            return False

    def _create_analysis_summary(self, contextual_analysis: Dict) -> Dict[str, Any]:
        """Create summary of contextual analysis."""
        try:
            summary = {
                "analysis_quality": "unknown",
                "key_insights_count": 0,
                "value_opportunities_count": 0,
                "alerts_generated": 0,
                "confidence_level": "MEDIUM",
                "primary_insights": [],
                "recommendation_summary": "",
            }

            # Analysis quality
            confidence_analysis = contextual_analysis.get("confidence_analysis", {})
            overall_confidence = confidence_analysis.get("overall_confidence", 0.5)

            if overall_confidence > 0.8:
                summary["analysis_quality"] = "high"
            elif overall_confidence > 0.6:
                summary["analysis_quality"] = "medium"
            else:
                summary["analysis_quality"] = "low"

            # Count insights and opportunities
            contextual_summary = contextual_analysis.get("contextual_summary", {})
            summary["key_insights_count"] = len(
                contextual_summary.get("key_insights", [])
            )

            value_assessment = contextual_analysis.get("value_assessment", {})
            summary["value_opportunities_count"] = len(
                value_assessment.get("value_horses", [])
            )

            summary["alerts_generated"] = len(
                contextual_analysis.get("intelligent_alerts", [])
            )

            # Confidence level
            summary["confidence_level"] = contextual_summary.get(
                "confidence_level", "MEDIUM"
            )

            # Primary insights
            summary["primary_insights"] = contextual_summary.get("key_insights", [])[:3]

            # Recommendation summary
            summary["recommendation_summary"] = contextual_summary.get(
                "recommended_approach", "Standard analysis approach"
            )

            return summary

        except Exception as e:
            self.logger.error(f"Error creating analysis summary: {e}")
            return {"error": str(e)}

    def _count_contextual_factors(self, contextual_analysis: Dict) -> int:
        """Count the number of contextual factors analyzed."""
        try:
            factor_count = 0

            # Race conditions factors
            race_conditions = contextual_analysis.get("race_conditions", {})
            factor_count += len(race_conditions.get("weather_analysis", {}))
            factor_count += len(race_conditions.get("track_analysis", {}))
            factor_count += len(race_conditions.get("time_factors", {}))

            # Form insight factors
            form_insights = contextual_analysis.get("form_insights", {})
            factor_count += len(form_insights.get("individual_insights", []))
            factor_count += len(form_insights.get("form_patterns", []))

            # Pattern analysis factors
            pattern_analysis = contextual_analysis.get("pattern_analysis", {})
            factor_count += len(pattern_analysis.get("trainer_patterns", []))
            factor_count += len(pattern_analysis.get("jockey_patterns", []))

            return factor_count

        except Exception as e:
            self.logger.error(f"Error counting contextual factors: {e}")
            return 0

    def _merge_with_pipeline_data(
        self, pipeline_data: Dict, stage_results: Dict
    ) -> Dict[str, Any]:
        """Merge stage results with existing pipeline data."""
        try:
            enhanced_data = pipeline_data.copy()

            # Add stage results
            if "pipeline_stages" not in enhanced_data:
                enhanced_data["pipeline_stages"] = {}

            enhanced_data["pipeline_stages"][
                "contextual_ai_enhancement"
            ] = stage_results

            # Update predictions with contextual enhancements
            if "updated_predictions" in stage_results:
                enhanced_data["predictions"] = stage_results["updated_predictions"]

            # Add contextual analysis to main data
            enhanced_data["contextual_analysis"] = stage_results.get(
                "contextual_analysis", {}
            )

            # Add alerts and recommendations
            enhanced_data["alerts_and_recommendations"] = stage_results.get(
                "alerts_and_recommendations", {}
            )

            # Update metadata
            if "pipeline_metadata" not in enhanced_data:
                enhanced_data["pipeline_metadata"] = {}

            enhanced_data["pipeline_metadata"]["contextual_ai"] = {
                "processed": True,
                "processing_time": stage_results.get("processing_time_seconds", 0),
                "analysis_quality": stage_results.get("analysis_summary", {}).get(
                    "analysis_quality", "unknown"
                ),
                "alerts_count": stage_results.get("stage_metadata", {}).get(
                    "alerts_generated", 0
                ),
            }

            return enhanced_data

        except Exception as e:
            self.logger.error(f"Error merging with pipeline data: {e}")
            return pipeline_data

    def _create_error_result(
        self, error_message: str, pipeline_data: Dict, duration: float = 0
    ) -> Dict[str, Any]:
        """Create error result for failed stage."""
        error_result = pipeline_data.copy()

        error_result["pipeline_stages"] = error_result.get("pipeline_stages", {})
        error_result["pipeline_stages"]["contextual_ai_enhancement"] = {
            "stage_name": "contextual_ai_enhancement",
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": duration,
        }

        return error_result

    def _create_passthrough_result(self, pipeline_data: Dict) -> Dict[str, Any]:
        """Create passthrough result when stage is disabled."""
        passthrough_result = pipeline_data.copy()

        passthrough_result["pipeline_stages"] = passthrough_result.get(
            "pipeline_stages", {}
        )
        passthrough_result["pipeline_stages"]["contextual_ai_enhancement"] = {
            "stage_name": "contextual_ai_enhancement",
            "status": "skipped",
            "reason": "Stage disabled in configuration",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": 0,
        }

        return passthrough_result

    def _create_insufficient_data_result(self, pipeline_data: Dict) -> Dict[str, Any]:
        """Create result for insufficient data scenario."""
        insufficient_result = pipeline_data.copy()

        insufficient_result["pipeline_stages"] = insufficient_result.get(
            "pipeline_stages", {}
        )
        insufficient_result["pipeline_stages"]["contextual_ai_enhancement"] = {
            "stage_name": "contextual_ai_enhancement",
            "status": "skipped",
            "reason": "Insufficient data for contextual AI analysis",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": 0,
        }

        return insufficient_result

    def _create_analysis_error_result(
        self, error_message: str, pipeline_data: Dict
    ) -> Dict[str, Any]:
        """Create result for analysis validation errors."""
        error_result = pipeline_data.copy()

        error_result["pipeline_stages"] = error_result.get("pipeline_stages", {})
        error_result["pipeline_stages"]["contextual_ai_enhancement"] = {
            "stage_name": "contextual_ai_enhancement",
            "status": "failed",
            "error": f"Analysis validation failed: {error_message}",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": 0,
        }

        return error_result


async def main():
    """Main function for testing contextual AI pipeline integration."""
    # Initialize pipeline integration
    integration = ContextualAIPipelineIntegration()

    # Sample pipeline data
    pipeline_data = {
        "race_data": {
            "race_id": "test_contextual_001",
            "race_time": "15:30",
            "track": "Ascot",
            "distance": 2400,
            "weather": "light_rain",
            "track_condition": "good_to_soft",
        },
        "horses_data": [
            {
                "horse_name": "Masterful",
                "odds": 3.2,
                "form_string": "11234",
                "last_run_days": 21,
            },
            {
                "horse_name": "Storm Shadow",
                "odds": 4.5,
                "form_string": "21112",
                "last_run_days": 35,
            },
        ],
        "predictions": {
            "Masterful": {
                "win_probability": 0.38,
                "place_probability": 0.72,
                "confidence": 0.85,
            },
            "Storm Shadow": {
                "win_probability": 0.28,
                "place_probability": 0.65,
                "confidence": 0.78,
            },
        },
    }

    # Run contextual AI stage
    results = await integration.run_contextual_ai_stage(pipeline_data)

    print("\n=== CONTEXTUAL AI PIPELINE INTEGRATION TEST ===")
    print(
        f"Stage Status: {results.get('pipeline_stages', {}).get('contextual_ai_enhancement', {}).get('status', 'Unknown')}"
    )

    stage_results = results.get("pipeline_stages", {}).get(
        "contextual_ai_enhancement", {}
    )
    if stage_results.get("status") == "completed":
        metadata = stage_results.get("stage_metadata", {})
        print(
            f"Processing Time: {stage_results.get('processing_time_seconds', 0):.2f}s"
        )
        print(f"Horses Analyzed: {metadata.get('horses_analyzed', 0)}")
        print(f"Alerts Generated: {metadata.get('alerts_generated', 0)}")
        print(f"Value Opportunities: {metadata.get('value_opportunities', 0)}")
        print(f"Confidence Level: {metadata.get('confidence_level', 0):.2f}")

        # Show some contextual analysis results
        contextual_analysis = results.get("contextual_analysis", {})
        if contextual_analysis:
            print(f"\n📊 Contextual Analysis Summary:")
            summary = contextual_analysis.get("contextual_summary", {})
            print(f"  Race Character: {summary.get('race_character', 'Unknown')}")
            print(f"  Confidence Level: {summary.get('confidence_level', 'MEDIUM')}")
            print(
                f"  Recommended Approach: {summary.get('recommended_approach', 'Standard')}"
            )

    print("\n=== CONTEXTUAL AI PIPELINE INTEGRATION COMPLETE ===")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Run the main function
    asyncio.run(main())
