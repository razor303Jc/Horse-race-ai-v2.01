#!/usr/bin/env python3
"""
PostgreSQL Entity Tables Setup and Testing Script
=================================================

This script:
1. Tests PostgreSQL connection to all 3 databases
2. Creates entity tables in each database  
3. Validates table creation and constraints
4. Provides sample data insertion for testing

Usage:
    python3 setup_entity_tables.py

Databases:
    - results_horse_racing_db
    - cards_horse_racing_db  
    - advanced_metrics (needs to be created)
"""

import psycopg2
import os
import sys
from datetime import datetime
import json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'horse_racing',
    'password': os.getenv('POSTGRES_PASSWORD', 'secure_password_123'),
    'default_db': 'postgres'
}

# Target databases
TARGET_DATABASES = [
    'results_horse_racing_db',
    'cards_horse_racing_db',
    'advanced_metrics_horse_racing_db'
]

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    NC = '\033[0m'  # No Color

def log(message, color=Colors.GREEN):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{color}[{timestamp}]{Colors.NC} {message}")

def error(message):
    log(f"ERROR: {message}", Colors.RED)

def info(message):
    log(f"INFO: {message}", Colors.BLUE)

def success(message):
    log(f"SUCCESS: {message}", Colors.PURPLE)

def warn(message):
    log(f"WARNING: {message}", Colors.YELLOW)

def test_connection():
    """Test connection to PostgreSQL"""
    try:
        log("🔄 Testing PostgreSQL connection...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['default_db']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        success(f"✅ PostgreSQL connection successful")
        info(f"Database version: {version}")
        return True
        
    except Exception as e:
        error(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_database_exists(db_name):
    """Check if database exists"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['default_db']
        )
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return exists
        
    except Exception as e:
        error(f"Error checking database {db_name}: {e}")
        return False

def create_database(db_name):
    """Create database if it doesn't exist"""
    try:
        if check_database_exists(db_name):
            info(f"Database {db_name} already exists")
            return True
            
        log(f"🔄 Creating database: {db_name}")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['default_db']
        )
        conn.autocommit = True
        
        cursor = conn.cursor()
        cursor.execute(f'CREATE DATABASE "{db_name}";')
        
        cursor.close()
        conn.close()
        
        success(f"✅ Created database: {db_name}")
        return True
        
    except Exception as e:
        error(f"❌ Failed to create database {db_name}: {e}")
        return False

def read_sql_file(file_path):
    """Read SQL file content"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        error(f"Failed to read SQL file {file_path}: {e}")
        return None

def create_entity_table(db_name, table_name, sql_file_path):
    """Create entity table in specified database"""
    try:
        log(f"🔄 Creating {table_name} table in {db_name}...")
        
        # Read SQL schema
        sql_content = read_sql_file(sql_file_path)
        if not sql_content:
            return False
        
        # Connect to target database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=db_name
        )
        
        cursor = conn.cursor()
        
        # Execute SQL (split by semicolon for multiple statements)
        statements = sql_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        success(f"✅ Created {table_name} table in {db_name}")
        return True
        
    except Exception as e:
        error(f"❌ Failed to create {table_name} table in {db_name}: {e}")
        return False

def validate_table_structure(db_name, table_name):
    """Validate table was created with correct structure"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=db_name
        )
        
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = %s AND table_schema = 'public'
        """, (table_name,))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            warn(f"Table {table_name} not found in {db_name}")
            return False
            
        # Get column information
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        # Get index information
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = %s AND schemaname = 'public'
        """, (table_name,))
        
        indexes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        info(f"📊 Table {table_name} in {db_name}:")
        info(f"   Columns: {len(columns)}")
        info(f"   Indexes: {len(indexes)}")
        
        return True
        
    except Exception as e:
        error(f"Error validating table {table_name} in {db_name}: {e}")
        return False

