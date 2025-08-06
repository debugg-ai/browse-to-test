"""Tests for the new E2eTestConverter class introduced in the architectural restructuring."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
from browse_to_test.core.config import Config, ConfigBuilder
from browse_to_test.core.processing.input_parser import ParsedAutomationData
from browse_to_test.core.processing.action_analyzer import ComprehensiveAnalysisResult
from browse_to_test.core.processing.context_collector import SystemContext


class TestE2eTestConverter:
    """Test the E2eTestConverter class."""

    @pytest.fixture
    def basic_config(self):
        """Create a basic config for testing."""
        return ConfigBuilder().framework("playwright").ai_provider("openai").build()

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies for E2eTestConverter."""
        with patch('browse_to_test.core.executor.InputParser') as mock_input_parser, \
             patch('browse_to_test.core.executor.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.executor.AIProviderFactory') as mock_ai_factory, \
             patch('browse_to_test.core.executor.ActionAnalyzer') as mock_action_analyzer, \
             patch('browse_to_test.core.executor.ContextCollector') as mock_context_collector:
            
            yield {
                'input_parser': mock_input_parser,
                'plugin_registry': mock_plugin_registry,
                'ai_factory': mock_ai_factory,
                'action_analyzer': mock_action_analyzer,
                'context_collector': mock_context_collector
            }

    def test_init_basic(self, basic_config, mock_dependencies):
        """Test basic E2eTestConverter initialization."""
        converter = E2eTestConverter(basic_config)
        
        assert converter.config == basic_config
        mock_dependencies['input_parser'].assert_called_once_with(basic_config)
        mock_dependencies['plugin_registry'].assert_called_once()

    def test_init_with_ai_provider(self, mock_dependencies):
        """Test E2eTestConverter initialization with AI provider enabled."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .enable_ai_analysis(True) \
            .build()
        
        mock_ai_provider = Mock()
        mock_dependencies['ai_factory'].return_value.create_provider.return_value = mock_ai_provider
        
        converter = E2eTestConverter(config)
        
        # Check that AI provider creation was attempted (config.ai is a property)
        mock_dependencies['ai_factory'].return_value.create_provider.assert_called_once()
        assert converter.ai_provider == mock_ai_provider

    def test_init_with_ai_provider_failure(self, mock_dependencies):
        """Test E2eTestConverter initialization when AI provider creation fails."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .enable_ai_analysis(True) \
            .debug(True) \
            .build()
        
        mock_dependencies['ai_factory'].return_value.create_provider.side_effect = Exception("API key missing")
        
        # Should not raise exception, just log warning
        converter = E2eTestConverter(config)
        assert converter.ai_provider is None

    def test_init_with_context_collection(self, mock_dependencies):
        """Test E2eTestConverter initialization with context collection enabled."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .enable_context_collection(True) \
            .project_root("/test/project") \
            .build()
        
        converter = E2eTestConverter(config)
        
        # ContextCollector is always initialized, but behavior depends on config
        mock_dependencies['context_collector'].assert_called_once_with(config)
        assert converter.context_collector is not None

    def test_init_without_context_collection(self, basic_config, mock_dependencies):
        """Test E2eTestConverter initialization without context collection."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .enable_context_collection(False) \
            .build()
        
        converter = E2eTestConverter(config)
        
        # Context collector is not initialized when disabled
        mock_dependencies['context_collector'].assert_not_called()
        assert converter.context_collector is None

    def test_convert_basic(self, basic_config, mock_dependencies, sample_automation_data):
        """Test basic convert functionality."""
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1", "step2"]  # Mock steps attribute
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1", "analyzed_step2"]
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "Generated test script"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(basic_config)
        result = converter.convert(sample_automation_data)
        
        assert result == "Generated test script"
        mock_dependencies['input_parser'].return_value.parse.assert_called_once_with(sample_automation_data)
        mock_plugin.generate_script.assert_called_once()

    def test_convert_with_target_url(self, basic_config, mock_dependencies, sample_automation_data):
        """Test convert with target URL."""
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "URL-specific script"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(basic_config)
        result = converter.convert(sample_automation_data, target_url="https://example.com")
        
        assert result == "URL-specific script"
        
        # Check that the plugin was called correctly
        call_args, call_kwargs = mock_plugin.generate_script.call_args
        assert call_kwargs['steps'] == ["analyzed_step1"]

    def test_convert_with_context_collection(self, mock_dependencies, sample_automation_data):
        """Test convert with context collection enabled."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .enable_context_collection(True) \
            .build()
        
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_context = Mock()
        mock_dependencies['context_collector'].return_value.collect_context.return_value = mock_context
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "Context-aware script"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(config)
        result = converter.convert(sample_automation_data, target_url="https://example.com")
        
        assert result == "Context-aware script"
        
        # Verify context collection was called
        mock_dependencies['context_collector'].return_value.collect_context.assert_called_once()
        
        # Check that context was passed to plugin
        call_args, call_kwargs = mock_plugin.generate_script.call_args
        assert call_kwargs['context'] == mock_context

    def test_convert_with_ai_analysis(self, mock_dependencies, sample_automation_data):
        """Test convert with AI analysis enabled."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .enable_ai_analysis(True) \
            .build()
        
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        mock_ai_provider = Mock()
        mock_dependencies['ai_factory'].return_value.create_provider.return_value = mock_ai_provider
        
        # Mock action analyzer - in the executor it calls analyze_steps, not analyze_comprehensive
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "AI-enhanced script"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(config)
        result = converter.convert(sample_automation_data)
        
        assert result == "AI-enhanced script"
        
        # Verify action analysis was called
        mock_dependencies['action_analyzer'].return_value.analyze_steps.assert_called_once()
        
        # Check that steps were passed to plugin
        call_args, call_kwargs = mock_plugin.generate_script.call_args
        assert call_kwargs['steps'] == ["analyzed_step1"]

    def test_convert_with_context_collection_failure(self, mock_dependencies, sample_automation_data):
        """Test convert when context collection fails."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .enable_context_collection(True) \
            .debug(True) \
            .build()
        
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_dependencies['context_collector'].return_value.collect_context.side_effect = Exception("Context error")
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "Script without context"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(config)
        # Should not raise exception, just continue without context
        result = converter.convert(sample_automation_data)
        
        assert result == "Script without context"
        
        # Check that context is empty dict in plugin call
        call_args, call_kwargs = mock_plugin.generate_script.call_args
        assert call_kwargs['context'] == {}

    def test_convert_with_ai_analysis_failure(self, mock_dependencies, sample_automation_data):
        """Test convert when AI analysis fails."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .enable_ai_analysis(True) \
            .debug(True) \
            .build()
        
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        mock_ai_provider = Mock()
        mock_dependencies['ai_factory'].return_value.create_provider.return_value = mock_ai_provider
        
        mock_dependencies['action_analyzer'].return_value.analyze_steps.side_effect = Exception("AI error")
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "Script without AI analysis"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(config)
        # In debug mode, original exception should be raised
        with pytest.raises(Exception, match="AI error"):
            converter.convert(sample_automation_data)

    def test_convert_parsing_failure(self, basic_config, mock_dependencies, sample_automation_data):
        """Test convert when input parsing fails."""
        mock_dependencies['input_parser'].return_value.parse.side_effect = ValueError("Invalid data")
        
        converter = E2eTestConverter(basic_config)
        
        with pytest.raises(RuntimeError, match="Failed to convert automation data"):
            converter.convert(sample_automation_data)

    def test_convert_plugin_failure(self, basic_config, mock_dependencies, sample_automation_data):
        """Test convert when plugin generation fails."""
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_plugin = Mock()
        mock_plugin.generate_script.side_effect = Exception("Plugin error")
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(basic_config)
        
        # The executor now raises RuntimeError on failure
        with pytest.raises(RuntimeError, match="Failed to convert automation data"):
            converter.convert(sample_automation_data)

    def test_convert_debug_mode_exceptions(self, mock_dependencies, sample_automation_data):
        """Test that exceptions are re-raised in debug mode."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .debug(True) \
            .build()
        
        mock_dependencies['input_parser'].return_value.parse.side_effect = ValueError("Parse error")
        
        converter = E2eTestConverter(config)
        
        # In debug mode, original exception should be raised
        with pytest.raises(ValueError, match="Parse error"):
            converter.convert(sample_automation_data)

    def test_validate_data(self, basic_config, mock_dependencies):
        """Test validate_data method."""
        mock_parsed_data = Mock()
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        mock_dependencies['input_parser'].return_value.validate.return_value = ["Error 1", "Error 2"]
        
        converter = E2eTestConverter(basic_config)
        errors = converter.validate_data(["some", "data"])
        
        assert errors == ["Error 1", "Error 2"]
        mock_dependencies['input_parser'].return_value.parse.assert_called_once_with(["some", "data"])
        mock_dependencies['input_parser'].return_value.validate.assert_called_once_with(mock_parsed_data)

    def test_validate_data_parsing_failure(self, basic_config, mock_dependencies):
        """Test validate_data when parsing fails."""
        mock_dependencies['input_parser'].return_value.parse.side_effect = ValueError("Parse error")
        
        converter = E2eTestConverter(basic_config)
        errors = converter.validate_data(["invalid", "data"])
        
        assert len(errors) == 1
        assert "Parsing failed: Parse error" in errors[0]

    def test_get_supported_frameworks(self, basic_config, mock_dependencies):
        """Test get_supported_frameworks method."""
        mock_dependencies['plugin_registry'].return_value.list_available_plugins.return_value = ["playwright", "selenium"]
        
        converter = E2eTestConverter(basic_config)
        frameworks = converter.get_supported_frameworks()
        
        assert frameworks == ["playwright", "selenium"]
        mock_dependencies['plugin_registry'].return_value.list_available_plugins.assert_called_once()

    def test_get_supported_ai_providers(self, basic_config, mock_dependencies):
        """Test get_supported_ai_providers method."""
        mock_dependencies['ai_factory'].return_value.list_available_providers.return_value = ["openai", "anthropic"]
        
        converter = E2eTestConverter(basic_config)
        providers = converter.get_supported_ai_providers()
        
        assert providers == ["openai", "anthropic"]
        mock_dependencies['ai_factory'].return_value.list_available_providers.assert_called_once()

    def test_convert_full_context_passing(self, mock_dependencies, sample_automation_data):
        """Test that all context is properly passed to the plugin."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .enable_context_collection(True) \
            .enable_ai_analysis(True) \
            .build()
        
        # Setup mocks
        mock_parsed_data = Mock()
        mock_parsed_data.steps = ["step1"]
        mock_dependencies['input_parser'].return_value.parse.return_value = mock_parsed_data
        
        mock_ai_provider = Mock()
        mock_dependencies['ai_factory'].return_value.create_provider.return_value = mock_ai_provider
        
        mock_context = Mock()
        mock_dependencies['context_collector'].return_value.collect_context.return_value = mock_context
        
        # Mock action analyzer
        mock_dependencies['action_analyzer'].return_value.analyze_steps.return_value = ["analyzed_step1"]
        
        mock_plugin = Mock()
        mock_plugin.generate_script.return_value = "Full context script"
        mock_dependencies['plugin_registry'].return_value.create_plugin.return_value = mock_plugin
        
        converter = E2eTestConverter(config)
        result = converter.convert(
            sample_automation_data, 
            target_url="https://example.com",
            context_hints={"test": "hint"}
        )
        
        assert result == "Full context script"
        
        # Verify all context was passed to plugin
        call_args, call_kwargs = mock_plugin.generate_script.call_args
        assert call_kwargs['steps'] == ["analyzed_step1"]
        assert call_kwargs['context'] == mock_context
        assert call_kwargs['config'] == config


