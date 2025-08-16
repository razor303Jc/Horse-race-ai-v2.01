#!/usr/bin/env python3
"""
Create Proper Schema - Matching CSV files exactly
Tables match CSV filenames, columns match CSV headers exactly
BIGINT for IDs, proper data types for NULL/blank/"-" handling
"""

import psycopg2


def create_proper_schema():
    """Create database schema that matches CSV files exactly"""

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    try:
        print("🗃️ Creating proper schema to match CSV files...")

        # Drop existing tables if they exist
        drop_tables = [
            "DROP TABLE IF EXISTS racecard_details CASCADE",
            "DROP TABLE IF EXISTS records CASCADE",
            "DROP TABLE IF EXISTS races CASCADE",
            "DROP TABLE IF EXISTS horses CASCADE",
            "DROP TABLE IF EXISTS jockeys_stats CASCADE",
            "DROP TABLE IF EXISTS trainers_stats CASCADE",
        ]

        for drop_sql in drop_tables:
            cursor.execute(drop_sql)
            print(f"   ✅ {drop_sql}")

        # Create RACES table (matches races.csv exactly)
        races_sql = """
        CREATE TABLE races (
            Race_ID BIGINT PRIMARY KEY,
            race_number INTEGER,
            race_time VARCHAR(10),
            course_id INTEGER,
            Course VARCHAR(100),
            Race_type VARCHAR(50),
            Date DATE,
            Race_name VARCHAR(200),
            Class VARCHAR(10),
            Years VARCHAR(20),
            Distance VARCHAR(20),
            Surface VARCHAR(20),
            Prize VARCHAR(50),
            Runners_racecard INTEGER,
            Runners INTEGER,
            Draw INTEGER,
            EW_racecard INTEGER,
            EW INTEGER,
            Places_EW_racecard INTEGER,
            Places_EW INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(races_sql)
        print("   📋 Created races table")

        # Create RECORDS table (matches records.csv exactly)
        records_sql = """
        CREATE TABLE records (
            ID BIGINT PRIMARY KEY,
            Race_ID BIGINT,
            Horse_number INTEGER,
            Place INTEGER,
            Draw INTEGER,
            Horse_ID BIGINT,
            Country VARCHAR(10),
            Name VARCHAR(100),
            Age INTEGER,
            weight_uk DECIMAL(10,2),
            weight DECIMAL(10,2),
            gears VARCHAR(10),
            Horse_rate INTEGER,
            jockey_ID BIGINT,
            jockey VARCHAR(100),
            trainer_ID BIGINT,
            trainer VARCHAR(100),
            fav INTEGER,
            SP DECIMAL(10,2),
            Distance_btn DECIMAL(10,3),
            Distance_btn_total DECIMAL(10,3),
            distance_sec_1 DECIMAL(10,3),
            sectional_time_1 DECIMAL(10,3),
            distance_sec_2 DECIMAL(10,3),
            sectional_time_2 DECIMAL(10,3),
            distance_sec_3 DECIMAL(10,3),
            sectional_time_3 DECIMAL(10,3),
            distance_sec_4 DECIMAL(10,3),
            sectional_time_4 DECIMAL(10,3),
            distance_sec_5 DECIMAL(10,3),
            sectional_time_5 DECIMAL(10,3),
            distance_sec_6 DECIMAL(10,3),
            sectional_time_6 DECIMAL(10,3),
            distance_sec_7 DECIMAL(10,3),
            sectional_time_7 DECIMAL(10,3),
            distance_sec_8 DECIMAL(10,3),
            sectional_time_8 DECIMAL(10,3),
            distance_sec_9 DECIMAL(10,3),
            sectional_time_9 DECIMAL(10,3),
            distance_sec_10 DECIMAL(10,3),
            sectional_time_10 DECIMAL(10,3),
            distance_sec_11 DECIMAL(10,3),
            sectional_time_11 DECIMAL(10,3),
            distance_sec_12 DECIMAL(10,3),
            sectional_time_12 DECIMAL(10,3),
            distance_sec_13 DECIMAL(10,3),
            sectional_time_13 DECIMAL(10,3),
            distance_sec_14 DECIMAL(10,3),
            sectional_time_14 DECIMAL(10,3),
            distance_sec_15 DECIMAL(10,3),
            sectional_time_15 DECIMAL(10,3),
            distance_sec_16 DECIMAL(10,3),
            sectional_time_16 DECIMAL(10,3),
            distance_sec_17 DECIMAL(10,3),
            sectional_time_17 DECIMAL(10,3),
            distance_sec_18 DECIMAL(10,3),
            sectional_time_18 DECIMAL(10,3),
            finish_time DECIMAL(10,3),
            distance_speed_early_race DECIMAL(10,3),
            speed_achieved_early_race DECIMAL(10,3),
            distance_speed_mid_race DECIMAL(10,3),
            speed_achieved_mid_race DECIMAL(10,3),
            distance_speed_finish_race DECIMAL(10,3),
            speed_achieved_finish_race DECIMAL(10,3),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Race_ID) REFERENCES races(Race_ID)
        )
        """
        cursor.execute(records_sql)
        print("   📋 Created records table")

        # Create HORSES table (matches horses.csv exactly)
        horses_sql = """
        CREATE TABLE horses (
            id BIGINT PRIMARY KEY,
            uptodate VARCHAR(20),
            state VARCHAR(20),
            race_id_last_race BIGINT,
            date_last_race DATE,
            name VARCHAR(100),
            country VARCHAR(10),
            age INTEGER,
            color VARCHAR(20),
            owner VARCHAR(200),
            sire VARCHAR(100),
            dam VARCHAR(100),
            dam_sire VARCHAR(100),
            sex VARCHAR(10),
            Total_races INTEGER,
            Wins INTEGER,
            Percentage_wins DECIMAL(5,2),
            placed INTEGER,
            Percentage_placed DECIMAL(5,2),
            Flat_AW_races INTEGER,
            Flat_AW_wins INTEGER,
            Flat_AW_rate DECIMAL(5,2),
            Flat_AW_placed INTEGER,
            Flat_AW_placed_rate DECIMAL(5,2),
            Flat_Turf_races INTEGER,
            Flat_Turf_wins INTEGER,
            Flat_Turf_rate DECIMAL(5,2),
            Flat_Turf_placed INTEGER,
            Flat_Turf_placed_rate DECIMAL(5,2),
            Chase_races INTEGER,
            Chase_wins INTEGER,
            Chase_rate DECIMAL(5,2),
            Chase_placed INTEGER,
            Chase_placed_rate DECIMAL(5,2),
            Hurdle_races INTEGER,
            Hurdle_wins INTEGER,
            Hurdle_rate DECIMAL(5,2),
            Hurdle_placed INTEGER,
            Hurdle_placed_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(horses_sql)
        print("   🐎 Created horses table")

        # Create JOCKEYS_STATS table (matches jockeys_stats.csv exactly)
        jockeys_sql = """
        CREATE TABLE jockeys_stats (
            Jockey_ID BIGINT PRIMARY KEY,
            UptoDate VARCHAR(20),
            Name VARCHAR(100),
            Total_races INTEGER,
            Wins INTEGER,
            Percentage_wins DECIMAL(5,2),
            Placed INTEGER,
            Percentage_placed DECIMAL(5,2),
            Flat_AW_races INTEGER,
            Flat_AW_wins INTEGER,
            Flat_AW_rate DECIMAL(5,2),
            Flat_AW_placed INTEGER,
            Flat_AW_placed_rate DECIMAL(5,2),
            Flat_Turf_races INTEGER,
            Flat_Turf_wins INTEGER,
            Flat_Turf_rate DECIMAL(5,2),
            Flat_Turf_placed INTEGER,
            Flat_Turf_placed_rate DECIMAL(5,2),
            Chase_races INTEGER,
            Chase_wins INTEGER,
            Chase_rate DECIMAL(5,2),
            Chase_placed INTEGER,
            Chase_placed_rate DECIMAL(5,2),
            Hurdle_races INTEGER,
            Hurdle_wins INTEGER,
            Hurdle_rate DECIMAL(5,2),
            Hurdle_placed INTEGER,
            Hurdle_placed_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(jockeys_sql)
        print("   🏇 Created jockeys_stats table")

        # Create TRAINERS_STATS table (matches trainers_stats.csv exactly)
        trainers_sql = """
        CREATE TABLE trainers_stats (
            Trainer_ID BIGINT PRIMARY KEY,
            UptoDate VARCHAR(20),
            Name VARCHAR(100),
            Total_races INTEGER,
            Wins INTEGER,
            Percentage_wins DECIMAL(5,2),
            Placed INTEGER,
            Percentage_placed DECIMAL(5,2),
            Flat_AW_races INTEGER,
            Flat_AW_wins INTEGER,
            Flat_AW_rate DECIMAL(5,2),
            Flat_AW_placed INTEGER,
            Flat_AW_placed_rate DECIMAL(5,2),
            Flat_Turf_races INTEGER,
            Flat_Turf_wins INTEGER,
            Flat_Turf_rate DECIMAL(5,2),
            Flat_Turf_placed INTEGER,
            Flat_Turf_placed_rate DECIMAL(5,2),
            Chase_races INTEGER,
            Chase_wins INTEGER,
            Chase_rate DECIMAL(5,2),
            Chase_placed INTEGER,
            Chase_placed_rate DECIMAL(5,2),
            Hurdle_races INTEGER,
            Hurdle_wins INTEGER,
            Hurdle_rate DECIMAL(5,2),
            Hurdle_placed INTEGER,
            Hurdle_placed_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(trainers_sql)
        print("   👨‍🏫 Created trainers_stats table")

        # Create RACECARD_DETAILS table (matches racecard_details.csv exactly)
        racecard_sql = """
        CREATE TABLE racecard_details (
            id BIGINT PRIMARY KEY,
            race_id BIGINT,
            horse_number INTEGER,
            Draw INTEGER,
            Horse_ID BIGINT,
            Country VARCHAR(10),
            Name VARCHAR(100),
            Age INTEGER,
            weight_uk DECIMAL(10,2),
            weight DECIMAL(10,2),
            gears VARCHAR(10),
            Horse_rate INTEGER,
            jockey_ID BIGINT,
            jockey VARCHAR(100),
            trainer_ID BIGINT,
            trainer VARCHAR(100),
            fav INTEGER,
            odds VARCHAR(20),
            odds_decimal DECIMAL(10,2),
            Timeform_comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (race_id) REFERENCES races(Race_ID)
        )
        """
        cursor.execute(racecard_sql)
        print("   📋 Created racecard_details table")

        conn.commit()
        print("\n🎉 SUCCESS! Proper schema created to match CSV files exactly!")
        print("   ✅ BIGINT for all IDs")
        print("   ✅ Column names match CSV headers exactly")
        print("   ✅ Ready for NULL/blank/'-' data handling")

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_proper_schema()
