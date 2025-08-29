#!/usr/bin/env python3
"""
Stage 11 Integration and Automation Pipeline for Horse Racing AI V2.03
Orchestrates external data integration, automated retraining, deployment,
monitoring, and testing automation
"""

import os
import sys
import json
import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import sqlite3
import threading

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our integration components
from tools.integration.external_data_integrator import ExternalDataIntegrator
from tools.integration.automated_model_retrainer import AutomatedModelRetrainer
from tools.integration.automated_deployment_pipeline import AutomatedDeploymentPipeline
from tools.integration.system_health_monitor import SystemHealthMonitor
from tools.integration.automated_testing_framework import AutomatedTestingFramework

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationTask:
    """Integration automation task configuration"""

    task_id: str
    name: str
    component: str
    schedule_pattern: str  # cron-like pattern
    enabled: bool
    dependencies: List[str]
    timeout_minutes: int
    retry_count: int
    last_execution: Optional[datetime]
    next_execution: Optional[datetime]
    success_count: int
    failure_count: int


class Stage11IntegrationPipeline:
    """
    Stage 11 Integration and Automation Pipeline
    Orchestrates all integration and automation components
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Stage 11 Integration Pipeline"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")

        # Initialize components
        self.external_data_integrator = None
        self.model_retrainer = None
        self.deployment_pipeline = None
        self.health_monitor = None
        self.testing_framework = None

        # Task management
        self.integration_tasks = self._initialize_integration_tasks()
        self.scheduler_running = False
        self.scheduler_thread = None

        # Pipeline state
        self.pipeline_status = "stopped"
        self.last_cycle_start = None
        self.last_cycle_end = None

        # Statistics
        self.stats = {
            "total_cycles_completed": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "tasks_executed": 0,
            "pipeline_uptime_start": datetime.now(),
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "pipeline_interval_minutes": 60,  # 1 hour
            "max_concurrent_tasks": 3,
            "task_timeout_minutes": 30,
            "health_check_interval_minutes": 5,
            "auto_recovery_enabled": True,
            "notification": {"email_alerts": False, "webhook_url": None},
            "schedules": {
                "external_data_update": "*/30 * * * *",  # Every 30 minutes
                "model_performance_check": "0 */4 * * *",  # Every 4 hours
                "health_monitoring": "*/5 * * * *",  # Every 5 minutes
                "daily_testing": "0 2 * * *",  # Daily at 2 AM
                "weekly_full_test": "0 3 * * 0",  # Weekly on Sunday at 3 AM
            },
        }

    def _initialize_integration_tasks(self) -> List[IntegrationTask]:
        """Initialize integration task configurations"""
        tasks = []
        schedules = self.config.get("schedules", {})

        # External Data Integration Task
        tasks.append(
            IntegrationTask(
                task_id="external_data_update",
                name="External Data Update",
                component="external_data_integrator",
                schedule_pattern=schedules.get("external_data_update", "*/30 * * * *"),
                enabled=True,
                dependencies=[],
                timeout_minutes=15,
                retry_count=2,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # Model Performance Monitoring Task
        tasks.append(
            IntegrationTask(
                task_id="model_performance_check",
                name="Model Performance Check",
                component="model_retrainer",
                schedule_pattern=schedules.get(
                    "model_performance_check", "0 */4 * * *"
                ),
                enabled=True,
                dependencies=["external_data_update"],
                timeout_minutes=30,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # System Health Monitoring Task
        tasks.append(
            IntegrationTask(
                task_id="health_monitoring",
                name="System Health Monitoring",
                component="health_monitor",
                schedule_pattern=schedules.get("health_monitoring", "*/5 * * * *"),
                enabled=True,
                dependencies=[],
                timeout_minutes=5,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # Daily Testing Task
        tasks.append(
            IntegrationTask(
                task_id="daily_testing",
                name="Daily Automated Testing",
                component="testing_framework",
                schedule_pattern=schedules.get("daily_testing", "0 2 * * *"),
                enabled=True,
                dependencies=[],
                timeout_minutes=60,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # Weekly Full Test Suite
        tasks.append(
            IntegrationTask(
                task_id="weekly_full_test",
                name="Weekly Full Test Suite",
                component="testing_framework",
                schedule_pattern=schedules.get("weekly_full_test", "0 3 * * 0"),
                enabled=True,
                dependencies=[],
                timeout_minutes=120,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # Model Retraining Processing
        tasks.append(
            IntegrationTask(
                task_id="model_retraining_process",
                name="Process Model Retraining Queue",
                component="model_retrainer",
                schedule_pattern="*/15 * * * *",  # Every 15 minutes
                enabled=True,
                dependencies=[],
                timeout_minutes=45,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        # Deployment Pipeline Processing
        tasks.append(
            IntegrationTask(
                task_id="deployment_processing",
                name="Process Deployment Queue",
                component="deployment_pipeline",
                schedule_pattern="*/10 * * * *",  # Every 10 minutes
                enabled=True,
                dependencies=[],
                timeout_minutes=30,
                retry_count=1,
                last_execution=None,
                next_execution=None,
                success_count=0,
                failure_count=0,
            )
        )

        return tasks

    async def initialize_database(self):
        """Initialize database tables for pipeline tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Integration pipeline execution table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS integration_pipeline_executions (
                    execution_id TEXT PRIMARY KEY,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL,
                    tasks_executed INTEGER DEFAULT 0,
                    tasks_successful INTEGER DEFAULT 0,
                    tasks_failed INTEGER DEFAULT 0,
                    error_message TEXT,
                    cycle_duration REAL
                )
            """
            )

            # Integration task executions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS integration_task_executions (
                    task_execution_id TEXT PRIMARY KEY,
                    pipeline_execution_id TEXT,
                    task_id TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    component TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL,
                    execution_duration REAL,
                    retry_attempt INTEGER DEFAULT 0,
                    error_message TEXT,
                    result_summary_json TEXT,
                    FOREIGN KEY (pipeline_execution_id) REFERENCES integration_pipeline_executions(execution_id)
                )
            """
            )

            # Integration task schedules table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS integration_task_schedules (
                    task_id TEXT PRIMARY KEY,
                    task_name TEXT NOT NULL,
                    component TEXT NOT NULL,
                    schedule_pattern TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    last_execution TIMESTAMP,
                    next_execution TIMESTAMP,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Pipeline health metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_health_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    pipeline_status TEXT NOT NULL,
                    active_tasks INTEGER NOT NULL,
                    pending_tasks INTEGER NOT NULL,
                    failed_tasks INTEGER NOT NULL,
                    component_status_json TEXT,
                    resource_usage_json TEXT
                )
            """
            )

            # Indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_pipeline_exec_start ON integration_pipeline_executions(start_time)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_task_exec_start ON integration_task_executions(start_time)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_task_exec_component ON integration_task_executions(component)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_pipeline_health_timestamp ON pipeline_health_metrics(timestamp)"
            )

            conn.commit()
            conn.close()

            logger.info("Stage 11 integration pipeline database tables initialized")

        except Exception as e:
            logger.error(f"Error initializing pipeline database: {e}")
            raise

    async def initialize_components(self):
        """Initialize all integration components"""
        try:
            logger.info("Initializing integration components...")

            # Initialize External Data Integrator
            self.external_data_integrator = ExternalDataIntegrator()
            await self.external_data_integrator.initialize_database()

            # Initialize Model Retrainer
            self.model_retrainer = AutomatedModelRetrainer()
            await self.model_retrainer.initialize_database()

            # Initialize Deployment Pipeline
            self.deployment_pipeline = AutomatedDeploymentPipeline()
            await self.deployment_pipeline.initialize_database()
            await self.deployment_pipeline.initialize_docker_client()

            # Initialize Health Monitor
            self.health_monitor = SystemHealthMonitor()
            await self.health_monitor.initialize_database()
            await self.health_monitor.initialize_docker_client()

            # Initialize Testing Framework
            self.testing_framework = AutomatedTestingFramework()
            await self.testing_framework.initialize_database()

            logger.info("All integration components initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise

    async def execute_task(
        self, task: IntegrationTask, pipeline_execution_id: str
    ) -> Dict[str, Any]:
        """Execute a specific integration task"""
        task_execution_id = f"{task.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Executing task: {task.name}")

            start_time = datetime.now()

            # Save task execution start
            await self._save_task_execution_start(
                task_execution_id, pipeline_execution_id, task, start_time
            )

            # Execute based on component
            if task.component == "external_data_integrator":
                result = await self._execute_external_data_task(task)
            elif task.component == "model_retrainer":
                result = await self._execute_model_retrainer_task(task)
            elif task.component == "deployment_pipeline":
                result = await self._execute_deployment_task(task)
            elif task.component == "health_monitor":
                result = await self._execute_health_monitor_task(task)
            elif task.component == "testing_framework":
                result = await self._execute_testing_task(task)
            else:
                raise ValueError(f"Unknown component: {task.component}")

            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()

            # Update task tracking
            task.last_execution = start_time
            task.success_count += 1

            # Save task execution completion
            await self._save_task_execution_completion(
                task_execution_id, "completed", execution_duration, None, result
            )

            logger.info(
                f"Task {task.name} completed successfully in {execution_duration:.2f}s"
            )

            return {
                "status": "completed",
                "execution_duration": execution_duration,
                "result": result,
            }

        except Exception as e:
            end_time = datetime.now()
            execution_duration = (
                (end_time - start_time).total_seconds()
                if "start_time" in locals()
                else 0
            )

            # Update task tracking
            task.failure_count += 1

            # Save task execution failure
            await self._save_task_execution_completion(
                task_execution_id, "failed", execution_duration, str(e), None
            )

            logger.error(f"Task {task.name} failed: {e}")

            return {
                "status": "failed",
                "execution_duration": execution_duration,
                "error": str(e),
            }

    async def _execute_external_data_task(
        self, task: IntegrationTask
    ) -> Dict[str, Any]:
        """Execute external data integration task"""
        if task.task_id == "external_data_update":
            return await self.external_data_integrator.update_all_sources()
        else:
            raise ValueError(f"Unknown external data task: {task.task_id}")

    async def _execute_model_retrainer_task(
        self, task: IntegrationTask
    ) -> Dict[str, Any]:
        """Execute model retrainer task"""
        if task.task_id == "model_performance_check":
            return await self.model_retrainer.monitor_all_models()
        elif task.task_id == "model_retraining_process":
            return await self.model_retrainer.process_retraining_queue()
        else:
            raise ValueError(f"Unknown model retrainer task: {task.task_id}")

    async def _execute_deployment_task(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute deployment pipeline task"""
        if task.task_id == "deployment_processing":
            return await self.deployment_pipeline.process_deployment_queue()
        else:
            raise ValueError(f"Unknown deployment task: {task.task_id}")

    async def _execute_health_monitor_task(
        self, task: IntegrationTask
    ) -> Dict[str, Any]:
        """Execute health monitoring task"""
        if task.task_id == "health_monitoring":
            return await self.health_monitor.perform_monitoring_cycle()
        else:
            raise ValueError(f"Unknown health monitor task: {task.task_id}")

    async def _execute_testing_task(self, task: IntegrationTask) -> Dict[str, Any]:
        """Execute testing framework task"""
        if task.task_id == "daily_testing":
            # Run validation rules only for daily testing
            execution_id = await self.testing_framework.run_validation_rules(
                "daily_automated"
            )
            return {"execution_id": execution_id, "type": "validation_only"}
        elif task.task_id == "weekly_full_test":
            # Run full test suite for weekly testing
            execution_id = await self.testing_framework.run_full_test_execution(
                "weekly_automated"
            )
            return {"execution_id": execution_id, "type": "full_test_suite"}
        else:
            raise ValueError(f"Unknown testing task: {task.task_id}")

    async def _save_task_execution_start(
        self,
        task_execution_id: str,
        pipeline_execution_id: str,
        task: IntegrationTask,
        start_time: datetime,
    ):
        """Save task execution start to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO integration_task_executions 
                (task_execution_id, pipeline_execution_id, task_id, task_name, 
                 component, start_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_execution_id,
                    pipeline_execution_id,
                    task.task_id,
                    task.name,
                    task.component,
                    start_time,
                    "running",
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving task execution start: {e}")

    async def _save_task_execution_completion(
        self,
        task_execution_id: str,
        status: str,
        execution_duration: float,
        error_message: Optional[str],
        result_summary: Optional[Dict[str, Any]],
    ):
        """Save task execution completion to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE integration_task_executions 
                SET end_time = ?, status = ?, execution_duration = ?, 
                    error_message = ?, result_summary_json = ?
                WHERE task_execution_id = ?
            """,
                (
                    datetime.now(),
                    status,
                    execution_duration,
                    error_message,
                    json.dumps(result_summary, default=str) if result_summary else None,
                    task_execution_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving task execution completion: {e}")

    async def run_pipeline_cycle(self) -> Dict[str, Any]:
        """Run one complete pipeline cycle"""
        execution_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            self.last_cycle_start = datetime.now()
            logger.info(f"Starting pipeline cycle: {execution_id}")

            # Create pipeline execution record
            await self._create_pipeline_execution_record(execution_id)

            # Get enabled tasks
            enabled_tasks = [task for task in self.integration_tasks if task.enabled]

            # Execute tasks
            tasks_executed = 0
            tasks_successful = 0
            tasks_failed = 0

            for task in enabled_tasks:
                try:
                    # Check dependencies
                    if not await self._check_task_dependencies(task):
                        logger.warning(
                            f"Skipping task {task.name} due to unmet dependencies"
                        )
                        continue

                    # Execute task
                    task_result = await self.execute_task(task, execution_id)
                    tasks_executed += 1

                    if task_result["status"] == "completed":
                        tasks_successful += 1
                    else:
                        tasks_failed += 1

                    self.stats["tasks_executed"] += 1

                except Exception as e:
                    logger.error(f"Error executing task {task.name}: {e}")
                    tasks_failed += 1

            self.last_cycle_end = datetime.now()
            cycle_duration = (
                self.last_cycle_end - self.last_cycle_start
            ).total_seconds()

            # Update pipeline execution record
            status = "completed" if tasks_failed == 0 else "partial_failure"
            await self._update_pipeline_execution_record(
                execution_id,
                status,
                tasks_executed,
                tasks_successful,
                tasks_failed,
                cycle_duration,
            )

            # Update statistics
            self.stats["total_cycles_completed"] += 1
            if tasks_failed == 0:
                self.stats["successful_cycles"] += 1
            else:
                self.stats["failed_cycles"] += 1

            logger.info(
                f"Pipeline cycle completed: {tasks_successful}/{tasks_executed} tasks successful"
            )

            return {
                "execution_id": execution_id,
                "status": status,
                "tasks_executed": tasks_executed,
                "tasks_successful": tasks_successful,
                "tasks_failed": tasks_failed,
                "cycle_duration": cycle_duration,
            }

        except Exception as e:
            logger.error(f"Error in pipeline cycle {execution_id}: {e}")

            if "self.last_cycle_start" in locals():
                cycle_duration = (
                    datetime.now() - self.last_cycle_start
                ).total_seconds()
            else:
                cycle_duration = 0

            await self._update_pipeline_execution_record(
                execution_id, "failed", 0, 0, 0, cycle_duration, str(e)
            )

            self.stats["failed_cycles"] += 1

            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "cycle_duration": cycle_duration,
            }

    async def _check_task_dependencies(self, task: IntegrationTask) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for dependency_task_id in task.dependencies:
                # Check if dependency task has run successfully recently
                cursor.execute(
                    """
                    SELECT status, start_time
                    FROM integration_task_executions
                    WHERE task_id = ? AND status = 'completed'
                    ORDER BY start_time DESC
                    LIMIT 1
                """,
                    (dependency_task_id,),
                )

                result = cursor.fetchone()

                if not result:
                    logger.warning(
                        f"Dependency {dependency_task_id} has no successful executions"
                    )
                    conn.close()
                    return False

                # Check if execution is recent enough (within last 24 hours)
                last_success = datetime.fromisoformat(result[1])
                if (datetime.now() - last_success).total_seconds() > 24 * 3600:
                    logger.warning(
                        f"Dependency {dependency_task_id} last success is too old"
                    )
                    conn.close()
                    return False

            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error checking task dependencies: {e}")
            return False

    async def _create_pipeline_execution_record(self, execution_id: str):
        """Create pipeline execution record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO integration_pipeline_executions 
                (execution_id, start_time, status)
                VALUES (?, ?, ?)
            """,
                (execution_id, self.last_cycle_start, "running"),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error creating pipeline execution record: {e}")

    async def _update_pipeline_execution_record(
        self,
        execution_id: str,
        status: str,
        tasks_executed: int,
        tasks_successful: int,
        tasks_failed: int,
        cycle_duration: float,
        error_message: Optional[str] = None,
    ):
        """Update pipeline execution record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE integration_pipeline_executions 
                SET end_time = ?, status = ?, tasks_executed = ?, 
                    tasks_successful = ?, tasks_failed = ?, 
                    cycle_duration = ?, error_message = ?
                WHERE execution_id = ?
            """,
                (
                    datetime.now(),
                    status,
                    tasks_executed,
                    tasks_successful,
                    tasks_failed,
                    cycle_duration,
                    error_message,
                    execution_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating pipeline execution record: {e}")

    def start_scheduler(self):
        """Start the task scheduler"""
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return

        self.scheduler_running = True
        self.pipeline_status = "running"

        # Schedule pipeline cycles
        schedule.every(self.config.get("pipeline_interval_minutes", 60)).minutes.do(
            self._schedule_pipeline_cycle
        )

        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=True
        )
        self.scheduler_thread.start()

        logger.info("Integration pipeline scheduler started")

    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.scheduler_running = False
        self.pipeline_status = "stopped"

        schedule.clear()

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)

        logger.info("Integration pipeline scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(60)

    def _schedule_pipeline_cycle(self):
        """Schedule a pipeline cycle (called by scheduler)"""
        try:
            # Run pipeline cycle in a new event loop (since we're in a thread)
            import asyncio

            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Run the pipeline cycle
                result = loop.run_until_complete(self.run_pipeline_cycle())
                logger.info(f"Scheduled pipeline cycle completed: {result['status']}")
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Error in scheduled pipeline cycle: {e}")

    async def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Pipeline execution summary
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_executions,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_executions,
                    AVG(cycle_duration) as avg_cycle_duration,
                    AVG(tasks_executed) as avg_tasks_per_cycle
                FROM integration_pipeline_executions 
                WHERE start_time >= datetime('now', '-30 days')
            """
            )
            pipeline_summary = cursor.fetchone()

            # Task execution summary
            cursor.execute(
                """
                SELECT 
                    task_id, task_name, component,
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_executions,
                    AVG(execution_duration) as avg_duration
                FROM integration_task_executions 
                WHERE start_time >= datetime('now', '-30 days')
                GROUP BY task_id, task_name, component
            """
            )
            task_summaries = [
                {
                    "task_id": row[0],
                    "task_name": row[1],
                    "component": row[2],
                    "total_executions": row[3],
                    "successful_executions": row[4],
                    "success_rate": (row[4] / row[3] * 100) if row[3] > 0 else 0,
                    "avg_duration": round(row[5] or 0, 2),
                }
                for row in cursor.fetchall()
            ]

            # Recent pipeline executions
            cursor.execute(
                """
                SELECT execution_id, start_time, status, tasks_executed, 
                       tasks_successful, cycle_duration
                FROM integration_pipeline_executions
                ORDER BY start_time DESC
                LIMIT 10
            """
            )
            recent_executions = [
                {
                    "execution_id": row[0],
                    "start_time": row[1],
                    "status": row[2],
                    "tasks_executed": row[3],
                    "tasks_successful": row[4],
                    "cycle_duration": round(row[5] or 0, 2),
                }
                for row in cursor.fetchall()
            ]

            conn.close()

            # Calculate uptime
            uptime_hours = (
                datetime.now() - self.stats["pipeline_uptime_start"]
            ).total_seconds() / 3600

            # Component status
            component_status = {}
            try:
                if self.external_data_integrator:
                    component_status["external_data"] = (
                        await self.external_data_integrator.get_integration_statistics()
                    )
                if self.model_retrainer:
                    component_status["model_retrainer"] = (
                        await self.model_retrainer.get_retraining_statistics()
                    )
                if self.deployment_pipeline:
                    component_status["deployment"] = (
                        await self.deployment_pipeline.get_deployment_statistics()
                    )
                if self.health_monitor:
                    component_status["health_monitor"] = (
                        await self.health_monitor.get_monitoring_statistics()
                    )
                if self.testing_framework:
                    component_status["testing"] = (
                        await self.testing_framework.get_testing_statistics()
                    )
            except Exception as e:
                logger.warning(f"Error getting component status: {e}")

            return {
                "pipeline_stats": {
                    **self.stats,
                    "uptime_hours": round(uptime_hours, 2),
                    "pipeline_status": self.pipeline_status,
                    "scheduler_running": self.scheduler_running,
                },
                "execution_summary": {
                    "total_executions": pipeline_summary[0] or 0,
                    "successful_executions": pipeline_summary[1] or 0,
                    "failed_executions": pipeline_summary[2] or 0,
                    "avg_cycle_duration": round(pipeline_summary[3] or 0, 2),
                    "avg_tasks_per_cycle": round(pipeline_summary[4] or 0, 1),
                    "success_rate": (
                        (pipeline_summary[1] or 0)
                        / max(pipeline_summary[0] or 1, 1)
                        * 100
                    ),
                },
                "task_summaries": task_summaries,
                "recent_executions": recent_executions,
                "component_status": component_status,
                "configured_tasks": len(self.integration_tasks),
                "enabled_tasks": len([t for t in self.integration_tasks if t.enabled]),
            }

        except Exception as e:
            logger.error(f"Error getting pipeline statistics: {e}")
            return {"error": str(e)}


