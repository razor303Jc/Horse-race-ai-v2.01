# Dockerfile for Bulk Uploader
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bulk uploader files
COPY . .

# Make scripts executable
RUN chmod +x cli.py container_runner.py

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BULK_UPLOAD_MODE=daily_downloads

# Default command
CMD ["python", "container_runner.py"]
