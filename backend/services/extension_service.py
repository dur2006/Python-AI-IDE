"""
Extension Service
Business logic for extension management
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from flask import current_app


class ExtensionService:
    """Service for managing IDE extensions"""
    
    def __init__(self):
        self.extensions_file = None
        self.extensions = []
    
    def _get_extensions_file(self) -> Path:
        """Get the extensions JSON file path"""
        if self.extensions_file is None:
            data_dir = current_app.config.get('DATA_DIR', Path('data'))
            self.extensions_file = data_dir / 'extensions.json'
            self.extensions_file.parent.mkdir(parents=True, exist_ok=True)
        return self.extensions_file
    
    def _load_extensions(self) -> List[Dict]:
        """Load extensions from JSON file"""
        try:
            extensions_file = self._get_extensions_file()
            if extensions_file.exists():
                with open(extensions_file, 'r') as f:
                    self.extensions = json.load(f)
            else:
                self.extensions = self._create_default_extensions()
                self._save_extensions()
            return self.extensions
        except Exception as e:
            current_app.logger.error(f"Error loading extensions: {e}")
            return []
    
    def _save_extensions(self):
        """Save extensions to JSON file"""
        try:
            extensions_file = self._get_extensions_file()
            with open(extensions_file, 'w') as f:
                json.dump(self.extensions, f, indent=2)
        except Exception as e:
            current_app.logger.error(f"Error saving extensions: {e}")
    
    def _create_default_extensions(self) -> List[Dict]:
        """Create default extensions list"""
        return [
            {
                'id': 1,
                'name': 'Python Language Support',
                'description': 'Syntax highlighting and IntelliSense for Python',
                'version': '1.0.0',
                'author': 'AutoPilot Team',
                'enabled': True,
                'installed': True,
                'icon': '🐍'
            },
            {
                'id': 2,
                'name': 'Git Integration',
                'description': 'Git source control integration',
                'version': '1.2.0',
                'author': 'AutoPilot Team',
                'enabled': True,
                'installed': True,
                'icon': '📦'
            },
            {
                'id': 3,
                'name': 'AI Code Assistant',
                'description': 'AI-powered code completion and suggestions',
                'version': '2.0.0',
                'author': 'AutoPilot Team',
                'enabled': True,
                'installed': True,
                'icon': '🤖'
            },
            {
                'id': 4,
                'name': 'Theme Pack',
                'description': 'Additional color themes for the IDE',
                'version': '1.0.0',
                'author': 'Community',
                'enabled': False,
                'installed': False,
                'icon': '🎨'
            },
            {
                'id': 5,
                'name': 'Docker Support',
                'description': 'Docker container management',
                'version': '1.1.0',
                'author': 'Community',
                'enabled': False,
                'installed': False,
                'icon': '🐳'
            }
        ]
    
    def get_all_extensions(self) -> List[Dict]:
        """Get all extensions"""
        if not self.extensions:
            self._load_extensions()
        return self.extensions
    
    def get_extension(self, ext_id: int) -> Optional[Dict]:
        """Get a specific extension by ID"""
        extensions = self.get_all_extensions()
        return next((e for e in extensions if e['id'] == ext_id), None)
    
    def toggle_extension(self, ext_id: int) -> Optional[Dict]:
        """Toggle extension enabled/disabled status"""
        extension = self.get_extension(ext_id)
        if not extension:
            return None
        
        if not extension.get('installed', False):
            current_app.logger.warning(f"Cannot toggle uninstalled extension: {ext_id}")
            return None
        
        extension['enabled'] = not extension.get('enabled', False)
        self._save_extensions()
        
        status = "enabled" if extension['enabled'] else "disabled"
        current_app.logger.info(f"Extension {extension['name']} {status}")
        return extension
    
    def install_extension(self, ext_id: int) -> Optional[Dict]:
        """Install an extension"""
        extension = self.get_extension(ext_id)
        if not extension:
            return None
        
        if extension.get('installed', False):
            current_app.logger.warning(f"Extension already installed: {ext_id}")
            return extension
        
        extension['installed'] = True
        extension['enabled'] = True
        self._save_extensions()
        
        current_app.logger.info(f"Installed extension: {extension['name']}")
        return extension
    
    def uninstall_extension(self, ext_id: int) -> bool:
        """Uninstall an extension"""
        extension = self.get_extension(ext_id)
        if not extension:
            return False
        
        extension['installed'] = False
        extension['enabled'] = False
        self._save_extensions()
        
        current_app.logger.info(f"Uninstalled extension: {extension['name']}")
        return True
