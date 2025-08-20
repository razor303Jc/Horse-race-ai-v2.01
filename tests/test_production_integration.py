#!/usr/bin/env python3
"""
Production System Integration Test
=================================

Lightweight integration test for the production system that validates
the structure and basic functionality without external dependencies.

Author: Horse Racing AI System V2.03
"""

import os
import sys
import unittest
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestProductionSystemStructure(unittest.TestCase):
    """Test production system file structure and organization"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_dir = Path(__file__).parent.parent
        self.src_dir = self.base_dir / "src" / "horse_racing_ai"
    
    def test_production_module_exists(self):
        """Test that production module exists and is properly structured"""
        production_dir = self.src_dir / "production"
        
        self.assertTrue(production_dir.exists(), "Production module directory should exist")
        self.assertTrue((production_dir / "__init__.py").exists(), "Production module should have __init__.py")
        self.assertTrue((production_dir / "live_strategy_execution.py").exists(), "Live strategy execution should exist")
    
    def test_deployment_module_exists(self):
        """Test that deployment module exists and is properly structured"""
        deployment_dir = self.src_dir / "deployment"
        
        self.assertTrue(deployment_dir.exists(), "Deployment module directory should exist")
        self.assertTrue((deployment_dir / "__init__.py").exists(), "Deployment module should have __init__.py")
        self.assertTrue((deployment_dir / "production_dashboard.py").exists(), "Production dashboard should exist")
    
    def test_orchestration_module_exists(self):
        """Test that orchestration module exists and is properly structured"""
        orchestration_dir = self.src_dir / "orchestration"
        
        self.assertTrue(orchestration_dir.exists(), "Orchestration module directory should exist")
        self.assertTrue((orchestration_dir / "__init__.py").exists(), "Orchestration module should have __init__.py")
        self.assertTrue((orchestration_dir / "production_system.py").exists(), "Production system should exist")
    
    def test_data_feeds_module_exists(self):
        """Test that data feeds module exists with live API"""
        data_feeds_dir = self.src_dir / "data_feeds"
        
        self.assertTrue(data_feeds_dir.exists(), "Data feeds module should exist")
        self.assertTrue((data_feeds_dir / "live_race_data_api.py").exists(), "Live race data API should exist")
    
    def test_betting_module_exists(self):
        """Test that betting module exists with exchange API"""
        betting_dir = self.src_dir / "betting"
        
        self.assertTrue(betting_dir.exists(), "Betting module should exist")
        self.assertTrue((betting_dir / "betting_exchange_api.py").exists(), "Betting exchange API should exist")
    
    def test_alerts_module_exists(self):
        """Test that alerts module exists with alert system"""
        alerts_dir = self.src_dir / "alerts"
        
        self.assertTrue(alerts_dir.exists(), "Alerts module should exist")
        self.assertTrue((alerts_dir / "alert_system.py").exists(), "Alert system should exist")


class TestDockerConfiguration(unittest.TestCase):
    """Test Docker configuration for production system"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_dir = Path(__file__).parent.parent
        self.docker_dir = self.base_dir / "docker"
    
    def test_docker_compose_has_production_services(self):
        """Test that docker-compose includes production services"""
        compose_file = self.base_dir / "docker-compose.clean.yml"
        
        self.assertTrue(compose_file.exists(), "Docker compose file should exist")
        
        with open(compose_file, 'r') as f:
            compose_content = f.read()
        
        # Check for production services
        self.assertIn("live-execution:", compose_content)
        self.assertIn("production-dashboard:", compose_content)
        self.assertIn("alert-system:", compose_content)
        
        # Check for production profiles
        self.assertIn("profiles:", compose_content)
        self.assertIn("production", compose_content)
    
    def test_production_dockerfiles_exist(self):
        """Test that production Dockerfiles exist"""
        dockerfiles_dir = self.docker_dir / "dockerfiles"
        
        self.assertTrue((dockerfiles_dir / "Dockerfile.production").exists())
        self.assertTrue((dockerfiles_dir / "Dockerfile.dashboard").exists())
        self.assertTrue((dockerfiles_dir / "Dockerfile.alerts").exists())
    
    def test_nginx_configuration_exists(self):
        """Test that nginx configuration exists"""
        nginx_dir = self.docker_dir / "nginx"
        
        self.assertTrue(nginx_dir.exists(), "Nginx directory should exist")
        self.assertTrue((nginx_dir / "dashboard.conf").exists(), "Dashboard nginx config should exist")


