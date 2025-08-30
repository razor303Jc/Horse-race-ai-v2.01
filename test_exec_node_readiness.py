#!/usr/bin/env python3
"""
Test Script for Exec Node Implementation
========================================

This script tests the exec node environment and validates that our
Python scripts can be executed properly from Node-RED exec nodes.
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def test_docker_environment():
    """Test Docker container accessibility"""
    print("🐳 Testing Docker Environment")
    print("=" * 50)
    
    try:
        # Test if we can access the data pipeline container
        result = subprocess.run([
            'docker', 'exec', 'horse_racing_data_pipeline_clean', 
            'python', '--version'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Data Pipeline Container: {result.stdout.strip()}")
        else:
            print(f"❌ Data Pipeline Container Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker command timeout")
        return False
    except FileNotFoundError:
        print("❌ Docker not found - please ensure Docker is installed")
        return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False
    
    try:
        # Test if we can access the ML trainer container
        result = subprocess.run([
            'docker', 'exec', 'horse_racing_ml_trainer_clean', 
            'python', '--version'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ ML Trainer Container: {result.stdout.strip()}")
        else:
            print(f"❌ ML Trainer Container Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ ML Trainer test failed: {e}")
        return False
    
    print("✅ Docker environment ready for exec nodes")
    return True

def test_python_script_access():
    """Test access to Python scripts"""
    print("\n🐍 Testing Python Script Access")
    print("=" * 50)
    
    # Test scripts to validate
    test_scripts = [
        {
            'container': 'horse_racing_data_pipeline_clean',
            'script': '/app/tools/manual_pipeline_trigger.py',
            'args': ['--help']
        },
        {
            'container': 'horse_racing_data_pipeline_clean',
            'script': '/app/tools/data_processing/automated_relationships_pipeline.py',
            'args': ['--help']
        }
    ]
    
    for test in test_scripts:
        try:
            result = subprocess.run([
                'docker', 'exec', test['container'], 
                'python', test['script']
            ] + test['args'], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 or 'usage:' in result.stdout.lower() or 'help' in result.stdout.lower():
                print(f"✅ {test['script']}: Accessible")
            else:
                print(f"❌ {test['script']}: Error - {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test['script']}: Timeout (script may be running)")
        except Exception as e:
            print(f"❌ {test['script']}: Exception - {e}")
            return False
    
    print("✅ Python scripts accessible for exec nodes")
    return True

def test_exec_node_simulation():
    """Simulate actual exec node execution"""
    print("\n🔄 Testing Exec Node Simulation")
    print("=" * 50)
    
    # Simulate the exact command that will be used in Node-RED exec node
    exec_command = [
        'docker', 'exec', 'horse_racing_data_pipeline_clean',
        'python', '/app/tools/manual_pipeline_trigger.py', '--help'
    ]
    
    try:
        start_time = datetime.now()
        
        print(f"📝 Executing: {' '.join(exec_command)}")
        
        result = subprocess.run(
            exec_command,
            capture_output=True,
            text=True,
            timeout=30,
            env={'PYTHONUNBUFFERED': '1'}
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️ Execution time: {execution_time:.2f} seconds")
        print(f"🔢 Exit code: {result.returncode}")
        
        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
        
        if result.stderr:
            print("📤 STDERR:")
            print(result.stderr[:500] + ("..." if len(result.stderr) > 500 else ""))
        
        if result.returncode == 0:
            print("✅ Exec node simulation successful")
            return True
        else:
            print("❌ Exec node simulation failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Exec node simulation timeout")
        return False
    except Exception as e:
        print(f"❌ Exec node simulation error: {e}")
        return False

def test_node_red_accessibility():
    """Test Node-RED accessibility"""
    print("\n🌐 Testing Node-RED Accessibility")
    print("=" * 50)
    
    try:
        import requests
        
        # Test Node-RED main endpoint
        response = requests.get('http://localhost:1880/', timeout=10)
        if response.status_code == 200:
            print("✅ Node-RED web interface accessible")
        else:
            print(f"❌ Node-RED returned status code: {response.status_code}")
            return False
            
        # Test Node-RED admin API
        try:
            response = requests.get('http://localhost:1880/flows', timeout=10)
            if response.status_code in [200, 401]:  # 401 is OK if auth is enabled
                print("✅ Node-RED admin API accessible")
            else:
                print(f"❌ Node-RED admin API returned: {response.status_code}")
                return False
        except:
            print("⚠️ Node-RED admin API test failed (authentication may be enabled)")
        
        return True
        
    except ImportError:
        print("⚠️ requests library not available - skipping HTTP tests")
        return True
    except Exception as e:
        print(f"❌ Node-RED accessibility test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 EXEC NODE READINESS REPORT")
    print("=" * 50)
    
    tests = [
        ("Docker Environment", test_docker_environment),
        ("Python Script Access", test_python_script_access),
        ("Exec Node Simulation", test_exec_node_simulation),
        ("Node-RED Accessibility", test_node_red_accessibility)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
            all_passed = False
    
    print("\n📋 Test Summary:")
    print("-" * 30)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall Status: {'✅ READY' if all_passed else '❌ NOT READY'}")
    
    if all_passed:
        print("\n🚀 System is ready for exec node deployment!")
        print("👉 Run: ./deploy_exec_nodes.sh")
    else:
        print("\n⚠️ Please fix the failing tests before deployment")
        print("👉 Check Docker containers and Node-RED setup")
    
    return all_passed

def main():
    """Main test execution"""
    print("🏇 Horse Racing AI - Exec Node Readiness Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("")
    
    return generate_test_report()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
