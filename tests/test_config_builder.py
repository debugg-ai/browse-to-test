"""Tests for the new ConfigBuilder class introduced in the architectural restructuring."""

import pytest
from unittest.mock import Mock, patch

from browse_to_test.core.configuration.config import Config, ConfigBuilder, AIConfig, OutputConfig, ProcessingConfig


class TestConfigBuilder:
    """Test the ConfigBuilder fluent interface."""

    def test_basic_builder_creation(self):
        """Test basic ConfigBuilder instantiation."""
        builder = ConfigBuilder()
        assert builder is not None
        assert hasattr(builder, '_config')
        assert isinstance(builder._config, Config)

    def test_framework_setting(self):
        """Test setting framework through builder."""
        config = ConfigBuilder().framework("playwright").build()
        assert config.output.framework == "playwright"

    def test_ai_provider_setting(self):
        """Test setting AI provider through builder."""
        config = ConfigBuilder().ai_provider("openai").build()
        assert config.ai.provider == "openai"

    def test_ai_provider_with_model_and_key(self):
        """Test setting AI provider with model and API key."""
        config = ConfigBuilder() \
            .ai_provider("openai", model="gpt-4", api_key="test-key") \
            .build()
        
        assert config.ai.provider == "openai"
        assert config.ai.model == "gpt-4"
        assert config.ai.api_key == "test-key"

    def test_language_setting(self):
        """Test setting target language through builder."""
        config = ConfigBuilder().language("typescript").build()
        assert config.output.language == "typescript"

    def test_fluent_interface_chaining(self):
        """Test that all methods return self for chaining."""
        builder = ConfigBuilder()
        
        result = builder \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .debug(True)
        
        assert result is builder
        
        config = result.build()
        assert config.output.framework == "playwright"
        assert config.ai.provider == "openai"
        assert config.output.language == "python"
        assert config.output.include_assertions is True
        assert config.output.include_error_handling is True
        assert config.debug is True

    def test_enable_context_collection(self):
        """Test enabling context collection."""
        config = ConfigBuilder().enable_context_collection(True).build()
        assert config.processing.collect_system_context is True
        
        config = ConfigBuilder().enable_context_collection(False).build()
        assert config.processing.collect_system_context is False

    def test_enable_ai_analysis(self):
        """Test enabling AI analysis."""
        config = ConfigBuilder().enable_ai_analysis(True).build()
        assert config.processing.analyze_actions_with_ai is True
        
        config = ConfigBuilder().enable_ai_analysis(False).build()
        assert config.processing.analyze_actions_with_ai is False

    def test_include_assertions(self):
        """Test setting assertion inclusion."""
        config = ConfigBuilder().include_assertions(True).build()
        assert config.output.include_assertions is True
        
        config = ConfigBuilder().include_assertions(False).build()
        assert config.output.include_assertions is False

    def test_include_error_handling(self):
        """Test setting error handling inclusion."""
        config = ConfigBuilder().include_error_handling(True).build()
        assert config.output.include_error_handling is True
        
        config = ConfigBuilder().include_error_handling(False).build()
        assert config.output.include_error_handling is False

    def test_debug_setting(self):
        """Test setting debug mode."""
        config = ConfigBuilder().debug(True).build()
        assert config.debug is True
        
        config = ConfigBuilder().debug(False).build()
        assert config.debug is False

    def test_temperature_setting(self):
        """Test setting AI temperature."""
        config = ConfigBuilder().temperature(0.5).build()
        assert config.ai.temperature == 0.5

    def test_timeout_setting(self):
        """Test setting test timeout."""
        config = ConfigBuilder().timeout(20000).build()
        assert config.output.test_timeout == 20000

    def test_sensitive_data_keys(self):
        """Test setting sensitive data keys."""
        keys = ["password", "token", "secret"]
        config = ConfigBuilder().sensitive_data_keys(keys).build()
        assert config.output.sensitive_data_keys == keys

    def test_project_root_setting(self):
        """Test setting project root."""
        config = ConfigBuilder().project_root("/path/to/project").build()
        assert config.project_root == "/path/to/project"

    def test_fast_mode(self):
        """Test fast mode configuration."""
        config = ConfigBuilder().fast_mode().build()
        
        # Fast mode should optimize for speed
        assert config.processing.collect_system_context is False
        assert config.processing.use_intelligent_analysis is False
        assert config.processing.context_analysis_depth == "shallow"
        assert config.ai.max_tokens == 2000

    def test_thorough_mode(self):
        """Test thorough mode configuration."""
        config = ConfigBuilder().thorough_mode().build()
        
        # Thorough mode should optimize for accuracy
        assert config.processing.collect_system_context is True
        assert config.processing.use_intelligent_analysis is True
        assert config.processing.context_analysis_depth == "deep"
        assert config.ai.max_tokens == 8000

    def test_from_dict(self):
        """Test building config from dictionary."""
        config_dict = {
            "ai": {"provider": "anthropic", "model": "claude-3"},
            "output": {"framework": "selenium", "language": "java"},
            "debug": True
        }
        
        config = ConfigBuilder().from_dict(config_dict).build()
        
        assert config.ai.provider == "anthropic"
        assert config.ai.model == "claude-3"
        assert config.output.framework == "selenium"
        assert config.output.language == "java"
        assert config.debug is True

    def test_from_dict_with_none(self):
        """Test from_dict with None value."""
        config = ConfigBuilder().from_dict(None).build()
        # Should not raise error and should have defaults
        assert config.ai.provider == "openai"  # default
        assert config.output.framework == "playwright"  # default

    def test_from_kwargs(self):
        """Test building config from keyword arguments."""
        config = ConfigBuilder().from_kwargs(
            api_key="test-key",
            model="gpt-4",
            temperature=0.3,
            timeout=25000,
            include_assertions=True,
            include_error_handling=False,
            debug=True,
            project_root="/test/path",
            context_collection=True
        ).build()
        
        assert config.ai.api_key == "test-key"
        assert config.ai.model == "gpt-4"
        assert config.ai.temperature == 0.3
        assert config.output.test_timeout == 25000
        assert config.output.include_assertions is True
        assert config.output.include_error_handling is False
        assert config.debug is True
        assert config.project_root == "/test/path"
        assert config.processing.collect_system_context is True

    def test_build_with_validation(self):
        """Test that build() performs validation."""
        with patch.object(Config, 'validate') as mock_validate:
            mock_validate.return_value = []  # No errors
            
            config = ConfigBuilder().build()
            
            mock_validate.assert_called_once()
            assert isinstance(config, Config)

    def test_build_with_validation_errors(self):
        """Test build() with validation errors."""
        with patch.object(Config, 'validate') as mock_validate:
            mock_validate.return_value = ["Invalid temperature", "Missing API key"]
            
            with pytest.raises(ValueError, match="Configuration validation failed"):
                ConfigBuilder().build()

    def test_complex_configuration_chain(self):
        """Test a complex configuration using all builder methods."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4", api_key="sk-test") \
            .language("typescript") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .enable_context_collection(True) \
            .enable_ai_analysis(True) \
            .temperature(0.2) \
            .timeout(30000) \
            .sensitive_data_keys(["password", "token"]) \
            .project_root("/my/project") \
            .debug(False) \
            .build()
        
        # Verify all settings
        assert config.output.framework == "playwright"
        assert config.ai.provider == "openai"
        assert config.ai.model == "gpt-4"
        assert config.ai.api_key == "sk-test"
        assert config.output.language == "typescript"
        assert config.output.include_assertions is True
        assert config.output.include_error_handling is True
        assert config.processing.collect_system_context is True
        assert config.processing.analyze_actions_with_ai is True
        assert config.ai.temperature == 0.2
        assert config.output.test_timeout == 30000
        assert config.output.sensitive_data_keys == ["password", "token"]
        assert config.project_root == "/my/project"
        assert config.debug is False


class TestConfigBuilderErrorHandling:
    """Test error handling in ConfigBuilder."""

    def test_invalid_temperature_validation(self):
        """Test validation catches invalid temperature."""
        with patch.object(Config, 'validate') as mock_validate:
            mock_validate.return_value = ["AI temperature must be between 0 and 2"]
            
            with pytest.raises(ValueError, match="AI temperature must be between 0 and 2"):
                ConfigBuilder().temperature(5.0).build()

    def test_invalid_timeout_validation(self):
        """Test validation catches invalid timeout."""
        with patch.object(Config, 'validate') as mock_validate:
            mock_validate.return_value = ["Test timeout must be at least 1000ms"]
            
            with pytest.raises(ValueError, match="Test timeout must be at least 1000ms"):
                ConfigBuilder().timeout(500).build()

    def test_empty_framework_validation(self):
        """Test validation catches empty framework."""
        with patch.object(Config, 'validate') as mock_validate:
            mock_validate.return_value = ["Output framework cannot be empty"]
            
            with pytest.raises(ValueError, match="Output framework cannot be empty"):
                ConfigBuilder().framework("").build()

    def test_multiple_validation_errors(self):
        """Test handling multiple validation errors."""
        with patch.object(Config, 'validate') as mock_validate:
            errors = [
                "AI provider cannot be empty",
                "Output framework cannot be empty",
                "Invalid temperature"
            ]
            mock_validate.return_value = errors
            
            with pytest.raises(ValueError) as exc_info:
                ConfigBuilder().build()
            
            error_message = str(exc_info.value)
            assert "Configuration validation failed" in error_message
            # Should contain all error messages
            for error in errors:
                assert error in error_message


class TestConfigBuilderIntegration:
    """Integration tests for ConfigBuilder with other components."""

    def test_builder_creates_valid_config_for_converter(self):
        """Test that ConfigBuilder creates valid config for E2eTestConverter."""
        from browse_to_test.core.orchestration.converter import E2eTestConverter
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .build()
        
        # Should be able to create E2eTestConverter without errors
        with patch('browse_to_test.core.orchestration.converter.InputParser'):
            with patch('browse_to_test.core.orchestration.converter.PluginRegistry'):
                with patch('browse_to_test.core.orchestration.converter.AIProviderFactory'):
                    with patch('browse_to_test.core.orchestration.converter.ActionAnalyzer'):
                        converter = E2eTestConverter(config)
                        assert converter.config == config

    def test_builder_creates_valid_config_for_session(self):
        """Test that ConfigBuilder creates valid config for IncrementalSession."""
        from browse_to_test.core.orchestration.session import IncrementalSession
        
        config = ConfigBuilder() \
            .framework("selenium") \
            .ai_provider("anthropic") \
            .build()
        
        # Should be able to create IncrementalSession without errors
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter'):
            session = IncrementalSession(config)
            assert session.config == config

    def test_fast_mode_vs_thorough_mode_differences(self):
        """Test that fast mode and thorough mode create meaningfully different configs."""
        fast_config = ConfigBuilder().fast_mode().build()
        thorough_config = ConfigBuilder().thorough_mode().build()
        
        # These should be different
        assert fast_config.processing.collect_system_context != thorough_config.processing.collect_system_context
        assert fast_config.processing.use_intelligent_analysis != thorough_config.processing.use_intelligent_analysis
        assert fast_config.processing.context_analysis_depth != thorough_config.processing.context_analysis_depth
        assert fast_config.ai.max_tokens != thorough_config.ai.max_tokens
        
        # Fast should be optimized for speed
        assert fast_config.processing.collect_system_context is False
        assert thorough_config.processing.collect_system_context is True

    def test_builder_preserves_method_call_order(self):
        """Test that later method calls override earlier ones."""
        config = ConfigBuilder() \
            .temperature(0.1) \
            .temperature(0.9) \
            .framework("playwright") \
            .framework("selenium") \
            .build()
        
        # Later calls should win
        assert config.ai.temperature == 0.9
        assert config.output.framework == "selenium"

    def test_include_logging_method_regression(self):
        """Test that include_logging method exists and works (Regression test)."""
        # This test prevents regression of the missing include_logging method
        config = ConfigBuilder() \
            .framework("playwright") \
            .include_logging(True) \
            .build()
        
        assert config.output.include_logging is True

    def test_include_logging_fluent_chaining(self):
        """Test that include_logging method works in fluent interface."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .include_logging(True) \
            .include_assertions(True) \
            .include_error_handling(True) \
            .build()
        
        assert config.output.include_logging is True
        assert config.output.include_assertions is True
        assert config.output.include_error_handling is True

    def test_include_logging_disable(self):
        """Test that include_logging can be explicitly disabled."""
        config = ConfigBuilder() \
            .include_logging(False) \
            .build()
        
        assert config.output.include_logging is False 