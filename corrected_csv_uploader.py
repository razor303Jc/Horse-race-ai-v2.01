#!/usr/bin/env python3
"""
Corrected CSV Uploader - Using actual database schema
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

def find_latest_csv_files():
    """Find the most recent CSV files from daily downloads"""
    downloads_dir = Path("data/daily_downloads")
    csv_files = {}
    
    # Look for records.csv (race results)
    records_files = list(downloads_dir.rglob("records/records.csv"))
    if records_files:
        csv_files["race_results"] = str(max(records_files, key=lambda f: f.stat().st_mtime))
    
    # Look for races.csv (race cards) in cards_data
    races_files = list(downloads_dir.glob("cards_data/races/races.csv"))
    if races_files:
        csv_files["races_cards"] = str(max(races_files, key=lambda f: f.stat().st_mtime))
        
    return csv_files

def create_correct_column_mapping(csv_columns, table_name):
    """Create mapping based on actual database schema"""
    
    mappings = {
        "race_results": {
            # CSV column -> Database column
            "Race_ID": "race_id",
            "Name": "horse_name", 
            "Jockey": "jockey_name",
            "Trainer": "trainer_name",
            "weight_uk": "horse_weight_kg",
            "Age": "horse_age",
            "Draw": "draw",
            "Odds": "win_odds",
            "Place": "finished_position",
            "Horse_ID": "horse_id"
        },
        "races_cards": {
            # CSV column -> Database column  
            "race_number": "race_number",
            "race_time": "race_time",
            "Course": "course",
            "Race_type": "race_type", 
            "Date": "date",  # This is the important one!
            "Race_name": "race_name",
            "Class": "class_level",
            "Years": "years"
        }
    }
    
    # Get mapping for this table
    table_mapping = mappings.get(table_name, {})
    
    # Build final mapping for available columns
    final_mapping = {}
    for csv_col in csv_columns:
        if csv_col in table_mapping:
            final_mapping[csv_col] = table_mapping[csv_col]
    
    return final_mapping

def clear_table(table_name, conn):
    """Clear existing data from table"""
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table_name}")
            conn.commit()
            print(f"   🧹 Cleared table {table_name}")
            return True
    except Exception as e:
        print(f"   ❌ Failed to clear {table_name}: {e}")
        return False

def upload_csv_corrected(file_path, table_name, conn):
    """Upload CSV with corrected column mapping"""
    try:
        print(f"📊 Processing {file_path} -> {table_name}")
        
        # Read CSV
        df = pd.read_csv(file_path, low_memory=False)
        print(f"   Original: {len(df)} rows, {len(df.columns)} columns")
        
        if len(df) == 0:
            print(f"   ⚠️ Empty file, skipping")
            return False
        
        # Create column mapping
        csv_columns = list(df.columns)
        column_mapping = create_correct_column_mapping(csv_columns, table_name)
        
        print(f"   Available CSV columns: {csv_columns[:10]}...")
        print(f"   Column mappings: {column_mapping}")
        
        if not column_mapping:
            print(f"   ❌ No column mappings found")
            return False
        
        # Prepare mapped data
        mapped_data = {}
        for csv_col, db_col in column_mapping.items():
            if csv_col in df.columns:
                mapped_data[db_col] = df[csv_col]
        
        if not mapped_data:
            print(f"   ❌ No mapped data available")
            return False
        
        # Create mapped DataFrame
        mapped_df = pd.DataFrame(mapped_data)
        
        # Clean data
        for col in mapped_df.columns:
            # Replace empty strings with None
            mapped_df[col] = mapped_df[col].replace('', None)
            mapped_df[col] = mapped_df[col].where(pd.notna(mapped_df[col]), None)
        
        # Show sample of date data for debugging
        if 'date' in mapped_df.columns:
            print(f"   📅 Sample dates: {mapped_df['date'].dropna().head(3).tolist()}")
        
        # Prepare insert data
        columns = list(mapped_df.columns)
        insert_data = []
        
        for _, row in mapped_df.iterrows():
            row_data = []
            for col in columns:
                val = row[col]
                if pd.isna(val) or val == '':
                    row_data.append(None)
                else:
                    # Convert numeric values appropriately
                    if col in ['horse_age', 'draw', 'finished_position', 'race_number', 'field_size', 'prize_money']:
                        try:
                            row_data.append(int(float(val)))
                        except (ValueError, TypeError):
                            row_data.append(None)
                    elif col in ['horse_weight_kg']:
                        try:
                            row_data.append(float(val))
                        except (ValueError, TypeError):
                            row_data.append(None)
                    else:
                        row_data.append(str(val))
            insert_data.append(tuple(row_data))
        
        # Insert data
        if insert_data:
            with conn.cursor() as cur:
                cols_str = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))
                
                execute_values(
                    cur,
                    f"INSERT INTO {table_name} ({cols_str}) VALUES %s",
                    insert_data,
                    page_size=1000
                )
                conn.commit()
                
                print(f"   ✅ Inserted {len(insert_data)} rows")
                return True
        else:
            print(f"   ⚠️ No valid data to insert")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
        return False

def main():
    print("🎯 Corrected CSV Uploader - With Proper Schema Mapping")
    print("=" * 60)
    
    # Find CSV files
    csv_files = find_latest_csv_files()
    print(f"📁 Found {len(csv_files)} CSV files:")
    for table, file_path in csv_files.items():
        print(f"   {table}: {file_path}")
    print()
    
    if not csv_files:
        print("❌ No CSV files found in data/daily_downloads")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Clear existing data  
    print("\n🧹 Clearing existing data...")
    for table_name in csv_files.keys():
        clear_table(table_name, conn)
    
    # Process each file
    successful = 0
    total = len(csv_files)
    
    for table_name, file_path in csv_files.items():
        print(f"\n🔄 Processing {table_name}...")
        if upload_csv_corrected(file_path, table_name, conn):
            successful += 1
    
    # Check final results with sample data
    print("\n📊 Final Database Status:")
    with conn.cursor() as cur:
        # Check race_results
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(race_date) as with_race_dates,
                MIN(race_date) as min_date,
                MAX(race_date) as max_date
            FROM race_results
        """)
        result = cur.fetchone()
        print(f"   race_results: {result[0]} total, {result[1]} with race_dates ({result[2]} to {result[3]})")
        
        # Show sample race results
        cur.execute("SELECT race_id, horse_name, jockey_name FROM race_results LIMIT 3")
        samples = cur.fetchall()
        print(f"   Sample race_results: {samples}")
        
        # Check races_cards
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(date) as with_dates,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM races_cards
        """)
        result = cur.fetchone()
        print(f"   races_cards: {result[0]} total, {result[1]} with dates ({result[2]} to {result[3]})")
        
        # Show sample race cards
        cur.execute("SELECT race_number, course, date FROM races_cards LIMIT 3")
        samples = cur.fetchall()
        print(f"   Sample races_cards: {samples}")
    
    conn.close()
    
    print(f"\n📊 SUMMARY: {successful}/{total} files uploaded successfully")
    
    if successful == total:
        print("🎉 All files uploaded successfully with proper dates!")
    else:
        print("⚠️ Some files failed - check errors above")

if __name__ == "__main__":
    main()
