"""
Files API Blueprint
Handles file operations with comprehensive validation, error handling, and security
"""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from backend.services.file_service import FileService
from backend.utils.validators import Validator, require_json

files_bp = Blueprint('files', __name__)
file_service = FileService()


@files_bp.route('/<project_id>/<path:file_path>', methods=['GET'])
def get_file(project_id: str, file_path: str) -> tuple[Dict[str, Any], int]:
    """
    Get file content
    
    Args:
        project_id: Unique project identifier
        file_path: Path to file within project
        
    Returns:
        JSON response with file content and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid project ID: {project_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    # Validate file path
    is_valid, error_msg = Validator.validate_file_path(file_path)
    if not is_valid:
        current_app.logger.warning(f"Invalid file path: {file_path}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        content = file_service.read_file(project_id, file_path)
        
        if content is not None:
            return jsonify({
                'status': 'success',
                'data': {
                    'path': file_path,
                    'content': content
                }
            }), 200
        else:
            current_app.logger.info(f"File not found: {project_id}/{file_path}")
            return jsonify({
                'status': 'error',
                'error': 'File not found'
            }), 404
            
    except PermissionError as e:
        current_app.logger.error(f"Permission denied reading file {file_path}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to read file',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['PUT'])
@require_json('content')
def update_file(project_id: str, file_path: str) -> tuple[Dict[str, Any], int]:
    """
    Update file content
    
    Args:
        project_id: Unique project identifier
        file_path: Path to file within project
        
    Required JSON fields:
        - content: New file content (string)
        
    Returns:
        JSON response with update status and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    # Validate file path
    is_valid, error_msg = Validator.validate_file_path(file_path)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # Validate content length
        is_valid, error_msg = Validator.validate_content_length(content)
        if not is_valid:
            current_app.logger.warning(f"Content too large for file {file_path}")
            return jsonify({
                'status': 'error',
                'error': error_msg
            }), 400
        
        # Write file
        success = file_service.write_file(project_id, file_path, content)
        
        if success:
            current_app.logger.info(f"File updated successfully: {project_id}/{file_path}")
            return jsonify({
                'status': 'success',
                'data': {
                    'path': file_path
                },
                'message': 'File updated successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to write file'
            }), 500
            
    except PermissionError as e:
        current_app.logger.error(f"Permission denied writing file {file_path}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error writing file {file_path}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to write file',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['POST'])
@require_json()
def create_file(project_id: str, file_path: str) -> tuple[Dict[str, Any], int]:
    """
    Create a new file
    
    Args:
        project_id: Unique project identifier
        file_path: Path for new file within project
        
    Optional JSON fields:
        - content: Initial file content (default: empty string)
        
    Returns:
        JSON response with creation status and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    # Validate file path
    is_valid, error_msg = Validator.validate_file_path(file_path)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # Validate content length
        is_valid, error_msg = Validator.validate_content_length(content)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'error': error_msg
            }), 400
        
        # Create file
        success = file_service.create_file(project_id, file_path, content)
        
        if success:
            current_app.logger.info(f"File created successfully: {project_id}/{file_path}")
            return jsonify({
                'status': 'success',
                'data': {
                    'path': file_path
                },
                'message': 'File created successfully'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to create file. File may already exist.'
            }), 409
            
    except FileExistsError as e:
        current_app.logger.warning(f"File already exists: {file_path}")
        return jsonify({
            'status': 'error',
            'error': 'File already exists'
        }), 409
    except PermissionError as e:
        current_app.logger.error(f"Permission denied creating file {file_path}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error creating file {file_path}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to create file',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@files_bp.route('/<project_id>/<path:file_path>', methods=['DELETE'])
def delete_file(project_id: str, file_path: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a file
    
    Args:
        project_id: Unique project identifier
        file_path: Path to file within project
        
    Returns:
        JSON response with deletion status and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    # Validate file path
    is_valid, error_msg = Validator.validate_file_path(file_path)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        success = file_service.delete_file(project_id, file_path)
        
        if success:
            current_app.logger.info(f"File deleted successfully: {project_id}/{file_path}")
            return jsonify({
                'status': 'success',
                'message': 'File deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'File not found'
            }), 404
            
    except PermissionError as e:
        current_app.logger.error(f"Permission denied deleting file {file_path}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete file',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@files_bp.route('/<project_id>/tree', methods=['GET'])
def get_file_tree(project_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get complete file tree for a project
    
    Args:
        project_id: Unique project identifier
        
    Returns:
        JSON response with file tree and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        tree = file_service.get_file_tree(project_id)
        
        if tree is not None:
            return jsonify({
                'status': 'success',
                'data': tree
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Project not found'
            }), 404
            
    except PermissionError as e:
        current_app.logger.error(f"Permission denied accessing project {project_id}: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error getting file tree for {project_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to get file tree',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
