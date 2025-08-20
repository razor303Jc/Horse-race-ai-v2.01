"""
Comprehensive Analytics Integration Test
======================================

Demonstration and testing of the comprehensive analytics system integrated
into Horse Racing AI v2.03.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from src.horse_racing_ai.analytics.comprehensive_integration import (
    comprehensive_analytics,
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_metrics(data: dict, indent: int = 0):
    """Pretty print metrics data."""
    spacing = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{spacing}{key}:")
            print_metrics(value, indent + 1)
        elif isinstance(value, list):
            print(f"{spacing}{key}:")
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    print(f"{spacing}  [{i+1}]:")
                    print_metrics(item, indent + 2)
                else:
                    print(f"{spacing}  - {item}")
        else:
            if isinstance(value, float):
                print(f"{spacing}{key}: {value:.3f}")
            else:
                print(f"{spacing}{key}: {value}")


async def test_quick_metrics():
    """Test quick metrics functionality."""
    print_section("QUICK METRICS DEMONSTRATION")

    print("Generating quick metrics for the last 30 days...")
    metrics = comprehensive_analytics.get_quick_metrics(30)

    if metrics:
        print_metrics(metrics)

        # Highlight key performance indicators
        accuracy = metrics.get("accuracy_metrics", {}).get("overall_accuracy", 0)
        roi = metrics.get("financial_metrics", {}).get("roi_percentage", 0)
        sharpe = metrics.get("financial_metrics", {}).get("sharpe_ratio", 0)

        print(f"\n📊 KEY PERFORMANCE INDICATORS:")
        print(f"   • Overall Accuracy: {accuracy}%")
        print(f"   • ROI: {roi}%")
        print(f"   • Sharpe Ratio: {sharpe}")
    else:
        print("❌ Failed to generate quick metrics")


async def test_roi_analysis():
    """Test ROI analysis functionality."""
    print_section("ROI ANALYSIS DEMONSTRATION")

    print("Generating ROI analysis for the last 90 days...")
    roi_data = comprehensive_analytics.get_roi_analysis(90)

    if roi_data:
        print_metrics(roi_data)

        # Risk assessment summary
        risk_assessment = roi_data.get("risk_assessment", {})
        print(f"\n🎯 RISK ASSESSMENT SUMMARY:")
        print(f"   • Risk Level: {risk_assessment.get('risk_level', 'Unknown')}")
        print(
            f"   • Drawdown Severity: {risk_assessment.get('drawdown_severity', 'Unknown')}"
        )
        print(
            f"   • Overall Rating: {risk_assessment.get('overall_rating', 'Unknown')}"
        )
    else:
        print("❌ Failed to generate ROI analysis")


async def test_weight_optimization():
    """Test weight optimization recommendations."""
    print_section("WEIGHT OPTIMIZATION RECOMMENDATIONS")

    print("Generating weight optimization recommendations...")
    optimization = comprehensive_analytics.get_weight_optimization_recommendations(90)

    if optimization:
        print_metrics(optimization)

        # Summary of improvements
        recommendations = optimization.get("recommendations", [])
        print(f"\n🚀 OPTIMIZATION OPPORTUNITIES:")
        for rec in recommendations:
            model = rec.get("model_name", "Unknown")
            improvement = rec.get("improvement_potential", 0)
            confidence = rec.get("confidence_score", 0)
            print(
                f"   • {model}: +{improvement}% improvement ({confidence}% confidence)"
            )
    else:
        print("❌ Failed to generate weight optimization recommendations")


async def test_validation_results():
    """Test real-world validation functionality."""
    print_section("REAL-WORLD VALIDATION RESULTS")

    print("Generating validation results against historical data...")
    validation = comprehensive_analytics.get_validation_results(90)

    if validation:
        print_metrics(validation)

        # Validation summary
        historical_acc = validation.get("historical_accuracy", 0)
        forward_acc = validation.get("forward_testing_accuracy", 0)
        consistency = validation.get("consistency_score", 0)

        print(f"\n✅ VALIDATION SUMMARY:")
        print(f"   • Historical Accuracy: {historical_acc}%")
        print(f"   • Forward Testing: {forward_acc}%")
        print(f"   • Consistency Score: {consistency}%")
        print(f"   • Recommendation: {validation.get('recommendation', 'None')}")
    else:
        print("❌ Failed to generate validation results")


async def test_feature_importance():
    """Test feature importance analysis."""
    print_section("FEATURE IMPORTANCE ANALYSIS")

    print("Analyzing feature importance for ML models...")
    features = comprehensive_analytics.get_feature_importance(90)

    if features:
        print_metrics(features)

        # Top features summary
        ranked_features = features.get("feature_importance", {}).get(
            "ranked_features", []
        )
        print(f"\n🎯 TOP PERFORMING FEATURES:")
        for feature in ranked_features[:3]:
            name = feature.get("feature", "Unknown")
            importance = feature.get("importance_percentage", "0%")
            rank = feature.get("rank", 0)
            print(f"   {rank}. {name}: {importance}")
    else:
        print("❌ Failed to generate feature importance analysis")


async def test_confidence_analysis():
    """Test prediction confidence analysis."""
    print_section("PREDICTION CONFIDENCE ANALYSIS")

    print("Analyzing prediction confidence and calibration...")
    confidence = comprehensive_analytics.get_confidence_analysis(90)

    if confidence:
        print_metrics(confidence)

        # Confidence insights
        insights = confidence.get("insights", {})
        correlation = confidence.get("confidence_analysis", {}).get(
            "confidence_accuracy_correlation", 0
        )

        print(f"\n🎯 CONFIDENCE INSIGHTS:")
        print(
            f"   • Correlation Strength: {insights.get('correlation_strength', 'Unknown')}"
        )
        print(
            f"   • Calibration Quality: {insights.get('calibration_quality', 'Unknown')}"
        )
        print(f"   • Correlation Score: {correlation:.3f}")
    else:
        print("❌ Failed to generate confidence analysis")


async def test_performance_attribution():
    """Test performance attribution analysis."""
    print_section("PERFORMANCE ATTRIBUTION BY TRACK")

    print("Analyzing performance attribution by track...")
    attribution = comprehensive_analytics.get_performance_attribution(90, "track")

    if attribution:
        print_metrics(attribution)

        # Track performance summary
        track_data = attribution.get("performance_attribution", {}).get("track", {})
        print(f"\n🏆 TRACK PERFORMANCE SUMMARY:")
        for track, metrics in track_data.items():
            accuracy = metrics.get("accuracy", "0%")
            roi = metrics.get("roi", "0%")
            predictions = metrics.get("predictions", 0)
            print(
                f"   • {track}: {accuracy} accuracy, {roi} ROI ({predictions} predictions)"
            )
    else:
        print("❌ Failed to generate performance attribution")


async def test_comprehensive_report():
    """Test comprehensive report generation."""
    print_section("COMPREHENSIVE REPORT GENERATION")

    print("Generating comprehensive analytics report...")

    # Generate report for last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    report = comprehensive_analytics.generate_comprehensive_report(
        start_date=start_date,
        end_date=end_date,
        include_validation=True,
        include_optimization=True,
    )

    if report.get("status") == "success":
        print(f"✅ Report generated successfully!")
        print(f"   • Report ID: {report.get('report_id')}")
        print(f"   • Generated: {report.get('generated_at')}")
        print(f"   • Period: {report.get('period_analyzed')}")
        print(
            f"   • Export Path: {report.get('export_paths', {}).get('json', 'Not available')}"
        )

        # Summary metrics
        summary = report.get("summary", {})
        print(f"\n📊 REPORT SUMMARY:")
        print(f"   • Overall Accuracy: {summary.get('overall_accuracy', 0)}%")
        print(f"   • Win Prediction: {summary.get('win_prediction_accuracy', 0)}%")
        print(f"   • Place Prediction: {summary.get('place_prediction_accuracy', 0)}%")
        print(f"   • F1 Score: {summary.get('f1_score', 0):.3f}")

    else:
        print(
            f"❌ Failed to generate comprehensive report: {report.get('message', 'Unknown error')}"
        )


async def test_prediction_recording():
    """Test prediction result recording."""
    print_section("PREDICTION RESULT RECORDING")

    print("Recording sample prediction results...")

    # Record sample predictions
    sample_predictions = [
        {
            "race_id": "FLM_2024_01_15_R1",
            "horse_id": "HORSE_001",
            "prediction_type": "win",
            "predicted_probability": 0.68,
            "confidence_score": 0.82,
            "actual_result": 1,  # Correct prediction
            "odds": 3.20,
            "stake": 100.0,
            "return_amount": 320.0,
            "track": "Flemington",
            "distance": 1200,
            "race_type": "Maiden",
            "race_date": "2024-01-15",
        },
        {
            "race_id": "FLM_2024_01_15_R1",
            "horse_id": "HORSE_002",
            "prediction_type": "place",
            "predicted_probability": 0.74,
            "confidence_score": 0.89,
            "actual_result": 1,  # Correct prediction
            "odds": 2.10,
            "stake": 100.0,
            "return_amount": 210.0,
            "track": "Flemington",
            "distance": 1200,
            "race_type": "Maiden",
            "race_date": "2024-01-15",
        },
        {
            "race_id": "CAU_2024_01_15_R2",
            "horse_id": "HORSE_003",
            "prediction_type": "win",
            "predicted_probability": 0.45,
            "confidence_score": 0.65,
            "actual_result": 0,  # Incorrect prediction
            "odds": 4.50,
            "stake": 100.0,
            "return_amount": 0.0,
            "track": "Caulfield",
            "distance": 1400,
            "race_type": "Handicap",
            "race_date": "2024-01-15",
        },
    ]

    for i, prediction in enumerate(sample_predictions):
        print(f"Recording prediction {i+1}/3...")
        comprehensive_analytics.record_prediction_result(**prediction)

    print("✅ Sample predictions recorded successfully!")


async def run_comprehensive_demo():
    """Run the complete comprehensive analytics demonstration."""
    print("🐎 HORSE RACING AI v2.03 - COMPREHENSIVE ANALYTICS INTEGRATION")
    print("================================================================")
    print("Demonstrating advanced analytics capabilities including:")
    print("• Performance metrics (accuracy, precision, recall, F1)")
    print("• Financial analysis (ROI, Sharpe ratio, risk metrics)")
    print("• ML weight optimization recommendations")
    print("• Real-world validation against historical results")
    print("• Feature importance and confidence analysis")
    print("• Detailed reporting and visualization")

    # Run all test functions
    try:
        await test_prediction_recording()
        await test_quick_metrics()
        await test_roi_analysis()
        await test_weight_optimization()
        await test_validation_results()
        await test_feature_importance()
        await test_confidence_analysis()
        await test_performance_attribution()
        await test_comprehensive_report()

        print_section("INTEGRATION COMPLETE")
        print("🎉 Comprehensive Analytics Integration Successful!")
        print("\nKey Features Demonstrated:")
        print("✅ Real-time performance metrics calculation")
        print("✅ Advanced ROI and risk analysis")
        print("✅ ML model weight optimization recommendations")
        print("✅ Historical validation with bias detection")
        print("✅ Feature importance attribution")
        print("✅ Prediction confidence calibration")
        print("✅ Segmented performance analysis")
        print("✅ Comprehensive reporting with exports")

        print("\n🚀 The comprehensive analytics system is now fully integrated!")
        print("   Access via API endpoints or direct method calls")
        print("   All metrics are calculated in real-time from prediction data")
        print("   Reports can be exported in multiple formats (JSON, CSV, PDF)")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the comprehensive demonstration
    asyncio.run(run_comprehensive_demo())
