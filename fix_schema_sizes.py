#!/usr/bin/env python3
"""
Fix Schema - Proper Column Sizes
Update VARCHAR lengths based on actual data lengths
"""

import psycopg2


def fix_schema_column_sizes():
    """Fix schema with proper column sizes for actual data"""

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    try:
        print("🔧 Fixing schema column sizes...")

        # Drop and recreate with proper sizes
        cursor.execute("DROP TABLE IF EXISTS racecard_details CASCADE")
        cursor.execute("DROP TABLE IF EXISTS records CASCADE")
        cursor.execute("DROP TABLE IF EXISTS races CASCADE")
        cursor.execute("DROP TABLE IF EXISTS horses CASCADE")
        cursor.execute("DROP TABLE IF EXISTS jockeys_stats CASCADE")
        cursor.execute("DROP TABLE IF EXISTS trainers_stats CASCADE")

        # Create RACES table with proper VARCHAR sizes
        races_sql = """
        CREATE TABLE races (
            Race_ID BIGINT PRIMARY KEY,
            race_number INTEGER,
            race_time VARCHAR(20),
            course_id INTEGER,
            Course VARCHAR(100),
            Race_type VARCHAR(50),
            Date DATE,
            Race_name TEXT,
            Class VARCHAR(50),
            Years VARCHAR(50),
            Distance VARCHAR(50),
            Surface VARCHAR(100),
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
        print("   ✅ Fixed races table")

        # Create RECORDS table with proper sizes
        records_sql = """
        CREATE TABLE records (
            ID BIGINT PRIMARY KEY,
            Race_ID BIGINT,
            Horse_number INTEGER,
            Place INTEGER,
            Draw INTEGER,
            Horse_ID BIGINT,
            Country VARCHAR(20),
            Name VARCHAR(150),
            Age INTEGER,
            weight_uk DECIMAL(10,2),
            weight DECIMAL(10,2),
            gears VARCHAR(20),
            Horse_rate INTEGER,
            jockey_ID BIGINT,
            jockey VARCHAR(150),
            trainer_ID BIGINT,
            trainer VARCHAR(150),
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
        print("   ✅ Fixed records table")

        # Create HORSES table with proper sizes
        horses_sql = """
        CREATE TABLE horses (
            id BIGINT PRIMARY KEY,
            uptodate VARCHAR(50),
            state VARCHAR(50),
            race_id_last_race BIGINT,
            date_last_race DATE,
            name VARCHAR(150),
            country VARCHAR(20),
            age INTEGER,
            color VARCHAR(50),
            owner TEXT,
            sire VARCHAR(150),
            dam VARCHAR(150),
            dam_sire VARCHAR(150),
            sex VARCHAR(20),
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
        print("   ✅ Fixed horses table")

        # Create JOCKEYS_STATS table
        jockeys_sql = """
        CREATE TABLE jockeys_stats (
            Jockey_ID BIGINT PRIMARY KEY,
            UptoDate VARCHAR(50),
            Name VARCHAR(150),
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
        print("   ✅ Fixed jockeys_stats table")

        # Create TRAINERS_STATS table
        trainers_sql = """
        CREATE TABLE trainers_stats (
            Trainer_ID BIGINT PRIMARY KEY,
            UptoDate VARCHAR(50),
            Name VARCHAR(150),
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
        print("   ✅ Fixed trainers_stats table")

        # Create RACECARD_DETAILS table
        racecard_sql = """
        CREATE TABLE racecard_details (
            id BIGINT PRIMARY KEY,
            race_id BIGINT,
            horse_number INTEGER,
            Draw INTEGER,
            Horse_ID BIGINT,
            Country VARCHAR(20),
            Name VARCHAR(150),
            Age INTEGER,
            weight_uk DECIMAL(10,2),
            weight DECIMAL(10,2),
            gears VARCHAR(20),
            Horse_rate INTEGER,
            jockey_ID BIGINT,
            jockey VARCHAR(150),
            trainer_ID BIGINT,
            trainer VARCHAR(150),
            fav INTEGER,
            odds VARCHAR(50),
            odds_decimal DECIMAL(10,2),
            Timeform_comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (race_id) REFERENCES races(Race_ID)
        )
        """
        cursor.execute(racecard_sql)
        print("   ✅ Fixed racecard_details table")

        conn.commit()
        print("\n🎉 Schema fixed with proper column sizes!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    fix_schema_column_sizes()
