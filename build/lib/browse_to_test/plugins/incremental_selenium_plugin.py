"""
Incremental Selenium plugin for generating Python test scripts with live updates.

Extends the base SeleniumPlugin to support incremental script generation with
setup, incremental step addition, and finalization phases.
"""

import logging
from typing import Any, Dict, List, Optional

from .selenium_plugin import SeleniumPlugin
from .base import GeneratedTestScript, PluginError
from ..core.configuration.config import OutputConfig
from ..core.processing.input_parser import ParsedAutomationData, ParsedAction, ParsedStep


logger = logging.getLogger(__name__)


class IncrementalSeleniumPlugin(SeleniumPlugin):
    """Incremental Selenium plugin for live test script generation."""
    
    def __init__(self, config: OutputConfig):
        """Initialize the incremental Selenium plugin."""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    @property
    def plugin_name(self) -> str:
        """Return the plugin name."""
        return "incremental_selenium"
    
    def setup_incremental_script(
        self,
        target_url: Optional[str] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Set up incremental Selenium script generation.
        
        Creates the basic script structure with imports, helpers, and browser setup.
        """
        try:
            self.logger.debug("Setting up incremental Selenium script")
            
            # Generate imports
            imports = self._generate_imports()
            
            # Generate sensitive data configuration
            sensitive_config = self._generate_sensitive_data_config()
            
            # Generate helper functions
            helpers = self._generate_helper_functions()
            
            # Generate class setup and test method beginning
            setup_code = self._generate_incremental_setup_code(target_url, context_hints)
            
            # Generate cleanup code
            cleanup_code = self._generate_incremental_cleanup_code()
            
            return {
                'imports': imports + sensitive_config,
                'helpers': helpers,
                'setup_code': setup_code,
                'cleanup_code': cleanup_code
            }
            
        except Exception as e:
            raise PluginError(f"Failed to setup incremental Selenium script: {e}", self.plugin_name) from e
    
    def add_incremental_step(
        self,
        step: ParsedStep,
        current_state: Any,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new step to the incremental Selenium script.
        
        Generates code for the step and validates it against the current state.
        """
        try:
            self.logger.debug(f"Adding incremental step {step.step_index + 1} with {len(step.actions)} actions")
            
            step_code = []
            validation_issues = []
            insights = []
            
            # Determine indentation level
            indent = "        "
            if self.config.include_error_handling:
                indent = "            "
            
            # Add step header comment
            step_code.append(f"{indent}# Step {step.step_index + 1}")
            
            if self.config.add_comments and step.metadata:
                step_code.append(f"{indent}# Step metadata: {step.metadata}")
            
            # Process each action in the step
            for action in step.actions:
                try:
                    action_code = self._generate_action_code(action, step.step_index, indent)
                    step_code.extend(action_code)
                    
                    # Validate action
                    action_issues = self._validate_incremental_action(action, current_state)
                    validation_issues.extend(action_issues)
                    
                    # Generate insights from analysis if available
                    if analysis_results:
                        action_insights = self._extract_action_insights(action, analysis_results)
                        insights.extend(action_insights)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to generate code for action {action.action_type}: {e}")
                    step_code.append(f"{indent}# Error generating action {action.action_type}: {e}")
                    validation_issues.append(f"Action {action.action_type} generation failed: {e}")
            
            # Add step separator
            step_code.append(f"{indent}")
            
            # Add timing information if available
            if step.timing_info and self.config.include_logging:
                if 'elapsed_time' in step.timing_info:
                    elapsed = step.timing_info['elapsed_time']
                    step_code.append(f"{indent}# Step completed in {elapsed:.2f}s")
                    step_code.append(f"{indent}")
            
            return {
                'step_code': step_code,
                'validation_issues': validation_issues,
                'insights': insights
            }
            
        except Exception as e:
            raise PluginError(f"Failed to add incremental step: {e}", self.plugin_name) from e
    
    def finalize_incremental_script(
        self,
        current_state: Any,
        final_validation: bool = True,
        optimize_script: bool = True
    ) -> Dict[str, Any]:
        """
        Finalize the incremental Selenium script generation.
        
        Performs final validation, optimizations, and cleanup.
        """
        try:
            self.logger.debug("Finalizing incremental Selenium script")
            
            validation_issues = []
            optimization_insights = []
            
            # Generate final cleanup code
            final_cleanup_code = self._generate_final_cleanup_code(current_state)
            
            # Perform final validation if requested
            if final_validation:
                validation_issues = self._perform_final_script_validation(current_state)
            
            # Apply optimizations if requested
            if optimize_script:
                optimization_insights = self._apply_selenium_optimizations(current_state)
            
            return {
                'final_cleanup_code': final_cleanup_code,
                'validation_issues': validation_issues,
                'optimization_insights': optimization_insights
            }
            
        except Exception as e:
            raise PluginError(f"Failed to finalize incremental script: {e}", self.plugin_name) from e
    
    def _generate_incremental_setup_code(
        self,
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate setup code for incremental Selenium script."""
        template_vars = self.get_template_variables()
        
        lines = [
            "class IncrementalBrowseToTestSelenium(unittest.TestCase):",
            "    \"\"\"Incrementally generated Selenium test class.\"\"\"",
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
            "    def test_incremental_automation_flow(self):",
            "        \"\"\"Main test method containing incremental automation steps.\"\"\"",
        ])
        
        if self.config.include_logging:
            lines.append("        print('Starting incremental Selenium test execution')")
        
        if self.config.include_error_handling:
            lines.extend([
                "        try:",
                "            test_start_time = time.time()",
            ])
        
        # Add initial navigation if target URL is provided
        if target_url:
            indent = "            " if self.config.include_error_handling else "        "
            lines.extend([
                f"{indent}# Initial navigation (setup phase)",
                f"{indent}print(f'Navigating to: {target_url}')",
                f"{indent}self.driver.get('{target_url}')",
                f"{indent}time.sleep(2)  # Wait for page load",
                f"{indent}",
            ])
        
        # Add context-specific setup if hints are provided
        if context_hints:
            indent = "            " if self.config.include_error_handling else "        "
            
            if context_hints.get('requires_authentication'):
                lines.extend([
                    f"{indent}# Authentication may be required",
                    f"{indent}print('Note: This flow may require authentication')",
                    f"{indent}",
                ])
            
            if context_hints.get('flow_type') == 'form_submission':
                lines.extend([
                    f"{indent}# Form submission flow detected",
                    f"{indent}print('Preparing for form submission flow')",
                    f"{indent}",
                ])
        
        # Add beginning of incremental execution
        indent = "            " if self.config.include_error_handling else "        "
        lines.extend([
            f"{indent}print('=== Beginning incremental test execution ===')",
            f"{indent}",
        ])
        
        return lines
    
    def _generate_incremental_cleanup_code(self) -> List[str]:
        """Generate cleanup code for incremental Selenium script."""
        lines = []
        
        if self.config.include_error_handling:
            lines.extend([
                "",
                "            print('=== Incremental test completed successfully ===')",
                "            elapsed_time = time.time() - test_start_time",
                "            print(f'Total test execution time: {elapsed_time:.2f} seconds')",
                "",
                "        except Exception as e:",
                "            print(f'Incremental test failed: {e}', file=sys.stderr)",
                "            if hasattr(self, 'driver'):",
                "                # Take screenshot on failure",
                "                try:",
                "                    timestamp = int(time.time())",
                "                    screenshot_path = f'incremental_test_failure_{timestamp}.png'",
                "                    self.driver.save_screenshot(screenshot_path)",
                "                    print(f'Failure screenshot saved: {screenshot_path}')",
                "                except Exception as cleanup_error:",
                "                    print(f'Screenshot error: {cleanup_error}', file=sys.stderr)",
                "            raise",
            ])
        else:
            lines.extend([
                "        print('Incremental test completed successfully')",
            ])
        
        return lines
    
    def _generate_final_cleanup_code(self, current_state: Any) -> List[str]:
        """Generate final cleanup code based on current state."""
        lines = self._generate_incremental_cleanup_code()
        
        # Add entry point
        entry_point = [
            "",
            "",
            "if __name__ == '__main__':",
            "    # Run the incremental test",
            "    unittest.main(verbosity=2)",
        ]
        
        lines.extend(entry_point)
        return lines
    
    def _validate_incremental_action(self, action: ParsedAction, current_state: Any) -> List[str]:
        """Validate an action in the context of the current script state."""
        issues = []
        
        # Check for missing selector information
        if action.action_type in ['click_element', 'input_text'] and not action.selector_info:
            issues.append(f"Action {action.action_type} missing selector information")
        
        # Check for navigation after first step without proper wait
        if action.action_type == 'go_to_url' and current_state.current_step_count > 0:
            issues.append("Navigation in middle of test - consider adding explicit wait")
        
        # Check for sensitive data patterns
        if action.action_type == 'input_text':
            text_value = action.parameters.get('text', '')
            if '<secret>' in text_value and not self.config.mask_sensitive_data:
                issues.append("Sensitive data detected but masking is disabled")
        
        # Check for Selenium-specific issues
        if action.action_type == 'scroll_down' and current_state.total_actions > 10:
            issues.append("Many scroll actions detected - consider using WebDriverWait instead")
        
        return issues
    
    def _extract_action_insights(self, action: ParsedAction, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract insights for an action from analysis results."""
        insights = []
        
        # Extract from comprehensive analysis if available
        if 'comprehensive_analysis' in analysis_results:
            comp_analysis = analysis_results['comprehensive_analysis']
            
            # Check if action is marked as critical
            if 'critical_actions' in comp_analysis:
                for critical_action_idx in comp_analysis['critical_actions']:
                    if critical_action_idx == action.action_index:
                        insights.append(f"Action {action.action_type} identified as critical by AI analysis")
                        break
            
            # Check for context recommendations
            if 'context_recommendations' in comp_analysis:
                for rec in comp_analysis['context_recommendations']:
                    if action.action_type.lower() in rec.lower():
                        insights.append(f"Context recommendation: {rec}")
        
        # Extract from basic analysis
        if 'validation_issues' in analysis_results:
            for issue in analysis_results['validation_issues']:
                if f"Action {action.action_index + 1}" in issue:
                    insights.append(f"Validation concern: {issue}")
        
        return insights
    
    def _perform_final_script_validation(self, current_state: Any) -> List[str]:
        """Perform final validation of the complete Selenium script."""
        issues = []
        
        # Check script completeness
        if not current_state.test_steps:
            issues.append("No test steps were generated")
        
        if current_state.total_actions == 0:
            issues.append("No actions were processed")
        
        # Check for proper script structure
        script_content = current_state.to_script()
        
        # Validate Selenium-specific requirements
        if "webdriver" not in script_content:
            issues.append("Missing Selenium WebDriver imports")
        
        if "self.driver." not in script_content:
            issues.append("No driver interactions detected")
        
        if "self.driver.quit()" not in script_content and "driver.quit()" not in script_content:
            issues.append("Missing driver cleanup in tearDown")
        
        if "unittest.TestCase" not in script_content:
            issues.append("Not using proper unittest structure")
        
        # Check for potential timing issues
        if current_state.total_actions > 5 and "WebDriverWait" not in script_content:
            issues.append("Consider using WebDriverWait for reliability")
        
        # Check for error handling
        if current_state.total_actions > 3 and not self.config.include_error_handling:
            issues.append("Error handling recommended for complex tests")
        
        # Check for proper test method structure
        if "def test_" not in script_content:
            issues.append("Missing proper test method naming convention")
        
        return issues
    
    def _apply_selenium_optimizations(self, current_state: Any) -> List[str]:
        """Apply Selenium-specific optimizations."""
        optimizations = []
        
        script_content = current_state.to_script()
        
        # Suggest explicit waits for many actions
        if current_state.total_actions > 8 and "WebDriverWait" not in script_content:
            optimizations.append("Consider using WebDriverWait instead of time.sleep() for better reliability")
        
        # Suggest page object pattern for complex tests
        if current_state.total_actions > 15:
            optimizations.append("Large test detected - consider implementing Page Object Pattern")
        
        # Suggest selector optimization
        if script_content.count("xpath") > script_content.count("id"):
            optimizations.append("Consider using ID selectors over XPath for better performance")
        
        # Suggest browser optimization
        if script_content.count("self.driver.get") > 2:
            optimizations.append("Multiple navigations detected - consider test splitting for better isolation")
        
        # Suggest screenshot optimization
        if current_state.total_actions > 10 and "screenshot" in script_content:
            optimizations.append("Limit screenshots to key assertions for better performance")
        
        optimizations.append("Applied Selenium-specific code formatting")
        
        return optimizations 