def insert_test_data(db_name, table_name):
    """Insert sample test data"""
    try:
        log(f"🔄 Inserting test data into {table_name} in {db_name}...")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=db_name
        )
        
        cursor = conn.cursor()
        
        # Sample data based on table type
        if table_name == 'horses':
            cursor.execute("""
                INSERT INTO horses (horse_id, name, age, jockey_id, trainer_id, 
                                  total_runs, total_wins, import_batch_id)
                VALUES 
                    (1234567, 'Test Horse 1', 4, 12345, 1234, 10, 3, 'test_batch_001'),
                    (2345678, 'Test Horse 2', 3, 23456, 2345, 8, 2, 'test_batch_001'),
                    (3456789, 'Test Horse 3', 5, 34567, 3456, 15, 5, 'test_batch_001')
                ON CONFLICT (horse_id) DO NOTHING
            """)
            
        elif table_name == 'jockeys':
            cursor.execute("""
                INSERT INTO jockeys (jockey_id, name, total_runs, total_wins, 
                                   claim_allowance, import_batch_id)
                VALUES 
                    (12345, 'Test Jockey 1', 100, 25, '7lb', 'test_batch_001'),
                    (23456, 'Test Jockey 2', 150, 35, '5lb', 'test_batch_001'),
                    (34567, 'Test Jockey 3', 80, 15, '10lb', 'test_batch_001')
                ON CONFLICT (jockey_id) DO NOTHING
            """)
            
        elif table_name == 'trainers':
            cursor.execute("""
                INSERT INTO trainers (trainer_id, name, stable_location, 
                                    total_runs, total_wins, import_batch_id)
                VALUES 
                    (1234, 'Test Trainer 1', 'Newmarket', 200, 45, 'test_batch_001'),
                    (2345, 'Test Trainer 2', 'Lambourn', 180, 38, 'test_batch_001'),
                    (3456, 'Test Trainer 3', 'Malton', 160, 32, 'test_batch_001')
                ON CONFLICT (trainer_id) DO NOTHING
            """)
        
        conn.commit()
        
        # Verify insertion
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        success(f"✅ Inserted test data into {table_name} (total records: {count})")
        return True
        
    except Exception as e:
        error(f"❌ Failed to insert test data into {table_name}: {e}")
        return False

def generate_summary_report():
    """Generate implementation summary report"""
    try:
        log("📊 Generating entity tables implementation summary...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'databases': {},
            'tables_created': [],
            'status': 'success'
        }
        
        for db_name in TARGET_DATABASES:
            if not check_database_exists(db_name):
                continue
                
            report['databases'][db_name] = {}
            
            for table_name in ['horses', 'jockeys', 'trainers']:
                try:
                    conn = psycopg2.connect(
                        host=DB_CONFIG['host'],
                        port=DB_CONFIG['port'],
                        user=DB_CONFIG['user'],
                        password=DB_CONFIG['password'],
                        database=db_name
                    )
                    
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    report['databases'][db_name][table_name] = {
                        'exists': True,
                        'record_count': count
                    }
                    
                    cursor.close()
                    conn.close()
                    
                except:
                    report['databases'][db_name][table_name] = {
                        'exists': False,
                        'record_count': 0
                    }
        
        # Save report
        with open('entity_tables_implementation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        success("✅ Implementation report saved: entity_tables_implementation_report.json")
        return True
        
    except Exception as e:
        error(f"Failed to generate summary report: {e}")
        return False

def main():
    """Main execution function"""
    log("🚀 Starting PostgreSQL Entity Tables Setup")
    print()
    
    # Test connection
    if not test_connection():
        error("Cannot proceed without database connection")
        return False
    
    print()
    
    # Create databases if needed
    for db_name in TARGET_DATABASES:
        create_database(db_name)
    
    print()
    
    # Entity table files
    entity_files = {
        'horses': 'database/entities/horses_entity_schema.sql',
        'jockeys': 'database/entities/jockeys_entity_schema.sql',  
        'trainers': 'database/entities/trainers_entity_schema.sql'
    }
    
    # Create entity tables in all databases
    for db_name in TARGET_DATABASES:
        if not check_database_exists(db_name):
            warn(f"Database {db_name} does not exist, skipping...")
            continue
            
        log(f"🔄 Setting up entity tables in {db_name}")
        
        for table_name, sql_file in entity_files.items():
            create_entity_table(db_name, table_name, sql_file)
            validate_table_structure(db_name, table_name)
            insert_test_data(db_name, table_name)
        
        print()
    
    # Generate summary report
    generate_summary_report()
    
    print()
    success("🎉 Entity tables setup completed!")
    print()
    info("📋 Next steps:")
    info("  1. Review implementation report: entity_tables_implementation_report.json")
    info("  2. Test entity lookups and relationships")
    info("  3. Populate with real CSV data")
    info("  4. Update existing tables to use entity foreign keys")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        warn("⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print("\n")
        error(f"❌ Setup failed: {e}")
        sys.exit(1)
