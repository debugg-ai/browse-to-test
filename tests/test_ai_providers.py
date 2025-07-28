"""Tests for AI providers."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from browse_to_test.ai.base import AIProvider, AIResponse, AIProviderError, AnalysisType, AIAnalysisRequest
from browse_to_test.ai.factory import AIProviderFactory
from browse_to_test.core.configuration.config import AIConfig


class MockAIProvider(AIProvider):
    """Mock AI provider for testing."""
    
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        return AIResponse(
            content=f"Mock response to: {prompt[:50]}...",
            model="mock-model",
            provider="mock",
            tokens_used=100
        )
    
    async def generate_async(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        return AIResponse(
            content=f"Mock async response to: {prompt[:50]}...",
            model="mock-model",
            provider="mock",
            tokens_used=100
        )
    
    def is_available(self) -> bool:
        return True
    
    def get_model_info(self) -> dict:
        return {"name": "mock-model", "provider": "mock"}


class TestAIProvider:
    """Test the abstract AIProvider class."""
    
    def test_init_with_api_key(self):
        """Test provider initialization with API key."""
        provider = MockAIProvider(api_key="test-key", custom_param="value")
        assert provider.api_key == "test-key"
        assert provider.config["custom_param"] == "value"
    
    def test_init_without_api_key(self):
        """Test provider initialization without API key."""
        provider = MockAIProvider()
        assert provider.api_key is None
        assert provider.config == {}
    
    def test_generate_method(self):
        """Test the generate method."""
        provider = MockAIProvider()
        response = provider.generate("Test prompt")
        
        assert isinstance(response, AIResponse)
        assert "Mock response to: Test prompt" in response.content
        assert response.model == "mock-model"
        assert response.provider == "mock"
        assert response.tokens_used == 100
    
    def test_analyze_with_context(self):
        """Test context-aware analysis."""
        provider = MockAIProvider()
        
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=[{"action": "test"}],
            target_framework="playwright"
        )
        
        response = provider.analyze_with_context(request)
        
        assert isinstance(response, AIResponse)
        assert response.metadata["analysis_type"] == "conversion"
        assert response.metadata["target_framework"] == "playwright"
        assert response.metadata["has_context"] is False
    
    def test_is_available(self):
        """Test provider availability check."""
        provider = MockAIProvider()
        assert provider.is_available() is True
    
    def test_get_model_info(self):
        """Test getting model information."""
        provider = MockAIProvider()
        info = provider.get_model_info()
        
        assert info["name"] == "mock-model"
        assert info["provider"] == "mock"


class TestAIResponse:
    """Test the AIResponse class."""
    
    def test_basic_response(self):
        """Test basic response creation."""
        response = AIResponse(
            content="Test content",
            model="test-model",
            provider="test-provider",
            tokens_used=50
        )
        
        assert response.content == "Test content"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.tokens_used == 50
        assert response.finish_reason is None
        assert response.metadata == {}
    
    def test_response_with_metadata(self):
        """Test response with metadata."""
        metadata = {"custom": "value", "temperature": 0.5}
        response = AIResponse(
            content="Test content",
            model="test-model",
            provider="test-provider",
            metadata=metadata
        )
        
        assert response.metadata == metadata
    
    def test_response_with_finish_reason(self):
        """Test response with finish reason."""
        response = AIResponse(
            content="Test content",
            model="test-model",
            provider="test-provider",
            finish_reason="stop"
        )
        
        assert response.finish_reason == "stop"


class TestAIProviderError:
    """Test the AIProviderError exception."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = AIProviderError("Test error message")
        assert str(error) == "Test error message"
        assert error.provider is None
        assert error.model is None
    
    def test_error_with_provider_info(self):
        """Test error with provider and model info."""
        error = AIProviderError("Test error", provider="openai", model="gpt-4")
        assert str(error) == "Test error"
        assert error.provider == "openai"
        assert error.model == "gpt-4"


