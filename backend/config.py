"""
Configuration management for AutoPilot IDE Backend
Centralized configuration with environment variable support
"""

import os
from pathlib import Path
from typing import Dict, Any


class BaseConfig:
    """Base configuration with common settings"""
    
    # Application
    APP_NAME = "AutoPilot IDE"
    VERSION = "2.0.0"
    DEBUG = False
    TESTING = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    PROJECTS_DIR = BASE_DIR / "projects"
    EXTENSIONS_DIR = BASE_DIR / "extensions"
    UPLOADS_DIR = BASE_DIR / "uploads"
    DATA_DIR = BASE_DIR / "data"
    
    # Flask
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    JSON_SORT_KEYS = False
    
    # SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # API
    API_PREFIX = '/api'
    API_VERSION = 'v1'
    
    # Terminal
    TERMINAL_TIMEOUT = 30  # seconds
    TERMINAL_MAX_OUTPUT = 10000  # characters
    
    # AI
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS = 2000
    AI_TEMPERATURE = 0.7
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with this config"""
        # Create necessary directories
        for directory in [cls.PROJECTS_DIR, cls.EXTENSIONS_DIR, 
                         cls.UPLOADS_DIR, cls.DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Stricter CORS in production
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get(
        'ALLOWED_ORIGINS', 
        'http://localhost:5000'
    ).split(',')
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        
        # Ensure secret key is set
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    TERMINAL_TIMEOUT = 5  # Shorter timeout for tests
    
    # Use in-memory or temporary directories for testing
    PROJECTS_DIR = Path('/tmp/autopilot_test/projects')
    EXTENSIONS_DIR = Path('/tmp/autopilot_test/extensions')
    UPLOADS_DIR = Path('/tmp/autopilot_test/uploads')
    DATA_DIR = Path('/tmp/autopilot_test/data')


# Configuration dictionary
config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> BaseConfig:
    """Get configuration for specified environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
