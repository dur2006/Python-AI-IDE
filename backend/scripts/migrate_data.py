#!/usr/bin/env python3
"""
Data Migration Script
Migrates existing separate JSON files (projects.json, extensions.json) 
into the unified AppData Manager system.

This script is safe to run multiple times - it will only migrate data if needed.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def log(message: str, level: str = "INFO"):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def backup_file(file_path: Path) -> bool:
    """Create backup of a file"""
    if not file_path.exists():
        return False
    
    backup_path = file_path.with_suffix(f'.json.backup.{int(datetime.now().timestamp())}')
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        log(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        log(f"Error creating backup: {e}", "ERROR")
        return False


def load_json(file_path: Path, default=None):
    """Load JSON file safely"""
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading {file_path}: {e}", "ERROR")
        return default


def save_json(file_path: Path, data):
    """Save JSON file safely"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"Error saving {file_path}: {e}", "ERROR")
        return False


def migrate_projects(data_dir: Path) -> bool:
    """Migrate projects.json to AppData format"""
    old_projects_file = data_dir / 'projects.json'
    new_projects_file = data_dir / 'projects.json'
    
    # Check if old format exists
    if not old_projects_file.exists():
        log("No projects.json found - will be created by AppData Manager")
        return True
    
    # Load existing projects
    projects = load_json(old_projects_file, [])
    if not projects:
        log("No projects to migrate")
        return True
    
    log(f"Found {len(projects)} projects to verify")
    
    # Ensure all projects have required fields
    migrated_count = 0
    for project in projects:
        if 'id' not in project:
            project['id'] = f"project-{int(datetime.now().timestamp())}"
            migrated_count += 1
        if 'createdAt' not in project:
            project['createdAt'] = datetime.now().isoformat()
            migrated_count += 1
        if 'lastOpened' not in project:
            project['lastOpened'] = datetime.now().isoformat()
            migrated_count += 1
        if 'files' not in project:
            project['files'] = []
            migrated_count += 1
    
    if migrated_count > 0:
        # Backup old file
        backup_file(old_projects_file)
        
        # Save updated projects
        if save_json(new_projects_file, projects):
            log(f"✅ Migrated {len(projects)} projects (updated {migrated_count} fields)")
            return True
        else:
            log("❌ Failed to save migrated projects", "ERROR")
            return False
    else:
        log(f"✅ All {len(projects)} projects already in correct format")
        return True


def migrate_extensions(data_dir: Path) -> bool:
    """Migrate extensions.json to AppData format"""
    old_extensions_file = data_dir / 'extensions.json'
    new_extensions_file = data_dir / 'extensions.json'
    
    # Check if old format exists
    if not old_extensions_file.exists():
        log("No extensions.json found - will be created by AppData Manager")
        return True
    
    # Load existing extensions
    extensions_data = load_json(old_extensions_file)
    
    # Handle old format with 'installed' and 'available' keys
    if isinstance(extensions_data, dict) and ('installed' in extensions_data or 'available' in extensions_data):
        log("Found old extensions format with 'installed' and 'available' keys")
        
        # Backup old file
        backup_file(old_extensions_file)
        
        # Merge installed and available into single list
        installed = extensions_data.get('installed', [])
        available = extensions_data.get('available', [])
        
        # Mark installed extensions
        for ext in installed:
            ext['installed'] = True
            if 'enabled' not in ext:
                ext['enabled'] = True
        
        # Mark available extensions
        for ext in available:
            ext['installed'] = False
            ext['enabled'] = False
        
        # Combine all extensions
        all_extensions = installed + available
        
        # Save new format
        if save_json(new_extensions_file, all_extensions):
            log(f"✅ Migrated {len(all_extensions)} extensions ({len(installed)} installed, {len(available)} available)")
            return True
        else:
            log("❌ Failed to save migrated extensions", "ERROR")
            return False
    
    # Already in new format (list of extensions)
    elif isinstance(extensions_data, list):
        log(f"✅ Extensions already in correct format ({len(extensions_data)} extensions)")
        return True
    
    else:
        log("❌ Unknown extensions format", "ERROR")
        return False


def verify_appdata_structure(data_dir: Path) -> bool:
    """Verify AppData Manager files exist and are valid"""
    required_files = {
        'projects.json': list,
        'extensions.json': list,
        'themes.json': list,
        'layouts.json': list,
        'settings.json': dict
    }
    
    log("\nVerifying AppData structure...")
    all_valid = True
    
    for filename, expected_type in required_files.items():
        file_path = data_dir / filename
        if file_path.exists():
            data = load_json(file_path)
            if isinstance(data, expected_type):
                count = len(data) if isinstance(data, (list, dict)) else 0
                log(f"  ✅ {filename}: Valid ({count} items)")
            else:
                log(f"  ❌ {filename}: Invalid type (expected {expected_type.__name__})", "ERROR")
                all_valid = False
        else:
            log(f"  ⚠️  {filename}: Not found (will be created by AppData Manager)", "WARNING")
    
    return all_valid


def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("  AutoPilot IDE - Data Migration Script")
    print("="*60 + "\n")
    
    # Get data directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    data_dir = project_root / 'data'
    
    log(f"Project root: {project_root}")
    log(f"Data directory: {data_dir}")
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    log(f"Data directory ready: {data_dir}")
    
    # Run migrations
    log("\n--- Starting Migration ---\n")
    
    success = True
    
    # Migrate projects
    log("Step 1: Migrating projects...")
    if not migrate_projects(data_dir):
        success = False
    
    # Migrate extensions
    log("\nStep 2: Migrating extensions...")
    if not migrate_extensions(data_dir):
        success = False
    
    # Verify structure
    log("\nStep 3: Verifying AppData structure...")
    if not verify_appdata_structure(data_dir):
        success = False
    
    # Summary
    print("\n" + "="*60)
    if success:
        log("✅ Migration completed successfully!", "SUCCESS")
        log("\nYou can now start the application with: python app.py")
    else:
        log("❌ Migration completed with errors", "ERROR")
        log("Please check the errors above and try again")
        sys.exit(1)
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
