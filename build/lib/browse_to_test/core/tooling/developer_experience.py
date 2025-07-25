"""
Developer Experience Enhancement System

This module provides comprehensive developer experience tools including
debugging utilities, intelligent error handling, test preview capabilities,
and interactive development features.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import json
import re
import sys
import traceback
import inspect
from pathlib import Path
from datetime import datetime
import subprocess
import webbrowser
import tempfile


class DebugLevel(Enum):
    """Debug output levels."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PreviewMode(Enum):
    """Test preview modes."""
    INTERACTIVE = "interactive"
    STATIC = "static"
    STEP_BY_STEP = "step_by_step"
    VISUAL = "visual"


class ErrorCategory(Enum):
    """Error categories for intelligent error handling."""
    SELECTOR_NOT_FOUND = "selector_not_found"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    ASSERTION_FAILED = "assertion_failed"
    CONFIGURATION_ERROR = "configuration_error"
    DATA_ERROR = "data_error"
    FRAMEWORK_ERROR = "framework_error"
    SYNTAX_ERROR = "syntax_error"


@dataclass
class DebugStep:
    """Individual debug step information."""
    step_number: int
    action: str
    element: Dict[str, Any]
    timestamp: datetime
    duration: float
    success: bool
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    page_source: Optional[str] = None
    network_requests: List[Dict] = field(default_factory=list)
    console_logs: List[str] = field(default_factory=list)


@dataclass
class ErrorContext:
    """Comprehensive error context for debugging."""
    error_type: ErrorCategory
    original_error: str
    suggestions: List[str]
    related_docs: List[str]
    auto_fix_available: bool
    context_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreviewConfig:
    """Configuration for test preview."""
    mode: PreviewMode
    show_selectors: bool = True
    highlight_elements: bool = True
    show_timings: bool = True
    enable_breakpoints: bool = True
    auto_scroll: bool = True
    capture_screenshots: bool = True


