"""
Logging Configuration
Centralized logging setup for AutoPilot IDE
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(app):
    """
    Configure application logging
    
    Args:
        app: Flask application instance
    """
    # Get log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_format = app.config.get('LOG_FORMAT')
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format
    )
    
    # Configure Flask app logger
    app.logger.setLevel(log_level)
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    app.logger.addHandler(console_handler)
    
    # File handler (rotating)
    if not app.config.get('TESTING'):
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_dir / 'autopilot_ide.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)
    
    app.logger.info("Logging configured successfully")
