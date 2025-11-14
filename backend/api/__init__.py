"""
API Blueprint Registration
Registers all API blueprints with the Flask application
"""

from flask import Flask, Blueprint, jsonify

from backend.api.extensions import extensions_bp
from backend.api.projects import projects_bp
from backend.api.files import files_bp
from backend.api.terminal import terminal_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    
    # Create main API blueprint
    api = Blueprint('api', __name__, url_prefix='/api')
    
    # Register sub-blueprints
    api.register_blueprint(extensions_bp, url_prefix='/extensions')
    api.register_blueprint(projects_bp, url_prefix='/projects')
    api.register_blueprint(files_bp, url_prefix='/files')
    api.register_blueprint(terminal_bp, url_prefix='/terminal')
    
    # Health check endpoint
    @api.route('/health', methods=['GET'])
    def health_check():
        """API health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': app.config['VERSION'],
            'service': 'AutoPilot IDE API'
        })
    
    # Register main API blueprint
    app.register_blueprint(api)
    
    # Root route - serve frontend
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory('../static', 'index.html')
    
    app.logger.info("API blueprints registered successfully")
