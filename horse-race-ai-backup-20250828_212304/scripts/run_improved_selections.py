#!/usr/bin/env python3
"""
🚀 Run Improved AI Selections - Version 2.0
===========================================

Runs the improved AI selections generator with:
- Fixed duplicate selection bugs
- Real odds integration
- Enhanced value analysis
- Better feature engineering
- Improved confidence scoring
"""

from improved_ai_selections_generator import ImprovedAISelectionsGenerator


def main():
    print("🚀 IMPROVED AI RACING SELECTIONS V2.0")
    print("📅 August 20, 2025")
    print("=" * 50)

    # Initialize improved generator
    generator = ImprovedAISelectionsGenerator()

    # Load models
    print("🤖 Initializing Improved AI Selections Generator...")
    generator.load_models()

    print(f"✅ Advanced Models: {len(generator.advanced_models)} loaded")
    print(f"   Features: {len(generator.feature_columns)} metrics")
    print()

    # Run improved selections
    print("🚀 Running improved daily selections with real data...")
    success = generator.run_improved_selections()

    if success:
        print("\n✅ Improved AI selections completed!")
    else:
        print("\n❌ Improved AI selections failed!")


if __name__ == "__main__":
    main()
