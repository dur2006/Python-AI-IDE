"""
Project Service
Business logic for project management - now using AppData Manager as backend
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app

from backend.services.appdata_manager import get_appdata_manager


class ProjectService:
    """
    Service for managing projects
    Now uses AppData Manager for data persistence while maintaining same API
    """
    
    def __init__(self):
        self.appdata = get_appdata_manager()
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        return self.appdata.get_projects()
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project by ID"""
        return self.appdata.get_project(project_id)
    
    def create_project(self, name: str, project_type: str = 'Python', 
                      path: str = None, description: str = '') -> Dict:
        """Create a new project"""
        
        # Use provided path or generate default
        if path is None:
            projects_dir = current_app.config.get('PROJECTS_DIR', Path('projects'))
            path = str(projects_dir / name.replace(' ', '-'))
        
        # Create project directory
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"Created project directory: {path}")
        except Exception as e:
            current_app.logger.error(f"Error creating project directory: {e}")
        
        # Create project via AppData manager
        project = self.appdata.create_project(
            name=name,
            project_type=project_type,
            description=description
        )
        
        # Update path if custom path was provided
        if path:
            project['path'] = path
            self.appdata.update_project(project['id'], {'path': path})
        
        current_app.logger.info(f"Created project: {name}")
        return project
    
    def update_project(self, project_id: str, updates: Dict) -> Optional[Dict]:
        """Update a project"""
        project = self.appdata.update_project(project_id, updates)
        if project:
            current_app.logger.info(f"Updated project: {project_id}")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        success = self.appdata.delete_project(project_id)
        if success:
            current_app.logger.info(f"Deleted project: {project['name']}")
        return success
    
    def get_project_files(self, project_id: str) -> Optional[List[Dict]]:
        """Get file tree for a project"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        project_path = Path(project['path'])
        if not project_path.exists():
            current_app.logger.warning(f"Project path does not exist: {project_path}")
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
                if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', 'venv', '.git']:
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
        except Exception as e:
            current_app.logger.error(f"Error building file tree: {e}")
        
        return tree
    
    def _get_file_icon(self, extension: str) -> str:
        """Get icon for file type"""
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.jsx': '⚛️',
            '.tsx': '⚛️',
            '.html': '🌐',
            '.css': '🎨',
            '.scss': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.xml': '📋',
            '.sql': '🗄️',
            '.sh': '🔧',
            '.bat': '🔧',
            '.env': '🔐',
            '.gitignore': '📦',
            '.dockerfile': '🐳',
            '.docker': '🐳',
        }
        return icon_map.get(extension.lower(), '📄')
    
    def open_project(self, project_id: str) -> Optional[Dict]:
        """Mark project as opened (updates lastOpened timestamp)"""
        return self.appdata.update_project(project_id, {
            'lastOpened': datetime.now().isoformat()
        })
    
    def get_recent_projects(self, limit: int = 5) -> List[Dict]:
        """Get recently opened projects"""
        projects = self.get_all_projects()
        # Sort by lastOpened timestamp
        sorted_projects = sorted(
            projects,
            key=lambda p: p.get('lastOpened', ''),
            reverse=True
        )
        return sorted_projects[:limit]
