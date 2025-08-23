#!/usr/bin/env python3
"""
🚀 Phase 2: Pipeline Reliability Integration
Integrate Pydantic configuration validation and enhanced error handling into the pipeline orchestrator

This script applies Phase 2 reliability improvements:
1. Replace basic dict config with Pydantic validation
2. Add circuit breakers to all external service calls
3. Implement enhanced retry mechanisms
4. Add comprehensive error logging and alerting
5. Create environment-specific configurations

Author: AI Assistant
Date: August 12, 2025
"""

import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path


def integrate_phase2_reliability():
    """Integrate Phase 2 reliability improvements into pipeline orchestrator."""

    orchestrator_file = Path("daily_pipeline_orchestrator.py")

    if not orchestrator_file.exists():
        print("❌ daily_pipeline_orchestrator.py not found!")
        return False

    print("🔧 Integrating Phase 2 Reliability Improvements...")
    with open(orchestrator_file, "r") as f:
        content = f.read()

    improvements_applied = []

    # 1. Add imports for new systems
    new_imports = """
# Phase 2: Enhanced reliability imports
from pipeline_config_validator import PipelineConfig, create_config_manager
from enhanced_error_handling import (
    CircuitBreaker, EnhancedRetry, ErrorContextLogger, AlertManager,
    CircuitBreakerError, RetryExhaustedException
)
"""

    if "from pipeline_config_validator import" not in content:
        # Insert after existing imports
        import_end = content.find("logger = logging.getLogger(__name__)")
        if import_end != -1:
            content = content[:import_end] + new_imports + "\n" + content[import_end:]
            improvements_applied.append("Added Phase 2 reliability imports")

    # 2. Enhanced __init__ method with Pydantic config
    enhanced_init = """
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config" / "daily_pipeline_config.json"
        self.reports_dir = self.project_root / "reports"
        self.docs_dir = self.project_root / "docs"

        # Phase 2: Initialize Pydantic configuration manager
        ConfigManagerClass = create_config_manager()
        self.config_manager = ConfigManagerClass(self.config_file)
        self.config = self.config_manager.get_config()
        
        # Validate configuration on startup
        issues = self.config_manager.validate_current_config()
        if issues:
            logger.warning(f"Configuration issues found: {issues}")
        else:
            logger.info("✅ Configuration validation passed")

        # Database connection pool with config validation
        self.db_config = {
            "host": self.config.database.host,
            "port": self.config.database.port,
            "database": self.config.database.database,
            "user": self.config.database.user,
            "password": self.config.database.password,
        }
        
        # Initialize connection pool with validated config
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.config.database.pool_min_connections,
                self.config.database.pool_max_connections,
                **self.db_config
            )
            logger.info("✅ Database connection pool initialized with validated config")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            self.connection_pool = None

        # Phase 2: Initialize error handling components
        self.error_logger = ErrorContextLogger("pipeline_errors")
        self.alert_manager = AlertManager()
        
        # Circuit breakers for external services
        self.circuit_breakers = {
            "database": CircuitBreaker(
                failure_threshold=self.config.data_sources.circuit_breaker_threshold,
                timeout=self.config.data_sources.circuit_breaker_timeout,
                name="database"
            ),
            "manual_data_loading": CircuitBreaker(
                failure_threshold=5,
                timeout=300,
                name="manual_data_loading"
            ),
            "relationships_pipeline": CircuitBreaker(
                failure_threshold=3,
                timeout=180,
                name="relationships_pipeline"
            ),
            "analytics_scripts": CircuitBreaker(
                failure_threshold=4,
                timeout=240,
                name="analytics_scripts"
            )
        }
        
        # Enhanced retry handlers
        self.retry_handlers = {
            "database_operations": EnhancedRetry(
                max_attempts=self.config.data_sources.retry_attempts,
                base_delay=1.0,
                circuit_breaker=self.circuit_breakers["database"],
                name="database_operations"
            ),
            "external_scripts": EnhancedRetry(
                max_attempts=3,
                base_delay=2.0,
                max_delay=60.0,
                name="external_scripts"
            ),
            "file_operations": EnhancedRetry(
                max_attempts=2,
                base_delay=0.5,
                name="file_operations"
            )
        }

        # Pipeline status tracking with enhanced metrics
        self.pipeline_status = {
            "last_run": None,
            "current_stage": None,
            "errors": [],
            "success_count": 0,
            "failure_count": 0,
            "stages_completed": {},
            "analytics_results": {},
            "circuit_breaker_metrics": {},
            "retry_metrics": {},
            "error_summary": {}
        }
"""

    # Replace the existing __init__ method
    init_pattern = r"def __init__\(self\):.*?(?=\n    def|\n    async def|\Z)"
    if re.search(init_pattern, content, re.DOTALL):
        content = re.sub(
            init_pattern, enhanced_init.strip() + "\n\n    ", content, flags=re.DOTALL
        )
        improvements_applied.append(
            "Enhanced __init__ with Pydantic config and error handling"
        )

    # 3. Enhanced database connection with circuit breaker
    enhanced_db_connection = '''
    @retry_on_failure(max_retries=3, delay=1, backoff=2)
    def get_db_connection(self):
        """Get database connection from pool with circuit breaker protection."""
        if not self.connection_pool:
            raise Exception("Database connection pool not initialized")
        
        # Check circuit breaker
        if not self.circuit_breakers["database"]._can_attempt():
            raise CircuitBreakerError("Database circuit breaker is open")
        
        try:
            conn = self.connection_pool.getconn()
            if conn.closed:
                self.connection_pool.putconn(conn)
                conn = self.connection_pool.getconn()
            
            # Circuit breaker success
            self.circuit_breakers["database"]._on_success()
            return conn
            
        except Exception as e:
            # Circuit breaker failure
            self.circuit_breakers["database"]._on_failure(e)
            
            self.error_logger.log_error(
                e,
                context={"operation": "get_db_connection", "pool_status": "active"},
                stage="database_connection",
                severity="error"
            )
            raise
'''

    # Replace the get_db_connection method
    db_conn_pattern = (
        r"def get_db_connection\(self\):.*?(?=\n    def|\n    async def|\Z)"
    )
    if re.search(db_conn_pattern, content, re.DOTALL):
        content = re.sub(
            db_conn_pattern,
            enhanced_db_connection.strip() + "\n\n    ",
            content,
            flags=re.DOTALL,
        )
        improvements_applied.append("Enhanced database connection with circuit breaker")

    # 4. Enhanced async subprocess with circuit breaker and retry
    enhanced_subprocess = '''
    async def _run_subprocess_safely(self, script_path: Path, args: list = None, timeout: int = None):
        """Run subprocess with circuit breaker, retry, and comprehensive error handling."""
        args = args or []
        timeout = timeout or self.config.processing.max_processing_time_minutes * 60
        
        # Determine which circuit breaker to use
        script_name = script_path.name.lower()
        if "downloader" in script_name:
            circuit_breaker = self.circuit_breakers["manual_data_loading"]
            retry_handler = self.retry_handlers["external_scripts"]
        elif "relationship" in script_name:
            circuit_breaker = self.circuit_breakers["relationships_pipeline"] 
            retry_handler = self.retry_handlers["external_scripts"]
        else:
            circuit_breaker = self.circuit_breakers["analytics_scripts"]
            retry_handler = self.retry_handlers["external_scripts"]
        
        # Check circuit breaker before attempting
        if not circuit_breaker._can_attempt():
            error_msg = f"Circuit breaker for {script_path.name} is open"
            await self.alert_manager.send_alert(
                "circuit_breaker_open",
                error_msg,
                severity="warning",
                context={"script": str(script_path)}
            )
            raise CircuitBreakerError(error_msg)
        
        async def subprocess_operation():
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
                    
                    result = {
                        "returncode": process.returncode,
                        "stdout": stdout.decode(),
                        "stderr": stderr.decode()
                    }
                    
                    if process.returncode == 0:
                        circuit_breaker._on_success()
                    else:
                        raise subprocess.CalledProcessError(
                            process.returncode, str(script_path), stderr.decode()
                        )
                    
                    return result
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    timeout_error = TimeoutError(f"Script {script_path.name} timed out after {timeout}s")
                    circuit_breaker._on_failure(timeout_error)
                    raise timeout_error
                    
            except Exception as e:
                circuit_breaker._on_failure(e)
                
                self.error_logger.log_error(
                    e,
                    context={
                        "script": str(script_path),
                        "args": args,
                        "timeout": timeout,
                        "circuit_breaker_state": circuit_breaker.state.value
                    },
                    stage="subprocess_execution",
                    severity="error"
                )
                raise
        
        # Apply retry mechanism
        try:
            retryable_operation = await retry_handler(subprocess_operation)
            return await retryable_operation()
        except RetryExhaustedException as e:
            await self.alert_manager.send_alert(
                "subprocess_retry_exhausted",
                f"Script {script_path.name} failed after all retry attempts",
                severity="critical",
                context={"script": str(script_path), "error": str(e)}
            )
            raise
'''

    # Replace the _run_subprocess_safely method
    subprocess_pattern = r"async def _run_subprocess_safely\(self, script_path: Path, args: list = None, timeout: int = 600\):.*?(?=\n    async def|\n    def|\Z)"
    if re.search(subprocess_pattern, content, re.DOTALL):
        content = re.sub(
            subprocess_pattern,
            enhanced_subprocess.strip() + "\n\n    ",
            content,
            flags=re.DOTALL,
        )
        improvements_applied.append(
            "Enhanced subprocess handling with circuit breaker and retry"
        )

    # 5. Enhanced status management with metrics
    enhanced_status_management = '''
    def _save_status(self):
        """Save current pipeline status with enhanced metrics."""
        status_file = self.project_root / "logs" / "pipeline_status.json"
        status_file.parent.mkdir(exist_ok=True)

        # Collect circuit breaker metrics
        self.pipeline_status["circuit_breaker_metrics"] = {
            name: cb.get_metrics() for name, cb in self.circuit_breakers.items()
        }
        
        # Collect retry metrics
        self.pipeline_status["retry_metrics"] = {
            name: handler.get_metrics() for name, handler in self.retry_handlers.items()
        }
        
        # Get error summary
        self.pipeline_status["error_summary"] = self.error_logger.get_error_summary(hours=24)
        
        # Add configuration validation status
        config_issues = self.config_manager.validate_current_config()
        self.pipeline_status["config_validation"] = {
            "valid": len(config_issues) == 0,
            "issues": config_issues,
            "last_validated": datetime.now().isoformat()
        }

        with open(status_file, "w") as f:
            json.dump(self.pipeline_status, f, indent=2, default=str)
    
    def get_enhanced_health_check(self) -> dict:
        """Enhanced health check with circuit breaker and configuration status."""
        health_status = self.health_check()  # Get basic health check
        
        # Add circuit breaker status
        circuit_breaker_health = {}
        for name, cb in self.circuit_breakers.items():
            circuit_breaker_health[name] = {
                "state": cb.state.value,
                "failure_count": cb.failure_count,
                "healthy": cb.state.value != "open"
            }
        
        health_status["circuit_breakers"] = circuit_breaker_health
        health_status["circuit_breakers_healthy"] = all(
            cb["healthy"] for cb in circuit_breaker_health.values()
        )
        
        # Add configuration validation status
        config_issues = self.config_manager.validate_current_config()
        health_status["configuration"] = {
            "valid": len(config_issues) == 0,
            "issues": config_issues
        }
        
        # Update overall health status
        health_status["overall"] = (
            health_status["overall"] and 
            health_status["circuit_breakers_healthy"] and
            health_status["configuration"]["valid"]
        )
        
        return health_status
    
    def reload_configuration(self) -> bool:
        """Reload configuration and update components."""
        try:
            old_config = self.config
            success = self.config_manager.reload_config()
            
            if success:
                self.config = self.config_manager.get_config()
                
                # Update circuit breaker thresholds if changed
                if hasattr(old_config, 'data_sources'):
                    if (old_config.data_sources.circuit_breaker_threshold != 
                        self.config.data_sources.circuit_breaker_threshold):
                        
                        for cb in self.circuit_breakers.values():
                            cb.failure_threshold = self.config.data_sources.circuit_breaker_threshold
                
                logger.info("✅ Configuration reloaded and applied")
                return True
            else:
                logger.error("❌ Configuration reload failed")
                return False
                
        except Exception as e:
            self.error_logger.log_error(
                e,
                context={"operation": "reload_configuration"},
                stage="configuration_management",
                severity="error"
            )
            return False
'''

    # Insert enhanced status management after _save_status
    save_status_end = content.find(
        "json.dump(self.pipeline_status, f, indent=2, default=str)"
    )
    if save_status_end != -1:
        next_method = content.find("\n    async def", save_status_end)
        if next_method == -1:
            next_method = content.find("\n    def", save_status_end)
        if next_method != -1:
            content = (
                content[:next_method]
                + "\n"
                + enhanced_status_management
                + content[next_method:]
            )
            improvements_applied.append("Enhanced status management with metrics")

    # Write the enhanced content back to the file
    print("🔧 Applying Phase 2 improvements...")
    with open(orchestrator_file, "w") as f:
        f.write(content)

    # Report applied improvements
    print("\n✅ Phase 2 reliability improvements applied:")
    for improvement in improvements_applied:
        print(f"   ✓ {improvement}")

    if not improvements_applied:
        print("ℹ️ No improvements were needed - code is already up to date")

    print(f"\n📊 Total improvements applied: {len(improvements_applied)}")
    return True


