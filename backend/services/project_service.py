"""
Project Service
Business logic for project management
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app


class ProjectService:
    """Service for managing projects"""
    
    def __init__(self):
        self.projects_file = None
        self.projects = []
    
    def _get_projects_file(self) -> Path:
        """Get the projects JSON file path"""
        if self.projects_file is None:
            data_dir = current_app.config.get('DATA_DIR', Path('data'))
            self.projects_file = data_dir / 'projects.json'
            self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        return self.projects_file
    
    def _load_projects(self) -> List[Dict]:
        """Load projects from JSON file"""
        try:
            projects_file = self._get_projects_file()
            if projects_file.exists():
                with open(projects_file, 'r') as f:
                    self.projects = json.load(f)
            else:
                self.projects = self._create_default_projects()
                self._save_projects()
            return self.projects
        except Exception as e:
            current_app.logger.error(f"Error loading projects: {e}")
            return []
    
    def _save_projects(self):
        """Save projects to JSON file"""
        try:
            projects_file = self._get_projects_file()
            with open(projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            current_app.logger.error(f"Error saving projects: {e}")
    
    def _create_default_projects(self) -> List[Dict]:
        """Create default sample projects"""
        return [
            {
                'id': 'autopilot-project-1',
                'name': 'AutoPilot-Project',
                'path': str(current_app.config['PROJECTS_DIR'] / 'AutoPilot-Project'),
                'type': 'Python',
                'createdAt': datetime.now().isoformat(),
                'lastOpened': datetime.now().isoformat(),
                'description': 'Main AutoPilot IDE project'
            },
            {
                'id': 'webapp-demo-1',
                'name': 'WebApp-Demo',
                'path': str(current_app.config['PROJECTS_DIR'] / 'WebApp-Demo'),
                'type': 'JavaScript',
                'createdAt': datetime.now().isoformat(),
                'lastOpened': datetime.now().isoformat(),
                'description': 'Sample web application'
            }
        ]
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        if not self.projects:
            self._load_projects()
        return self.projects
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project by ID"""
        projects = self.get_all_projects()
        return next((p for p in projects if p['id'] == project_id), None)
    
    def create_project(self, name: str, project_type: str = 'Python', 
                      path: str = None) -> Dict:
        """Create a new project"""
        project_id = f"project-{datetime.now().timestamp()}"
        
        if path is None:
            path = str(current_app.config['PROJECTS_DIR'] / name)
        
        project = {
            'id': project_id,
            'name': name,
            'path': path,
            'type': project_type,
            'createdAt': datetime.now().isoformat(),
            'lastOpened': datetime.now().isoformat(),
            'description': f'{project_type} project'
        }
        
        # Create project directory
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"Created project directory: {path}")
        except Exception as e:
            current_app.logger.error(f"Error creating project directory: {e}")
        
        projects = self.get_all_projects()
        projects.append(project)
        self._save_projects()
        
        current_app.logger.info(f"Created project: {name}")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        projects = self.get_all_projects()
        project = self.get_project(project_id)
        
        if not project:
            return False
        
        # Remove from list
        self.projects = [p for p in projects if p['id'] != project_id]
        self._save_projects()
        
        current_app.logger.info(f"Deleted project: {project['name']}")
        return True
    
    def get_project_files(self, project_id: str) -> Optional[List[Dict]]:
        """Get file tree for a project"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        project_path = Path(project['path'])
        if not project_path.exists():
            return []
        
        return self._build_file_tree(project_path)
    
    def _build_file_tree(self, path: Path, max_depth: int = 5, 
                        current_depth: int = 0) -> List[Dict]:
        """Recursively build file tree"""
        if current_depth >= max_depth:
            return []
        
        tree = []
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden files and common ignore patterns
                if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                    continue
                
                if item.is_file():
                    tree.append({
                        'name': item.name,
                        'type': 'file',
                        'path': str(item.relative_to(path.parent)),
                        'icon': self._get_file_icon(item.suffix)
                    })
                elif item.is_dir():
                    tree.append({
                        'name': item.name,
                        'type': 'folder',
                        'path': str(item.relative_to(path.parent)),
                        'icon': '📁',
                        'children': self._build_file_tree(item, max_depth, current_depth + 1)
                    })
        except PermissionError:
            current_app.logger.warning(f"Permission denied accessing: {path}")
        
        return tree
    
    def _get_file_icon(self, extension: str) -> str:
        """Get icon for file type"""
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.yml': '⚙️',
            '.yaml': '⚙️',
        }
        return icon_map.get(extension.lower(), '📄')
