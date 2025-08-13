# Racing News Analyzer Documentation

## Overview

The Racing News Analyzer is an automated system that uses Ollama AI models to scrape, analyze, and report on horse racing news from **5 major racing news sources** daily. It provides sentiment analysis, key topic extraction, and generates comprehensive daily reports with multi-source intelligence.

## Features

### 🌐 Multi-Source News Collection

- **Racing Post**: https://www.racingpost.com/news/
- **Sky Sports Racing**: https://www.skysports.com/racing/news
- **BBC Sport Horse Racing**: https://www.bbc.co.uk/sport/horse-racing
- **Sporting Life Racing**: https://www.sportinglife.com/racing/news
- **At The Races**: https://www.attheraces.com/news

## Features

### 🤖 AI-Powered Analysis

- **Model**: Llama 3.1 8B (via Ollama)
- **Sentiment Analysis**: Analyzes market sentiment (-1 to +1 scale)
- **Entity Extraction**: Horses, jockeys, trainers, race meetings
- **Topic Identification**: Key themes and market insights

### 📰 Multi-Source News Scraping

- **5 Major Sources**: Racing Post, Sky Sports, BBC Sport, Sporting Life, At The Races
- **Frequency**: 3 times daily (08:00, 14:00, 20:00) across all sources
- **Volume**: 15-20 articles per run from diverse sources
- **Storage**: SQLite database with full article content, analysis, and source attribution

### 📊 Reporting

- **Daily Reports**: Comprehensive markdown reports
- **Dashboard**: Real-time monitoring and status
- **Trend Analysis**: Sentiment trends over time

## Installation

### Quick Setup

```bash
cd /home/jc/Documents/Horse-race-ai-v2.01
./setup_news_analyzer.sh
```

### Manual Installation

1. **Install Dependencies**:

   ```bash
   sudo apt install python3-requests python3-bs4 python3-schedule
   ```

2. **Ensure Ollama is Running**:

   ```bash
   ollama serve
   ollama pull llama3.1:8b
   ```

3. **Make Scripts Executable**:
   ```bash
   chmod +x daily_news_analyzer.py news_scheduler.py news_dashboard.py
   ```

## Usage

### Run Analysis Once

```bash
python3 daily_news_analyzer.py
```

### Start Scheduler

```bash
python3 news_scheduler.py
```

### View Dashboard

```bash
python3 news_dashboard.py
```

### Run Specific Commands

```bash
# Show system status
python3 news_dashboard.py --status

# Run analysis immediately
python3 news_dashboard.py --run

# Clean old data (30+ days)
python3 news_dashboard.py --clean 30
```

## Docker Deployment

### Build and Run

```bash
# Build the container
docker-compose build news-analyzer

# Start the service
docker-compose --profile news-analyzer up -d

# View logs
docker-compose logs -f news-analyzer
```

### Container Features

- **Ollama Integration**: Built-in Ollama service
- **Model Management**: Automatic model downloading
- **Health Checks**: Continuous monitoring
- **Persistent Storage**: Reports and database volumes

## Configuration

### Main Config (`news_analyzer_config.json`)

```json
{
  "analyzer_config": {
    "model_name": "llama3.1:8b",
    "max_articles_per_run": 10,
    "rate_limit_seconds": 2
  },
  "scheduling_config": {
    "morning_analysis": "08:00",
    "afternoon_analysis": "14:00",
    "evening_analysis": "20:00"
  }
}
```

### Database Schema

- **news_articles**: Article content, analysis, sentiment
- **daily_reports**: Generated daily summaries

## Scheduled Operations

### Daily Schedule

- **08:00 AM**: Morning news analysis
- **02:00 PM**: Afternoon update analysis
- **08:00 PM**: Evening summary analysis
- **Hourly**: Ollama health checks

### System Service (Optional)

```bash
# Install as systemd service
sudo cp racing-news-scheduler.service /etc/systemd/system/
sudo systemctl enable racing-news-scheduler
sudo systemctl start racing-news-scheduler
```

## Output Files

### Daily Reports

- **Location**: `reports/daily_news/`
- **Format**: `racing_news_report_YYYY-MM-DD.md`
- **Content**: Executive summary, key stories, market trends, sentiment overview

### Example Report Structure

```markdown
# Daily Racing News Report - 2025-08-13

## Executive Summary

[AI-generated summary of the day's news]

## Key Stories

1. [Story headline and analysis]
2. [Another key story]

## Market Trends

1. [Identified trend]
2. [Market insight]

## Sentiment Overview

[Overall market sentiment analysis]
```

### Database Files

- **news_analysis.db**: SQLite database with all data
- **news_analyzer.log**: Application logs
- **news_scheduler.log**: Scheduler logs

## Monitoring

### Dashboard Features

- **System Status**: Ollama service, database health
- **Recent Articles**: Last analyzed articles with sentiment
- **Sentiment Trends**: 7-day sentiment visualization
- **Report Summary**: Generated reports count

### Health Checks

- **Ollama API**: Availability and model access
- **Database**: Connection and query functionality
- **Recent Activity**: Last analysis timestamp

## Troubleshooting

### Common Issues

1. **Ollama Not Running**

   ```bash
   # Start Ollama service
   ollama serve

   # Check if models are available
   ollama list
   ```

2. **Database Issues**

   ```bash
   # Check database file
   ls -la news_analysis.db

   # View recent logs
   tail -f news_analyzer.log
   ```

3. **Network Issues**

   ```bash
   # Test Racing Post connectivity
   curl -I https://www.racingpost.com/news/

   # Check Ollama API
   curl http://localhost:11434/api/tags
   ```

### Log Locations

- **Application**: `news_analyzer.log`
- **Scheduler**: `news_scheduler.log`
- **System Service**: `/var/log/racing-news-scheduler.log`

## API Integration

### Ollama API Endpoints

- **Generate**: `POST /api/generate`
- **Models**: `GET /api/tags`
- **Health**: `GET /api/version`

### Model Configuration

```python
{
    "model": "llama3.1:8b",
    "options": {
        "temperature": 0.3,
        "top_p": 0.9
    }
}
```

## Performance

### Resource Usage

- **RAM**: ~2-4GB (including Ollama + model)
- **Storage**: ~50MB per month (articles + reports)
- **CPU**: Moderate during analysis (5-10 minutes per run)

### Optimization Tips

- **Rate Limiting**: 2-second delays between requests
- **Content Limits**: 5000 characters per article
- **Model Efficiency**: Llama 3.1 8B for speed/quality balance

## Security

### Data Protection

- **Local Storage**: All data stored locally
- **No External APIs**: Except for news scraping
- **Rate Limiting**: Respectful scraping practices

### Access Control

- **Database**: SQLite file permissions
- **Logs**: Local file system only
- **API**: Ollama local-only by default

## Future Enhancements

### Planned Features

- **Web Interface**: Real-time dashboard (port 8080)
- **Email Notifications**: Daily report delivery
- **Advanced Analytics**: Predictive insights
- **Multi-Source Support**: Additional news sources

### Model Upgrades

- **Model Rotation**: Automatic model updates
- **Performance Tuning**: Optimized prompts
- **Specialized Models**: Racing-specific fine-tuning

---

**Last Updated**: August 13, 2025  
**Version**: 1.0.0  
**Author**: Racing AI Team
