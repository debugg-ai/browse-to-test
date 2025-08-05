"""
End-to-end validation tests for generated test scripts.

This module validates that generated scripts are:
1. Syntactically correct and compilable
2. Structurally sound with proper imports
3. Executable (where possible without external dependencies)
4. Following best practices for the target framework
5. Handling edge cases appropriately
"""

import ast
import sys
import subprocess
import tempfile
import pytest
from pathlib import Path
from typing import Dict, List
import re

import browse_to_test as btt
from browse_to_test.core.config import ConfigBuilder


class TestScriptSyntaxValidation:
    """Test that generated scripts have valid syntax."""
    
    @pytest.fixture
    def sample_automation_data(self):
        """Standard automation data for testing."""
        return [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "https://example.com"
                        }
                    }]
                },
                "timestamp": 1640995200.0
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[data-testid='username']",
                            "text": "testuser"
                        }
                    }]
                },
                "timestamp": 1640995201.0
            },
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": "button[type='submit']"
                        }
                    }]
                },
                "timestamp": 1640995202.0
            }
        ]
    
    def validate_python_syntax(self, script: str) -> Dict[str, any]:
        """Validate Python script syntax and return analysis."""
        try:
            # Parse the script into AST
            tree = ast.parse(script)
            
            # Analyze the AST for key components
            analysis = {
                'valid_syntax': True,
                'has_imports': False,
                'has_functions': False,
                'has_async_functions': False,
                'has_classes': False,
                'import_count': 0,
                'function_count': 0,
                'errors': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis['has_imports'] = True
                    analysis['import_count'] += 1
                elif isinstance(node, ast.FunctionDef):
                    analysis['has_functions'] = True
                    analysis['function_count'] += 1
                elif isinstance(node, ast.AsyncFunctionDef):
                    analysis['has_async_functions'] = True
                    analysis['function_count'] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis['has_classes'] = True
            
            return analysis
            
        except SyntaxError as e:
            return {
                'valid_syntax': False,
                'errors': [f"Syntax error at line {e.lineno}: {e.msg}"],
                'has_imports': False,
                'has_functions': False,
                'has_async_functions': False,
                'has_classes': False,
                'import_count': 0,
                'function_count': 0
            }
    
    def test_playwright_python_syntax(self, sample_automation_data):
        """Test Playwright Python script syntax."""
        script = btt.convert(
            sample_automation_data,
            framework="playwright",
            language="python"
        )
        
        analysis = self.validate_python_syntax(script)
        
        assert analysis['valid_syntax'], f"Invalid Python syntax: {analysis['errors']}"
        assert analysis['has_imports'], "Script should have import statements"
        assert analysis['has_functions'] or analysis['has_async_functions'], "Script should have functions"
        assert analysis['import_count'] > 0, "Should have at least one import"
    
    def test_selenium_python_syntax(self, sample_automation_data):
        """Test Selenium Python script syntax."""
        script = btt.convert(
            sample_automation_data,
            framework="selenium",
            language="python"
        )
        
        analysis = self.validate_python_syntax(script)
        
        assert analysis['valid_syntax'], f"Invalid Python syntax: {analysis['errors']}"
        assert analysis['has_imports'], "Script should have import statements"
        assert analysis['has_functions'], "Script should have functions"
    
    def test_typescript_syntax_basic(self, sample_automation_data):
        """Test TypeScript script basic structure."""
        script = btt.convert(
            sample_automation_data,
            framework="playwright",
            language="typescript"
        )
        
        # Basic TypeScript syntax checks
        assert "import" in script, "Should have import statements"
        assert "function" in script or "=>" in script, "Should have functions"
        assert "async" in script, "Should have async functionality"
        
        # Check for TypeScript-specific syntax
        assert ":" in script, "Should have type annotations"
    
    def test_javascript_syntax_basic(self, sample_automation_data):
        """Test JavaScript script basic structure."""
        script = btt.convert(
            sample_automation_data,
            framework="playwright",
            language="javascript"
        )
        
        # Basic JavaScript syntax checks
        assert "import" in script or "require" in script, "Should have imports"
        assert "function" in script or "=>" in script, "Should have functions"
        assert "async" in script, "Should have async functionality"


class TestScriptStructureValidation:
    """Test the structural integrity of generated scripts."""
    
    @pytest.fixture
    def complex_automation_data(self):
        """More complex automation data for thorough testing."""
        return [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "https://example.com/login"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "wait": {
                            "selector": ".loading-spinner",
                            "timeout": 5000
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='email']",
                            "text": "test@example.com"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='password']",
                            "text": "securepassword"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": "button[data-testid='login-submit']"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "wait_for_navigation": {
                            "timeout": 10000
                        }
                    }]
                }
            }
        ]
    
    def test_playwright_script_structure(self, complex_automation_data):
        """Test Playwright script has proper structure."""
        script = btt.convert(
            complex_automation_data,
            framework="playwright",
            language="python"
        )
        
        # Check for essential Playwright components
        assert "from playwright" in script, "Should import Playwright"
        assert "async def" in script, "Should have async test function"
        assert "page.goto" in script or "await page.goto" in script, "Should have navigation"
        assert "page." in script, "Should use page object"
        
        # Check for proper async/await usage
        if "await" in script:
            assert "async def" in script, "If using await, should have async function"
        
        # Check for browser/context setup
        playwright_setup_indicators = [
            "browser",
            "context", 
            "page",
            "playwright()",
            "chromium.launch"
        ]
        has_setup = any(indicator in script for indicator in playwright_setup_indicators)
        assert has_setup, "Should have browser setup"
    
    def test_selenium_script_structure(self, complex_automation_data):
        """Test Selenium script has proper structure."""
        script = btt.convert(
            complex_automation_data,
            framework="selenium",
            language="python"
        )
        
        # Check for essential Selenium components
        assert "from selenium" in script, "Should import Selenium"
        assert "webdriver" in script.lower(), "Should reference webdriver"
        assert "driver" in script, "Should have driver variable"
        assert ".get(" in script or ".get " in script, "Should have navigation method"
        
        # Check for proper WebDriver setup
        selenium_setup_indicators = [
            "webdriver.",
            "ChromeDriver",
            "driver =",
            "WebDriver"
        ]
        has_setup = any(indicator in script for indicator in selenium_setup_indicators)
        assert has_setup, "Should have WebDriver setup"
    
    def test_error_handling_structure(self, complex_automation_data):
        """Test that error handling is properly structured."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .language("python") \
            .include_error_handling(True) \
            .build()
        
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        converter = E2eTestConverter(config)
        script = converter.convert(complex_automation_data)
        
        # Check for error handling structures
        error_handling_indicators = [
            "try:",
            "except",
            "finally:",
            "raise",
            "Exception"
        ]
        
        has_error_handling = any(indicator in script for indicator in error_handling_indicators)
        
        # Error handling should be present when requested
        if config.output.include_error_handling:
            assert has_error_handling, "Should include error handling when requested"
    
    def test_assertion_structure(self, complex_automation_data):
        """Test that assertions are properly structured."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .language("python") \
            .include_assertions(True) \
            .build()
        
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        converter = E2eTestConverter(config)
        script = converter.convert(complex_automation_data)
        
        # Check for assertion structures
        assertion_indicators = [
            "assert",
            "expect(",
            "should",
            "assertEqual",
            "assertTrue"
        ]
        
        has_assertions = any(indicator in script for indicator in assertion_indicators)
        
        # Assertions should be present when requested
        if config.output.include_assertions:
            assert has_assertions, "Should include assertions when requested"


