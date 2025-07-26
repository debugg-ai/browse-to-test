"""
Tests for the CommentManager class and language-specific comment formatting.

This module tests the centralized comment management system to ensure
proper comment formatting across all supported programming languages.
"""

import pytest
from datetime import datetime
from browse_to_test.core.configuration import CommentManager, CommentStyle


class TestCommentManager:
    """Test cases for the CommentManager class."""
    
    def test_comment_manager_initialization(self):
        """Test CommentManager initialization for all supported languages."""
        supported_languages = ["python", "typescript", "javascript", "csharp", "java"]
        
        for language in supported_languages:
            manager = CommentManager(language)
            assert manager.language == language
            assert isinstance(manager.style, CommentStyle)
    
    def test_unsupported_language_raises_error(self):
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            CommentManager("unsupported_language")
    
    def test_single_line_comments(self):
        """Test single-line comment generation for all languages."""
        test_cases = [
            ("python", "# Test comment"),
            ("typescript", "// Test comment"),
            ("javascript", "// Test comment"),
            ("csharp", "// Test comment"),
            ("java", "// Test comment"),
        ]
        
        for language, expected in test_cases:
            manager = CommentManager(language)
            result = manager.single_line("Test comment")
            assert result == expected
    
    def test_single_line_comments_with_indent(self):
        """Test single-line comment generation with indentation."""
        manager = CommentManager("python")
        result = manager.single_line("Indented comment", "    ")
        assert result == "    # Indented comment"
        
        manager = CommentManager("javascript")
        result = manager.single_line("Indented comment", "    ")
        assert result == "    // Indented comment"
    
    def test_multi_line_comments(self):
        """Test multi-line comment generation for all languages."""
        lines = ["First line", "Second line", ""]
        
        # Python
        manager = CommentManager("python")
        result = manager.multi_line(lines)
        expected = ['"""', '# First line', '# Second line', '# ', '"""']
        assert result == expected
        
        # JavaScript/TypeScript
        manager = CommentManager("javascript")
        result = manager.multi_line(lines)
        expected = ['/*', ' * First line', ' * Second line', ' * ', '*/']
        assert result == expected
    
    def test_doc_string_generation(self):
        """Test documentation string generation for different languages."""
        description = "Test function description"
        params = {"param1": "First parameter", "param2": "Second parameter"}
        returns = "Return value description"
        
        # Python docstring
        manager = CommentManager("python")
        result = manager.doc_string(description, params, returns)
        assert '"""' in result[0]
        assert description in result[1]
        assert "Args:" in result
        assert "Returns:" in result
        
        # JavaScript/TypeScript JSDoc
        manager = CommentManager("javascript")
        result = manager.doc_string(description, params, returns)
        assert "/**" in result[0]
        assert f" * {description}" in result[1]
        assert any("@param" in line for line in result)
        assert any("@returns" in line for line in result)
    
    def test_step_header_generation(self):
        """Test step header comment generation."""
        metadata = {
            "description": "Click login button",
            "action_type": "click",
            "selector": "#login-btn"
        }
        
        # Python
        manager = CommentManager("python")
        result = manager.step_header(1, "Test step", metadata)
        assert any("# Step 1: Test step" in line for line in result)
        assert any("# action_type: click" in line for line in result)
        
        # JavaScript
        manager = CommentManager("javascript")
        result = manager.step_header(1, "Test step", metadata)
        assert any("// Step 1: Test step" in line for line in result)
        assert any("// action_type: click" in line for line in result)
    
    def test_action_comment_generation(self):
        """Test action comment generation with details."""
        additional_info = {"timeout": "5000ms", "retry": "3 times"}
        
        # Python
        manager = CommentManager("python")
        result = manager.action_comment("click", "#button", additional_info)
        assert result.startswith("# Click on '#button'")
        assert "timeout: 5000ms" in result
        
        # TypeScript
        manager = CommentManager("typescript")
        result = manager.action_comment("fill", "#input", {"value": "test@example.com"})
        assert result.startswith("// Fill on '#input'")
        assert "value: test@example.com" in result
    
    def test_error_comment_generation(self):
        """Test error comment generation."""
        manager = CommentManager("python")
        result = manager.error_comment("Element not found", "Selector #missing was not found")
        assert result == "# ERROR: Element not found - Selector #missing was not found"
        
        manager = CommentManager("java")
        result = manager.error_comment("Timeout", "Operation timed out after 30s")
        assert result == "// ERROR: Timeout - Operation timed out after 30s"
    
    def test_section_separator_generation(self):
        """Test section separator generation."""
        # Python
        manager = CommentManager("python")
        result = manager.section_separator("SETUP SECTION", width=40)
        assert len(result) == 3
        assert "#" * 40 in result[0]
        assert "SETUP SECTION" in result[1]
        
        # JavaScript
        manager = CommentManager("javascript")
        result = manager.section_separator("TEST SECTION", width=40)
        assert len(result) == 3
        assert "//" in result[0]
        assert "TEST SECTION" in result[1]
    
    def test_contextual_info_comment(self):
        """Test contextual information comment generation."""
        context = {
            "url": "https://example.com",
            "page_title": "Test Page",
            "element_count": 15,
            "viewport": "1920x1080",
            "browser": "Chrome",
            "user_inputs": ["username", "password"]
        }
        
        manager = CommentManager("python")
        result = manager.contextual_info_comment(context)
        
        assert any("# Target URL: https://example.com" in line for line in result)
        assert any("# Page Title: Test Page" in line for line in result)
        assert any("# Elements Found: 15" in line for line in result)
        assert any("# Viewport: 1920x1080" in line for line in result)
        assert any("# Browser: Chrome" in line for line in result)
        assert any("# User Inputs: 2 fields" in line for line in result)
    
    def test_timestamp_comment(self):
        """Test timestamp comment generation."""
        manager = CommentManager("python")
        result = manager.timestamp_comment()
        assert result.startswith("# Generated at:")
        
        # Verify it contains a reasonable timestamp format
        timestamp_part = result.split("Generated at: ")[1]
        assert len(timestamp_part.split()) == 2  # Date and time parts
        assert "-" in timestamp_part  # Date separators
        assert ":" in timestamp_part  # Time separators
    
    def test_inline_comments(self):
        """Test inline comment generation."""
        manager = CommentManager("python")
        result = manager.inline("Inline explanation")
        assert result == "  # Inline explanation"
        
        manager = CommentManager("csharp")
        result = manager.inline("C# inline comment")
        assert result == "  // C# inline comment"