class IntelligentErrorHandler:
    """Provides intelligent error analysis and suggestions."""
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.suggestion_database = self._load_suggestions()
    
    def analyze_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """Analyze an error and provide intelligent suggestions."""
        error_str = str(error)
        error_type = self._categorize_error(error, error_str)
        
        suggestions = self._generate_suggestions(error_type, error_str, context)
        docs = self._get_related_documentation(error_type)
        auto_fix = self._can_auto_fix(error_type, error_str)
        
        return ErrorContext(
            error_type=error_type,
            original_error=error_str,
            suggestions=suggestions,
            related_docs=docs,
            auto_fix_available=auto_fix,
            context_data=context
        )
    
    def _categorize_error(self, error: Exception, error_str: str) -> ErrorCategory:
        """Categorize the error type."""
        if "NoSuchElementException" in str(type(error)) or "not found" in error_str.lower():
            return ErrorCategory.SELECTOR_NOT_FOUND
        elif "timeout" in error_str.lower() or "TimeoutException" in str(type(error)):
            return ErrorCategory.TIMEOUT
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            return ErrorCategory.NETWORK_ERROR
        elif "assertion" in error_str.lower() or "expected" in error_str.lower():
            return ErrorCategory.ASSERTION_FAILED
        elif "config" in error_str.lower() or "configuration" in error_str.lower():
            return ErrorCategory.CONFIGURATION_ERROR
        elif "SyntaxError" in str(type(error)):
            return ErrorCategory.SYNTAX_ERROR
        else:
            return ErrorCategory.FRAMEWORK_ERROR
    
    def _generate_suggestions(self, error_type: ErrorCategory, error_str: str, context: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions based on error type."""
        suggestions = []
        
        if error_type == ErrorCategory.SELECTOR_NOT_FOUND:
            suggestions.extend([
                "🔍 Verify the element exists on the page",
                "⏱️ Add explicit wait for element to be present",
                "🎯 Try using a more robust selector (data-testid, aria-label)",
                "📱 Check if element is in a different frame or window",
                "🔄 Element might be dynamically loaded - wait for it",
                "🎭 Use browser dev tools to inspect and copy selector"
            ])
            
            # Extract selector from error message
            selector_match = re.search(r'selector["\s]*[:=]["\s]*([^"]+)', error_str)
            if selector_match:
                selector = selector_match.group(1)
                suggestions.append(f"💡 Suggested alternative: Try CSS selector with contains() or XPath")
        
        elif error_type == ErrorCategory.TIMEOUT:
            suggestions.extend([
                "⏰ Increase timeout value if operation takes longer",
                "🔄 Use explicit waits instead of implicit waits",
                "🚀 Check if page is fully loaded before interaction",
                "🌐 Verify network connectivity and page load speed",
                "📱 Consider if mobile viewport affects element visibility"
            ])
        
        elif error_type == ErrorCategory.ASSERTION_FAILED:
            suggestions.extend([
                "📊 Check if expected value matches actual value format",
                "🔤 Verify text content doesn't have extra whitespace",
                "🎯 Use contains() instead of exact match if appropriate",
                "⏱️ Wait for dynamic content to load before assertion",
                "🎭 Use debugging tools to inspect actual values"
            ])
        
        elif error_type == ErrorCategory.NETWORK_ERROR:
            suggestions.extend([
                "🌐 Check internet connectivity",
                "🔗 Verify the target URL is accessible",
                "🛡️ Check if VPN or firewall is blocking requests",
                "⏱️ Increase network timeout settings",
                "🔄 Implement retry logic for network operations"
            ])
        
        # Add context-specific suggestions
        if context.get("framework") == "playwright":
            suggestions.append("🎭 Use page.pause() to debug interactively")
        elif context.get("framework") == "selenium":
            suggestions.append("🔍 Use driver.save_screenshot() to capture current state")
        
        return suggestions
    
    def _get_related_documentation(self, error_type: ErrorCategory) -> List[str]:
        """Get related documentation links."""
        docs = {
            ErrorCategory.SELECTOR_NOT_FOUND: [
                "https://playwright.dev/docs/locators",
                "https://selenium-python.readthedocs.io/waits.html"
            ],
            ErrorCategory.TIMEOUT: [
                "https://playwright.dev/docs/actionability",
                "https://selenium-python.readthedocs.io/waits.html"
            ],
            ErrorCategory.ASSERTION_FAILED: [
                "https://playwright.dev/docs/test-assertions",
                "https://docs.pytest.org/en/stable/assert.html"
            ]
        }
        return docs.get(error_type, [])
    
    def _can_auto_fix(self, error_type: ErrorCategory, error_str: str) -> bool:
        """Determine if error can be automatically fixed."""
        auto_fixable = {
            ErrorCategory.SELECTOR_NOT_FOUND: True,
            ErrorCategory.TIMEOUT: True,
            ErrorCategory.SYNTAX_ERROR: False,
            ErrorCategory.CONFIGURATION_ERROR: True
        }
        return auto_fixable.get(error_type, False)
    
    def _load_error_patterns(self) -> Dict[str, str]:
        """Load error pattern database."""
        return {
            "element_not_found": r"(NoSuchElementException|Element not found|Could not find)",
            "timeout": r"(TimeoutException|timeout|timed out)",
            "stale_element": r"(StaleElementReferenceException|stale element)",
            "invalid_selector": r"(InvalidSelectorException|invalid selector)"
        }
    
    def _load_suggestions(self) -> Dict[str, List[str]]:
        """Load suggestion database."""
        return {
            "common_fixes": [
                "Add explicit waits",
                "Use more robust selectors",
                "Check element visibility",
                "Verify page load state"
            ]
        }


class InteractiveDebugger:
    """Interactive debugging tools for test development."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.debug_session = []
        self.breakpoints = set()
        self.current_step = 0
        
    def start_debug_session(self, test_name: str) -> None:
        """Start a new debug session."""
        self.debug_session = []
        self.current_step = 0
        print(f"🐛 Debug session started for: {test_name}")
        print("Available commands:")
        print("  - 'n' or 'next': Execute next step")
        print("  - 'c' or 'continue': Continue execution")
        print("  - 'b <step>': Set breakpoint at step")
        print("  - 'p <var>': Print variable value")
        print("  - 's' or 'screenshot': Take screenshot")
        print("  - 'q' or 'quit': Stop debugging")
    
    def add_debug_step(self, step: DebugStep) -> None:
        """Add a step to the debug session."""
        self.debug_session.append(step)
        
        if step.step_number in self.breakpoints or self.config.get("step_by_step", False):
            self._pause_execution(step)
    
    def _pause_execution(self, step: DebugStep) -> None:
        """Pause execution for interactive debugging."""
        print(f"\n🔍 Paused at step {step.step_number}: {step.action}")
        print(f"⏱️  Duration: {step.duration:.2f}s")
        print(f"✅ Success: {step.success}")
        
        if step.error_message:
            print(f"❌ Error: {step.error_message}")
        
        while True:
            command = input("debug> ").strip().lower()
            
            if command in ['n', 'next', 'c', 'continue']:
                break
            elif command.startswith('b '):
                try:
                    breakpoint_step = int(command.split(' ')[1])
                    self.breakpoints.add(breakpoint_step)
                    print(f"✓ Breakpoint set at step {breakpoint_step}")
                except ValueError:
                    print("❌ Invalid step number")
            elif command in ['s', 'screenshot']:
                if step.screenshot_path:
                    print(f"📸 Screenshot: {step.screenshot_path}")
                else:
                    print("📸 No screenshot available for this step")
            elif command.startswith('p '):
                var_name = command.split(' ')[1]
                self._print_variable(var_name, step)
            elif command in ['q', 'quit']:
                print("🛑 Debug session terminated")
                sys.exit(0)
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def _print_variable(self, var_name: str, step: DebugStep) -> None:
        """Print variable value during debugging."""
        if var_name == "element":
            print(f"Element: {json.dumps(step.element, indent=2)}")
        elif var_name == "action":
            print(f"Action: {step.action}")
        elif var_name == "logs":
            print("Console logs:")
            for log in step.console_logs:
                print(f"  {log}")
        else:
            print(f"❌ Unknown variable: {var_name}")
    
    def generate_debug_report(self, output_path: Path) -> str:
        """Generate a comprehensive debug report."""
        report = {
            "session_info": {
                "total_steps": len(self.debug_session),
                "successful_steps": len([s for s in self.debug_session if s.success]),
                "failed_steps": len([s for s in self.debug_session if not s.success]),
                "total_duration": sum(s.duration for s in self.debug_session)
            },
            "steps": []
        }
        
        for step in self.debug_session:
            step_data = {
                "step_number": step.step_number,
                "action": step.action,
                "duration": step.duration,
                "success": step.success,
                "timestamp": step.timestamp.isoformat(),
                "element": step.element
            }
            
            if step.error_message:
                step_data["error"] = step.error_message
            if step.screenshot_path:
                step_data["screenshot"] = step.screenshot_path
            if step.console_logs:
                step_data["console_logs"] = step.console_logs
            
            report["steps"].append(step_data)
        
        report_file = output_path / f"debug-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)


class TestPreviewGenerator:
    """Generates interactive test previews."""
    
    def __init__(self, config: PreviewConfig):
        self.config = config
        
    def generate_preview(self, test_data: Dict[str, Any], output_dir: Path) -> str:
        """Generate an interactive test preview."""
        if self.config.mode == PreviewMode.INTERACTIVE:
            return self._generate_interactive_preview(test_data, output_dir)
        elif self.config.mode == PreviewMode.VISUAL:
            return self._generate_visual_preview(test_data, output_dir)
        else:
            return self._generate_static_preview(test_data, output_dir)
    
    def _generate_interactive_preview(self, test_data: Dict[str, Any], output_dir: Path) -> str:
        """Generate interactive HTML preview."""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Browse-to-Test Preview</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 8px 8px 0 0; 
        }
        .controls { 
            padding: 20px; 
            background: #fafafa; 
            border-bottom: 1px solid #eee; 
        }
        .step { 
            padding: 15px 20px; 
            border-bottom: 1px solid #eee; 
            transition: background 0.2s; 
        }
        .step:hover { background: #f8f9fa; }
        .step.active { background: #e3f2fd; border-left: 4px solid #2196f3; }
        .step-number { 
            display: inline-block; 
            width: 30px; 
            height: 30px; 
            background: #2196f3; 
            color: white; 
            border-radius: 50%; 
            text-align: center; 
            line-height: 30px; 
            margin-right: 15px; 
        }
        .step-action { font-weight: 600; }
        .step-details { color: #666; margin-top: 5px; font-size: 14px; }
        .element-info { 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 4px; 
            margin-top: 10px; 
            font-family: monospace; 
        }
        .controls button { 
            background: #2196f3; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            margin-right: 10px; 
            cursor: pointer; 
        }
        .controls button:hover { background: #1976d2; }
        .controls button:disabled { background: #ccc; cursor: not-allowed; }
        .timeline { 
            position: fixed; 
            right: 20px; 
            top: 50%; 
            transform: translateY(-50%); 
            width: 4px; 
            background: #eee; 
            height: 300px; 
            border-radius: 2px; 
        }
        .timeline-progress { 
            background: #2196f3; 
            width: 100%; 
            border-radius: 2px; 
            transition: height 0.3s; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Test Preview</h1>
            <p>Interactive preview of your automated test</p>
        </div>
        
        <div class="controls">
            <button onclick="playTest()">▶️ Play</button>
            <button onclick="pauseTest()">⏸️ Pause</button>
            <button onclick="stepForward()">⏭️ Step Forward</button>
            <button onclick="stepBackward()">⏮️ Step Backward</button>
            <button onclick="resetTest()">🔄 Reset</button>
            <span style="margin-left: 20px;">Speed: 
                <select onchange="setSpeed(this.value)">
                    <option value="1">1x</option>
                    <option value="0.5">0.5x</option>
                    <option value="2" selected>2x</option>
                    <option value="5">5x</option>
                </select>
            </span>
        </div>
        
        <div id="steps-container">
        </div>
    </div>
    
    <div class="timeline">
        <div class="timeline-progress" id="timeline-progress"></div>
    </div>

    <script>
        let currentStep = 0;
        let isPlaying = false;
        let playbackSpeed = 2;
        
        const testSteps = """ + json.dumps(test_data.get("steps", [])) + """;
        
        function renderSteps() {
            const container = document.getElementById('steps-container');
            container.innerHTML = '';
            
            testSteps.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'step';
                stepDiv.id = `step-${index}`;
                
                stepDiv.innerHTML = `
                    <div>
                        <span class="step-number">${index + 1}</span>
                        <span class="step-action">${step.action || 'Unknown Action'}</span>
                    </div>
                    <div class="step-details">
                        ${step.description || 'No description available'}
                    </div>
                    ${step.element ? `<div class="element-info">Element: ${JSON.stringify(step.element, null, 2)}</div>` : ''}
                `;
                
                container.appendChild(stepDiv);
            });
            
            updateCurrentStep();
        }
        
        function updateCurrentStep() {
            document.querySelectorAll('.step').forEach((el, index) => {
                el.classList.toggle('active', index === currentStep);
            });
            
            const progress = (currentStep / Math.max(testSteps.length - 1, 1)) * 100;
            document.getElementById('timeline-progress').style.height = progress + '%';
        }
        
        function playTest() {
            if (isPlaying) return;
            isPlaying = true;
            
            const interval = setInterval(() => {
                if (!isPlaying || currentStep >= testSteps.length - 1) {
                    clearInterval(interval);
                    isPlaying = false;
                    return;
                }
                
                stepForward();
            }, 1000 / playbackSpeed);
        }
        
        function pauseTest() {
            isPlaying = false;
        }
        
        function stepForward() {
            if (currentStep < testSteps.length - 1) {
                currentStep++;
                updateCurrentStep();
            }
        }
        
        function stepBackward() {
            if (currentStep > 0) {
                currentStep--;
                updateCurrentStep();
            }
        }
        
        function resetTest() {
            currentStep = 0;
            isPlaying = false;
            updateCurrentStep();
        }
        
        function setSpeed(speed) {
            playbackSpeed = parseFloat(speed);
        }
        
        // Initialize
        renderSteps();
    </script>
</body>
</html>
        """
        
        preview_file = output_dir / "test-preview.html"
        with open(preview_file, 'w') as f:
            f.write(html_content)
        
        return str(preview_file)
    
    def _generate_visual_preview(self, test_data: Dict[str, Any], output_dir: Path) -> str:
        """Generate visual flow diagram preview."""
        # This would integrate with a diagram library to create visual flow
        pass
    
    def _generate_static_preview(self, test_data: Dict[str, Any], output_dir: Path) -> str:
        """Generate static markdown preview."""
        markdown_content = "# Test Preview\n\n"
        
        steps = test_data.get("steps", [])
        for i, step in enumerate(steps, 1):
            markdown_content += f"## Step {i}: {step.get('action', 'Unknown')}\n\n"
            
            if step.get('description'):
                markdown_content += f"**Description:** {step['description']}\n\n"
            
            if step.get('element'):
                markdown_content += f"**Element:** `{step['element']}`\n\n"
            
            markdown_content += "---\n\n"
        
        preview_file = output_dir / "test-preview.md"
        with open(preview_file, 'w') as f:
            f.write(markdown_content)
        
        return str(preview_file)


class IDEIntegration:
    """IDE integration utilities."""
    
    @staticmethod
    def generate_vscode_settings() -> Dict[str, Any]:
        """Generate VS Code settings for optimal browse-to-test development."""
        return {
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.pytestArgs": ["tests/"],
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "python.formatting.provider": "black",
            "files.associations": {
                "*.test.py": "python"
            },
            "emmet.includeLanguages": {
                "python": "html"
            },
            "browse-to-test": {
                "debug.enableStepThrough": True,
                "preview.autoOpen": True,
                "suggestions.enabled": True
            }
        }
    
    @staticmethod
    def generate_debug_config() -> Dict[str, Any]:
        """Generate debug configuration for IDEs."""
        return {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Debug Browse-to-Test",
                    "type": "python",
                    "request": "launch",
                    "module": "browse_to_test",
                    "args": ["--debug", "--step-by-step"],
                    "console": "integratedTerminal",
                    "env": {
                        "BROWSE_TO_TEST_DEBUG": "1"
                    }
                },
                {
                    "name": "Debug Test Generation",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/debug_test_generation.py",
                    "args": ["${file}"],
                    "console": "integratedTerminal"
                }
            ]
        }


class SmartSuggestionEngine:
    """Provides intelligent code completion and suggestions."""
    
    def __init__(self):
        self.suggestion_cache = {}
        
    def get_selector_suggestions(self, partial_selector: str, context: Dict[str, Any]) -> List[str]:
        """Get intelligent selector suggestions."""
        suggestions = []
        
        # Common selector patterns
        if partial_selector.startswith('['):
            suggestions.extend([
                '[data-testid=""]',
                '[aria-label=""]',
                '[role="button"]',
                '[type="submit"]'
            ])
        elif partial_selector.startswith('#'):
            suggestions.extend([
                '#submit-button',
                '#login-form',
                '#user-profile'
            ])
        elif partial_selector.startswith('.'):
            suggestions.extend([
                '.btn-primary',
                '.form-control',
                '.navigation-menu'
            ])
        
        # Framework-specific suggestions
        framework = context.get('framework', '')
        if framework == 'playwright':
            suggestions.extend([
                'page.getByRole("button")',
                'page.getByTestId("")',
                'page.getByLabel("")',
                'page.getByText("")'
            ])
        
        return suggestions
    
    def get_action_suggestions(self, element_type: str) -> List[str]:
        """Get action suggestions based on element type."""
        suggestions = {
            'button': ['click', 'hover', 'focus'],
            'input': ['fill', 'type', 'clear', 'focus'],
            'select': ['select_option', 'click'],
            'link': ['click', 'hover'],
            'checkbox': ['check', 'uncheck', 'click'],
            'radio': ['check', 'click']
        }
        
        return suggestions.get(element_type, ['click', 'hover'])
    
    def get_assertion_suggestions(self, element_info: Dict[str, Any]) -> List[str]:
        """Get assertion suggestions based on element."""
        suggestions = []
        
        if element_info.get('tag') == 'input':
            suggestions.extend([
                'expect(element).toHaveValue("")',
                'expect(element).toBeVisible()',
                'expect(element).toBeFocused()'
            ])
        elif element_info.get('tag') == 'button':
            suggestions.extend([
                'expect(element).toBeEnabled()',
                'expect(element).toBeVisible()',
                'expect(element).toHaveText("")'
            ])
        
        return suggestions


class DevToolsIntegration:
    """Integration with browser dev tools."""
    
    @staticmethod
    def capture_element_info(page_source: str, selector: str) -> Dict[str, Any]:
        """Capture detailed element information from page source."""
        # This would parse HTML and extract element information
        return {
            "selector": selector,
            "tag": "button",
            "attributes": {},
            "text_content": "",
            "computed_styles": {}
        }
    
    @staticmethod
    def generate_selector_alternatives(element_info: Dict[str, Any]) -> List[str]:
        """Generate alternative selectors for an element."""
        alternatives = []
        
        if element_info.get('attributes', {}).get('data-testid'):
            alternatives.append(f"[data-testid='{element_info['attributes']['data-testid']}']")
        
        if element_info.get('attributes', {}).get('id'):
            alternatives.append(f"#{element_info['attributes']['id']}")
        
        if element_info.get('attributes', {}).get('class'):
            classes = element_info['attributes']['class'].split()
            alternatives.append(f".{'.'.join(classes)}")
        
        return alternatives


class PerformanceProfiler:
    """Profiles test execution performance."""
    
    def __init__(self):
        self.metrics = {}
        
    def start_profiling(self, test_name: str) -> None:
        """Start profiling a test."""
        self.metrics[test_name] = {
            "start_time": datetime.now(),
            "steps": [],
            "network_requests": [],
            "memory_usage": []
        }
    
    def record_step(self, test_name: str, step_info: Dict[str, Any]) -> None:
        """Record step performance metrics."""
        if test_name in self.metrics:
            self.metrics[test_name]["steps"].append({
                "timestamp": datetime.now(),
                "duration": step_info.get("duration", 0),
                "action": step_info.get("action", ""),
                "selector_time": step_info.get("selector_time", 0),
                "wait_time": step_info.get("wait_time", 0)
            })
    
    def generate_performance_report(self, test_name: str) -> Dict[str, Any]:
        """Generate performance analysis report."""
        if test_name not in self.metrics:
            return {"error": "No profiling data available"}
        
        data = self.metrics[test_name]
        total_duration = (datetime.now() - data["start_time"]).total_seconds()
        
        step_durations = [step["duration"] for step in data["steps"]]
        avg_step_duration = sum(step_durations) / len(step_durations) if step_durations else 0
        
        return {
            "test_name": test_name,
            "total_duration": total_duration,
            "total_steps": len(data["steps"]),
            "average_step_duration": avg_step_duration,
            "slowest_steps": sorted(data["steps"], key=lambda x: x["duration"], reverse=True)[:5],
            "performance_score": self._calculate_performance_score(data),
            "recommendations": self._generate_performance_recommendations(data)
        }
    
    def _calculate_performance_score(self, data: Dict[str, Any]) -> float:
        """Calculate performance score (0-100)."""
        # Basic scoring algorithm
        step_durations = [step["duration"] for step in data["steps"]]
        if not step_durations:
            return 100.0
        
        avg_duration = sum(step_durations) / len(step_durations)
        
        # Score based on average step duration (lower is better)
        if avg_duration < 1.0:
            return 100.0
        elif avg_duration < 3.0:
            return 80.0
        elif avg_duration < 5.0:
            return 60.0
        else:
            return 40.0
    
    def _generate_performance_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        step_durations = [step["duration"] for step in data["steps"]]
        if step_durations:
            avg_duration = sum(step_durations) / len(step_durations)
            
            if avg_duration > 3.0:
                recommendations.append("🐌 Consider optimizing slow selectors")
                recommendations.append("⚡ Use more specific selectors to reduce search time")
            
            slow_steps = [step for step in data["steps"] if step["duration"] > 5.0]
            if slow_steps:
                recommendations.append(f"🔍 {len(slow_steps)} steps are taking longer than 5 seconds")
        
        return recommendations 