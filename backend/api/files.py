"""
Files API Blueprint
Handles file operations (read, write, create, delete)
"""

from flask import Blueprint, jsonify, request, current_app
from backend.services.file_service import FileService

files_bp = Blueprint('files', __name__)
file_service = FileService()


@files_bp.route('/<project_id>/<path:file_path>', methods=['GET'])
def get_file(project_id, file_path):
    """Get file content"""
    try:
        content = file_service.read_file(project_id, file_path)
        if content is not None:
            return jsonify({
                'path': file_path,
                'content': content
            }), 200
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error reading file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['PUT'])
def update_file(project_id, file_path):
    """Update file content"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        success = file_service.write_file(project_id, file_path, content)
        if success:
            return jsonify({
                'status': 'success',
                'path': file_path
            }), 200
        return jsonify({'error': 'Failed to write file'}), 500
    except Exception as e:
        current_app.logger.error(f"Error writing file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['POST'])
def create_file(project_id, file_path):
    """Create a new file"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        success = file_service.create_file(project_id, file_path, content)
        if success:
            return jsonify({
                'status': 'success',
                'path': file_path
            }), 201
        return jsonify({'error': 'Failed to create file'}), 500
    except Exception as e:
        current_app.logger.error(f"Error creating file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['DELETE'])
def delete_file(project_id, file_path):
    """Delete a file"""
    try:
        success = file_service.delete_file(project_id, file_path)
        if success:
            return jsonify({'status': 'success'}), 200
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/<project_id>/tree', methods=['GET'])
def get_file_tree(project_id):
    """Get complete file tree for a project"""
    try:
        tree = file_service.get_file_tree(project_id)
        if tree is not None:
            return jsonify(tree), 200
        return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting file tree for {project_id}: {e}")
        return jsonify({'error': str(e)}), 500
