#!/usr/bin/env python3
"""
🏇 Database Performance Monitor
Phase 1B: Performance Monitoring & Query Optimization
Target: Track query performance and identify bottlenecks
"""

import logging
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2
import yaml
from psycopg2.extras import DictCursor

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabasePerformanceMonitor:
    """Monitor and optimize database query performance."""
    
    def __init__(self, db_config: Optional[Dict] = None):
        """Initialize the performance monitor."""
        self.db_config = db_config or self._load_db_config()
        self.connection = None
        
    def _load_db_config(self) -> Dict:
        """Load database configuration."""
        # Try to load from environment or config file
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5433'),
            'database': os.getenv('DB_NAME', 'horse_racing_db'),
            'user': os.getenv('DB_USER', 'horse_racing'),
            'password': os.getenv('POSTGRES_PASSWORD', 'secure_password_123')
        }
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        try:
            if not self.connection or self.connection.closed:
                self.connection = psycopg2.connect(**self.db_config)
            yield self.connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if self.connection:
                self.connection.commit()
    
    def execute_timed_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        query_type: str = "unknown",
        description: str = ""
    ) -> Tuple[List, float]:
        """Execute a query and measure its performance."""
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                rows_returned = len(results)
                
                # Log performance
                self._log_query_performance(
                    query_type, description, execution_time, rows_returned
                )
                
                logger.info(
                    f"⚡ Query executed: {description} | "
                    f"Time: {execution_time:.2f}ms | Rows: {rows_returned}"
                )
                
                return results, execution_time
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Query failed: {description} | Error: {e}")
            self._log_query_performance(
                query_type, f"FAILED: {description}", execution_time, 0
            )
            raise
    
    def _log_query_performance(
        self,
        query_type: str,
        description: str,
        execution_time: float,
        rows_returned: int
    ):
        """Log query performance to database."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT log_query_performance(%s, %s, %s, %s)
                    """, (query_type, description, int(execution_time), rows_returned))
        except Exception as e:
            logger.warning(f"Failed to log performance: {e}")
    
    def benchmark_critical_queries(self) -> Dict[str, float]:
        """Benchmark critical queries used in ML training and analysis."""
        benchmarks = {}
        
        logger.info("🏁 Starting critical query benchmarks...")
        
        # 1. Race data retrieval for ML training
        query1 = """
        SELECT r.race_id, r.date, r.course, r.distance, r.race_type,
               rec.horse, rec.horse_id, rec.position, rec.sp, rec.draw,
               rec.jockey, rec.trainer, rec.age, rec.weight
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE r.date >= %s
        ORDER BY r.date DESC
        LIMIT 1000;
        """
        
        results, exec_time = self.execute_timed_query(
            query1, (datetime.now() - timedelta(days=30),),
            "ML_TRAINING", "Race data for ML training (30 days)"
        )
        benchmarks["ml_training_data"] = exec_time
        
        # 2. Horse performance aggregation
        query2 = """
        SELECT h.horse_name, h.percentage_wins, h.total_races,
               COUNT(rec.id) as recent_races,
               AVG(CASE WHEN rec.sp > 0 THEN rec.sp END) as avg_odds,
               AVG(rec.position::decimal) as avg_position
        FROM horses h
        LEFT JOIN records rec ON h.horse_id = rec.horse_id
        LEFT JOIN races r ON rec.race_id = r.race_id
        WHERE r.date >= %s
        GROUP BY h.horse_id, h.horse_name, h.percentage_wins, h.total_races
        HAVING COUNT(rec.id) > 0
        ORDER BY h.percentage_wins DESC
        LIMIT 500;
        """
        
        results, exec_time = self.execute_timed_query(
            query2, (datetime.now() - timedelta(days=90),),
            "HORSE_ANALYSIS", "Horse performance aggregation (90 days)"
        )
        benchmarks["horse_performance"] = exec_time
        
        # 3. Race summary for dashboard
        query3 = """
        SELECT r.race_id, r.race_name, r.course, r.date,
               COUNT(rec.id) as runners,
               MIN(CASE WHEN rec.sp > 0 THEN rec.sp END) as min_odds,
               MAX(CASE WHEN rec.sp > 0 THEN rec.sp END) as max_odds,
               MAX(CASE WHEN rec.position = 1 THEN rec.horse END) as winner
        FROM races r
        LEFT JOIN records rec ON r.race_id = rec.race_id
        WHERE r.date >= %s
        GROUP BY r.race_id, r.race_name, r.course, r.date
        ORDER BY r.date DESC
        LIMIT 100;
        """
        
        results, exec_time = self.execute_timed_query(
            query3, (datetime.now() - timedelta(days=7),),
            "DASHBOARD", "Race summary for dashboard (7 days)"
        )
        benchmarks["dashboard_summary"] = exec_time
        
        # 4. Jockey/Trainer performance lookup
        query4 = """
        SELECT j.jockey_name, j.percentage_wins, j.total_races,
               t.trainer_name, t.percentage_wins as trainer_win_pct,
               t.total_races as trainer_races
        FROM records rec
        JOIN jockeys_stats j ON rec.jockey_id::text = j.jockey_id
        JOIN trainers_stats t ON rec.trainer_id::text = t.trainer_id
        JOIN races r ON rec.race_id = r.race_id
        WHERE r.date >= %s
        GROUP BY j.jockey_id, j.jockey_name, j.percentage_wins, j.total_races,
                 t.trainer_id, t.trainer_name, t.percentage_wins, t.total_races
        LIMIT 500;
        """
        
        results, exec_time = self.execute_timed_query(
            query4, (datetime.now() - timedelta(days=30),),
            "CONNECTIONS", "Jockey/Trainer performance lookup (30 days)"
        )
        benchmarks["jockey_trainer_lookup"] = exec_time
        
        # 5. Feature engineering aggregation
        query5 = """
        SELECT race_id,
               AVG(CASE WHEN sp > 0 THEN sp END) as avg_odds,
               STDDEV(CASE WHEN sp > 0 THEN sp END) as odds_std,
               COUNT(*) as field_size,
               MIN(CASE WHEN sp > 0 THEN sp END) as favorite_odds,
               COUNT(CASE WHEN position = 1 THEN 1 END) as winners
        FROM records
        WHERE race_id IN (
            SELECT DISTINCT race_id FROM races
            WHERE date >= %s
            ORDER BY date DESC LIMIT 100
        )
        GROUP BY race_id;
        """
        
        results, exec_time = self.execute_timed_query(
            query5, (datetime.now() - timedelta(days=7),),
            "FEATURE_ENG", "Feature engineering aggregation (7 days)"
        )
        benchmarks["feature_engineering"] = exec_time
        
        return benchmarks
    
    def check_index_usage(self) -> List[Dict]:
        """Check index usage statistics."""
        query = """
        SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY idx_tup_read DESC;
        """
        
        results, _ = self.execute_timed_query(
            query, None, "ADMIN", "Index usage statistics"
        )
        
        return [dict(row) for row in results]
    
    def check_slow_queries(self, min_duration_ms: int = 1000) -> List[Dict]:
        """Check for slow queries in the performance log."""
        query = """
        SELECT query_type, query_description, execution_time_ms,
               rows_returned, timestamp
        FROM query_performance_log
        WHERE slow_query = TRUE AND timestamp >= %s
        ORDER BY execution_time_ms DESC
        LIMIT 50;
        """
        
        results, _ = self.execute_timed_query(
            query, (datetime.now() - timedelta(hours=24),),
            "ADMIN", "Recent slow queries (24h)"
        )
        
        return [dict(row) for row in results]
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""
        summary = {}
        
        # Query performance summary
        query = """
        SELECT query_type,
               COUNT(*) as total_queries,
               AVG(execution_time_ms) as avg_time_ms,
               MIN(execution_time_ms) as min_time_ms,
               MAX(execution_time_ms) as max_time_ms,
               COUNT(CASE WHEN slow_query THEN 1 END) as slow_queries
        FROM query_performance_log
        WHERE timestamp >= %s
        GROUP BY query_type
        ORDER BY avg_time_ms DESC;
        """
        
        results, _ = self.execute_timed_query(
            query, (datetime.now() - timedelta(hours=24),),
            "ADMIN", "Performance summary (24h)"
        )
        
        summary["query_performance"] = [dict(row) for row in results]
        
        # Table sizes
        query2 = """
        SELECT table_name,
               pg_size_pretty(pg_total_relation_size(table_name::regclass)) as size,
               pg_total_relation_size(table_name::regclass) as size_bytes
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY pg_total_relation_size(table_name::regclass) DESC;
        """
        
        results, _ = self.execute_timed_query(
            query2, None, "ADMIN", "Table sizes"
        )
        
        summary["table_sizes"] = [dict(row) for row in results]
        
        return summary
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        logger.info("📊 Generating performance report...")
        
        # Run benchmarks
        benchmarks = self.benchmark_critical_queries()
        index_usage = self.check_index_usage()
        slow_queries = self.check_slow_queries()
        summary = self.get_performance_summary()
        
        report = []
        report.append("🏇 DATABASE PERFORMANCE REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Benchmark results
        report.append("🏁 CRITICAL QUERY BENCHMARKS")
        report.append("-" * 30)
        for query_type, exec_time in benchmarks.items():
            if exec_time < 500:
                status = "✅ FAST"
            elif exec_time < 2000:
                status = "⚠️ SLOW"
            else:
                status = "❌ VERY SLOW"
            report.append(f"{query_type:<25}: {exec_time:>8.2f}ms {status}")
        report.append("")
        
        # Performance summary
        if summary.get("query_performance"):
            report.append("📈 QUERY PERFORMANCE SUMMARY (24h)")
            report.append("-" * 35)
            for perf in summary["query_performance"]:
                report.append(
                    f"{perf['query_type']:<15}: {perf['total_queries']:>4} queries, "
                    f"avg {perf['avg_time_ms']:>6.1f}ms, {perf['slow_queries']:>2} slow"
                )
            report.append("")
        
        # Index usage
        if index_usage:
            report.append("🔍 TOP INDEX USAGE")
            report.append("-" * 20)
            for idx in index_usage[:10]:
                report.append(
                    f"{idx['indexname']:<30}: {idx['idx_tup_read']:>8} reads"
                )
            report.append("")
        
        # Slow queries
        if slow_queries:
            report.append("🐌 RECENT SLOW QUERIES")
            report.append("-" * 25)
            for query in slow_queries[:5]:
                report.append(
                    f"{query['query_type']:<15}: {query['execution_time_ms']:>6}ms - "
                    f"{query['query_description'][:50]}..."
                )
            report.append("")
        
        # Table sizes
        if summary.get("table_sizes"):
            report.append("💾 TABLE SIZES")
            report.append("-" * 15)
            for table in summary["table_sizes"]:
                report.append(f"{table['table_name']:<20}: {table['size']:>10}")
            report.append("")
        
        report.append("🎯 OPTIMIZATION RECOMMENDATIONS")
        report.append("-" * 35)
        
        # Generate recommendations based on results
        recommendations = []
        
        if any(time > 1000 for time in benchmarks.values()):
            recommendations.append(
                "• Consider running database_optimization.sql if not done"
            )
            recommendations.append(
                "• Check for missing indexes on frequently queried columns"
            )

        if slow_queries:
            recommendations.append(
                f"• {len(slow_queries)} slow queries detected in last 24h"
            )
            recommendations.append(
                "• Review query patterns and consider optimization"
            )

        if not recommendations:
            recommendations.append("✅ Database performance is optimal!")
            recommendations.append("✅ All critical queries executing under 1000ms")
        
        report.extend(recommendations)
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def install_performance_monitoring(self):
        """Install performance monitoring setup."""
        logger.info("🔧 Installing performance monitoring...")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if optimization script has been run
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables
                        WHERE table_name = 'query_performance_log'
                    """)
                    
                    if cursor.fetchone()[0] == 0:
                        logger.warning("⚠️ Performance monitoring table not found!")
                        logger.info("📝 Please run database_optimization.sql first")
                        return False
                    
                    logger.info("✅ Performance monitoring is installed")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error checking performance monitoring: {e}")
            return False


def main():
    """Main function to run database performance monitoring."""
    print("🏇 Database Performance Monitor - Phase 1B")
    print("=" * 50)
    
    monitor = DatabasePerformanceMonitor()
    
    # Check if monitoring is installed
    if not monitor.install_performance_monitoring():
        print("\n❌ Performance monitoring not installed")
        print("📝 Please run database_optimization.sql first")
        return
    
    # Generate and display performance report
    try:
        report = monitor.generate_performance_report()
        print(report)
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "database" / "performance_report.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        print(f"📄 Report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"❌ Error generating performance report: {e}")
        return
    
    print("\n🎯 Performance monitoring complete!")


if __name__ == "__main__":
    main()
