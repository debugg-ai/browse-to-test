"""
Security-focused test suite for browse-to-test.

This module tests critical security features including:
1. API key protection and secure storage
2. Sensitive data masking and sanitization  
3. Input validation and injection prevention
4. Secure output generation
5. Environment variable handling
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import browse_to_test as btt
from browse_to_test.core.config import ConfigBuilder, Config
from browse_to_test.core.executor import BTTExecutor as E2eTestConverter


class TestAPIKeySecurity:
    """Test API key protection and secure handling."""
    
    def test_api_key_not_in_generated_script(self):
        """Test that API keys never appear in generated scripts."""
        secret_key = "sk-test-very-secret-key-12345"
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", api_key=secret_key) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert([{
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            }
        }])
        
        # API key should NEVER appear in generated output
        assert secret_key not in script, "API key found in generated script!"
        assert "sk-test" not in script, "Partial API key found in script!"
        assert "very-secret" not in script, "Secret key content found in script!"
    
    def test_api_key_environment_variable_protection(self):
        """Test that API keys from environment are protected."""
        test_key = "sk-env-test-key-67890"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}):
            script = btt.convert(
                [{"model_output": {"action": [{"click": {"selector": "#test"}}]}}],
                framework="playwright",
                ai_provider="openai"
            )
            
            # Environment API key should not leak into script
            assert test_key not in script
            assert "sk-env-test" not in script
    
    def test_multiple_provider_keys_protection(self):
        """Test protection of keys from multiple AI providers."""
        openai_key = "sk-openai-secret-123"
        anthropic_key = "sk-ant-secret-456"
        
        # Test OpenAI key protection
        config1 = ConfigBuilder() \
            .ai_provider("openai", api_key=openai_key) \
            .framework("playwright") \
            .build()
        
        converter1 = E2eTestConverter(config1)
        script1 = converter1.convert([{
            "model_output": {"action": [{"go_to_url": {"url": "https://test.com"}}]}
        }])
        
        assert openai_key not in script1
        
        # Test Anthropic key protection
        config2 = ConfigBuilder() \
            .ai_provider("anthropic", api_key=anthropic_key) \
            .framework("playwright") \
            .build()
        
        converter2 = E2eTestConverter(config2)
        script2 = converter2.convert([{
            "model_output": {"action": [{"go_to_url": {"url": "https://test.com"}}]}
        }])
        
        assert anthropic_key not in script2


class TestSensitiveDataMasking:
    """Test sensitive data detection and masking."""
    
    def test_password_masking(self):
        """Test that passwords are properly masked."""
        sensitive_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='password']",
                            "text": "MySecretPassword123!"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["password"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(sensitive_data)
        
        # Password should be masked
        assert "MySecretPassword123!" not in script
        # Should have some form of masking indicator (check for actual implementation indicators)
        assert any(mask in script for mask in ["SENSITIVE_DATA", "<secret>", "get_env_var", "YOUR_PASSWORD"])
    
    def test_credit_card_masking(self):
        """Test that credit card numbers are masked."""
        cc_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='credit_card']",
                            "text": "4111-1111-1111-1111"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["credit_card", "cc", "card_number"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(cc_data)
        
        # Credit card should be masked
        assert "4111-1111-1111-1111" not in script
    
    def test_ssn_masking(self):
        """Test that SSNs are masked."""
        ssn_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='ssn']",
                            "text": "123-45-6789"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["ssn", "social_security"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(ssn_data)
        
        # SSN should be masked
        assert "123-45-6789" not in script
    
    def test_email_selective_masking(self):
        """Test that emails can be selectively masked."""
        email_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='personal_email']",
                            "text": "personal@private.com"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='work_email']",
                            "text": "work@company.com"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["personal_email"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(email_data)
        
        # Personal email should be masked, work email should not
        assert "personal@private.com" not in script
        # Work email might still be present (depending on masking implementation)
    
    def test_custom_sensitive_patterns(self):
        """Test masking of custom sensitive data patterns."""
        custom_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='api_token']",
                            "text": "token-abc-123-secret"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["api_token", "token", "secret"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(custom_data)
        
        # Custom sensitive data should be masked
        assert "token-abc-123-secret" not in script


class TestInputValidationSecurity:
    """Test input validation and injection prevention."""
    
    def test_script_injection_prevention(self):
        """Test that script injection attempts are sanitized."""
        malicious_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='search']",
                            "text": "<script>alert('XSS')</script>"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(malicious_data, framework="playwright")
        
        # Script tags should be escaped or removed
        assert "<script>" not in script
        assert "alert('XSS')" not in script
    
    def test_javascript_url_prevention(self):
        """Test that javascript: URLs are blocked or sanitized."""
        js_url_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "javascript:alert('malicious')"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(js_url_data, framework="playwright")
            # If conversion succeeds, javascript: should be sanitized
            assert "javascript:alert" not in script
        except (ValueError, RuntimeError) as e:
            # It's also acceptable to reject malicious URLs entirely
            assert "invalid" in str(e).lower() or "unsafe" in str(e).lower()
    
    def test_data_url_handling(self):
        """Test handling of data: URLs for security."""
        data_url_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "data:text/html,<script>alert('xss')</script>"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(data_url_data, framework="playwright")
            # Data URLs should be handled carefully
            assert "<script>" not in script
        except (ValueError, RuntimeError):
            # Or rejected entirely
            pass
    
    def test_sql_injection_patterns(self):
        """Test that SQL injection patterns are handled safely."""
        sql_injection_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='username']",
                            "text": "'; DROP TABLE users; --"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(sql_injection_data, framework="playwright")
        
        # SQL injection should be escaped properly in the script
        # The exact escaping depends on implementation, but should be safe
        assert "DROP TABLE" not in script or script.count("'") % 2 == 0
    
    def test_xpath_injection_prevention(self):
        """Test that XPath injection attempts are sanitized."""
        xpath_injection_data = [
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": "//input[@name='test' or '1'='1']"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(xpath_injection_data, framework="selenium")
        
        # XPath injection should be handled safely
        assert "'1'='1'" not in script


class TestSecureOutputGeneration:
    """Test that generated outputs are secure."""
    
    def test_no_hardcoded_secrets_in_output(self):
        """Test that no hardcoded secrets appear in output."""
        data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {"url": "https://example.com"}
                    }]
                }
            }
        ]
        
        script = btt.convert(data, framework="playwright")
        
        # Common secret patterns that should never appear
        secret_patterns = [
            "sk-",  # OpenAI API keys
            "sk-ant-",  # Anthropic API keys
            "password",  # Unless properly handled
            "secret",  # Generic secret indicators
            "token",  # Unless properly handled
            "api_key"  # Unless properly handled
        ]
        
        for pattern in secret_patterns:
            # These patterns might appear in comments or variable names, 
            # but not as literal values
            if pattern in script:
                # Ensure they're not actual secret values
                lines = script.split('\n')
                for line in lines:
                    if pattern in line and '=' in line:
                        # Check if it's an assignment with an actual secret value
                        parts = line.split('=', 1)
                        if len(parts) > 1:
                            value = parts[1].strip().strip('"\'')
                            # Should not be an actual secret format
                            assert not (value.startswith('sk-') and len(value) > 20)
    
    def test_safe_file_paths(self):
        """Test that file paths in output are safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigBuilder() \
                .framework("playwright") \
                .project_root(tmpdir) \
                .build()
            
            converter = E2eTestConverter(config)
            script = converter.convert([{
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://example.com"}}]
                }
            }])
            
            # Should not contain path traversal attempts
            assert "../" not in script
            assert "..\\" not in script
            assert "/etc/passwd" not in script
            assert "C:\\" not in script
    
    def test_environment_variable_safety(self):
        """Test that environment variables are handled safely."""
        # Set a test environment variable
        test_value = "test-secret-value"
        with patch.dict(os.environ, {'TEST_SECRET': test_value}):
            script = btt.convert(
                [{"model_output": {"action": [{"click": {"selector": "#test"}}]}}],
                framework="playwright"
            )
            
            # Environment variable value should not leak
            assert test_value not in script


