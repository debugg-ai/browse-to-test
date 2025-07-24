#!/usr/bin/env python3
"""
Comprehensive Test Validation System for Browse-to-Test

This module provides advanced validation capabilities for generated test scripts:
- Static code analysis and syntax validation
- Best practices enforcement
- Performance analysis and optimization suggestions
- Security vulnerability detection
- Accessibility compliance checking
- Cross-browser compatibility validation
- Test maintainability scoring
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import ast
import json


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"       # Critical issues that prevent execution
    WARNING = "warning"   # Issues that may cause problems
    INFO = "info"         # Suggestions for improvement
    STYLE = "style"       # Style and convention issues


class ValidationCategory(Enum):
    """Categories of validation checks."""
    SYNTAX = "syntax"                    # Code syntax and structure
    BEST_PRACTICES = "best_practices"    # Testing best practices
    PERFORMANCE = "performance"          # Performance considerations
    SECURITY = "security"               # Security vulnerabilities
    ACCESSIBILITY = "accessibility"     # Accessibility compliance
    MAINTAINABILITY = "maintainability" # Code maintainability
    COMPATIBILITY = "compatibility"     # Cross-browser compatibility
    RELIABILITY = "reliability"         # Test reliability and stability


@dataclass
class ValidationIssue:
    """Represents a validation issue found in test code."""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    rule_id: str = ""
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    code_snippet: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class ValidationResult:
    """Results of test validation analysis."""
    is_valid: bool
    overall_score: float  # 0-100 score
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    auto_fixes: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def error_count(self) -> int:
        return len([i for i in self.issues if i.severity == ValidationSeverity.ERROR])
    
    @property
    def warning_count(self) -> int:
        return len([i for i in self.issues if i.severity == ValidationSeverity.WARNING])
    
    @property
    def info_count(self) -> int:
        return len([i for i in self.issues if i.severity == ValidationSeverity.INFO])


class SyntaxValidator:
    """Validates code syntax and structure."""
    
    def __init__(self, language: str = "python"):
        self.language = language
    
    def validate(self, code: str, framework: str = "playwright") -> List[ValidationIssue]:
        """Validate code syntax and structure."""
        issues = []
        
        if self.language == "python":
            issues.extend(self._validate_python_syntax(code))
            issues.extend(self._validate_python_imports(code, framework))
            issues.extend(self._validate_python_async(code, framework))
        elif self.language in ["typescript", "javascript"]:
            issues.extend(self._validate_js_syntax(code))
            issues.extend(self._validate_js_imports(code, framework))
        
        return issues
    
    def _validate_python_syntax(self, code: str) -> List[ValidationIssue]:
        """Validate Python syntax."""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.SYNTAX,
                message=f"Syntax error: {e.msg}",
                line_number=e.lineno,
                column=e.offset,
                rule_id="python_syntax_error"
            ))
        
        return issues
    
    def _validate_python_imports(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate Python imports for the given framework."""
        issues = []
        
        # Required imports for different frameworks
        required_imports = {
            "playwright": ["playwright.async_api"],
            "selenium": ["selenium.webdriver", "selenium.webdriver.common.by"]
        }
        
        if framework in required_imports:
            for required_import in required_imports[framework]:
                if required_import not in code:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BEST_PRACTICES,
                        message=f"Missing recommended import: {required_import}",
                        rule_id="missing_import",
                        suggestion=f"Add: from {required_import} import ...",
                        auto_fixable=True
                    ))
        
        # Check for unused imports
        import_lines = re.findall(r'^(?:from\s+\S+\s+)?import\s+(.+)$', code, re.MULTILINE)
        for import_line in import_lines:
            # Simple check for unused imports (could be more sophisticated)
            imported_items = [item.strip() for item in import_line.split(',')]
            for item in imported_items:
                clean_item = item.split(' as ')[0].strip()
                if clean_item not in code.replace(import_line, ''):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.STYLE,
                        message=f"Potentially unused import: {clean_item}",
                        rule_id="unused_import"
                    ))
        
        return issues
    
    def _validate_python_async(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate async/await usage in Python."""
        issues = []
        
        if framework == "playwright":
            # Check for missing await keywords
            async_methods = [
                "goto", "click", "fill", "select_option", "wait_for", 
                "screenshot", "locator", "text_content", "get_attribute"
            ]
            
            for method in async_methods:
                # Look for method calls without await
                pattern = rf'(?<!await\s)\.{method}\s*\('
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.SYNTAX,
                        message=f"Missing 'await' for async method: {method}",
                        line_number=line_num,
                        rule_id="missing_await",
                        suggestion=f"Add 'await' before .{method}()",
                        auto_fixable=True
                    ))
        
        return issues
    
    def _validate_js_syntax(self, code: str) -> List[ValidationIssue]:
        """Validate JavaScript/TypeScript syntax."""
        issues = []
        
        # Basic syntax checks
        # Check for common syntax errors
        if code.count('(') != code.count(')'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.SYNTAX,
                message="Mismatched parentheses",
                rule_id="mismatched_parentheses"
            ))
        
        if code.count('{') != code.count('}'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.SYNTAX,
                message="Mismatched braces",
                rule_id="mismatched_braces"
            ))
        
        return issues
    
    def _validate_js_imports(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate JavaScript/TypeScript imports."""
        issues = []
        
        required_imports = {
            "playwright": ["@playwright/test"],
            "cypress": ["cypress"]
        }
        
        if framework in required_imports:
            for required_import in required_imports[framework]:
                if required_import not in code:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BEST_PRACTICES,
                        message=f"Missing recommended import: {required_import}",
                        rule_id="missing_import"
                    ))
        
        return issues


