# Official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional ML dependencies
RUN pip install --no-cache-dir scikit-learn==1.7.1 httpx

# Install Playwright browsers as root first
RUN playwright install --with-deps chromium

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY main.py .

# Copy demo directory with all analysis scripts
COPY demos/ ./demos/

# Copy data analysis summary and any documentation
COPY RACE_DATA_ANALYSIS_SUMMARY.md* ./
COPY *.md* ./

# Install the package in development mode
RUN pip install -e .

# Create directories
RUN mkdir -p /app/data /app/logs /app/models /app/cache

# Create non-root user and set up permissions
RUN groupadd -r horseai && useradd -r -g horseai -m horseai
RUN chown -R horseai:horseai /app
RUN chmod -R 755 /app/logs /app/data /app/models /app/cache

# Install Playwright browsers for the horseai user
USER horseai
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
RUN playwright install chromium

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for any web services
EXPOSE 8000

# Default command - run the complete racing pipeline
CMD ["python", "demos/complete_racing_pipeline.py"]
