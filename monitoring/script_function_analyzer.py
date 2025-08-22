#!/usr/bin/env python3
"""
Script and Function Analysis System
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

class ScriptFunctionAnalyzer:
    """Simple analyzer for testing"""
    
    def __init__(self, log_dir=None):
        self.log_dir = log_dir or "/home/jc/Documents/Horse-race-ai-v2.03/monitoring/analysis_logs"
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('ScriptAnalyzer')
        
        self.function_calls = []
        print(f"✅ ScriptFunctionAnalyzer initialized with session: {self.session_id}")
    
    def track_function(self, func):
        """Simple function decorator"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                self.function_calls.append({
                    'function_name': func.__name__,
                    'success': True,
                    'duration_ms': duration
                })
                self.logger.info(f"✅ {func.__name__} - {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                self.function_calls.append({
                    'function_name': func.__name__,
                    'success': False,
                    'duration_ms': duration,
                    'error': str(e)
                })
                self.logger.error(f"❌ {func.__name__} - {str(e)}")
                raise
        return wrapper
    
    def generate_report(self):
        """Generate simple report"""
        return {
            'session_id': self.session_id,
            'function_statistics': self.function_calls,
            'summary': {
                'total_functions_tracked': len(set(f['function_name'] for f in self.function_calls)),
                'total_function_calls': len(self.function_calls)
            }
        }

def track_function(func):
    """Global decorator"""
    analyzer = ScriptFunctionAnalyzer()
    return analyzer.track_function(func)

print("✅ Script Function Analyzer module loaded successfully")
