"""
Docker configuration validation for auto-downloader
"""

import logging
import os

logger = logging.getLogger(__name__)

def validate_docker_setup():
    """Validate that Docker environment is properly configured"""
    try:
        # Check required environment variables
        required_vars = ['DATABASE_URL', 'REDIS_URL']
        
        for var in required_vars:
            if not os.getenv(var):
                logger.warning(f"Missing environment variable: {var}")
                return False
        
        # Check required directories
        required_dirs = ['/app/data', '/app/logs', '/app/cache']
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
        
        logger.info("✅ Docker setup validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Docker setup validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_docker_setup()
