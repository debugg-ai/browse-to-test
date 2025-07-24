"""
Modern Framework Support System

This module extends browse-to-test with support for modern testing frameworks
and enhanced TypeScript/JavaScript code generation capabilities.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import json
import re
from pathlib import Path


class ModernFramework(Enum):
    """Modern testing frameworks supported by the library."""
    JEST = "jest"
    TESTING_LIBRARY = "testing_library"
    VITEST = "vitest"
    WEBDRIVERIO = "webdriverio"
    PUPPETEER = "puppeteer"
    CYPRESS = "cypress"
    PLAYWRIGHT_TEST = "playwright_test"


class ReactComponent(Enum):
    """React component testing patterns."""
    FUNCTIONAL = "functional"
    CLASS = "class"
    HOOK = "hook"
    CONTEXT = "context"


class TestingPattern(Enum):
    """Modern testing patterns."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    COMPONENT = "component"
    VISUAL = "visual"
    API = "api"
    ACCESSIBILITY = "accessibility"


@dataclass
class FrameworkConfig:
    """Configuration for modern framework support."""
    framework: ModernFramework
    language: str = "typescript"
    testing_pattern: TestingPattern = TestingPattern.E2E
    react_component_type: Optional[ReactComponent] = None
    use_async_await: bool = True
    use_test_ids: bool = True
    use_accessibility_queries: bool = True
    generate_mocks: bool = False
    use_page_objects: bool = False
    typescript_strict: bool = True
    use_esm: bool = True
    test_timeout: int = 30000


@dataclass
class ModernTestTemplate:
    """Template for modern framework test generation."""
    framework: ModernFramework
    imports: List[str]
    setup_code: str
    teardown_code: str
    describe_pattern: str
    test_pattern: str
    assertion_patterns: Dict[str, str]
    selector_patterns: Dict[str, str]


@dataclass
class TypeScriptEnhancements:
    """Enhanced TypeScript code generation features."""
    use_strict_types: bool = True
    generate_interfaces: bool = True
    use_generic_types: bool = True
    enable_decorators: bool = False
    use_optional_chaining: bool = True
    use_nullish_coalescing: bool = True


