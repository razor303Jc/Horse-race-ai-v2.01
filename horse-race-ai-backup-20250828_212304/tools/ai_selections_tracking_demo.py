#!/usr/bin/env python3
"""
AI Selections Tracking Demo
===========================

Demonstration of the comprehensive AI horse selections tracking system
with profit/loss ROI and contextual analysis.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our tracking systems
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from horse_racing_ai.analytics.ai_selections_tracker import AISelectionsTracker
    from horse_racing_ai.integration.ai_selections_integration import (
        AISelectionsIntegrationSystem,
    )
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Please ensure you're running from the project root directory")
    exit(1)


def create_sample_race_data():
    """Create sample race data for demonstration."""
    return {
        "race_id": "DEMO_2025-08-20_R1",
        "race_date": "2025-08-20T14:30:00Z",
        "course": "Newmarket",
        "race_number": 1,
        "race_time": "14:30",
        "distance": 6.0,
        "class": "Class 2",
        "field_size": 8,
        "weather": "Clear",
        "track_condition": "Good",
        "pace_scenario": "Moderate",
    }


def create_sample_ai_predictions():
    """Create sample AI predictions for demonstration."""
    return {
        "consensus": [
            {
                "horse_name": "Thunder Strike",
                "horse_id": "TS001",
                "jockey": "James Doyle",
                "trainer": "Charlie Appleby",
                "win_probability": 0.35,
                "place_probability": 0.65,
                "confidence_score": 0.78,
                "odds_decimal": 3.5,
                "odds_fractional": "5/2",
                "market_rank": 2,
                "selection_type": "WIN",
                "stake_amount": 15.0,
                "weight": 59.0,
                "draw": 4,
            },
            {
                "horse_name": "Speed Demon",
                "horse_id": "SD002",
                "jockey": "Ryan Moore",
                "trainer": "Aidan O'Brien",
                "win_probability": 0.28,
                "place_probability": 0.58,
                "confidence_score": 0.72,
                "odds_decimal": 4.2,
                "odds_fractional": "16/5",
                "market_rank": 3,
                "selection_type": "WIN",
                "stake_amount": 12.0,
                "weight": 58.5,
                "draw": 7,
            },
        ],
        "ai_ml": [
            {
                "horse_name": "Lightning Bolt",
                "horse_id": "LB003",
                "jockey": "William Buick",
                "trainer": "John Gosden",
                "win_probability": 0.42,
                "place_probability": 0.72,
                "confidence_score": 0.85,
                "odds_decimal": 2.8,
                "odds_fractional": "9/5",
                "market_rank": 1,
                "selection_type": "WIN",
                "stake_amount": 20.0,
                "weight": 60.0,
                "draw": 2,
            }
        ],
    }


def create_sample_race_results():
    """Create sample race results for demonstration."""
    return [
        {"horse_name": "Lightning Bolt", "position": 1, "margin": 0.0},
        {"horse_name": "Thunder Strike", "position": 2, "margin": 1.5},
        {"horse_name": "Speed Demon", "position": 4, "margin": 3.2},
        {"horse_name": "Dark Horse", "position": 3, "margin": 2.8},
    ]


def create_sample_betting_results():
    """Create sample betting results for demonstration."""
    return [
        {
            "selection_id": "DEMO_2025-08-20_R1_Lightning Bolt_ai_ml",
            "horse_name": "Lightning Bolt",
            "stake": 20.0,
            "payout": 56.0,  # Won at 2.8/1
            "profit": 36.0,
        },
        {
            "selection_id": "DEMO_2025-08-20_R1_Thunder Strike_consensus",
            "horse_name": "Thunder Strike",
            "stake": 15.0,
            "payout": 15.75,  # Place payout (roughly 1/4 odds)
            "profit": 0.75,
        },
        {
            "selection_id": "DEMO_2025-08-20_R1_Speed Demon_consensus",
            "horse_name": "Speed Demon",
            "stake": 12.0,
            "payout": 0.0,  # Lost
            "profit": -12.0,
        },
    ]


def demonstrate_basic_tracking():
    """Demonstrate basic AI selections tracking."""
    print("\n🏇 AI Selections Tracking Demo")
    print("=" * 50)

    # Initialize tracker
    tracker = AISelectionsTracker("data/demo_ai_selections.db")

    # Sample data
    race_data = create_sample_race_data()
    ai_predictions = create_sample_ai_predictions()

    print("\n📊 Recording AI Selections...")

    # Record selections
    selection_ids = []
    for method, predictions in ai_predictions.items():
        for prediction in predictions:
            selection_id = tracker.record_ai_selection(
                race_data=race_data,
                selection_data=prediction,
                prediction_method=method,
                betting_strategy="value_bet",
            )
            selection_ids.append(selection_id)
            print(f"  ✅ Recorded: {prediction['horse_name']} ({method})")

    print(f"\n📈 Total selections recorded: {len(selection_ids)}")

    # Simulate race results
    print("\n🏁 Updating Race Results...")
    race_results = create_sample_race_results()
    betting_results = create_sample_betting_results()

    # Update results
    for selection_id in selection_ids:
        # Find corresponding result
        horse_name = selection_id.split("_")[3]  # Extract horse name

        race_result = next(
            (r for r in race_results if r["horse_name"] == horse_name), None
        )

        betting_result = next(
            (b for b in betting_results if b["horse_name"] == horse_name), None
        )

        if race_result:
            success = tracker.update_selection_result(
                selection_id, race_result, betting_result
            )
            if success:
                print(
                    f"  ✅ Updated: {horse_name} - Position {race_result['position']}"
                )

    # Get analytics
    print("\n📊 Analytics Summary:")
    analytics = tracker.get_selection_analytics()

    print(f"  Total Selections: {analytics.total_selections}")
    print(f"  Overall Accuracy: {analytics.overall_accuracy:.1%}")
    print(f"  ROI Percentage: {analytics.roi_percentage:.2f}%")
    print(f"  Net Profit: £{analytics.net_profit:.2f}")
    print(f"  Confidence Calibration: {analytics.confidence_calibration:.2f}")

    # Strategy performance
    if analytics.strategy_performance:
        print(f"\n🎯 Strategy Performance:")
        for strategy, performance in analytics.strategy_performance.items():
            print(
                f"  {strategy}: {performance['accuracy']:.1%} accuracy, "
                f"{performance['roi']:.2f}% ROI"
            )

    # Method performance
    if analytics.method_performance:
        print(f"\n🤖 Method Performance:")
        for method, performance in analytics.method_performance.items():
            print(
                f"  {method}: {performance['accuracy']:.1%} accuracy, "
                f"{performance['roi']:.2f}% ROI"
            )

    tracker.close()
    return analytics


def demonstrate_integration_system():
    """Demonstrate the integration system."""
    print("\n🔗 AI Selections Integration Demo")
    print("=" * 50)

    # Initialize integration system
    integration = AISelectionsIntegrationSystem(
        "data/demo_selections_integration.db", "data/demo_performance_integration.db"
    )

    # Sample data
    race_data = create_sample_race_data()
    ai_predictions = create_sample_ai_predictions()

    print("\n📊 Processing Race Predictions...")

    # Process predictions
    selection_ids = integration.process_race_predictions(
        race_data=race_data,
        ai_predictions=ai_predictions,
        betting_strategies=["value_bet", "80_20"],
    )

    print(
        f"  ✅ Processed selections for {len(selection_ids)} strategy/method combinations"
    )

    # Update with results
    print("\n🏁 Updating Race Results...")
    race_results = create_sample_race_results()
    betting_results = create_sample_betting_results()

    update_summary = integration.update_race_results(
        race_id="DEMO_2025-08-20_R1",
        actual_results=race_results,
        betting_results=betting_results,
    )

    print(f"  ✅ Updated {update_summary['selections_updated']} selections")
    print(f"  💰 Total profit impact: £{update_summary['total_profit_impact']:.2f}")

    # Get real-time performance
    print("\n⏱️ Real-time Performance:")
    performance = integration.get_real_time_performance()

    print(f"  System Status: {performance['status']}")
    print(f"  Today's Selections: {performance['today']['selections']}")
    print(f"  Today's ROI: {performance['today']['roi']:.2f}%")
    print(f"  Week's Selections: {performance['week']['selections']}")
    print(f"  Week's ROI: {performance['week']['roi']:.2f}%")

    integration.close()
    return performance


def demonstrate_contextual_analysis():
    """Demonstrate contextual analysis capabilities."""
    print("\n🔍 Contextual Analysis Demo")
    print("=" * 50)

    # Initialize tracker with some historical data
    tracker = AISelectionsTracker("data/demo_contextual_analysis.db")

    # Create multiple races with varied conditions
    races_data = [
        {
            "race_id": f"DEMO_2025-08-{20+i}_R{j+1}",
            "race_date": f"2025-08-{20+i}T{14+j}:30:00Z",
            "course": ["Newmarket", "Ascot", "York"][i % 3],
            "race_number": j + 1,
            "distance": [6.0, 8.0, 10.0][j % 3],
            "class": ["Class 1", "Class 2", "Class 3"][i % 3],
            "field_size": 8 + (i % 5),
            "weather": ["Clear", "Overcast", "Rain"][i % 3],
            "track_condition": ["Good", "Soft", "Heavy"][i % 3],
        }
        for i in range(3)
        for j in range(2)
    ]

    print(f"\n📊 Creating {len(races_data)} historical races...")

    selection_count = 0
    for race_data in races_data:
        # Create varied selections for each race
        for horse_num in range(2):  # 2 selections per race
            selection_data = {
                "horse_name": f'Horse_{race_data["race_id"]}_{horse_num}',
                "win_probability": 0.2 + (horse_num * 0.3),
                "confidence_score": 0.6 + (horse_num * 0.2),
                "odds_decimal": 3.0 + horse_num,
                "selection_type": "WIN",
                "stake_amount": 10.0,
            }

            # Record selection
            selection_id = tracker.record_ai_selection(
                race_data, selection_data, "consensus", "value_bet"
            )

            # Simulate results (varied success rates by conditions)
            weather = race_data["weather"]
            success_prob = (
                0.4 if weather == "Clear" else (0.3 if weather == "Overcast" else 0.2)
            )

            position = 1 if (hash(selection_id) % 100) / 100 < success_prob else 4
            payout = selection_data["odds_decimal"] * 10.0 if position == 1 else 0.0

            # Update result
            tracker.update_selection_result(
                selection_id, {"position": position}, {"stake": 10.0, "payout": payout}
            )

            selection_count += 1

    print(f"  ✅ Created {selection_count} selections with varied results")

    # Generate contextual analysis
    print("\n🔍 Generating Contextual Analysis...")
    analysis = tracker.generate_contextual_analysis(period_days=30)

    if analysis["status"] == "insufficient_data":
        print(f"  ⚠️ {analysis['message']}")
    else:
        print(f"\n📈 Analysis Results:")
        summary = analysis["performance_summary"]
        print(f"  Performance Grade: {summary['grade']}")
        print(f"  Total Selections: {summary['total_selections']}")
        print(f"  Overall Accuracy: {summary['overall_accuracy']:.1%}")
        print(f"  ROI Percentage: {summary['roi_percentage']:.2f}%")

        # Market intelligence
        market = analysis["market_intelligence"]
        print(f"\n💹 Market Intelligence:")
        print(f"  Average Odds: {market['average_odds']:.2f}")
        print(f"  Overlay Rate: {market['overlay_rate']:.1f}%")
        print(f"  Value Capture Rate: {market['value_capture_rate']:.1f}%")

        # Recommendations
        print(f"\n💡 Recommendations:")
        for rec in analysis["recommendations"][:3]:
            print(f"  • {rec}")

    tracker.close()
    return analysis


def demonstrate_export_capabilities():
    """Demonstrate data export capabilities."""
    print("\n💾 Data Export Demo")
    print("=" * 50)

    tracker = AISelectionsTracker("data/demo_export.db")

    # Create some sample data
    race_data = create_sample_race_data()
    ai_predictions = create_sample_ai_predictions()

    # Record selections
    for method, predictions in ai_predictions.items():
        for prediction in predictions:
            selection_id = tracker.record_ai_selection(
                race_data, prediction, method, "value_bet"
            )

            # Add result
            position = 1 if prediction["horse_name"] == "Lightning Bolt" else 3
            payout = (
                prediction["odds_decimal"] * prediction["stake_amount"]
                if position == 1
                else 0
            )

            tracker.update_selection_result(
                selection_id,
                {"position": position},
                {"stake": prediction["stake_amount"], "payout": payout},
            )

    # Export data in different formats
    print("\n📤 Exporting Data...")

    csv_file = tracker.export_selection_data(format_type="csv")
    print(f"  ✅ CSV Export: {csv_file}")

    json_file = tracker.export_selection_data(format_type="json")
    print(f"  ✅ JSON Export: {json_file}")

    excel_file = tracker.export_selection_data(format_type="excel")
    print(f"  ✅ Excel Export: {excel_file}")

    # Show file sizes
    for file_path in [csv_file, json_file, excel_file]:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"    📊 {Path(file_path).name}: {size} bytes")

    tracker.close()
    return [csv_file, json_file, excel_file]


def main():
    """Main demonstration function."""
    print("🎯 AI Horse Selections Tracking System Demo")
    print("=" * 70)
    print("This demo showcases comprehensive AI selection tracking with")
    print("profit/loss ROI and contextual analysis capabilities.")

    try:
        # Create data directory
        Path("data").mkdir(exist_ok=True)

        # Run demonstrations
        basic_analytics = demonstrate_basic_tracking()
        integration_performance = demonstrate_integration_system()
        contextual_analysis = demonstrate_contextual_analysis()
        export_files = demonstrate_export_capabilities()

        # Summary
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("✅ Basic tracking system demonstrated")
        print("✅ Integration system demonstrated")
        print("✅ Contextual analysis demonstrated")
        print("✅ Data export capabilities demonstrated")

        print(f"\n📊 Demo Results Summary:")
        print(f"  Basic Analytics ROI: {basic_analytics.roi_percentage:.2f}%")
        print(f"  Integration System Status: {integration_performance['status']}")
        print(f"  Export Files Created: {len(export_files)}")

        print(f"\n📁 Generated Files:")
        demo_files = [
            "data/demo_ai_selections.db",
            "data/demo_selections_integration.db",
            "data/demo_performance_integration.db",
            "data/demo_contextual_analysis.db",
            "data/demo_export.db",
        ]

        for file_path in demo_files:
            if Path(file_path).exists():
                print(f"  📄 {file_path}")

        for export_file in export_files:
            if Path(export_file).exists():
                print(f"  📊 {export_file}")

        print(f"\n🚀 The AI selections tracking system is ready for production use!")
        print("   You can now track AI selections with profit/loss ROI and")
        print("   comprehensive contextual analysis for AI improvement.")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        print("Please check the error logs and ensure all dependencies are installed.")


if __name__ == "__main__":
    main()
