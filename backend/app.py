"""
Flask Application Factory
Creates and configures the Flask application with all necessary components
"""

import os
from pathlib import Path
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS

from backend.config import config
from backend.utils.logger import setup_logging
from backend.services.appdata_manager import get_appdata_manager

# Initialize SocketIO with threading mode (Python 3.13 compatible)
# Using async_mode='threading' instead of 'eventlet' for Python 3.13+ compatibility
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=False
)


def _initialize_appdata(app):
    """Initialize AppData Manager and verify data integrity"""
    try:
        app.logger.info("Initializing AppData Manager...")
        
        # Get AppData Manager instance
        appdata = get_appdata_manager()
        
        # Initialize data files with defaults if they don't exist
        appdata.initialize()
        
        # Log initialization success
        app.logger.info("[OK] AppData Manager initialized successfully")
        app.logger.info(f"   - Data directory: {appdata.data_dir}")
        app.logger.info(f"   - Projects: {len(appdata.get_projects())}")
        app.logger.info(f"   - Themes: {len(appdata.get_themes())}")
        app.logger.info(f"   - Extensions: {len(appdata.get_extensions())}")
        app.logger.info(f"   - Layouts: {len(appdata.get_layouts())}")
        app.logger.info(f"   - Settings: {len(appdata.get_settings())}")
        
    except Exception as e:
        app.logger.error(f"Failed to initialize AppData Manager: {e}")
        raise


def create_app(config_name='development'):
    """
    Application factory function
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    # Determine base directory (project root)
    base_dir = Path(__file__).parent.parent
    
    # Create Flask app with static folder pointing to project root
    app = Flask(__name__, 
                static_folder=str(base_dir),
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    app.logger.info(f"Starting application in {config_name} mode")
    app.logger.info(f"SocketIO async mode: {socketio.async_mode}")
    
    # Initialize extensions
    CORS(app)
    socketio.init_app(app)
    
    # Initialize AppData Manager
    with app.app_context():
        _initialize_appdata(app)
    
    # Register blueprints
    from backend.api import register_blueprints
    register_blueprints(app)
    
    # Register socket handlers
    from backend.socket_handlers import register_socket_handlers
    register_socket_handlers(socketio, app)
    
    # Serve index.html at root (index.html is in project root, not static folder)
    @app.route('/')
    def index():
        """Serve the main index.html file"""
        return send_from_directory(str(base_dir), 'index.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        """Health check endpoint"""
        return {'status': 'ok', 'message': 'AutoPilot IDE is running'}
    
    return app
