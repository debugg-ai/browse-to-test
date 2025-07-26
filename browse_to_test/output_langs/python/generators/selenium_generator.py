"""
Selenium code generator for Python.

This module generates Python test scripts using the Selenium WebDriver framework.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...exceptions import TemplateGenerationError, CodeGenerationError
from browse_to_test.core.configuration import CommentManager


class SeleniumPythonGenerator:
    """
    Generator for Python + Selenium test scripts.
    
    This class handles the generation of complete test scripts, utility functions,
    and framework-specific code for Selenium automation in Python.
    """
    
    def __init__(self, template_dir: Optional[Path] = None, constants_path: Optional[Path] = None):
        """
        Initialize the Selenium Python generator.
        
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
        Generate import statements for Selenium Python script.
        
        Args:
            include_utilities: Whether to include utility imports
            
        Returns:
            Import statements as string
        """
        imports = []
        
        # Base imports
        base_template = self._load_template("base_imports")
        imports.append(base_template.format(
            framework="Selenium", 
            timestamp=datetime.now().isoformat()
        ))
        
        # Framework-specific imports
        selenium_imports = [
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "from selenium.webdriver.support.ui import Select",
            "from selenium.common.exceptions import TimeoutException, NoSuchElementException"
        ]
        imports.extend(selenium_imports)
        
        # Add utilities import if requested
        if include_utilities:
            imports.append("")  # Empty line
            imports.append("# Import utility functions")
            imports.append("from .utilities import (")
            utility_names = [
                "log_step", "log_error", "log_success", "safe_selenium_action",
                "try_locate_and_act_selenium", "replace_sensitive_data",
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
        
        # Timeouts (Selenium uses seconds, not milliseconds)
        timeouts = self.constants["timeouts"]
        lines.append("# Timeout settings (in seconds)")
        for key, value in timeouts.items():
            const_name = key.upper().replace('_MS', '')  # Remove _MS suffix
            lines.append(f"{const_name} = {value / 1000}")  # Convert to seconds
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
        
        # Browser arguments
        browser_args = self.constants["browser_args"]
        lines.append("# Browser arguments")
        lines.append(f"BROWSER_ARGS = {browser_args}")
        
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
        
        # Add Selenium-specific utilities
        utilities.append(self._generate_selenium_utilities())
        
        return "\n\n".join(utilities)
    
    def _generate_selenium_utilities(self) -> str:
        """Generate Selenium-specific utility functions."""
        lines = []
        lines.append("# Selenium-specific utilities")
        lines.append("")
        
        # Safe action execution
        lines.extend([
            "def safe_selenium_action(driver, action_func, *args, step_info: str = '', **kwargs):",
            "    \"\"\"Execute a Selenium action with error handling.\"\"\"",
            "    try:",
            "        log_step(f\"Executing action: {action_func.__name__}\", step_info)",
            "        return action_func(*args, **kwargs)",
            "    except Exception as e:",
            "        error_msg = f\"Selenium action failed ({action_func.__name__}): {e}\"",
            "        log_error(error_msg, step_info)",
            "        raise E2eActionError(error_msg) from e",
            ""
        ])
        
        # Element interaction with retry
        lines.extend([
            "def try_locate_and_act_selenium(driver, selector: str, by_type: str, action_type: str,",
            "                               text: str = None, step_info: str = '', timeout: int = 10):",
            "    \"\"\"Locate element and perform action with Selenium.\"\"\"",
            "    log_step(f\"Attempting {action_type} using {by_type}: {format_selector(selector)}\", step_info)",
            "    ",
            "    try:",
            "        # Map by_type string to By constants",
            "        by_mapping = {",
            "            'id': By.ID,",
            "            'name': By.NAME,",
            "            'xpath': By.XPATH,",
            "            'css': By.CSS_SELECTOR,",
            "            'class': By.CLASS_NAME,",
            "            'tag': By.TAG_NAME",
            "        }",
            "        ",
            "        by_locator = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)",
            "        ",
            "        wait = WebDriverWait(driver, timeout)",
            "        element = wait.until(EC.presence_of_element_located((by_locator, selector)))",
            "        ",
            "        if action_type == 'click':",
            "            element.click()",
            "            log_success(f\"Successfully clicked element: {format_selector(selector)}\")",
            "        elif action_type == 'send_keys' and text is not None:",
            "            element.clear()",
            "            element.send_keys(text)",
            "            log_success(f\"Successfully sent keys to element: {format_selector(selector)}\")",
            "        elif action_type == 'select' and text is not None:",
            "            select = Select(element)",
            "            select.select_by_visible_text(text)",
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
        script_parts.append(f"def {test_name}():")
        script_parts.append('    """Generated test function."""')
        script_parts.append("")
        
        # Browser setup
        script_parts.extend([
            "    # Setup WebDriver",
            "    from selenium.webdriver.chrome.options import Options",
            "    options = Options()",
            "    for arg in BROWSER_ARGS:",
            "        options.add_argument(arg)",
            f"    options.headless = {self.constants['browser_settings']['headless_mode']}",
            "    ",
            "    driver = webdriver.Chrome(options=options)",
            f"    driver.set_window_size({self.constants['browser_settings']['viewport']['width']}, {self.constants['browser_settings']['viewport']['height']})",
            "    ",
            "    try:"
        ])
        
        # Generate test steps with detailed comments
        comment_manager = CommentManager("python")
        indent = "        "
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
            "    finally:",
            "        # Cleanup",
            "        driver.quit()",
            ""
        ])
        
        # Main execution
        script_parts.extend([
            "if __name__ == '__main__':",
            f"    {test_name}()"
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
            lines.append(f"{indent}driver.get('{url}')")
            
        elif action_type == 'click':
            lines.append(f"{indent}try_locate_and_act_selenium(driver, '{selector}', 'css', 'click')")
            
        elif action_type == 'fill':
            lines.append(f"{indent}try_locate_and_act_selenium(driver, '{selector}', 'css', 'send_keys', '{text}')")
            
        elif action_type == 'select':
            lines.append(f"{indent}try_locate_and_act_selenium(driver, '{selector}', 'css', 'select', '{text}')")
            
        elif action_type == 'wait':
            timeout = step.get('timeout', self.constants['timeouts']['default_timeout_ms'])
            lines.append(f"{indent}import time")
            lines.append(f"{indent}time.sleep({timeout / 1000})")  # Convert to seconds
            
        else:
            lines.append(f"{indent}# TODO: Implement action type '{action_type}'")
            lines.append(f"{indent}log_warning(f\"Unimplemented action type: {action_type}\")")
        
        return lines 