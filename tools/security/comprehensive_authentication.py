#!/usr/bin/env python3
"""
Comprehensive Authentication and Authorization System for Horse Racing AI V2.03
Provides secure user management, role-based access control, and session management
"""

import os
import jwt
import bcrypt
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum
import time
import hashlib
from functools import wraps
import re


class Permission(Enum):
    """System permissions"""

    # Data permissions
    READ_RACES = "read_races"
    WRITE_RACES = "write_races"
    READ_HORSES = "read_horses"
    WRITE_HORSES = "write_horses"
    READ_PREDICTIONS = "read_predictions"
    WRITE_PREDICTIONS = "write_predictions"

    # Betting permissions
    PLACE_BETS = "place_bets"
    VIEW_BETS = "view_bets"
    MANAGE_BETS = "manage_bets"

    # Model permissions
    RUN_MODELS = "run_models"
    TRAIN_MODELS = "train_models"
    DEPLOY_MODELS = "deploy_models"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM = "manage_system"

    # API permissions
    API_ACCESS = "api_access"
    API_ADMIN = "api_admin"


class Role(Enum):
    """Predefined system roles"""

    GUEST = "guest"
    USER = "user"
    ANALYST = "analyst"
    TRADER = "trader"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class User:
    """User account data"""

    user_id: str
    username: str
    email: str
    password_hash: str
    salt: str
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    login_attempts: int
    account_locked: bool
    mfa_enabled: bool
    mfa_secret: Optional[str]
    session_timeout: int  # minutes
    api_key: Optional[str]
    api_key_expires: Optional[datetime]


@dataclass
class Session:
    """User session data"""

    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""

    success: bool
    user: Optional[User]
    session: Optional[Session]
    token: Optional[str]
    error_message: Optional[str]
    requires_mfa: bool = False


