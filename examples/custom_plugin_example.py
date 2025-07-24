#!/usr/bin/env python3
"""
Custom Plugin Example for browse-to-test library.

This example shows how to create custom plugins for new frameworks or languages.
"""

from typing import Any, Dict, List, Optional

# Import the plugin base classes
from browse_to_test.plugins.base import OutputPlugin, GeneratedTestScript, PluginError
from browse_to_test.core.configuration.config import OutputConfig
from browse_to_test.core.processing.input_parser import ParsedAutomationData, ParsedAction, ParsedStep
import browse_to_test as btt


class CypressPlugin(OutputPlugin):
    """
    Custom plugin for generating Cypress test scripts in JavaScript.
    
    This demonstrates how to create a plugin for a different framework
    and programming language.
    """
    
    def __init__(self, config: OutputConfig):
        """Initialize the Cypress plugin."""
        super().__init__(config)
    
    @property
    def plugin_name(self) -> str:
        """Return the plugin name."""
        return "cypress"
    
    @property
    def supported_frameworks(self) -> List[str]:
        """Return supported frameworks."""
        return ["cypress"]
    
    @property
    def supported_languages(self) -> List[str]:
        """Return supported languages."""
        return ["javascript", "typescript"]
    
    def validate_config(self) -> List[str]:
        """Validate the plugin configuration."""
        errors = []
        
        # Check framework and language support
        if not self.supports_framework(self.config.framework):
            errors.append(f"Framework '{self.config.framework}' not supported")
        
        if not self.supports_language(self.config.language):
            errors.append(f"Language '{self.config.language}' not supported")
        
        return errors
    
    def generate_test_script(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> GeneratedTestScript:
        """Generate Cypress test script from parsed data."""
        try:
            # Generate script content
            script_content = self._generate_script_content(parsed_data, analysis_results)
            
            # Format the code
            formatted_content = self._format_code(script_content)
            
            # Add header comment
            final_content = self._add_header_comment(formatted_content)
            
            return GeneratedTestScript(
                content=final_content,
                language=self.config.language,
                framework=self.config.framework,
                metadata={
                    "total_steps": len(parsed_data.steps),
                    "total_actions": parsed_data.total_actions,
                    "plugin_version": "1.0.0",
                    "has_assertions": self.config.include_assertions,
                }
            )
            
        except Exception as e:
            raise PluginError(f"Failed to generate Cypress script: {e}", self.plugin_name) from e
    
    def get_template_variables(self) -> Dict[str, Any]:
        """Get template variables for script generation."""
        framework_config = self.config.framework_config
        
        return {
            "browser": framework_config.get("browser", "chrome"),
            "viewport_width": framework_config.get("viewport_width", 1280),
            "viewport_height": framework_config.get("viewport_height", 720),
            "base_url": framework_config.get("base_url", ""),
            "default_command_timeout": framework_config.get("default_command_timeout", 4000),
            "include_assertions": self.config.include_assertions,
            "include_waits": self.config.include_waits,
            "sensitive_data_keys": self.config.sensitive_data_keys,
        }
    
    def _generate_script_content(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the main script content."""
        script_lines = []
        
        # Add sensitive data configuration
        script_lines.extend(self._generate_sensitive_data_config())
        
        # Add main describe block
        script_lines.extend(self._generate_test_suite(parsed_data, analysis_results))
        
        return "\n".join(script_lines)
    
    def _generate_sensitive_data_config(self) -> List[str]:
        """Generate sensitive data configuration for Cypress."""
        if not self.config.sensitive_data_keys:
            return []
        
        lines = [
            "// Sensitive data configuration",
            "const SENSITIVE_DATA = {",
        ]
        
        for key in self.config.sensitive_data_keys:
            env_var_name = key.upper()
            lines.append(f"  {key}: Cypress.env('{env_var_name}') || 'YOUR_{env_var_name}',")
        
        lines.extend(["};", ""])
        
        # Add helper function
        lines.extend([
            "// Helper function to replace sensitive data",
            "function replaceSensitiveData(text) {",
            "  if (typeof text !== 'string') return text;",
            "  let result = text;",
            "  Object.keys(SENSITIVE_DATA).forEach(key => {",
            "    const placeholder = `<secret>${key}</secret>`;",
            "    result = result.replace(new RegExp(placeholder, 'g'), SENSITIVE_DATA[key]);",
            "  });",
            "  return result;",
            "}",
            "",
        ])
        
        return lines
    
    def _generate_test_suite(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate the main test suite."""
        template_vars = self.get_template_variables()
        
        lines = [
            "describe('Generated Browser Automation Test', () => {",
            "  beforeEach(() => {",
            f"    cy.viewport({template_vars['viewport_width']}, {template_vars['viewport_height']});",
        ]
        
        if template_vars['base_url']:
            lines.append(f"    cy.visit('{template_vars['base_url']}');")
        
        lines.extend([
            "  });",
            "",
            "  it('should complete the automation flow', () => {",
        ])
        
        # Generate test steps
        for step in parsed_data.steps:
            lines.extend(self._generate_step_actions(step))
        
        lines.extend([
            "  });",
            "});",
        ])
        
        return lines
    
    def _generate_step_actions(self, step: ParsedStep) -> List[str]:
        """Generate actions for a single step."""
        lines = [f"    // Step {step.step_index + 1}"]
        
        for action in step.actions:
            lines.extend(self._generate_action_code(action, step.step_index))
        
        lines.append("")
        return lines
    
    def _generate_action_code(self, action: ParsedAction, step_index: int) -> List[str]:
        """Generate code for a single action."""
        if action.action_type == "go_to_url":
            return self._generate_go_to_url(action)
        elif action.action_type == "input_text":
            return self._generate_input_text(action)
        elif action.action_type in ["click_element", "click_element_by_index"]:
            return self._generate_click_element(action)
        elif action.action_type == "scroll_down":
            return self._generate_scroll(action, "down")
        elif action.action_type == "scroll_up":
            return self._generate_scroll(action, "up")
        elif action.action_type == "wait":
            return self._generate_wait(action)
        elif action.action_type == "done":
            return self._generate_done(action)
        else:
            return [f"    // Unsupported action: {action.action_type}"]
    
    def _generate_go_to_url(self, action: ParsedAction) -> List[str]:
        """Generate go_to_url action code."""
        url = action.parameters.get("url", "")
        if not url:
            return ["    // Skipping go_to_url: missing URL"]
        
        return [f"    cy.visit('{url}');"]
    
    def _generate_input_text(self, action: ParsedAction) -> List[str]:
        """Generate input_text action code."""
        text = action.parameters.get("text", "")
        if not action.selector_info or not text:
            return ["    // Skipping input_text: missing selector or text"]
        
        selector = self._get_cypress_selector(action.selector_info)
        clean_text = self._handle_sensitive_data_js(text)
        
        lines = [
            f"    cy.get('{selector}')",
            "      .should('be.visible')",
            "      .clear()",
            f"      .type({clean_text});",
        ]
        
        return lines
    
    def _generate_click_element(self, action: ParsedAction) -> List[str]:
        """Generate click_element action code."""
        if not action.selector_info:
            return ["    // Skipping click: missing selector"]
        
        selector = self._get_cypress_selector(action.selector_info)
        
        lines = [
            f"    cy.get('{selector}')",
            "      .should('be.visible')",
            "      .click();",
        ]
        
        return lines
    
    def _generate_scroll(self, action: ParsedAction, direction: str) -> List[str]:
        """Generate scroll action code."""
        amount = action.parameters.get("amount")
        
        if amount and isinstance(amount, int):
            scroll_amount = amount if direction == "down" else -amount
            return [f"    cy.scrollTo(0, {scroll_amount});"]
        else:
            scroll_position = "bottom" if direction == "down" else "top"
            return [f"    cy.scrollTo('{scroll_position}');"]
    
    def _generate_wait(self, action: ParsedAction) -> List[str]:
        """Generate wait action code."""
        seconds = action.parameters.get("seconds", 3)
        try:
            wait_ms = int(seconds) * 1000
        except (ValueError, TypeError):
            wait_ms = 3000
        
        return [f"    cy.wait({wait_ms});"]
    
    def _generate_done(self, action: ParsedAction) -> List[str]:
        """Generate done action code."""
        success = action.parameters.get("success", True)
        message = action.parameters.get("text", "Test completed")
        
        lines = [
            f"    // Test marked as done",
            f"    cy.log('Success: {success}');",
        ]
        
        if message:
            clean_message = self._handle_sensitive_data_js(str(message))
            lines.append(f"    cy.log({clean_message});")
        
        return lines
    
    def _get_cypress_selector(self, selector_info: Dict[str, Any]) -> str:
        """Get the best selector for Cypress."""
        # Cypress prefers data attributes, then CSS selectors
        if "attributes" in selector_info and isinstance(selector_info["attributes"], dict):
            attrs = selector_info["attributes"]
            
            # Look for data-testid or similar
            for attr_name in ["data-testid", "data-test", "data-cy"]:
                if attr_name in attrs and attrs[attr_name]:
                    return f"[{attr_name}='{attrs[attr_name]}']"
            
            # Look for id
            if "id" in attrs and attrs["id"]:
                return f"#{attrs['id']}"
        
        # Fall back to CSS selector
        if "css_selector" in selector_info and selector_info["css_selector"]:
            return selector_info["css_selector"]
        
        # Last resort: convert XPath to CSS (simplified)
        if "xpath" in selector_info and selector_info["xpath"]:
            xpath = selector_info["xpath"]
            if xpath.startswith("xpath="):
                xpath = xpath[6:]
            # Very basic XPath to CSS conversion for common cases
            if xpath == "//body":
                return "body"
            # Add more conversions as needed
        
        return "body"  # Fallback
    
    def _handle_sensitive_data_js(self, text: str) -> str:
        """Handle sensitive data for JavaScript output."""
        if not self.config.mask_sensitive_data:
            return f"'{text}'"
        
        # For JavaScript, we'll use template literals
        import re
        pattern = r'<secret>([^<]+)</secret>'
        
        def replace_secret(match):
            key = match.group(1)
            if key in self.config.sensitive_data_keys:
                return "${SENSITIVE_DATA." + key + "}"
            return match.group(0)
        
        processed_text = re.sub(pattern, replace_secret, text)
        
        # If we have replacements, use template literal, otherwise regular string
        if "${" in processed_text:
            return f"`{processed_text}`"
        else:
            return f"'{processed_text}'"
    
    def _add_header_comment(self, content: str) -> str:
        """Add header comment for JavaScript."""
        if not self.config.add_comments:
            return content
        
        header_lines = [
            "/**",
            " * Generated Cypress test script using browse-to-test",
            f" * Framework: {self.config.framework}",
            f" * Language: {self.config.language}",
            " * This script was automatically generated from browser automation data",
            " */",
            "",
        ]
        
        return '\n'.join(header_lines) + content


def demonstrate_custom_plugin():
    """Demonstrate using the custom Cypress plugin."""
    print("=== Custom Plugin Demo: Cypress ===\n")
    
    # Create sample automation data
    automation_data = [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://example.com/login"
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
                            "index": 0,
                            "text": "<secret>email</secret>"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "css_selector": "input[type='email']",
                        "xpath": "//input[@type='email']",
                        "attributes": {
                            "type": "email",
                            "name": "email",
                            "data-testid": "email-input"
                        }
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
                        "css_selector": "button[type='submit']",
                        "xpath": "//button[@type='submit']",
                        "attributes": {
                            "type": "submit",
                            "class": "btn-primary",
                            "data-testid": "login-button"
                        }
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "text": "Login test completed",
                            "success": True
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        }
    ]
    
    # Method 1: Register the plugin manually
    print("--- Method 1: Manual Plugin Registration ---")
    
    # Create configuration for Cypress
    config = btt.Config(
        output=btt.OutputConfig(
            framework="cypress",
            language="javascript",
            include_assertions=True,
            sensitive_data_keys=["email", "password"],
            add_comments=True,
            framework_config={
                "browser": "chrome",
                "viewport_width": 1280,
                "viewport_height": 720,
                "default_command_timeout": 5000,
            }
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=False,  # Disable for demo
        )
    )
    
    # Create orchestrator and register our custom plugin
    converter = btt.E2eTestConverter(config)
    orchestrator.plugin_registry.register_plugin("cypress", CypressPlugin)
    
    print("✓ Registered custom Cypress plugin")
    
    # Generate the test script
    try:
        cypress_script = converter.convert(automation_data)
        
        # Save the script
        output_file = "generated_cypress_test.spec.js"
        with open(output_file, 'w') as f:
            f.write(cypress_script)
        
        print(f"✓ Generated Cypress test: {output_file}")
        print(f"  Script length: {len(cypress_script.splitlines())} lines")
        
        # Show a preview
        print("\n--- Script Preview ---")
        lines = cypress_script.splitlines()
        for i, line in enumerate(lines[:15]):  # Show first 15 lines
            print(f"{i+1:2d}: {line}")
        if len(lines) > 15:
            print(f"... ({len(lines) - 15} more lines)")
        
    except Exception as e:
        print(f"✗ Failed to generate Cypress script: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_plugin_info():
    """Demonstrate getting information about available plugins."""
    print("\n=== Plugin Information ===\n")
    
    # Create a registry and register our custom plugin
    registry = btt.PluginRegistry()
    registry.register_plugin("cypress", CypressPlugin)
    
    # List available plugins
    available_plugins = registry.list_available_plugins()
    print(f"Available plugins: {', '.join(available_plugins)}")
    
    # Get detailed information about each plugin
    for plugin_name in available_plugins:
        try:
            info = registry.get_plugin_info(plugin_name)
            print(f"\n{plugin_name.upper()} Plugin:")
            print(f"  Name: {info['name']}")
            print(f"  Supported frameworks: {', '.join(info['supported_frameworks'])}")
            print(f"  Supported languages: {', '.join(info['supported_languages'])}")
            print(f"  Class: {info['class']}")
        except Exception as e:
            print(f"  Error getting info for {plugin_name}: {e}")
    
    # Test framework/language combinations
    print(f"\nFramework/Language Support:")
    test_combinations = [
        ("cypress", "javascript"),
        ("playwright", "python"),
        ("selenium", "python"),
        ("cypress", "python"),  # Should be False
    ]
    
    for framework, language in test_combinations:
        supported = registry.validate_framework_language_combination(framework, language)
        status = "✓" if supported else "✗"
        print(f"  {status} {framework} + {language}")


def main():
    """Run the custom plugin example."""
    print("Browse-to-Test Custom Plugin Example")
    print("=" * 40)
    
    try:
        demonstrate_custom_plugin()
        demonstrate_plugin_info()
        
        print("\n" + "=" * 40)
        print("Custom plugin example completed!")
        print("\nTo use your custom Cypress test:")
        print("1. Install Cypress: npm install cypress")
        print("2. Run: npx cypress run --spec generated_cypress_test.spec.js")
        
    except Exception as e:
        print(f"\nExample execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 