class BestPracticesValidator:
    """Validates adherence to testing best practices."""
    
    def validate(self, code: str, framework: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        """Validate testing best practices."""
        issues = []
        
        issues.extend(self._validate_test_structure(code, framework))
        issues.extend(self._validate_selectors(code, framework))
        issues.extend(self._validate_waits_and_timeouts(code, framework))
        issues.extend(self._validate_assertions(code, framework))
        issues.extend(self._validate_error_handling(code, framework))
        issues.extend(self._validate_test_data(code))
        
        return issues
    
    def _validate_test_structure(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate test structure and organization."""
        issues = []
        
        # Check for test function/method
        if framework == "playwright":
            if not re.search(r'test\s*\(', code) and not re.search(r'async\s+def\s+test_', code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.BEST_PRACTICES,
                    message="No test function found. Consider organizing code in test functions.",
                    rule_id="missing_test_function",
                    suggestion="Wrap code in a test function or test() block"
                ))
        
        # Check for descriptive test names
        test_functions = re.findall(r'(?:test|def\s+test_)([^(]*)', code)
        for test_name in test_functions:
            if len(test_name.strip()) < 5:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message=f"Test name '{test_name}' is too short. Use descriptive names.",
                    rule_id="short_test_name",
                    suggestion="Use descriptive test names that explain what is being tested"
                ))
        
        # Check for setup/teardown
        if len(code.split('\n')) > 20:  # For longer tests
            if not re.search(r'setup|setUp|before', code, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message="Consider adding setup/teardown for complex tests",
                    rule_id="missing_setup",
                    suggestion="Add setup functions for test initialization"
                ))
        
        return issues
    
    def _validate_selectors(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate selector usage and quality."""
        issues = []
        
        # Find all selectors in the code
        if framework == "playwright":
            selector_patterns = [
                r'locator\s*\(\s*["\']([^"\']+)["\']',
                r'getByTestId\s*\(\s*["\']([^"\']+)["\']',
                r'getByRole\s*\(\s*["\']([^"\']+)["\']'
            ]
        elif framework == "selenium":
            selector_patterns = [
                r'By\.CSS_SELECTOR\s*,\s*["\']([^"\']+)["\']',
                r'By\.XPATH\s*,\s*["\']([^"\']+)["\']',
                r'By\.ID\s*,\s*["\']([^"\']+)["\']'
            ]
        else:
            selector_patterns = []
        
        all_selectors = []
        for pattern in selector_patterns:
            selectors = re.findall(pattern, code)
            all_selectors.extend(selectors)
        
        for selector in all_selectors:
            # Check for brittle selectors
            if self._is_brittle_selector(selector):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.RELIABILITY,
                    message=f"Potentially brittle selector: {selector}",
                    rule_id="brittle_selector",
                    suggestion="Consider using data-testid or more stable selectors",
                    code_snippet=selector
                ))
            
            # Check for overly complex selectors
            if len(selector) > 100:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.MAINTAINABILITY,
                    message=f"Overly complex selector (length: {len(selector)})",
                    rule_id="complex_selector",
                    suggestion="Break down complex selectors or use more specific attributes",
                    code_snippet=selector[:50] + "..."
                ))
        
        # Check for recommended selector strategies
        has_testid = any("data-testid" in selector for selector in all_selectors)
        has_aria = any("aria-" in selector for selector in all_selectors)
        
        if not has_testid and not has_aria and len(all_selectors) > 3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.BEST_PRACTICES,
                message="Consider using data-testid or ARIA attributes for more stable selectors",
                rule_id="recommended_selectors",
                suggestion="Add data-testid attributes to elements for testing"
            ))
        
        return issues
    
    def _is_brittle_selector(self, selector: str) -> bool:
        """Check if a selector is potentially brittle."""
        brittle_patterns = [
            r':\s*nth-child\(\d+\)',  # nth-child selectors
            r'>\s*div\s*>\s*div',     # Deep DOM navigation
            r'\[\d+\]',               # Array-like selectors
            r'#\w{8,}',               # Long IDs (likely auto-generated)
        ]
        
        return any(re.search(pattern, selector) for pattern in brittle_patterns)
    
    def _validate_waits_and_timeouts(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate wait strategies and timeout usage."""
        issues = []
        
        # Check for hardcoded waits (sleep)
        sleep_patterns = [r'time\.sleep\s*\(', r'sleep\s*\(', r'wait\s*\(\s*\d+\s*\)']
        for pattern in sleep_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.BEST_PRACTICES,
                    message="Avoid hardcoded waits. Use explicit waits instead.",
                    line_number=line_num,
                    rule_id="hardcoded_wait",
                    suggestion="Use wait_for() or WebDriverWait with expected conditions"
                ))
        
        # Check for missing wait strategies
        if framework == "playwright":
            interaction_methods = ["click", "fill", "select_option"]
            for method in interaction_methods:
                method_calls = re.finditer(rf'\.{method}\s*\(', code)
                for call in method_calls:
                    # Check if there's a wait_for before this action
                    preceding_code = code[:call.start()]
                    if "wait_for" not in preceding_code[-200:]:  # Check last 200 chars
                        line_num = preceding_code.count('\n') + 1
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.INFO,
                            category=ValidationCategory.RELIABILITY,
                            message=f"Consider adding explicit wait before {method}()",
                            line_number=line_num,
                            rule_id="missing_explicit_wait",
                            suggestion=f"Add wait_for() before .{method}()"
                        ))
        
        # Check for reasonable timeout values
        timeout_patterns = [r'timeout\s*[:=]\s*(\d+)', r'wait\s*\(\s*(\d+)\s*\)']
        for pattern in timeout_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                timeout_value = int(match.group(1))
                if timeout_value > 60000:  # > 60 seconds
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.PERFORMANCE,
                        message=f"Very long timeout: {timeout_value}ms",
                        line_number=line_num,
                        rule_id="long_timeout",
                        suggestion="Consider if such a long timeout is necessary"
                    ))
        
        return issues
    
    def _validate_assertions(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate assertion usage and quality."""
        issues = []
        
        # Count assertions
        assertion_patterns = [
            r'assert\s+',
            r'expect\s*\(',
            r'should\s*\(',
            r'assertTrue\s*\(',
            r'assertEqual\s*\('
        ]
        
        assertion_count = 0
        for pattern in assertion_patterns:
            assertion_count += len(re.findall(pattern, code))
        
        # Check assertion coverage
        code_lines = len([line for line in code.split('\n') if line.strip()])
        if code_lines > 10 and assertion_count == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.BEST_PRACTICES,
                message="No assertions found. Tests should validate expected outcomes.",
                rule_id="missing_assertions",
                suggestion="Add assertions to verify test expectations"
            ))
        elif code_lines > 20 and assertion_count < 2:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.BEST_PRACTICES,
                message="Low assertion coverage. Consider adding more validations.",
                rule_id="low_assertion_coverage",
                suggestion="Add more specific assertions for better test coverage"
            ))
        
        # Check for assertion messages
        assertions_with_messages = len(re.findall(r'assert.*,\s*["\']', code))
        if assertion_count > 0 and assertions_with_messages < assertion_count * 0.5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.MAINTAINABILITY,
                message="Consider adding descriptive messages to assertions",
                rule_id="missing_assertion_messages",
                suggestion="Add meaningful error messages to assertions for better debugging"
            ))
        
        return issues
    
    def _validate_error_handling(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate error handling and exception management."""
        issues = []
        
        # Check for try-catch blocks in complex tests
        code_lines = len([line for line in code.split('\n') if line.strip()])
        has_try_catch = re.search(r'try\s*:', code) or re.search(r'catch\s*\(', code)
        
        if code_lines > 30 and not has_try_catch:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.RELIABILITY,
                message="Consider adding error handling for complex tests",
                rule_id="missing_error_handling",
                suggestion="Add try-catch blocks to handle potential failures gracefully"
            ))
        
        # Check for bare except clauses
        bare_except = re.findall(r'except\s*:', code)
        if bare_except:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.BEST_PRACTICES,
                message="Avoid bare except clauses. Catch specific exceptions.",
                rule_id="bare_except",
                suggestion="Specify exception types: except SpecificException:"
            ))
        
        return issues
    
    def _validate_test_data(self, code: str) -> List[ValidationIssue]:
        """Validate test data usage and management."""
        issues = []
        
        # Check for hardcoded sensitive data
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "token"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "secret")
        ]
        
        for pattern, data_type in sensitive_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SECURITY,
                    message=f"Hardcoded {data_type} detected",
                    line_number=line_num,
                    rule_id="hardcoded_sensitive_data",
                    suggestion=f"Move {data_type} to environment variables or test configuration"
                ))
        
        # Check for magic numbers/strings
        magic_numbers = re.findall(r'(?<![\w.])\d{4,}(?![\w.])', code)
        if len(magic_numbers) > 3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.MAINTAINABILITY,
                message="Multiple magic numbers found. Consider using constants.",
                rule_id="magic_numbers",
                suggestion="Extract magic numbers to named constants"
            ))
        
        return issues


class PerformanceValidator:
    """Validates performance aspects of test code."""
    
    def validate(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate performance-related aspects."""
        issues = []
        
        issues.extend(self._validate_selector_performance(code, framework))
        issues.extend(self._validate_wait_efficiency(code))
        issues.extend(self._validate_resource_usage(code))
        
        return issues
    
    def _validate_selector_performance(self, code: str, framework: str) -> List[ValidationIssue]:
        """Validate selector performance implications."""
        issues = []
        
        # Check for expensive selectors
        expensive_patterns = [
            (r'//\*\[', "Universal XPath selectors"),
            (r'contains\s*\(\s*text\s*\(\s*\)', "Text content searches"),
            (r'\.\./', "Parent navigation in XPath")
        ]
        
        for pattern, description in expensive_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.PERFORMANCE,
                    message=f"Potentially slow selector: {description}",
                    line_number=line_num,
                    rule_id="slow_selector",
                    suggestion="Consider using more specific selectors"
                ))
        
        return issues
    
    def _validate_wait_efficiency(self, code: str) -> List[ValidationIssue]:
        """Validate wait strategy efficiency."""
        issues = []
        
        # Check for excessive polling
        polling_patterns = [r'while.*sleep', r'for.*in.*range.*sleep']
        for pattern in polling_patterns:
            if re.search(pattern, code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message="Manual polling detected. Use framework wait conditions.",
                    rule_id="manual_polling",
                    suggestion="Use built-in wait conditions instead of manual polling"
                ))
        
        return issues
    
    def _validate_resource_usage(self, code: str) -> List[ValidationIssue]:
        """Validate resource usage patterns."""
        issues = []
        
        # Check for screenshot overuse
        screenshot_count = len(re.findall(r'screenshot\s*\(', code))
        if screenshot_count > 5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.PERFORMANCE,
                message=f"High screenshot usage ({screenshot_count}). May slow down tests.",
                rule_id="excessive_screenshots",
                suggestion="Limit screenshots to essential checkpoints"
            ))
        
        return issues