async def main():
    """Main function for testing the Stage 11 Integration Pipeline"""

    print("🚀 Stage 11 Integration and Automation Pipeline V2.03")
    print("=" * 60)

    try:
        # Initialize pipeline
        pipeline = Stage11IntegrationPipeline()

        # Initialize database
        print("📊 Initializing pipeline database...")
        await pipeline.initialize_database()

        # Initialize components
        print("🔧 Initializing integration components...")
        await pipeline.initialize_components()

        # Run a single pipeline cycle
        print("🔄 Running pipeline cycle...")
        cycle_result = await pipeline.run_pipeline_cycle()

        print(f"✅ Pipeline cycle completed:")
        print(f"   - Status: {cycle_result['status']}")
        print(f"   - Tasks executed: {cycle_result['tasks_executed']}")
        print(f"   - Tasks successful: {cycle_result['tasks_successful']}")
        print(f"   - Tasks failed: {cycle_result['tasks_failed']}")
        print(f"   - Cycle duration: {cycle_result['cycle_duration']:.2f}s")

        # Get comprehensive statistics
        print("\n📈 Pipeline Statistics:")
        stats = await pipeline.get_pipeline_statistics()

        pipeline_stats = stats["pipeline_stats"]
        print(f"   - Pipeline status: {pipeline_stats['pipeline_status']}")
        print(
            f"   - Total cycles completed: {pipeline_stats['total_cycles_completed']}"
        )
        print(f"   - Successful cycles: {pipeline_stats['successful_cycles']}")
        print(f"   - Failed cycles: {pipeline_stats['failed_cycles']}")
        print(f"   - Tasks executed: {pipeline_stats['tasks_executed']}")
        print(f"   - Pipeline uptime: {pipeline_stats['uptime_hours']:.2f} hours")

        execution_summary = stats["execution_summary"]
        print(f"   - Success rate: {execution_summary['success_rate']:.1f}%")
        print(
            f"   - Average cycle duration: {execution_summary['avg_cycle_duration']}s"
        )

        if stats["task_summaries"]:
            print("   - Task performance:")
            for task in stats["task_summaries"]:
                print(
                    f"     • {task['task_name']}: {task['success_rate']:.1f}% success rate"
                )

        if stats["component_status"]:
            print("   - Component status:")
            for component, status in stats["component_status"].items():
                if "error" not in status:
                    print(f"     • {component}: operational")
                else:
                    print(f"     • {component}: error - {status['error']}")

        print(f"\n   - Configured tasks: {stats['configured_tasks']}")
        print(f"   - Enabled tasks: {stats['enabled_tasks']}")

        # Test scheduler (briefly)
        print("\n⏰ Testing scheduler...")
        pipeline.start_scheduler()
        print("   - Scheduler started")

        # Wait a moment then stop
        await asyncio.sleep(5)
        pipeline.stop_scheduler()
        print("   - Scheduler stopped")

        print("\n✅ Stage 11 Integration and Automation Pipeline testing completed!")
        print("\n🎯 Pipeline Features Implemented:")
        print("   ✓ External Data Integration - RSS feeds, APIs, weather data")
        print("   ✓ Automated Model Retraining - Performance monitoring & retraining")
        print("   ✓ Deployment Automation - Docker, CI/CD, testing integration")
        print("   ✓ System Health Monitoring - Metrics, alerts, health checks")
        print("   ✓ Automated Testing Framework - Unit, integration, validation tests")
        print("   ✓ Pipeline Orchestration - Scheduling, dependencies, error handling")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
