"""
Selenium plugin for generating Python test scripts.

Demonstrates multi-framework support by providing Selenium as an alternative to Playwright.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import OutputPlugin, GeneratedTestScript, PluginError
from ..core.configuration.config import OutputConfig
from ..core.processing.input_parser import ParsedAutomationData, ParsedAction, ParsedStep


logger = logging.getLogger(__name__)


class SeleniumPlugin(OutputPlugin):
    """Plugin for generating Selenium test scripts in Python."""
    
    def __init__(self, config: OutputConfig):
        """Initialize the Selenium plugin."""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    @property
    def plugin_name(self) -> str:
        """Return the plugin name."""
        return "selenium"
    
    @property
    def supported_frameworks(self) -> List[str]:
        """Return supported frameworks."""
        return ["selenium", "webdriver"]
    
    @property
    def supported_languages(self) -> List[str]:
        """Return supported languages."""
        return ["python", "typescript", "javascript", "csharp", "java"]
    
    def validate_config(self) -> List[str]:
        """Validate the plugin configuration."""
        errors = []
        
        # Check framework and language support
        if not self.supports_framework(self.config.framework):
            errors.append(f"Framework '{self.config.framework}' not supported")
        
        if not self.supports_language(self.config.language):
            errors.append(f"Language '{self.config.language}' not supported")
        
        # Validate framework-specific settings
        framework_config = self.config.framework_config
        
        # Check browser type if specified
        if "browser_type" in framework_config:
            valid_browsers = ["chrome", "firefox", "edge", "safari"]
            if framework_config["browser_type"] not in valid_browsers:
                errors.append(f"Invalid browser type. Valid options: {', '.join(valid_browsers)}")
        
        return errors
    
    def generate_test_script(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> GeneratedTestScript:
        """Generate Selenium test script from parsed data."""
        try:
            self.logger.debug(f"Generating Selenium script for {len(parsed_data.steps)} steps")
            
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
                    "has_error_handling": self.config.include_error_handling,
                }
            )
            
        except Exception as e:
            raise PluginError(f"Failed to generate Selenium script: {e}", self.plugin_name) from e
    
    def get_template_variables(self) -> Dict[str, Any]:
        """Get template variables for script generation."""
        framework_config = self.config.framework_config
        
        return {
            "browser_type": framework_config.get("browser_type", "chrome"),
            "headless": framework_config.get("headless", False),
            "window_width": framework_config.get("window_width", 1280),
            "window_height": framework_config.get("window_height", 720),
            "implicit_wait": framework_config.get("implicit_wait", 10),
            "page_load_timeout": framework_config.get("page_load_timeout", 30),
            "include_assertions": self.config.include_assertions,
            "include_waits": self.config.include_waits,
            "include_error_handling": self.config.include_error_handling,
            "include_logging": self.config.include_logging,
            "sensitive_data_keys": self.config.sensitive_data_keys,
        }
    
    def _generate_script_content(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the main script content."""
        script_lines = []
        
        # Add imports
        script_lines.extend(self._generate_imports())
        
        # Add sensitive data configuration
        script_lines.extend(self._generate_sensitive_data_config())
        
        # Add helper functions
        script_lines.extend(self._generate_helper_functions())
        
        # Add main test class
        script_lines.extend(self._generate_test_class(parsed_data, analysis_results))
        
        # Add entry point
        script_lines.extend(self._generate_entry_point())
        
        return "\n".join(script_lines)
    
    def _generate_imports(self) -> List[str]:
        """Generate import statements."""
        imports = [
            "import os",
            "import sys",
            "import time",
            "import unittest",
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.common.keys import Keys",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "from selenium.webdriver.chrome.service import Service as ChromeService",
            "from selenium.webdriver.firefox.service import Service as FirefoxService",
            "from selenium.webdriver.edge.service import Service as EdgeService",
            "from selenium.common.exceptions import TimeoutException, NoSuchElementException",
            "from dotenv import load_dotenv",
            "",
            "# Load environment variables",
            "load_dotenv(override=True)",
            "",
        ]
        
        if self.config.include_error_handling:
            imports.extend([
                "import traceback",
                "from datetime import datetime",
                "",
            ])
        
        return imports
    
    def _generate_sensitive_data_config(self) -> List[str]:
        """Generate sensitive data configuration."""
        if not self.config.sensitive_data_keys:
            return ["SENSITIVE_DATA = {}", ""]
        
        lines = ["# Sensitive data placeholders mapped to environment variables"]
        lines.append("SENSITIVE_DATA = {")
        
        for key in self.config.sensitive_data_keys:
            env_var_name = key.upper()
            default_value_placeholder = f"YOUR_{env_var_name}"
            lines.append(
                f'    "{key}": os.getenv("{env_var_name}", "{default_value_placeholder}"),'
            )
        
        lines.extend(["}", ""])
        return lines
    
    def _generate_helper_functions(self) -> List[str]:
        """Generate helper functions."""
        helpers = [
            "# Helper function for replacing sensitive data",
            "def replace_sensitive_data(text: str, sensitive_map: dict) -> str:",
            "    \"\"\"Replace sensitive data placeholders in text.\"\"\"",
            "    if not isinstance(text, str):",
            "        return text",
            "    for placeholder, value in sensitive_map.items():",
            "        replacement_value = str(value) if value is not None else ''",
            "        text = text.replace(f'<secret>{placeholder}</secret>', replacement_value)",
            "    return text",
            "",
        ]
        
        return helpers
    
    def _generate_test_class(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate the main test class."""
        template_vars = self.get_template_variables()
        
        lines = [
            "class BrowseToTestSelenium(unittest.TestCase):",
            "    \"\"\"Generated Selenium test class.\"\"\"",
            "",
            "    def setUp(self):",
            "        \"\"\"Set up the test browser.\"\"\"",
            f"        self.setup_driver('{template_vars['browser_type']}')",
            "",
            "    def tearDown(self):",
            "        \"\"\"Clean up after test.\"\"\"",
            "        if hasattr(self, 'driver'):",
            "            self.driver.quit()",
            "",
            "    def setup_driver(self, browser_type: str):",
            "        \"\"\"Set up the WebDriver.\"\"\"",
            "        if browser_type.lower() == 'chrome':",
            "            options = webdriver.ChromeOptions()",
        ]
        
        if template_vars['headless']:
            lines.append("            options.add_argument('--headless')")
        
        lines.extend([
            "            options.add_argument('--no-sandbox')",
            "            options.add_argument('--disable-dev-shm-usage')",
            f"            options.add_argument('--window-size={template_vars['window_width']},{template_vars['window_height']}')",
            "            self.driver = webdriver.Chrome(options=options)",
            "",
            "        elif browser_type.lower() == 'firefox':",
            "            options = webdriver.FirefoxOptions()",
        ])
        
        if template_vars['headless']:
            lines.append("            options.add_argument('--headless')")
        
        lines.extend([
            "            self.driver = webdriver.Firefox(options=options)",
            "",
            "        else:",
            "            raise ValueError(f'Unsupported browser: {browser_type}')",
            "",
            f"        self.driver.implicitly_wait({template_vars['implicit_wait']})",
            f"        self.driver.set_page_load_timeout({template_vars['page_load_timeout']})",
            f"        self.wait = WebDriverWait(self.driver, {template_vars['implicit_wait']})",
            "",
        ])
        
        # Generate test method
        lines.extend(self._generate_test_method(parsed_data, analysis_results))
        
        return lines
    
    def _generate_test_method(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate the main test method."""
        lines = [
            "    def test_automation_flow(self):",
            "        \"\"\"Main test method containing all automation steps.\"\"\"",
        ]
        
        if self.config.include_logging:
            lines.append("        print('Starting Selenium test execution')")
        
        if self.config.include_error_handling:
            lines.extend([
                "        try:",
                "            test_start_time = time.time()",
            ])
            indent = "            "
        else:
            indent = "        "
        
        # Generate actions for each step
        for step in parsed_data.steps:
            lines.extend(self._generate_step_actions(step, analysis_results, indent))
        
        if self.config.include_error_handling:
            lines.extend([
                "            elapsed_time = time.time() - test_start_time",
                "            print(f'Test completed successfully in {elapsed_time:.2f} seconds')",
                "",
                "        except Exception as e:",
                "            print(f'Test failed: {e}', file=sys.stderr)",
                "            if hasattr(self, 'driver'):",
                "                # Take screenshot on failure",
                "                try:",
                "                    screenshot_path = f'test_failure_{int(time.time())}.png'",
                "                    self.driver.save_screenshot(screenshot_path)",
                "                    print(f'Screenshot saved: {screenshot_path}')",
                "                except Exception:",
                "                    pass",
                "            raise",
            ])
        
        return lines
    
    def _generate_step_actions(
        self, 
        step: ParsedStep,
        analysis_results: Optional[Dict[str, Any]] = None,
        indent: str = "        "
    ) -> List[str]:
        """Generate actions for a single step."""
        lines = [f"{indent}# Step {step.step_index + 1}"]
        
        if self.config.add_comments and step.metadata:
            lines.append(f"{indent}# Step metadata: {step.metadata}")
        
        for action in step.actions:
            lines.extend(self._generate_action_code(action, step.step_index, indent))
        
        lines.append(f"{indent}")
        return lines
    
    def _generate_action_code(self, action: ParsedAction, step_index: int, indent: str) -> List[str]:
        """Generate code for a single action."""
        step_info = f"Step {step_index + 1}, Action {action.action_index + 1}"
        
        if action.action_type == "go_to_url":
            return self._generate_go_to_url(action, step_info, indent)
        elif action.action_type == "input_text":
            return self._generate_input_text(action, step_info, indent)
        elif action.action_type in ["click_element", "click_element_by_index"]:
            return self._generate_click_element(action, step_info, indent)
        elif action.action_type == "scroll_down":
            return self._generate_scroll(action, step_info, "down", indent)
        elif action.action_type == "scroll_up":
            return self._generate_scroll(action, step_info, "up", indent)
        elif action.action_type == "wait":
            return self._generate_wait(action, step_info, indent)
        elif action.action_type == "done":
            return self._generate_done(action, step_info, indent)
        else:
            return [f"{indent}# Unsupported action: {action.action_type} ({step_info})"]
    
    def _generate_go_to_url(self, action: ParsedAction, step_info: str, indent: str) -> List[str]:
        """Generate go_to_url action code."""
        url = action.parameters.get("url", "")
        if not url:
            return [f"{indent}# Skipping go_to_url: missing URL ({step_info})"]
        
        lines = []
        if self.config.include_logging:
            lines.append(f"{indent}print(f'Navigating to: {url} ({step_info})')")
        
        lines.append(f"{indent}self.driver.get({repr(url)})")
        
        if self.config.include_waits:
            lines.append(f"{indent}time.sleep(1)")
        
        if self.config.include_assertions:
            lines.extend([
                f"{indent}# Verify navigation",
                f"{indent}self.assertIn({repr(url)}, self.driver.current_url, 'Navigation failed')",
            ])
        
        return lines
    
    def _generate_input_text(self, action: ParsedAction, step_info: str, indent: str) -> List[str]:
        """Generate input_text action code."""
        text = action.parameters.get("text", "")
        if not action.selector_info or not text:
            return [f"{indent}# Skipping input_text: missing selector or text ({step_info})"]
        
        selector = self._get_selenium_selector(action.selector_info)
        clean_text = self._handle_sensitive_data(text)
        
        lines = []
        if self.config.include_logging:
            lines.append(f"{indent}print(f'Entering text in field ({step_info})')")
        
        lines.extend([
            f"{indent}element = self.wait.until(EC.element_to_be_clickable({selector}))",
            f"{indent}element.clear()",
            f"{indent}element.send_keys({repr(clean_text)})",
        ])
        
        if self.config.include_waits:
            lines.append(f"{indent}time.sleep(0.5)")
        
        return lines
    
    def _generate_click_element(self, action: ParsedAction, step_info: str, indent: str) -> List[str]:
        """Generate click_element action code."""
        if not action.selector_info:
            return [f"{indent}# Skipping click: missing selector ({step_info})"]
        
        selector = self._get_selenium_selector(action.selector_info)
        
        lines = []
        if self.config.include_logging:
            lines.append(f"{indent}print(f'Clicking element ({step_info})')")
        
        lines.extend([
            f"{indent}element = self.wait.until(EC.element_to_be_clickable({selector}))",
            f"{indent}element.click()",
        ])
        
        if self.config.include_waits:
            lines.append(f"{indent}time.sleep(0.5)")
        
        return lines
    
    def _generate_scroll(self, action: ParsedAction, step_info: str, direction: str, indent: str) -> List[str]:
        """Generate scroll action code."""
        amount = action.parameters.get("amount")
        
        lines = []
        if self.config.include_logging:
            lines.append(f"{indent}print(f'Scrolling {direction} ({step_info})')")
        
        if amount and isinstance(amount, int):
            scroll_amount = amount if direction == "down" else -amount
            lines.append(f"{indent}self.driver.execute_script(f'window.scrollBy(0, {scroll_amount})')")
        else:
            scroll_expr = "window.innerHeight" if direction == "down" else "-window.innerHeight"
            lines.append(f"{indent}self.driver.execute_script(f'window.scrollBy(0, {scroll_expr})')")
        
        if self.config.include_waits:
            lines.append(f"{indent}time.sleep(0.5)")
        
        return lines
    
    def _generate_wait(self, action: ParsedAction, step_info: str, indent: str) -> List[str]:
        """Generate wait action code."""
        seconds = action.parameters.get("seconds", 3)
        try:
            wait_seconds = int(seconds)
        except (ValueError, TypeError):
            wait_seconds = 3
        
        lines = []
        if self.config.include_logging:
            lines.append(f"{indent}print(f'Waiting for {wait_seconds} seconds ({step_info})')")
        
        lines.append(f"{indent}time.sleep({wait_seconds})")
        return lines
    
    def _generate_done(self, action: ParsedAction, step_info: str, indent: str) -> List[str]:
        """Generate done action code."""
        success = action.parameters.get("success", True)
        message = action.parameters.get("text", "Test completed")
        
        lines = [
            f"{indent}print('--- Test marked as Done ({step_info}) ---')",
            f"{indent}print(f'Success: {success}')",
        ]
        
        if message:
            clean_message = self._handle_sensitive_data(str(message))
            lines.append(f"{indent}print(f'Message: {clean_message}')")
        
        return lines
    
    def _generate_entry_point(self) -> List[str]:
        """Generate script entry point."""
        return [
            "",
            "if __name__ == '__main__':",
            "    unittest.main(verbosity=2)",
        ]
    
    def _get_selenium_selector(self, selector_info: Dict[str, Any]) -> str:
        """Convert selector info to Selenium By locator."""
        # Prefer CSS selector, fall back to XPath
        if "css_selector" in selector_info and selector_info["css_selector"]:
            css_selector = selector_info["css_selector"]
            return f"(By.CSS_SELECTOR, {repr(css_selector)})"
        elif "xpath" in selector_info and selector_info["xpath"]:
            xpath = selector_info["xpath"]
            # Remove xpath= prefix if present
            if xpath.startswith("xpath="):
                xpath = xpath[6:]
            return f"(By.XPATH, {repr(xpath)})"
        else:
            return "(By.TAG_NAME, 'body')"  # Fallback selector 