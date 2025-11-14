"""
Projects API Blueprint
Handles project management endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from backend.services.project_service import ProjectService

projects_bp = Blueprint('projects', __name__)
project_service = ProjectService()


@projects_bp.route('', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = project_service.get_all_projects()
        return jsonify(projects), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {e}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID"""
    try:
        project = project_service.get_project(project_id)
        if project:
            return jsonify(project), 200
        return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        name = data.get('name')
        project_type = data.get('type', 'Python')
        path = data.get('path')
        
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        project = project_service.create_project(name, project_type, path)
        return jsonify(project), 201
    except Exception as e:
        current_app.logger.error(f"Error creating project: {e}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        success = project_service.delete_project(project_id)
        if success:
            return jsonify({'status': 'success'}), 200
        return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<project_id>/files', methods=['GET'])
def get_project_files(project_id):
    """Get file tree for a project"""
    try:
        files = project_service.get_project_files(project_id)
        if files is not None:
            return jsonify(files), 200
        return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching files for project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500