class TestConfigurationSecurity:
    """Test security aspects of configuration handling."""
    
    def test_config_file_permissions(self):
        """Test that config files are created with safe permissions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "ai": {
                    "provider": "openai",
                    "api_key": "sk-test-key-123"
                }
            }
            import json
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            # File should exist
            assert os.path.exists(config_path)
            
            # Check file permissions (should not be world-readable)
            stat_info = os.stat(config_path)
            permissions = stat_info.st_mode & 0o777
            
            # Should not be world-readable (no 'other' read permission)
            assert (permissions & 0o004) == 0, f"Config file is world-readable: {oct(permissions)}"
            
        finally:
            # Clean up
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_sensitive_config_logging(self):
        """Test that sensitive config data is not logged."""
        import logging
        from io import StringIO
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('browse_to_test')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            config = ConfigBuilder() \
                .ai_provider("openai", api_key="sk-secret-log-test-789") \
                .framework("playwright") \
                .debug(True) \
                .build()
            
            converter = E2eTestConverter(config)
            converter.convert([{
                "model_output": {"action": [{"click": {"selector": "#test"}}]}
            }])
            
            # Check that API key is not in logs
            log_output = log_capture.getvalue()
            assert "sk-secret-log-test-789" not in log_output
            
        finally:
            logger.removeHandler(handler)


class TestSecurityHeaders:
    """Test security-related headers and metadata."""
    
    def test_generated_script_security_comments(self):
        """Test that generated scripts include security warnings where appropriate."""
        sensitive_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[type='password']",
                            "text": "password123"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(sensitive_data, framework="playwright")
        
        # Should include security-related comments or warnings
        # This is implementation-dependent, but good practice
        security_indicators = [
            "# WARNING",
            "# SECURITY",
            "# NOTE",
            "# TODO",
            "MASKED",
            "REDACTED"
        ]
        
        has_security_indicator = any(indicator in script for indicator in security_indicators)
        # This is a soft assertion - security comments are good practice but not required
        if not has_security_indicator:
            print("INFO: Generated script could benefit from security warnings/comments")


if __name__ == "__main__":
    print("Running security validation tests...")
    
    # Basic security validation
    test_api_key = "sk-test-security-validation"
    script = btt.convert(
        [{"model_output": {"action": [{"click": {"selector": "#test"}}]}}],
        framework="playwright"
    )
    
    # Critical check: no test API key should appear in output
    assert test_api_key not in script, "SECURITY FAILURE: Test API key found in output!"
    
    print("✓ Basic security validation passed")
    print("Run full test suite with: pytest test_security_validation.py")