#!/usr/bin/env python3
"""
🚀 Docker Integration Manager
Manages all Phase 1 & 2 improvements within Docker environment
"""

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add Docker paths to Python path
docker_root = Path(__file__).parent
sys.path.insert(0, str(docker_root))
sys.path.insert(0, str(docker_root / "ml_training"))
sys.path.insert(0, str(docker_root / "monitoring"))
sys.path.insert(0, str(docker_root / "error_handling"))
sys.path.insert(0, str(docker_root / "caching"))
sys.path.insert(0, str(docker_root / "database"))


class DockerIntegrationManager:
    """Manages integration of all Phase 1 & 2 improvements in Docker environment"""

    def __init__(self):
        self.docker_root = Path(__file__).parent
        self.components = {
            "ml_training": "unified_ml_trainer.py",
            "monitoring": "advanced_performance_monitor.py",
            "error_handling": "pipeline_error_handler.py",
            "caching": "pipeline_cache_manager.py",
            "database": "performance_monitor.py",
        }
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for integration manager"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.docker_root / "integration.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("DockerIntegration")

    def verify_component(self, component: str, module_file: str) -> bool:
        """Verify a component can be imported and initialized"""
        try:
            module_path = self.docker_root / component / module_file
            if not module_path.exists():
                self.logger.error(
                    f"❌ {component}: Module file not found at {module_path}"
                )
                return False

            # Try to import the module
            spec = importlib.util.spec_from_file_location(
                f"{component}_module", module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.logger.info(f"✅ {component}: Module imported successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ {component}: Import failed - {str(e)}")
            return False

    def verify_all_components(self) -> Dict[str, bool]:
        """Verify all components are working in Docker environment"""
        results = {}

        self.logger.info("🔍 Verifying all Phase 1 & 2 components...")

        for component, module_file in self.components.items():
            results[component] = self.verify_component(component, module_file)

        return results

    def get_component_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about each component"""
        stats = {}

        for component, module_file in self.components.items():
            module_path = self.docker_root / component / module_file
            if module_path.exists():
                stat = module_path.stat()
                with open(module_path, "r") as f:
                    lines = len(f.readlines())

                stats[component] = {
                    "file_size": f"{stat.st_size / 1024:.1f} KB",
                    "line_count": lines,
                    "last_modified": stat.st_mtime,
                    "path": str(module_path),
                }
            else:
                stats[component] = {"status": "Not found"}

        return stats

    def create_integration_test(self) -> bool:
        """Create a comprehensive integration test"""
        try:
            self.logger.info("🧪 Running integration tests...")

            # Test ML Training
            try:
                from unified_ml_trainer import UnifiedMLTrainer

                trainer = UnifiedMLTrainer()
                self.logger.info("✅ ML Training: UnifiedMLTrainer initialized")
            except ImportError as e:
                self.logger.warning(f"⚠️ ML Training: Import issue - {e}")

            # Test Monitoring
            try:
                from advanced_performance_monitor import AdvancedPerformanceMonitor

                monitor = AdvancedPerformanceMonitor()
                self.logger.info(
                    "✅ Monitoring: AdvancedPerformanceMonitor initialized"
                )
            except ImportError as e:
                self.logger.warning(f"⚠️ Monitoring: Import issue - {e}")

            # Test Error Handling
            try:
                from pipeline_error_handler import PipelineErrorHandler

                handler = PipelineErrorHandler()
                self.logger.info("✅ Error Handling: PipelineErrorHandler initialized")
            except ImportError as e:
                self.logger.warning(f"⚠️ Error Handling: Import issue - {e}")

            # Test Caching
            try:
                from pipeline_cache_manager import PipelineCacheManager

                cache = PipelineCacheManager()
                self.logger.info("✅ Caching: PipelineCacheManager initialized")
            except ImportError as e:
                self.logger.warning(f"⚠️ Caching: Import issue - {e}")

            self.logger.info("🎉 Integration test completed")
            return True

        except Exception as e:
            self.logger.error(f"❌ Integration test failed: {e}")
            return False

    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        report = []
        report.append("🚀 DOCKER INTEGRATION REPORT")
        report.append("=" * 50)
        report.append("")

        # Component verification
        results = self.verify_all_components()
        report.append("📋 COMPONENT VERIFICATION:")
        for component, status in results.items():
            status_icon = "✅" if status else "❌"
            report.append(f"  {status_icon} {component.replace('_', ' ').title()}")
        report.append("")

        # Component statistics
        stats = self.get_component_stats()
        report.append("📊 COMPONENT STATISTICS:")
        total_lines = 0
        for component, data in stats.items():
            if "line_count" in data:
                report.append(
                    f"  {component}: {data['line_count']} lines, {data['file_size']}"
                )
                total_lines += data["line_count"]
        report.append(f"  TOTAL: {total_lines} lines of integrated code")
        report.append("")

        # Integration status
        all_verified = all(results.values())
        if all_verified:
            report.append("🎉 STATUS: ALL COMPONENTS SUCCESSFULLY INTEGRATED")
        else:
            failed = [comp for comp, status in results.items() if not status]
            report.append(
                f"⚠️ STATUS: {len(failed)} components need attention: {', '.join(failed)}"
            )

        return "\n".join(report)


def main():
    """Main integration verification"""
    manager = DockerIntegrationManager()

    print("🚀 Starting Docker Integration Verification...")
    print()

    # Run integration test
    manager.create_integration_test()

    # Generate and display report
    report = manager.generate_integration_report()
    print(report)

    # Save report to file
    with open(manager.docker_root / "integration_report.txt", "w") as f:
        f.write(report)

    print(
        f"\n📄 Full report saved to: {manager.docker_root / 'integration_report.txt'}"
    )


if __name__ == "__main__":
    main()
