"""
API Blueprint Registration
Registers all API blueprints with the Flask application
"""

from flask import Flask, Blueprint, jsonify

from backend.api.extensions import extensions_bp
from backend.api.projects import projects_bp
from backend.api.files import files_bp
from backend.api.terminal import terminal_bp
from backend.api.themes import themes_bp
from backend.api.layouts import layouts_bp
from backend.api.settings import settings_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    
    # Create main API blueprint
    api = Blueprint('api', __name__, url_prefix='/api')
    
    # Register sub-blueprints
    api.register_blueprint(extensions_bp, url_prefix='/extensions')
    api.register_blueprint(projects_bp, url_prefix='/projects')
    api.register_blueprint(files_bp, url_prefix='/files')
    api.register_blueprint(terminal_bp, url_prefix='/terminal')
    api.register_blueprint(themes_bp, url_prefix='/themes')
    api.register_blueprint(layouts_bp, url_prefix='/layouts')
    api.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Health check endpoint
    @api.route('/health', methods=['GET'])
    def health_check():
        """API health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': app.config.get('VERSION', '1.0.0'),
            'service': 'AutoPilot IDE API'
        })
    
    # AppData status endpoint
    @api.route('/appdata/status', methods=['GET'])
    def appdata_status():
        """Get AppData manager status"""
        try:
            from backend.services.appdata_manager import get_appdata_manager
            appdata = get_appdata_manager()
            status = appdata.get_status()
            return jsonify(status), 200
        except Exception as e:
            app.logger.error(f"Error getting AppData status: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Register main API blueprint
    app.register_blueprint(api)
    
    # Root route - serve frontend
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory('../static', 'index.html')
    
    app.logger.info("[OK] API blueprints registered successfully")
    app.logger.info("   - Extensions API: /api/extensions")
    app.logger.info("   - Projects API: /api/projects")
    app.logger.info("   - Files API: /api/files")
    app.logger.info("   - Terminal API: /api/terminal")
    app.logger.info("   - Themes API: /api/themes")
    app.logger.info("   - Layouts API: /api/layouts")
    app.logger.info("   - Settings API: /api/settings")
    app.logger.info("   - AppData Status: /api/appdata/status")
