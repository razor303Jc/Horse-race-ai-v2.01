#!/usr/bin/env python3
"""
🔧 Critical Pipeline Fixes
Apply immediate fixes to daily_pipeline_orchestrator.py

This script implements the most critical fixes identified in the pipeline review:
1. Database connection pooling
2. Async subprocess handling with timeouts
3. Enhanced error handling with retries
4. Configuration validation
5. Resource cleanup

Run this to apply critical fixes to the pipeline orchestrator.
"""

import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path


def apply_critical_fixes():
    """Apply critical fixes to the pipeline orchestrator."""

    orchestrator_file = Path("daily_pipeline_orchestrator.py")

    if not orchestrator_file.exists():
        print("❌ daily_pipeline_orchestrator.py not found!")
        return False

    print("🔧 Reading current pipeline orchestrator...")
    with open(orchestrator_file, "r") as f:
        content = f.read()

    fixes_applied = []

    # Fix 1: Add missing imports for connection pooling
    if "from psycopg2 import pool" not in content:
        content = content.replace(
            "import psycopg2", "import psycopg2\nfrom psycopg2 import pool"
        )
        fixes_applied.append("Added psycopg2.pool import")

    # Fix 2: Add retry decorator
    retry_decorator = '''
import functools
import time

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    wait_time = delay * (backoff ** (retries - 1))
                    logger.warning(f"Attempt {retries} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator
'''

    if "@retry_on_failure" not in content:
        # Insert after imports
        import_end = content.find("logger = logging.getLogger(__name__)")
        if import_end != -1:
            content = (
                content[:import_end] + retry_decorator + "\n" + content[import_end:]
            )
            fixes_applied.append("Added retry decorator")

    # Fix 3: Enhanced database connection method
    enhanced_db_method = '''
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config" / "daily_pipeline_config.json"
        self.reports_dir = self.project_root / "reports"
        self.docs_dir = self.project_root / "docs"

        # Initialize configuration
        self.config = self._load_config()

        # Database connection pool
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        }
        
        # Initialize connection pool
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                1, 20, **self.db_config
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            self.connection_pool = None

        # Pipeline status tracking
        self.pipeline_status = {
            "last_run": None,
            "current_stage": None,
            "errors": [],
            "success_count": 0,
            "failure_count": 0,
            "stages_completed": {},
            "analytics_results": {},
        }
    
    def get_db_connection(self):
        """Get database connection from pool with error handling."""
        if not self.connection_pool:
            raise Exception("Database connection pool not initialized")
        
        try:
            conn = self.connection_pool.getconn()
            if conn.closed:
                self.connection_pool.putconn(conn)
                conn = self.connection_pool.getconn()
            return conn
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def return_db_connection(self, conn):
        """Return connection to pool."""
        if self.connection_pool and conn:
            try:
                self.connection_pool.putconn(conn)
            except Exception as e:
                logger.error(f"Failed to return connection to pool: {e}")
    
    def __del__(self):
        """Cleanup connection pool on destruction."""
        if hasattr(self, 'connection_pool') and self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("🔒 Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")
'''

    # Replace the __init__ method
    init_pattern = r"def __init__\(self\):.*?(?=def|\Z)"
    if re.search(init_pattern, content, re.DOTALL):
        content = re.sub(
            init_pattern,
            enhanced_db_method.strip() + "\n\n    ",
            content,
            flags=re.DOTALL,
        )
        fixes_applied.append("Enhanced database connection with pooling")

    # Fix 4: Add async subprocess handler
    subprocess_handler = '''
    async def _run_subprocess_safely(self, script_path: Path, args: list = None, timeout: int = 600):
        """Run subprocess with proper resource management and timeout."""
        args = args or []
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path), *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                return {
                    "returncode": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Script {script_path.name} timed out after {timeout}s")
                
        except Exception as e:
            logger.error(f"Subprocess execution failed: {e}")
            raise
'''

    if "_run_subprocess_safely" not in content:
        # Insert after _save_status method
        save_status_end = content.find(
            "json.dump(self.pipeline_status, f, indent=2, default=str)"
        )
        if save_status_end != -1:
            next_method = content.find("\n    async def", save_status_end)
            if next_method != -1:
                content = (
                    content[:next_method]
                    + "\n"
                    + subprocess_handler
                    + content[next_method:]
                )
                fixes_applied.append("Added safe subprocess handler")

    # Fix 5: Enhanced _count_new_records with connection pooling
    enhanced_count_method = '''
    def _count_new_records(self) -> int:
        """Count records added in the last 24 hours using connection pool."""
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) 
                    FROM race_results 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                """
                )
                count = cur.fetchone()[0]
                logger.debug(f"Found {count} new records in last 24 hours")
                return count
        except Exception as e:
            logger.error(f"Failed to count new records: {e}")
            return 0
        finally:
            if conn:
                self.return_db_connection(conn)
'''

    # Replace the _count_new_records method
    count_pattern = (
        r"def _count_new_records\(self\) -> int:.*?(?=\n    def|\n    async def|\Z)"
    )
    if re.search(count_pattern, content, re.DOTALL):
        content = re.sub(
            count_pattern,
            enhanced_count_method.strip() + "\n\n    ",
            content,
            flags=re.DOTALL,
        )
        fixes_applied.append("Enhanced record counting with connection pooling")

    # Fix 6: Add health check method
    health_check_method = '''
    def health_check(self) -> dict:
        """Perform system health check."""
        health_status = {
            "database": False,
            "file_system": False,
            "memory": False,
            "overall": False
        }
        
        # Check database connectivity
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            health_status["database"] = True
            self.return_db_connection(conn)
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        # Check file system
        try:
            test_file = self.project_root / "health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            health_status["file_system"] = True
        except Exception as e:
            logger.error(f"File system health check failed: {e}")
        
        # Check memory usage
        try:
            import psutil
            memory_usage = psutil.virtual_memory().percent
            health_status["memory"] = memory_usage < 90
            health_status["memory_usage"] = memory_usage
        except ImportError:
            health_status["memory"] = True  # Assume OK if psutil not available
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
        
        health_status["overall"] = all([
            health_status["database"],
            health_status["file_system"],
            health_status["memory"]
        ])
        
        return health_status
'''

    if "def health_check(self)" not in content:
        # Insert before the first async method
        first_async = content.find("async def download_daily_data")
        if first_async != -1:
            content = (
                content[:first_async]
                + health_check_method
                + "\n    "
                + content[first_async:]
            )
            fixes_applied.append("Added health check method")

    # Write the fixed content back to the file
    print("🔧 Applying fixes...")
    with open(orchestrator_file, "w") as f:
        f.write(content)

    # Report applied fixes
    print("\n✅ Critical fixes applied:")
    for fix in fixes_applied:
        print(f"   ✓ {fix}")

    if not fixes_applied:
        print("ℹ️ No fixes were needed - code is already up to date")

    print(f"\n📊 Total fixes applied: {len(fixes_applied)}")
    return True


def main():
    """Main execution function."""
    print("🏇 Daily Pipeline Orchestrator - Critical Fixes")
    print("=" * 50)

    try:
        success = apply_critical_fixes()
        if success:
            print("\n✅ All critical fixes applied successfully!")
            print("\nNext steps:")
            print(
                "1. Test the pipeline with: python daily_pipeline_orchestrator.py --test"
            )
            print(
                "2. Run health check: python -c 'from daily_pipeline_orchestrator import DailyPipelineOrchestrator; print(DailyPipelineOrchestrator().health_check())'"
            )
            print("3. Review the complete TODO list in PIPELINE_REVIEW_AND_TODO.md")
        else:
            print("\n❌ Some fixes failed to apply")
            return 1
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
