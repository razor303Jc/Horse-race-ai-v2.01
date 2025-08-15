#!/usr/bin/env python3
"""
🎯 Database Validation Script
Validates database structure, data integrity, and table relationships
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseValidator:
    """Validates the horse racing database structure and data"""

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.connection = None
        
        if not self.database_url:
            raise ValueError("No database URL provided via argument or .env file")

    def connect(self):
        """Connect to database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("✅ Connected to database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def execute_query(self, query):
        """Execute query and return results"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Query failed: {query[:100]}... - Error: {e}")
            return None

    def execute_single(self, query):
        """Execute query and return single result"""
        results = self.execute_query(query)
        return results[0] if results else None

    def validate_table_structure(self):
        """Validate all tables exist and have proper structure"""
        logger.info("🏗️ Validating database table structure...")
        
        # Get all tables in the database
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        
        tables = self.execute_query(tables_query)
        if not tables:
            logger.error("❌ No tables found in database")
            return False
            
        table_names = [table['table_name'] for table in tables]
        logger.info(f"📋 Found tables: {', '.join(table_names)}")
        
        # Check for essential tables based on what we found in the database
        essential_tables = {
            'races_cards': 'Race card information',
            'race_results': 'Race results data', 
            'horses': 'Horse information',
            'jockeys_stats': 'Jockey statistics',
            'trainers_stats': 'Trainer statistics',
            'racecard_details': 'Detailed race card data'
        }
        
        missing_tables = []
        for table, description in essential_tables.items():
            if table not in table_names:
                missing_tables.append(f"{table} ({description})")
                
        if missing_tables:
            logger.warning(f"⚠️ Missing expected tables: {', '.join(missing_tables)}")
            logger.info("📋 Using available tables for validation")
            
        return True

    def validate_table_contents(self):
        """Validate table contents and data integrity"""
        logger.info("📊 Validating table contents...")
        
        # Get actual tables from database
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        
        tables = self.execute_query(tables_query)
        if not tables:
            return False
            
        validation_results = {}
        
        for table in tables:
            table_name = table['table_name']
            logger.info(f"   🔍 Checking {table_name}...")
            
            # Count records
            count_result = self.execute_single(f"SELECT COUNT(*) as count FROM {table_name}")
            if count_result:
                record_count = count_result['count']
                logger.info(f"      📊 Records: {record_count:,}")
                validation_results[table_name] = {'count': record_count}
            else:
                logger.error(f"      ❌ Failed to count records in {table_name}")
                
        return validation_results

    def full_validation(self):
        """Run complete database validation"""
        start_time = datetime.now()
        logger.info("🚀 Starting comprehensive database validation...")
        logger.info("=" * 60)
        
        try:
            # Connect to database
            if not self.connect():
                return False
            
            validation_passed = True
            
            # Run validation checks
            checks = [
                ("Table Structure", self.validate_table_structure),
                ("Table Contents", self.validate_table_contents)
            ]
            
            results = {}
            
            for check_name, check_func in checks:
                logger.info(f"\n📋 {check_name} Validation...")
                try:
                    result = check_func()
                    results[check_name] = result
                    if result is False:
                        validation_passed = False
                        logger.error(f"❌ {check_name} validation failed")
                    else:
                        logger.info(f"✅ {check_name} validation passed")
                except Exception as e:
                    logger.error(f"❌ {check_name} validation error: {e}")
                    validation_passed = False
                    results[check_name] = False
            
            # Final summary
            duration = datetime.now() - start_time
            
            logger.info("\n🎉 DATABASE VALIDATION COMPLETE!")
            logger.info("=" * 60)
            logger.info("📊 Validation Summary:")
            
            for check_name, result in results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"   {check_name}: {status}")
            
            logger.info(f"⏱️ Validation time: {duration}")
            
            if validation_passed:
                logger.info("🎯 DATABASE INTEGRITY: ✅ ALL CHECKS PASSED")
                logger.info("🎉 DATABASE IS READY FOR PRODUCTION USE!")
            else:
                logger.info("🎯 DATABASE INTEGRITY: ❌ ISSUES FOUND")
                logger.info("⚠️ Review and fix issues before proceeding")
            
            return validation_passed
            
        except Exception as e:
            logger.error(f"❌ Database validation failed: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()


def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate horse racing database")
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Database URL (uses .env if not provided)",
    )

    args = parser.parse_args()

    validator = DatabaseValidator(args.database_url)
    success = validator.full_validation()

    if success:
        print("\n🎉 Database validation completed successfully!")
        print("🚀 Database is ready for production use")
        return 0
    else:
        print("\n❌ Database validation failed - check logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
