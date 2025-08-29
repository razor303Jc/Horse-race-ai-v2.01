#!/usr/bin/env python3
"""
🚀 Advanced ML Model Management API

FastAPI endpoints for the Advanced AI & ML Features:
- Model lifecycle management (CRUD)
- Performance monitoring and analytics
- A/B testing framework
- Premium model marketplace
- Live prediction updates
- Hyperparameter optimization

Connects to PostgreSQL database on port 5434 as configured in docker-compose.clean.yml
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from uuid import uuid4

import asyncpg
import numpy as np
import pandas as pd
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    BackgroundTasks,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import redis
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Float,
    Integer,
    DateTime,
    Boolean,
    JSON,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database configuration from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://horse_racing:secure_password_123@postgres:5432/cards_horse_racing_db",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379/0")

# Initialize FastAPI app for ML management
ml_app = FastAPI(
    title="🤖 Advanced ML Model Management API",
    description="Comprehensive ML pipeline management and optimization",
    version="2.0.0",
    docs_url="/ml/docs",
    redoc_url="/ml/redoc",
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup for caching and real-time updates
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# ============================================================================
# DATABASE MODELS
# ============================================================================


class MLModelDB(Base):
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # win_predictor, place_predictor, etc.
    status = Column(String(20), default="inactive")
    version = Column(String(20), nullable=False)
    description = Column(Text)
    tier = Column(String(20), default="free")
    features = Column(JSON)
    hyperparameters = Column(JSON)
    training_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trained = Column(DateTime)
    training_duration_hours = Column(Float)


class ModelPerformanceDB(Base):
    __tablename__ = "model_performance"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    model_id = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    sharpe_ratio = Column(Float)
    roi = Column(Float)
    win_rate = Column(Float)
    total_predictions = Column(Integer)
    correct_predictions = Column(Integer)
    profit_loss = Column(Float)
    max_drawdown = Column(Float)
    volatility = Column(Float)


class ABTestDB(Base):
    __tablename__ = "ab_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    model_a_id = Column(String, nullable=False)
    model_b_id = Column(String, nullable=False)
    traffic_split = Column(Float, default=0.5)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default="scheduled")
    success_metric = Column(String(50))
    minimum_sample_size = Column(Integer)
    confidence_level = Column(Float)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class PremiumModelDB(Base):
    __tablename__ = "premium_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    vendor = Column(String(255))
    tier = Column(String(20))
    price_per_prediction = Column(Float)
    monthly_subscription = Column(Float)
    performance_guarantee = Column(JSON)
    specializations = Column(JSON)
    track_compatibility = Column(JSON)
    weather_optimized = Column(Boolean, default=False)
    live_updates = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class MLModelConfig(BaseModel):
    id: Optional[str] = None
    name: str
    type: str = Field(
        ..., regex="^(win_predictor|place_predictor|odds_predictor|ensemble)$"
    )
    status: str = Field(default="inactive", regex="^(active|training|inactive|error)$")
    version: str
    description: str
    tier: str = Field(default="free", regex="^(free|premium|professional)$")
    features: List[str] = []
    hyperparameters: Dict[str, Any] = {}
    training_config: Dict[str, Any] = {}


class ModelPerformanceMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    sharpe_ratio: float
    roi: float
    win_rate: float
    total_predictions: int
    correct_predictions: int
    profit_loss: float
    max_drawdown: float
    volatility: float
    last_updated: datetime


class ABTestConfig(BaseModel):
    name: str
    model_a_id: str
    model_b_id: str
    traffic_split: float = Field(default=0.5, ge=0.1, le=0.9)
    duration_days: int = Field(..., ge=1, le=90)
    success_metric: str = Field(..., regex="^(accuracy|roi|sharpe_ratio)$")
    minimum_sample_size: int = Field(..., ge=100)
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99)


class PremiumModelListing(BaseModel):
    id: str
    name: str
    description: str
    vendor: str
    tier: str = Field(..., regex="^(premium|professional)$")
    price_per_prediction: float
    monthly_subscription: float
    performance_guarantee: ModelPerformanceMetrics
    specializations: List[str]
    track_compatibility: List[str]
    weather_optimized: bool
    live_updates: bool


class TrainingRequest(BaseModel):
    force_retrain: bool = False
    use_latest_data: bool = True
    notification_email: Optional[str] = None


class OptimizationRequest(BaseModel):
    optimization_method: str = Field(
        ..., regex="^(grid_search|random_search|bayesian)$"
    )
    parameter_space: Dict[str, Any]
    max_trials: int = Field(..., ge=10, le=1000)
    timeout_hours: int = Field(..., ge=1, le=48)
    objective_metric: str = Field(..., regex="^(accuracy|f1_score|roi)$")


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ML MODEL MANAGEMENT ENDPOINTS
# ============================================================================


@ml_app.get("/models", response_model=List[MLModelConfig])
async def get_models(
    status: Optional[str] = None,
    type: Optional[str] = None,
    tier: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get all ML models with optional filtering"""
    try:
        query = db.query(MLModelDB)

        if status:
            query = query.filter(MLModelDB.status == status)
        if type:
            query = query.filter(MLModelDB.type == type)
        if tier:
            query = query.filter(MLModelDB.tier == tier)
        if active_only:
            query = query.filter(MLModelDB.status == "active")

        models = query.all()

        return [
            MLModelConfig(
                id=model.id,
                name=model.name,
                type=model.type,
                status=model.status,
                version=model.version,
                description=model.description,
                tier=model.tier,
                features=model.features or [],
                hyperparameters=model.hyperparameters or {},
                training_config=model.training_config or {},
            )
            for model in models
        ]
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_app.get("/models/{model_id}", response_model=MLModelConfig)
async def get_model(model_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific model"""
    try:
        model = db.query(MLModelDB).filter(MLModelDB.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        return MLModelConfig(
            id=model.id,
            name=model.name,
            type=model.type,
            status=model.status,
            version=model.version,
            description=model.description,
            tier=model.tier,
            features=model.features or [],
            hyperparameters=model.hyperparameters or {},
            training_config=model.training_config or {},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_app.post("/models", response_model=MLModelConfig)
async def create_model(model_config: MLModelConfig, db: Session = Depends(get_db)):
    """Create a new ML model"""
    try:
        # Generate ID if not provided
        if not model_config.id:
            model_config.id = str(uuid4())

        # Check if model with same name already exists
        existing = (
            db.query(MLModelDB).filter(MLModelDB.name == model_config.name).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Model with this name already exists"
            )

        # Create new model record
        db_model = MLModelDB(
            id=model_config.id,
            name=model_config.name,
            type=model_config.type,
            status=model_config.status,
            version=model_config.version,
            description=model_config.description,
            tier=model_config.tier,
            features=model_config.features,
            hyperparameters=model_config.hyperparameters,
            training_config=model_config.training_config,
        )

        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        logger.info(f"Created new model: {model_config.name} ({model_config.id})")
        return model_config

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating model: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@ml_app.patch("/models/{model_id}", response_model=MLModelConfig)
async def update_model(
    model_id: str, updates: Dict[str, Any], db: Session = Depends(get_db)
):
    """Update an existing model configuration"""
    try:
        model = db.query(MLModelDB).filter(MLModelDB.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Update allowed fields
        allowed_fields = [
            "name",
            "status",
            "description",
            "tier",
            "features",
            "hyperparameters",
            "training_config",
        ]
        for field, value in updates.items():
            if field in allowed_fields and hasattr(model, field):
                setattr(model, field, value)

        model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(model)

        return MLModelConfig(
            id=model.id,
            name=model.name,
            type=model.type,
            status=model.status,
            version=model.version,
            description=model.description,
            tier=model.tier,
            features=model.features or [],
            hyperparameters=model.hyperparameters or {},
            training_config=model.training_config or {},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model {model_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@ml_app.delete("/models/{model_id}")
async def delete_model(model_id: str, db: Session = Depends(get_db)):
    """Delete a model"""
    try:
        model = db.query(MLModelDB).filter(MLModelDB.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Check if model is being used in active A/B tests
        active_tests = (
            db.query(ABTestDB)
            .filter(
                (ABTestDB.model_a_id == model_id) | (ABTestDB.model_b_id == model_id),
                ABTestDB.status == "running",
            )
            .first()
        )

        if active_tests:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete model that is part of active A/B tests",
            )

        db.delete(model)
        db.commit()

        logger.info(f"Deleted model: {model.name} ({model_id})")
        return {"message": "Model deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model {model_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRAINING ENDPOINTS
# ============================================================================


@ml_app.post("/models/{model_id}/train")
async def start_training(
    model_id: str,
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Start training a model"""
    try:
        model = db.query(MLModelDB).filter(MLModelDB.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        if model.status == "training":
            raise HTTPException(status_code=400, detail="Model is already training")

        # Update model status
        model.status = "training"
        model.updated_at = datetime.utcnow()
        db.commit()

        # Generate task ID
        task_id = str(uuid4())

        # Store training task in Redis
        redis_client.setex(
            f"training_task:{task_id}",
            3600 * 24,  # 24 hours
            json.dumps(
                {
                    "model_id": model_id,
                    "status": "training",
                    "progress": 0,
                    "start_time": datetime.utcnow().isoformat(),
                    "config": request.dict(),
                }
            ),
        )

        # Start training in background
        background_tasks.add_task(run_model_training, model_id, task_id, request)

        return {"task_id": task_id, "estimated_duration": 3.5}  # hours

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training for model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_model_training(model_id: str, task_id: str, config: TrainingRequest):
    """Background task for model training"""
    try:
        logger.info(f"Starting training for model {model_id} (task: {task_id})")

        # Simulate training process
        for epoch in range(1, 101):
            await asyncio.sleep(0.1)  # Simulate training time

            # Update progress in Redis
            progress_data = {
                "status": "training",
                "progress": epoch,
                "current_epoch": epoch,
                "total_epochs": 100,
                "current_loss": 0.5 - (epoch * 0.003),
                "best_accuracy": 0.6 + (epoch * 0.002),
                "estimated_time_remaining": (100 - epoch) * 2,  # minutes
                "logs": [f"Epoch {epoch}/100 - loss: {0.5 - (epoch * 0.003):.4f}"],
            }

            redis_client.setex(
                f"training_task:{task_id}",
                3600 * 24,
                json.dumps(progress_data, default=str),
            )

        # Update model status on completion
        db = SessionLocal()
        try:
            model = db.query(MLModelDB).filter(MLModelDB.id == model_id).first()
            if model:
                model.status = "active"
                model.last_trained = datetime.utcnow()
                model.training_duration_hours = 3.5
                model.version = f"{model.version.split('.')[0]}.{int(model.version.split('.')[1]) + 1}.0"
                db.commit()

            # Mark training as completed
            completion_data = {
                "status": "completed",
                "progress": 100,
                "final_accuracy": 0.8,
                "completion_time": datetime.utcnow().isoformat(),
            }

            redis_client.setex(
                f"training_task:{task_id}",
                3600 * 24,
                json.dumps(completion_data, default=str),
            )

        finally:
            db.close()

        logger.info(f"Training completed for model {model_id}")

    except Exception as e:
        logger.error(f"Training failed for model {model_id}: {e}")
        # Mark as failed in Redis
        redis_client.setex(
            f"training_task:{task_id}",
            3600 * 24,
            json.dumps(
                {
                    "status": "failed",
                    "error": str(e),
                    "completion_time": datetime.utcnow().isoformat(),
                },
                default=str,
            ),
        )


@ml_app.get("/models/{model_id}/training-status")
async def get_training_status(model_id: str, db: Session = Depends(get_db)):
    """Get training status and progress"""
    try:
        # Find active training task for this model
        task_keys = redis_client.keys(f"training_task:*")
        task_data = None

        for key in task_keys:
            data = redis_client.get(key)
            if data:
                task_info = json.loads(data)
                if task_info.get("model_id") == model_id:
                    task_data = task_info
                    break

        if not task_data:
            raise HTTPException(
                status_code=404, detail="No training task found for this model"
            )

        return {
            "status": task_data.get("status", "unknown"),
            "progress": task_data.get("progress", 0),
            "current_epoch": task_data.get("current_epoch", 0),
            "total_epochs": task_data.get("total_epochs", 100),
            "current_loss": task_data.get("current_loss", 0),
            "best_accuracy": task_data.get("best_accuracy", 0),
            "estimated_time_remaining": task_data.get("estimated_time_remaining", 0),
            "logs": task_data.get("logs", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training status for model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET FOR LIVE UPDATES
# ============================================================================


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection was closed
                self.disconnect(connection)


manager = ConnectionManager()


@ml_app.websocket("/live-predictions/{race_id}/ws")
async def websocket_endpoint(websocket: WebSocket, race_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Send live prediction updates
            predictions = {
                "race_id": race_id,
                "timestamp": datetime.utcnow().isoformat(),
                "predictions": [
                    {
                        "horse_id": f"horse_{i}",
                        "horse_name": f"Horse {i}",
                        "win_probability": np.random.random(),
                        "current_position": i,
                        "model_confidence": np.random.uniform(0.7, 0.95),
                    }
                    for i in range(1, 9)
                ],
            }

            await manager.send_personal_message(json.dumps(predictions), websocket)
            await asyncio.sleep(2)  # Update every 2 seconds

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# HEALTH CHECK
# ============================================================================


@ml_app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()

        # Test Redis connection
        redis_client.ping()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {"database": "connected", "redis": "connected"},
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(ml_app, host="0.0.0.0", port=8001)
