"""
Input Validation Utilities
Comprehensive validation for all user inputs to prevent security vulnerabilities
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class Validator:
    """Input validation utilities"""
    
    # Regex patterns
    PROJECT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\s]{1,100}$')
    FILE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]{1,255}$')
    PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\./\\]{1,500}$')
    ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,50}$')
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {'.exe', '.dll', '.so', '.dylib', '.bat', '.cmd', '.sh'}
    
    # Maximum sizes
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_PROJECT_NAME_LENGTH = 100
    MAX_PATH_LENGTH = 500
    
    @staticmethod
    def validate_project_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate project name
        
        Args:
            name: Project name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Project name is required"
        
        if not isinstance(name, str):
            return False, "Project name must be a string"
        
        if len(name) > Validator.MAX_PROJECT_NAME_LENGTH:
            return False, f"Project name must be less than {Validator.MAX_PROJECT_NAME_LENGTH} characters"
        
        if not Validator.PROJECT_NAME_PATTERN.match(name):
            return False, "Project name contains invalid characters. Use only letters, numbers, spaces, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_file_path(file_path: str, allow_absolute: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate file path for security
        
        Args:
            file_path: File path to validate
            allow_absolute: Whether to allow absolute paths
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path is required"
        
        if not isinstance(file_path, str):
            return False, "File path must be a string"
        
        if len(file_path) > Validator.MAX_PATH_LENGTH:
            return False, f"File path must be less than {Validator.MAX_PATH_LENGTH} characters"
        
        # Check for path traversal attempts
        if '..' in file_path:
            return False, "Path traversal detected. '..' is not allowed"
        
        # Check for null bytes
        if '\x00' in file_path:
            return False, "Null bytes not allowed in file path"
        
        # Check for absolute paths if not allowed
        if not allow_absolute:
            path_obj = Path(file_path)
            if path_obj.is_absolute():
                return False, "Absolute paths are not allowed"
        
        # Check file extension
        extension = Path(file_path).suffix.lower()
        if extension in Validator.DANGEROUS_EXTENSIONS:
            return False, f"File extension '{extension}' is not allowed for security reasons"
        
        return True, None
    
    @staticmethod
    def validate_id(id_value: str, field_name: str = "ID") -> Tuple[bool, Optional[str]]:
        """
        Validate ID format
        
        Args:
            id_value: ID to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not id_value:
            return False, f"{field_name} is required"
        
        if not isinstance(id_value, str):
            return False, f"{field_name} must be a string"
        
        if not Validator.ID_PATTERN.match(id_value):
            return False, f"{field_name} contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_content_length(content: str, max_length: int = MAX_FILE_SIZE) -> Tuple[bool, Optional[str]]:
        """
        Validate content length
        
        Args:
            content: Content to validate
            max_length: Maximum allowed length in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if content is None:
            return True, None  # Empty content is allowed
        
        if not isinstance(content, str):
            return False, "Content must be a string"
        
        content_bytes = len(content.encode('utf-8'))
        if content_bytes > max_length:
            return False, f"Content size ({content_bytes} bytes) exceeds maximum allowed size ({max_length} bytes)"
        
        return True, None
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: List[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON data structure
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if data is None:
            return False, "Request body is required"
        
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim to max length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value


def validate_request(*validators):
    """
    Decorator to validate request data
    
    Usage:
        @validate_request(
            ('project_name', Validator.validate_project_name),
            ('file_path', Validator.validate_file_path)
        )
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get request data
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.get_json(silent=True)
                if data is None:
                    return jsonify({'error': 'Invalid JSON in request body'}), 400
            else:
                data = {}
            
            # Merge with URL parameters
            data.update(kwargs)
            
            # Run validators
            for field_name, validator_func in validators:
                if field_name in data:
                    is_valid, error_msg = validator_func(data[field_name])
                    if not is_valid:
                        current_app.logger.warning(f"Validation failed for {field_name}: {error_msg}")
                        return jsonify({
                            'error': error_msg,
                            'field': field_name
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_json(*required_fields):
    """
    Decorator to require JSON body with specific fields
    
    Usage:
        @require_json('name', 'type')
        def my_endpoint():
            data = request.get_json()
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json(silent=True)
            
            is_valid, error_msg = Validator.validate_json_data(data, required_fields)
            if not is_valid:
                current_app.logger.warning(f"JSON validation failed: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
