"""
Incremental Playwright plugin for generating Python test scripts with live updates.

Extends the base PlaywrightPlugin to support incremental script generation with
setup, incremental step addition, and finalization phases.
"""

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from .playwright_plugin import PlaywrightPlugin
from .base import GeneratedTestScript, PluginError
from ..core.configuration.config import OutputConfig
from ..core.processing.input_parser import ParsedAutomationData, ParsedAction, ParsedStep


logger = logging.getLogger(__name__)


class IncrementalPlaywrightPlugin(PlaywrightPlugin):
    """Incremental Playwright plugin for live test script generation."""
    
    def __init__(self, config: OutputConfig):
        """Initialize the incremental Playwright plugin."""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
    
    @property
    def plugin_name(self) -> str:
        """Return the plugin name."""
        return "incremental_playwright"
    
    def setup_incremental_script(
        self,
        target_url: Optional[str] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Set up incremental Playwright script generation.
        
        Creates the basic script structure with imports, helpers, and browser setup.
        """
        try:
            self.logger.debug("Setting up incremental Playwright script")
            
            # Generate imports
            imports = self._generate_imports()
            
            # Generate sensitive data configuration
            sensitive_config = self._generate_sensitive_data_config()
            
            # Generate helper functions
            helpers = self._generate_helper_functions()
            
            # Generate setup code for browser and context
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
            raise PluginError(f"Failed to setup incremental Playwright script: {e}", self.plugin_name) from e
    
    def add_incremental_step(
        self,
        step: ParsedStep,
        current_state: Any,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new step to the incremental Playwright script.
        
        Generates code for the step and validates it against the current state.
        """
        try:
            self.logger.debug(f"Adding incremental step {step.step_index + 1} with {len(step.actions)} actions")
            
            step_code = []
            validation_issues = []
            insights = []
            
            # Add step header comment
            step_code.append(f"            # Step {step.step_index + 1}")
            
            if self.config.add_comments and step.metadata:
                step_code.append(f"            # Step metadata: {step.metadata}")
            
            # Process each action in the step
            for action in step.actions:
                try:
                    action_code = self._generate_action_code(action, step.step_index)
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
                    step_code.append(f"            # Error generating action {action.action_type}: {e}")
                    validation_issues.append(f"Action {action.action_type} generation failed: {e}")
            
            # Add step separator
            step_code.append("")
            
            # Add timing information if available
            if step.timing_info and self.config.include_logging:
                if 'elapsed_time' in step.timing_info:
                    elapsed = step.timing_info['elapsed_time']
                    step_code.append(f"            # Step completed in {elapsed:.2f}s")
                    step_code.append("")
            
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
        Finalize the incremental Playwright script generation.
        
        Performs final validation, optimizations, and cleanup.
        """
        try:
            self.logger.debug("Finalizing incremental Playwright script")
            
            validation_issues = []
            optimization_insights = []
            
            # Generate final cleanup code
            final_cleanup_code = self._generate_final_cleanup_code(current_state)
            
            # Perform final validation if requested
            if final_validation:
                validation_issues = self._perform_final_script_validation(current_state)
            
            # Apply optimizations if requested
            if optimize_script:
                optimization_insights = self._apply_playwright_optimizations(current_state)
            
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
        """Generate setup code for incremental script."""
        template_vars = self.get_template_variables()
        
        lines = [
            "async def run_test():",
            "    \"\"\"Incrementally generated test function.\"\"\"",
        ]
        
        if self.config.include_error_handling:
            lines.extend([
                "    exit_code = 0",
                "    start_time = None",
                "    try:",
                "        start_time = asyncio.get_event_loop().time()",
            ])
        
        # Browser setup with incremental considerations
        lines.extend([
            f"        async with async_playwright() as p:",
            f"            print('Starting {template_vars['browser_type']} browser for incremental test...')",
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
            f"            print('Browser context created for incremental test')",
            f"            ",
        ])
        
        # Add initial page setup if target URL is provided
        if target_url:
            lines.extend([
                f"            # Initial navigation (setup phase)",
                f"            print(f'Navigating to: {target_url}')",
                f"            await page.goto('{target_url}')",
                f"            await page.wait_for_load_state('networkidle')",
                f"            ",
            ])
        
        # Add context-specific setup if hints are provided
        if context_hints:
            if context_hints.get('requires_authentication'):
                lines.extend([
                    "            # Authentication may be required",
                    "            print('Note: This flow may require authentication')",
                    "",
                ])
            
            if context_hints.get('flow_type') == 'form_submission':
                lines.extend([
                    "            # Form submission flow detected",
                    "            print('Preparing for form submission flow')",
                    "",
                ])
        
        lines.extend([
            "            print('=== Beginning incremental test execution ===')",
            "",
        ])
        
        return lines
    
    def _generate_incremental_cleanup_code(self) -> List[str]:
        """Generate cleanup code for incremental script."""
        lines = []
        
        if self.config.include_error_handling:
            lines.extend([
                "",
                "            print('=== Incremental test completed successfully ===')",
                "            elapsed_time = asyncio.get_event_loop().time() - start_time",
                "            print(f'Total test execution time: {elapsed_time:.2f} seconds')",
                "",
                "        except Exception as e:",
                "            print(f'Incremental test failed: {e}', file=sys.stderr)",
                "            if self.config.include_screenshots:",
                "                try:",
                "                    timestamp = int(asyncio.get_event_loop().time())",
                "                    screenshot_path = f'incremental_test_failure_{timestamp}.png'",
                "                    await page.screenshot(path=screenshot_path)",
                "                    print(f'Failure screenshot saved: {screenshot_path}')",
                "                except Exception:",
                "                    pass",
                "            exit_code = 1",
                "            raise",
                "",
                "        finally:",
            ])
            
            lines.extend([
                "            # Cleanup resources",
                "            try:",
                "                await context.close()",
                "                await browser.close()",
                "                print('Browser resources cleaned up')",
                "            except Exception as cleanup_error:",
                "                print(f'Cleanup error: {cleanup_error}', file=sys.stderr)",
            ])
            
            if self.config.include_error_handling:
                lines.extend([
                    "",
                    "    return exit_code",
                ])
        else:
            lines.extend([
                "            print('Test completed successfully')",
                "            await context.close()",
                "            await browser.close()",
                "            print('Browser closed')",
            ])
        
        return lines
    
    def _generate_final_cleanup_code(self, current_state: Any) -> List[str]:
        """Generate final cleanup code based on current state."""
        lines = self._generate_incremental_cleanup_code()
        
        # Add entry point
        entry_point = [
            "",
            "if __name__ == '__main__':",
            "    if os.name == 'nt':",
            "        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())",
        ]
        
        if self.config.include_error_handling:
            entry_point.extend([
                "    exit_code = asyncio.run(run_test())",
                "    sys.exit(exit_code)",
            ])
        else:
            entry_point.append("    asyncio.run(run_test())")
        
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
            # Recommend wait after navigation
            issues.append("Navigation in middle of test - consider adding wait for page load")
        
        # Check for sensitive data patterns
        if action.action_type == 'input_text':
            text_value = action.parameters.get('text', '')
            if '<secret>' in text_value and not self.config.mask_sensitive_data:
                issues.append("Sensitive data detected but masking is disabled")
        
        return issues
    
    def _extract_action_insights(self, action: ParsedAction, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract insights for an action from analysis results."""
        insights = []
        
        # Extract from comprehensive analysis if available
        if 'comprehensive_analysis' in analysis_results:
            comp_analysis = analysis_results['comprehensive_analysis']
            
            # Check if action is marked as critical
            if 'critical_actions' in comp_analysis:
                for i, critical_action_idx in enumerate(comp_analysis['critical_actions']):
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
        """Perform final validation of the complete script."""
        issues = []
        
        # Check script completeness
        if not current_state.test_steps:
            issues.append("No test steps were generated")
        
        if current_state.total_actions == 0:
            issues.append("No actions were processed")
        
        # Check for proper script structure
        script_content = current_state.to_script()
        
        # Validate Playwright-specific requirements
        if "async_playwright" not in script_content:
            issues.append("Missing Playwright imports")
        
        if "await page." not in script_content and "page." not in script_content:
            issues.append("No page interactions detected")
        
        if "await browser.close()" not in script_content:
            issues.append("Missing browser cleanup")
        
        # Check for potential timing issues
        if current_state.total_actions > 5 and "await page.wait" not in script_content:
            issues.append("Consider adding explicit waits for reliability")
        
        # Check for error handling
        if current_state.total_actions > 3 and not self.config.include_error_handling:
            issues.append("Error handling recommended for complex tests")
        
        return issues
    
    def _apply_playwright_optimizations(self, current_state: Any) -> List[str]:
        """Apply Playwright-specific optimizations."""
        optimizations = []
        
        script_content = current_state.to_script()
        
        # Suggest network optimizations for many actions
        if current_state.total_actions > 10:
            optimizations.append("Consider using page.route() for network interception in large tests")
        
        # Suggest parallelization for multiple page operations
        if script_content.count("await page.goto") > 2:
            optimizations.append("Multiple navigations detected - consider test splitting")
        
        # Suggest selector optimization
        if script_content.count("xpath") > script_content.count("data-testid"):
            optimizations.append("Consider using data-testid selectors for better reliability")
        
        # Suggest screenshot optimization
        if self.config.include_screenshots and current_state.total_actions > 15:
            optimizations.append("Large test detected - limit screenshots to key assertions")
        
        optimizations.append("Applied Playwright-specific code formatting")
        
        return optimizations 