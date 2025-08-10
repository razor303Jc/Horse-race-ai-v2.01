#!/usr/bin/env python3
"""
🗄️ Database Optimization Analysis - Priority 2A

Analyzes current database performance and identifies optimization opportunities.
Focus: Indexes, constraints, query optimization for 250K+ record scaling.

Priority: 2A (High Impact, Medium Effort - 2 hours implementation)
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple

import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseOptimizationAnalyzer:
    """
    Analyzes database performance and recommends optimizations.

    Focus areas:
    - Query performance analysis
    - Index effectiveness assessment
    - Constraint validation
    - Storage optimization
    - Scaling readiness for 250K records
    """

    def __init__(self):
        """Initialize the database optimization analyzer."""
        self.connection = None
        self.cursor = None
        self.analysis_results = {}
        logger.info("🗄️ Database Optimization Analyzer initialized")

    def connect_database(self):
        """Connect to the horse racing database."""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                port=5433,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            self.cursor = self.connection.cursor()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def analyze_table_sizes(self) -> Dict[str, Dict]:
        """Analyze table sizes and storage usage."""
        logger.info("📊 Analyzing table sizes and storage...")

        size_analysis = {}
        tables = [
            "race_results",
            "horses",
            "jockey_stats",
            "trainer_stats",
            "races_cards",
            "racecard_details",
        ]

        for table in tables:
            try:
                # Get record count
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                record_count = self.cursor.fetchone()[0]

                # Get table size
                self.cursor.execute(
                    f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table}')) as size,
                           pg_total_relation_size('{table}') as size_bytes
                """
                )
                size_result = self.cursor.fetchone()

                size_analysis[table] = {
                    "records": record_count,
                    "size_pretty": size_result[0],
                    "size_bytes": size_result[1],
                    "avg_record_size": size_result[1] / max(record_count, 1),
                }

            except Exception as e:
                logger.warning(f"❌ Error analyzing {table}: {e}")
                size_analysis[table] = {"error": str(e)}

        self.analysis_results["table_sizes"] = size_analysis
        return size_analysis

    def analyze_index_usage(self) -> Dict[str, Dict]:
        """Analyze index usage and effectiveness."""
        logger.info("🔍 Analyzing index usage and effectiveness...")

        try:
            # Get index usage statistics
            self.cursor.execute(
                """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    CASE 
                        WHEN idx_tup_read > 0 THEN 
                            ROUND((idx_tup_fetch::numeric / idx_tup_read) * 100, 2)
                        ELSE 0 
                    END as efficiency_pct
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY idx_tup_read DESC
            """
            )

            index_stats = []
            for row in self.cursor.fetchall():
                index_stats.append(
                    {
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2],
                        "reads": row[3],
                        "fetches": row[4],
                        "efficiency": row[5],
                    }
                )

            self.analysis_results["index_usage"] = index_stats
            return index_stats

        except Exception as e:
            logger.error(f"❌ Error analyzing indexes: {e}")
            return {}

    def analyze_query_performance(self) -> Dict[str, float]:
        """Test common query performance."""
        logger.info("⚡ Analyzing query performance...")

        performance_tests = {}

        # Test queries with timing
        test_queries = [
            (
                "select_by_date",
                "SELECT COUNT(*) FROM race_results WHERE race_date >= '2023-01-01'",
            ),
            (
                "select_by_course",
                "SELECT COUNT(*) FROM race_results WHERE course = 'Flemington'",
            ),
            (
                "select_by_jockey",
                "SELECT COUNT(*) FROM race_results WHERE jockey_name = 'Unknown'",
            ),
            (
                "select_by_trainer",
                "SELECT COUNT(*) FROM race_results WHERE trainer_name = 'Unknown'",
            ),
            (
                "join_horses_results",
                """
                SELECT COUNT(*) 
                FROM race_results rr 
                JOIN horses h ON rr.horse_name = h.horse_name 
                LIMIT 1000
            """,
            ),
            (
                "aggregate_by_course",
                """
                SELECT course, COUNT(*), AVG(win_odds) 
                FROM race_results 
                GROUP BY course 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            """,
            ),
        ]

        for test_name, query in test_queries:
            try:
                start_time = time.time()
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                end_time = time.time()

                execution_time = (
                    end_time - start_time
                ) * 1000  # Convert to milliseconds
                performance_tests[test_name] = {
                    "execution_time_ms": round(execution_time, 2),
                    "result_count": len(result),
                }

            except Exception as e:
                logger.warning(f"❌ Query test {test_name} failed: {e}")
                performance_tests[test_name] = {"error": str(e)}

        self.analysis_results["query_performance"] = performance_tests
        return performance_tests

    def analyze_foreign_key_opportunities(self) -> List[Dict]:
        """Identify potential foreign key relationships."""
        logger.info("🔗 Analyzing foreign key opportunities...")

        opportunities = []

        # Check for relationship patterns
        relationship_queries = [
            {
                "name": "race_results_to_horses",
                "description": "Link race_results.horse_name to horses.horse_name",
                "query": """
                    SELECT COUNT(DISTINCT rr.horse_name) as race_horses,
                           COUNT(DISTINCT h.horse_name) as master_horses,
                           COUNT(DISTINCT rr.horse_name) - COUNT(DISTINCT h.horse_name) as missing_horses
                    FROM race_results rr
                    LEFT JOIN horses h ON rr.horse_name = h.horse_name
                """,
            },
            {
                "name": "race_results_to_jockey_stats",
                "description": "Link race_results.jockey_name to jockey_stats.jockey_name",
                "query": """
                    SELECT COUNT(DISTINCT rr.jockey_name) as result_jockeys,
                           COUNT(DISTINCT js.jockey_name) as stats_jockeys
                    FROM race_results rr
                    LEFT JOIN jockey_stats js ON rr.jockey_name = js.jockey_name
                """,
            },
            {
                "name": "race_results_to_trainer_stats",
                "description": "Link race_results.trainer_name to trainer_stats.trainer_name",
                "query": """
                    SELECT COUNT(DISTINCT rr.trainer_name) as result_trainers,
                           COUNT(DISTINCT ts.trainer_name) as stats_trainers
                    FROM race_results rr
                    LEFT JOIN trainer_stats ts ON rr.trainer_name = ts.trainer_name
                """,
            },
        ]

        for relationship in relationship_queries:
            try:
                self.cursor.execute(relationship["query"])
                result = self.cursor.fetchone()

                opportunities.append(
                    {
                        "name": relationship["name"],
                        "description": relationship["description"],
                        "analysis": result,
                        "viable": True,  # All relationships are viable with proper cleanup
                    }
                )

            except Exception as e:
                logger.warning(
                    f"❌ Relationship analysis {relationship['name']} failed: {e}"
                )

        self.analysis_results["foreign_key_opportunities"] = opportunities
        return opportunities

    def check_data_integrity(self) -> Dict[str, Dict]:
        """Check data integrity issues."""
        logger.info("🔍 Checking data integrity...")

        integrity_checks = {}

        # Check for NULL values in important columns
        null_checks = [
            ("race_results", "horse_name"),
            ("race_results", "jockey_name"),
            ("race_results", "trainer_name"),
            ("race_results", "race_date"),
            ("horses", "horse_name"),
            ("jockey_stats", "jockey_name"),
            ("trainer_stats", "trainer_name"),
        ]

        for table, column in null_checks:
            try:
                self.cursor.execute(
                    f"""
                    SELECT COUNT(*) as total_records,
                           COUNT({column}) as non_null_records,
                           COUNT(*) - COUNT({column}) as null_records
                    FROM {table}
                """
                )
                result = self.cursor.fetchone()

                integrity_checks[f"{table}.{column}"] = {
                    "total": result[0],
                    "non_null": result[1],
                    "null_count": result[2],
                    "null_percentage": round((result[2] / max(result[0], 1)) * 100, 2),
                }

            except Exception as e:
                logger.warning(f"❌ Integrity check {table}.{column} failed: {e}")

        self.analysis_results["data_integrity"] = integrity_checks
        return integrity_checks

    def generate_optimization_recommendations(self) -> List[Dict]:
        """Generate optimization recommendations based on analysis."""
        logger.info("💡 Generating optimization recommendations...")

        recommendations = []

        # Analyze results and create recommendations
        table_sizes = self.analysis_results.get("table_sizes", {})
        query_performance = self.analysis_results.get("query_performance", {})

        # Storage optimization recommendations
        for table, data in table_sizes.items():
            if isinstance(data, dict) and "records" in data:
                records = data["records"]

                if records > 5000:  # Large tables
                    recommendations.append(
                        {
                            "priority": "HIGH",
                            "category": "Storage Optimization",
                            "table": table,
                            "recommendation": f"Consider partitioning {table} by date for better performance",
                            "impact": "Significant query performance improvement for date-based queries",
                            "effort": "Medium",
                        }
                    )

        # Query performance recommendations
        for test_name, result in query_performance.items():
            if isinstance(result, dict) and "execution_time_ms" in result:
                exec_time = result["execution_time_ms"]

                if exec_time > 100:  # Slow queries
                    recommendations.append(
                        {
                            "priority": "MEDIUM",
                            "category": "Query Performance",
                            "test": test_name,
                            "recommendation": f"Optimize {test_name} query (currently {exec_time}ms)",
                            "impact": "Faster application response times",
                            "effort": "Low",
                        }
                    )

        # Foreign key recommendations
        fk_opportunities = self.analysis_results.get("foreign_key_opportunities", [])
        for opportunity in fk_opportunities:
            if opportunity.get("viable"):
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "category": "Data Integrity",
                        "relationship": opportunity["name"],
                        "recommendation": f"Add foreign key constraint: {opportunity['description']}",
                        "impact": "Improved data integrity and query optimization",
                        "effort": "Low",
                    }
                )

        self.analysis_results["recommendations"] = recommendations
        return recommendations

    def run_complete_analysis(self) -> Dict:
        """Run the complete database optimization analysis."""
        logger.info("🚀 Starting complete database optimization analysis...")

        if not self.connect_database():
            return {"error": "Failed to connect to database"}

        try:
            # Run all analysis components
            self.analyze_table_sizes()
            self.analyze_index_usage()
            self.analyze_query_performance()
            self.analyze_foreign_key_opportunities()
            self.check_data_integrity()
            self.generate_optimization_recommendations()

            logger.info("✅ Database optimization analysis complete")
            return self.analysis_results

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {"error": str(e)}

        finally:
            if self.connection:
                self.connection.close()

    def print_analysis_summary(self):
        """Print a formatted summary of the analysis results."""
        if not self.analysis_results:
            print("❌ No analysis results available")
            return

        print("🗄️ Database Optimization Analysis - Priority 2A")
        print("=" * 60)

        # Table sizes summary
        if "table_sizes" in self.analysis_results:
            print("\n📊 Table Sizes:")
            for table, data in self.analysis_results["table_sizes"].items():
                if isinstance(data, dict) and "records" in data:
                    print(
                        f"   {table:20}: {data['records']:,} records ({data['size_pretty']})"
                    )

        # Query performance summary
        if "query_performance" in self.analysis_results:
            print("\n⚡ Query Performance:")
            for test, result in self.analysis_results["query_performance"].items():
                if isinstance(result, dict) and "execution_time_ms" in result:
                    status = "🔴" if result["execution_time_ms"] > 100 else "🟢"
                    print(f"   {status} {test:25}: {result['execution_time_ms']}ms")

        # Recommendations summary
        if "recommendations" in self.analysis_results:
            print(
                f"\n💡 Optimization Recommendations ({len(self.analysis_results['recommendations'])}):"
            )
            for i, rec in enumerate(self.analysis_results["recommendations"][:5], 1):
                priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡"
                print(f"   {priority_icon} {i}. {rec['recommendation']}")

            if len(self.analysis_results["recommendations"]) > 5:
                print(
                    f"      ... and {len(self.analysis_results['recommendations']) - 5} more"
                )

        print("\n🎯 Next Steps:")
        print("   1. Review optimization recommendations")
        print("   2. Implement high-priority optimizations")
        print("   3. Add foreign key constraints")
        print("   4. Test performance improvements")


def main():
    """Run the database optimization analysis."""
    analyzer = DatabaseOptimizationAnalyzer()
    results = analyzer.run_complete_analysis()

    if "error" in results:
        print(f"❌ Analysis failed: {results['error']}")
        return

    analyzer.print_analysis_summary()

    print(f"\n🎉 Database optimization analysis complete!")
    print(f"📋 Ready to implement Priority 2A optimizations")


if __name__ == "__main__":
    main()
