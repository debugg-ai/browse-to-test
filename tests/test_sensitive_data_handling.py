"""
Tests for sensitive data handling functionality.

This file specifically tests the sensitive data masking features
that were fixed in the OutputPlugin base class.
"""

import pytest
from unittest.mock import Mock

from browse_to_test.core.configuration.config import Config
from browse_to_test.plugins.base import OutputPlugin


class MockOutputPlugin(OutputPlugin):
    """Mock plugin for testing sensitive data handling."""
    
    def __init__(self, config):
        # Fix: Pass output config to parent, not full config
        super().__init__(config.output if hasattr(config, 'output') else config)
    
    @property
    def plugin_name(self):
        return "mock"
    
    @property
    def supported_frameworks(self):
        return ["mock"]
    
    @property
    def supported_languages(self):
        return ["python"]
    
    def validate_config(self, config):
        return []
    
    def get_template_variables(self, *args, **kwargs):
        return {}
    
    def generate_test_script(self, *args, **kwargs):
        """Mock implementation."""
        return "# Mock generated script"


class TestSensitiveDataHandling:
    """Test sensitive data handling functionality."""

    def test_sensitive_data_masking_enabled(self):
        """Test that sensitive data masking works when enabled."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Test that sensitive text gets masked
        sensitive_text = "secure_password123"
        result = plugin._handle_sensitive_data(sensitive_text)
        
        assert result == "***REDACTED***"

    def test_sensitive_data_masking_case_insensitive(self):
        """Test that sensitive data masking is case-insensitive."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Test various case combinations
        test_cases = [
            "PASSWORD123",
            "MyPassword",
            "userEMAIL",
            "Email_field"
        ]
        
        for text in test_cases:
            result = plugin._handle_sensitive_data(text)
            assert result == "***REDACTED***", f"Failed for text: {text}"

    def test_non_sensitive_data_preserved(self):
        """Test that non-sensitive data is not masked."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Test non-sensitive text
        normal_text = "username123"
        result = plugin._handle_sensitive_data(normal_text)
        
        assert result == "username123"

    def test_sensitive_data_masking_disabled(self):
        """Test that sensitive data is not masked when masking is disabled."""
        config = Config()
        config.output.mask_sensitive_data = False
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Even sensitive text should not be masked
        sensitive_text = "secure_password123"
        result = plugin._handle_sensitive_data(sensitive_text)
        
        assert result == "secure_password123"

    def test_placeholder_syntax_still_works(self):
        """Test that the original placeholder syntax still works."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Test original placeholder syntax
        placeholder_text = "<secret>password</secret>"
        result = plugin._handle_sensitive_data(placeholder_text)
        
        # Should be replaced with environment variable reference
        assert "get_env_var" in result
        assert "PASSWORD" in result

    def test_placeholder_with_non_sensitive_key(self):
        """Test placeholder with key not in sensitive_data_keys."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Placeholder with key not in sensitive list
        placeholder_text = "<secret>username</secret>"
        result = plugin._handle_sensitive_data(placeholder_text)
        
        # Should remain unchanged since username is not in sensitive keys
        assert result == "<secret>username</secret>"

    def test_multiple_sensitive_keys(self):
        """Test that multiple sensitive data keys work correctly."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email", "token", "secret", "key"]
        
        plugin = MockOutputPlugin(config)
        
        # Test that any of the configured sensitive keys trigger masking
        test_cases = [
            ("mypassword", "***REDACTED***"),
            ("user@email.com", "***REDACTED***"),
            ("bearer_token", "***REDACTED***"),
            ("api_secret", "***REDACTED***"),
            ("private_key", "***REDACTED***"),
            ("username", "username"),  # Should not be masked
            ("userid", "userid")       # Should not be masked
        ]
        
        for input_text, expected in test_cases:
            result = plugin._handle_sensitive_data(input_text)
            assert result == expected, f"Failed for input: {input_text}"

    def test_empty_sensitive_keys_list(self):
        """Test behavior when sensitive_data_keys list is empty."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = []
        
        plugin = MockOutputPlugin(config)
        
        # Should not mask anything when no sensitive keys are configured
        sensitive_text = "password123"
        result = plugin._handle_sensitive_data(sensitive_text)
        
        assert result == "password123"

    def test_none_sensitive_keys_list(self):
        """Test behavior when sensitive_data_keys is None."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = None
        
        plugin = MockOutputPlugin(config)
        
        # Should not mask anything when sensitive keys is None
        sensitive_text = "password123"
        result = plugin._handle_sensitive_data(sensitive_text)
        
        assert result == "password123"

    def test_sensitive_data_partial_matches(self):
        """Test that partial matches in sensitive keywords work correctly."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["pass"]
        
        plugin = MockOutputPlugin(config)
        
        # Text containing the sensitive keyword should be masked
        test_cases = [
            ("password123", "***REDACTED***"),
            ("mypass", "***REDACTED***"),
            ("passing", "***REDACTED***"),
            ("username", "username")  # Should not be masked
        ]
        
        for input_text, expected in test_cases:
            result = plugin._handle_sensitive_data(input_text)
            assert result == expected, f"Failed for input: {input_text}"

    def test_combined_placeholder_and_keyword_masking(self):
        """Test that both placeholder and keyword masking work together."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Test placeholder replacement first
        placeholder_text = "<secret>password</secret>"
        result1 = plugin._handle_sensitive_data(placeholder_text)
        assert "get_env_var" in result1
        
        # Test keyword masking
        keyword_text = "mypassword123"
        result2 = plugin._handle_sensitive_data(keyword_text)
        assert result2 == "***REDACTED***"

    def test_edge_case_empty_string(self):
        """Test edge case with empty string."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password"]
        
        plugin = MockOutputPlugin(config)
        
        result = plugin._handle_sensitive_data("")
        assert result == ""

    def test_edge_case_none_input(self):
        """Test edge case with None input."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password"]
        
        plugin = MockOutputPlugin(config)
        
        # Should handle None gracefully (though unlikely in practice)
        result = plugin._handle_sensitive_data(None)
        assert result is None


class TestSensitiveDataRegressionPrevention:
    """Tests specifically to prevent regression of the sensitive data masking fix."""

    def test_regression_sensitive_text_not_masked_before_fix(self):
        """
        Test that demonstrates the issue that was fixed.
        
        Before the fix, text containing sensitive keywords was not being masked,
        only placeholder syntax was handled.
        """
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # These should now be masked (this was the bug that was fixed)
        sensitive_inputs = [
            "secure_password123",
            "user@example.email", 
            "PASSWORD_VALUE",
            "my_email_address"
        ]
        
        for sensitive_input in sensitive_inputs:
            result = plugin._handle_sensitive_data(sensitive_input)
            assert result == "***REDACTED***", f"Regression: {sensitive_input} was not masked"

    def test_regression_placeholder_functionality_preserved(self):
        """Test that the original placeholder functionality was preserved during the fix."""
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password", "email"]
        
        plugin = MockOutputPlugin(config)
        
        # Original functionality should still work
        placeholder_text = "<secret>password</secret>"
        result = plugin._handle_sensitive_data(placeholder_text)
        
        # Should be replaced with environment variable reference (not just masked)
        assert "get_env_var" in result
        assert "PASSWORD" in result
        assert "***REDACTED***" not in result  # Should not use simple masking for placeholders 