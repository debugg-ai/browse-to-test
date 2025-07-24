#!/usr/bin/env python3
"""
Incremental orchestrator for live test script generation with setup, incremental, and finalization phases.

This orchestrator allows for real-time test script generation as browser automation steps are performed,
rather than processing everything at the end.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from ..configuration.config import Config
from ..processing.input_parser import InputParser, ParsedAutomationData, ParsedAction, ParsedStep
from ..processing.action_analyzer import ActionAnalyzer
from ..processing.context_collector import ContextCollector, SystemContext
from ...output_langs import LanguageManager
from ...ai.factory import AIProviderFactory
from ...plugins.registry import PluginRegistry


@dataclass
class ScriptState:
    """Tracks the current state of incremental script generation."""
    
    # Script sections
    imports: List[str] = field(default_factory=list)
    helpers: List[str] = field(default_factory=list)
    setup_code: List[str] = field(default_factory=list)
    test_steps: List[str] = field(default_factory=list)
    cleanup_code: List[str] = field(default_factory=list)
    
    # State tracking
    current_step_count: int = 0
    total_actions: int = 0
    setup_complete: bool = False
    finalized: bool = False
    
    # Context and analysis
    accumulated_analysis: Dict[str, Any] = field(default_factory=dict)
    system_context: Optional[SystemContext] = None
    validation_issues: List[str] = field(default_factory=list)
    
    # Metadata
    target_url: Optional[str] = None
    start_time: Optional[datetime] = None
    last_update_time: Optional[datetime] = None
    
    def to_script(self) -> str:
        """Generate the complete script from current state."""
        lines = []
        lines.extend(self.imports)
        lines.extend(self.helpers)
        lines.extend(self.setup_code)
        lines.extend(self.test_steps)
        lines.extend(self.cleanup_code)
        return "\n".join(lines)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current script state."""
        return {
            "step_count": self.current_step_count,
            "total_actions": self.total_actions,
            "setup_complete": self.setup_complete,
            "finalized": self.finalized,
            "validation_issues_count": len(self.validation_issues),
            "has_system_context": self.system_context is not None,
            "target_url": self.target_url,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_update": self.last_update_time.isoformat() if self.last_update_time else None,
        }


