"""
Configuration management for AutoPilot IDE Backend
Centralized configuration with environment variable support and security hardening
"""

import os
import secrets
from pathlib import Path
from typing import Dict, Any


class BaseConfig:
    """Base configuration with common settings and security hardening"""
    
    # Application
    APP_NAME = "AutoPilot IDE"
    VERSION = "2.0.0"
    DEBUG = False
    TESTING = False
    
    # Security - Generate strong secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Session Security
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per minute"  # Default rate limit
    RATELIMIT_STORAGE_URL = "memory://"  # Use Redis in production
    
    # Rate limit configurations for different endpoints
    RATELIMIT_API_DEFAULT = 100  # requests per minute
    RATELIMIT_API_WINDOW = 60  # seconds
    RATELIMIT_TERMINAL = 10  # Terminal commands per minute
    RATELIMIT_FILE_UPLOAD = 20  # File uploads per minute
    RATELIMIT_AUTH = 5  # Authentication attempts per minute
    
    # CSRF Protection
    CSRF_ENABLED = True
    CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Content Security
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {
        'py', 'js', 'jsx', 'ts', 'tsx', 'html', 'css', 'json',
        'md', 'txt', 'yml', 'yaml', 'xml', 'sql', 'sh', 'bat',
        'c', 'cpp', 'h', 'java', 'go', 'rs', 'php', 'rb'
    }
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    PROJECTS_DIR = BASE_DIR / "projects"
    EXTENSIONS_DIR = BASE_DIR / "extensions"
    UPLOADS_DIR = BASE_DIR / "uploads"
    DATA_DIR = BASE_DIR / "data"
    
    # Flask
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # API
    API_PREFIX = '/api'
    API_VERSION = 'v1'
    
    # Terminal Security
    TERMINAL_TIMEOUT = 30  # seconds
    TERMINAL_MAX_TIMEOUT = 300  # Maximum allowed timeout
    TERMINAL_MAX_OUTPUT = 10000  # characters
    TERMINAL_ALLOWED_COMMANDS = [
        'python', 'python3', 'pip', 'pip3',
        'node', 'npm', 'npx', 'yarn',
        'git', 'ls', 'dir', 'cd', 'pwd',
        'echo', 'cat', 'type', 'more', 'less',
        'grep', 'find', 'which', 'where',
        'env', 'set', 'export'
    ]
    TERMINAL_BLOCKED_COMMANDS = [
        'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs',
        'dd', 'shutdown', 'reboot', 'halt', 'poweroff',
        'kill', 'killall', 'pkill', 'taskkill',
        'chmod', 'chown', 'chgrp', 'passwd', 'sudo', 'su',
        'wget', 'curl', 'nc', 'netcat', 'telnet', 'ssh',
        'eval', 'exec', 'source', 'bash', 'sh', 'cmd',
        'reg', 'regedit', 'bcdedit', 'diskpart'
    ]
    
    # AI Configuration
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS = 2000
    AI_TEMPERATURE = 0.7
    AI_TIMEOUT = 30  # seconds
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    LOG_FILE = None  # Set to path for file logging
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self' data:",
        'connect-src': "'self' ws: wss:",
        'frame-ancestors': "'none'"
    }
    
    # IP Blocklist
    IP_BLOCKLIST_ENABLED = True
    IP_VIOLATION_THRESHOLD = 10  # Block after 10 violations
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with this config"""
        # Create necessary directories
        for directory in [cls.PROJECTS_DIR, cls.EXTENSIONS_DIR, 
                         cls.UPLOADS_DIR, cls.DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Validate security settings
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            if not cls.DEBUG:
                raise ValueError("SECRET_KEY must be set to a strong random value in production")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    RATELIMIT_ENABLED = False  # Disable rate limiting in development
    CSRF_ENABLED = False  # Disable CSRF in development for easier testing
    
    # Development secret key (will be auto-generated if not set)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-' + secrets.token_hex(16))


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    RATELIMIT_ENABLED = True
    CSRF_ENABLED = True
    
    # Must use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Use Redis for rate limiting in production
    RATELIMIT_STORAGE_URL = os.environ.get(
        'REDIS_URL', 
        'redis://localhost:6379/0'
    )
    
    # Stricter CORS in production
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get(
        'ALLOWED_ORIGINS', 
        'https://yourdomain.com'
    ).split(',')
    
    # Enable HSTS
    SECURITY_HEADERS = {
        **BaseConfig.SECURITY_HEADERS,
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Production logging
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/production.log')
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        
        # Ensure secret key is set and strong
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        
        if len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        # Create logs directory
        if cls.LOG_FILE:
            log_dir = Path(cls.LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    TERMINAL_TIMEOUT = 5  # Shorter timeout for tests
    
    # Disable security features for testing
    RATELIMIT_ENABLED = False
    CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Use in-memory or temporary directories for testing
    PROJECTS_DIR = Path('/tmp/autopilot_test/projects')
    EXTENSIONS_DIR = Path('/tmp/autopilot_test/extensions')
    UPLOADS_DIR = Path('/tmp/autopilot_test/uploads')
    DATA_DIR = Path('/tmp/autopilot_test/data')
    
    # Test secret key
    SECRET_KEY = 'test-secret-key-' + secrets.token_hex(16)


# Configuration dictionary
config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> BaseConfig:
    """
    Get configuration for specified environment
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Configuration class for the environment
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


def generate_secret_key() -> str:
    """
    Generate a cryptographically strong secret key
    
    Returns:
        URL-safe random string suitable for SECRET_KEY
    """
    return secrets.token_urlsafe(32)


# Export configuration utilities
__all__ = [
    'BaseConfig',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'config',
    'get_config',
    'generate_secret_key'
]