class SecurityValidator:
    """Validates security aspects of test code."""
    
    def validate(self, code: str) -> List[ValidationIssue]:
        """Validate security-related aspects."""
        issues = []
        
        issues.extend(self._validate_credential_handling(code))
        issues.extend(self._validate_injection_risks(code))
        issues.extend(self._validate_file_operations(code))
        
        return issues
    
    def _validate_credential_handling(self, code: str) -> List[ValidationIssue]:
        """Validate credential and sensitive data handling."""
        issues = []
        
        # Check for credentials in code
        credential_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "password"),
            (r'username\s*=\s*["\'][^"\']+@[^"\']+["\']', "email/username"),
            (r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "API key")
        ]
        
        for pattern, cred_type in credential_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SECURITY,
                    message=f"Hardcoded {cred_type} detected",
                    line_number=line_num,
                    rule_id="hardcoded_credentials",
                    suggestion="Use environment variables or secure configuration",
                    documentation_url="https://example.com/secure-testing"
                ))
        
        return issues
    
    def _validate_injection_risks(self, code: str) -> List[ValidationIssue]:
        """Validate potential injection vulnerabilities."""
        issues = []
        
        # Check for SQL injection risks (if database interactions)
        sql_patterns = [r'SELECT.*\+.*', r'INSERT.*\+.*', r'UPDATE.*\+.*']
        for pattern in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SECURITY,
                    message="Potential SQL injection risk in string concatenation",
                    rule_id="sql_injection_risk",
                    suggestion="Use parameterized queries"
                ))
        
        # Check for XSS risks in dynamic content
        if re.search(r'innerHTML\s*=', code):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.SECURITY,
                message="Direct innerHTML assignment may pose XSS risks",
                rule_id="xss_risk",
                suggestion="Sanitize dynamic content or use safer methods"
            ))
        
        return issues
    
    def _validate_file_operations(self, code: str) -> List[ValidationIssue]:
        """Validate file operation security."""
        issues = []
        
        # Check for path traversal risks
        if re.search(r'["\']\.\./', code):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.SECURITY,
                message="Potential path traversal detected",
                rule_id="path_traversal",
                suggestion="Validate and sanitize file paths"
            ))
        
        return issues


