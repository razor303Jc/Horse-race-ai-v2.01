# 📡 API Reference

The Horse Racing AI v2.0 system provides a comprehensive REST API for programmatic access to all features and data.

## 🔗 Base URL

When running locally:

```
http://localhost:8000/api
```

## 🔐 Authentication

Currently, the API uses basic authentication. In production environments, consider implementing JWT tokens or API keys.

## 📊 Core Endpoints

### Health Check

Check system health and status.

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T17:03:11.741143"
}
```

### Data Statistics

Get comprehensive system statistics and performance metrics.

```http
GET /api/data-stats
```

**Response:**

```json
{
  "total_races": 8900,
  "prediction_accuracy": 61.9,
  "place_accuracy": 76.6,
  "confidence_score": 72.4,
  "last_updated": "2025-08-04T17:00:00Z"
}
```

### Race Cards

Retrieve race cards with AI predictions and analysis.

```http
GET /api/race-cards
GET /api/race-cards?date=2025-08-04
GET /api/race-cards?track=ascot
```

**Parameters:**

- `date` (optional): Filter by specific date (YYYY-MM-DD)
- `track` (optional): Filter by track name
- `limit` (optional): Limit number of results (default: 50)

**Response:**

```json
{
  "races": [
    {
      "race_id": "ASC_R1_20250804",
      "track": "Ascot",
      "race_time": "14:30",
      "distance": "1200m",
      "horses": [
        {
          "horse_name": "Thunder Strike",
          "jockey": "J. Smith",
          "barrier": 3,
          "weight": 58.5,
          "prediction": {
            "win_probability": 0.245,
            "place_probability": 0.678,
            "confidence": 0.832,
            "ai_rating": 8.4
          }
        }
      ]
    }
  ]
}
```

### Horse Analysis

Get detailed analysis for a specific horse.

```http
GET /api/horses/{horse_id}
GET /api/horses/{horse_id}/performance
```

**Response:**

```json
{
  "horse_id": "THUNDER_STRIKE_001",
  "name": "Thunder Strike",
  "age": 4,
  "trainer": "M. Johnson",
  "recent_form": [
    {
      "date": "2025-07-28",
      "position": 2,
      "track": "Flemington",
      "distance": "1400m"
    }
  ],
  "statistics": {
    "career_wins": 8,
    "career_starts": 22,
    "win_percentage": 36.4,
    "place_percentage": 63.6
  }
}
```

### Predictions

Get AI predictions for upcoming races.

```http
GET /api/predictions
GET /api/predictions?race_id={race_id}
```

**Response:**

```json
{
  "predictions": [
    {
      "race_id": "ASC_R1_20250804",
      "predictions": [
        {
          "horse_name": "Thunder Strike",
          "win_probability": 0.245,
          "place_probability": 0.678,
          "confidence": 0.832,
          "recommended_bet": "place",
          "value_rating": 7.2
        }
      ],
      "model_info": {
        "model_version": "2.0",
        "accuracy": 61.9,
        "confidence_threshold": 0.7
      }
    }
  ]
}
```

### 20/80 Betting Strategy (NEW!)

Get 20/80 betting strategy recommendations for horses.

```http
GET /api/betting/twenty-eighty
GET /api/betting/twenty-eighty?stake=100
POST /api/betting/twenty-eighty
```

**POST Request Body:**

```json
{
  "horses": [
    {
      "horse_name": "Thunder Strike",
      "win_odds": 4.2,
      "place_odds": 1.6,
      "win_probability": 0.28,
      "place_probability": 0.72,
      "confidence": 0.85
    }
  ],
  "total_stake": 100,
  "daily_budget": 1500
}
```

**Response:**

```json
{
  "strategy_type": "20_80",
  "selections": [
    {
      "horse_name": "Thunder Strike",
      "total_stake": 100.0,
      "win_stake": 20.0,
      "place_stake": 80.0,
      "win_odds": 4.2,
      "place_odds": 1.6,
      "potential_win_return": 84.0,
      "potential_place_return": 128.0,
      "expected_value": 13.33,
      "risk_rating": "LOW",
      "scenarios": {
        "win": { "return": 84.0, "profit": -16.0 },
        "place_only": { "return": 128.0, "profit": 28.0 },
        "fail": { "return": 0.0, "profit": -100.0 }
      }
    }
  ],
  "top_three_daily": [
    {
      "rank": 1,
      "horse_name": "Midnight Express",
      "race_id": "RAN_R5_20250804",
      "expected_value": 106.84,
      "selection_value": 68.42
    }
  ],
  "portfolio_summary": {
    "total_stakes": 300.0,
    "combined_expected_value": 377.79,
    "expected_roi": 25.2,
    "risk_distribution": {
      "low": 2,
      "medium": 1,
      "high": 0
    }
  }
}
```

**Query Parameters:**

- `stake` (optional): Default stake amount per horse
- `daily_budget` (optional): Total daily betting budget
- `confidence_threshold` (optional): Minimum confidence level (default: 0.6)
- `max_selections` (optional): Maximum number of selections (default: 3)

## 🔧 WebSocket API

For real-time updates, connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Real-time update:", data);
};
```

### Event Types

- `race_result`: Race has finished with results
- `odds_update`: Betting odds have changed
- `prediction_update`: AI prediction has been updated
- `system_alert`: System status or health alert

## 📝 Data Export

Export data in various formats:

```http
GET /api/export/races?format=csv&date_from=2025-08-01&date_to=2025-08-04
GET /api/export/predictions?format=json&race_id={race_id}
```

**Supported Formats:**

- `json` (default)
- `csv`
- `excel`

## ⚠️ Rate Limiting

API requests are limited to:

- 100 requests per minute for general endpoints
- 10 requests per minute for export endpoints
- Unlimited for WebSocket connections

## 🚨 Error Handling

All API endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication required)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

**Error Response Format:**

```json
{
  "error": {
    "code": 400,
    "message": "Invalid date format",
    "details": "Date must be in YYYY-MM-DD format"
  }
}
```

## 📱 SDK and Libraries

Official SDKs are available for:

- **Python**: `pip install horse-racing-ai-sdk`
- **JavaScript/Node.js**: `npm install horse-racing-ai`
- **R**: `install.packages("horseracingai")`

**Python Example:**

```python
from horse_racing_ai import Client

client = Client(base_url="http://localhost:8000")
races = client.get_race_cards(date="2025-08-04")
predictions = client.get_predictions(race_id="ASC_R1_20250804")
```

## 🔗 Integration Examples

### Betting Bot Integration

```python
import requests
import time

def monitor_races():
    while True:
        response = requests.get("http://localhost:8000/api/predictions")
        predictions = response.json()

        for race in predictions['predictions']:
            for horse in race['predictions']:
                if horse['confidence'] > 0.8 and horse['value_rating'] > 7.0:
                    print(f"High confidence bet: {horse['horse_name']}")

        time.sleep(300)  # Check every 5 minutes
```

### Data Analysis Integration

```python
import pandas as pd

# Get historical data
races_df = pd.read_json("http://localhost:8000/api/export/races?format=json&date_from=2025-01-01")

# Analyze performance
accuracy_by_track = races_df.groupby('track')['prediction_accuracy'].mean()
print(accuracy_by_track)
```

---

**Need more endpoints?** Check the [OpenAPI specification](http://localhost:8000/docs) when the system is running, or contact the development team for custom integrations.
