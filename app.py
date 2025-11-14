import os
import json
import subprocess
from pathlib import Path
from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
from config import config

app = Flask(__name__, static_folder='.')
app.config.from_object(config['development'])
socketio = SocketIO(app, cors_allowed_origins="*")

# Store for extensions
EXTENSIONS_FILE = Path(__file__).parent / "extensions.json"

def load_extensions():
    """Load extensions from JSON file"""
    if EXTENSIONS_FILE.exists():
        with open(EXTENSIONS_FILE, 'r') as f:
            return json.load(f)
    return {"installed": [], "available": []}

def save_extensions(data):
    """Save extensions to JSON file"""
    with open(EXTENSIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize extensions file if it doesn't exist
if not EXTENSIONS_FILE.exists():
    initial_extensions = {
        "installed": [
            {"id": 1, "name": "Python Linter", "version": "1.0.0", "enabled": True},
            {"id": 2, "name": "Git Integration", "version": "2.1.0", "enabled": True},
            {"id": 3, "name": "REST Client", "version": "0.9.0", "enabled": True},
            {"id": 4, "name": "TypeScript Support", "version": "1.2.0", "enabled": True}
        ],
        "available": [
            {"id": 5, "name": "Database Explorer", "version": "2.0.0", "description": "Browse and query databases"},
            {"id": 6, "name": "API Tester", "version": "1.8.0", "description": "Test REST APIs directly"},
            {"id": 7, "name": "Code Formatter", "version": "3.1.0", "description": "Auto-format code with multiple styles"},
            {"id": 8, "name": "Theme Pack", "version": "1.0.0", "description": "Additional color themes"}
        ]
    }
    save_extensions(initial_extensions)

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

# API Routes
@app.route('/api/extensions', methods=['GET'])
def get_extensions():
    """Get all extensions"""
    return jsonify(load_extensions())

@app.route('/api/extensions/<int:ext_id>/toggle', methods=['POST'])
def toggle_extension(ext_id):
    """Toggle extension enabled/disabled status"""
    data = load_extensions()
    for ext in data['installed']:
        if ext['id'] == ext_id:
            ext['enabled'] = not ext['enabled']
            save_extensions(data)
            return jsonify({"status": "success", "extension": ext})
    return jsonify({"status": "error", "message": "Extension not found"}), 404

@app.route('/api/extensions/<int:ext_id>/install', methods=['POST'])
def install_extension(ext_id):
    """Install an extension"""
    data = load_extensions()
    for ext in data['available']:
        if ext['id'] == ext_id:
            ext['enabled'] = True
            data['installed'].append(ext)
            data['available'].remove(ext)
            save_extensions(data)
            return jsonify({"status": "success", "extension": ext})
    return jsonify({"status": "error", "message": "Extension not found"}), 404

@app.route('/api/extensions/<int:ext_id>/uninstall', methods=['POST'])
def uninstall_extension(ext_id):
    """Uninstall an extension"""
    data = load_extensions()
    for ext in data['installed']:
        if ext['id'] == ext_id:
            data['available'].append({
                "id": ext['id'],
                "name": ext['name'],
                "version": ext['version'],
                "description": f"Uninstalled {ext['name']}"
            })
            data['installed'].remove(ext)
            save_extensions(data)
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Extension not found"}), 404

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get list of projects"""
    return jsonify({
        "projects": [
            {"id": 1, "name": "AutoPilot-Project", "path": "./projects/autopilot", "language": "Python"}
        ]
    })

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
