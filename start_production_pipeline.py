#!/usr/bin/env python3
"""
🚀 Production Startup Script for 17-Stage Dynamic Pipeline
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator

logger = logging.getLogger(__name__)

class ProductionPipelineService:
    def __init__(self):
        self.orchestrator = DailyPipelineOrchestrator()
        self.running = True

    async def run_production_service(self):
        """Run the production pipeline service"""
        logger.info("🚀 Starting Production 17-Stage Dynamic Pipeline Service")
        
        while self.running:
            try:
                # Generate and execute dynamic schedule
                schedule = self.orchestrator.generate_dynamic_schedule()
                
                if schedule:
                    logger.info("✅ Dynamic schedule generated successfully")
                    
                    # Execute pipeline according to schedule
                    await self.orchestrator.execute_dynamic_pipeline(schedule)
                    
                    # Wait until next run (24 hours)
                    await asyncio.sleep(24 * 60 * 60)
                else:
                    logger.error("❌ Failed to generate schedule - retrying in 1 hour")
                    await asyncio.sleep(60 * 60)
                    
            except Exception as e:
                logger.error(f"❌ Production pipeline error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute

    def stop_service(self):
        """Stop the production service"""
        self.running = False
        logger.info("🛑 Production pipeline service stopping...")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("📶 Shutdown signal received")
    service.stop_service()

if __name__ == "__main__":
    service = ProductionPipelineService()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the service
    asyncio.run(service.run_production_service())
