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
COPY app.py .

# Copy enhanced web application templates and static files
COPY templates/ ./templates/

# Copy racing analyzer components
COPY background_racing_analyzer.py .
COPY webapp_racing_interface.py .
COPY dynamic_racing_analyzer.py .

# Copy demo directory with all analysis scripts
COPY demos/ ./demos/

# Copy configuration and documentation (conditionally)
COPY config/ ./config/
COPY docs/ ./docs/
COPY *.md ./

# Copy startup scripts
COPY start_web_app.sh ./
RUN chmod +x start_web_app.sh

# Install the package in development mode
RUN pip install -e .

# Create directories
RUN mkdir -p /app/data /app/logs /app/models /app/cache /app/reports

# Create non-root user and set up permissions
RUN groupadd -r horseai && useradd -r -g horseai -m horseai
RUN chown -R horseai:horseai /app
RUN chmod -R 755 /app/logs /app/data /app/models /app/cache /app/reports

# Install Playwright browsers for the horseai user
USER horseai
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
RUN playwright install chromium

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose ports for web services
EXPOSE 5002 8000

# Default command - run the enhanced web application
CMD ["python", "app.py"]
