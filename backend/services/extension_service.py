"""
Extension Service
Business logic for extension management - now using AppData Manager as backend
"""

from typing import List, Dict, Optional
from flask import current_app

from backend.services.appdata_manager import get_appdata_manager


class ExtensionService:
    """
    Service for managing IDE extensions
    Now uses AppData Manager for data persistence while maintaining same API
    """
    
    def __init__(self):
        self.appdata = get_appdata_manager()
    
    def get_all_extensions(self) -> List[Dict]:
        """Get all extensions"""
        return self.appdata.get_extensions()
    
    def get_extension(self, ext_id: int) -> Optional[Dict]:
        """Get a specific extension by ID"""
        return self.appdata.get_extension(ext_id)
    
    def get_installed_extensions(self) -> List[Dict]:
        """Get only installed extensions"""
        return self.appdata.get_installed_extensions()
    
    def get_available_extensions(self) -> List[Dict]:
        """Get available (not installed) extensions"""
        return self.appdata.get_available_extensions()
    
    def toggle_extension(self, ext_id: int) -> Optional[Dict]:
        """Toggle extension enabled/disabled status"""
        extension = self.get_extension(ext_id)
        if not extension:
            current_app.logger.warning(f"Extension not found: {ext_id}")
            return None
        
        if not extension.get('installed', False):
            current_app.logger.warning(f"Cannot toggle uninstalled extension: {ext_id}")
            return None
        
        result = self.appdata.toggle_extension(ext_id)
        if result:
            status = "enabled" if result['enabled'] else "disabled"
            current_app.logger.info(f"Extension {result['name']} {status}")
        
        return result
    
    def install_extension(self, ext_id: int) -> Optional[Dict]:
        """Install an extension"""
        extension = self.get_extension(ext_id)
        if not extension:
            current_app.logger.warning(f"Extension not found: {ext_id}")
            return None
        
        if extension.get('installed', False):
            current_app.logger.warning(f"Extension already installed: {ext_id}")
            return extension
        
        result = self.appdata.install_extension(ext_id)
        if result:
            current_app.logger.info(f"Installed extension: {result['name']}")
        
        return result
    
    def uninstall_extension(self, ext_id: int) -> bool:
        """Uninstall an extension"""
        extension = self.get_extension(ext_id)
        if not extension:
            current_app.logger.warning(f"Extension not found: {ext_id}")
            return False
        
        if not extension.get('installed', False):
            current_app.logger.warning(f"Extension not installed: {ext_id}")
            return False
        
        success = self.appdata.uninstall_extension(ext_id)
        if success:
            current_app.logger.info(f"Uninstalled extension: {extension['name']}")
        
        return success
    
    def get_enabled_extensions(self) -> List[Dict]:
        """Get all enabled extensions"""
        extensions = self.get_all_extensions()
        return [e for e in extensions if e.get('enabled', False) and e.get('installed', False)]
    
    def get_extension_count(self) -> Dict[str, int]:
        """Get extension statistics"""
        extensions = self.get_all_extensions()
        return {
            'total': len(extensions),
            'installed': len([e for e in extensions if e.get('installed', False)]),
            'enabled': len([e for e in extensions if e.get('enabled', False)]),
            'available': len([e for e in extensions if not e.get('installed', False)])
        }
