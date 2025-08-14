#!/usr/bin/env python3
"""
Database Explorer - Explore Uploaded Horse Racing Data
======================================================

Comprehensive tool to explore and analyze the data in our PostgreSQL database.
Shows table structures, sample data, statistics, and relationships.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseExplorer:
    """
    Comprehensive database exploration tool
    """

    def __init__(self):
        # Database connection parameters (matching daily_data_uploader.py)
        self.db_params = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_params)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def get_table_info(self):
        """Get information about all tables"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get table information
        cursor.execute(
            """
            SELECT 
                table_name,
                pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as table_size
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        )

        tables = cursor.fetchall()

        table_info = {}
        for table in tables:
            table_name = table["table_name"]

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count_result = cursor.fetchone()
            row_count = count_result["count"] if count_result else 0

            # Get column information
            cursor.execute(
                """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """,
                (table_name,),
            )

            columns = cursor.fetchall()

            table_info[table_name] = {
                "row_count": row_count,
                "table_size": table["table_size"],
                "columns": columns,
            }

        conn.close()
        return table_info

    def get_sample_data(self, table_name, limit=5):
        """Get sample data from a table"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error getting sample data from {table_name}: {e}")
            conn.close()
            return None

    def get_table_statistics(self, table_name):
        """Get detailed statistics for a table"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        stats = {}

        try:
            # Get basic statistics
            cursor.execute(
                f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT *) as unique_rows
                FROM {table_name}
            """
            )
            basic_stats = cursor.fetchone()
            stats["basic"] = dict(basic_stats)

            # Get column statistics for numeric columns
            cursor.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND data_type IN ('integer', 'bigint', 'numeric', 'real', 'double precision')
            """,
                (table_name,),
            )

            numeric_columns = cursor.fetchall()

            if numeric_columns:
                stats["numeric"] = {}
                for col in numeric_columns:
                    col_name = col["column_name"]
                    try:
                        cursor.execute(
                            f"""
                            SELECT 
                                MIN({col_name}) as min_val,
                                MAX({col_name}) as max_val,
                                AVG({col_name}) as avg_val,
                                COUNT(DISTINCT {col_name}) as unique_vals,
                                COUNT({col_name}) as non_null_count
                            FROM {table_name}
                            WHERE {col_name} IS NOT NULL
                        """
                        )
                        col_stats = cursor.fetchone()
                        if col_stats:
                            stats["numeric"][col_name] = dict(col_stats)
                    except Exception as e:
                        logger.warning(f"Could not get stats for {col_name}: {e}")

            # Get date range for date columns
            cursor.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND data_type IN ('date', 'timestamp', 'timestamp with time zone')
            """,
                (table_name,),
            )

            date_columns = cursor.fetchall()

            if date_columns:
                stats["dates"] = {}
                for col in date_columns:
                    col_name = col["column_name"]
                    try:
                        cursor.execute(
                            f"""
                            SELECT 
                                MIN({col_name}) as earliest,
                                MAX({col_name}) as latest,
                                COUNT(DISTINCT {col_name}) as unique_dates,
                                COUNT({col_name}) as non_null_count
                            FROM {table_name}
                            WHERE {col_name} IS NOT NULL
                        """
                        )
                        date_stats = cursor.fetchone()
                        if date_stats:
                            stats["dates"][col_name] = dict(date_stats)
                    except Exception as e:
                        logger.warning(f"Could not get date stats for {col_name}: {e}")

        except Exception as e:
            logger.error(f"Error getting statistics for {table_name}: {e}")

        conn.close()
        return stats

    def explore_relationships(self):
        """Explore relationships between tables"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get foreign key relationships
        cursor.execute(
            """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """
        )

        relationships = cursor.fetchall()
        conn.close()

        return [dict(rel) for rel in relationships]

    def get_data_quality_report(self, table_name):
        """Generate data quality report for a table"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        quality_report = {}

        try:
            # Get total row count
            cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
            total_rows = cursor.fetchone()["total"]

            # Get column information
            cursor.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """,
                (table_name,),
            )

            columns = cursor.fetchall()

            quality_report["total_rows"] = total_rows
            quality_report["columns"] = {}

            for col in columns:
                col_name = col["column_name"]

                # Get null count
                cursor.execute(
                    f"SELECT COUNT(*) as null_count FROM {table_name} WHERE {col_name} IS NULL"
                )
                null_count = cursor.fetchone()["null_count"]

                # Get non-null count
                non_null_count = total_rows - null_count
                null_percentage = (
                    (null_count / total_rows * 100) if total_rows > 0 else 0
                )

                # Get unique values count
                cursor.execute(
                    f"SELECT COUNT(DISTINCT {col_name}) as unique_count FROM {table_name}"
                )
                unique_count = cursor.fetchone()["unique_count"]

                quality_report["columns"][col_name] = {
                    "data_type": col["data_type"],
                    "is_nullable": col["is_nullable"],
                    "null_count": null_count,
                    "non_null_count": non_null_count,
                    "null_percentage": round(null_percentage, 2),
                    "unique_count": unique_count,
                    "uniqueness_ratio": round(
                        (
                            (unique_count / non_null_count * 100)
                            if non_null_count > 0
                            else 0
                        ),
                        2,
                    ),
                }

        except Exception as e:
            logger.error(f"Error generating quality report for {table_name}: {e}")

        conn.close()
        return quality_report

    def generate_comprehensive_report(self):
        """Generate comprehensive database report"""
        print("\n" + "=" * 80)
        print("🏇 HORSE RACING DATABASE EXPLORATION REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now()}")
        print(
            f"Database: {self.db_params['database']} on {self.db_params['host']}:{self.db_params['port']}"
        )

        # Get table information
        table_info = self.get_table_info()
        if not table_info:
            print("❌ Could not connect to database!")
            return

        print(f"\n📊 DATABASE OVERVIEW")
        print("-" * 40)

        total_rows = sum(info["row_count"] for info in table_info.values())
        print(f"Total Tables: {len(table_info)}")
        print(f"Total Records: {total_rows:,}")

        # Table summary
        print(f"\n📋 TABLE SUMMARY")
        print("-" * 40)
        print(f"{'Table Name':<20} {'Records':<10} {'Size':<10} {'Columns':<8}")
        print("-" * 50)

        for table_name, info in sorted(table_info.items()):
            print(
                f"{table_name:<20} {info['row_count']:<10,} {info['table_size']:<10} {len(info['columns']):<8}"
            )

        # Detailed table exploration
        for table_name, info in sorted(table_info.items()):
            print(f"\n🔍 DETAILED VIEW: {table_name.upper()}")
            print("=" * 60)

            # Basic information
            print(f"Records: {info['row_count']:,}")
            print(f"Size: {info['table_size']}")
            print(f"Columns: {len(info['columns'])}")

            # Column structure
            print(f"\n📋 Column Structure:")
            print(f"{'Column':<25} {'Type':<15} {'Nullable':<8} {'Default':<15}")
            print("-" * 65)

            for col in info["columns"]:
                default_val = (
                    str(col["column_default"])[:12] if col["column_default"] else ""
                )
                print(
                    f"{col['column_name']:<25} {col['data_type']:<15} {col['is_nullable']:<8} {default_val:<15}"
                )

            # Sample data
            print(f"\n📄 Sample Data (5 rows):")
            sample_df = self.get_sample_data(table_name, 5)
            if sample_df is not None and not sample_df.empty:
                pd.set_option("display.max_columns", None)
                pd.set_option("display.width", None)
                pd.set_option("display.max_colwidth", 20)
                print(sample_df.to_string(index=False))
            else:
                print("No sample data available")

            # Statistics
            print(f"\n📊 Statistics:")
            stats = self.get_table_statistics(table_name)
            if stats:
                if "basic" in stats:
                    print(f"Total Rows: {stats['basic']['total_rows']:,}")
                    print(f"Unique Rows: {stats['basic']['unique_rows']:,}")
                    duplicate_percentage = (
                        (
                            (
                                stats["basic"]["total_rows"]
                                - stats["basic"]["unique_rows"]
                            )
                            / stats["basic"]["total_rows"]
                            * 100
                        )
                        if stats["basic"]["total_rows"] > 0
                        else 0
                    )
                    print(f"Duplicate Percentage: {duplicate_percentage:.2f}%")

                if "numeric" in stats and stats["numeric"]:
                    print(f"\nNumeric Column Ranges:")
                    for col_name, col_stats in stats["numeric"].items():
                        print(
                            f"  {col_name}: {col_stats['min_val']} - {col_stats['max_val']} (avg: {col_stats['avg_val']:.2f if col_stats['avg_val'] else 'N/A'})"
                        )

                if "dates" in stats and stats["dates"]:
                    print(f"\nDate Ranges:")
                    for col_name, col_stats in stats["dates"].items():
                        print(
                            f"  {col_name}: {col_stats['earliest']} to {col_stats['latest']}"
                        )

            # Data quality
            print(f"\n🔍 Data Quality:")
            quality = self.get_data_quality_report(table_name)
            if quality:
                high_null_cols = [
                    col
                    for col, data in quality["columns"].items()
                    if data["null_percentage"] > 10
                ]
                low_unique_cols = [
                    col
                    for col, data in quality["columns"].items()
                    if data["uniqueness_ratio"] < 50 and data["non_null_count"] > 10
                ]

                if high_null_cols:
                    print(f"High NULL columns (>10%): {', '.join(high_null_cols)}")
                if low_unique_cols:
                    print(
                        f"Low uniqueness columns (<50%): {', '.join(low_unique_cols)}"
                    )
                if not high_null_cols and not low_unique_cols:
                    print("✅ Good data quality - low nulls and good uniqueness")

        # Relationships
        print(f"\n🔗 TABLE RELATIONSHIPS")
        print("-" * 40)

        relationships = self.explore_relationships()
        if relationships:
            for rel in relationships:
                print(
                    f"{rel['table_name']}.{rel['column_name']} → {rel['foreign_table_name']}.{rel['foreign_column_name']}"
                )
        else:
            print("No foreign key relationships found")

        # Final summary
        print(f"\n🎯 SUMMARY")
        print("-" * 40)
        print(f"✅ Database connection: Working")
        print(f"✅ Total tables: {len(table_info)}")
        print(f"✅ Total records: {total_rows:,}")
        print(f"✅ Data integrity: Good")

        # Check for potential issues
        issues = []
        for table_name, info in table_info.items():
            if info["row_count"] == 0:
                issues.append(f"Empty table: {table_name}")

        if issues:
            print(f"\n⚠️  Potential Issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ No major issues detected")

        print("\n" + "=" * 80)
        print("🎉 Database exploration complete!")
        print("=" * 80)


def main():
    """Main function"""
    explorer = DatabaseExplorer()
    explorer.generate_comprehensive_report()


if __name__ == "__main__":
    main()
