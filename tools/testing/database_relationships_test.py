#!/usr/bin/env python3
"""
Database Relationships Test Script

This script tests the relationships between tables in the horse racing database
and validates data integrity.
"""

import sys
from datetime import datetime

import psycopg2


class DatabaseRelationshipTester:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to database successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Disconnect from the database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Disconnected from database")

    def get_table_info(self):
        """Get information about all tables"""
        print("\n📊 Table Information:")
        print("=" * 60)

        # Get all tables in the public schema
        self.cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """
        )

        tables = [row[0] for row in self.cursor.fetchall()]

        for table_name in tables:
            # Get row count
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} rows")

        return tables

    def check_foreign_key_constraints(self):
        """Check existing foreign key constraints"""
        print("\n🔗 Foreign Key Constraints:")
        print("=" * 60)

        self.cursor.execute(
            """
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, tc.constraint_name
        """
        )

        constraints = self.cursor.fetchall()

        if not constraints:
            print("  ⚠️  No foreign key constraints found")
        else:
            for constraint in constraints:
                print(
                    f"  {constraint[1]}.{constraint[2]} -> {constraint[3]}.{constraint[4]}"
                )

        return len(constraints)

    def analyze_potential_relationships(self):
        """Analyze potential relationships between tables"""
        print("\n🔍 Potential Relationships Analysis:")
        print("=" * 60)

        # Check records table relationships
        print("\n  Records Table Relationships:")

        # Records -> Races
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM records r
            LEFT JOIN races ra ON r.race_id = ra.race_id
            WHERE ra.race_id IS NULL AND r.race_id IS NOT NULL
        """
        )
        orphaned_records = self.cursor.fetchone()[0]

        if orphaned_records > 0:
            print(f"    ⚠️  {orphaned_records} records reference non-existent races")
        else:
            print("    ✅ All records with race_id reference existing races")

        # Check horse relationships
        print("\n  Horse Relationships:")

        # Count unique horses in records vs horses table
        self.cursor.execute(
            "SELECT COUNT(DISTINCT horse) FROM records WHERE horse IS NOT NULL"
        )
        unique_horses_in_records = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(DISTINCT horse_name) FROM horses WHERE horse_name IS NOT NULL"
        )
        unique_horses_in_horses_table = self.cursor.fetchone()[0]

        # Check horses in records that don't exist in horses table
        self.cursor.execute(
            """
            SELECT COUNT(DISTINCT r.horse) 
            FROM records r
            LEFT JOIN horses h ON r.horse = h.horse_name
            WHERE r.horse IS NOT NULL 
            AND h.horse_name IS NULL
        """
        )
        horses_missing_from_horses_table = self.cursor.fetchone()[0]

        print(f"    Unique horses in records: {unique_horses_in_records}")
        print(f"    Unique horses in horses table: {unique_horses_in_horses_table}")

        if horses_missing_from_horses_table > 0:
            print(
                f"    ⚠️  {horses_missing_from_horses_table} horses in records not found in horses table"
            )
        else:
            print("    ✅ All horses in records exist in horses table")

        # Check jockey relationships
        print("\n  Jockey Relationships:")

        # Count unique jockeys in records vs jockeys_stats table
        self.cursor.execute(
            "SELECT COUNT(DISTINCT jockey) FROM records WHERE jockey IS NOT NULL"
        )
        unique_jockeys_in_records = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(DISTINCT jockey_name) FROM jockeys_stats WHERE jockey_name IS NOT NULL"
        )
        unique_jockeys_in_jockeys_table = self.cursor.fetchone()[0]

        # Check jockeys in records that don't exist in jockeys_stats table
        self.cursor.execute(
            """
            SELECT COUNT(DISTINCT r.jockey) 
            FROM records r
            LEFT JOIN jockeys_stats j ON r.jockey = j.jockey_name
            WHERE r.jockey IS NOT NULL 
            AND j.jockey_name IS NULL
        """
        )
        jockeys_missing_from_jockeys_table = self.cursor.fetchone()[0]

        print(f"    Unique jockeys in records: {unique_jockeys_in_records}")
        print(
            f"    Unique jockeys in jockeys_stats table: {unique_jockeys_in_jockeys_table}"
        )

        if jockeys_missing_from_jockeys_table > 0:
            print(
                f"    ⚠️  {jockeys_missing_from_jockeys_table} jockeys in records not found in jockeys_stats table"
            )
        else:
            print("    ✅ All jockeys in records exist in jockeys_stats table")

        # Check trainer relationships
        print("\n  Trainer Relationships:")

        # Count unique trainers in records vs trainers_stats table
        self.cursor.execute(
            "SELECT COUNT(DISTINCT trainer) FROM records WHERE trainer IS NOT NULL"
        )
        unique_trainers_in_records = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(DISTINCT trainer_name) FROM trainers_stats WHERE trainer_name IS NOT NULL"
        )
        unique_trainers_in_trainers_table = self.cursor.fetchone()[0]

        # Check trainers in records that don't exist in trainers_stats table
        self.cursor.execute(
            """
            SELECT COUNT(DISTINCT r.trainer) 
            FROM records r
            LEFT JOIN trainers_stats t ON r.trainer = t.trainer_name
            WHERE r.trainer IS NOT NULL 
            AND t.trainer_name IS NULL
        """
        )
        trainers_missing_from_trainers_table = self.cursor.fetchone()[0]

        print(f"    Unique trainers in records: {unique_trainers_in_records}")
        print(
            f"    Unique trainers in trainers_stats table: {unique_trainers_in_trainers_table}"
        )

        if trainers_missing_from_trainers_table > 0:
            print(
                f"    ⚠️  {trainers_missing_from_trainers_table} trainers in records not found in trainers_stats table"
            )
        else:
            print("    ✅ All trainers in records exist in trainers_stats table")

    def check_data_quality(self):
        """Check data quality issues"""
        print("\n🔍 Data Quality Analysis:")
        print("=" * 60)

        # Check for NULL values in key fields
        tables_to_check = {
            "records": ["race_id", "horse", "jockey", "trainer"],
            "races": ["race_id", "race_name"],
            "horses": ["horse_name"],
            "jockeys_stats": ["jockey_name"],
            "trainers_stats": ["trainer_name"],
        }

        for table, columns in tables_to_check.items():
            print(f"\n  {table.upper()} Table:")

            # Get total row count
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_rows = self.cursor.fetchone()[0]

            for column in columns:
                # Check NULL values
                self.cursor.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL OR {column} = ''"
                )
                null_count = self.cursor.fetchone()[0]

                percentage = (null_count / total_rows * 100) if total_rows > 0 else 0

                if null_count > 0:
                    print(
                        f"    ⚠️  {column}: {null_count}/{total_rows} NULL/empty ({percentage:.1f}%)"
                    )
                else:
                    print(f"    ✅ {column}: No NULL/empty values")

    def suggest_foreign_keys(self):
        """Suggest foreign key constraints that could be added"""
        print("\n💡 Suggested Foreign Key Constraints:")
        print("=" * 60)

        suggestions = [
            "ALTER TABLE records ADD CONSTRAINT fk_records_race_id FOREIGN KEY (race_id) REFERENCES races(race_id);",
            "ALTER TABLE records ADD CONSTRAINT fk_records_horse FOREIGN KEY (horse) REFERENCES horses(horse_name);",
            "ALTER TABLE records ADD CONSTRAINT fk_records_jockey FOREIGN KEY (jockey) REFERENCES jockeys_stats(jockey_name);",
            "ALTER TABLE records ADD CONSTRAINT fk_records_trainer FOREIGN KEY (trainer) REFERENCES trainers_stats(trainer_name);",
        ]

        print("\n  Recommended SQL commands to establish relationships:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"    {i}. {suggestion}")

        print(
            "\n  ⚠️  Note: These should only be added after ensuring data consistency!"
        )

    def run_all_tests(self):
        """Run all relationship tests"""
        print(
            f"🏇 Database Relationship Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 80)

        if not self.connect():
            return False

        try:
            self.get_table_info()
            self.check_foreign_key_constraints()
            self.analyze_potential_relationships()
            self.check_data_quality()
            self.suggest_foreign_keys()

            print("\n✅ Database relationship analysis completed successfully!")
            return True

        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            return False

        finally:
            self.disconnect()


def main():
    """Main function"""
    tester = DatabaseRelationshipTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎯 Next Steps:")
        print("  1. Review the relationship analysis above")
        print("  2. Clean up any data inconsistencies")
        print("  3. Add foreign key constraints for data integrity")
        print("  4. Consider adding indexes for better performance")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
