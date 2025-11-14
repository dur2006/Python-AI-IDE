"""
Themes API Blueprint
Handles theme management endpoints
"""

from flask import Blueprint, jsonify, request
from backend.services.appdata_manager import get_appdata_manager
import logging

logger = logging.getLogger(__name__)

themes_bp = Blueprint('themes', __name__, url_prefix='/api/themes')


@themes_bp.route('', methods=['GET'])
def get_themes():
    """Get all themes"""
    try:
        appdata = get_appdata_manager()
        themes = appdata.get_themes()
        return jsonify(themes), 200
    except Exception as e:
        logger.error(f"Error getting themes: {e}")
        return jsonify({'error': str(e)}), 500


@themes_bp.route('/active', methods=['GET'])
def get_active_theme():
    """Get currently active theme"""
    try:
        appdata = get_appdata_manager()
        theme = appdata.get_active_theme()
        
        if theme:
            return jsonify(theme), 200
        else:
            return jsonify({'error': 'No active theme found'}), 404
    except Exception as e:
        logger.error(f"Error getting active theme: {e}")
        return jsonify({'error': str(e)}), 500


@themes_bp.route('/<theme_id>/activate', methods=['POST'])
def activate_theme(theme_id):
    """Activate a theme"""
    try:
        appdata = get_appdata_manager()
        success = appdata.set_active_theme(theme_id)
        
        if success:
            theme = appdata.get_theme(theme_id)
            return jsonify({
                'message': 'Theme activated successfully',
                'theme': theme
            }), 200
        else:
            return jsonify({'error': 'Theme not found'}), 404
    except Exception as e:
        logger.error(f"Error activating theme: {e}")
        return jsonify({'error': str(e)}), 500


@themes_bp.route('/<theme_id>', methods=['GET'])
def get_theme(theme_id):
    """Get specific theme by ID"""
    try:
        appdata = get_appdata_manager()
        theme = appdata.get_theme(theme_id)
        
        if theme:
            return jsonify(theme), 200
        else:
            return jsonify({'error': 'Theme not found'}), 404
    except Exception as e:
        logger.error(f"Error getting theme: {e}")
        return jsonify({'error': str(e)}), 500
