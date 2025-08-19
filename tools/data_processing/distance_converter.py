#!/usr/bin/env python3
"""
Distance Conversion Module - Critical Data Mapping Fix
Convert UK horse racing distances to standardized formats

Handles formats like:
- "6f" -> 1200 meters
- "1m 2f" -> 1610 meters
- "7f 50y" -> 1449 meters
- "2m 4f 110y" -> 4389 meters
"""

import re
import pandas as pd
from typing import Optional


class DistanceConverter:
    """Convert UK horse racing distances to meters"""

    # Standard conversions
    FURLONG_TO_METERS = 201.168  # 1 furlong = 201.168 meters
    YARD_TO_METERS = 0.9144  # 1 yard = 0.9144 meters
    MILE_TO_METERS = 1609.344  # 1 mile = 1609.344 meters

    def __init__(self):
        # Regex patterns for different distance formats
        self.patterns = {
            # "1m 2f 50y" - miles, furlongs, yards
            "full": re.compile(r"(\d+)m\s*(\d+)f\s*(\d+)y"),
            # "1m 2f" - miles and furlongs
            "mile_furlong": re.compile(r"(\d+)m\s*(\d+)f"),
            # "2f 50y" - furlongs and yards
            "furlong_yard": re.compile(r"(\d+)f\s*(\d+)y"),
            # "6f" - furlongs only
            "furlong_only": re.compile(r"(\d+)f"),
            # "1m" - miles only
            "mile_only": re.compile(r"(\d+)m"),
            # "50y" - yards only
            "yard_only": re.compile(r"(\d+)y"),
        }

    def convert_to_meters(self, distance_str: str) -> Optional[float]:
        """Convert UK distance string to meters"""
        if not distance_str or pd.isna(distance_str):
            return None

        distance_str = str(distance_str).strip().lower()

        # Handle empty or invalid strings
        if not distance_str or distance_str in ["", "nan", "null"]:
            return None

        try:
            # Try full pattern first: "1m 2f 50y"
            match = self.patterns["full"].search(distance_str)
            if match:
                miles, furlongs, yards = map(int, match.groups())
                meters = (
                    miles * self.MILE_TO_METERS
                    + furlongs * self.FURLONG_TO_METERS
                    + yards * self.YARD_TO_METERS
                )
                return round(meters, 2)

            # Try mile + furlong: "1m 2f"
            match = self.patterns["mile_furlong"].search(distance_str)
            if match:
                miles, furlongs = map(int, match.groups())
                meters = miles * self.MILE_TO_METERS + furlongs * self.FURLONG_TO_METERS
                return round(meters, 2)

            # Try furlong + yard: "2f 50y"
            match = self.patterns["furlong_yard"].search(distance_str)
            if match:
                furlongs, yards = map(int, match.groups())
                meters = furlongs * self.FURLONG_TO_METERS + yards * self.YARD_TO_METERS
                return round(meters, 2)

            # Try furlong only: "6f"
            match = self.patterns["furlong_only"].search(distance_str)
            if match:
                furlongs = int(match.group(1))
                meters = furlongs * self.FURLONG_TO_METERS
                return round(meters, 2)

            # Try mile only: "1m"
            match = self.patterns["mile_only"].search(distance_str)
            if match:
                miles = int(match.group(1))
                meters = miles * self.MILE_TO_METERS
                return round(meters, 2)

            # Try yard only: "50y"
            match = self.patterns["yard_only"].search(distance_str)
            if match:
                yards = int(match.group(1))
                meters = yards * self.YARD_TO_METERS
                return round(meters, 2)

            # If it's already a number, assume it's in meters
            try:
                return float(distance_str)
            except ValueError:
                print(f"⚠️ Unrecognized distance format: '{distance_str}'")
                return None

        except Exception as e:
            print(f"❌ Error converting distance '{distance_str}': {e}")
            return None

    def get_distance_category(self, meters: float) -> str:
        """Categorize distance for analysis"""
        if meters < 1000:
            return "Sprint"
        elif meters < 1400:
            return "Short"
        elif meters < 2000:
            return "Mile"
        elif meters < 2800:
            return "Middle"
        elif meters < 4000:
            return "Long"
        else:
            return "Extended"

    def test_conversions(self):
        """Test various distance conversion patterns"""
        test_cases = [
            ("6f", 1207.01),  # 6 furlongs
            ("1m", 1609.34),  # 1 mile
            ("1m 2f", 2011.70),  # 1 mile 2 furlongs
            ("7f 50y", 1453.18),  # 7 furlongs 50 yards
            ("2m 4f", 4023.02),  # 2 miles 4 furlongs
            ("5f 212y", 1199.85),  # 5 furlongs 212 yards
            ("1m 4f 13y", 2422.59),  # 1 mile 4 furlongs 13 yards
        ]

        print("🧪 Testing Distance Conversions:")
        for distance_str, expected in test_cases:
            result = self.convert_to_meters(distance_str)
            status = "✅" if result and abs(result - expected) < 1 else "❌"
            print(f"  {status} '{distance_str}' -> {result}m (expected: {expected}m)")

        return True


def fix_race_distances():
    """Fix all race distances in the database"""
    import psycopg2

    converter = DistanceConverter()

    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        port="5434",
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )
    cursor = conn.cursor()

    print("🔧 Fixing Race Distances...")

    # Get all races with unconverted distances
    cursor.execute("SELECT id, race_id, distance FROM races WHERE distance IS NOT NULL")
    races = cursor.fetchall()

    print(f"📊 Processing {len(races)} races...")

    updated_count = 0
    errors = []

    for race_id, race_code, distance_str in races:
        # Convert distance to meters
        meters = converter.convert_to_meters(distance_str)

        if meters:
            # Add new columns if they don't exist
            try:
                cursor.execute(
                    """
                    ALTER TABLE races 
                    ADD COLUMN IF NOT EXISTS distance_meters NUMERIC,
                    ADD COLUMN IF NOT EXISTS distance_category TEXT
                """
                )
                conn.commit()
            except:
                pass  # Columns might already exist

            # Update race with converted distance
            category = converter.get_distance_category(meters)
            cursor.execute(
                """
                UPDATE races 
                SET distance_meters = %s, distance_category = %s 
                WHERE id = %s
            """,
                (meters, category, race_id),
            )

            updated_count += 1

            if updated_count <= 5:  # Show first 5 conversions
                print(
                    f"  ✅ Race {race_code}: '{distance_str}' -> {meters}m ({category})"
                )
        else:
            errors.append(f"Race {race_code}: '{distance_str}'")

    conn.commit()

    print(f"\n📊 Distance Conversion Results:")
    print(f"  - Successfully converted: {updated_count}")
    print(f"  - Errors: {len(errors)}")

    if errors and len(errors) <= 10:
        print("❌ Failed conversions:")
        for error in errors:
            print(f"  - {error}")

    conn.close()
    return updated_count, len(errors)


if __name__ == "__main__":
    converter = DistanceConverter()

    # Test the converter
    converter.test_conversions()

    # Fix database distances
    print("\n" + "=" * 50)
    fixed, errors = fix_race_distances()

    if errors == 0:
        print("✅ All distances converted successfully!")
    else:
        print(f"⚠️ Completed with {errors} errors - manual review needed")
