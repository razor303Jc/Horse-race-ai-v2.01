#!/usr/bin/env python3
"""
Weight Conversion Module - Fix Critical Weight Mapping Issue
Convert UK horse racing weights (stones-pounds) to kilograms

Handles formats like:
- "10-2" -> 10 stones 2 pounds -> 64.4 kg
- "9-7" -> 9 stones 7 pounds -> 60.3 kg
- "8-12" -> 8 stones 12 pounds -> 56.7 kg
"""

import re
import pandas as pd
import psycopg2
from typing import Optional


class WeightConverter:
    """Convert UK racing weights to kilograms"""

    # Standard conversions
    STONE_TO_KG = 6.35029318  # 1 stone = 6.35029318 kg
    POUND_TO_KG = 0.45359237  # 1 pound = 0.45359237 kg
    POUNDS_PER_STONE = 14  # 14 pounds per stone

    def __init__(self):
        # Regex pattern for UK weight format "stones-pounds"
        self.uk_weight_pattern = re.compile(r"(\d+)[.-](\d+)")

    def convert_uk_to_kg(self, weight_str: str) -> Optional[float]:
        """Convert UK weight format to kilograms"""
        if not weight_str or pd.isna(weight_str):
            return None

        weight_str = str(weight_str).strip()

        # Handle empty or invalid strings
        if not weight_str or weight_str in ["", "nan", "null", "0", "0.0"]:
            return None

        try:
            # Check for UK format "10-2" or "10.2"
            match = self.uk_weight_pattern.search(weight_str)
            if match:
                stones = int(match.group(1))
                pounds = int(match.group(2))

                # Validate reasonable ranges
                if stones < 6 or stones > 12:  # Racing weights typically 6-12 stones
                    print(f"⚠️ Unusual stone weight: {stones}")
                if pounds >= 14:  # Pounds should be 0-13
                    print(f"⚠️ Invalid pounds (>=14): {pounds}")
                    return None

                # Convert to kg: (stones * 14 + pounds) * pound_to_kg
                total_pounds = (stones * self.POUNDS_PER_STONE) + pounds
                kg = total_pounds * self.POUND_TO_KG
                return round(kg, 2)

            # If it's already a decimal number, check if it needs conversion
            try:
                value = float(weight_str)
                # If value is in UK decimal format (like 10.2 for 10st 2lb)
                if 6 <= value <= 12 and "." in weight_str:
                    stones = int(value)
                    pounds = int(
                        (value - stones) * 14
                    )  # Convert decimal part to pounds
                    total_pounds = (stones * self.POUNDS_PER_STONE) + pounds
                    kg = total_pounds * self.POUND_TO_KG
                    return round(kg, 2)
                # If already in kg (reasonable range 40-80kg)
                elif 40 <= value <= 80:
                    return value
                else:
                    print(f"⚠️ Unrecognized weight value: {value}")
                    return None
            except ValueError:
                print(f"⚠️ Invalid weight format: '{weight_str}'")
                return None

        except Exception as e:
            print(f"❌ Error converting weight '{weight_str}': {e}")
            return None

    def get_weight_category(self, kg: float) -> str:
        """Categorize weight for analysis"""
        if kg < 50:
            return "Light"
        elif kg < 55:
            return "Medium-Light"
        elif kg < 60:
            return "Medium"
        elif kg < 65:
            return "Medium-Heavy"
        else:
            return "Heavy"

    def test_conversions(self):
        """Test weight conversion patterns"""
        test_cases = [
            ("10-2", 64.4),  # 10 stone 2 pounds
            ("9-7", 60.3),  # 9 stone 7 pounds
            ("8-12", 56.7),  # 8 stone 12 pounds
            ("11-5", 72.1),  # 11 stone 5 pounds
            ("10.2", 64.4),  # Decimal format
            ("9.7", 60.3),  # Decimal format
        ]

        print("🧪 Testing Weight Conversions:")
        for weight_str, expected in test_cases:
            result = self.convert_uk_to_kg(weight_str)
            if result:
                diff = abs(result - expected)
                status = "✅" if diff < 0.5 else "❌"
                print(
                    f"  {status} '{weight_str}' -> {result}kg (expected: {expected}kg)"
                )
            else:
                print(f"  ❌ '{weight_str}' -> Failed to convert")

        return True


def fix_record_weights():
    """Fix all weight data in the records table"""
    converter = WeightConverter()

    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        port="5434",
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )
    cursor = conn.cursor()

    print("🔧 Fixing Record Weights...")

    # Get all records with weight data
    cursor.execute(
        "SELECT id, weight, weight_uk FROM records WHERE weight IS NOT NULL OR weight_uk IS NOT NULL"
    )
    records = cursor.fetchall()

    print(f"📊 Processing {len(records)} weight records...")

    updated_count = 0
    errors = []

    for record_id, current_weight, current_weight_uk in records:
        # Determine which field to convert from
        source_weight = None
        if current_weight_uk and current_weight_uk != 0:
            source_weight = str(current_weight_uk)
        elif current_weight and current_weight != 0:
            # Check if current weight looks like it needs conversion
            if 6 <= float(current_weight) <= 12:  # Likely in UK format
                source_weight = str(current_weight)

        if source_weight:
            # Convert to kg
            weight_kg = converter.convert_uk_to_kg(source_weight)

            if weight_kg:
                # Add new column if it doesn't exist
                try:
                    cursor.execute(
                        """
                        ALTER TABLE records 
                        ADD COLUMN IF NOT EXISTS weight_kg NUMERIC,
                        ADD COLUMN IF NOT EXISTS weight_category TEXT
                    """
                    )
                    conn.commit()
                except:
                    pass  # Column might already exist

                # Update record with converted weight
                category = converter.get_weight_category(weight_kg)
                cursor.execute(
                    """
                    UPDATE records 
                    SET weight_kg = %s, weight_category = %s 
                    WHERE id = %s
                """,
                    (weight_kg, category, record_id),
                )

                updated_count += 1

                if updated_count <= 5:  # Show first 5 conversions
                    print(
                        f"  ✅ Record {record_id}: '{source_weight}' -> {weight_kg}kg ({category})"
                    )
            else:
                errors.append(f"Record {record_id}: '{source_weight}'")

    conn.commit()

    print(f"\n📊 Weight Conversion Results:")
    print(f"  - Successfully converted: {updated_count}")
    print(f"  - Errors: {len(errors)}")

    if errors and len(errors) <= 10:
        print("❌ Failed conversions:")
        for error in errors[:10]:
            print(f"  - {error}")

    conn.close()
    return updated_count, len(errors)


if __name__ == "__main__":
    converter = WeightConverter()

    # Test the converter
    converter.test_conversions()

    # Fix database weights
    print("\n" + "=" * 50)
    fixed, errors = fix_record_weights()

    if errors == 0:
        print("✅ All weights converted successfully!")
    else:
        print(f"⚠️ Completed with {errors} errors - manual review needed")
