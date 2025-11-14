"""
Terminal API Blueprint
Handles terminal command execution endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from backend.services.terminal_service import TerminalService

terminal_bp = Blueprint('terminal', __name__)
terminal_service = TerminalService()


@terminal_bp.route('/execute', methods=['POST'])
def execute_command():
    """Execute a terminal command"""
    try:
        data = request.get_json()
        command = data.get('command')
        cwd = data.get('cwd')
        
        if not command:
            return jsonify({'error': 'Command is required'}), 400
        
        result = terminal_service.execute_command(command, cwd)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error executing command: {e}")
        return jsonify({'error': str(e)}), 500


@terminal_bp.route('/history', methods=['GET'])
def get_history():
    """Get command history"""
    try:
        history = terminal_service.get_history()
        return jsonify({'history': history}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching history: {e}")
        return jsonify({'error': str(e)}), 500


@terminal_bp.route('/clear', methods=['POST'])
def clear_terminal():
    """Clear terminal history"""
    try:
        terminal_service.clear_history()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        current_app.logger.error(f"Error clearing terminal: {e}")
        return jsonify({'error': str(e)}), 500