def create_environment_configs():
    """Create environment-specific configuration files."""
    print("\n🔧 Creating environment-specific configurations...")

    try:
        from pipeline_config_validator import PipelineConfig

        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        environments = {
            "development": {
                "debug_mode": True,
                "log_level": "DEBUG",
                "database": {"pool_max_connections": 10},
                "processing": {"parallel_workers": 2},
            },
            "staging": {
                "debug_mode": False,
                "log_level": "INFO",
                "database": {"pool_max_connections": 20},
                "processing": {"parallel_workers": 4},
            },
            "production": {
                "debug_mode": False,
                "log_level": "WARNING",
                "database": {"pool_max_connections": 50},
                "processing": {"parallel_workers": 8, "memory_limit_mb": 8192},
                "notifications": {
                    "email_enabled": True,
                    "notification_level": "warning",
                },
            },
        }

        for env_name, env_settings in environments.items():
            try:
                config = PipelineConfig.create_environment_config(env_name)
                config_file = config_dir / f"pipeline_config_{env_name}.json"
                config.save_to_file(config_file)
                print(f"   ✅ Created {env_name} config: {config_file}")
            except Exception as e:
                print(f"   ❌ Failed to create {env_name} config: {e}")

        return True

    except ImportError:
        print("   ❌ pipeline_config_validator module not available")
        return False


def main():
    """Main execution function."""
    print("🚀 Phase 2: Pipeline Reliability Integration")
    print("=" * 50)

    try:
        # Apply reliability improvements
        success = integrate_phase2_reliability()

        if success:
            print("\n✅ Phase 2 reliability improvements applied successfully!")

            # Create environment configs
            create_environment_configs()

            print("\nNext steps:")
            print(
                "1. Test enhanced pipeline: python daily_pipeline_orchestrator.py --test"
            )
            print(
                "2. Check enhanced health: python -c 'from daily_pipeline_orchestrator import DailyPipelineOrchestrator; print(DailyPipelineOrchestrator().get_enhanced_health_check())'"
            )
            print("3. Review configuration: project_root / 'config' / pipeline_config_*.json")
            print("4. Monitor circuit breaker metrics in pipeline status")

        else:
            print("\n❌ Some improvements failed to apply")
            return 1

    except Exception as e:
        print(f"\n❌ Error applying Phase 2 improvements: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
