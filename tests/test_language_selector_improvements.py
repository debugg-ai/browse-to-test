#!/usr/bin/env python3
"""
Tests for language selector improvements.

These tests verify the enhanced language selector functionality including:
- Language auto-detection from filenames
- Better validation and error messages  
- Framework optimization suggestions
- Configuration validation with alternatives
"""

import pytest
import sys
import os

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import browse_to_test as btt
from browse_to_test.core.config import Config, ConfigBuilder


class TestLanguageDetection:
    """Test language auto-detection from filenames."""
    
    def test_detect_python_from_extension(self):
        """Test Python detection from .py files."""
        assert Config.detect_language_from_filename("test.py") == "python"
        assert Config.detect_language_from_filename("Test.PY") == "python"  # Case insensitive
        assert Config.detect_language_from_filename("my_test_file.py") == "python"
    
    def test_detect_typescript_from_extension(self):
        """Test TypeScript detection from .ts files."""
        assert Config.detect_language_from_filename("test.ts") == "typescript"
        assert Config.detect_language_from_filename("component.TS") == "typescript"
        assert Config.detect_language_from_filename("e2e.spec.ts") == "typescript"
    
    def test_detect_javascript_from_extension(self):
        """Test JavaScript detection from .js files."""
        assert Config.detect_language_from_filename("test.js") == "javascript"
        assert Config.detect_language_from_filename("app.JS") == "javascript"
        assert Config.detect_language_from_filename("test.spec.js") == "javascript"
    
    def test_detect_java_from_extension(self):
        """Test Java detection from .java files."""
        assert Config.detect_language_from_filename("Test.java") == "java"
        assert Config.detect_language_from_filename("MyClass.JAVA") == "java"
    
    def test_detect_csharp_from_extension(self):
        """Test C# detection from .cs files."""
        assert Config.detect_language_from_filename("Test.cs") == "csharp"
        assert Config.detect_language_from_filename("Program.CS") == "csharp"
    
    def test_fallback_to_python_for_unknown_extension(self):
        """Test fallback to Python for unknown extensions."""
        assert Config.detect_language_from_filename("test.txt") == "python"
        assert Config.detect_language_from_filename("test.xyz") == "python"
        assert Config.detect_language_from_filename("test") == "python"
        assert Config.detect_language_from_filename("") == "python"


class TestFrameworkOptimization:
    """Test framework optimization for languages."""
    
    def test_optimal_framework_for_python(self):
        """Test optimal framework selection for Python."""
        optimal = Config.get_optimal_framework_for_language("python")
        # Should prefer Playwright if available
        assert optimal in ["playwright", "selenium"]  # Both are supported for Python
    
    def test_optimal_framework_for_typescript(self):
        """Test optimal framework selection for TypeScript."""
        optimal = Config.get_optimal_framework_for_language("typescript")
        assert optimal == "playwright"  # TypeScript primarily supports Playwright
    
    def test_optimal_framework_for_javascript(self):
        """Test optimal framework selection for JavaScript."""
        optimal = Config.get_optimal_framework_for_language("javascript")
        assert optimal == "playwright"  # JavaScript primarily supports Playwright
    
    def test_fallback_for_unknown_language(self):
        """Test fallback framework for unknown languages."""
        optimal = Config.get_optimal_framework_for_language("unknown_lang")
        assert optimal == "playwright"  # Safe default


class TestConfigBuilderEnhancements:
    """Test enhanced ConfigBuilder functionality."""
    
    def test_auto_detect_language_method(self):
        """Test ConfigBuilder auto-detection method."""
        config = ConfigBuilder() \
            .auto_detect_language("test.ts") \
            .framework("playwright") \
            .build()
        
        assert config.language == "typescript"
        assert config.framework == "playwright"
    
    def test_optimize_for_language_method(self):
        """Test ConfigBuilder optimization method."""
        config = ConfigBuilder() \
            .optimize_for_language("python") \
            .build()
        
        assert config.language == "python"
        assert config.framework in ["playwright", "selenium"]  # Should pick optimal
    
    def test_chaining_with_new_methods(self):
        """Test method chaining with new methods."""
        config = ConfigBuilder() \
            .optimize_for_language("typescript") \
            .ai_provider("openai") \
            .include_assertions(True) \
            .build()
        
        assert config.language == "typescript"
        assert config.framework == "playwright"
        assert config.ai_provider == "openai"
        assert config.include_assertions is True


class TestConfigValidation:
    """Test enhanced configuration validation."""
    
    def test_validate_valid_combination(self):
        """Test validation of valid language-framework combinations."""
        config = Config(language="python", framework="playwright")
        is_valid, message, suggestions = config.validate_and_suggest_alternatives()
        
        assert is_valid is True
        assert "valid" in message.lower()
        assert suggestions == {}
    
    def test_validate_invalid_language(self):
        """Test validation of invalid language."""
        # This should raise ValueError during construction due to validation
        with pytest.raises(ValueError) as excinfo:
            Config(language="invalid_lang", framework="playwright")
        
        error_message = str(excinfo.value)
        assert "invalid_lang" in error_message
        assert "Available:" in error_message or "try:" in error_message
    
    def test_validate_invalid_framework_for_language(self):
        """Test validation of invalid framework for valid language."""
        # This should raise ValueError during construction due to validation
        with pytest.raises(ValueError) as excinfo:
            Config(language="python", framework="invalid_framework")
        
        error_message = str(excinfo.value)
        assert "invalid_framework" in error_message
        assert "python" in error_message
        assert "Supported frameworks" in error_message