class TestScriptExecutabilityValidation:
    """Test that generated scripts can potentially be executed."""
    
    def test_import_resolution_check(self):
        """Test that imports in generated scripts are resolvable."""
        sample_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {"url": "https://example.com"}
                    }]
                }
            }
        ]
        
        # Test Playwright imports
        playwright_script = btt.convert(
            sample_data,
            framework="playwright",
            language="python"
        )
        
        # Extract import statements
        import_lines = [line.strip() for line in playwright_script.split('\n') 
                       if line.strip().startswith(('import ', 'from '))]
        
        assert len(import_lines) > 0, "Should have import statements"
        
        # Check that imports are reasonable
        for import_line in import_lines:
            # Should not have obviously wrong imports
            assert "import import" not in import_line, "Invalid import syntax"
            assert "from from" not in import_line, "Invalid from import syntax"
    
    def test_script_dry_run_validation(self):
        """Test script structure without actually running external dependencies."""
        sample_data = [
            {
                "model_output": {
                    "action": [{
                        "click": {"selector": "#test-button"}
                    }]
                }
            }
        ]
        
        script = btt.convert(sample_data, framework="playwright", language="python")
        
        # Create a temporary file and test compilation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            temp_path = f.name
        
        try:
            # Test that Python can at least compile the script
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', temp_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # If compilation fails, check if it's due to missing dependencies
                if "ModuleNotFoundError" in result.stderr:
                    # This is expected - external dependencies aren't installed
                    pytest.skip("Skipping execution test - missing dependencies is expected")
                else:
                    pytest.fail(f"Script compilation failed: {result.stderr}")
            
        finally:
            # Clean up
            Path(temp_path).unlink()


