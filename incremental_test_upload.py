#!/usr/bin/env python3
"""
Incremental CSV Upload - Test each column group as we add them
Based on successful test patterns from git history
"""

import os

import pandas as pd
import psycopg2


def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def test_incremental_upload():
    """Upload data incrementally, testing each column group"""
    print("🧪 Incremental CSV Upload Testing")
    print("=" * 50)

    # Load CSV
    csv_file = "data/daily_downloads/results_data/racecard_details/racecard_details.csv"
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} rows")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear table
        cursor.execute("DELETE FROM records")
        print("🧹 Cleared records table")

        # Test Column Group 1: Basic required columns (we know these work)
        print("\n📝 Testing Group 1: Basic columns...")
        group1_mapping = {
            "id": "record_id",
            "race_id": "race_id",
            "Name": "horse",
            "Age": "age",
        }

        success_count = 0
        for i, row in df.head(5).iterrows():  # Test with first 5 rows
            try:
                values = []
                columns = []
                for csv_col, db_col in group1_mapping.items():
                    val = row[csv_col]
                    if pd.isna(val):
                        if db_col == "age":
                            val = 0
                        else:
                            val = "none"
                    columns.append(db_col)
                    values.append(val)

                sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
                cursor.execute(sql, values)
                success_count += 1
            except Exception as e:
                print(f"   ❌ Row {i} failed: {e}")
                break

        if success_count == 5:
            print(f"   ✅ Group 1 SUCCESS: {success_count}/5 rows")
            conn.commit()

            # Test Column Group 2: Add numeric columns
            print("\n📝 Testing Group 2: Add numeric columns...")
            cursor.execute("DELETE FROM records")  # Clear for next test

            group2_mapping = {
                "id": "record_id",
                "race_id": "race_id",
                "horse_number": "horse_number",
                "Draw": "draw",
                "Horse_ID": "horse_id",
                "Name": "horse",
                "Age": "age",
                "Horse_rate": "or_rating",
            }

            success_count = 0
            for i, row in df.head(5).iterrows():
                try:
                    values = []
                    columns = []
                    for csv_col, db_col in group2_mapping.items():
                        val = row[csv_col]
                        if pd.isna(val):
                            if db_col in [
                                "horse_number",
                                "draw",
                                "horse_id",
                                "age",
                                "or_rating",
                            ]:
                                val = 0
                            else:
                                val = "none"
                        columns.append(db_col)
                        values.append(val)

                    sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
                    cursor.execute(sql, values)
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ Row {i} failed: {e}")
                    break

            if success_count == 5:
                print(f"   ✅ Group 2 SUCCESS: {success_count}/5 rows")
                conn.commit()

                # Test Column Group 3: Add all remaining columns
                print("\n📝 Testing Group 3: Add all columns...")
                cursor.execute("DELETE FROM records")  # Clear for next test

                group3_mapping = {
                    "id": "record_id",
                    "race_id": "race_id",
                    "horse_number": "horse_number",
                    "Draw": "draw",
                    "Horse_ID": "horse_id",
                    "Country": "country",
                    "Name": "horse",
                    "Age": "age",
                    "weight_uk": "weight_uk",
                    "weight": "weight",
                    "gears": "gears",
                    "Horse_rate": "or_rating",
                    "jockey_ID": "jockey_id",
                    "jockey": "jockey",
                    "trainer_ID": "trainer_id",
                    "trainer": "trainer",
                    "fav": "fav",
                }

                success_count = 0
                for i, row in df.head(5).iterrows():
                    try:
                        values = []
                        columns = []
                        for csv_col, db_col in group3_mapping.items():
                            val = row[csv_col]
                            if pd.isna(val):
                                if db_col in [
                                    "horse_number",
                                    "draw",
                                    "horse_id",
                                    "age",
                                    "or_rating",
                                    "jockey_id",
                                    "trainer_id",
                                ]:
                                    val = 0
                                elif db_col in ["weight_uk", "weight"]:
                                    val = 0.0
                                else:
                                    val = "none"
                            columns.append(db_col)
                            values.append(val)

                        sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
                        cursor.execute(sql, values)
                        success_count += 1
                    except Exception as e:
                        print(f"   ❌ Row {i} failed: {e}")
                        print(
                            f"   ❌ Failed column mapping: {csv_col} -> {db_col}, value: {val}"
                        )
                        break

                if success_count == 5:
                    print(f"   ✅ Group 3 SUCCESS: {success_count}/5 rows")
                    conn.commit()

                    # Final test: Upload all data
                    print(f"\n🚀 Final Upload: All {len(df)} rows...")
                    cursor.execute("DELETE FROM records")

                    uploaded = 0
                    for i, row in df.iterrows():
                        try:
                            values = []
                            columns = []
                            for csv_col, db_col in group3_mapping.items():
                                val = row[csv_col]
                                if pd.isna(val):
                                    if db_col in [
                                        "horse_number",
                                        "draw",
                                        "horse_id",
                                        "age",
                                        "or_rating",
                                        "jockey_id",
                                        "trainer_id",
                                    ]:
                                        val = 0
                                    elif db_col in ["weight_uk", "weight"]:
                                        val = 0.0
                                    else:
                                        val = "none"
                                columns.append(db_col)
                                values.append(val)

                            sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
                            cursor.execute(sql, values)
                            uploaded += 1
                        except Exception as e:
                            print(f"   ⚠️ Skipped row {i}: {e}")
                            continue

                    conn.commit()
                    print(f"   ✅ Final upload: {uploaded}/{len(df)} rows")

                    # Verify final count
                    cursor.execute("SELECT COUNT(*) FROM records")
                    final_count = cursor.fetchone()[0]
                    print(f"   📊 Database verification: {final_count} records")

                    return final_count > 0
                else:
                    print(f"   ❌ Group 3 FAILED: {success_count}/5 rows")
                    return False
            else:
                print(f"   ❌ Group 2 FAILED: {success_count}/5 rows")
                return False
        else:
            print(f"   ❌ Group 1 FAILED: {success_count}/5 rows")
            return False

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("🧪 Using Test Framework Approach: Debug As We Go")
    success = test_incremental_upload()
    if success:
        print("\n🎉 SUCCESS! Records uploaded and tested incrementally")
        print("Now ML training should have access to the data!")
    else:
        print("\n❌ FAILED! Debugging shows exactly where the issue is")
