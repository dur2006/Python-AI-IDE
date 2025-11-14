"""
File Service
Business logic for file operations
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from flask import current_app


class FileService:
    """Service for managing file operations"""
    
    def __init__(self):
        self.project_service = None
    
    def _get_project_service(self):
        """Lazy load project service to avoid circular imports"""
        if self.project_service is None:
            from backend.services.project_service import ProjectService
            self.project_service = ProjectService()
        return self.project_service
    
    def _get_file_path(self, project_id: str, file_path: str) -> Optional[Path]:
        """Get absolute file path from project ID and relative path"""
        project = self._get_project_service().get_project(project_id)
        if not project:
            return None
        
        project_path = Path(project['path'])
        full_path = project_path / file_path
        
        # Security check: ensure file is within project directory
        try:
            full_path.resolve().relative_to(project_path.resolve())
        except ValueError:
            current_app.logger.warning(f"Attempted path traversal: {file_path}")
            return None
        
        return full_path
    
    def read_file(self, project_id: str, file_path: str) -> Optional[str]:
        """Read file content"""
        full_path = self._get_file_path(project_id, file_path)
        if not full_path or not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            current_app.logger.info(f"Read file: {file_path}")
            return content
        except UnicodeDecodeError:
            # Try reading as binary for non-text files
            try:
                with open(full_path, 'rb') as f:
                    return f"[Binary file: {full_path.name}]"
            except Exception as e:
                current_app.logger.error(f"Error reading file {file_path}: {e}")
                return None
        except Exception as e:
            current_app.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, project_id: str, file_path: str, content: str) -> bool:
        """Write content to file"""
        full_path = self._get_file_path(project_id, file_path)
        if not full_path:
            return False
        
        try:
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            current_app.logger.info(f"Wrote file: {file_path}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    def create_file(self, project_id: str, file_path: str, content: str = '') -> bool:
        """Create a new file"""
        full_path = self._get_file_path(project_id, file_path)
        if not full_path:
            return False
        
        if full_path.exists():
            current_app.logger.warning(f"File already exists: {file_path}")
            return False
        
        return self.write_file(project_id, file_path, content)
    
    def delete_file(self, project_id: str, file_path: str) -> bool:
        """Delete a file"""
        full_path = self._get_file_path(project_id, file_path)
        if not full_path or not full_path.exists():
            return False
        
        try:
            if full_path.is_file():
                full_path.unlink()
                current_app.logger.info(f"Deleted file: {file_path}")
                return True
            elif full_path.is_dir():
                # For directories, use rmdir (only works if empty)
                full_path.rmdir()
                current_app.logger.info(f"Deleted directory: {file_path}")
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_tree(self, project_id: str) -> Optional[List[Dict]]:
        """Get file tree for a project"""
        return self._get_project_service().get_project_files(project_id)
    
    def create_directory(self, project_id: str, dir_path: str) -> bool:
        """Create a new directory"""
        full_path = self._get_file_path(project_id, dir_path)
        if not full_path:
            return False
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    
    def rename_file(self, project_id: str, old_path: str, new_path: str) -> bool:
        """Rename/move a file"""
        old_full_path = self._get_file_path(project_id, old_path)
        new_full_path = self._get_file_path(project_id, new_path)
        
        if not old_full_path or not new_full_path:
            return False
        
        if not old_full_path.exists():
            return False
        
        try:
            new_full_path.parent.mkdir(parents=True, exist_ok=True)
            old_full_path.rename(new_full_path)
            current_app.logger.info(f"Renamed file: {old_path} -> {new_path}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error renaming file {old_path}: {e}")
            return False