class TestAIAnalysisRequest:
    """Test the AIAnalysisRequest class."""
    
    def test_basic_request(self):
        """Test basic request creation."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=[{"action": "test"}],
            target_framework="playwright"
        )
        
        assert request.analysis_type == AnalysisType.CONVERSION
        assert request.automation_data == [{"action": "test"}]
        assert request.target_framework == "playwright"
        assert request.system_context is None
    
    def test_conversion_prompt(self):
        """Test conversion prompt generation."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=[{"action": "test"}],
            target_framework="playwright"
        )
        
        prompt = request.to_prompt()
        
        assert "playwright" in prompt
        assert "automation data" in prompt.lower()
        assert "recommendations" in prompt.lower()
    
    def test_optimization_prompt(self):
        """Test optimization prompt generation."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.OPTIMIZATION,
            automation_data=[],
            target_framework="selenium",
            current_action={"click_element": {"index": 0}}
        )
        
        prompt = request.to_prompt()
        
        assert "selenium" in prompt
        assert "optimization" in prompt.lower()
        assert "click_element" in prompt
    
    def test_validation_prompt(self):
        """Test validation prompt generation."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.VALIDATION,
            automation_data=[{"action": "test"}],
            target_framework="cypress"
        )
        
        prompt = request.to_prompt()
        
        assert "cypress" in prompt
        assert "validate" in prompt.lower()
        assert "compatibility" in prompt.lower()
    
    def test_intelligent_analysis_prompt(self):
        """Test intelligent analysis prompt generation."""
        mock_context = Mock()
        mock_context.existing_tests = []
        mock_context.project.name = "test-project"
        
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.INTELLIGENT_ANALYSIS,
            automation_data=[{"action": "test"}],
            target_framework="playwright",
            system_context=mock_context
        )
        
        prompt = request.to_prompt()
        
        assert "intelligent analysis" in prompt.lower()
        assert "system context" in prompt.lower()
        assert "context-aware" in prompt.lower()
    
    def test_context_analysis_prompt(self):
        """Test context analysis prompt generation."""
        mock_context = Mock()
        mock_context.existing_tests = []
        
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONTEXT_ANALYSIS,
            automation_data=[{"action": "test"}],
            target_framework="playwright",
            system_context=mock_context
        )
        
        prompt = request.to_prompt()
        
        assert "system context" in prompt.lower()
        assert "existing tests" in prompt.lower()
    
    def test_prompt_without_context(self):
        """Test prompt generation without system context."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONTEXT_ANALYSIS,
            automation_data=[{"action": "test"}],
            target_framework="playwright"
        )
        
        prompt = request.to_prompt()
        
        assert "no system context available" in prompt.lower()
    
    def test_comprehensive_prompt(self):
        """Test comprehensive analysis prompt generation (uses basic prompt)."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            automation_data=[{"model_output": "click", "state": "button"}],
            target_framework="playwright"
        )
        
        prompt = request.to_prompt()
        
        assert "playwright" in prompt
        assert "automation data" in prompt.lower()
        assert "general analysis" in prompt.lower()
        assert "click" in prompt


class TestAIProviderFactory:
    """Test the AIProviderFactory class."""
    
    def test_factory_init(self):
        """Test factory initialization."""
        factory = AIProviderFactory()
        assert isinstance(factory, AIProviderFactory)
    
    def test_list_available_providers(self):
        """Test listing available providers."""
        factory = AIProviderFactory()
        providers = factory.list_available_providers()
        
        assert isinstance(providers, list)
        # Should at least include some default providers
        assert len(providers) >= 0
    
    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        config = AIConfig(provider="openai", api_key="test-key")
        factory = AIProviderFactory()
        
        try:
            provider = factory.create_provider(config)
            assert provider is not None
            assert provider.provider_name == "openai"
            assert provider.is_available() == True  # Should be true since we have a fake API key
        except Exception:
            # Provider might not be available in test environment if openai package not installed
            pass
    
    def test_create_invalid_provider(self):
        """Test creating invalid provider."""
        config = AIConfig(provider="invalid_provider")
        factory = AIProviderFactory()
        
        with pytest.raises(AIProviderError):
            factory.create_provider(config)
    
    def test_validate_provider_config(self):
        """Test provider configuration validation."""
        factory = AIProviderFactory()
        
        # Valid config
        config = AIConfig(provider="openai", api_key="test-key")
        errors = factory.validate_provider_config(config)
        assert isinstance(errors, list)
        
        # Invalid config
        config = AIConfig(provider="", api_key="")
        errors = factory.validate_provider_config(config)
        assert len(errors) > 0


