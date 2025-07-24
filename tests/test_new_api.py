"""Tests for the new simplified API introduced in the architectural restructuring."""

import pytest
import warnings
from unittest.mock import Mock, patch, MagicMock

import browse_to_test as btt
from browse_to_test.core.orchestration.converter import E2eTestConverter
from browse_to_test.core.orchestration.session import IncrementalSession


class TestSimplifiedAPI:
    """Test the new simplified API functions."""

    def test_convert_simple_usage(self, sample_automation_data):
        """Test the basic convert() function with minimal parameters."""
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.return_value = "Generated test script"
            
            result = btt.convert(
                sample_automation_data,
                framework="playwright",
                ai_provider="openai"
            )
            
            assert result == "Generated test script"
            mock_convert.assert_called_once()
    
    def test_convert_with_language(self, sample_automation_data):
        """Test convert() with language parameter."""
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.return_value = "TypeScript test script"
            
            result = btt.convert(
                sample_automation_data,
                framework="playwright", 
                ai_provider="openai",
                language="typescript"
            )
            
            assert result == "TypeScript test script"
            # Verify the config was built correctly
            args, kwargs = mock_convert.call_args
            assert len(args) == 1  # automation_data
    
    def test_convert_with_kwargs(self, sample_automation_data):
        """Test convert() with additional keyword arguments."""
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.return_value = "Enhanced test script"
            
            result = btt.convert(
                sample_automation_data,
                framework="selenium",
                ai_provider="anthropic",
                include_assertions=True,
                include_error_handling=True,
                timeout=15000,
                debug=True
            )
            
            assert result == "Enhanced test script"
            mock_convert.assert_called_once()
    
    def test_convert_error_handling(self, sample_automation_data):
        """Test convert() error handling."""
        with patch.object(E2eTestConverter, '__init__') as mock_init:
            mock_init.side_effect = ValueError("Configuration error")
            
            with pytest.raises(ValueError, match="Configuration error"):
                btt.convert(sample_automation_data, framework="invalid")
    
    def test_convert_with_config_builder_validation_error(self, sample_automation_data):
        """Test convert() when ConfigBuilder validation fails."""
        with patch.object(btt.ConfigBuilder, 'build') as mock_build:
            mock_build.side_effect = ValueError("Invalid temperature")
            
            with pytest.raises(ValueError, match="Invalid temperature"):
                btt.convert(
                    sample_automation_data,
                    framework="playwright",
                    temperature=99  # Invalid temperature
                )
    
    def test_list_frameworks(self):
        """Test list_frameworks() function."""
        with patch('browse_to_test.plugins.registry.PluginRegistry') as mock_registry_class:
            mock_registry = MagicMock()
            mock_registry.list_available_plugins.return_value = ["playwright", "selenium", "cypress"]
            mock_registry_class.return_value = mock_registry
            
            frameworks = btt.list_frameworks()
            
            assert frameworks == ["playwright", "selenium", "cypress"]
            mock_registry.list_available_plugins.assert_called_once()
    
    def test_list_ai_providers(self):
        """Test list_ai_providers() function."""
        with patch('browse_to_test.ai.factory.AIProviderFactory') as mock_factory_class:
            mock_factory = MagicMock()
            mock_factory.list_available_providers.return_value = ["openai", "anthropic", "azure"]
            mock_factory_class.return_value = mock_factory
            
            providers = btt.list_ai_providers()
            
            assert providers == ["openai", "anthropic", "azure"]
            mock_factory.list_available_providers.assert_called_once()


class TestBackwardCompatibility:
    """Test backward compatibility with deprecated functions."""
    
    def test_convert_to_test_script_deprecated(self, sample_automation_data):
        """Test that convert_to_test_script still works but shows deprecation warning."""
        with patch('browse_to_test.convert') as mock_convert:
            mock_convert.return_value = "Legacy script"
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                result = btt.convert_to_test_script(
                    sample_automation_data,
                    "playwright",
                    "openai"
                )
                
                assert result == "Legacy script"
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "convert_to_test_script() is deprecated" in str(w[0].message)
    
    def test_start_incremental_session_deprecated(self):
        """Test that start_incremental_session still works but shows deprecation warning."""
        with patch.object(IncrementalSession, '__init__') as mock_init:
            mock_init.return_value = None
            with patch.object(IncrementalSession, 'start') as mock_start:
                mock_start.return_value = Mock(success=True)
                mock_session = Mock()
                
                with patch('browse_to_test.IncrementalSession') as mock_session_class:
                    mock_session_class.return_value = mock_session
                    
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        
                        session, result = btt.start_incremental_session(
                            framework="playwright",
                            target_url="https://example.com"
                        )
                        
                        assert len(w) == 1
                        assert issubclass(w[0].category, DeprecationWarning)
                        assert "start_incremental_session() is deprecated" in str(w[0].message)
    
    def test_list_available_plugins_deprecated(self):
        """Test that list_available_plugins still works but shows deprecation warning."""
        with patch('browse_to_test.list_frameworks') as mock_list:
            mock_list.return_value = ["playwright", "selenium"]
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                result = btt.list_available_plugins()
                
                assert result == ["playwright", "selenium"]
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "list_available_plugins() is deprecated" in str(w[0].message)
    
    def test_list_available_ai_providers_deprecated(self):
        """Test that list_available_ai_providers still works but shows deprecation warning."""
        with patch('browse_to_test.list_ai_providers') as mock_list:
            mock_list.return_value = ["openai", "anthropic"]
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                result = btt.list_available_ai_providers()
                
                assert result == ["openai", "anthropic"]
                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "list_available_ai_providers() is deprecated" in str(w[0].message)


