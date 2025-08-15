#!/usr/bin/env python3
"""
Integration tests for Enhanced Error Handling System - Phase 2A
"""

import pytest
import sys
import os
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from tools.error_handling.pipeline_error_handler import (
        PipelineErrorHandler, ErrorCategory, ErrorSeverity, 
        handle_pipeline_errors, get_error_handler
    )
    from tools.error_handling.recovery_strategies import (
        DatabaseRecoveryManager, NetworkRecoveryManager,
        MLTrainingRecoveryManager, FileSystemRecoveryManager,
        CacheRecoveryManager, RecoveryResult
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestPipelineErrorHandler:
    """Test suite for pipeline error handling."""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler for testing."""
        return PipelineErrorHandler()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_error_classification(self, error_handler):
        """Test automatic error classification."""
        print("🔍 Testing error classification...")
        
        # Test network error
        network_error = ConnectionError("Connection timeout to database")
        category, severity = error_handler.classify_error(network_error)
        assert category == ErrorCategory.NETWORK
        assert severity == ErrorSeverity.MEDIUM
        print("✅ Network error classified correctly")
        
        # Test database error
        db_error = Exception("database connection failed")
        category, severity = error_handler.classify_error(db_error)
        assert category == ErrorCategory.DATABASE
        print("✅ Database error classified correctly")
        
        # Test file system error
        fs_error = FileNotFoundError("No such file or directory")
        category, severity = error_handler.classify_error(fs_error)
        assert category == ErrorCategory.FILE_SYSTEM
        assert severity == ErrorSeverity.MEDIUM
        print("✅ File system error classified correctly")
    
    def test_error_context_creation(self, error_handler):
        """Test error context creation with metadata."""
        print("📊 Testing error context creation...")
        
        try:
            raise ValueError("Test validation error")
        except Exception as e:
            context = error_handler.create_error_context(
                e, 
                context_data={"test": "data", "user_id": 123}
            )
            
            assert context.error_type == "ValueError"
            assert context.error_message == "Test validation error"
            assert context.context_data["test"] == "data"
            assert context.context_data["user_id"] == 123
            assert context.retry_count == 0
            print("✅ Error context created with correct metadata")
    
    def test_retry_mechanism(self, error_handler):
        """Test retry mechanism with exponential backoff."""
        print("🔄 Testing retry mechanism...")
        
        call_count = 0
        
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary network failure")
            return "Success after retries"
        
        start_time = time.time()
        result = error_handler.retry_with_backoff(
            flaky_function,
            context_data={"test": "retry"}
        )
        duration = time.time() - start_time
        
        assert result == "Success after retries"
        assert call_count == 3
        assert duration > 1.0  # Should have delays from retries
        print(f"✅ Retry succeeded after {call_count} attempts in {duration:.2f}s")
    
    def test_error_suppression(self, error_handler):
        """Test error suppression with fallback values."""
        print("🛡️ Testing error suppression...")
        
        with error_handler.handle_errors(
            context_data={"test": "suppression"},
            suppress_exceptions=True,
            fallback_value="fallback_result"
        ):
            raise RuntimeError("This error should be suppressed")
        
        # Should not raise an exception
        print("✅ Error suppressed successfully")
    
    def test_decorator_functionality(self):
        """Test error handling decorator."""
        print("🎯 Testing error handling decorator...")
        
        @handle_pipeline_errors(retry=True, context_data={"test": "decorator"})
        def decorated_function(fail_count: int = 0):
            if hasattr(decorated_function, '_call_count'):
                decorated_function._call_count += 1
            else:
                decorated_function._call_count = 1
            
            if decorated_function._call_count <= fail_count:
                raise ConnectionError("Temporary failure")
            return f"Success after {decorated_function._call_count} attempts"
        
        result = decorated_function(fail_count=2)
        assert "Success after" in result
        print("✅ Decorator handled retries correctly")
    
    def test_error_statistics(self, error_handler):
        """Test error statistics tracking."""
        print("📈 Testing error statistics...")
        
        # Generate some test errors
        for i in range(3):
            try:
                if i == 0:
                    raise ConnectionError("Network issue")
                elif i == 1:
                    raise FileNotFoundError("File missing")
                else:
                    raise ValueError("Validation error")
            except Exception as e:
                context = error_handler.create_error_context(e)
                error_handler.error_history.append(context)
        
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 3
        assert "network" in stats["categories"]
        assert "filesystem" in stats["categories"]
        print(f"✅ Statistics: {stats['total_errors']} errors tracked")


class TestRecoveryStrategies:
    """Test suite for recovery strategies."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_file_system_recovery(self, temp_dir):
        """Test file system recovery with backup locations."""
        print("📁 Testing file system recovery...")
        
        primary_dir = os.path.join(temp_dir, "primary")
        backup_dir = os.path.join(temp_dir, "backup")
        
        fs_recovery = FileSystemRecoveryManager(primary_dir, [backup_dir])
        
        # Test saving file
        result = fs_recovery.save_file("test.txt", "Hello, world!", use_pickle=False)
        assert result.success
        assert "primary" in result.method_used
        print("✅ File saved to primary location")
        
        # Test loading file
        result = fs_recovery.load_file("test.txt", use_pickle=False)
        assert result.success
        assert result.fallback_data == "Hello, world!"
        print("✅ File loaded from primary location")
        
        # Test backup location (simulate primary failure)
        shutil.rmtree(primary_dir)
        result = fs_recovery.save_file("backup_test.txt", "Backup data", use_pickle=False)
        assert result.success
        assert "backup" in result.method_used
        print("✅ File saved to backup location when primary failed")
    
    def test_ml_training_recovery(self, temp_dir):
        """Test ML training recovery with fallback models."""
        print("🤖 Testing ML training recovery...")
        
        ml_recovery = MLTrainingRecoveryManager(
            fallback_models_dir=os.path.join(temp_dir, "models")
        )
        
        # Test creating simple model
        result = ml_recovery.create_simple_model("linear_regression")
        assert result.success
        assert result.fallback_data is not None
        print("✅ Simple model created successfully")
        
        # Test saving fallback model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        success = ml_recovery.save_fallback_model(
            model, "test_model", {"accuracy": 0.85}
        )
        assert success
        print("✅ Fallback model saved")
        
        # Test loading fallback model
        result = ml_recovery.load_fallback_model("test_model")
        assert result.success
        assert result.fallback_data is not None
        print("✅ Fallback model loaded")
    
    def test_network_recovery_circuit_breaker(self):
        """Test network recovery with circuit breaker."""
        print("🌐 Testing network recovery circuit breaker...")
        
        network_recovery = NetworkRecoveryManager(failure_threshold=2, recovery_timeout=1)
        
        # Test normal operation
        assert not network_recovery.is_circuit_open()
        print("✅ Circuit initially closed")
        
        # Test failure accumulation
        network_recovery.record_failure()
        network_recovery.record_failure()
        assert network_recovery.is_circuit_open()
        print("✅ Circuit opened after failures")
        
        # Test recovery timeout
        time.sleep(1.1)  # Wait for recovery timeout
        assert not network_recovery.is_circuit_open()
        print("✅ Circuit reset after timeout")
    
    def test_cache_recovery_fallback(self):
        """Test cache recovery with memory fallback."""
        print("💾 Testing cache recovery fallback...")
        
        # Test with invalid Redis config to force memory fallback
        cache_recovery = CacheRecoveryManager({"host": "invalid", "port": 9999})
        
        # Test setting value (should fallback to memory)
        result = cache_recovery.set("test_key", {"data": "test_value"})
        assert result.success
        assert "memory" in result.method_used
        print("✅ Cache set fallback to memory")
        
        # Test getting value from memory cache
        result = cache_recovery.get("test_key")
        assert result.success
        assert result.fallback_data["data"] == "test_value"
        print("✅ Cache get from memory successful")


