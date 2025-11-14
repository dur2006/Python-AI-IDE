"""
Extensions API Blueprint
Handles extension management with comprehensive validation and security
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.extension_service import ExtensionService
from backend.utils.validators import Validator

extensions_bp = Blueprint('extensions', __name__)
extension_service = ExtensionService()


@extensions_bp.route('', methods=['GET'])
def get_extensions() -> tuple[Dict[str, Any], int]:
    """
    Get all extensions (installed and available)
    
    Returns:
        JSON response with list of extensions and HTTP status code
    """
    try:
        extensions = extension_service.get_all_extensions()
        return jsonify({
            'status': 'success',
            'data': extensions,
            'count': len(extensions) if isinstance(extensions, list) else 0
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching extensions: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch extensions',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/<ext_id>', methods=['GET'])
def get_extension(ext_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific extension by ID
    
    Args:
        ext_id: Extension identifier (can be int or string)
        
    Returns:
        JSON response with extension data and HTTP status code
    """
    # Validate extension ID
    is_valid, error_msg = Validator.validate_id(ext_id, "Extension ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid extension ID: {ext_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        # Try to convert to int if it's numeric
        try:
            ext_id_int = int(ext_id)
            extension = extension_service.get_extension(ext_id_int)
        except ValueError:
            # If not numeric, use as string ID
            extension = extension_service.get_extension(ext_id)
        
        if extension:
            return jsonify({
                'status': 'success',
                'data': extension
            }), 200
        
        current_app.logger.info(f"Extension not found: {ext_id}")
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching extension {ext_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch extension',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/<ext_id>/toggle', methods=['POST'])
def toggle_extension(ext_id: str) -> tuple[Dict[str, Any], int]:
    """
    Toggle extension enabled/disabled status
    
    Args:
        ext_id: Extension identifier
        
    Returns:
        JSON response with updated extension data and HTTP status code
    """
    # Validate extension ID
    is_valid, error_msg = Validator.validate_id(ext_id, "Extension ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        # Try to convert to int if it's numeric
        try:
            ext_id_int = int(ext_id)
            extension = extension_service.toggle_extension(ext_id_int)
        except ValueError:
            extension = extension_service.toggle_extension(ext_id)
        
        if extension:
            current_app.logger.info(f"Extension toggled successfully: {ext_id}")
            return jsonify({
                'status': 'success',
                'data': extension,
                'message': 'Extension status toggled successfully'
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found'
        }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied toggling extension {ext_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied. Cannot modify system extensions.'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error toggling extension {ext_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to toggle extension',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/<ext_id>/install', methods=['POST'])
def install_extension(ext_id: str) -> tuple[Dict[str, Any], int]:
    """
    Install an extension
    
    Args:
        ext_id: Extension identifier
        
    Returns:
        JSON response with installed extension data and HTTP status code
    """
    # Validate extension ID
    is_valid, error_msg = Validator.validate_id(ext_id, "Extension ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        # Try to convert to int if it's numeric
        try:
            ext_id_int = int(ext_id)
            extension = extension_service.install_extension(ext_id_int)
        except ValueError:
            extension = extension_service.install_extension(ext_id)
        
        if extension:
            current_app.logger.info(f"Extension installed successfully: {ext_id}")
            return jsonify({
                'status': 'success',
                'data': extension,
                'message': 'Extension installed successfully'
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found or already installed'
        }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied installing extension {ext_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied. Insufficient privileges to install extensions.'
        }), 403
    except ValueError as e:
        current_app.logger.warning(f"Invalid extension installation request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error installing extension {ext_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to install extension',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/<ext_id>/uninstall', methods=['POST'])
def uninstall_extension(ext_id: str) -> tuple[Dict[str, Any], int]:
    """
    Uninstall an extension
    
    Args:
        ext_id: Extension identifier
        
    Returns:
        JSON response with uninstall status and HTTP status code
    """
    # Validate extension ID
    is_valid, error_msg = Validator.validate_id(ext_id, "Extension ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        # Try to convert to int if it's numeric
        try:
            ext_id_int = int(ext_id)
            success = extension_service.uninstall_extension(ext_id_int)
        except ValueError:
            success = extension_service.uninstall_extension(ext_id)
        
        if success:
            current_app.logger.info(f"Extension uninstalled successfully: {ext_id}")
            return jsonify({
                'status': 'success',
                'message': 'Extension uninstalled successfully'
            }), 200
        
        return jsonify({
            'status': 'error',
            'error': 'Extension not found or not installed'
        }), 404
    except PermissionError as e:
        current_app.logger.error(f"Permission denied uninstalling extension {ext_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied. Cannot uninstall system extensions.'
        }), 403
    except ValueError as e:
        current_app.logger.warning(f"Invalid extension uninstall request: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error uninstalling extension {ext_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to uninstall extension',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@extensions_bp.route('/search', methods=['GET'])
def search_extensions() -> tuple[Dict[str, Any], int]:
    """
    Search for extensions by query
    
    Query parameters:
        - q: Search query string
        - category: Filter by category
        - installed: Filter by installation status (true/false)
        
    Returns:
        JSON response with search results and HTTP status code
    """
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        installed_filter = request.args.get('installed', '').lower()
        
        # Sanitize inputs
        if query:
            query = Validator.sanitize_string(query, max_length=100)
        if category:
            category = Validator.sanitize_string(category, max_length=50)
        
        # Convert installed filter to boolean
        installed = None
        if installed_filter in ['true', '1', 'yes']:
            installed = True
        elif installed_filter in ['false', '0', 'no']:
            installed = False
        
        # Search extensions
        results = extension_service.search_extensions(
            query=query if query else None,
            category=category if category else None,
            installed=installed
        )
        
        return jsonify({
            'status': 'success',
            'data': results,
            'count': len(results) if isinstance(results, list) else 0,
            'query': {
                'q': query,
                'category': category,
                'installed': installed
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error searching extensions: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to search extensions',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
