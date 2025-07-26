"""
Playwright code generator for Python.

This module generates Python test scripts using the Playwright testing framework.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...exceptions import TemplateGenerationError, CodeGenerationError
from browse_to_test.core.configuration import CommentManager


class PlaywrightPythonGenerator:
    """
    Generator for Python + Playwright test scripts.
    
    This class handles the generation of complete test scripts, utility functions,
    and framework-specific code for Playwright automation in Python.
    """
    
    def __init__(self, template_dir: Optional[Path] = None, constants_path: Optional[Path] = None):
        """
        Initialize the Playwright Python generator.
        
        Args:
            template_dir: Path to Python template directory
            constants_path: Path to common constants file
        """
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.constants_path = constants_path or Path(__file__).parent.parent.parent / "common" / "constants.json"
        self.messages_path = Path(__file__).parent.parent.parent / "common" / "messages.json"
        
        # Load shared constants and messages
        self._load_constants()
        self._load_messages()
        
        # Load Python language metadata
        metadata_path = Path(__file__).parent.parent / "metadata.json"
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
    
    def _load_constants(self):
        """Load shared constants from JSON file."""
        try:
            with open(self.constants_path, 'r') as f:
                self.constants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("constants", "python", f"Failed to load constants: {e}")
    
    def _load_messages(self):
        """Load shared messages from JSON file."""
        try:
            with open(self.messages_path, 'r') as f:
                self.messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("messages", "python", f"Failed to load messages: {e}")
    
    def _load_template(self, template_name: str) -> str:
        """Load a template file."""
        template_path = self.template_dir / f"{template_name}.txt"
        try:
            return template_path.read_text()
        except FileNotFoundError:
            raise TemplateGenerationError(template_name, "python", f"Template file not found: {template_path}")
    
    def generate_imports(self, include_utilities: bool = True) -> str:
        """
        Generate import statements for Playwright Python script.
        
        Args:
            include_utilities: Whether to include utility imports
            
        Returns:
            Import statements as string
        """
        imports = []
        
        # Base imports
        base_template = self._load_template("base_imports")
        imports.append(base_template.format(
            framework="Playwright", 
            timestamp=datetime.now().isoformat()
        ))
        
        # Framework-specific imports
        playwright_imports = [
            "from playwright.async_api import async_playwright, Page, Browser, BrowserContext",
            "from playwright.async_api import Locator, TimeoutError as PlaywrightTimeoutError"
        ]
        imports.extend(playwright_imports)
        
        # Add utilities import if requested
        if include_utilities:
            imports.append("")  # Empty line
            imports.append("# Import utility functions")
            imports.append("from .utilities import (")
            utility_names = [
                "log_step", "log_error", "log_success", "safe_playwright_action",
                "try_locate_and_act_playwright", "wait_for_page_load_playwright",
                "assert_element_visible_playwright", "replace_sensitive_data",
                "mask_sensitive_data", "generate_test_data"
            ]
            for i, util in enumerate(utility_names):
                comma = "," if i < len(utility_names) - 1 else ""
                imports.append(f"    {util}{comma}")
            imports.append(")")
        
        return "\n".join(imports)
    
    def generate_constants(self) -> str:
        """
        Generate constants code for Python.
        
        Returns:
            Constants definitions as string
        """
        lines = []
        lines.append("# Test configuration constants")
        lines.append("")
        
        # Timeouts
        timeouts = self.constants["timeouts"]
        lines.append("# Timeout settings (in milliseconds)")
        for key, value in timeouts.items():
            const_name = key.upper()
            lines.append(f"{const_name} = {value}")
        lines.append("")
        
        # Browser settings
        browser_settings = self.constants["browser_settings"]
        lines.append("# Browser configuration")
        for key, value in browser_settings.items():
            const_name = key.upper()
            if isinstance(value, str):
                lines.append(f'{const_name} = "{value}"')
            elif isinstance(value, dict):
                lines.append(f"{const_name} = {value}")
            else:
                lines.append(f"{const_name} = {value}")
        lines.append("")
        
        # Common selectors
        selectors = self.constants["common_selectors"]
        lines.append("# Common element selectors")
        lines.append("COMMON_SELECTORS = {")
        for key, value in selectors.items():
            if isinstance(value, list):
                formatted_list = "[" + ", ".join(f'"{v}"' for v in value) + "]"
                lines.append(f'    "{key}": {formatted_list},')
            else:
                lines.append(f'    "{key}": "{value}",')
        lines.append("}")
        lines.append("")
        
        # Sensitive data patterns
        sensitive_patterns = self.constants["sensitive_data_patterns"]
        lines.append("# Sensitive data patterns")
        lines.append(f"SENSITIVE_DATA_PATTERNS = {sensitive_patterns}")
        
        return "\n".join(lines)
    
    def generate_exceptions(self) -> str:
        """
        Generate exception classes for Python.
        
        Returns:
            Exception class definitions as string
        """
        return self._load_template("exception_classes")
    
    def generate_utilities(self) -> str:
        """
        Generate utility functions for Python.
        
        Returns:
            Utility function definitions as string
        """
        utilities = [self._load_template("utility_functions")]
        
        # Add Playwright-specific utilities
        utilities.append(self._generate_playwright_utilities())
        
        return "\n\n".join(utilities)
    
    def _generate_playwright_utilities(self) -> str:
        """Generate Playwright-specific utility functions."""
        lines = []
        lines.append("# Playwright-specific utilities")
        lines.append("")
        
        # Safe action execution
        lines.extend([
            "async def safe_playwright_action(page: Page, action_func, *args, step_info: str = '', **kwargs):",
            "    \"\"\"Execute a Playwright action with error handling.\"\"\"",
            "    try:",
            "        log_step(f\"Executing action: {action_func.__name__}\", step_info)",
            "        return await action_func(*args, **kwargs)",
            "    except Exception as e:",
            "        error_msg = f\"Playwright action failed ({action_func.__name__}): {e}\"",
            "        log_error(error_msg, step_info)",
            "        raise E2eActionError(error_msg) from e",
            ""
        ])
        
        # Element interaction with retry
        lines.extend([
            "async def try_locate_and_act_playwright(page: Page, selector: str, action_type: str, ",
            "                                      text: str = None, step_info: str = '', timeout: int = 10000):",
            "    \"\"\"Locate element and perform action with fallback selectors.\"\"\"",
            "    log_step(f\"Attempting {action_type} using selector: {format_selector(selector)}\", step_info)",
            "    ",
            "    try:",
            "        locator = page.locator(selector).first",
            "        ",
            "        if action_type == 'click':",
            "            await locator.click(timeout=timeout)",
            "            log_success(f\"Successfully clicked element: {format_selector(selector)}\")",
            "        elif action_type == 'fill' and text is not None:",
            "            await locator.fill(text, timeout=timeout)",
            "            log_success(f\"Successfully filled element: {format_selector(selector)}\")",
            "        elif action_type == 'select' and text is not None:",
            "            await locator.select_option(value=text, timeout=timeout)",
            "            log_success(f\"Successfully selected option: {text}\")",
            "        else:",
            "            raise ValueError(f'Unknown action type: {action_type}')",
            "            ",
            "    except Exception as e:",
            "        error_msg = f\"Failed to {action_type} element {format_selector(selector)}: {e}\"",
            "        log_error(error_msg, step_info)",
            "        raise ElementNotFoundError(selector) from e",
            ""
        ])
        
        # Element visibility assertion
        lines.extend([
            "async def assert_element_visible_playwright(page: Page, selector: str, timeout: int = 10000):",
            "    \"\"\"Assert that an element is visible on the page.\"\"\"",
            "    try:",
            "        log_step(f\"Asserting element is visible: {format_selector(selector)}\")",
            "        element = page.locator(selector).first",
            "        await element.wait_for(state=\"visible\", timeout=timeout)",
            "        log_success(f\"Element is visible: {format_selector(selector)}\")",
            "    except Exception as e:",
            "        error_msg = f\"Element not visible: {format_selector(selector)} - {e}\"",
            "        log_error(error_msg)",
            "        raise ElementNotFoundError(selector, timeout) from e",
            ""
        ])
        
        # Page load waiting
        lines.extend([
            "async def wait_for_page_load_playwright(page: Page, timeout: int = 30000):",
            "    \"\"\"Wait for page to fully load.\"\"\"",
            "    try:",
            "        log_step(\"Waiting for page load\")",
            "        await page.wait_for_load_state(\"networkidle\", timeout=timeout)",
            "        log_success(\"Page loaded successfully\")",
            "    except Exception as e:",
            "        error_msg = f\"Page load timeout: {e}\"",
            "        log_error(error_msg)",
            "        raise TimeoutError(\"page_load\", timeout) from e",
            ""
        ])
        
        return "\n".join(lines)
    
    def generate_test_script(self, automation_data: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a complete test script from automation data.
        
        Args:
            automation_data: List of automation steps
            **kwargs: Additional generation options
            
        Returns:
            Complete test script as string
        """
        script_parts = []
        
        # Generate imports
        script_parts.append(self.generate_imports(include_utilities=kwargs.get('include_utilities', True)))
        script_parts.append("")
        
        # Generate main test function
        test_name = kwargs.get('test_name', 'generated_test')
        # Generate function header with proper documentation
        comment_manager = CommentManager("python")
        script_parts.append(f"async def {test_name}():")
        
        # Add contextual documentation
        doc_lines = comment_manager.doc_string(
            "Generated test function for automated browser testing",
            returns="None",
            indent="    "
        )
        script_parts.extend(doc_lines)
        script_parts.append("")
        
        # Browser setup
        script_parts.extend([
            "    async with async_playwright() as p:",
            "        # Launch browser",
            f"        browser = await p.chromium.launch(headless={self.constants['browser_settings']['headless_mode']})",
            "        context = await browser.new_context(",
            f"            viewport={self.constants['browser_settings']['viewport']},",
            f"            ignore_https_errors={self.constants['default_config']['ignore_https_errors']},",
            f"            locale='{self.constants['default_config']['locale']}'",
            "        )",
            "        page = await context.new_page()",
            "        ",
            "        try:"
        ])
        
        # Generate test steps with detailed comments
        indent = "            "
        for i, step in enumerate(automation_data):
            # Create detailed step header
            step_header_lines = comment_manager.step_header(
                step_number=i + 1,
                description=step.get('description', 'Unknown action'),
                metadata=step if isinstance(step, dict) else None,
                indent=indent
            )
            script_parts.extend(step_header_lines)
            
            # Add contextual information if available
            if step.get('url'):
                context_lines = comment_manager.contextual_info_comment({
                    'url': step.get('url'),
                    'element_count': step.get('element_count'),
                    'action_type': step.get('type'),
                }, indent)
                script_parts.extend(context_lines)
            
            script_parts.extend(self._generate_step_code(step, indent))
            script_parts.append("")
        
        # Cleanup
        script_parts.extend([
            "        finally:",
            "            # Cleanup",
            "            await page.close()",
            "            await context.close()",
            "            await browser.close()",
            ""
        ])
        
        # Main execution
        script_parts.extend([
            "if __name__ == '__main__':",
            f"    asyncio.run({test_name}())"
        ])
        
        return "\n".join(script_parts)
    
    def _generate_step_code(self, step: Dict[str, Any], indent: str) -> List[str]:
        """Generate code for a single automation step."""
        lines = []
        action_type = step.get('type', '').lower()
        selector = step.get('selector', '')
        text = step.get('text', '')
        url = step.get('url', '')
        
        if action_type == 'navigate':
            lines.append(f"{indent}await page.goto('{url}')")
            lines.append(f"{indent}await wait_for_page_load_playwright(page)")
            
        elif action_type in ['click', 'fill', 'select']:
            if action_type == 'fill':
                lines.append(f"{indent}await try_locate_and_act_playwright(page, '{selector}', '{action_type}', '{text}')")
            elif action_type == 'select':
                lines.append(f"{indent}await try_locate_and_act_playwright(page, '{selector}', '{action_type}', '{text}')")
            else:
                lines.append(f"{indent}await try_locate_and_act_playwright(page, '{selector}', '{action_type}')")
                
        elif action_type == 'wait':
            timeout = step.get('timeout', self.constants['timeouts']['default_timeout_ms'])
            lines.append(f"{indent}await page.wait_for_timeout({timeout})")
            
        elif action_type == 'assert_visible':
            lines.append(f"{indent}await assert_element_visible_playwright(page, '{selector}')")
            
        else:
            lines.append(f"{indent}# TODO: Implement action type '{action_type}'")
            lines.append(f"{indent}log_warning(f\"Unimplemented action type: {action_type}\")")
        
        return lines 