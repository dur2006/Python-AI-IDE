"""
Terminal API Blueprint
Handles terminal command execution with CRITICAL security measures
Prevents command injection, validates commands, and restricts dangerous operations
"""

from typing import Dict, Any, List
from flask import Blueprint, jsonify, request, current_app
from backend.services.terminal_service import TerminalService
from backend.utils.validators import Validator, require_json
import re

terminal_bp = Blueprint('terminal', __name__)
terminal_service = TerminalService()

# Dangerous commands that should NEVER be allowed
BLOCKED_COMMANDS = [
    'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs',
    'dd', 'shutdown', 'reboot', 'halt', 'poweroff',
    'kill', 'killall', 'pkill', 'taskkill',
    'chmod', 'chown', 'chgrp', 'passwd', 'sudo', 'su',
    'wget', 'curl', 'nc', 'netcat', 'telnet', 'ssh',
    'eval', 'exec', 'source', 'bash', 'sh', 'cmd',
    '>', '>>', '<', '|', '&', ';', '&&', '||',
    'reg', 'regedit', 'bcdedit', 'diskpart'
]

# Allowed safe commands for IDE operations
ALLOWED_COMMANDS = [
    'python', 'python3', 'pip', 'pip3',
    'node', 'npm', 'npx', 'yarn',
    'git', 'ls', 'dir', 'cd', 'pwd',
    'echo', 'cat', 'type', 'more', 'less',
    'grep', 'find', 'which', 'where',
    'env', 'set', 'export'
]


def validate_command(command: str) -> tuple[bool, str]:
    """
    Validate terminal command for security
    
    Args:
        command: Command string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not command or not command.strip():
        return False, "Command cannot be empty"
    
    # Sanitize command
    command = command.strip()
    
    # Check length
    if len(command) > 1000:
        return False, "Command too long (max 1000 characters)"
    
    # Check for null bytes
    if '\x00' in command:
        return False, "Command contains null bytes"
    
    # Check for command injection patterns
    injection_patterns = [
        r'[;&|`$()]',  # Shell metacharacters
        r'\$\(',       # Command substitution
        r'`',          # Backticks
        r'>\s*/',      # Redirect to root
        r'<\s*/',      # Read from root
        r'\|\s*\w',    # Pipe to command
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, command):
            return False, f"Command contains dangerous pattern: {pattern}"
    
    # Extract base command (first word)
    base_command = command.split()[0].lower()
    
    # Remove path if present
    if '/' in base_command or '\\' in base_command:
        base_command = base_command.split('/')[-1].split('\\')[-1]
    
    # Check if command is blocked
    for blocked in BLOCKED_COMMANDS:
        if blocked in base_command:
            return False, f"Command '{blocked}' is not allowed for security reasons"
    
    # Check if command is in allowed list
    is_allowed = False
    for allowed in ALLOWED_COMMANDS:
        if allowed in base_command:
            is_allowed = True
            break
    
    if not is_allowed:
        return False, f"Command '{base_command}' is not in the allowed list"
    
    return True, ""


@terminal_bp.route('/execute', methods=['POST'])
@require_json('command')
def execute_command() -> tuple[Dict[str, Any], int]:
    """
    Execute a terminal command with strict security validation
    
    Required JSON fields:
        - command: Command to execute (string)
        
    Optional JSON fields:
        - cwd: Working directory (string)
        - timeout: Command timeout in seconds (default: 30)
        
    Returns:
        JSON response with command output and HTTP status code
    """
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        cwd = data.get('cwd')
        timeout = data.get('timeout', 30)
        
        # Validate command
        is_valid, error_msg = validate_command(command)
        if not is_valid:
            current_app.logger.warning(f"Blocked dangerous command: {command}")
            return jsonify({
                'status': 'error',
                'error': error_msg,
                'field': 'command'
            }), 403
        
        # Validate working directory if provided
        if cwd:
            cwd = Validator.sanitize_string(cwd, max_length=500)
            is_valid, error_msg = Validator.validate_file_path(cwd, allow_absolute=True)
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'error': error_msg,
                    'field': 'cwd'
                }), 400
        
        # Validate timeout
        try:
            timeout = int(timeout)
            if timeout < 1 or timeout > 300:
                return jsonify({
                    'status': 'error',
                    'error': 'Timeout must be between 1 and 300 seconds',
                    'field': 'timeout'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'Timeout must be a valid integer',
                'field': 'timeout'
            }), 400
        
        # Execute command with timeout
        current_app.logger.info(f"Executing command: {command} (cwd: {cwd}, timeout: {timeout}s)")
        result = terminal_service.execute_command(command, cwd, timeout)
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except TimeoutError as e:
        current_app.logger.error(f"Command timeout: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Command execution timed out'
        }), 408
    except PermissionError as e:
        current_app.logger.error(f"Permission denied executing command: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Error executing command: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to execute command',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@terminal_bp.route('/history', methods=['GET'])
def get_history() -> tuple[Dict[str, Any], int]:
    """
    Get command history
    
    Query parameters:
        - limit: Maximum number of history items (default: 100)
        
    Returns:
        JSON response with command history and HTTP status code
    """
    try:
        # Get limit from query params
        limit = request.args.get('limit', '100')
        try:
            limit = int(limit)
            if limit < 1 or limit > 1000:
                limit = 100
        except ValueError:
            limit = 100
        
        history = terminal_service.get_history(limit=limit)
        
        return jsonify({
            'status': 'success',
            'data': history,
            'count': len(history) if isinstance(history, list) else 0
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching history: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch command history',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@terminal_bp.route('/clear', methods=['POST'])
def clear_terminal() -> tuple[Dict[str, Any], int]:
    """
    Clear terminal history
    
    Returns:
        JSON response with clear status and HTTP status code
    """
    try:
        terminal_service.clear_history()
        current_app.logger.info("Terminal history cleared")
        
        return jsonify({
            'status': 'success',
            'message': 'Terminal history cleared successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error clearing terminal: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to clear terminal history',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@terminal_bp.route('/allowed-commands', methods=['GET'])
def get_allowed_commands() -> tuple[Dict[str, Any], int]:
    """
    Get list of allowed commands
    
    Returns:
        JSON response with allowed commands list and HTTP status code
    """
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'allowed': sorted(ALLOWED_COMMANDS),
                'blocked': sorted(BLOCKED_COMMANDS)
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching allowed commands: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to fetch allowed commands',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500


@terminal_bp.route('/validate', methods=['POST'])
@require_json('command')
def validate_command_endpoint() -> tuple[Dict[str, Any], int]:
    """
    Validate a command without executing it
    
    Required JSON fields:
        - command: Command to validate (string)
        
    Returns:
        JSON response with validation result and HTTP status code
    """
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        is_valid, error_msg = validate_command(command)
        
        if is_valid:
            return jsonify({
                'status': 'success',
                'data': {
                    'valid': True,
                    'command': command
                }
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'data': {
                    'valid': False,
                    'command': command,
                    'reason': error_msg
                }
            }), 200
    except Exception as e:
        current_app.logger.error(f"Error validating command: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': 'Failed to validate command',
            'message': str(e) if current_app.debug else 'Internal server error'
        }), 500
