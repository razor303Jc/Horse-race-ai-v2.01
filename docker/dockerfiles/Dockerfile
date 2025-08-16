# Auto-Downloader Service Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY docker/requirements/requirements-auto-downloader.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-auto-downloader.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY tools/ ./tools/

# Create necessary directories
RUN mkdir -p data logs cache && \
    chmod 777 data logs cache

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user for security using environment variable
ARG USER_NAME=jc
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USER_NAME} && \
    chown -R ${USER_NAME}:${USER_NAME} /app
USER ${USER_NAME}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from src.automation.docker_config import validate_docker_setup; exit(0 if validate_docker_setup() else 1)" || exit 1

# Default command
CMD ["python", "run_docker_auto_downloader.py", "--mode", "scheduled", "--log-level", "INFO"]
