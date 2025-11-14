"""
AppData Manager - Centralized Data Management
Manages all application data including projects, themes, extensions, layouts, and settings.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


logger = logging.getLogger(__name__)


class AppDataManager:
    """
    Centralized manager for all application data.
    Implements singleton pattern for global access.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize AppData Manager"""
        if self._initialized:
            return
            
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self.projects_file = self.data_dir / 'projects.json'
        self.themes_file = self.data_dir / 'themes.json'
        self.extensions_file = self.data_dir / 'extensions.json'
        self.layouts_file = self.data_dir / 'layouts.json'
        self.settings_file = self.data_dir / 'settings.json'
        
        # In-memory cache
        self._cache = {
            'projects': None,
            'themes': None,
            'extensions': None,
            'layouts': None,
            'settings': None
        }
        
        self._initialized = True
        logger.info("AppData Manager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize data directory and files with defaults
        Returns True if successful
        """
        try:
            # Create data directory
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Data directory created: {self.data_dir}")
            
            # Initialize each data file
            self._init_projects()
            self._init_themes()
            self._init_extensions()
            self._init_layouts()
            self._init_settings()
            
            logger.info("[OK] AppData initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] AppData initialization failed: {e}")
            return False
    
    # ==================== PROJECTS ====================
    
    def _init_projects(self):
        """Initialize projects file with default data"""
        if not self.projects_file.exists():
            default_projects = [{
                'id': f'project-{int(datetime.now().timestamp())}',
                'name': 'AutoPilot-Project',
                'path': './projects/AutoPilot-Project',
                'type': 'Python',
                'createdAt': datetime.now().isoformat(),
                'lastOpened': datetime.now().isoformat(),
                'description': 'Main AutoPilot IDE project',
                'files': []
            }]
            self._write_json(self.projects_file, default_projects)
            logger.info("Projects initialized with default data")
    
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        if self._cache['projects'] is None:
            self._cache['projects'] = self._read_json(self.projects_file, [])
        return self._cache['projects']
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get specific project by ID"""
        projects = self.get_projects()
        return next((p for p in projects if p['id'] == project_id), None)
    
    def create_project(self, name: str, project_type: str = 'Python', 
                      description: str = '') -> Dict:
        """Create new project"""
        projects = self.get_projects()
        
        new_project = {
            'id': f'project-{int(datetime.now().timestamp())}',
            'name': name,
            'path': f'./projects/{name.replace(" ", "-")}',
            'type': project_type,
            'createdAt': datetime.now().isoformat(),
            'lastOpened': datetime.now().isoformat(),
            'description': description,
            'files': []
        }
        
        projects.append(new_project)
        self._write_json(self.projects_file, projects)
        self._cache['projects'] = projects
        
        logger.info(f"Project created: {name}")
        return new_project
    
    def update_project(self, project_id: str, updates: Dict) -> Optional[Dict]:
        """Update existing project"""
        projects = self.get_projects()
        
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                projects[i].update(updates)
                projects[i]['lastOpened'] = datetime.now().isoformat()
                self._write_json(self.projects_file, projects)
                self._cache['projects'] = projects
                logger.info(f"Project updated: {project_id}")
                return projects[i]
        
        return None
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        projects = self.get_projects()
        initial_count = len(projects)
        
        projects = [p for p in projects if p['id'] != project_id]
        
        if len(projects) < initial_count:
            self._write_json(self.projects_file, projects)
            self._cache['projects'] = projects
            logger.info(f"Project deleted: {project_id}")
            return True
        
        return False
    
    # ==================== THEMES ====================
    
    def _init_themes(self):
        """Initialize themes file with default data"""
        if not self.themes_file.exists():
            default_themes = [
                {
                    'id': 'dark-default',
                    'name': 'Dark (Default)',
                    'active': True,
                    'colors': {
                        'primary': '#667eea',
                        'secondary': '#764ba2',
                        'background': '#1e1e1e',
                        'surface': '#252526',
                        'text': '#d4d4d4',
                        'textSecondary': '#858585',
                        'border': '#3e3e42',
                        'accent': '#007acc'
                    }
                },
                {
                    'id': 'light-default',
                    'name': 'Light',
                    'active': False,
                    'colors': {
                        'primary': '#667eea',
                        'secondary': '#764ba2',
                        'background': '#ffffff',
                        'surface': '#f3f3f3',
                        'text': '#1e1e1e',
                        'textSecondary': '#6e6e6e',
                        'border': '#e5e5e5',
                        'accent': '#0066cc'
                    }
                }
            ]
            self._write_json(self.themes_file, default_themes)
            logger.info("Themes initialized with default data")
    
    def get_themes(self) -> List[Dict]:
        """Get all themes"""
        if self._cache['themes'] is None:
            self._cache['themes'] = self._read_json(self.themes_file, [])
        return self._cache['themes']
    
    def get_theme(self, theme_id: str) -> Optional[Dict]:
        """Get specific theme by ID"""
        themes = self.get_themes()
        return next((t for t in themes if t['id'] == theme_id), None)
    
    def get_active_theme(self) -> Optional[Dict]:
        """Get currently active theme"""
        themes = self.get_themes()
        return next((t for t in themes if t.get('active', False)), None)
    
    def set_active_theme(self, theme_id: str) -> bool:
        """Set active theme"""
        themes = self.get_themes()
        
        # Deactivate all themes
        for theme in themes:
            theme['active'] = False
        
        # Activate selected theme
        for theme in themes:
            if theme['id'] == theme_id:
                theme['active'] = True
                self._write_json(self.themes_file, themes)
                self._cache['themes'] = themes
                logger.info(f"Theme activated: {theme_id}")
                return True
        
        return False
    
    # ==================== EXTENSIONS ====================
    
    def _init_extensions(self):
        """Initialize extensions file with default data"""
        if not self.extensions_file.exists():
            default_extensions = [
                {
                    'id': 1,
                    'name': 'Python Language Support',
                    'description': 'Syntax highlighting and IntelliSense for Python',
                    'version': '1.0.0',
                    'author': 'AutoPilot Team',
                    'enabled': True,
                    'installed': True,
                    'icon': 'python'
                },
                {
                    'id': 2,
                    'name': 'Git Integration',
                    'description': 'Version control with Git',
                    'version': '1.0.0',
                    'author': 'AutoPilot Team',
                    'enabled': True,
                    'installed': True,
                    'icon': 'git'
                },
                {
                    'id': 3,
                    'name': 'Code Formatter',
                    'description': 'Auto-format code with Black',
                    'version': '1.0.0',
                    'author': 'AutoPilot Team',
                    'enabled': True,
                    'installed': True,
                    'icon': 'format'
                },
                {
                    'id': 4,
                    'name': 'Linter',
                    'description': 'Code quality checks with Pylint',
                    'version': '1.0.0',
                    'author': 'AutoPilot Team',
                    'enabled': True,
                    'installed': True,
                    'icon': 'search'
                },
                {
                    'id': 5,
                    'name': 'Debugger',
                    'description': 'Interactive debugging support',
                    'version': '1.0.0',
                    'author': 'AutoPilot Team',
                    'enabled': True,
                    'installed': True,
                    'icon': 'bug'
                }
            ]
            self._write_json(self.extensions_file, default_extensions)
            logger.info("Extensions initialized with default data")
    
    def get_extensions(self) -> List[Dict]:
        """Get all extensions"""
        if self._cache['extensions'] is None:
            self._cache['extensions'] = self._read_json(self.extensions_file, [])
        return self._cache['extensions']
    
    def get_extension(self, extension_id: int) -> Optional[Dict]:
        """Get specific extension by ID"""
        extensions = self.get_extensions()
        return next((e for e in extensions if e['id'] == extension_id), None)
    
    def get_installed_extensions(self) -> List[Dict]:
        """Get installed extensions"""
        return [e for e in self.get_extensions() if e.get('installed', False)]
    
    def get_available_extensions(self) -> List[Dict]:
        """Get available (not installed) extensions"""
        return [e for e in self.get_extensions() if not e.get('installed', False)]
    
    def toggle_extension(self, extension_id: int) -> Optional[Dict]:
        """Toggle extension enabled state"""
        extensions = self.get_extensions()
        
        for i, ext in enumerate(extensions):
            if ext['id'] == extension_id:
                extensions[i]['enabled'] = not extensions[i].get('enabled', False)
                self._write_json(self.extensions_file, extensions)
                self._cache['extensions'] = extensions
                logger.info(f"Extension toggled: {extension_id}")
                return extensions[i]
        
        return None
    
    def install_extension(self, extension_id: int) -> Optional[Dict]:
        """Install extension"""
        extensions = self.get_extensions()
        
        for i, ext in enumerate(extensions):
            if ext['id'] == extension_id:
                extensions[i]['installed'] = True
                extensions[i]['enabled'] = True
                self._write_json(self.extensions_file, extensions)
                self._cache['extensions'] = extensions
                logger.info(f"Extension installed: {extension_id}")
                return extensions[i]
        
        return None
    
    def uninstall_extension(self, extension_id: int) -> bool:
        """Uninstall extension"""
        extensions = self.get_extensions()
        
        for i, ext in enumerate(extensions):
            if ext['id'] == extension_id:
                extensions[i]['installed'] = False
                extensions[i]['enabled'] = False
                self._write_json(self.extensions_file, extensions)
                self._cache['extensions'] = extensions
                logger.info(f"Extension uninstalled: {extension_id}")
                return True
        
        return False
    
    # ==================== LAYOUTS ====================
    
    def _init_layouts(self):
        """Initialize layouts file with default data"""
        if not self.layouts_file.exists():
            default_layouts = [
                {
                    'id': 'default',
                    'name': 'Default Layout',
                    'active': True,
                    'config': {
                        'sidebar': {'visible': True, 'width': 250},
                        'editor': {'visible': True},
                        'terminal': {'visible': True, 'height': 250},
                        'aiPanel': {'visible': True, 'width': 380}
                    },
                    'createdAt': datetime.now().isoformat(),
                    'updatedAt': datetime.now().isoformat()
                },
                {
                    'id': 'focus',
                    'name': 'Focus Mode',
                    'active': False,
                    'config': {
                        'sidebar': {'visible': False, 'width': 250},
                        'editor': {'visible': True},
                        'terminal': {'visible': False, 'height': 250},
                        'aiPanel': {'visible': False, 'width': 380}
                    },
                    'createdAt': datetime.now().isoformat(),
                    'updatedAt': datetime.now().isoformat()
                },
                {
                    'id': 'coding',
                    'name': 'Coding Layout',
                    'active': False,
                    'config': {
                        'sidebar': {'visible': True, 'width': 200},
                        'editor': {'visible': True},
                        'terminal': {'visible': True, 'height': 300},
                        'aiPanel': {'visible': True, 'width': 300}
                    },
                    'createdAt': datetime.now().isoformat(),
                    'updatedAt': datetime.now().isoformat()
                }
            ]
            self._write_json(self.layouts_file, default_layouts)
            logger.info("Layouts initialized with default data")
    
    def get_layouts(self) -> List[Dict]:
        """Get all layouts"""
        if self._cache['layouts'] is None:
            self._cache['layouts'] = self._read_json(self.layouts_file, [])
        return self._cache['layouts']
    
    def get_layout(self, layout_id: str) -> Optional[Dict]:
        """Get specific layout by ID"""
        layouts = self.get_layouts()
        return next((l for l in layouts if l['id'] == layout_id), None)
    
    def get_active_layout(self) -> Optional[Dict]:
        """Get currently active layout"""
        layouts = self.get_layouts()
        return next((l for l in layouts if l.get('active', False)), None)
    
    def set_active_layout(self, layout_id: str) -> bool:
        """Set active layout"""
        layouts = self.get_layouts()
        
        # Deactivate all layouts
        for layout in layouts:
            layout['active'] = False
        
        # Activate selected layout
        for layout in layouts:
            if layout['id'] == layout_id:
                layout['active'] = True
                layout['updatedAt'] = datetime.now().isoformat()
                self._write_json(self.layouts_file, layouts)
                self._cache['layouts'] = layouts
                logger.info(f"Layout activated: {layout_id}")
                return True
        
        return False
    
    def save_layout(self, layout_id: str, config: Dict) -> Optional[Dict]:
        """Save layout configuration"""
        layouts = self.get_layouts()
        
        for i, layout in enumerate(layouts):
            if layout['id'] == layout_id:
                layouts[i]['config'] = config
                layouts[i]['updatedAt'] = datetime.now().isoformat()
                self._write_json(self.layouts_file, layouts)
                self._cache['layouts'] = layouts
                logger.info(f"Layout saved: {layout_id}")
                return layouts[i]
        
        return None
    
    # ==================== SETTINGS ====================
    
    def _init_settings(self):
        """Initialize settings file with default data"""
        if not self.settings_file.exists():
            default_settings = {
                'theme': 'dark-default',
                'layout': 'default',
                'fontSize': 14,
                'fontFamily': 'Consolas, Monaco, monospace',
                'autoSave': True,
                'autoSaveInterval': 5000,
                'showLineNumbers': True,
                'wordWrap': True,
                'tabSize': 4,
                'insertSpaces': True,
                'minimap': True,
                'bracketPairColorization': True,
                'formatOnSave': True,
                'formatOnPaste': False
            }
            self._write_json(self.settings_file, default_settings)
            logger.info("Settings initialized with default data")
    
    def get_settings(self) -> Dict:
        """Get all settings"""
        if self._cache['settings'] is None:
            self._cache['settings'] = self._read_json(self.settings_file, {})
        return self._cache['settings']
    
    def get_setting(self, key: str) -> Any:
        """Get specific setting"""
        settings = self.get_settings()
        return settings.get(key)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set specific setting"""
        settings = self.get_settings()
        settings[key] = value
        self._write_json(self.settings_file, settings)
        self._cache['settings'] = settings
        logger.info(f"Setting updated: {key} = {value}")
        return True
    
    def update_settings(self, updates: Dict) -> Dict:
        """Update multiple settings"""
        settings = self.get_settings()
        settings.update(updates)
        self._write_json(self.settings_file, settings)
        self._cache['settings'] = settings
        logger.info(f"Settings updated: {list(updates.keys())}")
        return settings
    
    # ==================== UTILITY METHODS ====================
    
    def _read_json(self, file_path: Path, default: Any = None) -> Any:
        """Read JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return default
    
    def _write_json(self, file_path: Path, data: Any) -> bool:
        """Write JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
            return False
    
    def clear_cache(self):
        """Clear in-memory cache"""
        self._cache = {
            'projects': None,
            'themes': None,
            'extensions': None,
            'layouts': None,
            'settings': None
        }
        logger.info("Cache cleared")
    
    def get_status(self) -> Dict:
        """Get AppData manager status"""
        return {
            'initialized': self._initialized,
            'dataDir': str(self.data_dir),
            'projects': len(self.get_projects()),
            'themes': len(self.get_themes()),
            'extensions': len(self.get_extensions()),
            'layouts': len(self.get_layouts()),
            'settings': len(self.get_settings())
        }


# Global singleton instance
_appdata_manager = None


def get_appdata_manager() -> AppDataManager:
    """Get global AppData manager instance"""
    global _appdata_manager
    if _appdata_manager is None:
        _appdata_manager = AppDataManager()
    return _appdata_manager
