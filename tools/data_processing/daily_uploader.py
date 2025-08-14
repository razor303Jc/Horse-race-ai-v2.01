#!/usr/bin/env python3
"""
Smart Daily CSV Uploader - Handle auto-increment IDs and data types
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

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
    downloads_dir = Path("project_root / 'data' / daily_downloads")
    csv_files = {}
    
    # Look for records.csv (race results)
    records_files = list(downloads_dir.rglob("records/records.csv"))
    if records_files:
        csv_files["race_results"] = str(max(records_files, key=lambda f: f.stat().st_mtime))
    
    # Look for races.csv (race cards) in cards_data
    races_files = list(downloads_dir.glob("cards_project_root / 'data' / races/races.csv"))
    if races_files:
        csv_files["races_cards"] = str(max(races_files, key=lambda f: f.stat().st_mtime))
        
    return csv_files

def get_table_schema(table_name, conn):
    """Get table schema info"""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        return cur.fetchall()

def upload_csv_smart(file_path, table_name, conn):
    """Smart CSV upload that handles primary keys and data types"""
    try:
        print(f"📊 Processing {file_path} -> {table_name}")
        
        # Read CSV with basic cleaning
        df = pd.read_csv(file_path, low_memory=False)
        print(f"   Original: {len(df)} rows, {len(df.columns)} columns")
        
        if len(df) == 0:
            print(f"   ⚠️ Empty file, skipping")
            return False
            
        # Get table schema
        schema = get_table_schema(table_name, conn)
        if not schema:
            print(f"   ❌ Table {table_name} not found")
            return False
            
        print(f"   Table has {len(schema)} columns")
        
        # Build column mapping
        csv_cols = [col.lower().strip() for col in df.columns]
        table_cols = {}
        auto_id_col = None
        
        for col_name, data_type, is_nullable, default in schema:
            table_cols[col_name] = {
                'type': data_type,
                'nullable': is_nullable == 'YES',
                'default': default
            }
            
            # Check if this is an auto-increment ID
            if default and 'nextval' in str(default):
                auto_id_col = col_name
                print(f"   Auto-increment ID column: {col_name}")
        
        # Map CSV columns to table columns
        mapped_cols = []
        for table_col in table_cols.keys():
            if table_col == auto_id_col:
                continue  # Skip auto-increment ID
            if table_col in csv_cols:
                mapped_cols.append(table_col)
        
        print(f"   Mapped columns: {mapped_cols[:5]}...")
        
        if not mapped_cols:
            print(f"   ❌ No matching columns found")
            return False
            
        # Clean and prepare data
        clean_df = df.copy()
        
        # Handle common data issues
        for col in mapped_cols:
            if col in clean_df.columns:
                # Convert empty strings to None for nullable fields
                if table_cols[col]['nullable']:
                    clean_df[col] = clean_df[col].replace('', None)
                    clean_df[col] = clean_df[col].where(pd.notna(clean_df[col]), None)
                
        # Prepare insert data
        insert_data = []
        for _, row in clean_df.iterrows():
            row_data = []
            for col in mapped_cols:
                if col in row.index:
                    val = row[col]
                    if pd.isna(val) or val == '':
                        row_data.append(None)
                    else:
                        # Handle different data types
                        col_type = table_cols[col]['type']
                        if 'int' in col_type or 'bigint' in col_type:
                            try:
                                row_data.append(int(float(val)))
                            except (ValueError, TypeError):
                                row_data.append(None if table_cols[col]['nullable'] else 0)
                        elif 'float' in col_type or 'numeric' in col_type:
                            try:
                                row_data.append(float(val))
                            except (ValueError, TypeError):
                                row_data.append(None if table_cols[col]['nullable'] else 0.0)
                        else:
                            row_data.append(str(val))
                else:
                    row_data.append(None)
            insert_data.append(tuple(row_data))
        
        # Insert data
        if insert_data:
            with conn.cursor() as cur:
                cols_str = ", ".join(mapped_cols)
                placeholders = ", ".join(["%s"] * len(mapped_cols))
                
                # Use ON CONFLICT for tables with unique constraints
                if table_name == "race_results" and auto_id_col:
                    query = f"""
                        INSERT INTO {table_name} ({cols_str}) 
                        VALUES %s
                        ON CONFLICT DO NOTHING
                    """
                else:
                    query = f"INSERT INTO {table_name} ({cols_str}) VALUES %s"
                
                execute_values(cur, query, insert_data, page_size=1000)
                conn.commit()
                
                # Get actual inserted count
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_count = cur.fetchone()[0]
                
                print(f"   ✅ Insert completed - Table now has {total_count} total rows")
                return True
        else:
            print(f"   ⚠️ No valid data to insert")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.rollback()
        return False

def main():
    print("🧠 Smart Daily CSV Uploader - Processing Downloaded Files")
    print("=" * 60)
    
    # Find CSV files
    csv_files = find_latest_csv_files()
    print(f"📁 Found {len(csv_files)} CSV files:")
    for table, file_path in csv_files.items():
        print(f"   {table}: {file_path}")
    print()
    
    if not csv_files:
        print("❌ No CSV files found in project_root / 'data' / daily_downloads")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Check current record counts
    print("\n📊 Current Database Status:")
    with conn.cursor() as cur:
        for table_name in csv_files.keys():
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"   {table_name}: {count} records")
    
    # Process each file
    successful = 0
    total = len(csv_files)
    
    for table_name, file_path in csv_files.items():
        print(f"\n🔄 Processing {table_name}...")
        if upload_csv_smart(file_path, table_name, conn):
            successful += 1
    
    # Show final counts
    print("\n📊 Final Database Status:")
    with conn.cursor() as cur:
        for table_name in csv_files.keys():
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"   {table_name}: {count} records")
    
    conn.close()
    
    print(f"\n📊 SUMMARY: {successful}/{total} files uploaded successfully")
    
    if successful == total:
        print("🎉 All files uploaded successfully!")
    else:
        print("⚠️ Some files failed - check errors above")

if __name__ == "__main__":
    main()
