"""
AutoPilot IDE - Application Factory
Creates and configures the Flask application with all extensions
"""

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from backend.config import get_config
from backend.api import register_blueprints
from backend.socket_handlers import register_socket_handlers
from backend.utils.logger import setup_logging


# Global SocketIO instance
socketio = SocketIO()


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern
    Creates and configures the Flask application
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    config.init_app(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    CORS(app)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        ping_timeout=app.config['SOCKETIO_PING_TIMEOUT'],
        ping_interval=app.config['SOCKETIO_PING_INTERVAL']
    )
    
    # Register blueprints (API routes)
    register_blueprints(app)
    
    # Register socket handlers
    register_socket_handlers(socketio)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log startup
    app.logger.info(f"AutoPilot IDE v{app.config['VERSION']} initialized")
    app.logger.info(f"Environment: {config_name or 'development'}")
    
    return app


def register_error_handlers(app: Flask):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        return {'error': 'An unexpected error occurred'}, 500