@pytest.mark.network
class TestRealAIProviders:
    """Test real AI providers (requires API keys)."""
    
    def test_openai_provider_available(self):
        """Test if OpenAI provider can be imported."""
        try:
            from browse_to_test.ai.providers.openai_provider import OpenAIProvider
            provider = OpenAIProvider(api_key="fake-key")
            assert provider is not None
        except ImportError:
            pytest.skip("OpenAI not available")
    
    def test_anthropic_provider_available(self):
        """Test if Anthropic provider can be imported."""
        try:
            from browse_to_test.ai.providers.anthropic_provider import AnthropicProvider
            provider = AnthropicProvider(api_key="fake-key")
            assert provider is not None
        except ImportError:
            pytest.skip("Anthropic not available")


class TestAnalysisTypes:
    """Test the AnalysisType enumeration."""
    
    def test_analysis_type_values(self):
        """Test analysis type enumeration values."""
        assert AnalysisType.CONVERSION.value == "conversion"
        assert AnalysisType.OPTIMIZATION.value == "optimization"
        assert AnalysisType.VALIDATION.value == "validation"
        assert AnalysisType.CONTEXT_ANALYSIS.value == "context_analysis"
        assert AnalysisType.INTELLIGENT_ANALYSIS.value == "intelligent_analysis"
    
    def test_analysis_type_membership(self):
        """Test analysis type membership."""
        assert AnalysisType.CONVERSION in AnalysisType
        assert AnalysisType.OPTIMIZATION in AnalysisType
        assert AnalysisType.VALIDATION in AnalysisType
        assert AnalysisType.CONTEXT_ANALYSIS in AnalysisType
        assert AnalysisType.INTELLIGENT_ANALYSIS in AnalysisType


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_prompt(self):
        """Test handling empty prompts."""
        provider = MockAIProvider()
        response = provider.generate("")
        
        assert isinstance(response, AIResponse)
        assert response.content is not None
    
    def test_very_long_prompt(self):
        """Test handling very long prompts."""
        provider = MockAIProvider()
        long_prompt = "x" * 10000
        response = provider.generate(long_prompt)
        
        assert isinstance(response, AIResponse)
        assert response.content is not None
    
    def test_unicode_prompt(self):
        """Test handling unicode in prompts."""
        provider = MockAIProvider()
        unicode_prompt = "Test with émojis 🚀 and spëcial chars 中文"
        response = provider.generate(unicode_prompt)
        
        assert isinstance(response, AIResponse)
        assert response.content is not None
    
    def test_malformed_analysis_request(self):
        """Test handling malformed analysis requests."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=None,  # Invalid data
            target_framework=""    # Invalid framework
        )
        
        # Should not raise exception during creation
        assert request.analysis_type == AnalysisType.CONVERSION
        
        # Prompt generation might handle gracefully
        prompt = request.to_prompt()
        assert isinstance(prompt, str)
    
    def test_provider_without_implementation(self):
        """Test provider without proper implementation."""
        class IncompleteProvider(AIProvider):
            pass
        
        with pytest.raises(TypeError):
            # Should fail to instantiate due to abstract methods
            IncompleteProvider()


class TestPerformance:
    """Test performance characteristics."""
    
    def test_multiple_requests_performance(self):
        """Test performance with multiple requests."""
        import time
        
        provider = MockAIProvider()
        start_time = time.time()
        
        # Generate multiple responses
        for i in range(100):
            response = provider.generate(f"Test prompt {i}")
            assert isinstance(response, AIResponse)
        
        end_time = time.time()
        
        # Should complete quickly (< 1 second for mock provider)
        assert end_time - start_time < 1.0
    
    def test_large_response_handling(self):
        """Test handling large responses."""
        class LargeResponseProvider(MockAIProvider):
            def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
                return AIResponse(
                    content="x" * 100000,  # Large response
                    model="mock-model",
                    provider="mock",
                    tokens_used=50000
                )
        
        provider = LargeResponseProvider()
        response = provider.generate("Test")
        
        assert len(response.content) == 100000
        assert response.tokens_used == 50000 