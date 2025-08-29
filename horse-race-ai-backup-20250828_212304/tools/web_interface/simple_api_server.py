#!/usr/bin/env python3
"""
Simple API Server for Frontend-Backend Integration Testing
=========================================================

A simplified API server that provides the required endpoints for testing
frontend-backend integration without complex database setup.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Any
import uvicorn
from pathlib import Path

app = FastAPI(title="Horse Racing AI API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock data for testing
def generate_mock_race_data():
    """Generate mock race data for testing"""
    horses = []
    horse_names = [
        "Thunder Bolt",
        "Lightning Strike",
        "Fast Forward",
        "Royal Runner",
        "Speed Demon",
        "Wind Walker",
        "Storm Chaser",
        "Golden Arrow",
    ]
    jockeys = [
        "J. Smith",
        "M. Johnson",
        "A. Brown",
        "S. Davis",
        "R. Wilson",
        "C. Taylor",
        "L. Anderson",
        "D. Thomas",
    ]
    trainers = [
        "John Trainer",
        "Mary Coach",
        "Bob Handler",
        "Sue Mentor",
        "Tom Guide",
        "Lisa Leader",
        "Paul Prep",
        "Jane Director",
    ]

    for i in range(8):
        horse = {
            "horse_name": horse_names[i] if i < len(horse_names) else f"Horse {i+1}",
            "jockey_name": random.choice(jockeys),
            "trainer_name": random.choice(trainers),
            "age": random.randint(3, 8),
            "weight_kg": random.randint(50, 65),
            "win_odds": round(random.uniform(2.0, 20.0), 1),
            "win_probability": round(random.uniform(5, 40), 1),
            "career_record": f"{random.randint(0, 10)}/{random.randint(15, 50)}",
            "recent_form": "".join(
                random.choices(["1", "2", "3", "4", "5", "6", "F"], k=5)
            ),
            "position": i + 1,
            "silk_colors": random.choice(
                ["Red/Blue", "Green/Yellow", "Purple/White", "Orange/Black"]
            ),
        }
        horses.append(horse)

    return horses


@app.get("/api/daily_races")
async def get_daily_races():
    """Get daily races data"""
    return {
        "total_races": 45,
        "total_meetings": 8,
        "daily_stats": {
            "total_prize_money": 2500000,
            "group_races": 3,
            "average_field_size": 12.5,
            "handicaps": 18,
            "maiden_races": 8,
            "chase_hurdle_races": 6,
            "quality_distribution": {
                "Group 1": 1,
                "Group 2": 2,
                "Listed": 4,
                "Class 1": 8,
                "Class 2": 12,
                "Class 3": 18,
            },
        },
        "races": [
            {
                "race_id": f"race_{i}",
                "meeting": random.choice(
                    ["Ascot", "Newmarket", "York", "Cheltenham", "Aintree"]
                ),
                "race_number": i + 1,
                "time": f"{13 + i//2}:{30 if i%2 else 0:02d}",
                "race_name": f"The {random.choice(['Sprint', 'Classic', 'Handicap', 'Stakes'])} Race",
                "class": f"Class {random.randint(1, 4)}",
                "distance": f"{random.choice(['5f', '6f', '7f', '1m', '1m2f', '1m4f', '2m'])}",
                "distance_meters": random.randint(1000, 3200),
                "going": random.choice(
                    ["Good", "Good to Firm", "Firm", "Soft", "Heavy"]
                ),
                "prize_money": random.randint(10000, 100000),
                "field_size": random.randint(8, 16),
                "age_restriction": random.choice(["3yo+", "4yo+", "2yo", "3yo"]),
                "race_type": random.choice(
                    ["Flat", "National Hunt", "Hurdle", "Chase"]
                ),
                "surface": random.choice(["Turf", "All Weather"]),
                "quality_rating": f"{random.randint(70, 110)}",
                "predicted_competitiveness": round(random.uniform(0.6, 0.95), 2),
                "betting_volume": random.randint(50000, 500000),
                "favorite": {
                    "horse": random.choice(
                        ["Thunder Bolt", "Lightning Strike", "Fast Forward"]
                    ),
                    "odds": round(random.uniform(2.0, 5.0), 1),
                    "probability": round(random.uniform(20, 40), 1),
                },
                "race_insights": [
                    "Strong field with competitive betting",
                    "Weather conditions favor front runners",
                    "Track bias towards inside rail",
                ],
            }
            for i in range(10)
        ],
    }


@app.get("/api/real_race_cards")
async def get_real_race_cards():
    """Get real race cards data"""
    races = []
    for i in range(5):
        race = {"race_id": f"card_race_{i}", "horses": generate_mock_race_data()}
        races.append(race)

    return {
        "total_races": 5,
        "total_horses": 40,
        "data_source": "Mock API",
        "timestamp": datetime.now().isoformat(),
        "races": races,
    }


@app.get("/api/betting/recommendations")
async def get_betting_recommendations():
    """Get betting recommendations"""
    recommendations = []
    horse_names = [
        "Thunder Bolt",
        "Lightning Strike",
        "Fast Forward",
        "Royal Runner",
        "Speed Demon",
    ]
    venues = ["Ascot", "Newmarket", "York", "Cheltenham", "Aintree"]

    for i in range(3):
        rec = {
            "horse_name": horse_names[i],
            "race_time": f"{14 + i}:30",
            "venue": random.choice(venues),
            "confidence": round(random.uniform(0.70, 0.95), 2),
            "current_odds": round(random.uniform(3.0, 12.0), 1),
            "value": round(random.uniform(0.02, 0.15), 3),
            "stake_recommendation": round(random.uniform(5.0, 25.0), 2),
            "recommended_action": random.choice(["BET", "WATCH", "STRONG BET"]),
            "reasoning": "Strong form and favorable conditions",
        }
        recommendations.append(rec)

    return recommendations


@app.get("/api/stage8/performance")
async def get_stage8_performance():
    """Get Stage 8 performance data"""
    return {
        "account_balance": 1250.75,
        "daily_pnl": 45.30,
        "win_rate": 73.2,
        "roi": 12.5,
        "total_bets": 156,
        "active_bets": 3,
        "recent_performance": [
            {"date": "Mon", "pnl": 25.50},
            {"date": "Tue", "pnl": 42.30},
            {"date": "Wed", "pnl": -15.20},
            {"date": "Thu", "pnl": 67.80},
            {"date": "Fri", "pnl": 31.40},
            {"date": "Sat", "pnl": 78.90},
            {"date": "Sun", "pnl": 45.30},
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
    }


# Serve static files for the React app
web_build_path = Path(__file__).parent.parent.parent / "src" / "web" / "dist"
if web_build_path.exists():
    app.mount(
        "/", StaticFiles(directory=str(web_build_path), html=True), name="frontend"
    )

if __name__ == "__main__":
    print("🚀 Starting Simple API Server for Frontend-Backend Integration")
    print("📊 Mock data endpoints available:")
    print("   • GET /api/daily_races")
    print("   • GET /api/real_race_cards")
    print("   • GET /api/betting/recommendations")
    print("   • GET /api/stage8/performance")
    print("   • GET /health")
    print("\n🌐 Server starting on http://localhost:8000")
    print("📱 Frontend available at http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False)
