"""
AppData Manager Module
Manages the AutoPilot IDE AppData folder structure in the user's local AppData directory.
Creates and maintains: Themes, Extensions, Layouts, and Projects folders.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class AppDataManager:
    """Manages AutoPilot IDE AppData folder structure"""
    
    # Folder structure
    APPDATA_FOLDER_NAME = "AutoPilot-IDE"
    SUBFOLDERS = {
        "themes": "Color themes and UI customizations",
        "extensions": "Installed extensions and plugins",
        "layouts": "Saved window layouts and configurations",
        "projects": "User projects and workspaces"
    }
    
    def __init__(self):
        """Initialize AppData manager"""
        self.appdata_path = self._get_appdata_path()
        self.initialized = False
        
    def _get_appdata_path(self) -> Path:
        """Get the AppData folder path based on OS"""
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if not appdata:
                appdata = os.path.expanduser('~\\AppData\\Roaming')
        else:  # Linux/Mac
            appdata = os.path.expanduser('~/.config')
        
        return Path(appdata) / self.APPDATA_FOLDER_NAME
    
    def initialize(self) -> Dict:
        """
        Initialize AppData folder structure.
        Creates all necessary folders and default files.
        """
        try:
            # Create main AppData folder
            self.appdata_path.mkdir(parents=True, exist_ok=True)
            
            # Create subfolders
            for folder_name in self.SUBFOLDERS.keys():
                folder_path = self.appdata_path / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create default configuration files
            self._create_default_themes()
            self._create_default_layouts()
            self._create_default_extensions_config()
            self._create_projects_index()
            
            self.initialized = True
            
            return {
                "status": "success",
                "message": "AppData folder initialized successfully",
                "appdata_path": str(self.appdata_path),
                "folders": self.SUBFOLDERS
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize AppData: {str(e)}"
            }
    
    def _create_default_themes(self) -> None:
        """Create default theme files"""
        themes_dir = self.appdata_path / "themes"
        
        # Default dark theme
        dark_theme = {
            "name": "Dark (Default)",
            "id": "dark-default",
            "description": "Default dark theme",
            "colors": {
                "bg-primary": "#1e1e1e",
                "bg-secondary": "#252526",
                "bg-tertiary": "#2d2d30",
                "border-color": "#3e3e42",
                "text-primary": "#d4d4d4",
                "text-secondary": "#999",
                "accent-primary": "#667eea",
                "accent-secondary": "#764ba2"
            }
        }
        
        # Default light theme
        light_theme = {
            "name": "Light",
            "id": "light",
            "description": "Light theme",
            "colors": {
                "bg-primary": "#ffffff",
                "bg-secondary": "#f5f5f5",
                "bg-tertiary": "#eeeeee",
                "border-color": "#e0e0e0",
                "text-primary": "#333333",
                "text-secondary": "#666666",
                "accent-primary": "#667eea",
                "accent-secondary": "#764ba2"
            }
        }
        
        # Save themes
        with open(themes_dir / "dark-default.json", 'w') as f:
            json.dump(dark_theme, f, indent=2)
        
        with open(themes_dir / "light.json", 'w') as f:
            json.dump(light_theme, f, indent=2)
        
        # Create themes index
        themes_index = {
            "themes": [
                {"id": "dark-default", "name": "Dark (Default)", "file": "dark-default.json"},
                {"id": "light", "name": "Light", "file": "light.json"}
            ],
            "active": "dark-default"
        }
        
        with open(themes_dir / "themes.json", 'w') as f:
            json.dump(themes_index, f, indent=2)
    
    def _create_default_layouts(self) -> None:
        """Create default layout files"""
        layouts_dir = self.appdata_path / "layouts"
        
        layouts = {
            "layouts": [
                {
                    "id": "default",
                    "name": "Default",
                    "description": "Standard IDE layout with all panels visible",
                    "config": {
                        "sidebar": {"visible": True, "width": 250},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": True, "height": 250},
                        "aiPanel": {"visible": True, "width": 380}
                    }
                },
                {
                    "id": "focus",
                    "name": "Focus Mode",
                    "description": "Editor only - minimize distractions",
                    "config": {
                        "sidebar": {"visible": False},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": False},
                        "aiPanel": {"visible": False}
                    }
                },
                {
                    "id": "coding",
                    "name": "Coding",
                    "description": "Editor with sidebar and terminal",
                    "config": {
                        "sidebar": {"visible": True, "width": 250},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": True, "height": 250},
                        "aiPanel": {"visible": False}
                    }
                },
                {
                    "id": "debugging",
                    "name": "Debugging",
                    "description": "Full layout with larger terminal",
                    "config": {
                        "sidebar": {"visible": True, "width": 250},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": True, "height": 350},
                        "aiPanel": {"visible": True, "width": 380}
                    }
                },
                {
                    "id": "aiAssist",
                    "name": "AI Assist",
                    "description": "Editor with AI panel, no terminal",
                    "config": {
                        "sidebar": {"visible": True, "width": 250},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": False},
                        "aiPanel": {"visible": True, "width": 450}
                    }
                },
                {
                    "id": "minimal",
                    "name": "Minimal",
                    "description": "Editor and terminal only",
                    "config": {
                        "sidebar": {"visible": False},
                        "editorArea": {"visible": True},
                        "terminal": {"visible": True, "height": 200},
                        "aiPanel": {"visible": False}
                    }
                }
            ],
            "active": "default"
        }
        
        with open(layouts_dir / "layouts.json", 'w') as f:
            json.dump(layouts, f, indent=2)
    
    def _create_default_extensions_config(self) -> None:
        """Create default extensions configuration"""
        extensions_dir = self.appdata_path / "extensions"
        
        extensions_config = {
            "installed": [
                {
                    "id": 1,
                    "name": "Python Linter",
                    "version": "1.0.0",
                    "enabled": True,
                    "description": "Python code linting and analysis",
                    "author": "AutoPilot"
                },
                {
                    "id": 2,
                    "name": "Git Integration",
                    "version": "2.1.0",
                    "enabled": True,
                    "description": "Git version control integration",
                    "author": "AutoPilot"
                },
                {
                    "id": 3,
                    "name": "REST Client",
                    "version": "0.9.0",
                    "enabled": True,
                    "description": "Test REST APIs directly from the IDE",
                    "author": "AutoPilot"
                },
                {
                    "id": 4,
                    "name": "TypeScript Support",
                    "version": "1.2.0",
                    "enabled": True,
                    "description": "TypeScript language support",
                    "author": "AutoPilot"
                }
            ],
            "available": [
                {
                    "id": 5,
                    "name": "Database Explorer",
                    "version": "2.0.0",
                    "description": "Browse and query databases",
                    "author": "AutoPilot"
                },
                {
                    "id": 6,
                    "name": "API Tester",
                    "version": "1.8.0",
                    "description": "Test REST APIs directly",
                    "author": "AutoPilot"
                },
                {
                    "id": 7,
                    "name": "Code Formatter",
                    "version": "3.1.0",
                    "description": "Auto-format code with multiple styles",
                    "author": "AutoPilot"
                },
                {
                    "id": 8,
                    "name": "Theme Pack",
                    "version": "1.0.0",
                    "description": "Additional color themes",
                    "author": "AutoPilot"
                }
            ]
        }
        
        with open(extensions_dir / "extensions.json", 'w') as f:
            json.dump(extensions_config, f, indent=2)
    
    def _create_projects_index(self) -> None:
        """Create projects index file"""
        projects_dir = self.appdata_path / "projects"
        
        projects_index = {
            "projects": [],
            "recent": [],
            "favorites": []
        }
        
        with open(projects_dir / "projects.json", 'w') as f:
            json.dump(projects_index, f, indent=2)
    
    def get_appdata_info(self) -> Dict:
        """Get AppData folder information"""
        if not self.appdata_path.exists():
            return {
                "status": "error",
                "message": "AppData folder not initialized"
            }
        
        return {
            "status": "success",
            "appdata_path": str(self.appdata_path),
            "folders": {
                "themes": str(self.appdata_path / "themes"),
                "extensions": str(self.appdata_path / "extensions"),
                "layouts": str(self.appdata_path / "layouts"),
                "projects": str(self.appdata_path / "projects")
            }
        }
    
    def load_themes(self) -> Dict:
        """Load all available themes"""
        themes_file = self.appdata_path / "themes" / "themes.json"
        
        if not themes_file.exists():
            return {"status": "error", "message": "Themes file not found"}
        
        try:
            with open(themes_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def load_layouts(self) -> Dict:
        """Load all available layouts"""
        layouts_file = self.appdata_path / "layouts" / "layouts.json"
        
        if not layouts_file.exists():
            return {"status": "error", "message": "Layouts file not found"}
        
        try:
            with open(layouts_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def load_extensions(self) -> Dict:
        """Load extensions configuration"""
        extensions_file = self.appdata_path / "extensions" / "extensions.json"
        
        if not extensions_file.exists():
            return {"status": "error", "message": "Extensions file not found"}
        
        try:
            with open(extensions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def load_projects(self) -> Dict:
        """Load projects index"""
        projects_file = self.appdata_path / "projects" / "projects.json"
        
        if not projects_file.exists():
            return {"status": "error", "message": "Projects file not found"}
        
        try:
            with open(projects_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def save_extensions(self, data: Dict) -> Dict:
        """Save extensions configuration"""
        extensions_file = self.appdata_path / "extensions" / "extensions.json"
        
        try:
            with open(extensions_file, 'w') as f:
                json.dump(data, f, indent=2)
            return {"status": "success", "message": "Extensions saved"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def save_projects(self, data: Dict) -> Dict:
        """Save projects index"""
        projects_file = self.appdata_path / "projects" / "projects.json"
        
        try:
            with open(projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            return {"status": "success", "message": "Projects saved"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def add_project(self, project_data: Dict) -> Dict:
        """Add a new project to the index"""
        projects = self.load_projects()
        
        if "status" in projects and projects["status"] == "error":
            return projects
        
        try:
            projects["projects"].append(project_data)
            return self.save_projects(projects)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_theme(self, theme_id: str) -> Dict:
        """Get a specific theme"""
        themes_dir = self.appdata_path / "themes"
        theme_file = themes_dir / f"{theme_id}.json"
        
        if not theme_file.exists():
            return {"status": "error", "message": f"Theme '{theme_id}' not found"}
        
        try:
            with open(theme_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instance
appdata_manager = AppDataManager()
