#!/usr/bin/env python3
"""
Horse Data Duplicate and Anomaly Analysis
Checks for duplicate horses and unusual ages in the database
"""

from datetime import date, datetime

import pandas as pd
import psycopg2


def get_db_connection():
    """Get database connection with correct credentials"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def analyze_horse_duplicates():
    """Analyze horses for duplicates and age anomalies"""
    print("🔍 ANALYZING HORSE DATA FOR DUPLICATES AND AGE ANOMALIES")
    print("=" * 60)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Check for duplicate horse names
        print("\n📋 1. DUPLICATE HORSE NAMES:")
        print("-" * 40)

        cursor.execute(
            """
            SELECT horse_name, COUNT(*) as count, 
                   STRING_AGG(DISTINCT CAST(id AS TEXT), ', ') as horse_ids,
                   STRING_AGG(DISTINCT CAST(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled) AS TEXT), ', ') as ages,
                   STRING_AGG(DISTINCT sire, ', ') as sires,
                   STRING_AGG(DISTINCT dam, ', ') as dams
            FROM horses 
            WHERE horse_name IS NOT NULL
            GROUP BY horse_name 
            HAVING COUNT(*) > 1
            ORDER BY count DESC, horse_name;
        """
        )

        duplicates = cursor.fetchall()
        if duplicates:
            print(f"Found {len(duplicates)} horses with duplicate names:")
            for row in duplicates:
                name, count, ids, ages, sires, dams = row
                print(f"  • {name}: {count} entries")
                print(f"    IDs: {ids}")
                print(f"    Ages: {ages}")
                print(f"    Sires: {sires}")
                print(f"    Dams: {dams}")
                print()
        else:
            print("✅ No duplicate horse names found!")

        # 2. Check for unusual ages
        print("\n🎂 2. AGE DISTRIBUTION ANALYSIS:")
        print("-" * 40)

        cursor.execute(
            """
            SELECT 
                EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled) as age, 
                COUNT(*) as count,
                STRING_AGG(horse_name, ', ' ORDER BY horse_name) as horses
            FROM horses 
            WHERE foaled IS NOT NULL
            GROUP BY EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled)
            ORDER BY age DESC;
        """
        )

        age_data = cursor.fetchall()
        print("Age distribution:")
        unusual_ages = []

        for age, count, horses in age_data:
            status = ""
            if age > 15:
                status = " ⚠️  VERY OLD"
                unusual_ages.append((age, count, horses))
            elif age > 10:
                status = " 🔶 OLD"
            elif age < 2:
                status = " 🐴 VERY YOUNG"
                unusual_ages.append((age, count, horses))

            print(f"  Age {age}: {count} horses{status}")
            if len(horses) < 200:  # Only show individual horses for smaller groups
                print(f"    Horses: {horses}")

        # 3. Focus on very unusual ages
        if unusual_ages:
            print(f"\n⚠️  3. HORSES WITH UNUSUAL AGES:")
            print("-" * 40)

            for age, count, horses in unusual_ages:
                if age > 15 or age < 2:
                    print(f"\n🚨 Age {age} ({count} horses):")
                    horse_list = horses.split(", ")
                    for i, horse in enumerate(horse_list[:10]):  # Show first 10
                        print(f"  {i+1}. {horse}")
                    if len(horse_list) > 10:
                        print(f"  ... and {len(horse_list) - 10} more")

        # 4. Check for horses with same name but different breeding
        print(f"\n🧬 4. HORSES WITH IDENTICAL NAMES BUT DIFFERENT BREEDING:")
        print("-" * 60)

        cursor.execute(
            """
            SELECT horse_name, COUNT(DISTINCT CONCAT(sire, '|', dam)) as breeding_variants,
                   STRING_AGG(DISTINCT CONCAT(sire, ' x ', dam), ' | ') as breeding_combinations,
                   COUNT(*) as total_entries
            FROM horses 
            WHERE sire IS NOT NULL AND dam IS NOT NULL
            GROUP BY horse_name 
            HAVING COUNT(DISTINCT CONCAT(sire, '|', dam)) > 1
            ORDER BY breeding_variants DESC, horse_name;
        """
        )

        breeding_issues = cursor.fetchall()
        if breeding_issues:
            print(f"Found {len(breeding_issues)} horses with name conflicts:")
            for name, variants, combinations, total in breeding_issues:
                print(f"\n  • {name} ({variants} different breeding combinations):")
                print(f"    Breeding: {combinations}")
                print(f"    Total entries: {total}")
        else:
            print("✅ No breeding conflicts found!")

        # 5. Statistical summary
        print("\n📊 5. STATISTICAL SUMMARY:")
        print("-" * 40)

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_horses,
                COUNT(DISTINCT horse_name) as unique_names,
                MIN(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled)) as min_age,
                MAX(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled)) as max_age,
                ROUND(AVG(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled)), 1) as avg_age,
                COUNT(*) - COUNT(DISTINCT horse_name) as name_duplicates
            FROM horses 
            WHERE foaled IS NOT NULL;
        """
        )

        stats = cursor.fetchone()
        total, unique_names, min_age, max_age, avg_age, name_dups = stats

        print(f"Total horse records: {total}")
        print(f"Unique horse names: {unique_names}")
        print(f"Name duplicates: {name_dups}")
        print(f"Age range: {min_age} - {max_age} years")
        print(f"Average age: {avg_age} years")

        # 6. Check for specific age 22
        print("\n🎯 6. HORSES AGED 22 (AS REQUESTED):")
        print("-" * 40)

        cursor.execute(
            """
            SELECT id, horse_name, 
                   EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled) as age,
                   foaled, sire, dam, trainer, owner
            FROM horses 
            WHERE EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM foaled) = 22
            ORDER BY horse_name;
        """
        )

        age_22_horses = cursor.fetchall()
        if age_22_horses:
            print(f"Found {len(age_22_horses)} horses aged 22:")
            for horse_id, name, age, foaled, sire, dam, trainer, owner in age_22_horses:
                print(f"  • ID {horse_id}: {name} (age {age}, foaled {foaled})")
                print(f"    Breeding: {sire} x {dam}")
                print(f"    Trainer: {trainer}")
                print(f"    Owner: {owner}")
                print()
        else:
            print("✅ No horses aged 22 found!")

    except Exception as e:
        print(f"❌ Error analyzing horse data: {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    analyze_horse_duplicates()
