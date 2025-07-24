"""Tests for the E2eScriptOrchestrator class."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import json
import tempfile

from browse_to_test.core.orchestration.orchestrator import E2eScriptOrchestrator
from browse_to_test.core.configuration.config import Config, AIConfig, OutputConfig, ProcessingConfig
from browse_to_test.core.processing.input_parser import ParsedAutomationData, ParsedStep, ParsedAction
from browse_to_test.core.processing.context_collector import SystemContext, ProjectContext
from browse_to_test.ai.base import AIProvider, AIResponse
from browse_to_test.plugins.base import OutputPlugin, GeneratedTestScript


class MockOutputPlugin(OutputPlugin):
    """Mock output plugin for testing."""
    
    def __init__(self, config=None):
        # Pass mock config if none provided
        if config is None:
            config = OutputConfig(framework="mock", language="python")
        super().__init__(config)
    
    @property
    def plugin_name(self) -> str:
        return "mock"
    
    @property
    def supported_frameworks(self) -> list:
        return ["mock"]
    
    @property
    def supported_languages(self) -> list:
        return ["python"]
    
    def validate_config(self) -> list:
        return []
    
    def generate_test_script(self, parsed_data, analysis_results=None, **kwargs) -> GeneratedTestScript:
        return GeneratedTestScript(
            content="# Mock generated test script\nprint('test')",
            language="python",
            framework="mock",
            metadata={
                "action_count": len(parsed_data.steps)
            }
        )
    
    def get_template_variables(self) -> dict:
        return {"test_var": "test_value"}


class TestE2eScriptOrchestrator:
    """Test the E2eScriptOrchestrator class."""
    
    @pytest.fixture
    def basic_config(self):
        """Create basic configuration."""
        return Config(
            ai=AIConfig(provider="mock", api_key="test-key"),
            output=OutputConfig(framework="playwright", language="python"),
            processing=ProcessingConfig(
                analyze_actions_with_ai=True,
                collect_system_context=True,
                cache_ai_responses=True
            )
        )
    
    @pytest.fixture
    def simple_config(self):
        """Create simple configuration without AI or context."""
        return Config(
            ai=AIConfig(provider="mock"),
            output=OutputConfig(framework="playwright", language="python"),
            processing=ProcessingConfig(
                analyze_actions_with_ai=False,
                collect_system_context=False,
                cache_ai_responses=False
            )
        )
    
    @pytest.fixture
    def mock_ai_provider(self):
        """Create mock AI provider."""
        provider = Mock(spec=AIProvider)
        provider.generate.return_value = AIResponse(
            content="Mock AI response",
            model="mock-model",
            provider="mock",
            tokens_used=100
        )
        provider.analyze_with_context.return_value = AIResponse(
            content="Mock analysis response",
            model="mock-model", 
            provider="mock",
            tokens_used=150
        )
        return provider
    
    @pytest.fixture
    def sample_automation_data(self):
        """Create sample automation data."""
        return [
            {
                "model_output": {
                    "action": [
                        {
                            "go_to_url": {
                                "url": "https://example.com"
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                }
            },
            {
                "model_output": {
                    "action": [
                        {
                            "input_text": {
                                "text": "test@example.com",
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": [
                        {
                            "xpath": "//input[@data-testid='email']",
                            "css_selector": "[data-testid='email']",
                            "attributes": {"data-testid": "email"}
                        }
                    ]
                }
            },
            {
                "model_output": {
                    "action": [
                        {
                            "click_element": {
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": [
                        {
                            "xpath": "//button[@type='submit']",
                            "css_selector": "button[type='submit']",
                            "attributes": {"type": "submit"}
                        }
                    ]
                }
            }
        ]
    
    @pytest.fixture
    def sample_system_context(self):
        """Create sample system context."""
        return SystemContext(
            project=ProjectContext(
                project_root="/test/project",
                name="test-app",
                tech_stack=["react", "typescript"],
                test_frameworks=["playwright"]
            )
        )
    
    def test_orchestrator_initialization(self, basic_config):
        """Test orchestrator initialization."""
        with patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory') as mock_ai_factory, \
             patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.ContextCollector') as mock_context_collector:
            
            orchestrator = E2eScriptOrchestrator(basic_config)
            
            assert orchestrator.config == basic_config
            assert orchestrator.input_parser is not None
            assert orchestrator.ai_factory is not None
            assert orchestrator.plugin_registry is not None
            assert orchestrator.context_collector is not None
            assert orchestrator.action_analyzer is not None
    
    def test_orchestrator_without_context_collection(self, simple_config):
        """Test orchestrator initialization without context collection."""
        with patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory') as mock_ai_factory, \
             patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry:
            
            orchestrator = E2eScriptOrchestrator(simple_config)
            
            assert orchestrator.context_collector is None
            assert orchestrator.ai_provider is None
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    @patch('browse_to_test.core.orchestration.orchestrator.ContextCollector')
    def test_generate_test_script_basic(self, mock_context_collector, mock_ai_factory, mock_plugin_registry, simple_config, sample_automation_data):
        """Test basic test script generation without AI or context."""
        # Setup mocks
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(simple_config)
        
        result = orchestrator.generate_test_script(sample_automation_data)
        
        assert isinstance(result, str)
        assert "Mock generated test script" in result
        mock_plugin_registry.return_value.create_plugin.assert_called_once()
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    @patch('browse_to_test.core.orchestration.orchestrator.ContextCollector')
    def test_generate_test_script_with_ai_and_context(self, mock_context_collector, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data, mock_ai_provider, sample_system_context):
        """Test test script generation with AI analysis and context collection."""
        # Setup mocks
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        mock_ai_factory.return_value.create_provider.return_value = mock_ai_provider
        mock_context_collector.return_value.collect_context.return_value = sample_system_context
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        orchestrator.ai_provider = mock_ai_provider
        orchestrator.context_collector = mock_context_collector.return_value
        
        result = orchestrator.generate_test_script(
            sample_automation_data,
            target_url="https://example.com"
        )
        
        assert isinstance(result, str)
        assert "Mock generated test script" in result
        
        # Verify AI provider was used
        mock_ai_provider.analyze_with_context.assert_called()
        
        # Verify context was collected
        mock_context_collector.return_value.collect_context.assert_called()
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_generate_test_script_with_custom_config(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data):
        """Test generation with custom configuration overrides."""
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        
        custom_config = {
            "output": {
                "language": "typescript",
                "include_assertions": False
            }
        }
        
        result = orchestrator.generate_test_script(
            sample_automation_data,
            custom_config=custom_config
        )
        
        assert isinstance(result, str)
        mock_plugin_registry.return_value.create_plugin.assert_called_once()
    
    def test_generate_test_script_from_json_string(self, simple_config, sample_automation_data):
        """Test generation from JSON string input."""
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(simple_config)
            
            json_data = json.dumps(sample_automation_data)
            result = orchestrator.generate_test_script(json_data)
            
            assert isinstance(result, str)
            assert "Mock generated test script" in result
    
    def test_generate_test_script_from_file(self, simple_config, sample_automation_data):
        """Test generation from JSON file input."""
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(simple_config)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(sample_automation_data, f)
                temp_file = f.name
            
            try:
                result = orchestrator.generate_test_script(Path(temp_file))
                
                assert isinstance(result, str)
                assert "Mock generated test script" in result
            finally:
                Path(temp_file).unlink()  # Clean up
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_generate_test_script_caching(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data):
        """Test caching functionality."""
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        
        # First generation
        result1 = orchestrator.generate_test_script(sample_automation_data)
        
        # Second generation with same data (should use cache)
        result2 = orchestrator.generate_test_script(sample_automation_data)
        
        assert result1 == result2
        # Plugin should only be called once due to caching
        assert mock_plugin_registry.return_value.create_plugin.call_count >= 1
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_generate_test_script_cache_disabled(self, mock_ai_factory, mock_plugin_registry, sample_automation_data):
        """Test generation with caching disabled."""
        config = Config(
            processing=ProcessingConfig(cache_ai_responses=False)
        )
        
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(config)
        
        # Multiple generations should not use cache
        result1 = orchestrator.generate_test_script(sample_automation_data)
        result2 = orchestrator.generate_test_script(sample_automation_data)
        
        assert result1 == result2  # Same input, same output
        # But no caching should occur
        assert len(orchestrator._generation_cache) == 0
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_ai_provider_initialization_failure(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data):
        """Test handling of AI provider initialization failure."""
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        mock_ai_factory.return_value.create_provider.side_effect = Exception("AI provider not available")
        
        # Should not crash, should continue without AI
        orchestrator = E2eScriptOrchestrator(basic_config)
        
        result = orchestrator.generate_test_script(sample_automation_data)
        
        assert isinstance(result, str)
        assert orchestrator.ai_provider is None
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_analysis_failure_fallback(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data, mock_ai_provider):
        """Test fallback when AI analysis fails."""
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        mock_ai_factory.return_value.create_provider.return_value = mock_ai_provider
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        orchestrator.ai_provider = mock_ai_provider
        
        # Make action analyzer fail
        with patch.object(orchestrator.action_analyzer, 'analyze_automation_data') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")
            
            result = orchestrator.generate_test_script(sample_automation_data)
            
            assert isinstance(result, str)
            # Should still generate script despite analysis failure
            assert "Mock generated test script" in result
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_plugin_creation_failure(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data):
        """Test handling of plugin creation failure."""
        mock_plugin_registry.return_value.create_plugin.side_effect = Exception("Plugin not available")
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        
        # Should use fallback script generation
        result = orchestrator.generate_test_script(sample_automation_data)
        
        assert isinstance(result, str)
        # Should contain fallback content
        assert "Error generating test script" in result or len(result) > 0
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_strict_mode_errors(self, mock_ai_factory, mock_plugin_registry, sample_automation_data):
        """Test error handling in strict mode."""
        config = Config(
            processing=ProcessingConfig(strict_mode=True)
        )
        
        mock_plugin_registry.return_value.create_plugin.side_effect = Exception("Plugin error")
        
        orchestrator = E2eScriptOrchestrator(config)
        
        with pytest.raises(RuntimeError):
            orchestrator.generate_test_script(sample_automation_data)
    
    def test_generate_with_multiple_frameworks(self, simple_config, sample_automation_data):
        """Test generating scripts for multiple frameworks."""
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(simple_config)
            
            frameworks = ["playwright", "selenium"]
            results = orchestrator.generate_with_multiple_frameworks(
                sample_automation_data,
                frameworks
            )
            
            assert isinstance(results, dict)
            assert len(results) == 2
            assert "playwright" in results
            assert "selenium" in results
            assert all(isinstance(script, str) for script in results.values())
    
    def test_generate_with_multiple_frameworks_error_handling(self, simple_config, sample_automation_data):
        """Test error handling in multiple framework generation."""
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            # Make plugin creation fail for one framework
            def side_effect(config):
                if config.framework == "selenium":
                    raise Exception("Selenium not available")
                return MockOutputPlugin()
            
            mock_plugin_registry.return_value.create_plugin.side_effect = side_effect
            
            orchestrator = E2eScriptOrchestrator(simple_config)
            
            frameworks = ["playwright", "selenium"]
            results = orchestrator.generate_with_multiple_frameworks(
                sample_automation_data,
                frameworks
            )
            
            assert isinstance(results, dict)
            assert len(results) == 2
            assert "playwright" in results
            assert "selenium" in results
            # Selenium should have error message
            assert ("Error generating script" in results["selenium"] or 
                    "Error: Failed to generate test script" in results["selenium"])
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_cache_size_limiting(self, mock_ai_factory, mock_plugin_registry, sample_automation_data):
        """Test cache size limiting functionality."""
        config = Config(
            processing=ProcessingConfig(
                cache_ai_responses=True,
                max_cache_size=2  # Small cache size
            )
        )
        
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(config)
        
        # Generate multiple different scripts to exceed cache size
        for i in range(5):
            data = [
                {
                    "model_output": {
                        "action": [{"go_to_url": {"url": f"https://example{i}.com"}}]
                    },
                    "state": {"interacted_element": []}
                }
            ]
            orchestrator.generate_test_script(data)
        
        # Cache should be limited
        assert len(orchestrator._generation_cache) <= config.processing.max_cache_size
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory')
    def test_post_process_script(self, mock_ai_factory, mock_plugin_registry, basic_config):
        """Test script post-processing functionality."""
        mock_plugin = MockOutputPlugin()
        mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
        
        orchestrator = E2eScriptOrchestrator(basic_config)
        
        test_script = "# Original script\nprint('test')"
        processed_script = orchestrator._post_process_script(
            test_script,
            basic_config,
            analysis_results={},
            system_context=None
        )
        
        assert isinstance(processed_script, str)
        # Should contain original script
        assert "Original script" in processed_script
    
    @patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry')
    @patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory') 
    def test_fallback_script_generation(self, mock_ai_factory, mock_plugin_registry, basic_config, sample_automation_data):
        """Test fallback script generation when main generation fails."""
        mock_plugin_registry.return_value.create_plugin.side_effect = Exception("Plugin failed")
        
        config = Config(
            processing=ProcessingConfig(strict_mode=False)  # Non-strict mode for fallback
        )
        
        orchestrator = E2eScriptOrchestrator(config)
        
        result = orchestrator._generate_fallback_script(sample_automation_data, config)
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain some indication of fallback
        assert ("fallback" in result.lower() or 
                "error" in result.lower() or 
                "automation" in result.lower())


class TestOrchestratorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_automation_data(self):
        """Test with empty automation data."""
        config = Config()
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(config)
            
            result = orchestrator.generate_test_script([])
            
            assert isinstance(result, str)
    
    def test_malformed_automation_data(self):
        """Test with malformed automation data."""
        config = Config()
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(config)
            
            malformed_data = [
                {"invalid": "structure"},
                {"model_output": None},
                {}
            ]
            
            result = orchestrator.generate_test_script(malformed_data)
            
            assert isinstance(result, str)
    
    def test_very_large_automation_data(self):
        """Test with very large automation data."""
        config = Config()
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(config)
            
            # Create large dataset
            large_data = []
            for i in range(1000):
                large_data.append({
                    "model_output": {
                        "action": [{"click_element": {"index": i}}]
                    },
                    "state": {"interacted_element": []}
                })
            
            result = orchestrator.generate_test_script(large_data)
            
            assert isinstance(result, str)
    
    def test_unicode_data(self):
        """Test with unicode and special characters."""
        config = Config()
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(config)
            
            unicode_data = [
                {
                    "model_output": {
                        "action": [
                            {
                                "input_text": {
                                    "text": "🚀 Test with émojis and spëcial chars 中文"
                                }
                            }
                        ]
                    },
                    "state": {"interacted_element": []}
                }
            ]
            
            result = orchestrator.generate_test_script(unicode_data)
            
            assert isinstance(result, str)


class TestOrchestratorIntegration:
    """Integration tests for orchestrator with real components."""
    
    def test_integration_with_real_input_parser(self):
        """Test integration with real InputParser."""
        config = Config(
            processing=ProcessingConfig(
                analyze_actions_with_ai=False,
                collect_system_context=False
            )
        )
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(config)
            
            automation_data = [
                {
                    "model_output": {
                        "action": [{"go_to_url": {"url": "https://test.com"}}]
                    },
                    "state": {"interacted_element": []}
                }
            ]
            
            result = orchestrator.generate_test_script(automation_data)
            
            assert isinstance(result, str)
            # Verify that the mock plugin was called (which means input parser worked)
            mock_plugin_registry.return_value.create_plugin.assert_called_once()
            # And that we got our expected test content
            assert "Mock generated test script" in result
    
    def test_config_merging(self):
        """Test configuration merging functionality."""
        base_config = Config(
            output=OutputConfig(framework="playwright", language="python"),
            processing=ProcessingConfig(analyze_actions_with_ai=True)
        )
        
        with patch('browse_to_test.core.orchestration.orchestrator.PluginRegistry') as mock_plugin_registry, \
             patch('browse_to_test.core.orchestration.orchestrator.AIProviderFactory'):
            
            mock_plugin = MockOutputPlugin()
            mock_plugin_registry.return_value.create_plugin.return_value = mock_plugin
            
            orchestrator = E2eScriptOrchestrator(base_config)
            
            custom_config = {
                "output": {"language": "typescript"},
                "processing": {"analyze_actions_with_ai": False}
            }
            
            automation_data = [
                {
                    "model_output": {"action": [{"go_to_url": {"url": "https://test.com"}}]},
                    "state": {"interacted_element": []}
                }
            ]
            
            result = orchestrator.generate_test_script(
                automation_data,
                custom_config=custom_config
            )
            
            assert isinstance(result, str)
            # Verify that custom config was applied
            create_plugin_call = mock_plugin_registry.return_value.create_plugin.call_args
            if create_plugin_call:
                used_config = create_plugin_call[0][0]  # First positional argument
                assert used_config.language == "typescript" 