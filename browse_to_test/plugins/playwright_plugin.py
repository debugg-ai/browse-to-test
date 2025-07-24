"""
Playwright plugin for generating Python test scripts.

Integrates the existing Playwright script generation into the new plugin architecture.
"""

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base import OutputPlugin, GeneratedTestScript, PluginError
from ..core.configuration.config import OutputConfig
from ..core.processing.input_parser import ParsedAutomationData, ParsedAction, ParsedStep
from ..core.configuration.language_templates import LanguageTemplateManager


logger = logging.getLogger(__name__)


class PlaywrightPlugin(OutputPlugin):
    """Plugin for generating Playwright test scripts in Python."""
    
    def __init__(self, config: OutputConfig):
        """Initialize the Playwright plugin."""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.template_manager = LanguageTemplateManager()
    
    @property
    def plugin_name(self) -> str:
        """Return the plugin name."""
        return "playwright"
    
    @property
    def supported_frameworks(self) -> List[str]:
        """Return supported frameworks."""
        return ["playwright"]
    
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
            valid_browsers = ["chromium", "firefox", "webkit"]
            if framework_config["browser_type"] not in valid_browsers:
                errors.append(f"Invalid browser type. Valid options: {', '.join(valid_browsers)}")
        
        # Check headless setting
        if "headless" in framework_config and not isinstance(framework_config["headless"], bool):
            errors.append("Headless setting must be boolean")
        
        return errors
    
    def generate_test_script(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> GeneratedTestScript:
        """Generate Playwright test script from parsed data."""
        try:
            self.logger.debug(f"Generating Playwright {self.config.language} script for {len(parsed_data.steps)} steps")
            
            # Generate script content based on language
            if self.config.language == "python":
                script_content = self._generate_script_content(parsed_data, analysis_results)
            else:
                # Use language templates for non-Python languages
                script_content = self._generate_multi_language_script(parsed_data, analysis_results, system_context, context_hints)
            
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
                    "plugin_version": "2.0.0",
                    "has_assertions": self.config.include_assertions,
                    "has_error_handling": self.config.include_error_handling,
                    "language": self.config.language,
                }
            )
            
        except Exception as e:
            raise PluginError(f"Failed to generate Playwright script: {e}", self.plugin_name) from e
    
    def get_template_variables(self) -> Dict[str, Any]:
        """Get template variables for script generation."""
        framework_config = self.config.framework_config
        
        return {
            "browser_type": framework_config.get("browser_type", "chromium"),
            "headless": framework_config.get("headless", False),
            "viewport_width": framework_config.get("viewport_width", 1280),
            "viewport_height": framework_config.get("viewport_height", 720),
            "timeout": framework_config.get("timeout", 30000),
            "include_assertions": self.config.include_assertions,
            "include_waits": self.config.include_waits,
            "include_error_handling": self.config.include_error_handling,
            "include_logging": self.config.include_logging,
            "include_screenshots": self.config.include_screenshots,
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
        
        # Add main test function
        script_lines.extend(self._generate_main_function(parsed_data, analysis_results))
        
        # Add entry point
        script_lines.extend(self._generate_entry_point())
        
        return "\n".join(script_lines)
    
    def _generate_multi_language_script(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate script content for non-Python languages using templates."""
        language = self.config.language
        template = self.template_manager.get_template(language)
        
        if not template:
            raise PluginError(f"Language '{language}' not supported", self.plugin_name)
        
        script_lines = []
        
        # Add language-specific imports
        if language == "typescript":
            script_lines.extend([
                "import { test, expect } from '@playwright/test';",
                "import { Page } from '@playwright/test';",
                ""
            ])
        elif language == "javascript":
            script_lines.extend([
                "const { test, expect } = require('@playwright/test');",
                ""
            ])
        elif language == "csharp":
            script_lines.extend([
                "using Microsoft.Playwright;",
                "using System.Threading.Tasks;",
                "using System;",
                "",
                "namespace PlaywrightTests",
                "{",
                ""
            ])
        elif language == "java":
            script_lines.extend([
                "import com.microsoft.playwright.*;",
                "import java.util.concurrent.CompletableFuture;",
                "",
                "public class PlaywrightTest {",
                ""
            ])
        
        # Add main test function
        if language == "typescript":
            script_lines.extend([
                "test('login test', async ({ page }: { page: Page }) => {",
            ])
        elif language == "javascript":
            script_lines.extend([
                "test('login test', async ({ page }) => {",
            ])
        elif language == "csharp":
            script_lines.extend([
                "    public class LoginTest",
                "    {",
                "        public static async Task Main(string[] args)",
                "        {",
                "            using var playwright = await Playwright.CreateAsync();",
                "            await using var browser = await playwright.Chromium.LaunchAsync();",
                "            var page = await browser.NewPageAsync();",
                ""
            ])
        elif language == "java":
            script_lines.extend([
                "    public static void main(String[] args) {",
                "        CompletableFuture.runAsync(() -> {",
                "            try (Playwright playwright = Playwright.create()) {",
                "                Browser browser = playwright.chromium().launch();",
                "                Page page = browser.newPage();",
                ""
            ])
        
        # Generate actions for each step
        for step in parsed_data.steps:
            for action in step.actions:
                action_code = self._generate_multi_language_action(action, language)
                script_lines.extend(action_code)
        
        # Add closing braces/statements
        if language in ["typescript", "javascript"]:
            script_lines.append("});")
        elif language == "csharp":
            script_lines.extend([
                "",
                "            await page.CloseAsync();",
                "            await browser.CloseAsync();",
                "        }",
                "    }",
                "}",
            ])
        elif language == "java":
            script_lines.extend([
                "",
                "                page.close();",
                "                browser.close();",
                "            } catch (Exception e) {",
                "                e.printStackTrace();",
                "            }",
                "        });",
                "    }",
                "}",
            ])
        
        return "\n".join(script_lines)
    
    def _generate_multi_language_action(self, action: ParsedAction, language: str) -> List[str]:
        """Generate action code for different languages."""
        lines = []
        
        if action.action_type == "go_to_url":
            url = action.parameters.get("url", "")
            if language == "typescript":
                lines.append(f"    await page.goto('{url}');")
            elif language == "javascript":
                lines.append(f"    await page.goto('{url}');")
            elif language == "csharp":
                lines.append(f"            await page.GotoAsync(\"{url}\");")
            elif language == "java":
                lines.append(f"                page.navigate(\"{url}\");")
                
        elif action.action_type == "input_text":
            text = action.parameters.get("text", "")
            selector = action.selector_info.get("css_selector", "") if action.selector_info else ""
            if language == "typescript":
                lines.append(f"    await page.fill('{selector}', '{text}');")
            elif language == "javascript":
                lines.append(f"    await page.fill('{selector}', '{text}');")
            elif language == "csharp":
                lines.append(f"            await page.FillAsync(\"{selector}\", \"{text}\");")
            elif language == "java":
                lines.append(f"                page.fill(\"{selector}\", \"{text}\");")
                
        elif action.action_type in ["click_element", "click_element_by_index"]:
            selector = action.selector_info.get("css_selector", "") if action.selector_info else ""
            if language == "typescript":
                lines.append(f"    await page.click('{selector}');")
            elif language == "javascript":
                lines.append(f"    await page.click('{selector}');")
            elif language == "csharp":
                lines.append(f"            await page.ClickAsync(\"{selector}\");")
            elif language == "java":
                lines.append(f"                page.click(\"{selector}\");")
                
        elif action.action_type == "wait":
            seconds = action.parameters.get("seconds", 3)
            wait_ms = int(seconds) * 1000
            if language == "typescript":
                lines.append(f"    await page.waitForTimeout({wait_ms});")
            elif language == "javascript":
                lines.append(f"    await page.waitForTimeout({wait_ms});")
            elif language == "csharp":
                lines.append(f"            await page.WaitForTimeoutAsync({wait_ms});")
            elif language == "java":
                lines.append(f"                page.waitForTimeout({wait_ms});")
        else:
            # Unsupported action
            comment_prefix = "//" if language in ["typescript", "javascript", "csharp", "java"] else "#"
            lines.append(f"    {comment_prefix} Unsupported action: {action.action_type}")
        
        return lines
    
    def _generate_imports(self) -> List[str]:
        """Generate import statements."""
        imports = [
            "import asyncio",
            "import json",
            "import os",
            "import sys",
            "from pathlib import Path",
            "import urllib.parse",
            "from playwright.async_api import async_playwright, Page, BrowserContext",
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
        
        if self.config.include_error_handling:
            helpers.extend([
                "# Custom exception for test failures",
                "class E2eActionError(Exception):",
                "    \"\"\"Exception raised when a test action fails.\"\"\"",
                "    pass",
                "",
            ])
        
        if self.config.include_waits or self.config.include_assertions:
            helpers.extend(self._generate_action_helpers())
        
        return helpers
    
    def _generate_action_helpers(self) -> List[str]:
        """Generate action helper functions."""
        helpers = [
            "# Helper function for robust action execution",
            "async def safe_action(page: Page, action_func, *args, step_info: str = '', **kwargs):",
            "    \"\"\"Execute an action with error handling.\"\"\"",
            "    try:",
            "        return await action_func(*args, **kwargs)",
            "    except Exception as e:",
        ]
        
        if self.config.include_error_handling:
            helpers.extend([
                "        if step_info:",
                "            print(f'Action failed ({step_info}): {e}', file=sys.stderr)",
                "        else:",
                "            print(f'Action failed: {e}', file=sys.stderr)",
                "        raise E2eActionError(f'Action failed: {e}') from e",
            ])
        else:
            helpers.extend([
                "        if step_info:",
                "            print(f'Action failed ({step_info}): {e}', file=sys.stderr)",
                "        raise",
            ])
        
        helpers.extend([
            "",
            "async def try_locate_and_act(page: Page, selector: str, action_type: str, text: str = None, step_info: str = ''):",
            "    \"\"\"Locate element and perform action with fallback.\"\"\"",
            "    print(f'Attempting {action_type} using selector: {selector} ({step_info})')",
            "    ",
            "    try:",
            "        locator = page.locator(selector).first",
            "        ",
            "        if action_type == 'click':",
            "            await locator.click(timeout=10000)",
            "        elif action_type == 'fill' and text is not None:",
            "            await locator.fill(text, timeout=10000)",
            "        else:",
            "            raise ValueError(f'Unknown action type: {action_type}')",
            "        ",
            "        print(f'  ✓ {action_type} successful')",
            "        await page.wait_for_timeout(500)",
            "        ",
            "    except Exception as e:",
            "        error_msg = f'Element interaction failed: {e} ({step_info})'",
            "        print(f'  ✗ {error_msg}', file=sys.stderr)",
        ])
        
        if self.config.include_error_handling:
            helpers.append("        raise E2eActionError(error_msg) from e")
        else:
            helpers.append("        raise")
        
        helpers.append("")
        return helpers
    
    def _generate_main_function(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate the main test function."""
        template_vars = self.get_template_variables()
        
        lines = [
            "async def run_test():",
            "    \"\"\"Main test function.\"\"\"",
        ]
        
        if self.config.include_error_handling:
            lines.extend([
                "    exit_code = 0",
                "    start_time = None",
                "    try:",
                "        start_time = asyncio.get_event_loop().time()",
            ])
        
        # Browser setup
        lines.extend([
            f"        async with async_playwright() as p:",
            f"            print('Starting {template_vars['browser_type']} browser...')",
            f"            browser = await p.{template_vars['browser_type']}.launch(",
            f"                headless={template_vars['headless']},",
            f"                timeout={template_vars['timeout']},",
            f"            )",
            f"            ",
            f"            context = await browser.new_context(",
            f"                viewport={{'width': {template_vars['viewport_width']}, 'height': {template_vars['viewport_height']}}},",
            f"            )",
            f"            ",
            f"            page = await context.new_page()",
            f"            print('Browser context created')",
            f"            ",
        ])
        
        # Generate actions for each step
        for step in parsed_data.steps:
            lines.extend(self._generate_step_actions(step, analysis_results))
        
        # Browser cleanup
        lines.extend([
            "            print('Test completed successfully')",
            "            await context.close()",
            "            await browser.close()",
            "            print('Browser closed')",
        ])
        
        if self.config.include_error_handling:
            lines.extend([
                "    except E2eActionError as e:",
                "        print(f'Test failed: {e}', file=sys.stderr)",
                "        exit_code = 1",
                "    except Exception as e:",
                "        print(f'Unexpected error: {e}', file=sys.stderr)",
                "        traceback.print_exc()",
                "        exit_code = 1",
                "    finally:",
                "        if start_time:",
                "            elapsed = asyncio.get_event_loop().time() - start_time",
                "            print(f'Test execution time: {elapsed:.2f} seconds')",
                "        if exit_code != 0:",
                "            sys.exit(exit_code)",
            ])
        
        lines.append("")
        return lines
    
    def _generate_step_actions(
        self, 
        step: ParsedStep,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate actions for a single step."""
        lines = [f"            # Step {step.step_index + 1}"]
        
        if self.config.add_comments and step.metadata:
            lines.append(f"            # Step metadata: {step.metadata}")
        
        for action in step.actions:
            lines.extend(self._generate_action_code(action, step.step_index))
        
        lines.append("")
        return lines
    
    def _generate_action_code(self, action: ParsedAction, step_index: int) -> List[str]:
        """Generate code for a single action."""
        step_info = f"Step {step_index + 1}, Action {action.action_index + 1}"
        
        if action.action_type == "go_to_url":
            return self._generate_go_to_url(action, step_info)
        elif action.action_type == "input_text":
            return self._generate_input_text(action, step_info)
        elif action.action_type in ["click_element", "click_element_by_index"]:
            return self._generate_click_element(action, step_info)
        elif action.action_type == "scroll_down":
            return self._generate_scroll(action, step_info, "down")
        elif action.action_type == "scroll_up":
            return self._generate_scroll(action, step_info, "up")
        elif action.action_type == "wait":
            return self._generate_wait(action, step_info)
        elif action.action_type == "done":
            return self._generate_done(action, step_info)
        else:
            return [f"            # Unsupported action: {action.action_type} ({step_info})"]
    
    def _generate_go_to_url(self, action: ParsedAction, step_info: str) -> List[str]:
        """Generate go_to_url action code."""
        url = action.parameters.get("url", "")
        if not url:
            return [f"            # Skipping go_to_url: missing URL ({step_info})"]
        
        lines = []
        if self.config.include_logging:
            lines.append(f"            print(f'Navigating to: {url} ({step_info})')")
        
        lines.extend([
            f"            await page.goto({repr(url)}, timeout={self.get_template_variables()['timeout']})",
            f"            await page.wait_for_load_state('load')",
        ])
        
        if self.config.include_waits:
            lines.append("            await page.wait_for_timeout(1000)")
        
        if self.config.include_assertions:
            lines.extend([
                f"            # Verify navigation",
                f"            assert '{url}' in page.url, f'Navigation failed. Expected {url}, got {{page.url}}'",
            ])
        
        return lines
    
    def _generate_input_text(self, action: ParsedAction, step_info: str) -> List[str]:
        """Generate input_text action code."""
        text = action.parameters.get("text", "")
        if not action.selector_info or not text:
            return [f"            # Skipping input_text: missing selector or text ({step_info})"]
        
        selector = self._get_best_selector(action.selector_info)
        clean_text = self._handle_sensitive_data(text)
        
        lines = []
        if self.config.include_logging:
            lines.append(f"            print(f'Entering text in field ({step_info})')")
        
        if self.config.include_waits or self.config.include_error_handling:
            lines.append(f"            await try_locate_and_act(page, {repr(selector)}, 'fill', {repr(clean_text)}, {repr(step_info)})")
        else:
            lines.extend([
                f"            await page.locator({repr(selector)}).fill({repr(clean_text)})",
                f"            await page.wait_for_timeout(500)",
            ])
        
        return lines
    
    def _generate_click_element(self, action: ParsedAction, step_info: str) -> List[str]:
        """Generate click_element action code."""
        if not action.selector_info:
            return [f"            # Skipping click: missing selector ({step_info})"]
        
        selector = self._get_best_selector(action.selector_info)
        
        lines = []
        if self.config.include_logging:
            lines.append(f"            print(f'Clicking element ({step_info})')")
        
        if self.config.include_waits or self.config.include_error_handling:
            lines.append(f"            await try_locate_and_act(page, {repr(selector)}, 'click', step_info={repr(step_info)})")
        else:
            lines.extend([
                f"            await page.locator({repr(selector)}).click()",
                f"            await page.wait_for_timeout(500)",
            ])
        
        return lines
    
    def _generate_scroll(self, action: ParsedAction, step_info: str, direction: str) -> List[str]:
        """Generate scroll action code."""
        amount = action.parameters.get("amount")
        
        lines = []
        if self.config.include_logging:
            lines.append(f"            print(f'Scrolling {direction} ({step_info})')")
        
        if amount and isinstance(amount, int):
            scroll_amount = amount if direction == "down" else -amount
            lines.append(f"            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')")
        else:
            scroll_expr = "window.innerHeight" if direction == "down" else "-window.innerHeight"
            lines.append(f"            await page.evaluate(f'window.scrollBy(0, {scroll_expr})')")
        
        if self.config.include_waits:
            lines.append("            await page.wait_for_timeout(500)")
        
        return lines
    
    def _generate_wait(self, action: ParsedAction, step_info: str) -> List[str]:
        """Generate wait action code."""
        seconds = action.parameters.get("seconds", 3)
        try:
            wait_seconds = int(seconds)
        except (ValueError, TypeError):
            wait_seconds = 3
        
        lines = []
        if self.config.include_logging:
            lines.append(f"            print(f'Waiting for {wait_seconds} seconds ({step_info})')")
        
        lines.append(f"            await asyncio.sleep({wait_seconds})")
        return lines
    
    def _generate_done(self, action: ParsedAction, step_info: str) -> List[str]:
        """Generate done action code."""
        success = action.parameters.get("success", True)
        message = action.parameters.get("text", "Test completed")
        
        lines = [
            f"            print('--- Test marked as Done ({step_info}) ---')",
            f"            print(f'Success: {success}')",
        ]
        
        if message:
            clean_message = self._handle_sensitive_data(str(message))
            lines.append(f"            print(f'Message: {clean_message}')")
        
        return lines
    
    def _generate_entry_point(self) -> List[str]:
        """Generate script entry point."""
        return [
            "if __name__ == '__main__':",
            "    if os.name == 'nt':",
            "        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())",
            "    asyncio.run(run_test())",
        ]
    
    def _get_best_selector(self, selector_info: Dict[str, Any]) -> str:
        """Get the best selector from selector info."""
        # Prefer CSS selector for maintainability, fall back to XPath
        if "css_selector" in selector_info and selector_info["css_selector"]:
            return selector_info["css_selector"]
        elif "xpath" in selector_info and selector_info["xpath"]:
            xpath = selector_info["xpath"]
            # Remove xpath= prefix if present
            if xpath.startswith("xpath="):
                xpath = xpath[6:]
            return f"xpath={xpath}"
        else:
            return "body"  # Fallback selector 