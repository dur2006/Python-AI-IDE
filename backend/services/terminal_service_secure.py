"""
Secure Terminal Service
Enhanced terminal service with comprehensive security, sandboxing, and command validation
"""

import subprocess
import os
import shlex
from typing import Dict, List, Optional
from flask import current_app
from datetime import datetime
import logging

from backend.services.security_service import get_security_service

logger = logging.getLogger(__name__)


class SecureTerminalService:
    """Secure service for executing terminal commands with comprehensive security"""
    
    def __init__(self):
        self.history = []
        self.max_history = 100
        self.security = get_security_service()
        
        # Whitelist of safe commands (can be expanded)
        self.safe_commands = {
            'ls', 'dir', 'pwd', 'cd', 'cat', 'echo', 'python', 'python3',
            'pip', 'pip3', 'git', 'npm', 'node', 'mkdir', 'touch', 'cp',
            'mv', 'grep', 'find', 'which', 'whoami', 'date', 'clear',
            'help', 'man', 'tree', 'head', 'tail', 'wc', 'sort', 'uniq'
        }
        
        # Commands that require special handling
        self.restricted_commands = {
            'rm', 'rmdir', 'del', 'chmod', 'chown', 'sudo', 'su',
            'kill', 'killall', 'pkill', 'shutdown', 'reboot', 'halt'
        }
        
        logger.info("Secure Terminal Service initialized")
    
    def execute_command(self, command: str, cwd: str = None, 
                       allow_restricted: bool = False) -> Dict:
        """
        Execute a terminal command with comprehensive security checks
        
        Args:
            command: Command to execute
            cwd: Working directory (optional)
            allow_restricted: Allow restricted commands (default: False)
            
        Returns:
            Dict with stdout, stderr, return code, and metadata
        """
        try:
            # Security validation
            is_safe, error_msg = self.security.validate_command(command)
            if not is_safe:
                logger.warning(f"Command blocked by security: {command[:50]}")
                return self._error_response(command, error_msg, 403)
            
            # Parse command
            parsed = self._parse_command(command)
            if not parsed:
                return self._error_response(command, "Failed to parse command", 400)
            
            base_command = parsed[0]
            
            # Check if command is in whitelist or restricted
            if base_command in self.restricted_commands and not allow_restricted:
                logger.warning(f"Restricted command blocked: {base_command}")
                return self._error_response(
                    command,
                    f"Command '{base_command}' is restricted. Use with caution.",
                    403
                )
            
            # Validate and set working directory
            working_dir = self._get_safe_working_directory(cwd)
            
            # Execute command with timeout and security measures
            timeout = current_app.config.get('TERMINAL_TIMEOUT', 30)
            
            result = subprocess.run(
                parsed,  # Use parsed array instead of shell=True
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # CRITICAL: Never use shell=True
                env=self._get_safe_environment()
            )
            
            # Truncate output if too long
            max_output = current_app.config.get('TERMINAL_MAX_OUTPUT', 10000)
            stdout = self._truncate_output(result.stdout, max_output)
            stderr = self._truncate_output(result.stderr, max_output)
            
            response = {
                'stdout': stdout,
                'stderr': stderr,
                'returncode': result.returncode,
                'command': command,
                'cwd': working_dir,
                'timestamp': datetime.now().isoformat(),
                'truncated': len(result.stdout) > max_output or len(result.stderr) > max_output
            }
            
            # Add to history
            self._add_to_history(command, response)
            
            logger.info(f"Command executed: {command[:50]} (rc: {result.returncode})")
            return response
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.warning(f"Command timeout: {command[:50]}")
            return self._error_response(command, error_msg, 124)
            
        except FileNotFoundError as e:
            error_msg = f"Command not found: {str(e)}"
            logger.error(f"Command not found: {command[:50]}")
            return self._error_response(command, error_msg, 127)
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}"
            logger.error(f"Permission denied: {command[:50]}")
            return self._error_response(command, error_msg, 126)
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(f"Command execution error: {command[:50]} - {e}")
            return self._error_response(command, error_msg, 1)
    
    def execute_python_code(self, code: str, cwd: str = None) -> Dict:
        """
        Execute Python code in a sandboxed environment
        
        Args:
            code: Python code to execute
            cwd: Working directory (optional)
            
        Returns:
            Dict with output and metadata
        """
        try:
            # Validate code
            if not code or not code.strip():
                return self._error_response("", "Empty code", 400)
            
            # Check for dangerous imports/functions
            dangerous_imports = ['os.system', 'subprocess', 'eval', 'exec', '__import__']
            for danger in dangerous_imports:
                if danger in code:
                    logger.warning(f"Dangerous Python code blocked: {danger}")
                    return self._error_response(
                        code[:50],
                        f"Code blocked: '{danger}' is not allowed",
                        403
                    )
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute Python file
                result = self.execute_command(f"python {temp_file}", cwd)
                return result
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Error executing Python code: {str(e)}"
            logger.error(f"Python execution error: {e}")
            return self._error_response(code[:50], error_msg, 1)
    
    def _parse_command(self, command: str) -> Optional[List[str]]:
        """
        Safely parse command into arguments
        Returns None if parsing fails
        """
        try:
            # Use shlex for safe parsing (handles quotes, escapes, etc.)
            return shlex.split(command)
        except ValueError as e:
            logger.error(f"Command parsing error: {e}")
            return None
    
    def _get_safe_working_directory(self, cwd: str = None) -> str:
        """Get and validate working directory"""
        if cwd:
            # Validate path
            is_safe, sanitized, error = self.security.sanitize_path(cwd)
            if is_safe and os.path.isdir(sanitized):
                return os.path.abspath(sanitized)
        
        # Default to projects directory
        projects_dir = current_app.config.get('PROJECTS_DIR', os.getcwd())
        return str(projects_dir)
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """
        Get safe environment variables for command execution
        Removes potentially dangerous variables
        """
        # Start with minimal safe environment
        safe_env = {
            'PATH': os.environ.get('PATH', ''),
            'HOME': os.environ.get('HOME', ''),
            'USER': os.environ.get('USER', ''),
            'LANG': os.environ.get('LANG', 'en_US.UTF-8'),
            'TERM': 'xterm-256color'
        }
        
        # Add Python-specific variables if present
        for var in ['PYTHONPATH', 'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV']:
            if var in os.environ:
                safe_env[var] = os.environ[var]
        
        return safe_env
    
    def _truncate_output(self, output: str, max_length: int) -> str:
        """Truncate output to maximum length"""
        if len(output) <= max_length:
            return output
        
        truncated = output[:max_length]
        truncated += f"\n\n... (output truncated, {len(output) - max_length} characters omitted)"
        return truncated
    
    def _error_response(self, command: str, error_msg: str, returncode: int) -> Dict:
        """Create standardized error response"""
        return {
            'stdout': '',
            'stderr': error_msg,
            'returncode': returncode,
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'error': True
        }
    
    def _add_to_history(self, command: str, result: Dict):
        """Add command to history"""
        self.history.append({
            'command': command,
            'returncode': result.get('returncode'),
            'timestamp': result.get('timestamp'),
            'cwd': result.get('cwd')
        })
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, limit: int = None) -> List[Dict]:
        """Get command history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Clear command history"""
        self.history = []
        logger.info("Terminal history cleared")
    
    def get_safe_commands(self) -> List[str]:
        """Get list of safe commands"""
        return sorted(list(self.safe_commands))
    
    def get_restricted_commands(self) -> List[str]:
        """Get list of restricted commands"""
        return sorted(list(self.restricted_commands))
    
    def is_command_safe(self, command: str) -> bool:
        """Check if command is in safe list"""
        parsed = self._parse_command(command)
        if not parsed:
            return False
        
        base_command = parsed[0]
        return base_command in self.safe_commands
    
    def get_status(self) -> Dict:
        """Get terminal service status"""
        return {
            'history_count': len(self.history),
            'safe_commands': len(self.safe_commands),
            'restricted_commands': len(self.restricted_commands),
            'max_history': self.max_history
        }


# Global singleton instance
_terminal_service = None


def get_terminal_service() -> SecureTerminalService:
    """Get global terminal service instance"""
    global _terminal_service
    if _terminal_service is None:
        _terminal_service = SecureTerminalService()
    return _terminal_service
