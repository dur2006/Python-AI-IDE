"""
Layouts API Blueprint
Handles layout management with comprehensive validation and error handling
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.appdata_manager import get_appdata_manager
from backend.utils.validators import Validator, require_json

layouts_bp = Blueprint('layouts', __name__, url_prefix='/api/layouts')


@layouts_bp.route('', methods=['GET'])
def get_layouts() -> tuple[Dict[str, Any], int]:
    """
    Get all available layouts
    
    Returns:
        JSON response with list of layouts and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        layouts = appdata.get_layouts()
        
        return jsonify({
            'status': 'success',
            'data': layouts,
            'count': len(layouts) if isinstance(layouts, list) else 0
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting layouts: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch layouts',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('/active', methods=['GET'])
def get_active_layout() -> tuple[Dict[str, Any], int]:
    """
    Get currently active layout
    
    Returns:
        JSON response with active layout data and HTTP status code
    """
    try:
        appdata = get_appdata_manager()
        layout = appdata.get_active_layout()
        
        if layout:
            return jsonify({
                'status': 'success',
                'data': layout
            }), 200
        else:
            current_app.logger.warning("No active layout found")
            return jsonify({
                'status': 'error',
                'error': 'No active layout found'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting active layout: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch active layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('/<layout_id>/activate', methods=['POST'])
def activate_layout(layout_id: str) -> tuple[Dict[str, Any], int]:
    """
    Activate a layout
    
    Args:
        layout_id: Unique layout identifier
        
    Returns:
        JSON response with activated layout data and HTTP status code
    """
    # Validate layout ID
    is_valid, error_msg = Validator.validate_id(layout_id, "Layout ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid layout ID: {layout_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        success = appdata.set_active_layout(layout_id)
        
        if success:
            layout = appdata.get_layout(layout_id)
            current_app.logger.info(f"Layout activated successfully: {layout_id}")
            return jsonify({
                'status': 'success',
                'data': layout,
                'message': 'Layout activated successfully'
            }), 200
        else:
            current_app.logger.warning(f"Layout not found: {layout_id}")
            return jsonify({
                'status': 'error',
                'error': 'Layout not found'
            }), 404
    except ValueError as e:
        current_app.logger.warning(f"Invalid layout activation request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error activating layout {layout_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to activate layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('/<layout_id>', methods=['GET'])
def get_layout(layout_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get specific layout by ID
    
    Args:
        layout_id: Unique layout identifier
        
    Returns:
        JSON response with layout data and HTTP status code
    """
    # Validate layout ID
    is_valid, error_msg = Validator.validate_id(layout_id, "Layout ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid layout ID: {layout_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        layout = appdata.get_layout(layout_id)
        
        if layout:
            return jsonify({
                'status': 'success',
                'data': layout
            }), 200
        else:
            current_app.logger.info(f"Layout not found: {layout_id}")
            return jsonify({
                'status': 'error',
                'error': 'Layout not found'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting layout {layout_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('/<layout_id>', methods=['PUT'])
@require_json('config')
def save_layout(layout_id: str) -> tuple[Dict[str, Any], int]:
    """
    Save layout configuration
    
    Args:
        layout_id: Unique layout identifier
        
    Required JSON fields:
        - config: Layout configuration object
        
    Returns:
        JSON response with saved layout data and HTTP status code
    """
    # Validate layout ID
    is_valid, error_msg = Validator.validate_id(layout_id, "Layout ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        data = request.get_json()
        config = data.get('config')
        
        # Validate config is a dict
        if not isinstance(config, dict):
            return jsonify({
                'status': 'error',
                'error': 'Layout config must be an object',
                'field': 'config'
            }), 400
        
        appdata = get_appdata_manager()
        layout = appdata.save_layout(layout_id, config)
        
        if layout:
            current_app.logger.info(f"Layout saved successfully: {layout_id}")
            return jsonify({
                'status': 'success',
                'data': layout,
                'message': 'Layout saved successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Layout not found'
            }), 404
    except ValueError as e:
        current_app.logger.warning(f"Invalid layout save request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error saving layout {layout_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to save layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('', methods=['POST'])
@require_json('name', 'config')
def create_layout() -> tuple[Dict[str, Any], int]:
    """
    Create a custom layout
    
    Required JSON fields:
        - name: Layout name
        - config: Layout configuration object
        
    Returns:
        JSON response with created layout data and HTTP status code
    """
    try:
        data = request.get_json()
        
        # Sanitize and validate name
        name = Validator.sanitize_string(data.get('name', ''), max_length=100)
        is_valid, error_msg = Validator.validate_project_name(name)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'error': error_msg,
                'field': 'name'
            }), 400
        
        # Validate config
        config = data.get('config')
        if not isinstance(config, dict):
            return jsonify({
                'status': 'error',
                'error': 'Layout config must be an object',
                'field': 'config'
            }), 400
        
        appdata = get_appdata_manager()
        layout = appdata.create_layout(name, config)
        
        if layout:
            current_app.logger.info(f"Layout created successfully: {name}")
            return jsonify({
                'status': 'success',
                'data': layout,
                'message': 'Layout created successfully'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to create layout'
            }), 500
    except ValueError as e:
        current_app.logger.warning(f"Invalid layout creation request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating layout: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to create layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@layouts_bp.route('/<layout_id>', methods=['DELETE'])
def delete_layout(layout_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a custom layout
    
    Args:
        layout_id: Unique layout identifier
        
    Returns:
        JSON response with deletion status and HTTP status code
    """
    # Validate layout ID
    is_valid, error_msg = Validator.validate_id(layout_id, "Layout ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        appdata = get_appdata_manager()
        success = appdata.delete_layout(layout_id)
        
        if success:
            current_app.logger.info(f"Layout deleted successfully: {layout_id}")
            return jsonify({
                'status': 'success',
                'message': 'Layout deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Layout not found or cannot be deleted (system layout)'
            }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied deleting layout {layout_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Cannot delete system layouts'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error deleting layout {layout_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete layout',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
