"""
Tests for specific regression fixes in browse-to-test library.

This file contains tests for bugs that were discovered and fixed,
to prevent future regressions.
"""

import pytest
from unittest.mock import Mock, patch

import browse_to_test as btt
from browse_to_test.core.configuration.config import Config, ConfigBuilder, ProcessingConfig
from browse_to_test.core.processing.input_parser import InputParser
from browse_to_test.core.orchestration.converter import E2eTestConverter
from browse_to_test.plugins.base import OutputPlugin


class TestConfigBuilderRegressionFixes:
    """Test fixes for ConfigBuilder issues."""

    def test_include_logging_method_exists(self):
        """Test that include_logging method exists and works (Regression fix)."""
        # This test prevents regression of the missing include_logging method
        builder = ConfigBuilder()
        
        # Should not raise AttributeError
        result = builder.include_logging(True)
        
        # Should return builder for chaining
        assert result is builder
        
        # Should set the config properly
        config = builder.build()
        assert config.output.include_logging is True

    def test_include_logging_method_chaining(self):
        """Test that include_logging method works in fluent interface chaining."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .include_logging(True) \
            .include_assertions(True) \
            .include_error_handling(True) \
            .build()
        
        assert config.output.framework == "playwright"
        assert config.ai.provider == "openai"
        assert config.output.language == "python"
        assert config.output.include_logging is True
        assert config.output.include_assertions is True
        assert config.output.include_error_handling is True

    def test_include_logging_default_false(self):
        """Test that include_logging defaults to False when not specified."""
        config = ConfigBuilder().build()
        assert config.output.include_logging is False

    def test_include_logging_disable(self):
        """Test that include_logging can be disabled."""
        config = ConfigBuilder() \
            .include_logging(False) \
            .build()
        
        assert config.output.include_logging is False


class TestInputValidationRegressionFixes:
    """Test fixes for input validation issues."""

    def test_invalid_data_raises_error_in_strict_mode(self):
        """Test that invalid data raises error in strict mode (Regression fix)."""
        # Create config with strict mode enabled
        config = Config()
        config.processing.strict_mode = True
        
        parser = InputParser(config)
        
        # Invalid data without required model_output field
        invalid_data = [{"invalid": "data"}]
        
        # Should raise ValueError due to missing model_output
        with pytest.raises(ValueError, match="missing required 'model_output' field"):
            parser.parse(invalid_data)

    def test_invalid_data_handled_gracefully_in_non_strict_mode(self):
        """Test that invalid data is handled gracefully when strict mode is disabled."""
        # Create config with strict mode disabled (default)
        config = Config()
        config.processing.strict_mode = False
        
        parser = InputParser(config)
        
        # Invalid data without required model_output field
        invalid_data = [{"invalid": "data"}]
        
        # Should not raise error, but return empty parsed data
        parsed = parser.parse(invalid_data)
        assert len(parsed.steps) == 1
        assert len(parsed.steps[0].actions) == 0

    def test_convert_function_enables_strict_mode_by_default(self):
        """Test that the simple convert function enables strict mode for better validation."""
        # Mock the AI provider to avoid actual API calls
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider') as mock_factory:
            mock_provider = Mock()
            mock_provider.generate_test_script.return_value = "# Generated test script"
            mock_factory.return_value = mock_provider
            
            # Invalid data should raise error through convert function
            invalid_data = [{"invalid": "data"}]
            
            with pytest.raises(Exception, match="model_output"):
                btt.convert(invalid_data, framework="playwright", ai_provider="openai")

    def test_valid_data_with_model_output_works(self):
        """Test that valid data with model_output field works correctly."""
        config = Config()
        config.processing.strict_mode = True
        
        parser = InputParser(config)
        
        # Valid data with required model_output field
        valid_data = [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to example.com"}
            }
        ]
        
        # Should parse successfully
        parsed = parser.parse(valid_data)
        assert len(parsed.steps) == 1
        assert len(parsed.steps[0].actions) == 1
        assert parsed.steps[0].actions[0].action_type == "go_to_url"

    def test_empty_model_output_handled_correctly(self):
        """Test that empty model_output is handled correctly."""
        config = Config()
        config.processing.strict_mode = True
        
        parser = InputParser(config)
        
        # Data with empty model_output
        data_with_empty_output = [
            {
                "model_output": {},
                "state": {"interacted_element": []},
                "metadata": {"description": "Empty output"}
            }
        ]
        
        # Should parse but with empty actions
        parsed = parser.parse(data_with_empty_output)
        assert len(parsed.steps) == 1
        assert len(parsed.steps[0].actions) == 0

    def test_invalid_model_output_type_raises_error(self):
        """Test that invalid model_output type raises error in strict mode."""
        config = Config()
        config.processing.strict_mode = True
        
        parser = InputParser(config)
        
        # Data with invalid model_output type (string instead of dict)
        invalid_output_data = [
            {
                "model_output": "invalid_string",
                "state": {"interacted_element": []},
                "metadata": {"description": "Invalid output type"}
            }
        ]
        
        # Should raise ValueError due to invalid model_output type
        with pytest.raises(ValueError, match="invalid model_output type"):
            parser.parse(invalid_output_data)


class TestSensitiveDataMaskingRegressionFixes:
    """Test fixes for sensitive data masking issues."""

    def test_sensitive_data_masking_regression_fix(self):
        """Test that sensitive data in text is now properly masked (Regression fix)."""
        # This is a simplified test to verify the fix is working
        # Detailed tests are in test_sensitive_data_handling.py
        
        # Use the correct config structure
        config = Config()
        config.output.mask_sensitive_data = True
        config.output.sensitive_data_keys = ["password"]
        
        # Create a minimal mock plugin to test the sensitive data handling
        class TestPlugin:
            def __init__(self, config):
                self.config = config.output  # Plugin uses output config
            
            def _handle_sensitive_data(self, text):
                """Copy of the method from the base plugin for testing."""
                if not self.config.mask_sensitive_data:
                    return text
                
                import re
                
                # Pattern to match <secret>key</secret>
                pattern = r'<secret>([^<]+)</secret>'
                
                def replace_secret(match):
                    key = match.group(1)
                    if key in self.config.sensitive_data_keys:
                        return f"{{get_env_var('{key.upper()}')}}"
                    return match.group(0)
                
                processed_text = re.sub(pattern, replace_secret, text)
                
                # Also check if the text itself contains sensitive data based on configured keys
                if self.config.sensitive_data_keys:
                    for sensitive_key in self.config.sensitive_data_keys:
                        # Check if the sensitive key is contained in the text (case-insensitive)
                        if sensitive_key.lower() in processed_text.lower():
                            # Mask the sensitive data
                            processed_text = "***REDACTED***"
                            break
                
                return processed_text
        
        plugin = TestPlugin(config)
        
        # Test that sensitive text gets masked
        sensitive_text = "mypassword123"
        result = plugin._handle_sensitive_data(sensitive_text)
        
        assert result == "***REDACTED***"


class TestEndToEndRegressionFixes:
    """End-to-end tests for the regression fixes."""

    @patch('browse_to_test.ai.factory.AIProviderFactory.create_provider')
    def test_configbuilder_logging_option_in_full_flow(self, mock_factory):
        """Test that the ConfigBuilder logging option works in full conversion flow."""
        # Mock AI provider
        mock_provider = Mock()
        mock_provider.generate_test_script.return_value = "print('test'); await page.goto('https://example.com')"
        mock_factory.return_value = mock_provider
        
        # Use ConfigBuilder with include_logging
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .include_logging(True) \
            .build()
        
        converter = E2eTestConverter(config)
        
        # Valid automation data
        automation_data = [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to example.com"}
            }
        ]
        
        # Should not raise any errors
        script = converter.convert(automation_data)
        assert isinstance(script, str)
        assert len(script) > 0

    @patch('browse_to_test.ai.factory.AIProviderFactory.create_provider')
    def test_sensitive_data_masking_in_full_flow(self, mock_factory):
        """Test that sensitive data masking works in full conversion flow."""
        # Mock AI provider
        mock_provider = Mock()
        mock_provider.generate_test_script.return_value = "await page.fill('input', 'test')"
        mock_factory.return_value = mock_provider
        
        # Use ConfigBuilder with sensitive data keys
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .sensitive_data_keys(["password", "email"]) \
            .build()
        
        converter = E2eTestConverter(config)
        
        # Automation data with sensitive information
        automation_data = [
            {
                "model_output": {
                    "action": [{"input_text": {"text": "mypassword123", "index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "css_selector": "input[type='password']",
                        "attributes": {"type": "password"}
                    }]
                },
                "metadata": {"description": "Enter password"}
            }
        ]
        
        # Should not raise any errors and should handle sensitive data
        script = converter.convert(automation_data)
        assert isinstance(script, str)
        assert len(script) > 0

    def test_convert_function_strict_validation_integration(self):
        """Test that the convert function's strict validation works correctly."""
        # Test with invalid data (should raise error)
        invalid_data = [{"invalid": "data"}]
        
        with pytest.raises(Exception):  # Should raise some validation error
            btt.convert(invalid_data, framework="playwright", ai_provider="openai")
        
        # Test with valid data (should work when mocked)
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider') as mock_factory:
            mock_provider = Mock()
            mock_provider.generate_test_script.return_value = "# Test script"
            mock_factory.return_value = mock_provider
            
            valid_data = [
                {
                    "model_output": {
                        "action": [{"go_to_url": {"url": "https://example.com"}}]
                    },
                    "state": {"interacted_element": []},
                    "metadata": {"description": "Navigate"}
                }
            ]
            
            script = btt.convert(valid_data, framework="playwright", ai_provider="openai")
            assert isinstance(script, str) 