class TestEnhancedConvertFunction:
    """Test enhanced convert function with new features."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample automation data for testing."""
        return [{
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            }
        }]
    
    def test_convert_with_auto_detection_python(self, sample_data):
        """Test convert function with Python auto-detection."""
        # Skip AI by providing empty API key
        os.environ["OPENAI_API_KEY"] = ""
        
        script = btt.convert(
            sample_data,
            output_file="test.py",
            enable_ai_analysis=False,
            enable_context_collection=False
        )
        
        assert script
        assert len(script) > 0
        # Should contain Python-specific syntax
        assert any(indicator in script for indicator in ["def ", "import ", "#!/usr/bin/env python"])
    
    def test_convert_with_auto_detection_typescript(self, sample_data):
        """Test convert function with TypeScript auto-detection."""
        os.environ["OPENAI_API_KEY"] = ""
        
        script = btt.convert(
            sample_data,
            output_file="test.ts",
            enable_ai_analysis=False,
            enable_context_collection=False
        )
        
        assert script
        assert len(script) > 0
        # Should contain TypeScript-specific patterns
        assert any(indicator in script for indicator in ["function", "const ", "async "])
    
    def test_convert_with_auto_detection_javascript(self, sample_data):
        """Test convert function with JavaScript auto-detection."""
        os.environ["OPENAI_API_KEY"] = ""
        
        script = btt.convert(
            sample_data,
            output_file="test.js",
            enable_ai_analysis=False,
            enable_context_collection=False
        )
        
        assert script
        assert len(script) > 0
        # Should contain JavaScript-specific patterns
        assert any(indicator in script for indicator in ["function", "const ", "require("])
    
    def test_convert_explicit_language_overrides_detection(self, sample_data):
        """Test that explicit language parameter overrides auto-detection."""
        os.environ["OPENAI_API_KEY"] = ""
        
        # Explicitly specify Python even though file extension is .ts
        script = btt.convert(
            sample_data,
            language="python",
            output_file="test.ts",  # TypeScript extension
            enable_ai_analysis=False,
            enable_context_collection=False
        )
        
        assert script
        # Should still be Python since explicitly specified
        assert any(indicator in script for indicator in ["def ", "import ", "#!/usr/bin/env python"])
    
    @pytest.mark.asyncio
    async def test_convert_async_with_auto_detection(self, sample_data):
        """Test async convert function with auto-detection."""
        os.environ["OPENAI_API_KEY"] = ""
        
        script = await btt.convert_async(
            sample_data,
            output_file="async_test.ts",
            enable_ai_analysis=False,
            enable_context_collection=False
        )
        
        assert script
        assert len(script) > 0


class TestErrorHandlingImprovements:
    """Test improved error handling and messaging."""
    
    def test_helpful_error_for_invalid_language(self):
        """Test that invalid language produces helpful error message."""
        with pytest.raises(ValueError) as excinfo:
            config = Config(language="invalid_lang", framework="playwright")
            config._validate()
        
        error_message = str(excinfo.value)
        assert "invalid_lang" in error_message
        assert "Available:" in error_message or "Supported" in error_message
        # Should include list of supported languages
        assert "python" in error_message
    
    def test_helpful_error_with_suggestions(self):
        """Test that errors include helpful suggestions."""
        try:
            config = Config(language="invalid_lang", framework="playwright")
            config._validate()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            error_message = str(e)
            # Should contain suggestions or alternatives
            assert any(keyword in error_message for keyword in [
                "Available:", "Supported", "try:", "alternative"
            ])


class TestBackwardCompatibility:
    """Test that improvements maintain backward compatibility."""
    
    def test_old_api_still_works(self):
        """Test that existing API calls continue to work."""
        os.environ["OPENAI_API_KEY"] = ""
        
        sample_data = [{
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            }
        }]
        
        # Old-style call should still work
        script = btt.convert(
            sample_data,
            framework="playwright",
            language="python",
            enable_ai_analysis=False
        )
        
        assert script
        assert len(script) > 0
    
    def test_config_builder_backward_compatibility(self):
        """Test ConfigBuilder backward compatibility."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .language("python") \
            .ai_provider("openai") \
            .build()
        
        assert config.framework == "playwright"
        assert config.language == "python"
        assert config.ai_provider == "openai"


class TestIntegration:
    """Integration tests for the enhanced language selector."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample automation data for testing."""
        return [{
            "model_output": {
                "action": [
                    {"go_to_url": {"url": "https://example.com"}},
                    {"click_element": {"selector": "button#submit"}},
                    {"wait": {"seconds": 2}}
                ]
            }
        }]
    
    def test_full_workflow_with_auto_detection(self, sample_data):
        """Test complete workflow with language auto-detection."""
        os.environ["OPENAI_API_KEY"] = ""
        
        # Test different language outputs
        test_cases = [
            ("output.py", "python"),
            ("output.ts", "typescript"),
            ("output.js", "javascript")
        ]
        
        for output_file, expected_lang in test_cases:
            script = btt.convert(
                sample_data,
                output_file=output_file,
                enable_ai_analysis=False,
                enable_context_collection=False
            )
            
            assert script
            assert len(script) > 100  # Should be substantial
            
            # Language-specific checks
            if expected_lang == "python":
                assert any(indicator in script for indicator in ["def ", "import "])
            elif expected_lang in ["typescript", "javascript"]:
                assert any(indicator in script for indicator in ["function", "const ", "async "])
    
    def test_configuration_validation_workflow(self):
        """Test the configuration validation workflow."""
        # Test valid configuration
        config = ConfigBuilder() \
            .optimize_for_language("python") \
            .ai_provider("openai") \
            .build()
        
        is_valid, message, suggestions = config.validate_and_suggest_alternatives()
        assert is_valid
        
        # Test validation provides helpful info
        assert "python" in message
        assert "playwright" in message or "selenium" in message