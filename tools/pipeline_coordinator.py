#!/usr/bin/env python3
"""
Pipeline Coordinator - Simple coordinator for data pipeline
"""
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Pipeline Coordinator starting...")
    
    # Create required directories
    os.makedirs('/app/data', exist_ok=True)
    os.makedirs('/app/logs', exist_ok=True)
    
    while True:
        logger.info("📊 Pipeline coordinator running...")
        time.sleep(30)

if __name__ == "__main__":
    main()
