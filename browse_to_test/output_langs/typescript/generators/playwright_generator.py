"""
Playwright code generator for TypeScript.

This module generates TypeScript test scripts using the Playwright testing framework.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...exceptions import TemplateGenerationError, CodeGenerationError
from browse_to_test.core.configuration import CommentManager


class PlaywrightTypescriptGenerator:
    """
    Generator for TypeScript + Playwright test scripts.
    
    This class handles the generation of complete test scripts, utility functions,
    and framework-specific code for Playwright automation in TypeScript.
    """
    
    def __init__(self, template_dir: Optional[Path] = None, constants_path: Optional[Path] = None):
        """
        Initialize the Playwright TypeScript generator.
        
        Args:
            template_dir: Path to TypeScript template directory
            constants_path: Path to common constants file
        """
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.constants_path = constants_path or Path(__file__).parent.parent.parent / "common" / "constants.json"
        self.messages_path = Path(__file__).parent.parent.parent / "common" / "messages.json"
        
        # Load shared constants and messages
        self._load_constants()
        self._load_messages()
        
        # Load TypeScript language metadata
        metadata_path = Path(__file__).parent.parent / "metadata.json"
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
    
    def _load_constants(self):
        """Load shared constants from JSON file."""
        try:
            with open(self.constants_path, 'r') as f:
                self.constants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("constants", "typescript", f"Failed to load constants: {e}")
    
    def _load_messages(self):
        """Load shared messages from JSON file."""
        try:
            with open(self.messages_path, 'r') as f:
                self.messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("messages", "typescript", f"Failed to load messages: {e}")
    
    def _load_template(self, template_name: str) -> str:
        """Load a template file."""
        template_path = self.template_dir / f"{template_name}.txt"
        try:
            return template_path.read_text()
        except FileNotFoundError:
            raise TemplateGenerationError(template_name, "typescript", f"Template file not found: {template_path}")
    
    def generate_imports(self, include_utilities: bool = True) -> str:
        """
        Generate import statements for Playwright TypeScript script.
        
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
        
        # Add Playwright test imports
        imports.append("import { test, expect } from '@playwright/test';")
        
        # Add utilities import if requested
        if include_utilities:
            imports.append("")  # Empty line
            imports.append("// Import utility functions")
            imports.append("import {")
            utility_names = [
                "logStep", "logError", "logSuccess", "logWarning",
                "replaceSensitiveData", "maskSensitiveData", "formatSelector"
            ]
            for i, util in enumerate(utility_names):
                comma = "," if i < len(utility_names) - 1 else ""
                imports.append(f"    {util}{comma}")
            imports.append("} from './utilities';")
        
        return "\n".join(imports)
    
    def generate_constants(self) -> str:
        """
        Generate constants code for TypeScript.
        
        Returns:
            Constants definitions as string
        """
        lines = []
        lines.append("// Test configuration constants")
        lines.append("")
        
        # Timeouts
        timeouts = self.constants["timeouts"]
        lines.append("// Timeout settings (in milliseconds)")
        for key, value in timeouts.items():
            const_name = key.upper()
            lines.append(f"export const {const_name} = {value};")
        lines.append("")
        
        # Browser settings
        browser_settings = self.constants["browser_settings"]
        lines.append("// Browser configuration")
        for key, value in browser_settings.items():
            const_name = key.upper()
            if isinstance(value, str):
                lines.append(f'export const {const_name} = "{value}";')
            elif isinstance(value, dict):
                lines.append(f"export const {const_name} = {json.dumps(value)};")
            else:
                lines.append(f"export const {const_name} = {json.dumps(value)};")
        lines.append("")
        
        # Common selectors
        selectors = self.constants["common_selectors"]
        lines.append("// Common element selectors")
        lines.append("export const COMMON_SELECTORS = {")
        for key, value in selectors.items():
            if isinstance(value, list):
                formatted_list = json.dumps(value)
                lines.append(f'    {key}: {formatted_list},')
            else:
                lines.append(f'    {key}: "{value}",')
        lines.append("};")
        
        return "\n".join(lines)
    
    def generate_exceptions(self) -> str:
        """
        Generate exception classes for TypeScript.
        
        Returns:
            Exception class definitions as string
        """
        return self._load_template("exception_classes")
    
    def generate_utilities(self) -> str:
        """
        Generate utility functions for TypeScript.
        
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
        lines.append("// Playwright-specific utilities")
        lines.append("")
        
        # Safe action execution
        lines.extend([
            "export async function safePlaywrightAction<T>(",
            "    page: Page,",
            "    action: () => Promise<T>,",
            "    stepInfo: string = ''",
            "): Promise<T> {",
            "    try {",
            "        logStep(`Executing action`, stepInfo);",
            "        return await action();",
            "    } catch (error) {",
            "        const errorMsg = `Playwright action failed: ${error}`;",
            "        logError(errorMsg, stepInfo);",
            "        throw new E2eActionError(errorMsg);",
            "    }",
            "}",
            ""
        ])
        
        # Element interaction
        lines.extend([
            "export async function tryLocateAndActPlaywright(",
            "    page: Page,",
            "    selector: string,",
            "    actionType: 'click' | 'fill' | 'select',",
            "    text?: string,",
            "    stepInfo: string = '',",
            "    timeout: number = 10000",
            "): Promise<void> {",
            "    logStep(`Attempting ${actionType} using selector: ${formatSelector(selector)}`, stepInfo);",
            "    ",
            "    try {",
            "        const locator = page.locator(selector).first();",
            "        ",
            "        switch (actionType) {",
            "            case 'click':",
            "                await locator.click({ timeout });",
            "                logSuccess(`Successfully clicked element: ${formatSelector(selector)}`);",
            "                break;",
            "            case 'fill':",
            "                if (text !== undefined) {",
            "                    await locator.fill(text, { timeout });",
            "                    logSuccess(`Successfully filled element: ${formatSelector(selector)}`);",
            "                }",
            "                break;",
            "            case 'select':",
            "                if (text !== undefined) {",
            "                    await locator.selectOption(text, { timeout });",
            "                    logSuccess(`Successfully selected option: ${text}`);",
            "                }",
            "                break;",
            "            default:",
            "                throw new Error(`Unknown action type: ${actionType}`);",
            "        }",
            "    } catch (error) {",
            "        const errorMsg = `Failed to ${actionType} element ${formatSelector(selector)}: ${error}`;",
            "        logError(errorMsg, stepInfo);",
            "        throw new ElementNotFoundError(selector);",
            "    }",
            "}",
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
        script_parts.append(f"test('{test_name}', async ({{ page }}) => {{")
        
        # Generate test steps with detailed comments
        comment_manager = CommentManager("typescript")
        indent = "    "
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
        
        script_parts.append("});")
        
        return "\n".join(script_parts)
    
    def _generate_step_code(self, step: Dict[str, Any], indent: str) -> List[str]:
        """Generate code for a single automation step."""
        lines = []
        action_type = step.get('type', '').lower()
        selector = step.get('selector', '')
        text = step.get('text', '')
        url = step.get('url', '')
        
        if action_type == 'navigate':
            lines.append(f"{indent}await page.goto('{url}');")
            
        elif action_type in ['click', 'fill', 'select']:
            if action_type == 'fill':
                lines.append(f"{indent}await tryLocateAndActPlaywright(page, '{selector}', '{action_type}', '{text}');")
            elif action_type == 'select':
                lines.append(f"{indent}await tryLocateAndActPlaywright(page, '{selector}', '{action_type}', '{text}');")
            else:
                lines.append(f"{indent}await tryLocateAndActPlaywright(page, '{selector}', '{action_type}');")
                
        elif action_type == 'wait':
            timeout = step.get('timeout', self.constants['timeouts']['default_timeout_ms'])
            lines.append(f"{indent}await page.waitForTimeout({timeout});")
            
        else:
            lines.append(f"{indent}// TODO: Implement action type '{action_type}'")
            lines.append(f"{indent}logWarning(`Unimplemented action type: {action_type}`);")
        
        return lines 