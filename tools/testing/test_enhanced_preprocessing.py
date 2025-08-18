#!/usr/bin/env python3
"""
Test Enhanced Preprocessing Pipeline
Quick test of the new preprocessing features
"""

import sys
from pathlib import Path

import pandas as pd

# Add the tools directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.enhanced_preprocessing_pipeline import EnhancedDataPreprocessor


def test_preprocessing():
    """Test the preprocessing pipeline with sample data"""

    print("🧪 TESTING ENHANCED PREPROCESSING PIPELINE")
    print("=" * 50)

    # Create test data with common issues
    test_data = {
        "percentage_col": ["85%", "90%", "", "-", "100%"],
        "currency_col": ["£6,281", "$1,000.50", "£28,010", "", "-"],
        "distance_col": ["1m 2f 5y", "6f", "1m", "-", "5f 100y"],
        "weight_col": ["9-7", "8-12", "10-0", "", "-"],
        "odds_col": ["5/1", "7/2", "1/2", "evens", "-"],
        "integer_col": [123, 456, "", "-", "NULL"],
        "string_col": ["Horse Name", "Another Horse", "", "-", "NULL"],
    }

    df = pd.DataFrame(test_data)
    print("📊 Original test data:")
    print(df)
    print(f"Data types: {dict(df.dtypes)}")

    # Expected results info
    print("\n📝 Expected conversions:")
    print("• percentage_col: '85%' → 0.85")
    print("• currency_col: '£6,281' → 6281.0")
    print("• distance_col: '6f' → 1207.0 meters (6 × 201.168)")
    print("• weight_col: '9-7' → 9.7")
    print("• integer_col: '' → 0")
    print("• string_col: '' → None")

    # Initialize preprocessor
    preprocessor = EnhancedDataPreprocessor()

    # Preprocess the data
    print("\n🧹 Preprocessing...")
    preprocessed_df = preprocessor.preprocess_dataframe(df, "test_data")

    print("\n✅ Preprocessed data:")
    print(preprocessed_df)
    print(f"Data types: {dict(preprocessed_df.dtypes)}")

    # Show specific cleaning examples
    print("\n🔍 CLEANING EXAMPLES:")
    print("-" * 30)

    for col in df.columns:
        original = df[col].tolist()
        cleaned = preprocessed_df[col].tolist()
        print(f"{col}:")
        for i, (orig, clean) in enumerate(zip(original, cleaned)):
            print(f"  {orig} → {clean}")
        print()

    # Show statistics
    preprocessor.print_preprocessing_summary()


if __name__ == "__main__":
    test_preprocessing()
