"""
Settings API Blueprint
Handles settings management with comprehensive validation and security
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.appdata_manager import get_appdata_manager
from backend.utils.validators import Validator, require_json

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('', methods=['GET'])
def get_settings() -> tuple[Dict[str, Any], int]:
    """
    Get all settings
    
    Returns:
        JSON response with all settings and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        settings = appdata.get_settings()
        
        return jsonify({
            'status': 'success',
            'data': settings,
            'count': len(settings) if isinstance(settings, dict) else 0
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch settings',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@settings_bp.route('/<key>', methods=['GET'])
def get_setting(key: str) -> tuple[Dict[str, Any], int]:
    """
    Get specific setting by key
    
    Args:
        key: Setting key identifier
        
    Returns:
        JSON response with setting value and HTTP status code
    """
    # Validate key
    key = Validator.sanitize_string(key, max_length=100)
    if not key:
        return jsonify({
            'status': 'error',
            'error': 'Setting key is required'
        }), 400
    
    try:
        appdata = get_appdata_manager()
        value = appdata.get_setting(key)
        
        if value is not None:
            return jsonify({
                'status': 'success',
                'data': {
                    'key': key,
                    'value': value
                }
            }), 200
        else:
            current_app.logger.info(f"Setting not found: {key}")
            return jsonify({
                'status': 'error',
                'error': 'Setting not found'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting setting {key}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch setting',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@settings_bp.route('/<key>', methods=['PUT'])
@require_json('value')
def update_setting(key: str) -> tuple[Dict[str, Any], int]:
    """
    Update specific setting
    
    Args:
        key: Setting key identifier
        
    Required JSON fields:
        - value: New setting value (any JSON-serializable type)
        
    Returns:
        JSON response with updated setting and HTTP status code
    """
    # Validate and sanitize key
    key = Validator.sanitize_string(key, max_length=100)
    if not key:
        return jsonify({
            'status': 'error',
            'error': 'Setting key is required'
        }), 400
    
    # Check for protected settings
    protected_keys = ['SECRET_KEY', 'DATABASE_URL', 'API_KEY']
    if key.upper() in protected_keys:
        current_app.logger.warning(f"Attempt to modify protected setting: {key}")
        return jsonify({
            'status': 'error',
            'error': 'Cannot modify protected settings via API'
        }), 403
    
    try:
        data = request.get_json()
        value = data.get('value')
        
        # Validate value is JSON-serializable
        try:
            import json
            json.dumps(value)
        except (TypeError, ValueError) as e:
            return jsonify({
                'status': 'error',
                'error': 'Setting value must be JSON-serializable',
                'field': 'value'
            }), 400
        
        appdata = get_appdata_manager()
        success = appdata.set_setting(key, value)
        
        if success:
            current_app.logger.info(f"Setting updated successfully: {key}")
            return jsonify({
                'status': 'success',
                'data': {
                    'key': key,
                    'value': value
                },
                'message': 'Setting updated successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to update setting'
            }), 500
    except ValueError as e:
        current_app.logger.warning(f"Invalid setting update request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error updating setting {key}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to update setting',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@settings_bp.route('', methods=['PUT'])
def update_settings() -> tuple[Dict[str, Any], int]:
    """
    Update multiple settings at once
    
    Required JSON body:
        Object with key-value pairs of settings to update
        
    Returns:
        JSON response with updated settings and HTTP status code
    """
    try:
        data = request.get_json(silent=True)
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'status': 'error',
                'error': 'Settings data must be a JSON object'
            }), 400
        
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'At least one setting must be provided'
            }), 400
        
        # Check for protected settings
        protected_keys = ['SECRET_KEY', 'DATABASE_URL', 'API_KEY']
        for key in data.keys():
            if key.upper() in protected_keys:
                current_app.logger.warning(f"Attempt to modify protected setting: {key}")
                return jsonify({
                    'status': 'error',
                    'error': f'Cannot modify protected setting: {key}'
                }), 403
        
        # Sanitize all keys
        sanitized_data = {}
        for key, value in data.items():
            sanitized_key = Validator.sanitize_string(key, max_length=100)
            if sanitized_key:
                # Validate value is JSON-serializable
                try:
                    import json
                    json.dumps(value)
                    sanitized_data[sanitized_key] = value
                except (TypeError, ValueError):
                    return jsonify({
                        'status': 'error',
                        'error': f'Value for key "{key}" must be JSON-serializable'
                    }), 400
        
        if not sanitized_data:
            return jsonify({
                'status': 'error',
                'error': 'No valid settings provided'
            }), 400
        
        appdata = get_appdata_manager()
        settings = appdata.update_settings(sanitized_data)
        
        current_app.logger.info(f"Multiple settings updated successfully: {list(sanitized_data.keys())}")
        return jsonify({
            'status': 'success',
            'data': settings,
            'message': f'{len(sanitized_data)} settings updated successfully'
        }), 200
    except ValueError as e:
        current_app.logger.warning(f"Invalid settings update request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error updating settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to update settings',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@settings_bp.route('/<key>', methods=['DELETE'])
def delete_setting(key: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a custom setting (cannot delete system settings)
    
    Args:
        key: Setting key identifier
        
    Returns:
        JSON response with deletion status and HTTP status code
    """
    # Validate and sanitize key
    key = Validator.sanitize_string(key, max_length=100)
    if not key:
        return jsonify({
            'status': 'error',
            'error': 'Setting key is required'
        }), 400
    
    # Check for protected settings
    protected_keys = ['SECRET_KEY', 'DATABASE_URL', 'API_KEY', 'LOG_LEVEL', 'DEBUG']
    if key.upper() in protected_keys:
        current_app.logger.warning(f"Attempt to delete protected setting: {key}")
        return jsonify({
            'status': 'error',
            'error': 'Cannot delete system settings'
        }), 403
    
    try:
        appdata = get_appdata_manager()
        success = appdata.delete_setting(key)
        
        if success:
            current_app.logger.info(f"Setting deleted successfully: {key}")
            return jsonify({
                'status': 'success',
                'message': 'Setting deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Setting not found or cannot be deleted'
            }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied deleting setting {key}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Cannot delete system settings'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error deleting setting {key}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete setting',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@settings_bp.route('/reset', methods=['POST'])
def reset_settings() -> tuple[Dict[str, Any], int]:
    """
    Reset all settings to default values
    
    Returns:
        JSON response with reset status and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        settings = appdata.reset_settings()
        
        current_app.logger.info("Settings reset to defaults successfully")
        return jsonify({
            'status': 'success',
            'data': settings,
            'message': 'Settings reset to defaults successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error resetting settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to reset settings',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
