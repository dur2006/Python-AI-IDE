"""
Security Middleware
Provides rate limiting, CSRF protection, and security headers
"""

from typing import Dict, Any, Callable, Optional
from flask import request, jsonify, current_app, session
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import secrets
import time


class RateLimiter:
    """
    Rate limiter using in-memory storage
    For production, use Redis or similar distributed cache
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_interval = 60  # Cleanup old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup(self):
        """Remove old entries to prevent memory bloat"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 3600  # Remove entries older than 1 hour
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    timestamp for timestamp in self.requests[key]
                    if timestamp > cutoff_time
                ]
                if not self.requests[key]:
                    del self.requests[key]
            self.last_cleanup = current_time
    
    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed based on rate limit
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        self._cleanup()
        
        current_time = time.time()
        cutoff_time = current_time - window
        
        # Get request timestamps for this key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old timestamps outside the window
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if timestamp > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            # Calculate retry-after time
            oldest_timestamp = min(self.requests[key])
            retry_after = int(oldest_timestamp + window - current_time)
            return False, max(retry_after, 1)
        
        # Add current request
        self.requests[key].append(current_time)
        return True, None


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 100, window: int = 60, key_func: Optional[Callable] = None):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Optional function to generate rate limit key (default: IP address)
        
    Example:
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def my_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                # Default: use IP address
                key = request.remote_addr or 'unknown'
            
            # Check rate limit
            is_allowed, retry_after = rate_limiter.is_allowed(key, limit, window)
            
            if not is_allowed:
                current_app.logger.warning(
                    f"Rate limit exceeded for {key}: {limit} requests per {window}s"
                )
                response = jsonify({
                    'status': 'error',
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                return response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class CSRFProtection:
    """
    CSRF Protection using double-submit cookie pattern
    """
    
    @staticmethod
    def generate_token() -> str:
        """Generate a new CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_token() -> str:
        """Get or create CSRF token for current session"""
        if 'csrf_token' not in session:
            session['csrf_token'] = CSRFProtection.generate_token()
        return session['csrf_token']
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate CSRF token"""
        if 'csrf_token' not in session:
            return False
        return secrets.compare_digest(session['csrf_token'], token)


def csrf_protect(f):
    """
    CSRF protection decorator
    Validates CSRF token for state-changing requests (POST, PUT, DELETE, PATCH)
    
    Token should be sent in:
    - Header: X-CSRF-Token
    - Or form data: csrf_token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only check CSRF for state-changing methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get token from header or form data
            token = request.headers.get('X-CSRF-Token')
            if not token:
                data = request.get_json(silent=True) or {}
                token = data.get('csrf_token')
            
            if not token:
                current_app.logger.warning(
                    f"CSRF token missing for {request.method} {request.path}"
                )
                return jsonify({
                    'status': 'error',
                    'error': 'CSRF token missing'
                }), 403
            
            if not CSRFProtection.validate_token(token):
                current_app.logger.warning(
                    f"Invalid CSRF token for {request.method} {request.path}"
                )
                return jsonify({
                    'status': 'error',
                    'error': 'Invalid CSRF token'
                }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def add_security_headers(response):
    """
    Add security headers to response
    Should be registered as an after_request handler
    """
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' ws: wss:; "
        "frame-ancestors 'none';"
    )
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=()'
    )
    
    # HSTS (only in production with HTTPS)
    if not current_app.debug:
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains'
        )
    
    return response


def validate_content_length(max_length: int = 10 * 1024 * 1024):
    """
    Validate request content length
    
    Args:
        max_length: Maximum content length in bytes (default: 10MB)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            
            if content_length and content_length > max_length:
                current_app.logger.warning(
                    f"Request too large: {content_length} bytes (max: {max_length})"
                )
                return jsonify({
                    'status': 'error',
                    'error': 'Request entity too large',
                    'max_size': f'{max_length / (1024 * 1024):.1f}MB'
                }), 413
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_https(f):
    """
    Require HTTPS for endpoint (in production)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.debug and not request.is_secure:
            current_app.logger.warning(
                f"HTTPS required for {request.method} {request.path}"
            )
            return jsonify({
                'status': 'error',
                'error': 'HTTPS required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


class IPBlocklist:
    """
    IP address blocklist for banning malicious IPs
    """
    
    def __init__(self):
        self.blocked_ips: set = set()
        self.violations: Dict[str, int] = {}
        self.violation_threshold = 10
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        current_app.logger.warning(f"IP blocked: {ip}")
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
        self.violations.pop(ip, None)
    
    def record_violation(self, ip: str):
        """Record a security violation for an IP"""
        self.violations[ip] = self.violations.get(ip, 0) + 1
        
        if self.violations[ip] >= self.violation_threshold:
            self.block_ip(ip)


# Global IP blocklist instance
ip_blocklist = IPBlocklist()


def check_ip_blocklist(f):
    """
    Check if IP is blocked
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr or 'unknown'
        
        if ip_blocklist.is_blocked(ip):
            current_app.logger.warning(f"Blocked IP attempted access: {ip}")
            return jsonify({
                'status': 'error',
                'error': 'Access denied'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def init_security_middleware(app):
    """
    Initialize security middleware for Flask app
    
    Args:
        app: Flask application instance
    """
    # Register security headers
    app.after_request(add_security_headers)
    
    # Set secure session cookie settings
    app.config['SESSION_COOKIE_SECURE'] = not app.debug
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Set permanent session lifetime (24 hours)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    current_app.logger.info("Security middleware initialized")


# Export commonly used decorators and functions
__all__ = [
    'rate_limit',
    'csrf_protect',
    'CSRFProtection',
    'add_security_headers',
    'validate_content_length',
    'require_https',
    'check_ip_blocklist',
    'ip_blocklist',
    'init_security_middleware'
]
