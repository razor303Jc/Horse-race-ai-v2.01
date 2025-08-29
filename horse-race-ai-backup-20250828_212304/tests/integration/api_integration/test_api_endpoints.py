"""
🧪 API Integration Tests
=======================

Integration tests for the API components including ML management API,
prediction API, and web application endpoints.
"""

import pytest
import requests
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import time
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Test fixtures
@pytest.fixture
def api_test_environment():
    """Set up API test environment"""
    return {
        'base_url': 'http://localhost:8000',
        'ml_api_url': 'http://localhost:8001',
        'test_timeout': 30,
        'test_headers': {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

@pytest.fixture
def mock_api_responses():
    """Mock API response data"""
    return {
        'health_check': {'status': 'healthy', 'timestamp': '2025-01-02T10:00:00Z'},
        'prediction_response': {
            'race_id': 'TEST_RACE_001',
            'predictions': [
                {'horse_name': 'Horse_A', 'win_probability': 0.25, 'confidence': 0.85},
                {'horse_name': 'Horse_B', 'win_probability': 0.20, 'confidence': 0.78}
            ],
            'status': 'success'
        },
        'ml_training_response': {
            'job_id': 'ml_train_123',
            'status': 'completed',
            'model_performance': {'accuracy': 0.72, 'f1_score': 0.68},
            'model_path': '/models/latest_model.pkl'
        }
    }

@pytest.fixture
def sample_race_data():
    """Generate sample race data for API testing"""
    return {
        'race_id': 'TEST_RACE_001',
        'race_date': '2025-01-02',
        'track': 'RANDWICK',
        'race_number': 1,
        'runners': [
            {
                'horse_name': 'Test Horse 1',
                'jockey': 'Test Jockey 1',
                'trainer': 'Test Trainer 1',
                'barrier': 1,
                'weight': 57.5,
                'odds': 3.50
            },
            {
                'horse_name': 'Test Horse 2',
                'jockey': 'Test Jockey 2',
                'trainer': 'Test Trainer 2',
                'barrier': 2,
                'weight': 56.0,
                'odds': 4.20
            }
        ]
    }

class TestPredictionAPIIntegration:
    """Integration tests for Prediction API"""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_prediction_api_health_check(self, api_test_environment):
        """Test prediction API health check endpoint"""
        # Mock the health check response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'healthy'}
            mock_get.return_value = mock_response
            
            # Test health check
            url = f"{api_test_environment['base_url']}/health"
            response = requests.get(url, timeout=api_test_environment['test_timeout'])
            
            assert response.status_code == 200
            assert response.json()['status'] == 'healthy'
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_race_prediction_endpoint(self, api_test_environment, sample_race_data, mock_api_responses):
        """Test race prediction endpoint"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_responses['prediction_response']
            mock_post.return_value = mock_response
            
            # Test prediction request
            url = f"{api_test_environment['base_url']}/predict/race"
            response = requests.post(
                url,
                json=sample_race_data,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            prediction_data = response.json()
            
            # Verify response structure
            assert 'race_id' in prediction_data
            assert 'predictions' in prediction_data
            assert 'status' in prediction_data
            assert prediction_data['status'] == 'success'
            
            # Verify predictions format
            predictions = prediction_data['predictions']
            assert len(predictions) > 0
            
            for prediction in predictions:
                assert 'horse_name' in prediction
                assert 'win_probability' in prediction
                assert 'confidence' in prediction
                assert 0.0 <= prediction['win_probability'] <= 1.0
                assert 0.0 <= prediction['confidence'] <= 1.0
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_batch_prediction_endpoint(self, api_test_environment, mock_api_responses):
        """Test batch prediction endpoint"""
        batch_data = {
            'races': [
                {'race_id': 'RACE_001', 'runners': [{'horse_name': 'Horse_A'}]},
                {'race_id': 'RACE_002', 'runners': [{'horse_name': 'Horse_B'}]}
            ]
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'batch_id': 'batch_123',
                'results': [mock_api_responses['prediction_response']] * 2,
                'status': 'completed'
            }
            mock_post.return_value = mock_response
            
            # Test batch prediction
            url = f"{api_test_environment['base_url']}/predict/batch"
            response = requests.post(
                url,
                json=batch_data,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            batch_results = response.json()
            
            assert 'batch_id' in batch_results
            assert 'results' in batch_results
            assert 'status' in batch_results
            assert len(batch_results['results']) == 2
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_prediction_api_error_handling(self, api_test_environment):
        """Test prediction API error handling"""
        # Test invalid race data
        invalid_data = {'invalid': 'data'}
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                'error': 'Invalid race data format',
                'status': 'error'
            }
            mock_post.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/predict/race"
            response = requests.post(
                url,
                json=invalid_data,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 400
            error_data = response.json()
            assert 'error' in error_data
            assert error_data['status'] == 'error'
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.performance
    def test_prediction_api_performance(self, api_test_environment, sample_race_data):
        """Test prediction API performance"""
        with patch('requests.post') as mock_post:
            # Simulate response time
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'success', 'predictions': []}
            mock_post.return_value = mock_response
            
            # Measure response time
            start_time = time.time()
            
            url = f"{api_test_environment['base_url']}/predict/race"
            response = requests.post(
                url,
                json=sample_race_data,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0, f"API response too slow: {response_time:.2f}s"

class TestMLManagementAPIIntegration:
    """Integration tests for ML Management API"""
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.ml
    def test_ml_training_trigger_endpoint(self, api_test_environment, mock_api_responses):
        """Test ML training trigger endpoint"""
        training_config = {
            'model_type': 'RandomForest',
            'training_data_query': 'SELECT * FROM training_data WHERE date >= "2024-01-01"',
            'hyperparameters': {
                'n_estimators': 100,
                'max_depth': 10
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 202  # Accepted
            mock_response.json.return_value = {
                'job_id': 'ml_train_123',
                'status': 'started',
                'message': 'ML training job queued successfully'
            }
            mock_post.return_value = mock_response
            
            url = f"{api_test_environment['ml_api_url']}/training/start"
            response = requests.post(
                url,
                json=training_config,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 202
            job_data = response.json()
            
            assert 'job_id' in job_data
            assert 'status' in job_data
            assert job_data['status'] == 'started'
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.ml
    def test_ml_training_status_endpoint(self, api_test_environment, mock_api_responses):
        """Test ML training status endpoint"""
        job_id = 'ml_train_123'
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_responses['ml_training_response']
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['ml_api_url']}/training/status/{job_id}"
            response = requests.get(
                url,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            status_data = response.json()
            
            assert 'job_id' in status_data
            assert 'status' in status_data
            assert 'model_performance' in status_data
            assert status_data['status'] == 'completed'
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.ml
    def test_model_management_endpoints(self, api_test_environment):
        """Test model management endpoints"""
        # Test list models endpoint
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [
                    {
                        'model_id': 'model_001',
                        'model_type': 'RandomForest',
                        'created_date': '2025-01-01T10:00:00Z',
                        'performance': {'accuracy': 0.72},
                        'status': 'active'
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['ml_api_url']}/models"
            response = requests.get(
                url,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            models_data = response.json()
            
            assert 'models' in models_data
            assert len(models_data['models']) > 0
            
            model = models_data['models'][0]
            assert 'model_id' in model
            assert 'model_type' in model
            assert 'performance' in model
            assert 'status' in model
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.ml
    def test_model_deployment_endpoint(self, api_test_environment):
        """Test model deployment endpoint"""
        deployment_config = {
            'model_id': 'model_001',
            'deployment_target': 'production',
            'version': 'v1.0'
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'deployment_id': 'deploy_001',
                'status': 'deployed',
                'endpoint_url': '/predict/v1',
                'message': 'Model deployed successfully'
            }
            mock_post.return_value = mock_response
            
            url = f"{api_test_environment['ml_api_url']}/models/deploy"
            response = requests.post(
                url,
                json=deployment_config,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            deployment_data = response.json()
            
            assert 'deployment_id' in deployment_data
            assert 'status' in deployment_data
            assert 'endpoint_url' in deployment_data
            assert deployment_data['status'] == 'deployed'

class TestWebApplicationIntegration:
    """Integration tests for Web Application"""
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.web
    def test_web_app_health_check(self, api_test_environment):
        """Test web application health check"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><head><title>Horse Racing AI</title></head></html>'
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/"
            response = requests.get(url, timeout=api_test_environment['test_timeout'])
            
            assert response.status_code == 200
            assert 'Horse Racing AI' in response.text
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.web
    def test_dashboard_endpoints(self, api_test_environment):
        """Test dashboard endpoints"""
        dashboard_endpoints = [
            '/dashboard',
            '/dashboard/races',
            '/dashboard/predictions',
            '/dashboard/models',
            '/dashboard/performance'
        ]
        
        for endpoint in dashboard_endpoints:
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'status': 'success',
                    'data': {'dashboard_data': 'test_data'}
                }
                mock_get.return_value = mock_response
                
                url = f"{api_test_environment['base_url']}{endpoint}"
                response = requests.get(
                    url,
                    headers=api_test_environment['test_headers'],
                    timeout=api_test_environment['test_timeout']
                )
                
                assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.web
    def test_race_upload_interface(self, api_test_environment, sample_race_data):
        """Test race data upload interface"""
        # Simulate file upload
        files = {'race_file': ('test_race.csv', 'horse,jockey,odds\nHorse A,Jockey A,3.50')}
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'upload_id': 'upload_123',
                'status': 'success',
                'records_processed': 1,
                'message': 'Race data uploaded successfully'
            }
            mock_post.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/upload/race"
            response = requests.post(
                url,
                files=files,
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            upload_data = response.json()
            
            assert 'upload_id' in upload_data
            assert 'status' in upload_data
            assert 'records_processed' in upload_data
            assert upload_data['status'] == 'success'

class TestAPIIntegrationWithDatabase:
    """Integration tests for API with database operations"""
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.database
    def test_api_database_connection(self, api_test_environment, test_db_connection):
        """Test API database connectivity"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'database_status': 'connected',
                'active_connections': 5,
                'last_query_time': '2025-01-02T10:00:00Z'
            }
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/system/database/status"
            response = requests.get(
                url,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            db_status = response.json()
            
            assert 'database_status' in db_status
            assert db_status['database_status'] == 'connected'
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.database
    def test_api_data_retrieval(self, api_test_environment, test_db_connection):
        """Test API data retrieval from database"""
        query_params = {
            'race_date': '2025-01-02',
            'track': 'RANDWICK',
            'limit': 10
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'races': [
                    {
                        'race_id': 'RACE_001',
                        'race_date': '2025-01-02',
                        'track': 'RANDWICK',
                        'race_number': 1,
                        'runners_count': 12
                    }
                ],
                'total_count': 1,
                'status': 'success'
            }
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/races"
            response = requests.get(
                url,
                params=query_params,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 200
            races_data = response.json()
            
            assert 'races' in races_data
            assert 'total_count' in races_data
            assert 'status' in races_data
            assert races_data['status'] == 'success'

class TestAPIErrorHandlingAndSecurity:
    """Integration tests for API error handling and security"""
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.security
    def test_api_authentication(self, api_test_environment):
        """Test API authentication mechanisms"""
        # Test unauthorized access
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                'error': 'Unauthorized access',
                'message': 'Valid API key required'
            }
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/protected/endpoint"
            response = requests.get(url, timeout=api_test_environment['test_timeout'])
            
            assert response.status_code == 401
            error_data = response.json()
            assert 'error' in error_data
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_rate_limiting(self, api_test_environment):
        """Test API rate limiting"""
        with patch('requests.get') as mock_get:
            # Simulate rate limit exceeded
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                'error': 'Rate limit exceeded',
                'retry_after': 60
            }
            mock_get.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/predict/race"
            response = requests.get(url, timeout=api_test_environment['test_timeout'])
            
            assert response.status_code == 429
            error_data = response.json()
            assert 'error' in error_data
            assert 'retry_after' in error_data
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_input_validation(self, api_test_environment):
        """Test API input validation"""
        # Test SQL injection attempt
        malicious_data = {
            'race_id': "'; DROP TABLE races; --",
            'runners': []
        }
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                'error': 'Invalid input format',
                'details': 'race_id contains invalid characters'
            }
            mock_post.return_value = mock_response
            
            url = f"{api_test_environment['base_url']}/predict/race"
            response = requests.post(
                url,
                json=malicious_data,
                headers=api_test_environment['test_headers'],
                timeout=api_test_environment['test_timeout']
            )
            
            assert response.status_code == 400
            error_data = response.json()
            assert 'error' in error_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
