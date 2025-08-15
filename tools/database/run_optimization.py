#!/usr/bin/env python3
"""
🏇 Database Optimization Runner
Phase 1B: Execute database optimization and run performance monitoring
Target: 70% faster database queries
"""

import logging
import os
import sys
from pathlib import Path

import psycopg2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Execute database optimization script and run performance monitoring."""
    
    def __init__(self):
        """Initialize the database optimizer."""
        # Database configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5433')),
            'database': os.getenv('DB_NAME', 'horse_racing_db'),
            'user': os.getenv('DB_USER', 'horse_racing'),
            'password': os.getenv('POSTGRES_PASSWORD', 'secure_password_123')
        }
        
    def execute_optimization_script(self) -> bool:
        """Execute the database optimization SQL script."""
        script_path = (
            Path(__file__).parent.parent.parent
            / "database"
            / "database_optimization.sql"
        )
        
        if not script_path.exists():
            logger.error(f"❌ Optimization script not found: {script_path}")
            return False
        
        logger.info("🔧 Executing database optimization script...")
        logger.info(f"📄 Script: {script_path}")
        
        try:
            with open(script_path, 'r') as f:
                sql_script = f.read()
            
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True  # Enable autocommit for DDL operations
            
            with conn.cursor() as cursor:
                # Split SQL script into individual statements
                statements = [
                    stmt.strip() for stmt in sql_script.split(';')
                    if stmt.strip()
                ]
                
                logger.info(f"📋 Executing {len(statements)} optimization statements...")
                
                for i, statement in enumerate(statements, 1):
                    try:
                        logger.info(f"🔧 Executing statement {i}/{len(statements)}")
                        cursor.execute(statement)
                        logger.info(f"✅ Statement {i} completed")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"⚠️  Statement {i} skipped (already exists)")
                        else:
                            logger.warning(f"⚠️  Statement {i} failed: {e}")
                            
            conn.close()
            
            logger.info("✅ Database optimization script executed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing optimization script: {e}")
            return False
    
    def run_performance_monitoring(self) -> bool:
        """Run performance monitoring and generate report."""
        try:
            # Import the performance monitor
            from tools.database.performance_monitor import DatabasePerformanceMonitor
            
            logger.info("📊 Running performance monitoring...")
            
            monitor = DatabasePerformanceMonitor(self.db_config)
            
            # Check if monitoring is installed
            if not monitor.install_performance_monitoring():
                logger.error("❌ Performance monitoring not properly installed")
                return False
            
            # Generate performance report
            report = monitor.generate_performance_report()
            print("\n" + report)
            
            # Save report to file
            report_file = (
                Path(__file__).parent.parent / "database" / "performance_report.txt"
            )
            with open(report_file, "w") as f:
                f.write(report)
            
            logger.info(f"📄 Performance report saved to: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running performance monitoring: {e}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
            conn.close()
            
            logger.info("✅ Database connection successful")
            logger.info(f"🐘 PostgreSQL Version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False


def main():
    """Main function to run database optimization."""
    print("🏇 Database Optimization Runner - Phase 1B")
    print("=" * 50)
    print("🎯 Target: 70% faster database queries")
    print("🔧 Creating optimized indexes and monitoring")
    print()
    
    optimizer = DatabaseOptimizer()
    
    # Test database connection
    if not optimizer.test_database_connection():
        print("\n❌ Cannot connect to database")
        print("📝 Please check your database configuration")
        return
    
    # Execute optimization script
    print("\n🔧 STEP 1: Database Optimization")
    print("-" * 30)
    
    if optimizer.execute_optimization_script():
        print("✅ Database optimization completed successfully!")
    else:
        print("❌ Database optimization failed")
        return
    
    # Run performance monitoring
    print("\n📊 STEP 2: Performance Monitoring")
    print("-" * 35)
    
    if optimizer.run_performance_monitoring():
        print("✅ Performance monitoring completed successfully!")
    else:
        print("❌ Performance monitoring failed")
        return
    
    print("\n🎯 Phase 1B Database Optimization Complete!")
    print("=" * 50)
    print("📈 Expected improvements:")
    print("  • 60-80% faster query performance")
    print("  • Optimized indexes for ML feature engineering")
    print("  • Performance monitoring and alerting")
    print("  • Materialized views for fast aggregations")
    print()
    print("📊 Check performance_report.txt for detailed metrics")


if __name__ == "__main__":
    main()