class TestCommentManagerIntegration:
    """Integration tests for CommentManager with actual code generation."""
    
    def test_comment_manager_with_output_config(self):
        """Test CommentManager integration with OutputConfig."""
        from browse_to_test.core.configuration import OutputConfig
        
        config = OutputConfig(language="typescript", framework="playwright")
        comment_manager = config.comment_manager
        
        assert isinstance(comment_manager, CommentManager)
        assert comment_manager.language == "typescript"
        
        # Test that it generates TypeScript-style comments
        result = comment_manager.single_line("Test comment")
        assert result.startswith("// ")
    
    def test_language_specific_comment_formats(self):
        """Test that each language produces its expected comment format."""
        test_data = [
            ("python", "#", '"""'),
            ("javascript", "//", "/*"),
            ("typescript", "//", "/**"),
            ("csharp", "//", "/// <summary>"),
            ("java", "//", "/**"),
        ]
        
        for language, single_prefix, doc_start in test_data:
            manager = CommentManager(language)
            
            # Test single line format
            single_result = manager.single_line("test")
            assert single_result.startswith(single_prefix)
            
            # Test documentation format
            doc_result = manager.doc_string("test description")
            assert any(doc_start in line for line in doc_result)
    
    def test_comment_consistency_across_generators(self):
        """Test that comment formatting is consistent across different generators."""
        from browse_to_test.output_langs.python.generators.playwright_generator import PlaywrightPythonGenerator
        
        generator = PlaywrightPythonGenerator()
        
        # Verify that the generator can handle CommentManager
        # This is more of an integration test to ensure no import errors
        manager = CommentManager("python")
        result = manager.single_line("Test from generator context")
        assert result == "# Test from generator context"


def test_comment_manager_examples():
    """Test CommentManager with realistic examples."""
    
    # Example: Step generation for different languages
    step_data = {
        "description": "Fill login form with user credentials",
        "action_type": "fill",
        "selector": "#username",
        "value": "testuser@example.com",
        "timeout": 5000
    }
    
    context_data = {
        "url": "https://app.example.com/login",
        "page_title": "Login - Example App",
        "element_count": 12,
        "viewport": "1366x768"
    }
    
    languages = ["python", "javascript", "typescript", "csharp", "java"]
    
    for language in languages:
        manager = CommentManager(language)
        
        # Generate step header
        step_header = manager.step_header(
            step_number=1,
            description=step_data["description"],
            metadata=step_data,
            indent="    "
        )
        
        # Generate context info
        context_info = manager.contextual_info_comment(context_data, "    ")
        
        # Generate action comment
        action_comment = manager.action_comment(
            step_data["action_type"],
            step_data["selector"],
            {"value": step_data["value"], "timeout": f"{step_data['timeout']}ms"},
            "    "
        )
        
        # Verify all comments use the correct prefix for the language
        expected_prefix = "#" if language == "python" else "//"
        
        for line in step_header + context_info + [action_comment]:
            if line.strip():  # Skip empty lines
                assert line.strip().startswith(expected_prefix), f"Language {language} failed: {line}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 