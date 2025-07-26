"""
Playwright code generator for JavaScript.

This module generates JavaScript test scripts using the Playwright testing framework.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...exceptions import TemplateGenerationError, CodeGenerationError
from browse_to_test.core.configuration import CommentManager


class PlaywrightJavascriptGenerator:
    """
    Generator for JavaScript + Playwright test scripts.
    
    This class handles the generation of complete test scripts, utility functions,
    and framework-specific code for Playwright automation in JavaScript.
    """
    
    def __init__(self, template_dir: Optional[Path] = None, constants_path: Optional[Path] = None):
        """
        Initialize the Playwright JavaScript generator.
        
        Args:
            template_dir: Path to JavaScript template directory
            constants_path: Path to common constants file
        """
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.constants_path = constants_path or Path(__file__).parent.parent.parent / "common" / "constants.json"
        self.messages_path = Path(__file__).parent.parent.parent / "common" / "messages.json"
        
        # Load shared constants and messages
        self._load_constants()
        self._load_messages()
        
        # Load JavaScript language metadata
        metadata_path = Path(__file__).parent.parent / "metadata.json"
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
    
    def _load_constants(self):
        """Load shared constants from JSON file."""
        try:
            with open(self.constants_path, 'r') as f:
                self.constants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("constants", "javascript", f"Failed to load constants: {e}")
    
    def _load_messages(self):
        """Load shared messages from JSON file."""
        try:
            with open(self.messages_path, 'r') as f:
                self.messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TemplateGenerationError("messages", "javascript", f"Failed to load messages: {e}")
    
    def generate_imports(self, include_utilities: bool = True) -> str:
        """Generate import statements for Playwright JavaScript script."""
        imports = []
        
        # Base imports
        imports.extend([
            "/**",
            " * Generated test script by browse-to-test.",
            " *",
            " * Framework: Playwright",
            " * Language: JavaScript",
            f" * Generated at: {datetime.now().isoformat()}",
            " */",
            "",
            "const { test, expect } = require('@playwright/test');"
        ])
        
        if include_utilities:
            imports.extend([
                "",
                "// Import utility functions", 
                "const { logStep, logError, logSuccess } = require('./utilities');"
            ])
        
        return "\n".join(imports)
    
    def generate_constants(self) -> str:
        """Generate constants code for JavaScript."""
        lines = []
        lines.append("// Test configuration constants")
        lines.append("")
        
        # Timeouts
        timeouts = self.constants["timeouts"]
        lines.append("// Timeout settings (in milliseconds)")
        for key, value in timeouts.items():
            const_name = key.upper()
            lines.append(f"const {const_name} = {value};")
        lines.append("")
        
        lines.append("module.exports = {")
        for key in timeouts.keys():
            const_name = key.upper()
            lines.append(f"    {const_name},")
        lines.append("};")
        
        return "\n".join(lines)
    
    def generate_exceptions(self) -> str:
        """Generate exception classes for JavaScript."""
        return """// Custom exception classes for test automation

class E2eActionError extends Error {
    constructor(message, action, selector) {
        super(message);
        this.name = 'E2eActionError';
        this.action = action;
        this.selector = selector;
    }
}

class ElementNotFoundError extends E2eActionError {
    constructor(selector, timeout) {
        const message = timeout 
            ? `Element not found: ${selector} (timeout: ${timeout}ms)`
            : `Element not found: ${selector}`;
        super(message, undefined, selector);
        this.name = 'ElementNotFoundError';
    }
}

module.exports = {
    E2eActionError,
    ElementNotFoundError
};"""
    
    def generate_utilities(self) -> str:
        """Generate utility functions for JavaScript."""
        return """// Utility functions for test automation

function logStep(step, details = '') {
    console.error(`🔸 ${step}`);
    if (details) {
        console.error(`   ${details}`);
    }
}

function logError(error, details = '') {
    console.error(`❌ ${error}`);
    if (details) {
        console.error(`   ${details}`);
    }
}

function logSuccess(message) {
    console.error(`✅ ${message}`);
}

module.exports = {
    logStep,
    logError,
    logSuccess
};"""
    
    def generate_test_script(self, automation_data: List[Dict[str, Any]], **kwargs) -> str:
        """Generate a complete test script from automation data."""
        script_parts = []
        
        # Generate imports
        script_parts.append(self.generate_imports(include_utilities=kwargs.get('include_utilities', True)))
        script_parts.append("")
        
        # Generate main test function
        test_name = kwargs.get('test_name', 'generated_test')
        script_parts.append(f"test('{test_name}', async ({{ page }}) => {{")
        
        # Generate test steps with detailed comments
        comment_manager = CommentManager("javascript")
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
        elif action_type == 'click':
            lines.append(f"{indent}await page.click('{selector}');")
        elif action_type == 'fill':
            lines.append(f"{indent}await page.fill('{selector}', '{text}');")
        elif action_type == 'wait':
            timeout = step.get('timeout', self.constants['timeouts']['default_timeout_ms'])
            lines.append(f"{indent}await page.waitForTimeout({timeout});")
        else:
            lines.append(f"{indent}// TODO: Implement action type '{action_type}'")
        
        return lines 