# pgAdmin Configuration File
# This file contains configuration settings for pgAdmin4

# Server settings
SERVE_STATIC = True
DEFAULT_SERVER = "0.0.0.0"
DEFAULT_SERVER_PORT = 80

# Authentication settings
AUTHENTICATION_SOURCES = ["internal"]
MASTER_PASSWORD_REQUIRED = False

# Database settings
SESSION_DB_PATH = "/var/lib/pgadmin/sessions"
STORAGE_DIR = "/var/lib/pgadmin/storage"
LOG_FILE = "/var/lib/pgadmin/pgadmin4.log"

# Security settings
ENHANCED_COOKIE_PROTECTION = True
LOGIN_BANNER = "Horse Racing AI - Database Administration"
CONSOLE_LOG_LEVEL = 20  # INFO level

# Server connection defaults
DEFAULT_BINARY_PATHS = {"pg": "/usr/bin"}

# Query tool settings
QUERY_HISTORY_MAX_COUNT = 100
SELECT_LIMIT_DEFAULT = 1000

# Browser settings
SHOW_SYSTEM_OBJECTS = False

# Auto-discovery settings
AUTO_DISCOVER_SERVERS = True
SERVER_GROUP_NAME = "Horse Racing Servers"

# Session settings
SESSION_COOKIE_NAME = "pga4_session"
SESSION_EXPIRATION_TIME = 1  # 1 hour

# Upload settings
FILE_UPLOAD_PATH = "/var/lib/pgadmin/upload"
MAX_FILE_UPLOAD_SIZE = 50  # 50MB

# Feature settings
FEATURE_TABS = True
ENABLE_PSQL = True

# Logging settings
CONSOLE_LOG_LEVEL = 20
FILE_LOG_LEVEL = 20
