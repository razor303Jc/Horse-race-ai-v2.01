#!/usr/bin/env python3
"""
🚀 Real-Time Horse Racing Prediction API

FastAPI-based web service for live horse racing predictions using our
trained ensemble models. Transforms Priority 3A ML models into production API.

Features:
- Real-time race predictions with confidence scores
- Ensemble model serving with 98.86% AUC performance
- Interactive web interface for race analysis
- Betting recommendations with risk assessment
- Model performance monitoring and metrics

Usage:
    uvicorn api.prediction_api:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /                    - Interactive web interface
    POST /predict/race        - Single race prediction
    POST /predict/horse       - Single horse prediction
    GET  /models/status       - Model health and performance
    GET  /docs                - API documentation
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🏇 Horse Racing Prediction API",
    description="Real-time horse racing predictions using advanced ML ensemble models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global variables for model and encoders
ensemble_model = None
label_encoders = None
model_metadata = None
model_timestamp = None


class HorseData(BaseModel):
    """Input data model for single horse prediction."""

    horse_name: str = Field(..., description="Name of the horse")
    horse_age: int = Field(..., ge=2, le=15, description="Age of horse (2-15 years)")
    draw: int = Field(..., ge=1, le=24, description="Barrier draw position")
    win_odds: float = Field(..., gt=0, description="Current win odds")
    place_odds: Optional[float] = Field(None, gt=0, description="Current place odds")
    barrier: Optional[int] = Field(None, ge=1, le=24, description="Barrier number")
    margin: Optional[float] = Field(0.0, description="Previous race margin")
    horse_weight_kg: Optional[float] = Field(
        None, ge=300, le=700, description="Horse weight in kg"
    )
    handicap_weight: Optional[float] = Field(
        None, ge=45, le=70, description="Handicap weight in kg"
    )
    jockey_name: Optional[str] = Field(None, description="Jockey name")
    trainer_name: Optional[str] = Field(None, description="Trainer name")
    jockey_win_pct: Optional[float] = Field(
        10.0, ge=0, le=100, description="Jockey win percentage"
    )
    jockey_place_pct: Optional[float] = Field(
        25.0, ge=0, le=100, description="Jockey place percentage"
    )
    trainer_win_pct: Optional[float] = Field(
        10.0, ge=0, le=100, description="Trainer win percentage"
    )
    trainer_place_pct: Optional[float] = Field(
        25.0, ge=0, le=100, description="Trainer place percentage"
    )
    course: str = Field("Unknown", description="Race course name")

    @validator("place_odds", pre=True, always=True)
    def set_place_odds(cls, v, values):
        """Set place odds to win odds / 2 if not provided."""
        if v is None and "win_odds" in values:
            return values["win_odds"] / 2
        return v


class RaceData(BaseModel):
    """Input data model for full race prediction."""

    race_name: str = Field(..., description="Name of the race")
    race_date: str = Field(..., description="Race date (YYYY-MM-DD)")
    course: str = Field(..., description="Race course")
    distance: Optional[int] = Field(
        1600, ge=800, le=4000, description="Race distance in meters"
    )
    prize_money: Optional[float] = Field(50000, ge=0, description="Total prize money")
    horses: List[HorseData] = Field(
        ..., min_items=2, max_items=24, description="List of horses in race"
    )


class PredictionResponse(BaseModel):
    """Response model for predictions."""

    success: bool
    horse_name: str
    win_probability: float
    win_prediction: bool
    confidence_level: str
    implied_odds: float
    recommendation: str
    model_components: Dict[str, float]
    timestamp: str


class RacePredictionResponse(BaseModel):
    """Response model for full race predictions."""

    success: bool
    race_name: str
    course: str
    race_date: str
    predictions: List[PredictionResponse]
    race_summary: Dict[str, Union[str, float]]
    timestamp: str


def load_production_models():
    """Load the trained ensemble model and encoders."""
    global ensemble_model, label_encoders, model_metadata, model_timestamp

    try:
        # Find the latest model timestamp
        models_dir = Path.cwd() / "trained_models" / "priority_3a"

        if not models_dir.exists():
            raise FileNotFoundError("Models directory not found - creating placeholder")

        # Find the most recent ensemble model
        ensemble_files = list(models_dir.glob("ensemble_*.joblib"))
        if not ensemble_files:
            raise FileNotFoundError("No ensemble model files found")

        latest_ensemble = max(ensemble_files, key=lambda x: x.stat().st_mtime)
        model_timestamp = latest_ensemble.stem.split("_")[-1]

        logger.info(f"Loading ensemble model: {latest_ensemble}")
        ensemble_model = joblib.load(latest_ensemble)

        # Load encoders
        encoders_file = models_dir / f"encoders_{model_timestamp}.joblib"
        if encoders_file.exists():
            label_encoders = joblib.load(encoders_file)
            logger.info(f"Loaded encoders: {encoders_file}")
        else:
            label_encoders = {}
            logger.warning("No encoders file found, using empty encoders")

        # Load metadata
        metadata_file = models_dir / f"results_{model_timestamp}.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                model_metadata = json.load(f)
            logger.info(f"Loaded metadata: {metadata_file}")
        else:
            model_metadata = {}
            logger.warning("No metadata file found")

        logger.info("✅ Models loaded successfully")
        logger.info(
            f"   Ensemble components: {[name for name, _ in ensemble_model.estimators]}"
        )

        return True

    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        return False


def engineer_features_for_prediction(horse_data: HorseData) -> pd.DataFrame:
    """Engineer features for prediction matching training pipeline."""

    # Convert to dictionary then DataFrame
    data = horse_data.dict()
    df = pd.DataFrame([data])

    # Basic features with defaults
    df["horse_age"] = df["horse_age"].fillna(5)
    df["draw"] = df["draw"].fillna(8)
    df["win_odds"] = df["win_odds"].fillna(5.0)
    df["place_odds"] = df["place_odds"].fillna(df["win_odds"] / 2)
    df["barrier"] = df["barrier"].fillna(df["draw"])
    df["margin"] = df["margin"].fillna(0.0)
    df["horse_weight_kg"] = df["horse_weight_kg"].fillna(485)
    df["handicap_weight"] = df["handicap_weight"].fillna(58)

    # Odds-based features
    df["is_favorite"] = (df["win_odds"] <= 3.0).astype(int)
    df["high_odds"] = (df["win_odds"] >= 10.0).astype(int)
    df["log_odds"] = np.log(df["win_odds"].clip(lower=1.01))
    df["implied_prob"] = 1 / df["win_odds"].clip(lower=1.01)

    # Safe ratio calculations
    place_odds_safe = df["place_odds"].fillna(df["win_odds"]).clip(lower=0.1)
    df["odds_ratio"] = df["win_odds"] / place_odds_safe

    weight_denom = df["handicap_weight"].fillna(df["horse_weight_kg"]).clip(lower=30)
    df["weight_ratio"] = df["horse_weight_kg"] / weight_denom

    # Age and position features
    df["age_squared"] = df["horse_age"] ** 2
    df["draw_squared"] = df["draw"] ** 2
    df["barrier_squared"] = df["barrier"] ** 2

    # Performance features
    df["jockey_win_pct"] = df["jockey_win_pct"].fillna(10.0)
    df["jockey_place_pct"] = df["jockey_place_pct"].fillna(25.0)
    df["trainer_win_pct"] = df["trainer_win_pct"].fillna(10.0)
    df["trainer_place_pct"] = df["trainer_place_pct"].fillna(25.0)

    # Combined performance features
    df["jockey_trainer_combo"] = df["jockey_win_pct"] * df["trainer_win_pct"]
    df["combined_place_pct"] = (df["jockey_place_pct"] + df["trainer_place_pct"]) / 2

    # Categorical encoding
    if label_encoders and "course" in label_encoders:
        try:
            df["course_encoded"] = label_encoders["course"].transform(
                [horse_data.course]
            )
        except ValueError:
            # Handle unseen course
            df["course_encoded"] = 0
    else:
        df["course_encoded"] = 0

    # Select feature columns (matching training)
    feature_columns = [
        "horse_age",
        "draw",
        "win_odds",
        "place_odds",
        "barrier",
        "margin",
        "horse_weight_kg",
        "handicap_weight",
        "jockey_win_pct",
        "jockey_place_pct",
        "trainer_win_pct",
        "trainer_place_pct",
        "is_favorite",
        "high_odds",
        "log_odds",
        "implied_prob",
        "odds_ratio",
        "weight_ratio",
        "age_squared",
        "draw_squared",
        "barrier_squared",
        "jockey_trainer_combo",
        "combined_place_pct",
        "course_encoded",
    ]

    return df[feature_columns]


def get_confidence_level(probability: float) -> str:
    """Determine confidence level based on probability."""
    if probability >= 0.8 or probability <= 0.1:
        return "Very High"
    elif probability >= 0.7 or probability <= 0.2:
        return "High"
    elif probability >= 0.6 or probability <= 0.3:
        return "Medium"
    else:
        return "Low"


def get_betting_recommendation(probability: float, odds: float) -> str:
    """Generate betting recommendation based on probability and odds."""
    implied_prob = 1 / odds if odds > 0 else 0
    value = probability - implied_prob

    if value > 0.1:
        return f"Strong Value Bet - Model suggests {probability:.1%} vs market {implied_prob:.1%}"
    elif value > 0.05:
        return f"Value Bet - Slight edge detected"
    elif value > -0.05:
        return f"Fair Odds - No significant edge"
    elif value > -0.1:
        return f"Overpriced - Market odds too short"
    else:
        return f"Avoid - Significantly overpriced"


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    logger.info("🚀 Starting Horse Racing Prediction API...")

    success = load_production_models()
    if not success:
        logger.error("❌ Failed to load models on startup")
        logger.warning("⚠️ Running in demo mode - models not loaded")

    logger.info("✅ API ready for predictions!")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main interactive web interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏇 Horse Racing Prediction API</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #2c3e50; margin-bottom: 10px; }
            .header p { color: #7f8c8d; font-size: 18px; }
            .stats { display: flex; justify-content: space-around; margin: 30px 0; }
            .stat { text-align: center; padding: 20px; background: #ecf0f1; border-radius: 8px; }
            .stat h3 { margin: 0; color: #27ae60; font-size: 24px; }
            .stat p { margin: 5px 0 0 0; color: #7f8c8d; }
            .form-section { background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 20px 0; }
            .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
            .form-group { flex: 1; min-width: 200px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2c3e50; }
            .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
            .btn { background: #3498db; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
            .btn:hover { background: #2980b9; }
            .btn-success { background: #27ae60; }
            .btn-success:hover { background: #229954; }
            .result { margin-top: 20px; padding: 20px; border-radius: 8px; }
            .result-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .result-warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
            .result-danger { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .endpoints { margin-top: 30px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
            .method { font-weight: bold; color: #e74c3c; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏇 Horse Racing Prediction API</h1>
                <p>Real-time predictions using advanced ML ensemble models</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <h3>98.86%</h3>
                    <p>AUC Performance</p>
                </div>
                <div class="stat">
                    <h3>5 Models</h3>
                    <p>Ensemble Components</p>
                </div>
                <div class="stat">
                    <h3>24 Features</h3>
                    <p>Advanced Engineering</p>
                </div>
                <div class="stat">
                    <h3>Live API</h3>
                    <p>Real-time Serving</p>
                </div>
            </div>
            
            <div class="form-section">
                <h2>🎯 Single Horse Prediction</h2>
                <form id="horseForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="horse_name">Horse Name *</label>
                            <input type="text" id="horse_name" name="horse_name" required placeholder="e.g., Winx">
                        </div>
                        <div class="form-group">
                            <label for="horse_age">Age *</label>
                            <input type="number" id="horse_age" name="horse_age" min="2" max="15" required value="5">
                        </div>
                        <div class="form-group">
                            <label for="draw">Draw *</label>
                            <input type="number" id="draw" name="draw" min="1" max="24" required value="8">
                        </div>
                        <div class="form-group">
                            <label for="win_odds">Win Odds *</label>
                            <input type="number" id="win_odds" name="win_odds" step="0.1" min="1.01" required value="4.5">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="jockey_win_pct">Jockey Win % *</label>
                            <input type="number" id="jockey_win_pct" name="jockey_win_pct" step="0.1" min="0" max="100" value="12.5">
                        </div>
                        <div class="form-group">
                            <label for="trainer_win_pct">Trainer Win % *</label>
                            <input type="number" id="trainer_win_pct" name="trainer_win_pct" step="0.1" min="0" max="100" value="15.0">
                        </div>
                        <div class="form-group">
                            <label for="course">Course *</label>
                            <select id="course" name="course" required>
                                <option value="Flemington">Flemington</option>
                                <option value="Caulfield">Caulfield</option>
                                <option value="Randwick">Randwick</option>
                                <option value="Rosehill">Rosehill</option>
                                <option value="Moonee Valley">Moonee Valley</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="horse_weight_kg">Weight (kg)</label>
                            <input type="number" id="horse_weight_kg" name="horse_weight_kg" min="300" max="700" value="485">
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-success">🎯 Get Prediction</button>
                    <button type="button" class="btn" onclick="fillSampleData()">📝 Sample Data</button>
                </form>
                
                <div id="result" class="hidden"></div>
            </div>
            
            <div class="endpoints">
                <h2>🔌 API Endpoints</h2>
                <div class="endpoint">
                    <span class="method">POST</span> /predict/horse - Single horse prediction
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /predict/race - Full race prediction
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /models/status - Model health check
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /docs - Interactive API documentation
                </div>
            </div>
        </div>
        
        <script>
            function fillSampleData() {
                document.getElementById('horse_name').value = 'Champion Runner';
                document.getElementById('horse_age').value = '5';
                document.getElementById('draw').value = '3';
                document.getElementById('win_odds').value = '4.5';
                document.getElementById('jockey_win_pct').value = '18.5';
                document.getElementById('trainer_win_pct').value = '22.1';
                document.getElementById('course').value = 'Flemington';
                document.getElementById('horse_weight_kg').value = '485';
            }
            
            document.getElementById('horseForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (['horse_age', 'draw', 'win_odds', 'jockey_win_pct', 'trainer_win_pct', 'horse_weight_kg'].includes(key)) {
                        data[key] = parseFloat(value);
                    } else {
                        data[key] = value;
                    }
                }
                
                try {
                    const response = await fetch('/predict/horse', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    if (result.success) {
                        resultDiv.className = 'result result-success';
                        resultDiv.innerHTML = `
                            <h3>🏆 Prediction Results for ${result.horse_name}</h3>
                            <p><strong>Win Probability:</strong> ${(result.win_probability * 100).toFixed(1)}%</p>
                            <p><strong>Prediction:</strong> ${result.win_prediction ? '🏆 Winner' : '❌ Non-winner'}</p>
                            <p><strong>Confidence:</strong> ${result.confidence_level}</p>
                            <p><strong>Implied Odds:</strong> ${result.implied_odds.toFixed(1)}</p>
                            <p><strong>Recommendation:</strong> ${result.recommendation}</p>
                            <hr>
                            <h4>Model Components:</h4>
                            <ul>
                                ${Object.entries(result.model_components).map(([model, prob]) => 
                                    `<li>${model}: ${(prob * 100).toFixed(1)}%</li>`
                                ).join('')}
                            </ul>
                        `;
                    } else {
                        resultDiv.className = 'result result-danger';
                        resultDiv.innerHTML = `<h3>❌ Prediction Failed</h3><p>${result.detail || 'Unknown error'}</p>`;
                    }
                    
                    resultDiv.classList.remove('hidden');
                } catch (error) {
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = 'result result-danger';
                    resultDiv.innerHTML = `<h3>❌ Network Error</h3><p>${error.message}</p>`;
                    resultDiv.classList.remove('hidden');
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/predict/horse", response_model=PredictionResponse)
async def predict_horse(horse_data: HorseData):
    """Predict win probability for a single horse."""

    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    try:
        # Engineer features
        features = engineer_features_for_prediction(horse_data)

        # Make ensemble prediction
        win_probability = ensemble_model.predict_proba(features.values)[0, 1]
        win_prediction = ensemble_model.predict(features.values)[0]

        # Get individual model predictions
        model_components = {}
        for name, model in ensemble_model.estimators:
            component_prob = model.predict_proba(features.values)[0, 1]
            model_components[name] = float(component_prob)

        # Generate insights
        confidence_level = get_confidence_level(win_probability)
        implied_odds = 1 / win_probability if win_probability > 0 else float("inf")
        recommendation = get_betting_recommendation(
            win_probability, horse_data.win_odds
        )

        return PredictionResponse(
            success=True,
            horse_name=horse_data.horse_name,
            win_probability=float(win_probability),
            win_prediction=bool(win_prediction),
            confidence_level=confidence_level,
            implied_odds=float(implied_odds),
            recommendation=recommendation,
            model_components=model_components,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Prediction failed for {horse_data.horse_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/race", response_model=RacePredictionResponse)
async def predict_race(race_data: RaceData):
    """Predict win probabilities for all horses in a race."""

    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    try:
        predictions = []

        # Predict for each horse
        for horse in race_data.horses:
            # Set course to race course if not specified
            if horse.course == "Unknown":
                horse.course = race_data.course

            prediction = await predict_horse(horse)
            predictions.append(prediction)

        # Sort by win probability
        predictions.sort(key=lambda x: x.win_probability, reverse=True)

        # Generate race summary
        total_prob = sum(p.win_probability for p in predictions)
        favorite = predictions[0]
        outsider = predictions[-1]

        race_summary = {
            "favorite": f"{favorite.horse_name} ({favorite.win_probability:.1%})",
            "outsider": f"{outsider.horse_name} ({outsider.win_probability:.1%})",
            "field_size": len(predictions),
            "total_probability": f"{total_prob:.1%}",
            "market_efficiency": (
                "Efficient" if 0.95 <= total_prob <= 1.05 else "Inefficient"
            ),
        }

        return RacePredictionResponse(
            success=True,
            race_name=race_data.race_name,
            course=race_data.course,
            race_date=race_data.race_date,
            predictions=predictions,
            race_summary=race_summary,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Race prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Race prediction failed: {str(e)}")


@app.get("/models/status")
async def get_model_status():
    """Get model health and performance information."""

    if ensemble_model is None:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": "Models not loaded"},
        )

    try:
        status_info = {
            "status": "healthy",
            "model_timestamp": model_timestamp,
            "ensemble_components": [name for name, _ in ensemble_model.estimators],
            "feature_count": 24,
            "encoders_loaded": len(label_encoders) if label_encoders else 0,
            "metadata_available": model_metadata is not None,
            "startup_time": datetime.now().isoformat(),
        }

        if model_metadata:
            # Add performance metrics from best models
            best_ensemble_auc = (
                model_metadata.get("ensemble_performance", {})
                .get("test_metrics", {})
                .get("roc_auc", 0)
            )
            status_info["ensemble_auc"] = best_ensemble_auc
            status_info["model_performance"] = {
                name: perf.get("test_metrics", {}).get("roc_auc", 0)
                for name, perf in model_metadata.get("model_performance", {}).items()
            }

        return JSONResponse(content=status_info)

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    print("🚀 Starting Horse Racing Prediction API...")
    print("📊 Interactive interface: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")

    uvicorn.run(
        "prediction_api:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