def test_integration_error_handling_and_recovery():
    """Integration test combining error handling and recovery."""
    print("🔗 Testing integrated error handling and recovery...")
    
    error_handler = PipelineErrorHandler()
    
    @handle_pipeline_errors(retry=True, context_data={"integration": "test"})
    def integrated_function():
        # Simulate a function that uses recovery strategies
        from tools.error_handling.recovery_strategies import FileSystemRecoveryManager
        
        fs_recovery = FileSystemRecoveryManager("/tmp/test_primary", ["/tmp/test_backup"])
        result = fs_recovery.save_file("integration_test.txt", "test data", use_pickle=False)
        
        if not result.success:
            raise RuntimeError("File system operation failed")
        
        return "Integration test successful"
    
    result = integrated_function()
    assert "successful" in result
    print("✅ Integrated error handling and recovery working")


def run_error_handling_tests():
    """Run all error handling tests."""
    print("🚨 Enhanced Error Handling System - Integration Tests")
    print("=" * 60)
    
    # Create test instances
    error_test = TestPipelineErrorHandler()
    recovery_test = TestRecoveryStrategies()
    
    # Run tests
    tests = [
        ("Error Classification", lambda: error_test.test_error_classification(PipelineErrorHandler())),
        ("Error Context Creation", lambda: error_test.test_error_context_creation(PipelineErrorHandler())),
        ("Retry Mechanism", lambda: error_test.test_retry_mechanism(PipelineErrorHandler())),
        ("Error Suppression", lambda: error_test.test_error_suppression(PipelineErrorHandler())),
        ("Decorator Functionality", lambda: error_test.test_decorator_functionality()),
        ("Error Statistics", lambda: error_test.test_error_statistics(PipelineErrorHandler())),
        ("File System Recovery", lambda: recovery_test.test_file_system_recovery(tempfile.mkdtemp())),
        ("ML Training Recovery", lambda: recovery_test.test_ml_training_recovery(tempfile.mkdtemp())),
        ("Network Circuit Breaker", lambda: recovery_test.test_network_recovery_circuit_breaker()),
        ("Cache Recovery Fallback", lambda: recovery_test.test_cache_recovery_fallback()),
        ("Integration Test", lambda: test_integration_error_handling_and_recovery()),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        try:
            test_func()
            print(f"✅ {test_name} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed! 🚀")
        print("📊 Enhanced error handling system ready for production")
        return True
    else:
        print("⚠️  Some tests failed - review implementation")
        return False


if __name__ == "__main__":
    success = run_error_handling_tests()
    sys.exit(0 if success else 1)
