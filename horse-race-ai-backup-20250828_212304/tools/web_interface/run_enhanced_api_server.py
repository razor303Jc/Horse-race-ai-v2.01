#!/usr/bin/env python3
"""
Enhanced API Server Runner - V2.03
==================================

Standalone runner for the Enhanced API and Web Interface System.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.web_interface.enhanced_web_interface_pipeline import (
    EnhancedWebInterfacePipeline,
)

if __name__ == "__main__":
    # Run the pipeline
    pipeline = EnhancedWebInterfacePipeline()
    pipeline.run_stage("start")
