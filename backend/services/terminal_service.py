"""
Terminal Service
Business logic for terminal command execution with comprehensive error handling
"""

import subprocess
import os
from typing import Dict, List, Optional
from datetime import datetime
from flask import current_app


class TerminalService:
    """Service for executing terminal commands with security and error handling"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.max_history: int = 100
    
    def execute_command(
        self, 
        command: str, 
        cwd: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Execute a terminal command with security checks
        
        Args:
            command: Command to execute
            cwd: Working directory (optional)
            timeout: Command timeout in seconds (optional, uses config default)
            
        Returns:
            Dict with stdout, stderr, returncode, command, and cwd
            
        Raises:
            TimeoutError: If command execution exceeds timeout
            PermissionError: If working directory is not accessible
        """
        try:
            # Validate and set working directory
            if cwd:
                if not os.path.isdir(cwd):
                    raise ValueError(f"Working directory does not exist: {cwd}")
                if not os.access(cwd, os.R_OK | os.X_OK):
                    raise PermissionError(f"No access to working directory: {cwd}")
                working_dir = cwd
            else:
                working_dir = str(current_app.config.get('PROJECTS_DIR', os.getcwd()))
            
            # Get timeout from config if not provided
            if timeout is None:
                timeout = current_app.config.get('TERMINAL_TIMEOUT', 30)
            
            # Validate timeout
            max_timeout = current_app.config.get('TERMINAL_MAX_TIMEOUT', 300)
            if timeout > max_timeout:
                timeout = max_timeout
            
            current_app.logger.info(
                f"Executing command: {command[:100]} (cwd: {working_dir}, timeout: {timeout}s)"
            )
            
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()  # Use current environment
            )
            
            # Limit output size
            max_output = current_app.config.get('TERMINAL_MAX_OUTPUT', 10000)
            stdout = result.stdout[:max_output] if result.stdout else ''
            stderr = result.stderr[:max_output] if result.stderr else ''
            
            if len(result.stdout) > max_output:
                stdout += f"\n... (output truncated, {len(result.stdout) - max_output} chars omitted)"
            if len(result.stderr) > max_output:
                stderr += f"\n... (output truncated, {len(result.stderr) - max_output} chars omitted)"
            
            response = {
                'stdout': stdout,
                'stderr': stderr,
                'returncode': result.returncode,
                'command': command,
                'cwd': working_dir,
                'success': result.returncode == 0
            }
            
            # Add to history
            self._add_to_history(command, response)
            
            if result.returncode == 0:
                current_app.logger.info(f"Command executed successfully: {command[:50]}")
            else:
                current_app.logger.warning(
                    f"Command failed with code {result.returncode}: {command[:50]}"
                )
            
            return response
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout} seconds"
            current_app.logger.warning(f"{error_msg}: {command[:50]}")
            
            response = {
                'stdout': e.stdout.decode() if e.stdout else '',
                'stderr': error_msg,
                'returncode': 124,  # Standard timeout exit code
                'command': command,
                'cwd': working_dir if cwd else os.getcwd(),
                'success': False
            }
            
            self._add_to_history(command, response)
            raise TimeoutError(error_msg)
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}"
            current_app.logger.error(f"{error_msg}: {command[:50]}")
            
            response = {
                'stdout': '',
                'stderr': error_msg,
                'returncode': 126,  # Standard permission denied exit code
                'command': command,
                'cwd': cwd or os.getcwd(),
                'success': False
            }
            
            self._add_to_history(command, response)
            raise
            
        except ValueError as e:
            error_msg = str(e)
            current_app.logger.error(f"Validation error: {error_msg}")
            
            return {
                'stdout': '',
                'stderr': error_msg,
                'returncode': 1,
                'command': command,
                'cwd': cwd or os.getcwd(),
                'success': False
            }
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            current_app.logger.error(f"{error_msg}: {command[:50]}", exc_info=True)
            
            response = {
                'stdout': '',
                'stderr': error_msg,
                'returncode': 1,
                'command': command,
                'cwd': cwd or os.getcwd(),
                'success': False
            }
            
            self._add_to_history(command, response)
            return response
    
    def _add_to_history(self, command: str, result: Dict[str, any]) -> None:
        """
        Add command to history
        
        Args:
            command: Executed command
            result: Command execution result
        """
        try:
            self.history.append({
                'command': command,
                'returncode': result.get('returncode'),
                'success': result.get('success', False),
                'cwd': result.get('cwd'),
                'timestamp': self._get_timestamp()
            })
            
            # Limit history size
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
                
        except Exception as e:
            current_app.logger.error(f"Error adding to history: {e}")
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get command history
        
        Args:
            limit: Maximum number of history items to return (optional)
            
        Returns:
            List of command history entries
        """
        try:
            if limit and limit > 0:
                return self.history[-limit:]
            return self.history
        except Exception as e:
            current_app.logger.error(f"Error getting history: {e}")
            return []
    
    def clear_history(self) -> None:
        """Clear command history"""
        try:
            self.history = []
            current_app.logger.info("Terminal history cleared")
        except Exception as e:
            current_app.logger.error(f"Error clearing history: {e}")
    
    def get_history_count(self) -> int:
        """
        Get number of commands in history
        
        Returns:
            Number of history entries
        """
        return len(self.history)
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp string
        """
        return datetime.now().isoformat()
    
    def validate_working_directory(self, cwd: str) -> tuple[bool, Optional[str]]:
        """
        Validate working directory
        
        Args:
            cwd: Working directory path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not cwd:
                return False, "Working directory cannot be empty"
            
            if not os.path.exists(cwd):
                return False, f"Directory does not exist: {cwd}"
            
            if not os.path.isdir(cwd):
                return False, f"Path is not a directory: {cwd}"
            
            if not os.access(cwd, os.R_OK | os.X_OK):
                return False, f"No access to directory: {cwd}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating directory: {str(e)}"
