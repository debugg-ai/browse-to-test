#!/usr/bin/env python3
"""
Language-specific templates for generating test utilities in different programming languages.

This module contains templates and generators for creating reusable test utilities
in Python, TypeScript, JavaScript, C#, Java, and other supported languages.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LanguageTemplate:
    """Template for generating code in a specific language."""
    
    language: str
    file_extension: str
    comment_prefix: str
    
    # File structure templates
    file_header_template: str
    import_template: str
    function_template: str
    class_template: str
    async_function_template: str
    
    # Language-specific syntax
    async_keyword: str
    function_keyword: str
    class_keyword: str
    exception_keyword: str
    

class LanguageTemplateManager:
    """Manages language-specific templates and code generation."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, LanguageTemplate]:
        """Initialize templates for all supported languages."""
        return {
            "python": self._create_python_template(),
            "typescript": self._create_typescript_template(),
            "javascript": self._create_javascript_template(),
            "csharp": self._create_csharp_template(),
            "java": self._create_java_template(),
        }
    
    def _create_python_template(self) -> LanguageTemplate:
        """Create Python-specific template."""
        return LanguageTemplate(
            language="python",
            file_extension=".py",
            comment_prefix="#",
            file_header_template='''#!/usr/bin/env python3
"""
{description}
"""

{imports}
''',
            import_template="from {module} import {items}",
            function_template='''def {name}({params}){return_type}:
    """{docstring}"""
{body}
''',
            class_template='''class {name}({base_classes}):
    """{docstring}"""
{body}
''',
            async_function_template='''async def {name}({params}){return_type}:
    """{docstring}"""
{body}
''',
            async_keyword="async",
            function_keyword="def",
            class_keyword="class",
            exception_keyword="Exception"
        )
    
    def _create_typescript_template(self) -> LanguageTemplate:
        """Create TypeScript-specific template."""
        return LanguageTemplate(
            language="typescript",
            file_extension=".ts",
            comment_prefix="//",
            file_header_template='''/**
 * {description}
 */

{imports}
''',
            import_template="import {{ {items} }} from '{module}';",
            function_template='''/**
 * {docstring}
 */
export function {name}({params}){return_type} {{
{body}
}}
''',
            class_template='''/**
 * {docstring}
 */
export class {name}{base_classes} {{
{body}
}}
''',
            async_function_template='''/**
 * {docstring}
 */
export async function {name}({params}){return_type} {{
{body}
}}
''',
            async_keyword="async",
            function_keyword="function",
            class_keyword="class",
            exception_keyword="Error"
        )
    
    def _create_javascript_template(self) -> LanguageTemplate:
        """Create JavaScript-specific template."""
        return LanguageTemplate(
            language="javascript",
            file_extension=".js",
            comment_prefix="//",
            file_header_template='''/**
 * {description}
 */

{imports}
''',
            import_template="import {{ {items} }} from '{module}';",
            function_template='''/**
 * {docstring}
 */
export function {name}({params}) {{
{body}
}}
''',
            class_template='''/**
 * {docstring}
 */
export class {name}{base_classes} {{
{body}
}}
''',
            async_function_template='''/**
 * {docstring}
 */
export async function {name}({params}) {{
{body}
}}
''',
            async_keyword="async",
            function_keyword="function",
            class_keyword="class",
            exception_keyword="Error"
        )
    
    def _create_csharp_template(self) -> LanguageTemplate:
        """Create C#-specific template."""
        return LanguageTemplate(
            language="csharp",
            file_extension=".cs",
            comment_prefix="//",
            file_header_template='''/// <summary>
/// {description}
/// </summary>

{imports}

namespace TestUtilities
{{
''',
            import_template="using {module};",
            function_template='''/// <summary>
/// {docstring}
/// </summary>
public static {return_type} {name}({params})
{{
{body}
}}
''',
            class_template='''/// <summary>
/// {docstring}
/// </summary>
public class {name}{base_classes}
{{
{body}
}}
''',
            async_function_template='''/// <summary>
/// {docstring}
/// </summary>
public static async Task{return_type} {name}({params})
{{
{body}
}}
''',
            async_keyword="async",
            function_keyword="",
            class_keyword="class",
            exception_keyword="Exception"
        )
    
    def _create_java_template(self) -> LanguageTemplate:
        """Create Java-specific template."""
        return LanguageTemplate(
            language="java",
            file_extension=".java",
            comment_prefix="//",
            file_header_template='''/**
 * {description}
 */

{imports}

public class TestUtilities {{
''',
            import_template="import {module};",
            function_template='''/**
 * {docstring}
 */
public static {return_type} {name}({params}) {{
{body}
}}
''',
            class_template='''/**
 * {docstring}
 */
public class {name}{base_classes} {{
{body}
}}
''',
            async_function_template='''/**
 * {docstring}
 */
public static CompletableFuture<{return_type}> {name}({params}) {{
{body}
}}
''',
            async_keyword="",
            function_keyword="",
            class_keyword="class",
            exception_keyword="Exception"
        )
    
    def get_template(self, language: str) -> Optional[LanguageTemplate]:
        """Get template for the specified language."""
        return self.templates.get(language)
    
    def generate_utility_code(self, language: str, utility_name: str, utility_type: str, **kwargs) -> str:
        """Generate utility code for the specified language."""
        template = self.get_template(language)
        if not template:
            raise ValueError(f"Unsupported language: {language}")
        
        # Generate language-specific utility based on type
        if utility_type == "exception":
            return self._generate_exception_utility(template, utility_name, **kwargs)
        elif utility_type == "helper":
            return self._generate_helper_utility(template, utility_name, **kwargs)
        elif utility_type == "assertion":
            return self._generate_assertion_utility(template, utility_name, **kwargs)
        elif utility_type == "framework":
            return self._generate_framework_utility(template, utility_name, **kwargs)
        else:
            return self._generate_generic_utility(template, utility_name, **kwargs)
    
    def _generate_exception_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate exception class utility."""
        if template.language == "python":
            return f'''class {name}({template.exception_keyword}):
    """Exception raised when a test action fails."""
    pass'''
        
        elif template.language in ["typescript", "javascript"]:
            return f'''export class {name} extends {template.exception_keyword} {{
    constructor(message: string) {{
        super(message);
        this.name = '{name}';
    }}
}}'''
        
        elif template.language == "csharp":
            return f'''public class {name} : {template.exception_keyword}
{{
    public {name}(string message) : base(message) {{ }}
}}'''
        
        elif template.language == "java":
            return f'''public class {name} extends {template.exception_keyword} {{
    public {name}(String message) {{
        super(message);
    }}
}}'''
        
        return f"// {name} exception not implemented for {template.language}"
    
    def _generate_helper_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate helper function utility."""
        framework = kwargs.get("framework", "playwright")
        
        if name == "replace_sensitive_data":
            return self._generate_replace_sensitive_data(template, framework)
        elif name == "safe_action":
            return self._generate_safe_action(template, framework)
        elif name == "try_locate_and_act":
            return self._generate_try_locate_and_act(template, framework)
        
        return f"// {name} helper not implemented for {template.language}"
    
    def _generate_assertion_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate assertion utility."""
        framework = kwargs.get("framework", "playwright")
        
        if name == "assert_element_text":
            return self._generate_assert_element_text(template, framework)
        
        return f"// {name} assertion not implemented for {template.language}"
    
    def _generate_framework_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate framework-specific utility."""
        framework = kwargs.get("framework", "playwright")
        
        if framework == "playwright":
            return self._generate_playwright_utility(template, name, **kwargs)
        elif framework == "selenium":
            return self._generate_selenium_utility(template, name, **kwargs)
        
        return f"// {name} framework utility not implemented for {template.language}"
    
    def _generate_generic_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate generic utility."""
        content = kwargs.get("content", "")
        docstring = kwargs.get("description", f"{name} utility function")
        
        if template.language == "python":
            return content  # Use content as-is for Python
        
        # For other languages, provide a basic template
        return f"// TODO: Implement {name} for {template.language}"
    
    def _generate_replace_sensitive_data(self, template: LanguageTemplate, framework: str) -> str:
        """Generate replace_sensitive_data utility for different languages."""
        if template.language == "python":
            return '''def replace_sensitive_data(text: str, sensitive_map: dict) -> str:
    """Replace sensitive data placeholders in text."""
    if not isinstance(text, str):
        return text
    for placeholder, value in sensitive_map.items():
        replacement_value = str(value) if value is not None else ''
        text = text.replace(f'<secret>{placeholder}</secret>', replacement_value)
    return text'''
        
        elif template.language in ["typescript", "javascript"]:
            return '''export function replaceSensitiveData(text: string, sensitiveMap: Record<string, any>): string {
    if (typeof text !== 'string') {
        return text;
    }
    
    for (const [placeholder, value] of Object.entries(sensitiveMap)) {
        const replacementValue = value !== null && value !== undefined ? String(value) : '';
        text = text.replace(`<secret>${placeholder}</secret>`, replacementValue);
    }
    
    return text;
}'''
        
        elif template.language == "csharp":
            return '''public static string ReplaceSensitiveData(string text, Dictionary<string, object> sensitiveMap)
{
    if (string.IsNullOrEmpty(text))
        return text;
    
    foreach (var kvp in sensitiveMap)
    {
        var replacementValue = kvp.Value?.ToString() ?? "";
        text = text.Replace($"<secret>{kvp.Key}</secret>", replacementValue);
    }
    
    return text;
}'''
        
        elif template.language == "java":
            return '''public static String replaceSensitiveData(String text, Map<String, Object> sensitiveMap) {
    if (text == null || text.isEmpty()) {
        return text;
    }
    
    for (Map.Entry<String, Object> entry : sensitiveMap.entrySet()) {
        String replacementValue = entry.getValue() != null ? entry.getValue().toString() : "";
        text = text.replace("<secret>" + entry.getKey() + "</secret>", replacementValue);
    }
    
    return text;
}'''
        
        return f"// replace_sensitive_data not implemented for {template.language}"
    
    def _generate_safe_action(self, template: LanguageTemplate, framework: str) -> str:
        """Generate safe_action utility for different languages."""
        if template.language == "python" and framework == "playwright":
            return '''async def safe_action(page: Page, action_func, *args, step_info: str = '', **kwargs):
    """Execute an action with error handling."""
    try:
        return await action_func(*args, **kwargs)
    except Exception as e:
        if step_info:
            print(f'Action failed ({step_info}): {e}', file=sys.stderr)
        else:
            print(f'Action failed: {e}', file=sys.stderr)
        raise E2eActionError(f'Action failed: {e}') from e'''
        
        elif template.language == "typescript" and framework == "playwright":
            return '''export async function safeAction<T>(
    page: Page, 
    actionFunc: () => Promise<T>, 
    stepInfo: string = ''
): Promise<T> {
    try {
        return await actionFunc();
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        if (stepInfo) {
            console.error(`Action failed (${stepInfo}): ${errorMessage}`);
        } else {
            console.error(`Action failed: ${errorMessage}`);
        }
        throw new E2eActionError(`Action failed: ${errorMessage}`);
    }
}'''
        
        elif template.language == "javascript" and framework == "playwright":
            return '''export async function safeAction(page, actionFunc, stepInfo = '') {
    try {
        return await actionFunc();
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        if (stepInfo) {
            console.error(`Action failed (${stepInfo}): ${errorMessage}`);
        } else {
            console.error(`Action failed: ${errorMessage}`);
        }
        throw new E2eActionError(`Action failed: ${errorMessage}`);
    }
}'''
        
        return f"// safe_action not implemented for {template.language} + {framework}"
    
    def _generate_try_locate_and_act(self, template: LanguageTemplate, framework: str) -> str:
        """Generate try_locate_and_act utility for different languages."""
        if template.language == "python" and framework == "playwright":
            return '''async def try_locate_and_act(page: Page, selector: str, action_type: str, text: str = None, step_info: str = ''):
    """Locate element and perform action with fallback."""
    print(f'Attempting {action_type} using selector: {selector} ({step_info})')
    
    try:
        locator = page.locator(selector).first
        
        if action_type == 'click':
            await locator.click(timeout=10000)
        elif action_type == 'fill' and text is not None:
            await locator.fill(text, timeout=10000)
        else:
            raise ValueError(f'Unknown action type: {action_type}')
        
        print(f'  ✓ {action_type} successful')
        await page.wait_for_timeout(500)
        
    except Exception as e:
        error_msg = f'Element interaction failed: {e} ({step_info})'
        print(f'  ✗ {error_msg}', file=sys.stderr)
        raise E2eActionError(error_msg) from e'''
        
        elif template.language == "typescript" and framework == "playwright":
            return '''export async function tryLocateAndAct(
    page: Page, 
    selector: string, 
    actionType: string, 
    text?: string, 
    stepInfo: string = ''
): Promise<void> {
    console.log(`Attempting ${actionType} using selector: ${selector} (${stepInfo})`);
    
    try {
        const locator = page.locator(selector).first();
        
        if (actionType === 'click') {
            await locator.click({ timeout: 10000 });
        } else if (actionType === 'fill' && text !== undefined) {
            await locator.fill(text, { timeout: 10000 });
        } else {
            throw new Error(`Unknown action type: ${actionType}`);
        }
        
        console.log(`  ✓ ${actionType} successful`);
        await page.waitForTimeout(500);
        
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        const errorMsg = `Element interaction failed: ${errorMessage} (${stepInfo})`;
        console.error(`  ✗ ${errorMsg}`);
        throw new E2eActionError(errorMsg);
    }
}'''
        
        return f"// try_locate_and_act not implemented for {template.language} + {framework}"
    
    def _generate_assert_element_text(self, template: LanguageTemplate, framework: str) -> str:
        """Generate assert_element_text utility for different languages."""
        if template.language == "python" and framework == "playwright":
            return '''async def assert_element_text(page: Page, selector: str, expected_text: str):
    """Assert that an element contains the expected text."""
    element = page.locator(selector).first
    actual_text = await element.text_content()
    if expected_text not in actual_text:
        raise AssertionError(f"Expected '{expected_text}' in element text, got '{actual_text}'")'''
        
        elif template.language == "typescript" and framework == "playwright":
            return '''export async function assertElementText(page: Page, selector: string, expectedText: string): Promise<void> {
    const element = page.locator(selector).first();
    const actualText = await element.textContent();
    if (!actualText?.includes(expectedText)) {
        throw new Error(`Expected '${expectedText}' in element text, got '${actualText}'`);
    }
}'''
        
        return f"// assert_element_text not implemented for {template.language} + {framework}"
    
    def _generate_playwright_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate Playwright-specific utility."""
        # Delegate to specific utility generators
        if name == "safe_action":
            return self._generate_safe_action(template, "playwright")
        elif name == "try_locate_and_act":
            return self._generate_try_locate_and_act(template, "playwright")
        
        return f"// Playwright utility {name} not implemented for {template.language}"
    
    def _generate_selenium_utility(self, template: LanguageTemplate, name: str, **kwargs) -> str:
        """Generate Selenium-specific utility."""
        # TODO: Implement Selenium utilities for different languages
        return f"// Selenium utility {name} not implemented for {template.language}"
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.templates.keys())
    
    def get_file_extension(self, language: str) -> str:
        """Get file extension for the specified language."""
        template = self.get_template(language)
        return template.file_extension if template else ".txt" 