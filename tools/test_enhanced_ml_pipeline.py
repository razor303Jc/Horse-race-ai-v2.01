#!/usr/bin/env python3
"""
Enhanced ML Pipeline Test Script
===============================

Test the enhanced ML pipeline integration with v2.01 ensemble approach.
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.ml.enhanced_ml_pipeline import EnhancedMLPipeline


def main():
    """Test the enhanced ML pipeline."""
    print("🚀 Testing Enhanced ML Pipeline Integration")
    print("=" * 60)

    try:
        # Initialize pipeline
        pipeline = EnhancedMLPipeline(
            models_dir=str(project_root / "models"),
            cache_dir=str(project_root / "ml_cache"),
            enable_ensemble=True,
        )

        # Override data directory for local testing
        pipeline._data_dir = str(project_root / "data/preprocessed")

        print("✅ Pipeline initialized")

        # Check initial status
        status = pipeline.get_model_status()
        print(f"📊 Initial status: {status['is_trained']}")

        # Train models
        print("\n🎯 Training enhanced models...")

        # Load data for training with correct path
        horses_df, target = pipeline.load_and_prepare_data(
            data_dir=str(project_root / "data/preprocessed")
        )

        training_results = pipeline.ensemble_predictor.train_ensemble(horses_df, target)

        print("✅ Training completed!")
        print("\n📈 Training Results Summary:")
        for model_name, metrics in training_results.items():
            if isinstance(metrics, dict) and "roc_auc" in metrics:
                print(
                    f"  {model_name}: AUC={metrics['roc_auc']:.4f}, Accuracy={metrics['accuracy']:.4f}"
                )

        # Test prediction
        print("\n🏁 Testing race prediction...")

        # Load sample data for prediction
        horses_df, _ = pipeline.load_and_prepare_data()
        sample_race = horses_df.sample(n=min(8, len(horses_df)), random_state=42)

        # Make prediction
        prediction_result = pipeline.predict_race(
            sample_race, race_id="INTEGRATION_TEST", include_confidence=True
        )

        print("✅ Prediction completed!")
        print(f"\n🏇 Race: {prediction_result['race_id']}")
        print(f"📊 Horses: {prediction_result['race_summary']['horse_count']}")
        print(
            f"🎯 High confidence: {prediction_result['race_summary']['high_confidence_predictions']}"
        )
        print(
            f"💰 Value bets: {prediction_result['race_summary']['value_bets_identified']}"
        )

        print("\n🏆 Top 3 Predictions:")
        for i, pred in enumerate(prediction_result["predictions"][:3], 1):
            print(f"  {i}. {pred['horse_name']}")
            print(f"     Ensemble: {pred['ensemble_probability']:.3f}")
            print(f"     Confidence: {pred['confidence']:.3f}")
            print(f"     Value bet: {pred['value_bet']}")

        # Show feature importance
        if "feature_importance" in prediction_result:
            print("\n🔍 Top 5 Features:")
            for feat in prediction_result["feature_importance"][:5]:
                print(f"  {feat['rank']}. {feat['feature']}: {feat['importance']:.4f}")

        # Export for production
        print("\n📦 Exporting for production...")
        production_path = pipeline.export_model_for_production()
        print(f"✅ Production model: {production_path}")

        # Compare with v2.01 archive (if available)
        print("\n🔄 Checking v2.01 compatibility...")
        archive_files = list(
            (project_root / "data/v2_01_archive").glob("ml_predictions_*.csv")
        )

        if archive_files:
            latest_archive = max(archive_files, key=lambda x: x.stat().st_mtime)
            comparison = pipeline.compare_with_v2_01_archive(str(latest_archive))

            if "error" not in comparison:
                print("✅ v2.01 compatibility check passed")
                print(f"📈 Archive records: {comparison['archive_records']}")
                print(f"🤖 Model compatibility: {comparison['model_compatibility']}")
            else:
                print(f"⚠️ Compatibility check failed: {comparison['error']}")
        else:
            print("ℹ️ No v2.01 archive found for comparison")

        # Final status
        final_status = pipeline.get_model_status()
        print(f"\n📊 Final Status:")
        print(f"  Trained: {final_status['is_trained']}")
        print(f"  Models: {len(final_status.get('ensemble_models', []))}")
        print(f"  Features: {final_status.get('feature_count', 0)}")
        print(f"  Last prediction: {final_status.get('last_prediction_time', 'None')}")

        print("\n🎉 Enhanced ML Pipeline integration test completed successfully!")

        # Save test results
        test_results = {
            "test_timestamp": pd.Timestamp.now().isoformat(),
            "training_results": training_results,
            "prediction_result": prediction_result,
            "final_status": final_status,
            "test_passed": True,
        }

        results_file = project_root / "enhanced_ml_test_results.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2, default=str)

        print(f"📄 Test results saved to {results_file}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
