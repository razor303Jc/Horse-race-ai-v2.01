#!/usr/bin/env python3
"""
Card Data Processor - Upload extracted card data to cards database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_cards_db():
    """Connect to cards database"""
    return psycopg2.connect(
        host='postgres',
        database='cards_horse_racing_db',
        user='horse_racing',
        password=os.getenv('POSTGRES_PASSWORD', 'secure_password_123')
    )

def upload_races_data(races_df):
    """Upload races data"""
    logger.info(f"📊 Processing {len(races_df)} races...")
    
    conn = connect_cards_db()
    cursor = conn.cursor()
    
    # Clear existing data for these dates
    dates = races_df['Date'].unique()
    for date in dates:
        cursor.execute("DELETE FROM races WHERE date = %s", (date,))
        logger.info(f"🗑️ Cleared existing races for {date}")
    
    # Prepare data for insertion
    races_data = []
    for _, row in races_df.iterrows():
        race_data = (
            int(row['Race_ID']),
            int(row['race_number']) if pd.notna(row['race_number']) else None,
            row['race_time'],
            int(row['course_id']) if pd.notna(row['course_id']) else None,
            row['Course'],
            row['Race_type'],
            row['Date'],
            row['Race_name'],
            row['Class'],
            row['Years'],
            row['Distance'],
            row['Surface'],
            row['Prize']
        )
        races_data.append(race_data)
    
    # Insert races
    insert_query = """
        INSERT INTO races (race_id, race_number, race_time, course_id, course, 
                          race_type, date, race_name, class, years, distance, 
                          surface, prize)
        VALUES %s
    """
    
    execute_values(cursor, insert_query, races_data)
    conn.commit()
    
    logger.info(f"✅ Uploaded {len(races_data)} races")
    conn.close()

def upload_racecard_data(racecard_df):
    """Upload racecard details to database"""
    print(f"📋 Uploading {len(racecard_df)} racecard entries...")
    
    conn = connect_cards_db()
    cursor = conn.cursor()
    
    try:
        # Get the current max detail_id
        cursor.execute("SELECT COALESCE(MAX(detail_id), 0) FROM racecard_details")
        max_detail_id = cursor.fetchone()[0]
        print(f"� Current max detail_id: {max_detail_id}")
        
        # Prepare data for insertion with proper detail_ids
        racecard_data = []
        for i, (_, row) in enumerate(racecard_df.iterrows()):
            detail_id = max_detail_id + i + 1
            
            # Clean weight data: replace "-" with "."
            weight_cleaned = None
            if pd.notna(row['weight']) and row['weight']:
                weight_str = str(row['weight']).replace('-', '.')
                weight_cleaned = weight_str if weight_str else None
            
            racecard_data.append((
                detail_id,
                row['race_id'],
                row['Name'],  # horse_name -> Name
                row['jockey'],
                row['trainer'],
                int(row['horse_number']) if pd.notna(row['horse_number']) else None,  # number -> horse_number
                float(row['odds_decimal']) if pd.notna(row['odds_decimal']) else None,  # odds -> odds_decimal
                weight_cleaned,  # cleaned weight data
                int(row['Age']) if pd.notna(row['Age']) else None,  # age -> Age
                None  # form column doesn't exist in this data
            ))
        
        # Insert query with detail_id
        insert_query = """
            INSERT INTO racecard_details 
            (detail_id, race_id, horse_name, jockey, trainer, number, odds, weight, age, form)
            VALUES %s
        """
        
        execute_values(cursor, insert_query, racecard_data)
        conn.commit()
        print(f"✅ Successfully uploaded {len(racecard_data)} racecard entries")
        
    except Exception as e:
        print(f"❌ Error uploading racecard data: {e}")
        conn.rollback()
    finally:
        conn.close()

def process_card_data(date_folder=""):
    """Process card data for a specific date"""
    base_path = "/app/tools/temp_card_processing"
    
    if date_folder:
        races_file = f"{base_path}/{date_folder}/races/races.csv"
        racecard_file = f"{base_path}/{date_folder}/racecard_details/racecard_details.csv"
    else:
        races_file = f"{base_path}/races/races.csv"
        racecard_file = f"{base_path}/racecard_details/racecard_details.csv"
    
    logger.info(f"🚀 Processing card data from {races_file}")
    
    # Load data
    races_df = pd.read_csv(races_file)
    racecard_df = pd.read_csv(racecard_file)
    
    logger.info(f"📊 Loaded {len(races_df)} races and {len(racecard_df)} horses")
    
    # Upload to database
    upload_races_data(races_df)
    upload_racecard_data(racecard_df)
    
    logger.info("🎉 Card data processing complete!")

if __name__ == "__main__":
    # Process both dates
    logger.info("🏇 CARD DATA UPLOAD STARTED")
    logger.info("="*50)
    
    # Process 22nd August data
    logger.info("📅 Processing 2025-08-22 data...")
    process_card_data("")
    
    # Process 23rd August data  
    logger.info("📅 Processing 2025-08-23 data...")
    process_card_data("2025-08-23")
    
    logger.info("🏁 ALL CARD DATA PROCESSED!")
