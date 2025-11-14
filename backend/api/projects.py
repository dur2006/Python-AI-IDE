"""
Projects API Blueprint
Handles project management endpoints with comprehensive validation and error handling
"""

from typing import Dict, Any, Optional
from flask import Blueprint, jsonify, request, current_app
from backend.services.project_service import ProjectService
from backend.utils.validators import Validator, require_json

projects_bp = Blueprint('projects', __name__)
project_service = ProjectService()


@projects_bp.route('', methods=['GET'])
def get_projects() -> tuple[Dict[str, Any], int]:
    """
    Get all projects
    
    Returns:
        JSON response with list of projects and HTTP status code
    """
    try:
        projects = project_service.get_all_projects()
        return jsonify({
            'status': 'success',
            'data': projects,
            'count': len(projects)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch projects',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get a specific project by ID
    
    Args:
        project_id: Unique project identifier
        
    Returns:
        JSON response with project data and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        current_app.logger.warning(f"Invalid project ID: {project_id}")
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        project = project_service.get_project(project_id)
        if project:
            return jsonify({
                'status': 'success',
                'data': project
            }), 200
        
        current_app.logger.info(f"Project not found: {project_id}")
        return jsonify({
            'status': 'error',
            'error': 'Project not found'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching project {project_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch project',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@projects_bp.route('', methods=['POST'])
@require_json('name')
def create_project() -> tuple[Dict[str, Any], int]:
    """
    Create a new project
    
    Required JSON fields:
        - name: Project name (string)
        
    Optional JSON fields:
        - type: Project type (default: 'Python')
        - path: Project path (string)
        
    Returns:
        JSON response with created project data and HTTP status code
    """
    try:
        data = request.get_json()
        
        # Extract and validate fields
        name = Validator.sanitize_string(data.get('name', ''))
        project_type = Validator.sanitize_string(data.get('type', 'Python'))
        path = data.get('path')
        
        # Validate project name
        is_valid, error_msg = Validator.validate_project_name(name)
        if not is_valid:
            current_app.logger.warning(f"Invalid project name: {name}")
            return jsonify({
                'status': 'error',
                'error': error_msg,
                'field': 'name'
            }), 400
        
        # Validate path if provided
        if path:
            path = Validator.sanitize_string(path, max_length=500)
            is_valid, error_msg = Validator.validate_file_path(path, allow_absolute=True)
            if not is_valid:
                current_app.logger.warning(f"Invalid project path: {path}")
                return jsonify({
                    'status': 'error',
                    'error': error_msg,
                    'field': 'path'
                }), 400
        
        # Create project
        project = project_service.create_project(name, project_type, path)
        
        if project:
            current_app.logger.info(f"Project created successfully: {name}")
            return jsonify({
                'status': 'success',
                'data': project,
                'message': 'Project created successfully'
            }), 201
        else:
            current_app.logger.error(f"Failed to create project: {name}")
            return jsonify({
                'status': 'error',
                'error': 'Failed to create project'
            }), 500
            
    except ValueError as e:
        current_app.logger.warning(f"Validation error creating project: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating project: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to create project',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@projects_bp.route('/<project_id>', methods=['PUT'])
@require_json()
def update_project(project_id: str) -> tuple[Dict[str, Any], int]:
    """
    Update an existing project
    
    Args:
        project_id: Unique project identifier
        
    Optional JSON fields:
        - name: New project name
        - type: New project type
        - path: New project path
        
    Returns:
        JSON response with updated project data and HTTP status code
    """
    # Validate project ID
    is_valid, error_msg = Validator.validate_id(project_id, "Project ID")
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': error_msg
        }), 400
    
    try:
        data = request.get_json()
        
        # Validate name if provided
        if 'name' in data:
            name = Validator.sanitize_string(data['name'])
            is_valid, error_msg = Validator.validate_project_name(name)
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'error': error_msg,
                    'field': 'name'
                }), 400
            data['name'] = name
        
        # Validate path if provided
        if 'path' in data:
            path = Validator.sanitize_string(data['path'], max_length=500)
            is_valid, error_msg = Validator.validate_file_path(path, allow_absolute=True)
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'error': error_msg,
                    'field': 'path'
                }), 400
            data['path'] = path
        
        # Update project
        project = project_service.update_project(project_id, data)
        
        if project:
            current_app.logger.info(f"Project updated successfully: {project_id}")
            return jsonify({
                'status': 'success',
                'data': project,
                'message': 'Project updated successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Project not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error updating project {project_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to update project',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
def delete_project(project_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a project
    
    Args:
        project_id: Unique project identifier
        
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
    
    try:
        success = project_service.delete_project(project_id)
        
        if success:
            current_app.logger.info(f"Project deleted successfully: {project_id}")
            return jsonify({
                'status': 'success',
                'message': 'Project deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Project not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting project {project_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete project',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@projects_bp.route('/<project_id>/files', methods=['GET'])
def get_project_files(project_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get file tree for a project
    
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
        files = project_service.get_project_files(project_id)
        
        if files is not None:
            return jsonify({
                'status': 'success',
                'data': files
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'error': 'Project not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error fetching files for project {project_id}: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch project files',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
