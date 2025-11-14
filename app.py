import os
import json
import subprocess
from pathlib import Path
from flask import Flask, jsonify, render_template_string, send_from_directory, request
from flask_socketio import SocketIO, emit
from config import config
from appdata_manager import appdata_manager

app = Flask(__name__, static_folder='.')
app.config.from_object(config['development'])
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AppData on startup
print("[*] Initializing AppData folder structure...")
init_result = appdata_manager.initialize()
print(f"[*] AppData Status: {init_result['status']}")
print(f"[*] AppData Path: {appdata_manager.appdata_path}")

# API Routes - AppData Management
@app.route('/api/appdata/init', methods=['POST'])
def init_appdata():
    """Initialize AppData folder structure"""
    result = appdata_manager.initialize()
    return jsonify(result)

@app.route('/api/appdata/info', methods=['GET'])
def get_appdata_info():
    """Get AppData folder information"""
    return jsonify(appdata_manager.get_appdata_info())

# API Routes - Themes
@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get all available themes"""
    themes = appdata_manager.load_themes()
    return jsonify(themes)

@app.route('/api/themes/<theme_id>', methods=['GET'])
def get_theme(theme_id):
    """Get a specific theme"""
    theme = appdata_manager.get_theme(theme_id)
    return jsonify(theme)

# API Routes - Layouts
@app.route('/api/layouts', methods=['GET'])
def get_layouts():
    """Get all available layouts"""
    layouts = appdata_manager.load_layouts()
    return jsonify(layouts)

# API Routes - Extensions
@app.route('/api/extensions', methods=['GET'])
def get_extensions():
    """Get all extensions"""
    extensions = appdata_manager.load_extensions()
    return jsonify(extensions)

@app.route('/api/extensions/<int:ext_id>/toggle', methods=['POST'])
def toggle_extension(ext_id):
    """Toggle extension enabled/disabled status"""
    data = appdata_manager.load_extensions()
    
    if "status" in data and data["status"] == "error":
        return jsonify(data), 400
    
    for ext in data['installed']:
        if ext['id'] == ext_id:
            ext['enabled'] = not ext['enabled']
            result = appdata_manager.save_extensions(data)
            if result['status'] == 'success':
                return jsonify({"status": "success", "extension": ext})
            else:
                return jsonify(result), 500
    
    return jsonify({"status": "error", "message": "Extension not found"}), 404

@app.route('/api/extensions/<int:ext_id>/install', methods=['POST'])
def install_extension(ext_id):
    """Install an extension"""
    data = appdata_manager.load_extensions()
    
    if "status" in data and data["status"] == "error":
        return jsonify(data), 400
    
    for ext in data['available']:
        if ext['id'] == ext_id:
            ext['enabled'] = True
            data['installed'].append(ext)
            data['available'].remove(ext)
            result = appdata_manager.save_extensions(data)
            if result['status'] == 'success':
                return jsonify({"status": "success", "extension": ext})
            else:
                return jsonify(result), 500
    
    return jsonify({"status": "error", "message": "Extension not found"}), 404

@app.route('/api/extensions/<int:ext_id>/uninstall', methods=['POST'])
def uninstall_extension(ext_id):
    """Uninstall an extension"""
    data = appdata_manager.load_extensions()
    
    if "status" in data and data["status"] == "error":
        return jsonify(data), 400
    
    for ext in data['installed']:
        if ext['id'] == ext_id:
            data['available'].append({
                "id": ext['id'],
                "name": ext['name'],
                "version": ext['version'],
                "description": f"Uninstalled {ext['name']}"
            })
            data['installed'].remove(ext)
            result = appdata_manager.save_extensions(data)
            if result['status'] == 'success':
                return jsonify({"status": "success"})
            else:
                return jsonify(result), 500
    
    return jsonify({"status": "error", "message": "Extension not found"}), 404

# API Routes - Projects
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get list of projects"""
    projects = appdata_manager.load_projects()
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    project_data = request.get_json()
    result = appdata_manager.add_project(project_data)
    
    if result['status'] == 'success':
        return jsonify({"status": "success", "project": project_data}), 201
    else:
        return jsonify(result), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get file tree structure"""
    return jsonify({
        "files": [
            {"name": "main.py", "type": "file", "path": "main.py"},
            {"name": "src", "type": "folder", "path": "src", "children": [
                {"name": "utils.py", "type": "file", "path": "src/utils.py"},
                {"name": "config.py", "type": "file", "path": "src/config.py"}
            ]},
            {"name": "README.md", "type": "file", "path": "README.md"}
        ]
    })

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('response', {'data': 'Connected to backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('terminal_execute')
def handle_terminal_command(data):
    """Execute terminal command"""
    command = data.get('command', '')
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        emit('terminal_output', {
            'stdout': result.stdout,
            'stderr': result.stderr
        }, broadcast=True)
    except subprocess.TimeoutExpired:
        emit('terminal_output', {
            'stderr': 'Command timed out'
        }, broadcast=True)
    except Exception as e:
        emit('terminal_output', {
            'stderr': str(e)
        }, broadcast=True)

@socketio.on('ai_message')
def handle_ai_message(data):
    """Handle AI assistant messages"""
    message = data.get('message', '')
    mode = data.get('mode', 'Chat')
    
    # Simple AI response logic
    responses = {
        "Chat": f"I received your message: {message}",
        "Explain": f"Explaining: {message}",
        "Debug": f"Debugging: {message}",
        "Refactor": f"Refactoring: {message}"
    }
    
    response = responses.get(mode, f"Processing: {message}")
    emit('ai_response', {'message': response}, broadcast=True)

if __name__ == '__main__':
    print("=" * 50)
    print("  AutoPilot IDE - Backend Server")
    print("=" * 50)
    print("\n[*] Starting server on http://localhost:5000")
    print("[*] Open your browser and navigate to http://localhost:5000")
    print("[*] Press Ctrl+C to stop the server\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
