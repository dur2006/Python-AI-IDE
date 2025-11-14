"""
Layouts API Blueprint
Handles layout management endpoints
"""

from flask import Blueprint, jsonify, request
from backend.services.appdata_manager import get_appdata_manager
import logging

logger = logging.getLogger(__name__)

layouts_bp = Blueprint('layouts', __name__, url_prefix='/api/layouts')


@layouts_bp.route('', methods=['GET'])
def get_layouts():
    """Get all layouts"""
    try:
        appdata = get_appdata_manager()
        layouts = appdata.get_layouts()
        return jsonify(layouts), 200
    except Exception as e:
        logger.error(f"Error getting layouts: {e}")
        return jsonify({'error': str(e)}), 500


@layouts_bp.route('/active', methods=['GET'])
def get_active_layout():
    """Get currently active layout"""
    try:
        appdata = get_appdata_manager()
        layout = appdata.get_active_layout()
        
        if layout:
            return jsonify(layout), 200
        else:
            return jsonify({'error': 'No active layout found'}), 404
    except Exception as e:
        logger.error(f"Error getting active layout: {e}")
        return jsonify({'error': str(e)}), 500


@layouts_bp.route('/<layout_id>/activate', methods=['POST'])
def activate_layout(layout_id):
    """Activate a layout"""
    try:
        appdata = get_appdata_manager()
        success = appdata.set_active_layout(layout_id)
        
        if success:
            layout = appdata.get_layout(layout_id)
            return jsonify({
                'message': 'Layout activated successfully',
                'layout': layout
            }), 200
        else:
            return jsonify({'error': 'Layout not found'}), 404
    except Exception as e:
        logger.error(f"Error activating layout: {e}")
        return jsonify({'error': str(e)}), 500


@layouts_bp.route('/<layout_id>', methods=['GET'])
def get_layout(layout_id):
    """Get specific layout by ID"""
    try:
        appdata = get_appdata_manager()
        layout = appdata.get_layout(layout_id)
        
        if layout:
            return jsonify(layout), 200
        else:
            return jsonify({'error': 'Layout not found'}), 404
    except Exception as e:
        logger.error(f"Error getting layout: {e}")
        return jsonify({'error': str(e)}), 500


@layouts_bp.route('/<layout_id>', methods=['PUT'])
def save_layout(layout_id):
    """Save layout configuration"""
    try:
        data = request.get_json()
        
        if not data or 'config' not in data:
            return jsonify({'error': 'Layout config is required'}), 400
        
        appdata = get_appdata_manager()
        layout = appdata.save_layout(layout_id, data['config'])
        
        if layout:
            return jsonify({
                'message': 'Layout saved successfully',
                'layout': layout
            }), 200
        else:
            return jsonify({'error': 'Layout not found'}), 404
    except Exception as e:
        logger.error(f"Error saving layout: {e}")
        return jsonify({'error': str(e)}), 500
