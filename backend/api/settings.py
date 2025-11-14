"""
Settings API Blueprint
Handles settings management endpoints
"""

from flask import Blueprint, jsonify, request
from backend.services.appdata_manager import get_appdata_manager
import logging

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get all settings"""
    try:
        appdata = get_appdata_manager()
        settings = appdata.get_settings()
        return jsonify(settings), 200
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/<key>', methods=['GET'])
def get_setting(key):
    """Get specific setting by key"""
    try:
        appdata = get_appdata_manager()
        value = appdata.get_setting(key)
        
        if value is not None:
            return jsonify({key: value}), 200
        else:
            return jsonify({'error': 'Setting not found'}), 404
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/<key>', methods=['PUT'])
def update_setting(key):
    """Update specific setting"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({'error': 'Value is required'}), 400
        
        appdata = get_appdata_manager()
        success = appdata.set_setting(key, data['value'])
        
        if success:
            return jsonify({
                'message': 'Setting updated successfully',
                'key': key,
                'value': data['value']
            }), 200
        else:
            return jsonify({'error': 'Failed to update setting'}), 500
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        return jsonify({'error': str(e)}), 500


@settings_bp.route('', methods=['PUT'])
def update_settings():
    """Update multiple settings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Settings data is required'}), 400
        
        appdata = get_appdata_manager()
        settings = appdata.update_settings(data)
        
        return jsonify({
            'message': 'Settings updated successfully',
            'settings': settings
        }), 200
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({'error': str(e)}), 500