class PasswordValidator:
    """Password strength validation"""

    @staticmethod
    def validate_password_strength(password: str) -> List[str]:
        """Validate password meets security requirements"""
        errors = []

        if len(password) < 12:
            errors.append("Password must be at least 12 characters long")

        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Check for common patterns
        if re.search(r"(.)\1{2,}", password):
            errors.append("Password cannot contain repeated characters")

        if re.search(r"(012|123|234|345|456|567|678|789|890)", password):
            errors.append("Password cannot contain sequential numbers")

        if re.search(
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
            password.lower(),
        ):
            errors.append("Password cannot contain sequential letters")

        # Check for common words
        common_words = ["password", "admin", "user", "horse", "racing", "bet", "win"]
        for word in common_words:
            if word.lower() in password.lower():
                errors.append(f"Password cannot contain common word: {word}")

        return errors

    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password"""
        import string

        # Ensure password contains required character types
        chars = string.ascii_letters + string.digits + "!@#$%^&*"

        while True:
            password = "".join(secrets.choice(chars) for _ in range(length))
            if not PasswordValidator.validate_password_strength(password):
                return password


class TokenManager:
    """JWT token management"""

    def __init__(self, secret_key: str, issuer: str = "horse_racing_ai"):
        self.secret_key = secret_key
        self.issuer = issuer
        self.algorithm = "HS256"

    def generate_access_token(self, user: User, expires_minutes: int = 60) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "roles": user.roles,
            "permissions": user.permissions,
            "iss": self.issuer,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user: User, expires_days: int = 30) -> str:
        """Generate JWT refresh token"""
        payload = {
            "user_id": user.user_id,
            "iss": self.issuer,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=expires_days),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class RoleBasedAccessControl:
    """Role-based access control system"""

    def __init__(self):
        self.role_permissions = self._init_role_permissions()
        self.logger = logging.getLogger(__name__)

    def _init_role_permissions(self) -> Dict[str, Set[Permission]]:
        """Initialize role-permission mappings"""
        return {
            Role.GUEST.value: {
                Permission.READ_RACES,
                Permission.READ_HORSES,
                Permission.READ_PREDICTIONS,
            },
            Role.USER.value: {
                Permission.READ_RACES,
                Permission.READ_HORSES,
                Permission.READ_PREDICTIONS,
                Permission.PLACE_BETS,
                Permission.VIEW_BETS,
                Permission.API_ACCESS,
            },
            Role.ANALYST.value: {
                Permission.READ_RACES,
                Permission.WRITE_RACES,
                Permission.READ_HORSES,
                Permission.WRITE_HORSES,
                Permission.READ_PREDICTIONS,
                Permission.WRITE_PREDICTIONS,
                Permission.RUN_MODELS,
                Permission.API_ACCESS,
            },
            Role.TRADER.value: {
                Permission.READ_RACES,
                Permission.READ_HORSES,
                Permission.READ_PREDICTIONS,
                Permission.PLACE_BETS,
                Permission.VIEW_BETS,
                Permission.MANAGE_BETS,
                Permission.RUN_MODELS,
                Permission.API_ACCESS,
            },
            Role.ADMIN.value: {perm for perm in Permission},  # All permissions
            Role.SYSTEM.value: {perm for perm in Permission},  # All permissions
        }

    def get_role_permissions(self, role: str) -> Set[Permission]:
        """Get permissions for a role"""
        return self.role_permissions.get(role, set())

    def has_permission(
        self, user_roles: List[str], required_permission: Permission
    ) -> bool:
        """Check if user roles have required permission"""
        for role in user_roles:
            if required_permission in self.get_role_permissions(role):
                return True
        return False

    def can_access_resource(
        self, user_roles: List[str], resource: str, action: str
    ) -> bool:
        """Check if user can access resource with specific action"""
        # Map resource/action combinations to permissions
        resource_permissions = {
            ("races", "read"): Permission.READ_RACES,
            ("races", "write"): Permission.WRITE_RACES,
            ("horses", "read"): Permission.READ_HORSES,
            ("horses", "write"): Permission.WRITE_HORSES,
            ("predictions", "read"): Permission.READ_PREDICTIONS,
            ("predictions", "write"): Permission.WRITE_PREDICTIONS,
            ("bets", "read"): Permission.VIEW_BETS,
            ("bets", "write"): Permission.PLACE_BETS,
            ("bets", "manage"): Permission.MANAGE_BETS,
            ("models", "run"): Permission.RUN_MODELS,
            ("models", "train"): Permission.TRAIN_MODELS,
            ("models", "deploy"): Permission.DEPLOY_MODELS,
            ("users", "manage"): Permission.MANAGE_USERS,
            ("audit", "read"): Permission.VIEW_AUDIT_LOGS,
            ("system", "manage"): Permission.MANAGE_SYSTEM,
            ("api", "access"): Permission.API_ACCESS,
            ("api", "admin"): Permission.API_ADMIN,
        }

        required_permission = resource_permissions.get((resource, action))
        if not required_permission:
            return False

        return self.has_permission(user_roles, required_permission)


class UserManager:
    """User account management"""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize user database schema"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    permissions TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login TEXT,
                    login_attempts INTEGER DEFAULT 0,
                    account_locked INTEGER DEFAULT 0,
                    mfa_enabled INTEGER DEFAULT 0,
                    mfa_secret TEXT,
                    session_timeout INTEGER DEFAULT 60,
                    api_key TEXT,
                    api_key_expires TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """
            )

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)"
            )

            conn.commit()

    def create_user(
        self, username: str, email: str, password: str, roles: List[str] = None
    ) -> Optional[User]:
        """Create new user account"""
        try:
            # Validate password
            password_errors = PasswordValidator.validate_password_strength(password)
            if password_errors:
                self.logger.error(f"Password validation failed: {password_errors}")
                return None

            # Generate salt and hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

            # Create user
            user = User(
                user_id=self._generate_user_id(),
                username=username,
                email=email,
                password_hash=password_hash.decode("utf-8"),
                salt=salt.decode("utf-8"),
                roles=roles or [Role.USER.value],
                permissions=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_login=None,
                login_attempts=0,
                account_locked=False,
                mfa_enabled=False,
                mfa_secret=None,
                session_timeout=60,
                api_key=None,
                api_key_expires=None,
            )

            # Store user in database
            with sqlite3.connect(self.database_path) as conn:
                conn.execute(
                    """
                    INSERT INTO users (
                        user_id, username, email, password_hash, salt, roles,
                        permissions, created_at, updated_at, last_login,
                        login_attempts, account_locked, mfa_enabled, mfa_secret,
                        session_timeout, api_key, api_key_expires
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user.user_id,
                        user.username,
                        user.email,
                        user.password_hash,
                        user.salt,
                        ",".join(user.roles),
                        ",".join(user.permissions),
                        user.created_at.isoformat(),
                        user.updated_at.isoformat(),
                        None,
                        user.login_attempts,
                        int(user.account_locked),
                        int(user.mfa_enabled),
                        user.mfa_secret,
                        user.session_timeout,
                        user.api_key,
                        None,
                    ),
                )
                conn.commit()

            self.logger.info(f"Created user: {username}")
            return user

        except Exception as e:
            self.logger.error(f"Error creating user {username}: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None

            # Check if account is locked
            if user.account_locked:
                self.logger.warning(
                    f"Authentication attempt on locked account: {username}"
                )
                return None

            # Verify password
            if bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            ):
                # Reset login attempts on successful authentication
                self._reset_login_attempts(user.user_id)
                self._update_last_login(user.user_id)
                return user
            else:
                # Increment login attempts
                self._increment_login_attempts(user.user_id)
                return None

        except Exception as e:
            self.logger.error(f"Error authenticating user {username}: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ?", (username,)
                )
                row = cursor.fetchone()

                if row:
                    return self._row_to_user(row)
                return None

        except Exception as e:
            self.logger.error(f"Error getting user {username}: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()

                if row:
                    return self._row_to_user(row)
                return None

        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return None

    def create_session(
        self, user: User, ip_address: str, user_agent: str
    ) -> Optional[Session]:
        """Create user session"""
        try:
            session = Session(
                session_id=self._generate_session_id(),
                user_id=user.user_id,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=user.session_timeout),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True,
            )

            # Store session in database
            with sqlite3.connect(self.database_path) as conn:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        session_id, user_id, created_at, last_activity,
                        expires_at, ip_address, user_agent, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.user_id,
                        session.created_at.isoformat(),
                        session.last_activity.isoformat(),
                        session.expires_at.isoformat(),
                        session.ip_address,
                        session.user_agent,
                        int(session.is_active),
                    ),
                )
                conn.commit()

            return session

        except Exception as e:
            self.logger.error(f"Error creating session for user {user.user_id}: {e}")
            return None

    def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate and refresh session"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM sessions 
                    WHERE session_id = ? AND is_active = 1
                """,
                    (session_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return None

                session = self._row_to_session(row)

                # Check if session is expired
                if datetime.now() > session.expires_at:
                    self._deactivate_session(session_id)
                    return None

                # Update last activity
                self._update_session_activity(session_id)
                session.last_activity = datetime.now()

                return session

        except Exception as e:
            self.logger.error(f"Error validating session {session_id}: {e}")
            return None

    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        import uuid

        return str(uuid.uuid4())

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid

        return str(uuid.uuid4())

    def _increment_login_attempts(self, user_id: str):
        """Increment failed login attempts"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.execute(
                """
                UPDATE users SET login_attempts = login_attempts + 1,
                account_locked = CASE WHEN login_attempts >= 4 THEN 1 ELSE 0 END
                WHERE user_id = ?
            """,
                (user_id,),
            )
            conn.commit()

    def _reset_login_attempts(self, user_id: str):
        """Reset login attempts counter"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                UPDATE users SET login_attempts = 0, account_locked = 0
                WHERE user_id = ?
            """,
                (user_id,),
            )
            conn.commit()

    def _update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                UPDATE users SET last_login = ?
                WHERE user_id = ?
            """,
                (datetime.now().isoformat(), user_id),
            )
            conn.commit()

    def _update_session_activity(self, session_id: str):
        """Update session activity timestamp"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                UPDATE sessions SET last_activity = ?
                WHERE session_id = ?
            """,
                (datetime.now().isoformat(), session_id),
            )
            conn.commit()

    def _deactivate_session(self, session_id: str):
        """Deactivate session"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                UPDATE sessions SET is_active = 0
                WHERE session_id = ?
            """,
                (session_id,),
            )
            conn.commit()

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            salt=row["salt"],
            roles=row["roles"].split(",") if row["roles"] else [],
            permissions=row["permissions"].split(",") if row["permissions"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_login=(
                datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
            ),
            login_attempts=row["login_attempts"],
            account_locked=bool(row["account_locked"]),
            mfa_enabled=bool(row["mfa_enabled"]),
            mfa_secret=row["mfa_secret"],
            session_timeout=row["session_timeout"],
            api_key=row["api_key"],
            api_key_expires=(
                datetime.fromisoformat(row["api_key_expires"])
                if row["api_key_expires"]
                else None
            ),
        )

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Convert database row to Session object"""
        return Session(
            session_id=row["session_id"],
            user_id=row["user_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_activity=datetime.fromisoformat(row["last_activity"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            ip_address=row["ip_address"],
            user_agent=row["user_agent"],
            is_active=bool(row["is_active"]),
        )


class ComprehensiveAuthSystem:
    """Main authentication and authorization system"""

    def __init__(self, database_path: str, jwt_secret: str):
        self.user_manager = UserManager(database_path)
        self.token_manager = TokenManager(jwt_secret)
        self.rbac = RoleBasedAccessControl()
        self.logger = logging.getLogger(__name__)

    def register_user(
        self, username: str, email: str, password: str, roles: List[str] = None
    ) -> AuthenticationResult:
        """Register new user"""
        try:
            user = self.user_manager.create_user(username, email, password, roles)

            if user:
                return AuthenticationResult(
                    success=True,
                    user=user,
                    session=None,
                    token=None,
                    error_message=None,
                )
            else:
                return AuthenticationResult(
                    success=False,
                    user=None,
                    session=None,
                    token=None,
                    error_message="Failed to create user account",
                )

        except Exception as e:
            self.logger.error(f"Error registering user {username}: {e}")
            return AuthenticationResult(
                success=False, user=None, session=None, token=None, error_message=str(e)
            )

    def login(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> AuthenticationResult:
        """User login"""
        try:
            # Authenticate user
            user = self.user_manager.authenticate_user(username, password)

            if not user:
                return AuthenticationResult(
                    success=False,
                    user=None,
                    session=None,
                    token=None,
                    error_message="Invalid username or password",
                )

            # Create session
            session = self.user_manager.create_session(user, ip_address, user_agent)

            if not session:
                return AuthenticationResult(
                    success=False,
                    user=None,
                    session=None,
                    token=None,
                    error_message="Failed to create session",
                )

            # Generate access token
            access_token = self.token_manager.generate_access_token(user)

            return AuthenticationResult(
                success=True,
                user=user,
                session=session,
                token=access_token,
                error_message=None,
                requires_mfa=user.mfa_enabled,
            )

        except Exception as e:
            self.logger.error(f"Error during login for {username}: {e}")
            return AuthenticationResult(
                success=False,
                user=None,
                session=None,
                token=None,
                error_message="Login failed",
            )

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        return self.token_manager.verify_token(token)

    def authorize(self, user_roles: List[str], resource: str, action: str) -> bool:
        """Check authorization for resource access"""
        return self.rbac.can_access_resource(user_roles, resource, action)

    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get user from context (implementation depends on framework)
                user_roles = kwargs.get("user_roles", [])

                if not self.rbac.has_permission(user_roles, permission):
                    raise PermissionError(f"Permission {permission.value} required")

                return func(*args, **kwargs)

            return wrapper

        return decorator

    def require_role(self, required_role: Role):
        """Decorator to require specific role"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_roles = kwargs.get("user_roles", [])

                if required_role.value not in user_roles:
                    raise PermissionError(f"Role {required_role.value} required")

                return func(*args, **kwargs)

            return wrapper

        return decorator