class ModernFrameworkGenerator:
    """Generates test code for modern testing frameworks."""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[ModernFramework, ModernTestTemplate]:
        """Load framework-specific templates."""
        return {
            ModernFramework.JEST: self._get_jest_template(),
            ModernFramework.TESTING_LIBRARY: self._get_testing_library_template(),
            ModernFramework.VITEST: self._get_vitest_template(),
            ModernFramework.WEBDRIVERIO: self._get_webdriverio_template(),
            ModernFramework.PUPPETEER: self._get_puppeteer_template(),
            ModernFramework.CYPRESS: self._get_cypress_template(),
            ModernFramework.PLAYWRIGHT_TEST: self._get_playwright_test_template(),
        }
    
    def _get_jest_template(self) -> ModernTestTemplate:
        """Get Jest framework template."""
        return ModernTestTemplate(
            framework=ModernFramework.JEST,
            imports=[
                "import { jest } from '@jest/globals';",
                "import { screen, render, fireEvent, waitFor } from '@testing-library/react';",
                "import { setupServer } from 'msw/node';",
                "import userEvent from '@testing-library/user-event';"
            ],
            setup_code="""
beforeAll(() => {
  server.listen();
});

beforeEach(() => {
  jest.clearAllMocks();
});

afterEach(() => {
  server.resetHandlers();
  cleanup();
});

afterAll(() => {
  server.close();
});
            """,
            teardown_code="",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="it('{description}', async () => {{",
            assertion_patterns={
                "visible": "expect(screen.getByTestId('{selector}')).toBeVisible()",
                "text": "expect(screen.getByTestId('{selector}')).toHaveTextContent('{expected}')",
                "value": "expect(screen.getByTestId('{selector}')).toHaveValue('{expected}')",
                "exists": "expect(screen.getByTestId('{selector}')).toBeInTheDocument()"
            },
            selector_patterns={
                "testid": "screen.getByTestId('{value}')",
                "role": "screen.getByRole('{role}', {{ name: '{name}' }})",
                "text": "screen.getByText('{text}')",
                "label": "screen.getByLabelText('{label}')"
            }
        )
    
    def _get_testing_library_template(self) -> ModernTestTemplate:
        """Get Testing Library template."""
        return ModernTestTemplate(
            framework=ModernFramework.TESTING_LIBRARY,
            imports=[
                "import { render, screen, fireEvent, waitFor } from '@testing-library/react';",
                "import { userEvent } from '@testing-library/user-event';",
                "import { within } from '@testing-library/react';",
                "import { axe, toHaveNoViolations } from 'jest-axe';"
            ],
            setup_code="""
expect.extend(toHaveNoViolations);

const user = userEvent.setup();
            """,
            teardown_code="cleanup();",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="test('{description}', async () => {{",
            assertion_patterns={
                "accessible": "expect(await axe(container)).toHaveNoViolations()",
                "focus": "expect(screen.getByTestId('{selector}')).toHaveFocus()",
                "disabled": "expect(screen.getByTestId('{selector}')).toBeDisabled()",
                "checked": "expect(screen.getByTestId('{selector}')).toBeChecked()"
            },
            selector_patterns={
                "role": "screen.getByRole('{role}')",
                "accessible_name": "screen.getByRole('{role}', {{ name: /^{name}/i }})",
                "placeholder": "screen.getByPlaceholderText('{placeholder}')",
                "alt": "screen.getByAltText('{alt}')"
            }
        )
    
    def _get_vitest_template(self) -> ModernTestTemplate:
        """Get Vitest framework template."""
        return ModernTestTemplate(
            framework=ModernFramework.VITEST,
            imports=[
                "import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';",
                "import { render, screen, cleanup } from '@testing-library/react';",
                "import { createMemoryRouter, RouterProvider } from 'react-router-dom';"
            ],
            setup_code="""
beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
});
            """,
            teardown_code="",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="it('{description}', async () => {{",
            assertion_patterns={
                "called": "expect(mockFn).toHaveBeenCalled()",
                "called_with": "expect(mockFn).toHaveBeenCalledWith({args})",
                "called_times": "expect(mockFn).toHaveBeenCalledTimes({count})",
                "snapshot": "expect(container.firstChild).toMatchSnapshot()"
            },
            selector_patterns={
                "data_testid": "screen.getByTestId('{testid}')",
                "query_by": "screen.queryByTestId('{testid}')",
                "find_by": "await screen.findByTestId('{testid}')",
                "get_all": "screen.getAllByTestId('{testid}')"
            }
        )
    
    def _get_webdriverio_template(self) -> ModernTestTemplate:
        """Get WebDriver.io template."""
        return ModernTestTemplate(
            framework=ModernFramework.WEBDRIVERIO,
            imports=[
                "import { browser, $, $$ } from '@wdio/globals';",
                "import { expect } from '@wdio/globals';"
            ],
            setup_code="""
beforeEach(async () => {
  await browser.maximizeWindow();
});
            """,
            teardown_code="",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="it('{description}', async () => {{",
            assertion_patterns={
                "displayed": "await expect($('[data-testid=\"{selector}\"]')).toBeDisplayed()",
                "text": "await expect($('[data-testid=\"{selector}\"]')).toHaveText('{expected}')",
                "value": "await expect($('[data-testid=\"{selector}\"]')).toHaveValue('{expected}')",
                "existing": "await expect($('[data-testid=\"{selector}\"]')).toExist()"
            },
            selector_patterns={
                "testid": "$('[data-testid=\"{value}\"]')",
                "css": "$('{css}')",
                "xpath": "$('={xpath}')",
                "text": "$('*={text}')"
            }
        )
    
    def _get_puppeteer_template(self) -> ModernTestTemplate:
        """Get Puppeteer template."""
        return ModernTestTemplate(
            framework=ModernFramework.PUPPETEER,
            imports=[
                "import puppeteer, { Browser, Page } from 'puppeteer';",
                "import { toMatchImageSnapshot } from 'jest-image-snapshot';"
            ],
            setup_code="""
let browser: Browser;
let page: Page;

beforeAll(async () => {
  browser = await puppeteer.launch({ headless: 'new' });
});

beforeEach(async () => {
  page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });
});

afterEach(async () => {
  await page.close();
});

afterAll(async () => {
  await browser.close();
});

expect.extend({ toMatchImageSnapshot });
            """,
            teardown_code="",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="test('{description}', async () => {{",
            assertion_patterns={
                "visible": "await expect(page.locator('[data-testid=\"{selector}\"]')).toBeVisible()",
                "text": "await expect(page.locator('[data-testid=\"{selector}\"]')).toHaveText('{expected}')",
                "screenshot": "expect(await page.screenshot()).toMatchImageSnapshot()",
                "url": "expect(page.url()).toBe('{expected}')"
            },
            selector_patterns={
                "testid": "page.locator('[data-testid=\"{value}\"]')",
                "css": "page.locator('{css}')",
                "xpath": "page.locator('xpath={xpath}')",
                "text": "page.locator('text={text}')"
            }
        )
    
    def _get_cypress_template(self) -> ModernTestTemplate:
        """Get Cypress template."""
        return ModernTestTemplate(
            framework=ModernFramework.CYPRESS,
            imports=[],
            setup_code="""
beforeEach(() => {
  cy.visit('/');
});
            """,
            teardown_code="",
            describe_pattern="describe('{description}', () => {{",
            test_pattern="it('{description}', () => {{",
            assertion_patterns={
                "visible": "cy.get('[data-cy=\"{selector}\"]').should('be.visible')",
                "text": "cy.get('[data-cy=\"{selector}\"]').should('contain.text', '{expected}')",
                "value": "cy.get('[data-cy=\"{selector}\"]').should('have.value', '{expected}')",
                "exists": "cy.get('[data-cy=\"{selector}\"]').should('exist')"
            },
            selector_patterns={
                "testid": "cy.get('[data-cy=\"{value}\"]')",
                "css": "cy.get('{css}')",
                "contains": "cy.contains('{text}')",
                "role": "cy.get('[role=\"{role}\"]')"
            }
        )
    
    def _get_playwright_test_template(self) -> ModernTestTemplate:
        """Get Playwright Test template."""
        return ModernTestTemplate(
            framework=ModernFramework.PLAYWRIGHT_TEST,
            imports=[
                "import { test, expect, Page } from '@playwright/test';",
                "import { AxeBuilder } from '@axe-core/playwright';"
            ],
            setup_code="",
            teardown_code="",
            describe_pattern="test.describe('{description}', () => {{",
            test_pattern="test('{description}', async ({{ page }}) => {{",
            assertion_patterns={
                "visible": "await expect(page.getByTestId('{selector}')).toBeVisible()",
                "text": "await expect(page.getByTestId('{selector}')).toHaveText('{expected}')",
                "accessible": "expect(await new AxeBuilder({{ page }}).analyze()).toHaveNoViolations()",
                "screenshot": "await expect(page).toHaveScreenshot('{name}.png')"
            },
            selector_patterns={
                "testid": "page.getByTestId('{value}')",
                "role": "page.getByRole('{role}')",
                "text": "page.getByText('{text}')",
                "label": "page.getByLabel('{label}')"
            }
        )
    
    def generate_test_file(self, test_data: Dict[str, Any]) -> str:
        """Generate a complete test file for the configured framework."""
        template = self.templates[self.config.framework]
        
        # Generate imports
        imports = self._generate_imports(template)
        
        # Generate setup and teardown
        setup = template.setup_code.strip()
        teardown = template.teardown_code.strip()
        
        # Generate test cases
        test_cases = self._generate_test_cases(test_data, template)
        
        # Combine everything
        test_file = f"""// Generated test file for {self.config.framework.value}
// Framework: {self.config.framework.value}
// Pattern: {self.config.testing_pattern.value}
// Language: {self.config.language}

{imports}

{setup}

{test_cases}

{teardown}
"""
        
        return self._format_typescript_code(test_file) if self.config.language == "typescript" else test_file
    
    def _generate_imports(self, template: ModernTestTemplate) -> str:
        """Generate framework-specific imports."""
        imports = template.imports.copy()
        
        # Add conditional imports based on config
        if self.config.use_accessibility_queries:
            if self.config.framework in [ModernFramework.JEST, ModernFramework.TESTING_LIBRARY]:
                imports.append("import { axe, toHaveNoViolations } from 'jest-axe';")
        
        if self.config.generate_mocks:
            if self.config.framework == ModernFramework.JEST:
                imports.append("import { jest } from '@jest/globals';")
            elif self.config.framework == ModernFramework.VITEST:
                imports.append("import { vi } from 'vitest';")
        
        return "\n".join(imports)
    
    def _generate_test_cases(self, test_data: Dict[str, Any], template: ModernTestTemplate) -> str:
        """Generate test cases from automation data."""
        test_cases = []
        
        # Extract test scenarios from data
        scenarios = self._extract_scenarios(test_data)
        
        for scenario in scenarios:
            test_case = self._generate_single_test_case(scenario, template)
            test_cases.append(test_case)
        
        return "\n\n".join(test_cases)
    
    def _extract_scenarios(self, test_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test scenarios from automation data."""
        # This would parse the input data and group actions into logical test scenarios
        scenarios = []
        
        if "steps" in test_data:
            current_scenario = {
                "name": "User interaction flow",
                "steps": test_data["steps"],
                "assertions": []
            }
            scenarios.append(current_scenario)
        
        return scenarios
    
    def _generate_single_test_case(self, scenario: Dict[str, Any], template: ModernTestTemplate) -> str:
        """Generate a single test case."""
        test_name = scenario.get("name", "Test case")
        steps = scenario.get("steps", [])
        
        test_body = []
        
        # Add navigation if URL is present
        if any(step.get("action") == "navigate" for step in steps):
            nav_step = next(step for step in steps if step.get("action") == "navigate")
            if self.config.framework == ModernFramework.PLAYWRIGHT_TEST:
                test_body.append(f"  await page.goto('{nav_step.get('url', '/')}');")
            elif self.config.framework == ModernFramework.PUPPETEER:
                test_body.append(f"  await page.goto('{nav_step.get('url', '/')}');")
            elif self.config.framework == ModernFramework.CYPRESS:
                test_body.append(f"  cy.visit('{nav_step.get('url', '/')}');")
        
        # Generate step actions
        for step in steps:
            action_code = self._generate_action_code(step, template)
            if action_code:
                test_body.append(f"  {action_code}")
        
        # Generate assertions
        for assertion in scenario.get("assertions", []):
            assertion_code = self._generate_assertion_code(assertion, template)
            if assertion_code:
                test_body.append(f"  {assertion_code}")
        
        test_pattern = template.test_pattern.format(description=test_name)
        test_content = "\n".join(test_body)
        
        return f"{test_pattern}\n{test_content}\n  }});"
    
    def _generate_action_code(self, step: Dict[str, Any], template: ModernTestTemplate) -> str:
        """Generate code for a single action step."""
        action = step.get("action", "")
        
        if action == "click":
            selector = self._get_selector_code(step, template)
            if self.config.framework in [ModernFramework.PLAYWRIGHT_TEST, ModernFramework.PUPPETEER]:
                return f"await {selector}.click();"
            elif self.config.framework == ModernFramework.CYPRESS:
                return f"{selector}.click();"
            else:
                return f"await user.click({selector});"
        
        elif action == "type" or action == "input_text":
            selector = self._get_selector_code(step, template)
            text = step.get("text", "")
            if self.config.framework in [ModernFramework.PLAYWRIGHT_TEST, ModernFramework.PUPPETEER]:
                return f"await {selector}.fill('{text}');"
            elif self.config.framework == ModernFramework.CYPRESS:
                return f"{selector}.type('{text}');"
            else:
                return f"await user.type({selector}, '{text}');"
        
        elif action == "wait":
            if self.config.framework == ModernFramework.PLAYWRIGHT_TEST:
                return f"await page.waitForTimeout({step.get('duration', 1000)});"
            elif self.config.framework == ModernFramework.CYPRESS:
                return f"cy.wait({step.get('duration', 1000)});"
            else:
                return f"await new Promise(resolve => setTimeout(resolve, {step.get('duration', 1000)}));"
        
        return ""
    
    def _get_selector_code(self, step: Dict[str, Any], template: ModernTestTemplate) -> str:
        """Generate selector code for an element."""
        element = step.get("element", {})
        
        # Prefer test IDs if available and enabled
        if self.config.use_test_ids and element.get("data-testid"):
            return template.selector_patterns["testid"].format(value=element["data-testid"])
        
        # Use accessibility queries if enabled
        if self.config.use_accessibility_queries:
            if element.get("role") and "role" in template.selector_patterns:
                return template.selector_patterns["role"].format(role=element["role"])
            if element.get("aria-label") and "label" in template.selector_patterns:
                return template.selector_patterns["label"].format(label=element["aria-label"])
        
        # Fallback to CSS or XPath
        if element.get("css_selector") and "css" in template.selector_patterns:
            return template.selector_patterns["css"].format(css=element["css_selector"])
        
        return "// TODO: Add appropriate selector"
    
    def _generate_assertion_code(self, assertion: Dict[str, Any], template: ModernTestTemplate) -> str:
        """Generate assertion code."""
        assertion_type = assertion.get("type", "")
        selector = assertion.get("selector", "")
        expected = assertion.get("expected", "")
        
        if assertion_type in template.assertion_patterns:
            pattern = template.assertion_patterns[assertion_type]
            return pattern.format(selector=selector, expected=expected) + ";"
        
        return ""
    
    def _format_typescript_code(self, code: str) -> str:
        """Format TypeScript code with enhanced features."""
        if not self.config.typescript_strict:
            return code
        
        # Add TypeScript enhancements
        enhancements = TypeScriptEnhancements(
            use_strict_types=self.config.typescript_strict,
            use_optional_chaining=True,
            use_nullish_coalescing=True
        )
        
        # Apply TypeScript formatting
        formatted_code = code
        
        # Add strict type annotations if enabled
        if enhancements.use_strict_types:
            formatted_code = self._add_type_annotations(formatted_code)
        
        return formatted_code
    
    def _add_type_annotations(self, code: str) -> str:
        """Add TypeScript type annotations."""
        # This would add proper type annotations to the generated code
        return code


class ModernFrameworkDetector:
    """Detects and recommends modern frameworks based on project structure."""
    
    @staticmethod
    def detect_project_frameworks(project_path: Path) -> Dict[str, Any]:
        """Detect frameworks used in a project."""
        detection_results = {
            "detected_frameworks": [],
            "package_json": None,
            "test_files": [],
            "recommendations": []
        }
        
        # Check package.json
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    detection_results["package_json"] = package_data
                    
                    # Detect frameworks from dependencies
                    all_deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {})
                    }
                    
                    framework_indicators = {
                        ModernFramework.JEST: ["jest", "@jest/core"],
                        ModernFramework.TESTING_LIBRARY: ["@testing-library/react", "@testing-library/dom"],
                        ModernFramework.VITEST: ["vitest"],
                        ModernFramework.WEBDRIVERIO: ["@wdio/cli", "webdriverio"],
                        ModernFramework.PUPPETEER: ["puppeteer"],
                        ModernFramework.CYPRESS: ["cypress"],
                        ModernFramework.PLAYWRIGHT_TEST: ["@playwright/test"]
                    }
                    
                    for framework, indicators in framework_indicators.items():
                        if any(indicator in all_deps for indicator in indicators):
                            detection_results["detected_frameworks"].append(framework.value)
            
            except (json.JSONDecodeError, IOError):
                pass
        
        # Scan for test files
        test_patterns = [
            "**/*.test.ts", "**/*.test.js", "**/*.spec.ts", "**/*.spec.js",
            "**/test/**/*.ts", "**/test/**/*.js", "**/__tests__/**/*.ts", "**/__tests__/**/*.js"
        ]
        
        for pattern in test_patterns:
            test_files = list(project_path.glob(pattern))
            detection_results["test_files"].extend([str(f.relative_to(project_path)) for f in test_files])
        
        # Generate recommendations
        detection_results["recommendations"] = ModernFrameworkDetector._generate_recommendations(
            detection_results["detected_frameworks"],
            detection_results["package_json"]
        )
        
        return detection_results
    
    @staticmethod
    def _generate_recommendations(detected_frameworks: List[str], package_json: Optional[Dict]) -> List[str]:
        """Generate framework recommendations."""
        recommendations = []
        
        if not detected_frameworks:
            recommendations.append("Consider adding a modern testing framework like Jest or Vitest")
        
        # React-specific recommendations
        if package_json and "react" in package_json.get("dependencies", {}):
            if "testing_library" not in detected_frameworks:
                recommendations.append("Add @testing-library/react for component testing")
            if "jest" not in detected_frameworks and "vitest" not in detected_frameworks:
                recommendations.append("Add Jest or Vitest for unit testing")
        
        # E2E testing recommendations
        if not any(fw in detected_frameworks for fw in ["playwright_test", "cypress", "webdriverio"]):
            recommendations.append("Consider adding Playwright or Cypress for E2E testing")
        
        return recommendations


# Framework-specific utilities
class FrameworkUtilities:
    """Utilities for working with modern frameworks."""
    
    @staticmethod
    def generate_config_files(framework: ModernFramework, project_path: Path) -> Dict[str, str]:
        """Generate configuration files for modern frameworks."""
        configs = {}
        
        if framework == ModernFramework.JEST:
            configs["jest.config.js"] = """
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '\\\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
            """
        
        elif framework == ModernFramework.VITEST:
            configs["vitest.config.ts"] = """
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      threshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
})
            """
        
        elif framework == ModernFramework.PLAYWRIGHT_TEST:
            configs["playwright.config.ts"] = """
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
            """
        
        return configs
    
    @staticmethod
    def get_best_practices(framework: ModernFramework) -> Dict[str, List[str]]:
        """Get best practices for each framework."""
        practices = {
            ModernFramework.JEST: [
                "Use descriptive test names",
                "Group related tests with describe blocks",
                "Use beforeEach/afterEach for setup/cleanup",
                "Mock external dependencies",
                "Test behavior, not implementation",
                "Use data-testid for stable selectors"
            ],
            ModernFramework.TESTING_LIBRARY: [
                "Query by accessibility attributes first",
                "Use userEvent for user interactions",
                "Avoid testing implementation details",
                "Use waitFor for async assertions",
                "Test accessibility with jest-axe",
                "Use screen.debug() for debugging"
            ],
            ModernFramework.PLAYWRIGHT_TEST: [
                "Use built-in auto-waiting",
                "Leverage parallel test execution",
                "Use page.getByRole() for accessibility",
                "Implement visual regression testing",
                "Use test.beforeEach for common setup",
                "Configure multiple browsers"
            ]
        }
        
        return practices.get(framework, []) 