"""
Terminal Service
Business logic for terminal command execution
"""

import subprocess
import os
from typing import Dict, List
from flask import current_app


class TerminalService:
    """Service for executing terminal commands"""
    
    def __init__(self):
        self.history = []
        self.max_history = 100
    
    def execute_command(self, command: str, cwd: str = None) -> Dict:
        """
        Execute a terminal command
        
        Args:
            command: Command to execute
            cwd: Working directory (optional)
            
        Returns:
            Dict with stdout, stderr, and return code
        """
        try:
            # Security: Basic command validation
            if self._is_dangerous_command(command):
                return {
                    'stdout': '',
                    'stderr': 'Command blocked for security reasons',
                    'returncode': 1,
                    'command': command
                }
            
            # Set working directory
            if cwd and os.path.isdir(cwd):
                working_dir = cwd
            else:
                working_dir = str(current_app.config.get('PROJECTS_DIR', os.getcwd()))
            
            # Execute command with timeout
            timeout = current_app.config.get('TERMINAL_TIMEOUT', 30)
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            response = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'command': command,
                'cwd': working_dir
            }
            
            # Add to history
            self._add_to_history(command, response)
            
            current_app.logger.info(f"Executed command: {command}")
            return response
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            current_app.logger.warning(error_msg)
            return {
                'stdout': '',
                'stderr': error_msg,
                'returncode': 124,
                'command': command
            }
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            current_app.logger.error(error_msg)
            return {
                'stdout': '',
                'stderr': error_msg,
                'returncode': 1,
                'command': command
            }
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        dangerous_patterns = [
            'rm -rf /',
            'mkfs',
            'dd if=',
            ':(){ :|:& };:',  # Fork bomb
            'chmod -R 777 /',
            'chown -R'
        ]
        
        command_lower = command.lower().strip()
        return any(pattern in command_lower for pattern in dangerous_patterns)
    
    def _add_to_history(self, command: str, result: Dict):
        """Add command to history"""
        self.history.append({
            'command': command,
            'returncode': result.get('returncode'),
            'timestamp': self._get_timestamp()
        })
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self) -> List[Dict]:
        """Get command history"""
        return self.history
    
    def clear_history(self):
        """Clear command history"""
        self.history = []
        current_app.logger.info("Terminal history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
