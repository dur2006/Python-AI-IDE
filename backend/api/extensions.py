"""
Extensions API Blueprint
Handles extension management endpoints
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.appdata_manager import get_appdata_manager
from backend.utils.validators import Validator

extensions_bp = Blueprint('extensions', __name__)
appdata = get_appdata_manager()


@extensions_bp.route('', methods=['GET'])
def get_extensions() -> tuple[Dict[str, Any], int]:
    """
    Get all extensions
    
    Returns:
        JSON response with list of extensions and HTTP status code
    """
    try:
        extensions = appdata.get_extensions()
        return jsonify({
            'status': 'success',
            'data': extensions,
            'count': len(extensions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching extensions: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch extensions',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/installed', methods=['GET'])
def get_installed_extensions() -> tuple[Dict[str, Any], int]:
    """
    Get installed extensions
    
    Returns:
        JSON response with list of installed extensions
    """
    try:
        extensions = appdata.get_installed_extensions()
        return jsonify({
            'status': 'success',
            'data': extensions,
            'count': len(extensions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching installed extensions: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch installed extensions'
        }), 500


@extensions_bp.route('/available', methods=['GET'])
def get_available_extensions() -> tuple[Dict[str, Any], int]:
    """
    Get available (not installed) extensions
    
    Returns:
        JSON response with list of available extensions
    """
    try:
        extensions = appdata.get_available_extensions()
        return jsonify({
            'status': 'success',
            'data': extensions,
            'count': len(extensions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching available extensions: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch available extensions'
        }), 500


@extensions_bp.route('/<int:extension_id>', methods=['GET'])
def get_extension(extension_id: int) -> tuple[Dict[str, Any], int]:
    """
    Get a specific extension by ID
    
    Args:
        extension_id: Extension ID
        
    Returns:
        JSON response with extension data
    """
    try:
        extension = appdata.get_extension(extension_id)
        if extension:
            return jsonify({
                'status': 'success',
                'data': extension
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching extension {extension_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch extension'
        }), 500


@extensions_bp.route('/<int:extension_id>/toggle', methods=['POST'])
def toggle_extension(extension_id: int) -> tuple[Dict[str, Any], int]:
    """
    Toggle extension enabled state
    
    Args:
        extension_id: Extension ID
        
    Returns:
        JSON response with updated extension data
    """
    try:
        extension = appdata.toggle_extension(extension_id)
        if extension:
            current_app.logger.info(f"Extension toggled: {extension_id}")
            return jsonify({
                'status': 'success',
                'data': extension,
                'message': f"Extension {'enabled' if extension['enabled'] else 'disabled'}"
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error toggling extension {extension_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to toggle extension'
        }), 500


@extensions_bp.route('/<int:extension_id>/install', methods=['POST'])
def install_extension(extension_id: int) -> tuple[Dict[str, Any], int]:
    """
    Install extension
    
    Args:
        extension_id: Extension ID
        
    Returns:
        JSON response with installation status
    """
    try:
        extension = appdata.install_extension(extension_id)
        if extension:
            current_app.logger.info(f"Extension installed: {extension_id}")
            return jsonify({
                'status': 'success',
                'data': extension,
                'message': 'Extension installed successfully'
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error installing extension {extension_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to install extension'
        }), 500


@extensions_bp.route('/<int:extension_id>/uninstall', methods=['POST'])
def uninstall_extension(extension_id: int) -> tuple[Dict[str, Any], int]:
    """
    Uninstall extension
    
    Args:
        extension_id: Extension ID
        
    Returns:
        JSON response with uninstallation status
    """
    try:
        success = appdata.uninstall_extension(extension_id)
        if success:
            current_app.logger.info(f"Extension uninstalled: {extension_id}")
            return jsonify({
                'status': 'success',
                'message': 'Extension uninstalled successfully'
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error uninstalling extension {extension_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to uninstall extension'
        }), 500
