"""Integration tests for the architectural restructuring.

These tests verify that all components work together correctly
and that the new API provides the expected functionality.
"""

import pytest
import warnings
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

import browse_to_test as btt
from browse_to_test.core.configuration.config import ConfigBuilder
from browse_to_test.core.orchestration.converter import E2eTestConverter
from browse_to_test.core.orchestration.session import IncrementalSession


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    @pytest.mark.integration
    def test_simple_convert_workflow(self, sample_automation_data):
        """Test the simplest possible conversion workflow."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
            
            # Setup mocks
            mock_parser.return_value.parse.return_value = Mock()
            mock_plugin = Mock()
            mock_plugin.generate_test_script.return_value = "# Playwright test\nprint('Hello')"
            mock_registry.return_value.create_plugin.return_value = mock_plugin
            
            # Execute conversion
            result = btt.convert(sample_automation_data, framework="playwright")
            
            # Verify result
            assert result == "# Playwright test\nprint('Hello')"
            assert "Playwright" in result
            
            # Verify components were called correctly
            mock_parser.assert_called_once()
            mock_registry.assert_called_once()

    @pytest.mark.integration
    def test_advanced_convert_workflow(self, complex_automation_data):
        """Test advanced conversion with all features enabled."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry, \
             patch('browse_to_test.core.orchestration.converter.AIProviderFactory') as mock_ai_factory, \
             patch('browse_to_test.core.orchestration.converter.ActionAnalyzer') as mock_analyzer, \
             patch('browse_to_test.core.orchestration.converter.ContextCollector') as mock_context:
            
            # Setup comprehensive mocks
            mock_parser.return_value.parse.return_value = Mock()
            
            mock_ai_provider = Mock()
            mock_ai_factory.return_value.create_provider.return_value = mock_ai_provider
            
            mock_analysis = Mock()
            mock_analyzer.return_value.analyze_comprehensive.return_value = mock_analysis
            
            mock_system_context = Mock()
            mock_context.return_value.collect_context.return_value = mock_system_context
            
            mock_plugin = Mock()
            mock_plugin.generate_test_script.return_value = "# Advanced Selenium test with AI"
            mock_registry.return_value.create_plugin.return_value = mock_plugin
            
            # Execute advanced conversion
            result = btt.convert(
                complex_automation_data,
                framework="selenium",
                ai_provider="openai",
                language="python",
                include_assertions=True,
                include_error_handling=True,
                context_collection=True,
                project_root="/test/project"
            )
            
            # Verify result
            assert result == "# Advanced Selenium test with AI"
            
            # Verify all advanced features were used
            mock_ai_factory.return_value.create_provider.assert_called_once()
            mock_analyzer.return_value.analyze_comprehensive.assert_called_once()
            mock_context.return_value.collect_context.assert_called_once()

    @pytest.mark.integration
    def test_incremental_session_workflow(self, sample_automation_data):
        """Test complete incremental session workflow."""
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class:
            mock_converter = MagicMock()
            mock_converter.convert.side_effect = [
                "# Test with step 1\npage.goto('https://example.com')",
                "# Test with step 1-2\npage.goto('https://example.com')\npage.fill('input', 'test')",
                "# Complete test\npage.goto('https://example.com')\npage.fill('input', 'test')\npage.click('button')"
            ]
            mock_converter.validate_data.return_value = []
            mock_converter_class.return_value = mock_converter
            
            # Create session with advanced config
            config = btt.ConfigBuilder() \
                .framework("playwright") \
                .language("python") \
                .include_assertions(True) \
                .build()
            
            session = btt.IncrementalSession(config)
            
            # Execute complete workflow
            start_result = session.start("https://example.com")
            assert start_result.success
            assert session.is_active()
            
            # Add steps incrementally
            for i, step in enumerate(sample_automation_data):
                result = session.add_step(step)
                assert result.success
                assert result.step_count == i + 1
                assert "page." in result.current_script
            
            # Finalize session
            final_result = session.finalize()
            assert final_result.success
            assert not session.is_active()
            assert final_result.step_count == 3
            assert "Complete test" in final_result.current_script

    @pytest.mark.integration
    def test_config_builder_to_converter_integration(self):
        """Test ConfigBuilder integration with E2eTestConverter."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
            
            mock_parser.return_value.parse.return_value = Mock()
            mock_plugin = Mock()
            mock_plugin.generate_test_script.return_value = "# Config-driven test"
            mock_registry.return_value.create_plugin.return_value = mock_plugin
            
            # Build complex configuration
            config = btt.ConfigBuilder() \
                .framework("playwright") \
                .ai_provider("openai", model="gpt-4", api_key="test-key") \
                .language("typescript") \
                .include_assertions(True) \
                .include_error_handling(True) \
                .enable_context_collection(False) \
                .enable_ai_analysis(False) \
                .temperature(0.3) \
                .timeout(25000) \
                .debug(True) \
                .build()
            
            # Create converter with config
            converter = btt.E2eTestConverter(config)
            result = converter.convert([{"test": "data"}])
            
            # Verify configuration was applied
            assert result == "# Config-driven test"
            assert converter.config.output.framework == "playwright"
            assert converter.config.ai.provider == "openai"
            assert converter.config.ai.model == "gpt-4"
            assert converter.config.output.language == "typescript"
            assert converter.config.output.include_assertions is True
            assert converter.config.ai.temperature == 0.3

    @pytest.mark.integration 
    def test_error_propagation_through_stack(self, sample_automation_data):
        """Test that errors propagate correctly through the component stack."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser:
            
            # Test different error types at different levels
            error_scenarios = [
                (ValueError("Invalid automation data"), "parsing"),
                (RuntimeError("Plugin creation failed"), "plugin"),
                (Exception("Unknown error"), "general")
            ]
            
            for error, error_type in error_scenarios:
                mock_parser.return_value.parse.side_effect = error
                
                # Error should be wrapped in RuntimeError (unless debug mode)
                with pytest.raises(RuntimeError, match="Failed to convert automation data"):
                    btt.convert(sample_automation_data, framework="playwright")
                
                # In debug mode, original error should be preserved
                with pytest.raises(type(error)):
                    btt.convert(sample_automation_data, framework="playwright", debug=True)

    @pytest.mark.integration
    def test_validation_across_components(self, sample_automation_data):
        """Test validation consistency across components."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser:
            mock_parser.return_value.parse.return_value = Mock()
            mock_parser.return_value.validate.return_value = ["Input validation error"]
            
            # Test validation through E2eTestConverter
            config = btt.ConfigBuilder().framework("playwright").build()
            converter = btt.E2eTestConverter(config)
            
            errors = converter.validate_data(sample_automation_data)
            assert "Input validation error" in errors
            
            # Test validation through IncrementalSession
            with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_session_converter:
                mock_session_converter.return_value.validate_data.return_value = ["Session validation error"]
                
                session = btt.IncrementalSession(config)
                session.start()
                
                result = session.add_step(sample_automation_data[0], validate=True)
                assert "Session validation error" in result.validation_issues


class TestBackwardCompatibilityIntegration:
    """Test that backward compatibility works in practice."""

    @pytest.mark.integration
    def test_old_api_still_works(self, sample_automation_data):
        """Test that the old API still produces the same results."""
        with patch('browse_to_test.convert') as mock_new_convert:
            mock_new_convert.return_value = "Generated with new API"
            
            # Test old function calls new function internally
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                result = btt.convert_to_test_script(
                    sample_automation_data,
                    "playwright", 
                    "openai"
                )
                
                assert result == "Generated with new API"
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                
                # Verify new API was called with correct parameters
                mock_new_convert.assert_called_once()

    @pytest.mark.integration
    def test_old_incremental_api_compatibility(self):
        """Test that old incremental API works with new implementation."""
        with patch('browse_to_test.IncrementalSession') as mock_session_class:
            mock_session = MagicMock()
            mock_result = Mock(success=True)
            mock_session.start.return_value = mock_result
            mock_session_class.return_value = mock_session
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                session, result = btt.start_incremental_session(
                    framework="playwright",
                    target_url="https://example.com"
                )
                
                assert result.success is True
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                
                # Verify new session was created correctly
                mock_session_class.assert_called_once()
                mock_session.start.assert_called_once_with(
                    target_url="https://example.com",
                    context_hints=None
                )

    @pytest.mark.integration
    def test_old_utility_functions_compatibility(self):
        """Test that old utility functions work with new implementation."""
        with patch('browse_to_test.list_frameworks') as mock_new_frameworks, \
             patch('browse_to_test.list_ai_providers') as mock_new_providers:
            
            mock_new_frameworks.return_value = ["playwright", "selenium"]
            mock_new_providers.return_value = ["openai", "anthropic"]
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                frameworks = btt.list_available_plugins()
                providers = btt.list_available_ai_providers()
                
                assert frameworks == ["playwright", "selenium"]
                assert providers == ["openai", "anthropic"]
                assert len(w) == 2  # Two deprecation warnings
                
                for warning in w:
                    assert issubclass(warning.category, DeprecationWarning)


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    @pytest.mark.integration
    def test_file_based_automation_data(self):
        """Test conversion from file-based automation data."""
        # Create temporary file with test data
        automation_data = [
            {
                "model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]},
                "state": {"interacted_element": []}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(automation_data, f)
            temp_file = f.name
        
        try:
            with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
                 patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
                
                mock_parser.return_value.parse.return_value = Mock()
                mock_plugin = Mock()
                mock_plugin.generate_test_script.return_value = "# File-based test"
                mock_registry.return_value.create_plugin.return_value = mock_plugin
                
                # Test conversion from file path
                result = btt.convert(temp_file, framework="playwright")
                assert result == "# File-based test"
                
                # Verify file was passed to parser
                mock_parser.return_value.parse.assert_called_once_with(temp_file)
        finally:
            Path(temp_file).unlink()

    @pytest.mark.integration
    def test_multiple_framework_generation(self, sample_automation_data):
        """Test generating tests for multiple frameworks from same data."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
            
            mock_parser.return_value.parse.return_value = Mock()
            
            # Mock different plugins for different frameworks
            def create_plugin_side_effect(config):
                mock_plugin = Mock()
                framework = config.framework
                mock_plugin.generate_test_script.return_value = f"# {framework.title()} test script"
                return mock_plugin
            
            mock_registry.return_value.create_plugin.side_effect = create_plugin_side_effect
            
            frameworks = ["playwright", "selenium"]
            results = {}
            
            for framework in frameworks:
                result = btt.convert(sample_automation_data, framework=framework)
                results[framework] = result
                assert f"{framework.title()} test script" in result
            
            # Verify different results for different frameworks
            assert results["playwright"] != results["selenium"]
            assert "Playwright" in results["playwright"]
            assert "Selenium" in results["selenium"]

    @pytest.mark.integration
    def test_language_specific_generation(self, sample_automation_data):
        """Test generating tests in different programming languages."""
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
            
            mock_parser.return_value.parse.return_value = Mock()
            
            def create_plugin_side_effect(config):
                mock_plugin = Mock()
                language = config.language
                mock_plugin.generate_test_script.return_value = f"// {language.title()} test code"
                return mock_plugin
            
            mock_registry.return_value.create_plugin.side_effect = create_plugin_side_effect
            
            languages = ["python", "typescript", "javascript"]
            results = {}
            
            for language in languages:
                result = btt.convert(
                    sample_automation_data, 
                    framework="playwright",
                    language=language
                )
                results[language] = result
                assert f"{language.title()} test code" in result
            
            # Verify different results for different languages
            assert len(set(results.values())) == len(languages)

    @pytest.mark.integration
    def test_configuration_persistence_across_operations(self):
        """Test that configuration persists correctly across multiple operations."""
        # Build a complex configuration
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4") \
            .language("typescript") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .temperature(0.2) \
            .timeout(20000) \
            .debug(True) \
            .build()
        
        with patch('browse_to_test.core.orchestration.converter.InputParser') as mock_parser, \
             patch('browse_to_test.core.orchestration.converter.PluginRegistry') as mock_registry:
            
            mock_parser.return_value.parse.return_value = Mock()
            mock_plugin = Mock()
            mock_plugin.generate_test_script.return_value = "# Persistent config test"
            mock_registry.return_value.create_plugin.return_value = mock_plugin
            
            # Create converter and perform multiple operations
            converter = btt.E2eTestConverter(config)
            
            # Test that config persists across operations
            result1 = converter.convert([{"step": 1}])
            result2 = converter.convert([{"step": 2}])
            
            # Both operations should use the same configuration
            assert result1 == "# Persistent config test"
            assert result2 == "# Persistent config test"
            
            # Verify config hasn't changed
            assert converter.config.output.framework == "playwright"
            assert converter.config.ai.model == "gpt-4"
            assert converter.config.output.language == "typescript"
            assert converter.config.ai.temperature == 0.2

    @pytest.mark.integration
    def test_error_recovery_in_incremental_session(self, sample_automation_data):
        """Test that incremental sessions can recover from errors."""
        config = btt.ConfigBuilder().framework("playwright").build()
        
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class:
            mock_converter = MagicMock()
            
            # Simulate intermittent failures
            mock_converter.convert.side_effect = [
                "Script with step 1",  # Success
                Exception("Network error"),  # Failure
                "Script with step 1 and 3",  # Recovery
                "Final script"  # Success
            ]
            mock_converter.validate_data.return_value = []
            mock_converter_class.return_value = mock_converter
            
            session = btt.IncrementalSession(config)
            session.start()
            
            # Add steps with intermittent failures
            result1 = session.add_step(sample_automation_data[0])
            assert result1.success  # Should succeed
            
            result2 = session.add_step(sample_automation_data[1])
            assert result2.success  # Graceful error handling
            
            result3 = session.add_step(sample_automation_data[2])
            assert result3.success  # Should recover
            
            # Session should still be functional
            assert session.is_active()
            final_result = session.finalize()
            assert final_result.success 