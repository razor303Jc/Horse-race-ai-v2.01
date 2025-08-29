#!/usr/bin/env python3
"""
Complete Strategy Integration Demo
=================================

This script demonstrates the complete integration of 80/20 and Dutching betting
strategies into the ML models and AI selections system.

The demo shows:
1. How ML models are made aware of betting strategies
2. How strategy recommendations are integrated into AI predictions
3. How to use the enhanced system for real race analysis
4. Performance tracking and optimization

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("strategy_integration_demo.log"),
    ],
)

logger = logging.getLogger(__name__)

# Add project path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import our new strategy-aware components
    from src.horse_racing_ai.integration.strategy_aware_ml_hub import (
        StrategyAwareMLIntegrationHub,
        StrategyAwareAIResult,
    )
    from src.horse_racing_ai.integration.strategy_enhanced_ai_selections import (
        StrategyEnhancedAIGenerator,
        StrategyAwareSelection,
    )
    from src.horse_racing_ai.ml.strategy_integrated_ml import (
        StrategyIntegratedMLSystem,
        BettingStrategyMLClassifier,
    )
    from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem

    logger.info("✅ Successfully imported strategy-aware components")

except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.info("Falling back to demonstration with mock components")


def create_sample_race_data():
    """Create comprehensive sample race data for demonstration"""

    race_data = {
        "race_id": "DEMO_2025_08_20_R001",
        "race_name": "Strategy Integration Stakes",
        "distance": "1600m",
        "class": "Class 2",
        "field_size": 10,
        "prize_money": 50000,
        "track_condition": "Good",
        "weather": "Fine",
    }

    horses_data = [
        {
            "name": "Eighty Twenty Star",
            "jockey": "A. Champion",
            "weight": 58.0,
            "form": "1112",
            "recent_form_score": 92,
            "speed_rating": 105,
            "class_rating": 88,
            "win_probability": 0.35,
            "place_probability": 0.65,
        },
        {
            "name": "Value Seeker",
            "jockey": "B. Expert",
            "weight": 57.0,
            "form": "2131",
            "recent_form_score": 85,
            "speed_rating": 98,
            "class_rating": 82,
            "win_probability": 0.18,
            "place_probability": 0.45,
        },
        {
            "name": "Dutch Courage",
            "jockey": "C. Master",
            "weight": 56.5,
            "form": "3211",
            "recent_form_score": 88,
            "speed_rating": 102,
            "class_rating": 85,
            "win_probability": 0.22,
            "place_probability": 0.52,
        },
        {
            "name": "Perfect Place",
            "jockey": "D. Ace",
            "weight": 56.0,
            "form": "1324",
            "recent_form_score": 80,
            "speed_rating": 95,
            "class_rating": 78,
            "win_probability": 0.12,
            "place_probability": 0.38,
        },
        {
            "name": "Long Shot Hero",
            "jockey": "E. Rider",
            "weight": 55.5,
            "form": "4512",
            "recent_form_score": 75,
            "speed_rating": 88,
            "class_rating": 72,
            "win_probability": 0.08,
            "place_probability": 0.28,
        },
    ]

    betting_odds = {
        "Eighty Twenty Star": 2.8,  # Short odds - perfect for 80/20
        "Value Seeker": 5.5,  # Medium odds - value opportunity
        "Dutch Courage": 4.2,  # Good for dutching
        "Perfect Place": 8.5,  # Long odds with place value
        "Long Shot Hero": 15.0,  # Very long odds - 80/20 place potential
    }

    return race_data, horses_data, betting_odds


def demonstrate_ml_strategy_awareness():
    """Demonstrate how ML models become aware of betting strategies"""

    print("=" * 80)
    print("🤖 ML STRATEGY AWARENESS DEMONSTRATION")
    print("=" * 80)

    try:
        # Create strategy classifier
        strategy_classifier = BettingStrategyMLClassifier()

        print("1. Creating Strategy-Aware Features...")

        # Sample horse data for feature engineering
        sample_horse = {
            "name": "Demo Horse",
            "win_probability": 0.25,
            "place_probability": 0.55,
            "form_consistency": 0.8,
            "recent_placings_ratio": 0.6,
        }

        sample_race = {"field_size": 12, "class_rating": 85, "prize_money": 40000}

        sample_odds = {"Demo Horse": {"win": 3.5, "place": 1.2}}

        # Generate strategy features
        features = strategy_classifier.feature_engineering.create_strategy_features(
            sample_horse, sample_race, sample_odds
        )

        print("   ✅ Strategy-aware features generated:")
        for feature_name, value in list(features.items())[:8]:  # Show first 8
            print(f"      {feature_name}: {value:.3f}")
        print(f"      ... and {len(features)-8} more features")

        print("\n2. Strategy Suitability Analysis...")

        # Analyze strategy suitability
        eighty_twenty_pred, dutching_pred = (
            strategy_classifier._get_default_predictions(
                sample_horse, sample_race, sample_odds
            )
        )

        print(f"   🎯 80/20 Strategy:")
        print(f"      Recommended: {eighty_twenty_pred.recommended}")
        print(f"      Confidence: {eighty_twenty_pred.confidence:.1%}")
        print(f"      Expected ROI: {eighty_twenty_pred.expected_roi:.1f}%")
        print(f"      Risk Level: {eighty_twenty_pred.risk_level}")

        print(f"   🎲 Dutching Strategy:")
        print(f"      Recommended: {dutching_pred.recommended}")
        print(f"      Confidence: {dutching_pred.confidence:.1%}")
        print(f"      Expected ROI: {dutching_pred.expected_roi:.1f}%")
        print(f"      Risk Level: {dutching_pred.risk_level}")

        return True

    except Exception as e:
        logger.error(f"Error in ML strategy awareness demo: {e}")
        return False


def demonstrate_strategy_enhanced_selections():
    """Demonstrate strategy-enhanced AI selections"""

    print("\n" + "=" * 80)
    print("🎯 STRATEGY-ENHANCED AI SELECTIONS")
    print("=" * 80)

    try:
        # Create strategy-enhanced generator
        generator = StrategyEnhancedAIGenerator()

        print("1. Generating Strategy-Aware Selections...")

        # Get sample race data
        race_data, horses_data, betting_odds = create_sample_race_data()

        # Prepare race data for analysis
        enhanced_race_data = {
            **race_data,
            "horses": horses_data,
            "odds": {
                name: {"win": odds, "place": odds / 3}
                for name, odds in betting_odds.items()
            },
        }

        # Analyze race with strategies
        strategy_analysis = generator._analyze_race_with_strategies(enhanced_race_data)

        print(f"   ✅ Race Analysis Complete:")
        print(f"      Race: {strategy_analysis.race_id}")
        print(f"      Strategy Rating: {strategy_analysis.race_strategy_rating}")
        print(
            f"      Opportunity Score: {strategy_analysis.total_opportunity_score:.1f}/100"
        )
        print(f"      Recommended Approach: {strategy_analysis.recommended_approach}")

        print("\n2. Individual Horse Recommendations...")

        for i, selection in enumerate(strategy_analysis.strategy_selections[:3], 1):
            print(f"   {i}. {selection.horse_name}")
            print(f"      Strategy: {selection.recommended_strategy}")
            print(f"      Confidence: {selection.confidence_tier}")
            print(f"      Expected ROI: {selection.expected_strategy_roi:.1f}%")
            print(f"      Optimal Stake: {selection.optimal_stake_percentage:.1%}")
            print(f"      Advice: {selection.betting_advice}")
            print()

        print("3. Best Strategy Opportunities...")

        if strategy_analysis.best_eighty_twenty_selections:
            print("   🎯 Top 80/20 Selections:")
            for i, selection in enumerate(
                strategy_analysis.best_eighty_twenty_selections, 1
            ):
                print(
                    f"      {i}. {selection.horse_name} - ROI: {selection.expected_strategy_roi:.1f}%"
                )

        if strategy_analysis.best_dutching_combinations:
            print("   🎲 Dutching Combinations:")
            for i, combination in enumerate(
                strategy_analysis.best_dutching_combinations, 1
            ):
                horses = [s.horse_name for s in combination]
                print(f"      {i}. {' + '.join(horses)}")

        return strategy_analysis

    except Exception as e:
        logger.error(f"Error in strategy-enhanced selections demo: {e}")
        return None


def demonstrate_complete_integration():
    """Demonstrate the complete strategy-aware integration system"""

    print("\n" + "=" * 80)
    print("🚀 COMPLETE STRATEGY INTEGRATION")
    print("=" * 80)

    try:
        # Create integration hub
        hub = StrategyAwareMLIntegrationHub(
            initial_bankroll=10000.0, strategy_confidence_threshold=0.7
        )

        print("1. Initializing Enhanced ML System...")

        # Create and set enhanced ML system
        enhanced_ml = EnhancedMLRatingSystem(enable_neural_networks=True)
        hub.set_enhanced_ml_system(enhanced_ml)

        print("   ✅ Enhanced ML system integrated")

        print("\n2. Analyzing Race with Complete Integration...")

        # Get sample race data
        race_data, horses_data, betting_odds = create_sample_race_data()

        # Analyze with complete integration
        result = hub.analyze_race_with_strategy_integration(
            race_data, horses_data, betting_odds
        )

        print("   ✅ Complete analysis finished")

        print("\n3. Strategy-Aware Results:")
        print(f"   Primary Strategy: {result.primary_strategy_recommendation}")
        print(f"   Strategy Confidence: {result.strategy_confidence_score:.1%}")
        print(f"   Expected ROI: {result.expected_combined_roi:.1f}%")
        print(f"   Success Probability: {result.success_probability:.1%}")
        print(f"   Profit Expectation: ${result.profit_expectation:.2f}")

        if result.recommended_stakes:
            print("\n4. Recommended Stakes:")
            for horse, stake_info in result.recommended_stakes.items():
                print(f"   {horse}:")
                print(f"      Strategy: {stake_info['strategy']}")
                print(f"      Total Stake: {stake_info['total_stake']:.1%}")
                if stake_info.get("win_stake", 0) > 0:
                    print(f"      Win: {stake_info['win_stake']:.1%}")
                if stake_info.get("place_stake", 0) > 0:
                    print(f"      Place: {stake_info['place_stake']:.1%}")

        print("\n5. Bankroll Allocation:")
        for category, percentage in result.risk_adjusted_allocation.items():
            print(f"   {category.replace('_', ' ').title()}: {percentage:.1%}")

        # Export detailed analysis
        print("\n6. Generating Detailed Report...")
        detailed_report = hub.export_strategy_aware_analysis(result, "detailed")

        # Save report to file
        report_file = f"strategy_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w") as f:
            f.write(detailed_report)

        print(f"   ✅ Detailed report saved to: {report_file}")

        return hub, result

    except Exception as e:
        logger.error(f"Error in complete integration demo: {e}")
        return None, None


def demonstrate_performance_tracking():
    """Demonstrate performance tracking and optimization"""

    print("\n" + "=" * 80)
    print("📊 PERFORMANCE TRACKING & OPTIMIZATION")
    print("=" * 80)

    try:
        # Create integration hub
        hub = StrategyAwareMLIntegrationHub(initial_bankroll=10000.0)
        enhanced_ml = EnhancedMLRatingSystem(enable_neural_networks=True)
        hub.set_enhanced_ml_system(enhanced_ml)

        print("1. Simulating Multiple Race Analyses...")

        # Simulate analyzing multiple races
        for race_num in range(1, 6):
            race_data, horses_data, betting_odds = create_sample_race_data()
            race_data["race_id"] = f"DEMO_2025_08_20_R{race_num:03d}"

            # Analyze race
            result = hub.analyze_race_with_strategy_integration(
                race_data, horses_data, betting_odds
            )

            print(
                f"   Race {race_num}: {result.primary_strategy_recommendation} "
                f"(ROI: {result.expected_combined_roi:.1f}%)"
            )

        print("\n2. Performance Summary:")

        # Get performance summary
        performance = hub.get_strategy_performance_summary()

        print(f"   Total Races Analyzed: {performance['total_races_analyzed']}")
        print(f"   Average Confidence: {performance['average_confidence']:.1%}")
        print(f"   Average Expected ROI: {performance['average_expected_roi']:.1f}%")

        print("\n3. Strategy Performance Metrics:")
        for metric, value in performance["strategy_performance"].items():
            if isinstance(value, float):
                print(f"   {metric.replace('_', ' ').title()}: {value:.1%}")
            else:
                print(f"   {metric.replace('_', ' ').title()}: {value}")

        print("\n4. Recent Results:")
        for result in performance["recent_results"]:
            print(
                f"   {result['race_id']}: {result['primary_strategy']} "
                f"({result['confidence']:.0%}, {result['expected_roi']:.1f}% ROI)"
            )

        return performance

    except Exception as e:
        logger.error(f"Error in performance tracking demo: {e}")
        return None


def main():
    """Main demonstration function"""

    print("🎯 HORSE RACING AI - STRATEGY INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("This demo shows how 80/20 and Dutching betting strategies are")
    print("integrated into the ML models and AI selections system.")
    print("=" * 80)

    # Run demonstrations
    demos_passed = 0
    total_demos = 4

    # 1. ML Strategy Awareness
    if demonstrate_ml_strategy_awareness():
        demos_passed += 1

    # 2. Strategy-Enhanced Selections
    strategy_analysis = demonstrate_strategy_enhanced_selections()
    if strategy_analysis:
        demos_passed += 1

    # 3. Complete Integration
    hub, result = demonstrate_complete_integration()
    if hub and result:
        demos_passed += 1

    # 4. Performance Tracking
    performance = demonstrate_performance_tracking()
    if performance:
        demos_passed += 1

    # Summary
    print("\n" + "=" * 80)
    print("🏁 DEMONSTRATION SUMMARY")
    print("=" * 80)
    print(f"Demos Passed: {demos_passed}/{total_demos}")

    if demos_passed == total_demos:
        print("✅ ALL DEMONSTRATIONS SUCCESSFUL!")
        print("\nThe ML models are now aware of betting strategies and can:")
        print("   • Identify 80/20 strategy opportunities")
        print("   • Recognize dutching combinations")
        print("   • Provide strategy-specific confidence scores")
        print("   • Generate optimal stake recommendations")
        print("   • Track and optimize performance")

        print("\n🎯 INTEGRATION COMPLETE!")
        print("The system is ready for production use with strategy-aware predictions.")

    else:
        print("⚠️  Some demonstrations encountered issues.")
        print("Check the logs for detailed error information.")

    print(f"\nGenerated files:")
    print("   • strategy_integration_demo.log")
    if hub and result:
        print("   • strategy_integration_report_YYYYMMDD_HHMMSS.txt")


if __name__ == "__main__":
    main()