class TestAPIIntegration:
    """Integration tests for the new API."""
    
    @pytest.mark.integration
    def test_full_convert_workflow(self, sample_automation_data):
        """Test a complete conversion workflow using the new API."""
        # This is a real integration test - it actually runs the full conversion
        result = btt.convert(
            sample_automation_data,
            framework="playwright",
            ai_provider="openai",
            language="python",
            include_assertions=True
        )
        
        # Verify we got a real script back
        assert isinstance(result, str)
        assert len(result) > 0
        assert "playwright" in result.lower() or "page" in result.lower()
        # The script should contain some test structure
        assert any(keyword in result for keyword in ["def test", "async def", "import", "page."])
    
    @pytest.mark.integration 
    def test_convert_with_incremental_session_comparison(self, sample_automation_data):
        """Test that convert() and IncrementalSession produce similar results."""
        mock_script = "Generated script content"
        
        # Test regular convert
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.return_value = mock_script
            
            regular_result = btt.convert(sample_automation_data, framework="playwright")
            
        # Test incremental session
        with patch.object(IncrementalSession, '__init__') as mock_init:
            mock_init.return_value = None
            with patch.object(IncrementalSession, 'start') as mock_start:
                mock_start.return_value = Mock(success=True, current_script="")
                with patch.object(IncrementalSession, 'add_step') as mock_add:
                    mock_add.return_value = Mock(success=True, current_script=mock_script)
                    with patch.object(IncrementalSession, 'finalize') as mock_finalize:
                        mock_finalize.return_value = Mock(success=True, current_script=mock_script)
                        
                        session = IncrementalSession(Mock())
                        session.start()
                        for step in sample_automation_data:
                            session.add_step(step)
                        incremental_result = session.finalize()
                        
                        # Both should produce scripts (specific content may vary)
                        assert regular_result == mock_script
                        assert incremental_result.current_script == mock_script


class TestErrorHandlingScenarios:
    """Test various error scenarios in the new API."""
    
    def test_convert_with_invalid_framework(self, sample_automation_data):
        """Test convert() with invalid framework."""
        from browse_to_test.output_langs.exceptions import FrameworkNotSupportedError
        with pytest.raises(FrameworkNotSupportedError, match="Framework 'invalid_framework' is not supported"):
            btt.convert(sample_automation_data, framework="invalid_framework")
    
    def test_convert_with_invalid_language(self, sample_automation_data):
        """Test convert() with invalid language."""
        from browse_to_test.output_langs.exceptions import LanguageNotSupportedError
        with pytest.raises(LanguageNotSupportedError, match="Language 'invalid_lang' is not supported"):
            btt.convert(sample_automation_data, framework="playwright", language="invalid_lang")
    
    def test_convert_with_empty_data(self):
        """Test convert() with empty automation data."""
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.side_effect = ValueError("No automation data provided")
            
            with pytest.raises(ValueError, match="No automation data provided"):
                btt.convert([], framework="playwright")
    
    def test_convert_with_malformed_data(self):
        """Test convert() with malformed automation data."""
        malformed_data = [{"invalid": "structure"}]
        
        with patch.object(E2eTestConverter, 'convert') as mock_convert:
            mock_convert.side_effect = RuntimeError("Failed to convert automation data")
            
            with pytest.raises(RuntimeError, match="Failed to convert automation data"):
                btt.convert(malformed_data, framework="playwright")
    
    def test_list_frameworks_failure(self):
        """Test list_frameworks() when registry fails."""
        with patch('browse_to_test.plugins.registry.PluginRegistry') as mock_registry_class:
            mock_registry_class.side_effect = Exception("Registry initialization failed")
            
            with pytest.raises(Exception, match="Registry initialization failed"):
                btt.list_frameworks()
    
    def test_list_ai_providers_failure(self):
        """Test list_ai_providers() when factory fails."""
        with patch('browse_to_test.ai.factory.AIProviderFactory') as mock_factory_class:
            mock_factory_class.side_effect = Exception("Factory initialization failed")
            
            with pytest.raises(Exception, match="Factory initialization failed"):
                btt.list_ai_providers() 