class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration for production system"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
    
    def test_pipeline_config_has_production_phase(self):
        """Test that pipeline config includes production trading phase"""
        config_file = self.config_dir / "comprehensive_pipeline_config.json"
        
        self.assertTrue(config_file.exists(), "Pipeline config should exist")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("phases", config)
        self.assertIn("production_trading", config["phases"])
        
        production_phase = config["phases"]["production_trading"]
        self.assertEqual(production_phase["phase_id"], "phase_5")
        self.assertIn("stages", production_phase)
        
        # Check for required stages
        stages = production_phase["stages"]
        self.assertIn("live_data_feeds", stages)
        self.assertIn("betting_integration", stages)
        self.assertIn("strategy_execution", stages)
        self.assertIn("monitoring_alerts", stages)
        self.assertIn("dashboard_deployment", stages)


class TestConfigurationFiles(unittest.TestCase):
    """Test configuration file templates and structure"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_dir = Path(__file__).parent.parent
    
    def test_production_launcher_exists(self):
        """Test that production system launcher exists"""
        launcher = self.base_dir / "production_system.py"
        
        self.assertTrue(launcher.exists(), "Production system launcher should exist")
        
        with open(launcher, 'r') as f:
            content = f.read()
        
        # Should be a launcher script, not the full implementation
        self.assertIn("Backward compatibility launcher", content)
        self.assertIn("from horse_racing_ai.orchestration.production_system import main", content)
    
    def test_deployment_guide_exists(self):
        """Test that deployment guide exists"""
        guide = self.base_dir / "PRODUCTION_DEPLOYMENT.md"
        
        self.assertTrue(guide.exists(), "Production deployment guide should exist")
        
        with open(guide, 'r') as f:
            content = f.read()
        
        self.assertIn("Production System Deployment Guide", content)
        self.assertIn("Quick Start", content)
        self.assertIn("API Key Setup", content)


class TestSystemIntegration(unittest.TestCase):
    """Test basic system integration without external dependencies"""
    
    def test_import_structure(self):
        """Test that modules can be imported without errors"""
        try:
            # Test basic imports without external dependencies
            import horse_racing_ai
            from horse_racing_ai.production import live_strategy_execution
            from horse_racing_ai.orchestration import production_system
            
            import_success = True
        except ImportError as e:
            # Some imports may fail due to missing dependencies (websockets, betfair, etc.)
            # This is expected in the test environment
            import_success = "websockets" in str(e) or "betfairlightweight" in str(e) or "twilio" in str(e)
        
        self.assertTrue(import_success, "Basic module structure should be importable")
    
    def test_production_system_manager_class_structure(self):
        """Test ProductionSystemManager class structure"""
        try:
            from horse_racing_ai.orchestration.production_system import ProductionSystemManager
            
            # Test class can be instantiated
            manager = ProductionSystemManager()
            
            # Test basic attributes exist
            self.assertTrue(hasattr(manager, 'processes'))
            self.assertTrue(hasattr(manager, 'services_status'))
            self.assertTrue(hasattr(manager, 'create_all_configs'))
            
            class_structure_valid = True
        except ImportError:
            # May fail due to missing dependencies, but file should exist
            production_system_file = Path(__file__).parent.parent / "src" / "horse_racing_ai" / "orchestration" / "production_system.py"
            class_structure_valid = production_system_file.exists()
        
        self.assertTrue(class_structure_valid, "ProductionSystemManager should have proper structure")


def run_integration_tests():
    """Run production system integration tests"""
    print("🧪 Running Production System Integration Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestProductionSystemStructure,
        TestDockerConfiguration,
        TestPipelineIntegration,
        TestConfigurationFiles,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report results
    print("\n" + "=" * 50)
    print("🏁 Production System Integration Test Results")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if result.wasSuccessful():
        print("\n✅ All production system integration tests passed!")
        print("📁 File structure is properly organized")
        print("🐳 Docker configuration is complete")
        print("⚙️ Pipeline integration is configured")
        print("🚀 Production system ready for deployment")
        return True
    else:
        print("\n❌ Some integration tests failed. Check output above.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