def main():
    """Main execution function"""
    print("🔐 Horse Racing AI V2.03 - Comprehensive Authentication System")
    print("=" * 70)

    # Initialize auth system
    auth_system = ComprehensiveAuthSystem(
        database_path="config/auth.db", jwt_secret="your_jwt_secret_key_here"
    )

    print("\n👤 Testing User Registration:")

    # Test user registration
    test_users = [
        ("admin", "admin@example.com", "SecurePassword123!", [Role.ADMIN.value]),
        ("analyst", "analyst@example.com", "AnalystPass456!", [Role.ANALYST.value]),
        ("trader", "trader@example.com", "TraderPass789!", [Role.TRADER.value]),
        ("user", "user@example.com", "UserPass000!", [Role.USER.value]),
    ]

    for username, email, password, roles in test_users:
        result = auth_system.register_user(username, email, password, roles)
        print(
            f"  {'✅' if result.success else '❌'} Register {username}: "
            f"{'Success' if result.success else result.error_message}"
        )

    print("\n🔑 Testing User Authentication:")

    # Test authentication
    login_result = auth_system.login(
        "admin", "SecurePassword123!", "127.0.0.1", "Test Browser"
    )
    print(
        f"  {'✅' if login_result.success else '❌'} Admin Login: "
        f"{'Success' if login_result.success else login_result.error_message}"
    )

    if login_result.success:
        print(f"    - User ID: {login_result.user.user_id}")
        print(f"    - Roles: {', '.join(login_result.user.roles)}")
        print(f"    - Session ID: {login_result.session.session_id}")
        print(f"    - Token Generated: {bool(login_result.token)}")

    print("\n🛡️ Testing Authorization:")

    # Test role-based access control
    test_permissions = [
        (["admin"], "users", "manage", True),
        (["user"], "users", "manage", False),
        (["analyst"], "predictions", "write", True),
        (["user"], "predictions", "write", False),
        (["trader"], "bets", "place", True),
        (["guest"], "bets", "place", False),
    ]

    for roles, resource, action, expected in test_permissions:
        result = auth_system.authorize(roles, resource, action)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {'/'.join(roles)} → {resource}:{action} = {result}")

    print("\n🔍 Testing Token Validation:")

    if login_result.success and login_result.token:
        token_payload = auth_system.validate_token(login_result.token)
        if token_payload:
            print(f"  ✅ Token Valid:")
            print(f"    - User: {token_payload.get('username')}")
            print(f"    - Roles: {', '.join(token_payload.get('roles', []))}")
            print(
                f"    - Expires: {datetime.fromtimestamp(token_payload.get('exp', 0))}"
            )
        else:
            print(f"  ❌ Token Invalid or Expired")

    print("\n✅ Authentication and authorization system demonstration completed")


if __name__ == "__main__":
    main()
