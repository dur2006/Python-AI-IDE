"""
Themes API Blueprint
Handles theme management with comprehensive validation and error handling
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.appdata_manager import get_appdata_manager
from backend.utils.validators import Validator

themes_bp = Blueprint('themes', __name__, url_prefix='/api/themes')


@themes_bp.route('', methods=['GET'])
def get_themes() -> tuple[Dict[str, Any], int]:
    """
    Get all available themes
    
    Returns:
        JSON response with list of themes and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        themes = appdata.get_themes()
        
        return jsonify({
            'status': 'success',
            'data': themes,
            'count': len(themes) if isinstance(themes, list) else 0
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting themes: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch themes',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('/active', methods=['GET'])
def get_active_theme() -> tuple[Dict[str, Any], int]:
    """
    Get currently active theme
    
    Returns:
        JSON response with active theme data and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        theme = appdata.get_active_theme()
        
        if theme:
            return jsonify({
                'status': 'success',
                'data': theme
            }), 200
        else:
            current_app.logger.warning("No active theme found")
            return jsonify({
                'status': 'error',
                'error': 'No active theme found'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting active theme: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch active theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('/<theme_id>/activate', methods=['POST'])
def activate_theme(theme_id: str) -> tuple[Dict[str, Any], int]:
    """
    Activate a theme
    
    Args:
        theme_id: Unique theme identifier
        
    Returns:
        JSON response with activated theme data and HTTP status code
    """
    # Validate theme ID
    is_valid, error_msg = Validator.validate_id(theme_id, "Theme ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid theme ID: {theme_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        success = appdata.set_active_theme(theme_id)
        
        if success:
            theme = appdata.get_theme(theme_id)
            current_app.logger.info(f"Theme activated successfully: {theme_id}")
            return jsonify({
                'status': 'success',
                'data': theme,
                'message': 'Theme activated successfully'
            }), 200
        else:
            current_app.logger.warning(f"Theme not found: {theme_id}")
            return jsonify({
                'status': 'error',
                'error': 'Theme not found'
            }), 404
    except ValueError as e:
        current_app.logger.warning(f"Invalid theme activation request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error activating theme {theme_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to activate theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('/<theme_id>', methods=['GET'])
def get_theme(theme_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get specific theme by ID
    
    Args:
        theme_id: Unique theme identifier
        
    Returns:
        JSON response with theme data and HTTP status code
    """
    # Validate theme ID
    is_valid, error_msg = Validator.validate_id(theme_id, "Theme ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid theme ID: {theme_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        theme = appdata.get_theme(theme_id)
        
        if theme:
            return jsonify({
                'status': 'success',
                'data': theme
            }), 200
        else:
            current_app.logger.info(f"Theme not found: {theme_id}")
            return jsonify({
                'status': 'error',
                'error': 'Theme not found'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting theme {theme_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('/<theme_id>', methods=['PUT'])
def update_theme(theme_id: str) -> tuple[Dict[str, Any], int]:
    """
    Update theme settings
    
    Args:
        theme_id: Unique theme identifier
        
    Optional JSON fields:
        - name: Theme name
        - colors: Color scheme object
        - settings: Theme-specific settings
        
    Returns:
        JSON response with updated theme data and HTTP status code
    """
    # Validate theme ID
    is_valid, error_msg = Validator.validate_id(theme_id, "Theme ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                'status': 'error',
                'error': 'Invalid JSON in request body'
            }), 400
        
        # Sanitize name if provided
        if 'name' in data:
            data['name'] = Validator.sanitize_string(data['name'], max_length=100)
        
        appdata = get_appdata_manager()
        theme = appdata.update_theme(theme_id, data)
        
        if theme:
            current_app.logger.info(f"Theme updated successfully: {theme_id}")
            return jsonify({
                'status': 'success',
                'data': theme,
                'message': 'Theme updated successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Theme not found'
            }), 404
    except ValueError as e:
        current_app.logger.warning(f"Invalid theme update request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error updating theme {theme_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to update theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('', methods=['POST'])
def create_theme() -> tuple[Dict[str, Any], int]:
    """
    Create a custom theme
    
    Required JSON fields:
        - name: Theme name
        - colors: Color scheme object
        
    Optional JSON fields:
        - settings: Theme-specific settings
        
    Returns:
        JSON response with created theme data and HTTP status code
    """
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                'status': 'error',
                'error': 'Invalid JSON in request body'
            }), 400
        
        # Validate required fields
        if 'name' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Theme name is required',
                'field': 'name'
            }), 400
        
        if 'colors' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Theme colors are required',
                'field': 'colors'
            }), 400
        
        # Sanitize name
        data['name'] = Validator.sanitize_string(data['name'], max_length=100)
        
        appdata = get_appdata_manager()
        theme = appdata.create_theme(data)
        
        if theme:
            current_app.logger.info(f"Theme created successfully: {data['name']}")
            return jsonify({
                'status': 'success',
                'data': theme,
                'message': 'Theme created successfully'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to create theme'
            }), 500
    except ValueError as e:
        current_app.logger.warning(f"Invalid theme creation request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating theme: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to create theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@themes_bp.route('/<theme_id>', methods=['DELETE'])
def delete_theme(theme_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a custom theme
    
    Args:
        theme_id: Unique theme identifier
        
    Returns:
        JSON response with deletion status and HTTP status code
    """
    # Validate theme ID
    is_valid, error_msg = Validator.validate_id(theme_id, "Theme ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        success = appdata.delete_theme(theme_id)
        
        if success:
            current_app.logger.info(f"Theme deleted successfully: {theme_id}")
            return jsonify({
                'status': 'success',
                'message': 'Theme deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Theme not found or cannot be deleted (system theme)'
            }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied deleting theme {theme_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Cannot delete system themes'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error deleting theme {theme_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete theme',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