class TestE2eTestConverterIntegration:
    """Integration tests for E2eTestConverter."""

    def test_converter_with_real_config(self):
        """Test E2eTestConverter with a real configuration."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4.1-mini") \
            .language("python") \
            .include_assertions(True) \
            .enable_context_collection(False) \
            .enable_ai_analysis(False) \
            .build()
        
        # Mock only the minimum required dependencies
        with patch('browse_to_test.core.executor.InputParser') as mock_parser, \
             patch('browse_to_test.core.executor.PluginRegistry') as mock_registry, \
             patch('browse_to_test.core.executor.ActionAnalyzer') as mock_analyzer:
            
            mock_parsed_data = Mock()
            mock_parsed_data.steps = ["step1"]
            mock_parser.return_value.parse.return_value = mock_parsed_data
            mock_analyzer.return_value.analyze_steps.return_value = ["analyzed_step1"]
            mock_plugin = Mock()
            mock_plugin.generate_script.return_value = "Real config script"
            mock_registry.return_value.create_plugin.return_value = mock_plugin
            
            converter = E2eTestConverter(config)
            result = converter.convert([{"test": "data"}])
            
            assert result == "Real config script"
            assert converter.config == config

    def test_converter_error_handling_consistency(self, sample_automation_data):
        """Test that converter error handling is consistent."""
        config = ConfigBuilder().framework("playwright").build()
        
        with patch('browse_to_test.core.executor.InputParser') as mock_parser:
            mock_parser.return_value.parse.side_effect = [
                ValueError("Error 1"),
                RuntimeError("Error 2"),
                Exception("Error 3")
            ]
            
            converter = E2eTestConverter(config)
            
            # Executor now raises RuntimeError on failure
            for _ in range(3):
                with pytest.raises(RuntimeError, match="Failed to convert automation data"):
                    converter.convert(sample_automation_data) 