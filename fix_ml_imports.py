#!/usr/bin/env python3
"""
ML Training Import Fix Script
============================

Fix all import path issues in ML training tests
"""

import re
from pathlib import Path


def fix_ml_training_imports():
    """Fix import paths in ML training tests"""

    test_file = Path("tests/unit/ml_training/test_ml_pipeline.py")

    print("🔧 Fixing ML Training Import Paths")
    print("=" * 50)

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False

    # Read the file
    with open(test_file, "r") as f:
        content = f.read()

    # Track changes
    changes = []

    # Fix patch decorators
    patch_fixes = [
        (
            r"@patch\('docker\.ml_training\.real_ml_training_pipeline\.joblib\.dump'\)",
            "@patch('joblib.dump')",
        ),
        (
            r"patch\('docker\.ml_training\.real_ml_training_pipeline\.RandomForestClassifier'\)",
            "patch('sklearn.ensemble.RandomForestClassifier')",
        ),
        (
            r"patch\('docker\.ml_training\.real_ml_training_pipeline\.LogisticRegression'\)",
            "patch('sklearn.linear_model.LogisticRegression')",
        ),
        (
            r"patch\('docker\.ml_training\.real_ml_training_pipeline\.train_test_split'\)",
            "patch('sklearn.model_selection.train_test_split')",
        ),
        (
            r"patch\('docker\.ml_training\.real_ml_training_pipeline\.psycopg2\.connect'\)",
            "patch('psycopg2.connect')",
        ),
        (
            r"patch\('docker\.ml_training\.real_ml_training_pipeline\.pd\.read_sql'\)",
            "patch('pandas.read_sql')",
        ),
    ]

    original_content = content

    for old_pattern, new_pattern in patch_fixes:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            changes.append(f"Fixed: {old_pattern} -> {new_pattern}")

    # Write back if changes were made
    if content != original_content:
        with open(test_file, "w") as f:
            f.write(content)

        print(f"✅ Fixed {len(changes)} import path issues:")
        for change in changes:
            print(f"  • {change}")

        return True
    else:
        print("ℹ️  No changes needed")
        return False


def main():
    """Main function"""
    success = fix_ml_training_imports()

    if success:
        print("\n🎉 ML Training import paths fixed!")
        print("Now testing the fixes...")

        # Test the import
        try:
            import sys

            sys.path.append(".")
            from docker.ml_training.real_ml_training_pipeline import (
                RealMLTrainingPipeline,
            )

            print("✅ Import test successful")
        except Exception as e:
            print(f"❌ Import test failed: {e}")
            return False

    return success


if __name__ == "__main__":
    main()