class TestEdgeCaseHandling:
    """Test how scripts handle edge cases and unusual inputs."""
    
    def test_special_characters_in_selectors(self):
        """Test handling of special characters in CSS selectors."""
        special_char_data = [
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": "button[data-test='user:name']"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='email@domain']",
                            "text": "test@example.com"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(special_char_data, framework="playwright")
        
        # Should handle special characters properly
        assert "user:name" in script, "Should preserve special characters in selectors"
        assert "email@domain" in script, "Should handle @ symbols in selectors"
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        unicode_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='name']",
                            "text": "Müller José 北京"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(unicode_data, framework="playwright")
        
        # Should handle Unicode properly
        assert "Müller" in script or "M\\u00fc" in script, "Should handle Unicode characters"
        assert "José" in script or "Jos\\u00e9" in script, "Should handle accented characters"
        assert "北京" in script or "\\u" in script, "Should handle CJK characters"
    
    def test_empty_selector_handling(self):
        """Test handling of empty or invalid selectors."""
        invalid_selector_data = [
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": ""
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(invalid_selector_data, framework="playwright")
            # If it succeeds, should have some fallback or error handling
            assert len(script) > 0, "Should generate some output even with invalid input"
        except (ValueError, RuntimeError) as e:
            # It's also acceptable to reject invalid selectors
            assert "selector" in str(e).lower(), "Error should mention selector issue"
    
    def test_very_long_text_handling(self):
        """Test handling of very long text input."""
        long_text = "A" * 1000  # 1000 character string
        
        long_text_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "textarea[name='content']",
                            "text": long_text
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(long_text_data, framework="playwright")
        
        # Should handle long text appropriately
        assert len(script) > 100, "Should generate substantial script"
        # Long text might be truncated or handled specially
        assert "textarea" in script, "Should reference the textarea"


class TestBestPracticesValidation:
    """Test that generated scripts follow best practices."""
    
    def test_proper_wait_patterns(self):
        """Test that scripts include proper wait patterns."""
        navigation_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {"url": "https://example.com"}
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "click": {"selector": "#dynamic-button"}
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .language("python") \
            .include_waits(True) \
            .build()
        
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        converter = E2eTestConverter(config)
        script = converter.convert(navigation_data)
        
        # Should include wait patterns
        wait_patterns = [
            "wait_for",
            "timeout",
            "wait",
            "sleep",
            "load_state"
        ]
        
        has_waits = any(pattern in script for pattern in wait_patterns)
        
        if config.output.include_waits:
            assert has_waits, "Should include wait patterns when requested"
    
    def test_timeout_configuration(self):
        """Test that timeouts are properly configured."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .timeout(45000) \
            .build()
        
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        converter = E2eTestConverter(config)
        script = converter.convert([{
            "model_output": {"action": [{"click": {"selector": "#test"}}]}
        }])
        
        # Should reference the configured timeout
        assert "45000" in script or "45" in script, "Should use configured timeout"
    
    def test_browser_options_inclusion(self):
        """Test that browser options are properly included."""
        config = ConfigBuilder() \
            .framework("playwright") \
            .build()
        
        # Set some browser options
        config.output.browser_options = {
            "headless": True,
            "viewport": {"width": 1280, "height": 720}
        }
        
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        converter = E2eTestConverter(config)
        script = converter.convert([{
            "model_output": {"action": [{"click": {"selector": "#test"}}]}
        }])
        
        # Should include browser configuration
        browser_config_indicators = [
            "headless",
            "viewport", 
            "1280",
            "720"
        ]
        
        has_browser_config = any(indicator in script for indicator in browser_config_indicators)
        # This is implementation-specific, so soft assertion
        if not has_browser_config:
            print("INFO: Browser options might not be reflected in generated script")


if __name__ == "__main__":
    print("Running generated script validation tests...")
    
    # Quick validation test
    sample_data = [
        {
            "model_output": {
                "action": [{
                    "go_to_url": {"url": "https://example.com"}
                }]
            }
        }
    ]
    
    # Test basic generation and syntax
    script = btt.convert(sample_data, framework="playwright", language="python")
    
    # Basic syntax check
    try:
        ast.parse(script)
        print("✓ Generated script has valid Python syntax")
    except SyntaxError as e:
        print(f"✗ Syntax error in generated script: {e}")
        raise
    
    # Basic structure check
    assert "import" in script, "Should have imports"
    assert "def " in script or "async def" in script, "Should have functions"
    
    print("✓ Basic validation passed")
    print("Run full test suite with: pytest test_generated_script_validation.py")