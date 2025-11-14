"""
Security Service
Comprehensive security layer for authentication, authorization, rate limiting, and input validation
"""

import re
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """Comprehensive security service for the application"""
    
    def __init__(self):
        self.rate_limit_store = {}  # IP -> [(timestamp, count)]
        self.blocked_ips = set()
        self.session_tokens = {}  # token -> {user_id, expires_at, ip}
        self.failed_login_attempts = {}  # IP -> [(timestamp)]
        
        # Security configuration
        self.max_requests_per_minute = 60
        self.max_failed_logins = 5
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour
        
        # Dangerous command patterns
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'mkfs',
            r'dd\s+if=',
            r':\(\)\{\s*:\|:&\s*\};:',  # Fork bomb
            r'chmod\s+-R\s+777\s+/',
            r'chown\s+-R',
            r'>\s*/dev/sda',
            r'wget.*\|.*sh',
            r'curl.*\|.*bash',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'subprocess\.call',
            r'os\.system',
        ]
        
        logger.info("Security Service initialized")
    
    # ==================== AUTHENTICATION ====================
    
    def generate_session_token(self, user_id: str, ip_address: str) -> str:
        """Generate a secure session token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        
        self.session_tokens[token] = {
            'user_id': user_id,
            'expires_at': expires_at,
            'ip': ip_address,
            'created_at': datetime.now()
        }
        
        logger.info(f"Session token generated for user: {user_id}")
        return token
    
    def validate_session_token(self, token: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Validate session token
        Returns: (is_valid, user_id)
        """
        if not token or token not in self.session_tokens:
            return False, None
        
        session = self.session_tokens[token]
        
        # Check expiration
        if datetime.now() > session['expires_at']:
            del self.session_tokens[token]
            logger.warning(f"Expired session token used")
            return False, None
        
        # Check IP address (optional, can be disabled for mobile users)
        if session['ip'] != ip_address:
            logger.warning(f"Session token used from different IP: {ip_address}")
            # Optionally allow or deny based on configuration
            # return False, None
        
        return True, session['user_id']
    
    def revoke_session_token(self, token: str) -> bool:
        """Revoke a session token"""
        if token in self.session_tokens:
            del self.session_tokens[token]
            logger.info(f"Session token revoked")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired session tokens"""
        now = datetime.now()
        expired_tokens = [
            token for token, session in self.session_tokens.items()
            if now > session['expires_at']
        ]
        
        for token in expired_tokens:
            del self.session_tokens[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
    
    # ==================== RATE LIMITING ====================
    
    def check_rate_limit(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if IP address is within rate limits
        Returns: (is_allowed, error_message)
        """
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            return False, "IP address is temporarily blocked due to excessive requests"
        
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old entries
        if ip_address not in self.rate_limit_store:
            self.rate_limit_store[ip_address] = []
        
        # Remove entries older than 1 minute
        self.rate_limit_store[ip_address] = [
            timestamp for timestamp in self.rate_limit_store[ip_address]
            if timestamp > minute_ago
        ]
        
        # Check rate limit
        request_count = len(self.rate_limit_store[ip_address])
        
        if request_count >= self.max_requests_per_minute:
            # Block IP temporarily
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP blocked due to rate limit: {ip_address}")
            return False, f"Rate limit exceeded. Maximum {self.max_requests_per_minute} requests per minute."
        
        # Add current request
        self.rate_limit_store[ip_address].append(now)
        
        return True, None
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"IP unblocked: {ip_address}")
    
    def cleanup_rate_limits(self):
        """Clean up old rate limit entries"""
        now = time.time()
        minute_ago = now - 60
        
        for ip in list(self.rate_limit_store.keys()):
            self.rate_limit_store[ip] = [
                timestamp for timestamp in self.rate_limit_store[ip]
                if timestamp > minute_ago
            ]
            
            if not self.rate_limit_store[ip]:
                del self.rate_limit_store[ip]
    
    # ==================== FAILED LOGIN TRACKING ====================
    
    def record_failed_login(self, ip_address: str) -> bool:
        """
        Record a failed login attempt
        Returns: True if IP should be locked out
        """
        now = time.time()
        lockout_window = now - self.lockout_duration
        
        # Initialize or clean old entries
        if ip_address not in self.failed_login_attempts:
            self.failed_login_attempts[ip_address] = []
        
        # Remove old attempts
        self.failed_login_attempts[ip_address] = [
            timestamp for timestamp in self.failed_login_attempts[ip_address]
            if timestamp > lockout_window
        ]
        
        # Add current attempt
        self.failed_login_attempts[ip_address].append(now)
        
        # Check if should lock out
        if len(self.failed_login_attempts[ip_address]) >= self.max_failed_logins:
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP locked out due to failed login attempts: {ip_address}")
            return True
        
        return False
    
    def clear_failed_logins(self, ip_address: str):
        """Clear failed login attempts for an IP"""
        if ip_address in self.failed_login_attempts:
            del self.failed_login_attempts[ip_address]
    
    # ==================== INPUT VALIDATION ====================
    
    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate terminal command for security
        Returns: (is_safe, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"
        
        # Check against dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Dangerous command blocked: {command[:50]}")
                return False, f"Command blocked for security reasons: potentially dangerous pattern detected"
        
        # Additional checks
        if len(command) > 10000:
            return False, "Command too long (max 10000 characters)"
        
        return True, None
    
    def sanitize_path(self, path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Sanitize and validate file path
        Returns: (is_safe, sanitized_path, error_message)
        """
        if not path:
            return False, "", "Empty path"
        
        # Remove null bytes
        path = path.replace('\0', '')
        
        # Check for path traversal attempts
        if '..' in path or path.startswith('/'):
            logger.warning(f"Path traversal attempt blocked: {path}")
            return False, "", "Invalid path: path traversal not allowed"
        
        # Check for absolute paths (should be relative)
        if path.startswith('~') or ':' in path:
            return False, "", "Invalid path: absolute paths not allowed"
        
        # Sanitize
        sanitized = path.strip()
        
        # Validate characters
        if not re.match(r'^[a-zA-Z0-9_\-./\s]+$', sanitized):
            return False, "", "Invalid path: contains illegal characters"
        
        return True, sanitized, None
    
    def validate_filename(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate filename
        Returns: (is_valid, error_message)
        """
        if not filename:
            return False, "Empty filename"
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check for illegal characters
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*', '\0', '\\', '/']
        for char in illegal_chars:
            if char in filename:
                return False, f"Filename contains illegal character: {char}"
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        
        if filename.upper() in reserved_names:
            return False, f"Filename is reserved: {filename}"
        
        return True, None
    
    def sanitize_html(self, text: str) -> str:
        """Sanitize HTML to prevent XSS"""
        if not text:
            return ""
        
        # Basic HTML escaping
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        text = text.replace('/', '&#x2F;')
        
        return text
    
    def validate_json_input(self, data: dict, required_fields: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON input
        Returns: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Invalid input: expected JSON object"
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    # ==================== CSRF PROTECTION ====================
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, expected_token: str) -> bool:
        """Validate CSRF token"""
        if not token or not expected_token:
            return False
        
        return secrets.compare_digest(token, expected_token)
    
    # ==================== PASSWORD HASHING ====================
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, pwd_hash = hashed.split('$')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except:
            return False
    
    # ==================== DECORATORS ====================
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            ip_address = request.remote_addr
            
            is_valid, user_id = self.validate_session_token(token, ip_address)
            
            if not is_valid:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # Add user_id to request context
            request.user_id = user_id
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def rate_limit(self, f):
        """Decorator to apply rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.remote_addr
            
            is_allowed, error_message = self.check_rate_limit(ip_address)
            
            if not is_allowed:
                return jsonify({'error': error_message}), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    # ==================== UTILITY METHODS ====================
    
    def get_client_ip(self) -> str:
        """Get client IP address, considering proxies"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def log_security_event(self, event_type: str, details: dict):
        """Log security-related events"""
        logger.warning(f"SECURITY EVENT: {event_type} - {details}")
    
    def get_status(self) -> Dict:
        """Get security service status"""
        return {
            'active_sessions': len(self.session_tokens),
            'blocked_ips': len(self.blocked_ips),
            'rate_limited_ips': len(self.rate_limit_store),
            'failed_login_tracking': len(self.failed_login_attempts)
        }


# Global singleton instance
_security_service = None


def get_security_service() -> SecurityService:
    """Get global security service instance"""
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service
