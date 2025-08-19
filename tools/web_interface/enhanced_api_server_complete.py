#!/usr/bin/env python3
"""
Enhanced API and Web Interface System - V2.03
==============================================

Advanced web interface enhancements including:
- Real-time WebSocket updates
- Advanced filtering and search capabilities
- Mobile-responsive design improvements
- User authentication and authorization
- API rate limiting and security

This enhances the V2.03 web interface with modern features and security.
"""

import asyncio
import json
import logging
import os
import sys
import jwt
import bcrypt
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
    Request,
    Response,
    BackgroundTasks,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn
from pydantic import BaseModel

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class RaceFilters(BaseModel):
    date: Optional[str] = None
    venue: Optional[str] = None
    status: Optional[str] = None
    limit: int = 20
    offset: int = 0


class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = None
    limit: int = 10


# WebSocket Manager for real-time communication
class WebSocketManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.race_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection: {len(self.active_connections)}")

    async def connect_to_race(self, websocket: WebSocket, race_id: int) -> None:
        """Connect WebSocket to specific race updates."""
        await websocket.accept()
        if race_id not in self.race_connections:
            self.race_connections[race_id] = set()
        self.race_connections[race_id].add(websocket)
        logger.info(
            f"Connected to race {race_id}: "
            f"{len(self.race_connections[race_id])} connections"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        # Remove from race connections
        for race_id, connections in self.race_connections.items():
            connections.discard(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)}")

    def disconnect_from_race(self, websocket: WebSocket, race_id: int) -> None:
        """Remove WebSocket from race-specific updates."""
        if race_id in self.race_connections:
            self.race_connections[race_id].discard(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected WebSockets."""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_race(self, message: dict, race_id: int) -> None:
        """Broadcast message to race-specific connections."""
        if race_id not in self.race_connections:
            return

        disconnected = set()
        for connection in self.race_connections[race_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to race {race_id}: {e}")
                disconnected.add(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect_from_race(connection, race_id)


class EnhancedAPIServer:
    """Enhanced API server with modern web interface features."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the enhanced API server."""
        self.config = self._load_config(config_path)
        self.app = FastAPI(
            title="Horse Racing AI - Enhanced API",
            description="Advanced horse racing prediction system with real-time",
            version="2.03",
        )

        # Initialize components
        self._setup_middleware()
        self._setup_security()
        self._setup_database()
        self._setup_websocket()
        self._setup_templates()
        self._setup_routes()

        # Background task control
        self.background_tasks_running = False

        logger.info("Enhanced API server initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "racing_data",
                "user": "postgres",
                "password": "password",
            },
            "security": {
                "secret_key": "your-secret-key-change-this",
                "algorithm": "HS256",
                "access_token_expire_minutes": 60,
            },
            "redis": {"host": "localhost", "port": 6379, "db": 0, "password": None},
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "reload": False,
            },
            "rate_limiting": {
                "default": "100/minute",
                "auth": "10/minute",
                "websocket": "30/minute",
            },
            "websocket": {"enabled": True, "heartbeat_interval": 30},
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        return default_config

    def _setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure properly for production
        )

        # Rate limiting
        limiter = Limiter(key_func=get_remote_address)
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        self.limiter = limiter

    def _setup_security(self) -> None:
        """Setup security configuration."""
        self.security_config = self.config.get("security", {})
        self.secret_key = self.security_config.get("secret_key")
        self.algorithm = self.security_config.get("algorithm", "HS256")
        self.access_token_expire_minutes = self.security_config.get(
            "access_token_expire_minutes", 60
        )

        # Redis for session management
        redis_config = self.config.get("redis", {})
        try:
            self.redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                password=redis_config.get("password"),
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None

        # Fallback session storage
        self.user_sessions: Dict[str, dict] = {}

    def _setup_database(self) -> None:
        """Setup database configuration."""
        self.db_config = self.config.get("database", {})
        # Test connection
        try:
            conn = self.get_db_connection()
            conn.close()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def _setup_websocket(self) -> None:
        """Setup WebSocket configuration."""
        websocket_config = self.config.get("websocket", {})
        self.websocket_enabled = websocket_config.get("enabled", True)
        self.heartbeat_interval = websocket_config.get("heartbeat_interval", 30)
        self.websocket_manager = WebSocketManager()
        self.active_connections: Set[WebSocket] = set()

    def _setup_templates(self) -> None:
        """Setup template engine."""
        template_dir = project_root / "templates"
        if template_dir.exists():
            self.templates = Jinja2Templates(directory=str(template_dir))
        else:
            logger.warning(f"Template directory not found: {template_dir}")
            self.templates = None

        # Static files
        static_dir = project_root / "static"
        if static_dir.exists():
            self.app.mount(
                "/static", StaticFiles(directory=str(static_dir)), name="static"
            )

    def _setup_routes(self) -> None:
        """Setup API routes."""
        # Authentication routes
        self._setup_auth_routes()

        # API routes
        self._setup_api_routes()

        # WebSocket routes
        if self.websocket_enabled:
            self._setup_websocket_routes()

        # Web interface routes
        self._setup_web_routes()

    def _setup_auth_routes(self) -> None:
        """Setup authentication routes."""

        @self.app.post("/api/auth/register")
        @self.limiter.limit(self.config["rate_limiting"]["auth"])
        async def register(request: Request, user_data: UserRegistration):
            """Register new user."""
            # Check if user exists
            if await self._user_exists(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists",
                )

            # Hash password
            hashed_password = bcrypt.hashpw(
                user_data.password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Create user
            user_id = await self._create_user(
                user_data.username, hashed_password, user_data.email
            )

            # Create access token
            access_token = self._create_access_token(
                {"sub": user_data.username, "user_id": user_id}
            )

            # Store session
            session_data = {
                "username": user_data.username,
                "email": user_data.email,
                "created_at": datetime.now().isoformat(),
            }
            await self._store_user_session(user_id, session_data)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "username": user_data.username,
                    "email": user_data.email,
                },
            }

        @self.app.post("/api/auth/login")
        @self.limiter.limit(self.config["rate_limiting"]["auth"])
        async def login(request: Request, user_data: UserLogin):
            """Login user."""
            user = await self._authenticate_user(user_data.username, user_data.password)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

            # Create access token
            access_token = self._create_access_token(
                {"sub": user["username"], "user_id": user["id"]}
            )

            # Store session
            session_data = {
                "username": user["username"],
                "email": user["email"],
                "login_at": datetime.now().isoformat(),
            }
            await self._store_user_session(user["id"], session_data)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                },
            }

        @self.app.post("/api/auth/logout")
        async def logout(current_user: dict = Depends(self.get_current_user)):
            """Logout user."""
            await self._remove_user_session(current_user["user_id"])
            return {"message": "Successfully logged out"}

        @self.app.get("/api/auth/profile")
        async def get_profile(current_user: dict = Depends(self.get_current_user)):
            """Get user profile."""
            return {
                "user": {
                    "id": current_user["user_id"],
                    "username": current_user["username"],
                    "session_info": current_user,
                }
            }

    def _setup_api_routes(self) -> None:
        """Setup main API routes."""

        @self.app.get("/api/races")
        @self.limiter.limit(self.config["rate_limiting"]["default"])
        async def get_races(
            request: Request,
            filters: RaceFilters = Depends(),
            current_user: Optional[dict] = Depends(self.get_current_user_optional),
        ):
            """Get races with advanced filtering."""
            races = await self._get_races_filtered(
                filters.dict(exclude_unset=True), filters.limit, filters.offset
            )

            return {
                "races": races,
                "total": len(races),
                "filters": filters.dict(exclude_unset=True),
                "user_authenticated": current_user is not None,
            }

        @self.app.get("/api/races/{race_id}/predictions")
        @self.limiter.limit(self.config["rate_limiting"]["default"])
        async def get_race_predictions(
            request: Request,
            race_id: int,
            current_user: Optional[dict] = Depends(self.get_current_user_optional),
        ):
            """Get AI predictions for specific race."""
            predictions = await self._get_race_predictions(race_id)

            # Add betting suggestions for authenticated users
            if current_user:
                betting_suggestions = await self._get_betting_suggestions(
                    race_id, current_user["user_id"]
                )
                predictions["betting_suggestions"] = betting_suggestions

            return predictions

        @self.app.get("/api/dashboard/stats")
        async def get_dashboard_stats(
            current_user: dict = Depends(self.get_current_user),
        ):
            """Get dashboard statistics."""
            stats = await self._get_dashboard_stats(current_user["user_id"])
            return stats

        @self.app.post("/api/search")
        @self.limiter.limit(self.config["rate_limiting"]["default"])
        async def search(
            request: Request,
            search_data: SearchRequest,
            current_user: Optional[dict] = Depends(self.get_current_user_optional),
        ):
            """Advanced search across the database."""
            results = await self._perform_search(
                search_data.query, search_data.search_type, search_data.limit
            )

            return {
                "query": search_data.query,
                "results": results,
                "total": len(results),
            }

        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.03",
                "features": {
                    "websocket": self.websocket_enabled,
                    "redis": self.redis_client is not None,
                    "authentication": True,
                },
            }

    def _setup_websocket_routes(self) -> None:
        """Setup WebSocket routes."""

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Main WebSocket endpoint for real-time updates."""
            await self.websocket_manager.connect(websocket)

            # Send initial connection message
            await websocket.send_json(
                {
                    "type": "connection_established",
                    "timestamp": datetime.now().isoformat(),
                    "features": ["live_updates", "race_data", "predictions"],
                }
            )

            try:
                while True:
                    data = await websocket.receive_json()
                    await self._handle_websocket_message(websocket, data)

            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.websocket_manager.disconnect(websocket)

        @self.app.websocket("/ws/race/{race_id}")
        async def race_websocket_endpoint(websocket: WebSocket, race_id: int):
            """Race-specific WebSocket for live race updates."""
            await self.websocket_manager.connect_to_race(websocket, race_id)

            # Send initial race data
            race_data = await self._get_race_websocket_data(race_id)
            await websocket.send_json(
                {
                    "type": "race_connected",
                    "race_id": race_id,
                    "data": race_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            try:
                while True:
                    data = await websocket.receive_json()
                    await self._handle_race_websocket_message(websocket, race_id, data)

            except WebSocketDisconnect:
                self.websocket_manager.disconnect_from_race(websocket, race_id)
            except Exception as e:
                logger.error(f"Race WebSocket error: {e}")
                self.websocket_manager.disconnect_from_race(websocket, race_id)

    def _setup_web_routes(self) -> None:
        """Setup web interface routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard page."""
            if not self.templates:
                return HTMLResponse(
                    "<h1>Enhanced Racing AI Dashboard</h1>"
                    "<p>Template system not available</p>"
                )

            return self.templates.TemplateResponse(
                "enhanced_dashboard.html",
                {"request": request, "websocket_enabled": self.websocket_enabled},
            )

        @self.app.get("/race/{race_id}", response_class=HTMLResponse)
        async def race_details(request: Request, race_id: int):
            """Race details page with live updates."""
            if not self.templates:
                return HTMLResponse(
                    f"<h1>Race {race_id} Details</h1>"
                    "<p>Template system not available</p>"
                )

            return self.templates.TemplateResponse(
                "race_details.html",
                {
                    "request": request,
                    "race_id": race_id,
                    "websocket_enabled": self.websocket_enabled,
                },
            )

        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            """Login page."""
            if not self.templates:
                return HTMLResponse("<h1>Login</h1><p>Template not available</p>")

            return self.templates.TemplateResponse("login.html", {"request": request})

    # Authentication helper methods
    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        """Get current authenticated user."""
        token = credentials.credentials
        payload = self._verify_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        user_id = payload.get("user_id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if session is valid
        session = await self._get_user_session(user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"username": username, "user_id": user_id, **session}

    async def get_current_user_optional(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
    ):
        """Get current user if authenticated, otherwise return None."""
        if not credentials:
            return None

        try:
            return await self.get_current_user(credentials)
        except HTTPException:
            return None

    # Database helper methods
    def get_db_connection(self):
        """Get database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed",
            )

    async def _user_exists(self, username: str) -> bool:
        """Check if user exists."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            return result is not None

        except Exception as e:
            logger.error(f"User exists check error: {e}")
            return False

    async def _create_user(
        self, username: str, hashed_password: str, email: str
    ) -> int:
        """Create new user and return user ID."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Create users table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """
            )

            cursor.execute(
                """INSERT INTO users (username, email, password_hash) 
                   VALUES (%s, %s, %s) RETURNING id""",
                (username, email, hashed_password),
            )

            user_id = cursor.fetchone()[0]
            conn.commit()

            cursor.close()
            conn.close()

            return user_id

        except Exception as e:
            logger.error(f"Create user error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

    async def _authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """SELECT id, username, email, password_hash 
                   FROM users WHERE username = %s AND is_active = TRUE""",
                (username,),
            )

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user and bcrypt.checkpw(
                password.encode("utf-8"), user["password_hash"].encode("utf-8")
            ):
                return dict(user)

            return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def _store_user_session(self, user_id: int, session_data: dict) -> None:
        """Store user session data."""
        try:
            if self.redis_client:
                session_key = f"session:{user_id}"
                self.redis_client.setex(
                    session_key,
                    self.access_token_expire_minutes * 60,
                    json.dumps(session_data),
                )
            else:
                self.user_sessions[str(user_id)] = session_data

        except Exception as e:
            logger.error(f"Store session error: {e}")

    async def _get_user_session(self, user_id: int) -> Optional[dict]:
        """Get user session data."""
        try:
            if self.redis_client:
                session_key = f"session:{user_id}"
                session_data = self.redis_client.get(session_key)
                if session_data:
                    return json.loads(session_data)
            else:
                return self.user_sessions.get(str(user_id))

            return None

        except Exception as e:
            logger.error(f"Get session error: {e}")
            return None

    async def _remove_user_session(self, user_id: int) -> None:
        """Remove user session data."""
        try:
            if self.redis_client:
                session_key = f"session:{user_id}"
                self.redis_client.delete(session_key)
            else:
                self.user_sessions.pop(str(user_id), None)

        except Exception as e:
            logger.error(f"Remove session error: {e}")

    # Data retrieval methods
    async def _get_races_filtered(
        self, filters: dict, limit: int, offset: int
    ) -> List[dict]:
        """Get races with advanced filtering."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build dynamic query
            query = "SELECT * FROM races WHERE 1=1"
            params = []

            if filters.get("date"):
                query += " AND race_date = %s"
                params.append(filters["date"])

            if filters.get("venue"):
                query += " AND venue ILIKE %s"
                params.append(f"%{filters['venue']}%")

            if filters.get("status"):
                query += " AND status = %s"
                params.append(filters["status"])

            query += " ORDER BY race_date DESC, race_time DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            races = cursor.fetchall()

            cursor.close()
            conn.close()

            return [dict(race) for race in races]

        except Exception as e:
            logger.error(f"Get races filtered error: {e}")
            return []

    async def _get_race_predictions(self, race_id: int) -> dict:
        """Get AI predictions for a specific race."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get race details
            cursor.execute("SELECT * FROM races WHERE id = %s", (race_id,))
            race = cursor.fetchone()

            if not race:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
                )

            # Get predictions
            cursor.execute(
                """
                SELECT 
                    r.horse_name,
                    r.jockey,
                    r.trainer,
                    r.weight,
                    r.odds,
                    COALESCE(p.win_probability, 0) as win_probability,
                    COALESCE(p.place_probability, 0) as place_probability,
                    COALESCE(p.confidence_score, 0) as confidence_score
                FROM records r
                LEFT JOIN predictions p ON r.id = p.record_id
                WHERE r.race_id = %s
                ORDER BY p.win_probability DESC NULLS LAST
            """,
                (race_id,),
            )

            predictions = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                "race": dict(race),
                "predictions": [dict(pred) for pred in predictions],
                "generated_at": datetime.now().isoformat(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get race predictions error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch predictions",
            )

    async def _get_betting_suggestions(self, race_id: int, user_id: int) -> dict:
        """Get personalized betting suggestions."""
        try:
            # This would integrate with the betting system
            # For now, return basic suggestions based on predictions

            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                SELECT 
                    r.horse_name,
                    r.odds,
                    p.win_probability,
                    p.place_probability,
                    (p.win_probability * r.odds) as expected_value
                FROM records r
                LEFT JOIN predictions p ON r.id = p.record_id
                WHERE r.race_id = %s AND p.win_probability > 0.1
                ORDER BY expected_value DESC
                LIMIT 3
            """,
                (race_id,),
            )

            suggestions = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                "recommended_bets": [dict(sugg) for sugg in suggestions],
                "strategy": "value_betting",
                "confidence": "medium",
            }

        except Exception as e:
            logger.error(f"Get betting suggestions error: {e}")
            return {
                "recommended_bets": [],
                "strategy": "conservative",
                "confidence": "low",
            }

    async def _get_dashboard_stats(self, user_id: int) -> dict:
        """Get dashboard statistics for user."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get overall statistics
            cursor.execute("SELECT COUNT(*) as total_races FROM races")
            total_races = cursor.fetchone()["total_races"]

            cursor.execute(
                """SELECT COUNT(*) as total_horses 
                   FROM (SELECT DISTINCT horse_name FROM records) 
                   as unique_horses"""
            )
            total_horses = cursor.fetchone()["total_horses"]

            cursor.execute(
                """SELECT COUNT(*) as total_predictions 
                   FROM predictions WHERE confidence_score > 0.5"""
            )
            total_predictions = cursor.fetchone()["total_predictions"]

            # Get recent activity
            cursor.execute(
                """
                SELECT race_date, venue, COUNT(*) as race_count
                FROM races 
                WHERE race_date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY race_date, venue
                ORDER BY race_date DESC
                LIMIT 10
            """
            )

            recent_activity = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                "overview": {
                    "total_races": total_races,
                    "total_horses": total_horses,
                    "total_predictions": total_predictions,
                    "accuracy_rate": 0.85,  # This would be calculated from results
                },
                "recent_activity": [dict(activity) for activity in recent_activity],
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Get dashboard stats error: {e}")
            return {
                "overview": {
                    "total_races": 0,
                    "total_horses": 0,
                    "total_predictions": 0,
                },
                "recent_activity": [],
            }

    async def _perform_search(
        self, query: str, search_type: Optional[str], limit: int
    ) -> List[dict]:
        """Perform advanced search across the database."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            results = []

            # Search horses
            if not search_type or search_type == "horses":
                cursor.execute(
                    """
                    SELECT DISTINCT horse_name, COUNT(*) as race_count
                    FROM records 
                    WHERE horse_name ILIKE %s
                    GROUP BY horse_name
                    ORDER BY race_count DESC
                    LIMIT %s
                """,
                    (f"%{query}%", limit),
                )

                horses = cursor.fetchall()
                for horse in horses:
                    results.append(
                        {
                            "type": "horse",
                            "name": horse["horse_name"],
                            "race_count": horse["race_count"],
                        }
                    )

            # Search venues
            if not search_type or search_type == "venues":
                cursor.execute(
                    """
                    SELECT venue, COUNT(*) as race_count
                    FROM races 
                    WHERE venue ILIKE %s
                    GROUP BY venue
                    ORDER BY race_count DESC
                    LIMIT %s
                """,
                    (f"%{query}%", limit),
                )

                venues = cursor.fetchall()
                for venue in venues:
                    results.append(
                        {
                            "type": "venue",
                            "name": venue["venue"],
                            "race_count": venue["race_count"],
                        }
                    )

            # Search jockeys
            if not search_type or search_type == "jockeys":
                cursor.execute(
                    """
                    SELECT DISTINCT jockey, COUNT(*) as race_count
                    FROM records 
                    WHERE jockey ILIKE %s
                    GROUP BY jockey
                    ORDER BY race_count DESC
                    LIMIT %s
                """,
                    (f"%{query}%", limit),
                )

                jockeys = cursor.fetchall()
                for jockey in jockeys:
                    results.append(
                        {
                            "type": "jockey",
                            "name": jockey["jockey"],
                            "race_count": jockey["race_count"],
                        }
                    )

            cursor.close()
            conn.close()

            return results[:limit]

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    # WebSocket helper methods
    async def _handle_websocket_message(self, websocket: WebSocket, data: dict) -> None:
        """Handle incoming WebSocket message."""
        try:
            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )

            elif message_type == "subscribe":
                # Handle subscription to specific data feeds
                feed = data.get("feed")
                if feed:
                    await self._subscribe_to_feed(websocket, feed)

            elif message_type == "unsubscribe":
                # Handle unsubscription
                feed = data.get("feed")
                if feed:
                    await self._unsubscribe_from_feed(websocket, feed)

        except Exception as e:
            logger.error(f"WebSocket message handling error: {e}")

    async def _handle_race_websocket_message(
        self, websocket: WebSocket, race_id: int, data: dict
    ) -> None:
        """Handle race-specific WebSocket message."""
        try:
            message_type = data.get("type")

            if message_type == "get_updates":
                # Send latest race updates
                updates = await self._get_race_updates(race_id)
                await websocket.send_json(
                    {
                        "type": "race_updates",
                        "race_id": race_id,
                        "updates": updates,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Race WebSocket message handling error: {e}")

    async def _get_race_websocket_data(self, race_id: int) -> dict:
        """Get initial race data for WebSocket connection."""
        try:
            predictions = await self._get_race_predictions(race_id)
            return {
                "race": predictions["race"],
                "predictions": predictions["predictions"][:5],  # Top 5 only
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Get race WebSocket data error: {e}")
            return {}

    async def _get_race_updates(self, race_id: int) -> dict:
        """Get latest race updates."""
        try:
            # This would typically get live odds, scratches, track conditions
            # For now, return basic update information
            return {
                "odds_updated": datetime.now().isoformat(),
                "track_condition": "Good",
                "weather": "Clear",
                "scratches": [],
            }
        except Exception as e:
            logger.error(f"Get race updates error: {e}")
            return {}

    async def _subscribe_to_feed(self, websocket: WebSocket, feed: str) -> None:
        """Subscribe WebSocket to specific data feed."""
        # Implementation for feed subscriptions
        await websocket.send_json(
            {
                "type": "subscription_confirmed",
                "feed": feed,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _unsubscribe_from_feed(self, websocket: WebSocket, feed: str) -> None:
        """Unsubscribe WebSocket from data feed."""
        await websocket.send_json(
            {
                "type": "unsubscription_confirmed",
                "feed": feed,
                "timestamp": datetime.now().isoformat(),
            }
        )

    # Background tasks for real-time updates
    async def start_background_tasks(self) -> None:
        """Start background tasks for real-time updates."""
        if self.websocket_enabled and not self.background_tasks_running:
            self.background_tasks_running = True
            asyncio.create_task(self._broadcast_updates())
            asyncio.create_task(self._heartbeat_task())

    async def _broadcast_updates(self) -> None:
        """Periodically broadcast updates to all connected clients."""
        while self.background_tasks_running:
            try:
                # Get latest system updates
                updates = await self._get_system_updates()

                if updates and self.websocket_manager.active_connections:
                    await self.websocket_manager.broadcast(
                        {
                            "type": "system_update",
                            "updates": updates,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                await asyncio.sleep(30)  # Update every 30 seconds

            except Exception as e:
                logger.error(f"Broadcast updates error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _heartbeat_task(self) -> None:
        """Send heartbeat to maintain connections."""
        while self.background_tasks_running:
            try:
                if self.websocket_manager.active_connections:
                    await self.websocket_manager.broadcast(
                        {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                    )

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _get_system_updates(self) -> Optional[dict]:
        """Get latest system updates for broadcasting."""
        try:
            # This would check for new races, updated predictions, etc.
            # For now, return None to avoid unnecessary broadcasts
            return None
        except Exception as e:
            logger.error(f"Get system updates error: {e}")
            return None

    def run(self) -> None:
        """Run the enhanced API server."""
        server_config = self.config.get("server", {})

        # Start background tasks in event loop
        async def startup():
            await self.start_background_tasks()

        # Add startup event
        @self.app.on_event("startup")
        async def startup_event():
            await startup()

        uvicorn.run(
            self.app,
            host=server_config.get("host", "0.0.0.0"),
            port=server_config.get("port", 8000),
            debug=server_config.get("debug", False),
            reload=server_config.get("reload", False),
        )


# Main function for standalone execution
async def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced API and Web Interface Server"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize and run server
    server = EnhancedAPIServer(config_path=args.config)

    # Override config with command line args
    if args.host:
        server.config["server"]["host"] = args.host
    if args.port:
        server.config["server"]["port"] = args.port
    if args.debug:
        server.config["server"]["debug"] = True

    server.run()


if __name__ == "__main__":
    asyncio.run(main())