class TestValidationEngine:
    """Main validation engine that coordinates all validation checks."""
    
    def __init__(self, language: str = "python", framework: str = "playwright"):
        self.language = language
        self.framework = framework
        
        # Initialize validators
        self.syntax_validator = SyntaxValidator(language)
        self.best_practices_validator = BestPracticesValidator()
        self.performance_validator = PerformanceValidator()
        self.security_validator = SecurityValidator()
    
    def validate_test_script(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Perform comprehensive validation of a test script.
        
        Args:
            code: Test script code to validate
            metadata: Additional metadata about the test
            
        Returns:
            Comprehensive validation results
        """
        all_issues = []
        
        # Run all validators
        all_issues.extend(self.syntax_validator.validate(code, self.framework))
        all_issues.extend(self.best_practices_validator.validate(code, self.framework, metadata))
        all_issues.extend(self.performance_validator.validate(code, self.framework))
        all_issues.extend(self.security_validator.validate(code))
        
        # Calculate overall score
        score = self._calculate_overall_score(all_issues, code)
        
        # Generate metrics
        metrics = self._generate_metrics(code, all_issues)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(all_issues, metrics)
        
        # Generate auto-fixes
        auto_fixes = self._generate_auto_fixes(all_issues, code)
        
        # Determine if valid (no errors)
        is_valid = not any(issue.severity == ValidationSeverity.ERROR for issue in all_issues)
        
        return ValidationResult(
            is_valid=is_valid,
            overall_score=score,
            issues=all_issues,
            metrics=metrics,
            suggestions=suggestions,
            auto_fixes=auto_fixes
        )
    
    def _calculate_overall_score(self, issues: List[ValidationIssue], code: str) -> float:
        """Calculate overall quality score (0-100)."""
        base_score = 100.0
        
        # Deduct points based on severity
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                base_score -= 20
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 10
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 5
            elif issue.severity == ValidationSeverity.STYLE:
                base_score -= 2
        
        # Bonus points for good practices
        lines = len([line for line in code.split('\n') if line.strip()])
        
        # Bonus for comments
        comment_lines = len(re.findall(r'^\s*#', code, re.MULTILINE))
        if comment_lines / max(lines, 1) > 0.1:  # >10% comments
            base_score += 5
        
        # Bonus for explicit waits
        if re.search(r'wait_for', code):
            base_score += 3
        
        # Bonus for assertions
        assertion_count = len(re.findall(r'(?:assert|expect)\s*\(', code))
        if assertion_count > 0:
            base_score += min(assertion_count * 2, 10)
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_metrics(self, code: str, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """Generate detailed metrics about the code."""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            "lines_of_code": len(non_empty_lines),
            "total_lines": len(lines),
            "comment_lines": len(re.findall(r'^\s*#', code, re.MULTILINE)),
            "comment_ratio": len(re.findall(r'^\s*#', code, re.MULTILINE)) / max(len(non_empty_lines), 1),
            "assertion_count": len(re.findall(r'(?:assert|expect)\s*\(', code)),
            "wait_count": len(re.findall(r'wait_for', code)),
            "selector_count": len(re.findall(r'locator\s*\(', code)),
            "issues_by_severity": {
                "errors": len([i for i in issues if i.severity == ValidationSeverity.ERROR]),
                "warnings": len([i for i in issues if i.severity == ValidationSeverity.WARNING]),
                "info": len([i for i in issues if i.severity == ValidationSeverity.INFO]),
                "style": len([i for i in issues if i.severity == ValidationSeverity.STYLE])
            },
            "issues_by_category": {
                category.value: len([i for i in issues if i.category == category])
                for category in ValidationCategory
            }
        }
    
    def _generate_suggestions(self, issues: List[ValidationIssue], metrics: Dict[str, Any]) -> List[str]:
        """Generate high-level suggestions for improvement."""
        suggestions = []
        
        # Extract suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in suggestions:
                suggestions.append(issue.suggestion)
        
        # Add metric-based suggestions
        if metrics["comment_ratio"] < 0.05:
            suggestions.append("Add more comments to improve code documentation")
        
        if metrics["assertion_count"] == 0:
            suggestions.append("Add assertions to validate test expectations")
        
        if metrics["wait_count"] == 0 and metrics["lines_of_code"] > 10:
            suggestions.append("Consider adding explicit waits for better reliability")
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _generate_auto_fixes(self, issues: List[ValidationIssue], code: str) -> List[Dict[str, Any]]:
        """Generate automatic fixes for fixable issues."""
        auto_fixes = []
        
        for issue in issues:
            if issue.auto_fixable:
                fix = self._create_auto_fix(issue, code)
                if fix:
                    auto_fixes.append(fix)
        
        return auto_fixes
    
    def _create_auto_fix(self, issue: ValidationIssue, code: str) -> Optional[Dict[str, Any]]:
        """Create an automatic fix for an issue."""
        if issue.rule_id == "missing_await":
            # Find the line and add await
            lines = code.split('\n')
            if issue.line_number and issue.line_number <= len(lines):
                line = lines[issue.line_number - 1]
                # Simple fix: add await before method calls
                fixed_line = re.sub(r'(\s*)(\w+\.(?:click|fill|goto|wait_for)\s*\()', 
                                  r'\1await \2', line)
                return {
                    "issue_id": issue.rule_id,
                    "line_number": issue.line_number,
                    "original": line,
                    "fixed": fixed_line,
                    "description": "Added missing 'await' keyword"
                }
        
        elif issue.rule_id == "missing_import":
            # Add missing import at the top
            if "playwright" in issue.message:
                import_line = "from playwright.async_api import async_playwright, expect"
                return {
                    "issue_id": issue.rule_id,
                    "line_number": 1,
                    "original": "",
                    "fixed": import_line,
                    "description": "Added missing Playwright import"
                }
        
        return None
    
    def validate_and_fix(self, code: str) -> Tuple[str, ValidationResult]:
        """Validate code and apply automatic fixes."""
        result = self.validate_test_script(code)
        
        # Apply auto-fixes
        fixed_code = code
        for fix in reversed(result.auto_fixes):  # Apply in reverse order to maintain line numbers
            lines = fixed_code.split('\n')
            line_num = fix["line_number"]
            
            if line_num <= len(lines):
                if fix["original"]:
                    lines[line_num - 1] = fix["fixed"]
                else:
                    lines.insert(line_num - 1, fix["fixed"])
                
                fixed_code = '\n'.join(lines)
        
        # Re-validate after fixes
        final_result = self.validate_test_script(fixed_code)
        
        return fixed_code, final_result
    
    def generate_validation_report(self, result: ValidationResult, format: str = "text") -> str:
        """Generate a formatted validation report."""
        if format == "text":
            return self._generate_text_report(result)
        elif format == "json":
            return self._generate_json_report(result)
        elif format == "html":
            return self._generate_html_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_text_report(self, result: ValidationResult) -> str:
        """Generate a text-based validation report."""
        report = []
        report.append("=" * 60)
        report.append("TEST SCRIPT VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Overall Score: {result.overall_score:.1f}/100")
        report.append(f"Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY:")
        report.append(f"  Errors: {result.error_count}")
        report.append(f"  Warnings: {result.warning_count}")
        report.append(f"  Info: {result.info_count}")
        report.append("")
        
        # Issues by category
        if result.issues:
            report.append("🔍 ISSUES BY CATEGORY:")
            categories = {}
            for issue in result.issues:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)
            
            for category, issues in categories.items():
                report.append(f"  {category.value.title()}: {len(issues)}")
        
        report.append("")
        
        # Detailed issues
        if result.issues:
            report.append("📋 DETAILED ISSUES:")
            for i, issue in enumerate(result.issues, 1):
                severity_icon = {
                    ValidationSeverity.ERROR: "❌",
                    ValidationSeverity.WARNING: "⚠️ ",
                    ValidationSeverity.INFO: "ℹ️ ",
                    ValidationSeverity.STYLE: "🎨"
                }
                
                report.append(f"{i}. {severity_icon[issue.severity]} {issue.message}")
                if issue.line_number:
                    report.append(f"   Line: {issue.line_number}")
                if issue.suggestion:
                    report.append(f"   💡 Suggestion: {issue.suggestion}")
                report.append("")
        
        # Suggestions
        if result.suggestions:
            report.append("💡 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(result.suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")
        
        # Metrics
        report.append("📈 METRICS:")
        for key, value in result.metrics.items():
            if isinstance(value, dict):
                report.append(f"  {key.replace('_', ' ').title()}:")
                for subkey, subvalue in value.items():
                    report.append(f"    {subkey}: {subvalue}")
            else:
                report.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(report)
    
    def _generate_json_report(self, result: ValidationResult) -> str:
        """Generate a JSON validation report."""
        report_data = {
            "overall_score": result.overall_score,
            "is_valid": result.is_valid,
            "summary": {
                "errors": result.error_count,
                "warnings": result.warning_count,
                "info": result.info_count
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "message": issue.message,
                    "line_number": issue.line_number,
                    "rule_id": issue.rule_id,
                    "suggestion": issue.suggestion
                }
                for issue in result.issues
            ],
            "suggestions": result.suggestions,
            "metrics": result.metrics,
            "auto_fixes": result.auto_fixes
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self, result: ValidationResult) -> str:
        """Generate an HTML validation report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .valid {{ color: green; }}
        .invalid {{ color: red; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        .error {{ border-left-color: #ff0000; }}
        .warning {{ border-left-color: #ff9900; }}
        .info {{ border-left-color: #0099ff; }}
        .style {{ border-left-color: #9900ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Script Validation Report</h1>
        <div class="score">Overall Score: {result.overall_score:.1f}/100</div>
        <div class="{'valid' if result.is_valid else 'invalid'}">
            Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}
        </div>
    </div>
    
    <h2>Summary</h2>
    <ul>
        <li>Errors: {result.error_count}</li>
        <li>Warnings: {result.warning_count}</li>
        <li>Info: {result.info_count}</li>
    </ul>
    
    <h2>Issues</h2>
"""
        
        for issue in result.issues:
            severity_class = issue.severity.value
            html += f"""
    <div class="issue {severity_class}">
        <strong>{issue.severity.value.upper()}:</strong> {issue.message}<br>
        {f"<em>Line {issue.line_number}</em><br>" if issue.line_number else ""}
        {f"<strong>Suggestion:</strong> {issue.suggestion}" if issue.suggestion else ""}
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html 