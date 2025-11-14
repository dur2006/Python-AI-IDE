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


def _initialize_appdata(app: Flask):
    """Initialize AppData Manager with default data"""
    try:
        from backend.services.appdata_manager import get_appdata_manager
        
        app.logger.info("Initializing AppData Manager...")
        appdata = get_appdata_manager()
        
        # Initialize data files
        success = appdata.initialize()
        
        if success:
            status = appdata.get_status()
            app.logger.info("✅ AppData Manager initialized successfully")
            app.logger.info(f"   - Data directory: {status['dataDir']}")
            app.logger.info(f"   - Projects: {status['projects']}")
            app.logger.info(f"   - Themes: {status['themes']}")
            app.logger.info(f"   - Extensions: {status['extensions']}")
            app.logger.info(f"   - Layouts: {status['layouts']}")
            app.logger.info(f"   - Settings: {status['settings']}")
        else:
            app.logger.error("❌ AppData Manager initialization failed")
            
    except Exception as e:
        app.logger.error(f"❌ Error initializing AppData Manager: {e}")


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
    
    # Initialize AppData Manager
    _initialize_appdata(app)
    
    # Register blueprints (API routes)
    register_blueprints(app)
    
    # Register socket handlers
    register_socket_handlers(socketio)
    
    # Register AppData socket handlers
    register_appdata_socket_handlers(socketio, app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log startup
    app.logger.info(f"🚀 AutoPilot IDE v{app.config['VERSION']} initialized")
    app.logger.info(f"   Environment: {config_name or 'development'}")
    
    return app


def register_appdata_socket_handlers(socketio: SocketIO, app: Flask):
    """Register Socket.IO handlers for AppData synchronization"""
    
    @socketio.on('appdata:sync')
    def handle_appdata_sync(data):
        """Handle AppData sync request"""
        try:
            from backend.services.appdata_manager import get_appdata_manager
            from flask_socketio import emit
            
            appdata = get_appdata_manager()
            data_type = data.get('type')
            
            if data_type == 'projects':
                emit('appdata:projects', appdata.get_projects())
            elif data_type == 'themes':
                emit('appdata:themes', appdata.get_themes())
            elif data_type == 'extensions':
                emit('appdata:extensions', appdata.get_extensions())
            elif data_type == 'layouts':
                emit('appdata:layouts', appdata.get_layouts())
            elif data_type == 'settings':
                emit('appdata:settings', appdata.get_settings())
            elif data_type == 'all':
                emit('appdata:all', {
                    'projects': appdata.get_projects(),
                    'themes': appdata.get_themes(),
                    'extensions': appdata.get_extensions(),
                    'layouts': appdata.get_layouts(),
                    'settings': appdata.get_settings()
                })
            else:
                emit('appdata:error', {'error': 'Invalid data type'})
                
        except Exception as e:
            app.logger.error(f"Error handling AppData sync: {e}")
            emit('appdata:error', {'error': str(e)})
    
    @socketio.on('appdata:update')
    def handle_appdata_update(data):
        """Handle AppData update notification"""
        try:
            from flask_socketio import emit
            
            # Broadcast update to all clients
            emit('appdata:updated', data, broadcast=True)
            
        except Exception as e:
            app.logger.error(f"Error handling AppData update: {e}")


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
