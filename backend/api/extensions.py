"""
Extensions API Blueprint
Handles extension management endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from backend.services.extension_service import ExtensionService

extensions_bp = Blueprint('extensions', __name__)
extension_service = ExtensionService()


@extensions_bp.route('', methods=['GET'])
def get_extensions():
    """Get all extensions (installed and available)"""
    try:
        extensions = extension_service.get_all_extensions()
        return jsonify(extensions), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching extensions: {e}")
        return jsonify({'error': str(e)}), 500


@extensions_bp.route('/<int:ext_id>', methods=['GET'])
def get_extension(ext_id):
    """Get a specific extension by ID"""
    try:
        extension = extension_service.get_extension(ext_id)
        if extension:
            return jsonify(extension), 200
        return jsonify({'error': 'Extension not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching extension {ext_id}: {e}")
        return jsonify({'error': str(e)}), 500


@extensions_bp.route('/<int:ext_id>/toggle', methods=['POST'])
def toggle_extension(ext_id):
    """Toggle extension enabled/disabled status"""
    try:
        extension = extension_service.toggle_extension(ext_id)
        if extension:
            return jsonify({
                'status': 'success',
                'extension': extension
            }), 200
        return jsonify({'error': 'Extension not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error toggling extension {ext_id}: {e}")
        return jsonify({'error': str(e)}), 500


@extensions_bp.route('/<int:ext_id>/install', methods=['POST'])
def install_extension(ext_id):
    """Install an extension"""
    try:
        extension = extension_service.install_extension(ext_id)
        if extension:
            return jsonify({
                'status': 'success',
                'extension': extension
            }), 200
        return jsonify({'error': 'Extension not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error installing extension {ext_id}: {e}")
        return jsonify({'error': str(e)}), 500


@extensions_bp.route('/<int:ext_id>/uninstall', methods=['POST'])
def uninstall_extension(ext_id):
    """Uninstall an extension"""
    try:
        success = extension_service.uninstall_extension(ext_id)
        if success:
            return jsonify({'status': 'success'}), 200
        return jsonify({'error': 'Extension not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error uninstalling extension {ext_id}: {e}")
        return jsonify({'error': str(e)}), 500