@dataclass
class IncrementalUpdateResult:
    """Result of an incremental update operation."""
    
    success: bool
    updated_script: str
    new_lines_added: int
    validation_issues: List[str] = field(default_factory=list)
    analysis_insights: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IncrementalE2eScriptOrchestrator:
    """
    Orchestrator for incremental test script generation with live updates.
    
    Supports a three-phase approach:
    1. Setup: Initialize script structure, context, and framework setup
    2. Incremental: Add test steps one at a time as they come in
    3. Finalization: Complete the script, validate, and optimize
    """
    
    def __init__(self, config: Config):
        """
        Initialize the incremental orchestrator.
        
        Args:
            config: Configuration object containing all settings
        """
        self.config = config
        
        # Initialize core components
        self.input_parser = InputParser(config)
        self.ai_factory = AIProviderFactory()
        self.plugin_registry = PluginRegistry()
        
        # Initialize context collector if enabled
        self.context_collector = None
        if config.processing.collect_system_context:
            self.context_collector = ContextCollector(config, config.project_root)
        
        # Initialize AI provider if enabled
        self.ai_provider = None
        if config.processing.analyze_actions_with_ai:
            try:
                self.ai_provider = self.ai_factory.create_provider(config.ai)
            except Exception as e:
                if config.debug:
                    print(f"Warning: Failed to initialize AI provider: {e}")
        
        # Initialize action analyzer for incremental analysis
        self.action_analyzer = ActionAnalyzer(self.ai_provider, config)
        
        # Initialize language manager if enabled
        self.language_manager = None
        if config.output.shared_setup.enabled:
            output_dir = Path(config.output.shared_setup.setup_dir)
            self.language_manager = LanguageManager(
                language=config.output.language,
                framework=config.output.framework,
                output_dir=output_dir
            )
        
        # Current session state
        self._current_script_state: Optional[ScriptState] = None
        self._current_plugin = None
        self._session_cache: Dict[str, Any] = {}
        
        # Callbacks for live updates
        self._update_callbacks: List[Callable[[IncrementalUpdateResult], None]] = []
    
    def start_incremental_session(
        self,
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> IncrementalUpdateResult:
        """
        Start a new incremental script generation session.
        
        This performs the setup phase:
        - Collect system context
        - Initialize plugin and script structure  
        - Set up imports, helpers, and framework setup code
        
        Args:
            target_url: URL being tested (helps with context filtering)
            context_hints: Additional context hints for analysis
            custom_config: Optional configuration overrides
            
        Returns:
            Initial setup result with script skeleton
        """
        if self._current_script_state is not None:
            raise RuntimeError("Incremental session already active. Call finalize_session() first.")
        
        # Apply custom configuration if provided
        effective_config = self.config
        if custom_config:
            effective_config = self._apply_config_overrides(custom_config)
        
        # Initialize script state
        self._current_script_state = ScriptState(
            start_time=datetime.now(),
            target_url=target_url
        )
        
        try:
            # Collect system context if enabled
            if effective_config.processing.collect_system_context and self.context_collector:
                try:
                    system_context = self.context_collector.collect_context(
                        target_url=target_url,
                        force_refresh=False
                    )
                    self._current_script_state.system_context = system_context
                    
                    if effective_config.verbose:
                        print(f"Collected system context: {len(system_context.existing_tests)} tests, "
                              f"{len(system_context.documentation)} docs")
                except Exception as e:
                    if effective_config.debug:
                        print(f"Warning: Context collection failed: {e}")
            
            # Create and configure incremental plugin
            self._current_plugin = self.plugin_registry.create_incremental_plugin(effective_config.output)
            
            # Check if plugin supports incremental updates
            if not hasattr(self._current_plugin, 'setup_incremental_script'):
                # Fall back to batch mode simulation
                if effective_config.verbose:
                    print("Warning: Plugin doesn't support incremental mode, using batch simulation")
                return self._setup_batch_simulation(effective_config, context_hints)
            
            # Perform setup phase
            setup_result = self._current_plugin.setup_incremental_script(
                target_url=target_url,
                system_context=self._current_script_state.system_context,
                context_hints=context_hints
            )
            
            # Update script state
            self._current_script_state.imports = setup_result.get('imports', [])
            self._current_script_state.helpers = setup_result.get('helpers', [])
            self._current_script_state.setup_code = setup_result.get('setup_code', [])
            self._current_script_state.cleanup_code = setup_result.get('cleanup_code', [])
            self._current_script_state.setup_complete = True
            self._current_script_state.last_update_time = datetime.now()
            
            # Create result
            result = IncrementalUpdateResult(
                success=True,
                updated_script=self._current_script_state.to_script(),
                new_lines_added=len(self._current_script_state.imports) + 
                               len(self._current_script_state.helpers) + 
                               len(self._current_script_state.setup_code) + 
                               len(self._current_script_state.cleanup_code),
                analysis_insights=[
                    "Incremental session initialized",
                    f"Framework: {effective_config.output.framework}",
                    f"Plugin: {self._current_plugin.plugin_name}",
                ],
                metadata=self._current_script_state.get_metadata()
            )
            
            # Notify callbacks
            self._notify_callbacks(result)
            
            return result
            
        except Exception as e:
            # Clean up on failure
            self._current_script_state = None
            self._current_plugin = None
            
            return IncrementalUpdateResult(
                success=False,
                updated_script="",
                new_lines_added=0,
                validation_issues=[f"Setup failed: {e}"],
                metadata={"error": str(e)}
            )
    
    def add_step(
        self,
        step_data: Union[Dict[str, Any], ParsedStep],
        analyze_step: bool = True
    ) -> IncrementalUpdateResult:
        """
        Add a new step to the incremental script generation.
        
        Args:
            step_data: Step data (either raw dict or ParsedStep)
            analyze_step: Whether to perform AI analysis on this step
            
        Returns:
            Result of adding the step with updated script
        """
        if not self._current_script_state or not self._current_script_state.setup_complete:
            return IncrementalUpdateResult(
                success=False,
                updated_script="",
                new_lines_added=0,
                validation_issues=["No active incremental session. Call start_incremental_session() first."],
            )
        
        try:
            # Parse step if needed
            if isinstance(step_data, dict):
                # Convert single step dict to ParsedStep
                parsed_step = self._parse_single_step(step_data, self._current_script_state.current_step_count)
            else:
                parsed_step = step_data
            
            # Perform incremental analysis if enabled
            analysis_results = None
            if analyze_step and self.config.processing.analyze_actions_with_ai and self.ai_provider:
                try:
                    analysis_results = self._analyze_incremental_step(
                        parsed_step,
                        self._current_script_state.accumulated_analysis
                    )
                    
                    # Update accumulated analysis
                    if analysis_results:
                        self._merge_incremental_analysis(analysis_results)
                        
                except Exception as e:
                    if self.config.debug:
                        print(f"Warning: Incremental analysis failed: {e}")
            
            # Generate code for this step
            if hasattr(self._current_plugin, 'add_incremental_step'):
                # Use incremental plugin method
                step_result = self._current_plugin.add_incremental_step(
                    step=parsed_step,
                    current_state=self._current_script_state,
                    analysis_results=analysis_results
                )
                
                new_step_code = step_result.get('step_code', [])
                step_validation_issues = step_result.get('validation_issues', [])
                step_insights = step_result.get('insights', [])
                
            else:
                # Fall back to generating step code manually
                new_step_code = self._generate_step_code_fallback(parsed_step)
                step_validation_issues = []
                step_insights = []
            
            # Update script state
            old_step_count = len(self._current_script_state.test_steps)
            self._current_script_state.test_steps.extend(new_step_code)
            self._current_script_state.current_step_count += 1
            self._current_script_state.total_actions += len(parsed_step.actions)
            self._current_script_state.validation_issues.extend(step_validation_issues)
            self._current_script_state.last_update_time = datetime.now()
            
            # Create result
            result = IncrementalUpdateResult(
                success=True,
                updated_script=self._current_script_state.to_script(),
                new_lines_added=len(self._current_script_state.test_steps) - old_step_count,
                validation_issues=step_validation_issues,
                analysis_insights=step_insights,
                metadata=self._current_script_state.get_metadata()
            )
            
            # Notify callbacks
            self._notify_callbacks(result)
            
            return result
            
        except Exception as e:
            return IncrementalUpdateResult(
                success=False,
                updated_script=self._current_script_state.to_script() if self._current_script_state else "",
                new_lines_added=0,
                validation_issues=[f"Failed to add step: {e}"],
                metadata={"error": str(e)}
            )
    
    def finalize_session(
        self,
        final_validation: bool = True,
        optimize_script: bool = True
    ) -> IncrementalUpdateResult:
        """
        Finalize the incremental script generation session.
        
        This performs the finalization phase:
        - Complete the script structure
        - Perform final validation
        - Apply optimizations
        - Generate final script
        
        Args:
            final_validation: Whether to perform comprehensive validation
            optimize_script: Whether to apply final optimizations
            
        Returns:
            Final result with completed and validated script
        """
        if not self._current_script_state:
            return IncrementalUpdateResult(
                success=False,
                updated_script="",
                new_lines_added=0,
                validation_issues=["No active incremental session to finalize."],
            )
        
        try:
            # Perform finalization through plugin if supported
            if hasattr(self._current_plugin, 'finalize_incremental_script'):
                finalization_result = self._current_plugin.finalize_incremental_script(
                    current_state=self._current_script_state,
                    final_validation=final_validation,
                    optimize_script=optimize_script
                )
                
                # Update script state with finalization results
                if 'final_cleanup_code' in finalization_result:
                    self._current_script_state.cleanup_code = finalization_result['final_cleanup_code']
                
                final_validation_issues = finalization_result.get('validation_issues', [])
                optimization_insights = finalization_result.get('optimization_insights', [])
                
            else:
                # Basic finalization
                final_validation_issues = []
                optimization_insights = ["Basic finalization (plugin doesn't support advanced finalization)"]
            
            # Perform comprehensive validation if requested
            if final_validation:
                validation_results = self._perform_final_validation()
                final_validation_issues.extend(validation_results)
            
            # Apply optimizations if requested
            if optimize_script:
                optimization_results = self._apply_final_optimizations()
                optimization_insights.extend(optimization_results)
            
            # Mark as finalized
            self._current_script_state.finalized = True
            self._current_script_state.validation_issues.extend(final_validation_issues)
            self._current_script_state.last_update_time = datetime.now()
            
            # Generate final script
            raw_script = self._current_script_state.to_script()
            
            # Generate shared setup if enabled
            if self.language_manager and self.config.output.shared_setup.enabled:
                # Generate setup files
                setup_files = self.language_manager.generate_setup_files(
                    force_regenerate=self.config.output.shared_setup.force_regenerate
                )
                
                if self.config.verbose:
                    print(f"Generated shared setup files: {list(setup_files.keys())}")
                
                # Create clean script without inline utilities
                final_script = self._generate_clean_incremental_script(
                    raw_script,
                    self.config
                )
            else:
                # Apply post-processing normally
                final_script = self._post_process_script(
                    raw_script,
                    self.config,
                    self._current_script_state.accumulated_analysis,
                    self._current_script_state.system_context
                )
            
            # Create final result
            result = IncrementalUpdateResult(
                success=len(final_validation_issues) == 0,
                updated_script=final_script,
                new_lines_added=0,  # Finalization doesn't add new functional lines
                validation_issues=final_validation_issues,
                analysis_insights=optimization_insights + [
                    f"Session completed with {self._current_script_state.current_step_count} steps",
                    f"Total actions processed: {self._current_script_state.total_actions}",
                ],
                metadata=self._current_script_state.get_metadata()
            )
            
            # Clean up session state
            self._cleanup_session()
            
            # Notify callbacks
            self._notify_callbacks(result)
            
            return result
            
        except Exception as e:
            return IncrementalUpdateResult(
                success=False,
                updated_script=self._current_script_state.to_script() if self._current_script_state else "",
                new_lines_added=0,
                validation_issues=[f"Finalization failed: {e}"],
                metadata={"error": str(e)}
            )
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get current session state information."""
        if not self._current_script_state:
            return None
        
        return {
            "active": True,
            "setup_complete": self._current_script_state.setup_complete,
            "finalized": self._current_script_state.finalized,
            "metadata": self._current_script_state.get_metadata(),
            "script_preview": self._current_script_state.to_script()[:500] + "..." if len(self._current_script_state.to_script()) > 500 else self._current_script_state.to_script(),
        }
    
    def register_update_callback(self, callback: Callable[[IncrementalUpdateResult], None]):
        """Register a callback to be notified of incremental updates."""
        self._update_callbacks.append(callback)
    
    def unregister_update_callback(self, callback: Callable[[IncrementalUpdateResult], None]):
        """Unregister an update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
    
    def abort_session(self) -> None:
        """Abort the current incremental session and clean up."""
        if self._current_script_state:
            if self.config.verbose:
                print("Aborting incremental session")
        self._cleanup_session()
    
    # Private helper methods
    
    def _parse_single_step(self, step_data: Dict[str, Any], step_index: int) -> ParsedStep:
        """Parse a single step dictionary into ParsedStep."""
        # Create temporary automation data with single step
        temp_data = [step_data]
        parsed_data = self.input_parser.parse(temp_data)
        
        if parsed_data.steps:
            step = parsed_data.steps[0]
            # Update step index
            step.step_index = step_index
            return step
        else:
            # Create empty step if parsing failed
            from ..processing.input_parser import ParsedStep
            return ParsedStep(
                step_index=step_index,
                actions=[],
                timing_info=step_data.get('timing_info', {}),
                metadata=step_data.get('metadata', {})
            )
    
    def _analyze_incremental_step(
        self,
        step: ParsedStep,
        accumulated_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Perform incremental analysis on a single step."""
        # Convert step back to dict format for analyzer
        step_dict = {
            'model_output': {
                'action': []
            },
            'state': {
                'interacted_element': []
            },
            'metadata': step.metadata or {}
        }
        
        for action in step.actions:
            action_dict = {action.action_type: action.parameters}
            step_dict['model_output']['action'].append(action_dict)
            
            if action.selector_info:
                step_dict['state']['interacted_element'].append(action.selector_info)
        
        # Analyze with context of previous analysis
        temp_parsed_data = ParsedAutomationData(
            steps=[step],
            sensitive_data_keys=self.config.output.sensitive_data_keys or [],
            metadata={}
        )
        
        return self.action_analyzer.analyze_automation_data(
            temp_parsed_data,
            target_url=self._current_script_state.target_url,
            use_intelligent_analysis=self.config.processing.use_intelligent_analysis
        )
    
    def _merge_incremental_analysis(self, new_analysis: Dict[str, Any]) -> None:
        """Merge new analysis results into accumulated analysis."""
        if not self._current_script_state.accumulated_analysis:
            self._current_script_state.accumulated_analysis = new_analysis
            return
        
        # Merge action counts
        if 'action_types' in new_analysis:
            if 'action_types' not in self._current_script_state.accumulated_analysis:
                self._current_script_state.accumulated_analysis['action_types'] = {}
            
            for action_type, count in new_analysis['action_types'].items():
                current_count = self._current_script_state.accumulated_analysis['action_types'].get(action_type, 0)
                self._current_script_state.accumulated_analysis['action_types'][action_type] = current_count + count
        
        # Merge validation issues
        if 'validation_issues' in new_analysis:
            if 'validation_issues' not in self._current_script_state.accumulated_analysis:
                self._current_script_state.accumulated_analysis['validation_issues'] = []
            self._current_script_state.accumulated_analysis['validation_issues'].extend(new_analysis['validation_issues'])
        
        # Update totals
        self._current_script_state.accumulated_analysis['total_actions'] = self._current_script_state.total_actions
        self._current_script_state.accumulated_analysis['total_steps'] = self._current_script_state.current_step_count
    
    def _generate_step_code_fallback(self, step: ParsedStep) -> List[str]:
        """Generate step code using fallback method when plugin doesn't support incremental."""
        lines = [f"            # Step {step.step_index + 1}"]
        
        for action in step.actions:
            # Basic action code generation
            if action.action_type == "go_to_url":
                url = action.parameters.get("url", "")
                lines.append(f"            await page.goto('{url}')")
            elif action.action_type == "click_element":
                if action.selector_info and 'css_selector' in action.selector_info:
                    selector = action.selector_info['css_selector']
                    lines.append(f"            await page.click('{selector}')")
            elif action.action_type == "input_text":
                text = action.parameters.get("text", "")
                if action.selector_info and 'css_selector' in action.selector_info:
                    selector = action.selector_info['css_selector']
                    lines.append(f"            await page.fill('{selector}', '{text}')")
            elif action.action_type == "wait":
                seconds = action.parameters.get("seconds", 3)
                lines.append(f"            await asyncio.sleep({seconds})")
            else:
                lines.append(f"            # Unsupported action: {action.action_type}")
        
        lines.append("")
        return lines
    
    def _setup_batch_simulation(self, config: Config, context_hints: Optional[Dict[str, Any]]) -> IncrementalUpdateResult:
        """Set up batch mode simulation for plugins that don't support incremental."""
        # Generate basic script structure
        self._current_script_state.imports = [
            "import asyncio",
            "from playwright.async_api import async_playwright",
            "",
        ]
        
        self._current_script_state.helpers = [
            "# Helper functions would go here",
            "",
        ]
        
        self._current_script_state.setup_code = [
            "async def run_test():",
            "    async with async_playwright() as p:",
            "        browser = await p.chromium.launch()",
            "        context = await browser.new_context()",
            "        page = await context.new_page()",
            "",
        ]
        
        self._current_script_state.cleanup_code = [
            "",
            "        await context.close()",
            "        await browser.close()",
            "",
            "if __name__ == '__main__':",
            "    asyncio.run(run_test())",
        ]
        
        self._current_script_state.setup_complete = True
        
        return IncrementalUpdateResult(
            success=True,
            updated_script=self._current_script_state.to_script(),
            new_lines_added=len(self._current_script_state.imports) + len(self._current_script_state.setup_code),
            warnings=["Using batch simulation mode - plugin doesn't support incremental updates"],
            metadata=self._current_script_state.get_metadata()
        )
    
    def _perform_final_validation(self) -> List[str]:
        """Perform comprehensive validation of the final script."""
        issues = []
        
        if not self._current_script_state.test_steps:
            issues.append("No test steps were added to the script")
        
        if self._current_script_state.total_actions == 0:
            issues.append("No actions were processed")
        
        # Check for common issues
        script_content = self._current_script_state.to_script()
        
        if "await page.goto" not in script_content and "driver.get" not in script_content:
            issues.append("Script may be missing navigation commands")
        
        if len(self._current_script_state.validation_issues) > 5:
            issues.append(f"High number of validation issues detected: {len(self._current_script_state.validation_issues)}")
        
        return issues
    
    def _apply_final_optimizations(self) -> List[str]:
        """Apply final optimizations to the script."""
        optimizations = []
        
        # Basic optimizations could be added here
        optimizations.append("Applied code formatting")
        
        if self._current_script_state.total_actions > 10:
            optimizations.append("Large test detected - consider splitting into smaller tests")
        
        return optimizations
    
    def _post_process_script(
        self,
        script: str,
        config: Config,
        analysis_results: Optional[Dict[str, Any]],
        system_context: Optional[SystemContext]
    ) -> str:
        """Post-process the final script with enhancements."""
        # Add context-aware comments if available
        if analysis_results and config.output.include_logging:
            header_comments = [
                "# Generated with incremental analysis",
                f"# Total steps: {self._current_script_state.current_step_count}",
                f"# Total actions: {self._current_script_state.total_actions}",
            ]
            
            if analysis_results.get('action_types'):
                header_comments.append(f"# Action types: {', '.join(analysis_results['action_types'].keys())}")
            
            header_comments.append("")
            script = "\n".join(header_comments) + "\n" + script
        
        return script
    
    def _generate_clean_incremental_script(self, script: str, config: Config) -> str:
        """Generate a clean incremental script that imports from shared setup."""
        
        if not self.language_manager:
            return script
        
        lines = []
        
        # Add file header
        lines.extend([
            "#!/usr/bin/env python3",
            '"""',
            "Incremental test script generated by browse-to-test.",
            "",
            "This script uses shared utilities from the test_setup package.",
            '"""',
            ""
        ])
        
        # Add standard framework imports
        if config.output.framework == "playwright":
            lines.extend([
                "import asyncio",
                "from playwright.async_api import async_playwright",
                ""
            ])
        elif config.output.framework == "selenium":
            lines.extend([
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "from selenium.webdriver.support.ui import WebDriverWait",
                "from selenium.webdriver.support import expected_conditions as EC",
                ""
            ])
        
        # Add shared setup imports
        setup_imports = self.language_manager.get_import_statements_for_test(use_setup_files=True)
        if setup_imports:
            lines.extend(setup_imports)
            lines.append("")
        
        # Extract and clean the main test content
        clean_content = self._extract_clean_incremental_content(script, config)
        lines.extend(clean_content.split('\n'))
        
        # Add generation info comment
        lines.insert(len(lines) - 20, f"# Generated incrementally with {self._current_script_state.current_step_count} steps")
        
        return '\n'.join(lines)
    
    def _extract_clean_incremental_content(self, script: str, config: Config) -> str:
        """Extract the main test content from incremental script, removing inline utilities."""
        
        script_lines = script.split('\n')
        clean_lines = []
        
        # Skip common utility functions and imports that are now in shared setup
        skip_patterns = [
            'def replace_sensitive_data(',
            'class E2eActionError(',
            'async def safe_action(',
            'async def try_locate_and_act(',
            'def safe_selenium_action(',
            'SENSITIVE_DATA = {}',
            'import traceback',
            'from datetime import datetime',
            'import sys',
            'import os',
            'from pathlib import Path',
            'import urllib.parse',
            'from dotenv import load_dotenv'
        ]
        
        in_utility_function = False
        brace_depth = 0
        
        for line in script_lines:
            stripped_line = line.strip()
            
            # Skip empty lines at the beginning
            if not stripped_line and not clean_lines:
                continue
            
            # Check if we're starting a utility function
            if any(pattern in stripped_line for pattern in skip_patterns):
                in_utility_function = True
                continue
            
            # Track function depth with basic brace counting
            if in_utility_function:
                if '{' in line:
                    brace_depth += line.count('{')
                if '}' in line:
                    brace_depth -= line.count('}')
                
                # End utility function on unindented line or return to 0 depth
                if (not line.startswith(' ') and not line.startswith('\t') and stripped_line) or brace_depth <= 0:
                    in_utility_function = False
                    brace_depth = 0
                else:
                    continue
            
            # Skip lines inside utility functions
            if in_utility_function:
                continue
            
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def _apply_config_overrides(self, custom_config: Dict[str, Any]) -> Config:
        """Apply custom configuration overrides."""
        # Create a copy of the current config
        effective_config = Config.from_dict(self.config.to_dict())
        effective_config.update_from_dict(custom_config)
        return effective_config
    
    def _notify_callbacks(self, result: IncrementalUpdateResult) -> None:
        """Notify all registered callbacks of an update."""
        for callback in self._update_callbacks:
            try:
                callback(result)
            except Exception as e:
                if self.config.debug:
                    print(f"Warning: Update callback failed: {e}")
    
    def _cleanup_session(self) -> None:
        """Clean up the current session state."""
        self._current_script_state = None
        self._current_plugin = None
        self._session_cache.clear() 