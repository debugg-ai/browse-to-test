#!/usr/bin/env python3
"""
Simplified incremental session for live test script generation.

This module provides a clean interface for incremental test generation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import json
from dataclasses import dataclass, field
from datetime import datetime

from ..configuration.config import Config
from ..configuration.comment_manager import CommentManager
from .converter import E2eTestConverter
from ..processing.input_parser import ParsedStep, ParsedAutomationData
from .async_queue import queue_ai_task, wait_for_ai_task, get_global_queue_manager, QueuedTask


logger = logging.getLogger(__name__)


@dataclass
class SessionResult:
    """Result of an incremental session operation."""
    
    success: bool
    current_script: str
    lines_added: int = 0
    step_count: int = 0
    validation_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IncrementalSession:
    """
    Simplified incremental test session.
    
    This provides a clean interface for adding test steps incrementally
    and building up a test script over time.
    
    Example:
        >>> config = ConfigBuilder().framework("playwright").build()
        >>> session = IncrementalSession(config)
        >>> result = session.start("https://example.com")
        >>> result = session.add_step(step_data)
        >>> final_script = session.finalize()
    """
    
    def __init__(self, config: Config):
        """
        Initialize incremental session.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.converter = E2eTestConverter(config)
        
        # Session state
        self._is_active = False
        self._steps = []
        self._target_url = None
        self._context_hints = None
        self._start_time = None
        
        # Generated script tracking
        self._current_script = ""
        self._script_sections = {
            'imports': [],
            'setup': [],
            'steps': [],
            'teardown': []
        }
    
    def start(
        self, 
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> SessionResult:
        """
        Start the incremental session.
        
        Args:
            target_url: Target URL being tested
            context_hints: Additional context for test generation
            
        Returns:
            Session result with initial setup
        """
        if self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is already active"]
            )
        
        try:
            self._is_active = True
            self._target_url = target_url
            self._context_hints = context_hints or {}
            self._start_time = datetime.now()
            self._steps = []
            
            # Generate initial setup
            self._generate_initial_setup()
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                metadata={
                    'session_started': True,
                    'target_url': target_url,
                    'start_time': self._start_time.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            self._is_active = False
            return SessionResult(
                success=False,
                current_script="",
                validation_issues=[f"Startup failed: {str(e)}"]
            )
    
    def add_step(
        self, 
        step_data: Dict[str, Any],
        validate: bool = True
    ) -> SessionResult:
        """
        Add a step to the current session.
        
        Args:
            step_data: Step data dictionary
            validate: Whether to validate the step
            
        Returns:
            Session result with updated script
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        try:
            # Add step to internal list
            self._steps.append(step_data)
            
            # Generate script for current steps
            previous_script = self._current_script
            self._regenerate_script()
            
            # Calculate lines added
            previous_lines = len(previous_script.split('\n'))
            current_lines = len(self._current_script.split('\n'))
            lines_added = current_lines - previous_lines
            
            # Validate if requested
            validation_issues = []
            if validate:
                validation_issues = self.converter.validate_data(self._steps)
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                lines_added=max(0, lines_added),
                step_count=len(self._steps),
                validation_issues=validation_issues,
                metadata={
                    'steps_total': len(self._steps),
                    'last_update': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to add step: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Step addition failed: {str(e)}"]
            )
    
    def remove_last_step(self) -> SessionResult:
        """
        Remove the last added step.
        
        Returns:
            Session result with updated script
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        if not self._steps:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["No steps to remove"]
            )
        
        try:
            self._steps.pop()
            self._regenerate_script()
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                metadata={'step_removed': True}
            )
            
        except Exception as e:
            logger.error(f"Failed to remove step: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Step removal failed: {str(e)}"]
            )
    
    def finalize(self, validate: bool = True) -> SessionResult:
        """
        Finalize the session and get the complete script.
        
        Args:
            validate: Whether to perform final validation
            
        Returns:
            Final session result with complete script
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        try:
            # Final script generation
            if self._steps:
                self._regenerate_script()
            
            # Validate if requested
            validation_issues = []
            if validate and self._steps:
                validation_issues = self.converter.validate_data(self._steps)
            
            # Mark session as complete
            self._is_active = False
            end_time = datetime.now()
            duration = (end_time - self._start_time).total_seconds() if self._start_time else 0
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                validation_issues=validation_issues,
                metadata={
                    'session_finalized': True,
                    'duration_seconds': duration,
                    'end_time': end_time.isoformat(),
                    'total_steps': len(self._steps)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to finalize session: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Finalization failed: {str(e)}"]
            )
    
    def get_current_script(self) -> str:
        """Get the current script without finalizing."""
        return self._current_script
    
    def get_step_count(self) -> int:
        """Get the number of steps added so far."""
        return len(self._steps)
    
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self._is_active
    
    def _generate_initial_setup(self):
        """Generate initial script setup (imports, etc.)."""
        # For now, we'll generate a minimal setup
        # This could be enhanced to pre-generate imports and setup based on framework
        if self.config.output.framework == "playwright":
            self._script_sections['imports'] = [
                "from playwright.sync_api import sync_playwright",
                "import pytest",
                ""
            ]
        elif self.config.output.framework == "selenium":
            self._script_sections['imports'] = [
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "import pytest",
                ""
            ]
        
        self._update_current_script()
    
    def _regenerate_script(self):
        """Regenerate the complete script from current steps."""
        if self._steps:
            try:
                # Use CommentManager for language-appropriate comments
                comment_manager = CommentManager(self.config.output.language)
                
                # Build script with step data comments
                script_parts = []
                
                for step_data in self._steps:
                    # Create a comment with the stringified step data
                    step_data_json = json.dumps(step_data, indent=2)
                    step_data_lines = step_data_json.split('\n')
                    step_data_comment_lines = comment_manager.multi_line(
                        [f"Original step data:"] + step_data_lines,
                        "    "
                    )
                    # Join the comment lines into a single string
                    script_parts.append("\n".join(step_data_comment_lines))
                    
                    # Generate script for this individual step
                    step_script = self.converter.convert(
                        [step_data],
                        target_url=self._target_url,
                        context_hints=self._context_hints
                    )
                    script_parts.append(step_script)
                
                # Combine all parts
                self._current_script = "\n".join(script_parts)
                
            except Exception as e:
                logger.warning(f"Script regeneration failed: {e}")
                # Fall back to basic generation without comments
                try:
                    self._current_script = self.converter.convert(
                        self._steps,
                        target_url=self._target_url,
                        context_hints=self._context_hints
                    )
                except Exception as fallback_e:
                    logger.error(f"Fallback script generation also failed: {fallback_e}")
                    # Keep previous script
    
    def _update_current_script(self):
        """Update current script from sections."""
        all_lines = []
        for section in ['imports', 'setup', 'steps', 'teardown']:
            all_lines.extend(self._script_sections[section])
        
        self._current_script = '\n'.join(all_lines)
    
    def analyze_script_quality(self) -> SessionResult:
        """
        Perform optional AI-powered quality analysis of the generated script.
        
        This method provides the comprehensive script analysis that is disabled by default
        for performance. Use this when you want detailed feedback on script quality,
        optimization suggestions, and grading.
        
        Returns:
            SessionResult with analysis metadata including quality score and recommendations
        """
        if not self._steps:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["No steps available for analysis"]
            )
        
        analysis_start_time = time.time()
        logger.info(f"🔍 Starting optional script quality analysis - Script length: {len(self._current_script):,} chars")
        
        try:
            # Temporarily enable final script analysis for this specific analysis
            original_setting = self.config.processing.enable_final_script_analysis
            self.config.processing.enable_final_script_analysis = True
            
            # Perform comprehensive AI analysis of the current script and automation data
            analyzed_script = self.converter.convert(
                self._steps,
                target_url=self._target_url,
                context_hints=self._context_hints
            )
            
            # Restore original setting
            self.config.processing.enable_final_script_analysis = original_setting
            
            analysis_end_time = time.time()
            analysis_duration = analysis_end_time - analysis_start_time
            
            logger.info(f"✅ Script quality analysis completed in {analysis_duration:.2f}s - "
                       f"Analyzed script: {len(analyzed_script):,} chars")
            
            # Compare original vs analyzed script for insights
            original_lines = len(self._current_script.split('\n'))
            analyzed_lines = len(analyzed_script.split('\n'))
            
            return SessionResult(
                success=True,
                current_script=analyzed_script,  # Return the analyzed/optimized script
                step_count=len(self._steps),
                metadata={
                    'quality_analysis_completed': True,
                    'analysis_duration': analysis_duration,
                    'original_script_chars': len(self._current_script),
                    'analyzed_script_chars': len(analyzed_script),
                    'original_script_lines': original_lines,
                    'analyzed_script_lines': analyzed_lines,
                    'improvement_detected': len(analyzed_script) != len(self._current_script),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'total_steps_analyzed': len(self._steps)
                }
            )
            
        except Exception as e:
            # Restore original setting on error
            self.config.processing.enable_final_script_analysis = original_setting
            analysis_end_time = time.time()
            analysis_duration = analysis_end_time - analysis_start_time
            
            logger.error(f"❌ Script quality analysis failed after {analysis_duration:.2f}s: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Quality analysis failed: {str(e)}"],
                metadata={
                    'quality_analysis_failed': True,
                    'analysis_duration': analysis_duration,
                    'error_message': str(e)
                }
            ) 


class AsyncIncrementalSession:
    """
    Async version of IncrementalSession for non-blocking script generation.
    
    This version allows multiple script generation calls to be queued and processed
    asynchronously while maintaining the sequential nature of AI calls.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the async incremental session.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.converter = E2eTestConverter(config)
        
        # Session state
        self._is_active = False
        self._target_url: Optional[str] = None
        self._context_hints: Optional[Dict[str, Any]] = None
        self._start_time: Optional[datetime] = None
        self._steps: List[ParsedStep] = []
        self._current_script = ""
        
        # Async task management
        self._queued_tasks: Dict[str, QueuedTask] = {}
        self._step_counter = 0
        
        # Script sections for building incrementally
        self._script_sections = {
            'imports': [],
            'setup': [],
            'test_body': [],
            'cleanup': []
        }
    
    async def start(
        self, 
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> SessionResult:
        """
        Start the async incremental session.
        
        Args:
            target_url: Target URL being tested
            context_hints: Additional context for test generation
            
        Returns:
            Session result with initial setup
        """
        if self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is already active"]
            )
        
        try:
            self._is_active = True
            self._target_url = target_url
            self._context_hints = context_hints or {}
            self._start_time = datetime.now()
            self._steps = []
            self._step_counter = 0
            
            # Generate initial setup (sync, fast)
            self._generate_initial_setup()
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                metadata={
                    'session_started': True,
                    'target_url': target_url,
                    'start_time': self._start_time.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to start async session: {e}")
            self._is_active = False
            return SessionResult(
                success=False,
                current_script="",
                validation_issues=[f"Startup failed: {str(e)}"]
            )
    
    async def add_step_async(
        self, 
        step_data: Union[Dict[str, Any], ParsedStep],
        wait_for_completion: bool = False
    ) -> SessionResult:
        """
        Add a step to the session asynchronously.
        
        Args:
            step_data: Step data or ParsedStep object
            wait_for_completion: Whether to wait for the step to be processed before returning
            
        Returns:
            Session result (may contain a task ID if not waiting for completion)
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        step_start_time = time.time()
        logger.info(f"⚡ Adding step {len(self._steps) + 1} to async session - "
                   f"Wait for completion: {wait_for_completion}")
        
        try:
            # Parse step if needed
            if isinstance(step_data, dict):
                # Use the input parser to correctly parse the step data
                # This properly extracts actions from model_output.action structure
                step = self.converter.input_parser._parse_step(step_data, len(self._steps))
                # Keep original data for processing to preserve model_output structure
                original_step_data = step_data
            else:
                step = step_data
                original_step_data = step.to_dict()
            
            # Add step to collection
            step.step_index = len(self._steps)
            self._steps.append(step)
            
            # Generate unique task ID
            task_id = f"step_{self._step_counter}_{datetime.now().timestamp()}"
            self._step_counter += 1
            
            # Queue the step processing task, passing both the parsed step and original data
            queued_task = await queue_ai_task(
                task_id,
                self._process_step_async,
                step,
                original_step_data,  # Pass original data to preserve model_output
                priority=10 - len(self._steps)  # Earlier steps have higher priority
            )
            
            self._queued_tasks[task_id] = queued_task
            
            if wait_for_completion:
                # Wait for the task to complete and return final result
                logger.info(f"⏳ Waiting for step {step.step_index + 1} completion...")
                result = await wait_for_ai_task(task_id)
                step_end_time = time.time()
                step_duration = step_end_time - step_start_time
                logger.info(f"✅ Step {step.step_index + 1} completed in {step_duration:.2f}s")
                return result
            else:
                # Return immediately with task information
                step_end_time = time.time()
                step_duration = step_end_time - step_start_time
                logger.info(f"📤 Step {step.step_index + 1} queued in {step_duration:.2f}s - Task ID: {task_id}")
                return SessionResult(
                    success=True,
                    current_script=self._current_script,
                    step_count=len(self._steps),
                    metadata={
                        'task_id': task_id,
                        'step_queued': True,
                        'step_index': step.step_index,
                        'queue_time': step_duration
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to add step: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Step addition failed: {str(e)}"]
            )
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> SessionResult:
        """
        Wait for a specific queued task to complete.
        
        Args:
            task_id: ID of the task to wait for
            timeout: Maximum time to wait
            
        Returns:
            Session result from the completed task
        """
        if task_id not in self._queued_tasks:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Task {task_id} not found"]
            )
        
        try:
            result = await wait_for_ai_task(task_id, timeout)
            return result
        except Exception as e:
            logger.error(f"Failed to wait for task {task_id}: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Task wait failed: {str(e)}"]
            )
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> SessionResult:
        """
        Wait for all currently queued tasks to complete.
        
        Args:
            timeout: Maximum time to wait for all tasks
            
        Returns:
            Final session result with complete script
        """
        if not self._queued_tasks:
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps)
            )
        
        try:
            # Get the queue manager and wait for all tasks
            queue_manager = await get_global_queue_manager()
            task_ids = list(self._queued_tasks.keys())
            
            # Wait for all tasks to complete
            for task_id in task_ids:
                await wait_for_ai_task(task_id, timeout)
            
            # Generate final script
            await self._regenerate_script_async()
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                metadata={
                    'all_tasks_completed': True,
                    'completed_tasks': task_ids
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to wait for all tasks: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Waiting for tasks failed: {str(e)}"]
            )
    
    async def finalize_async(self, wait_for_pending: bool = True) -> SessionResult:
        """
        Finalize the session asynchronously.
        
        Args:
            wait_for_pending: Whether to wait for pending tasks before finalizing
            
        Returns:
            Final session result with complete script
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        try:
            if wait_for_pending:
                # Wait for all pending tasks
                await self.wait_for_all_tasks()
            
            # Final script generation
            if self._steps:
                await self._regenerate_script_async()
            
            # Mark session as inactive
            self._is_active = False
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                metadata={
                    'session_finalized': True,
                    'total_steps': len(self._steps),
                    'session_duration': (datetime.now() - self._start_time).total_seconds() if self._start_time else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to finalize session: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Finalization failed: {str(e)}"]
            )
    
    async def _process_step_async(self, step: ParsedStep, original_step_data: Dict[str, Any]) -> SessionResult:
        """
        Process a single step asynchronously.
        
        This method is called as an async task for each step.
        """
        process_start_time = time.time()
        logger.info(f"🔨 Processing step {step.step_index + 1} - "
                   f"Actions: {len(step.actions)}")
        
        try:
            # Use CommentManager for language-appropriate comments
            comment_manager = CommentManager(self.config.output.language)
            
            # Create a comment with the stringified original step data
            step_data_comment = comment_manager.multi_line(
                f"Original step data: {json.dumps(original_step_data, indent=2)}",
                "    "
            )
            
            # Check if step has any valid actions
            if not step.actions:
                logger.info(f"Step {step.step_index} has no valid actions - generating comment placeholder")
                
                # Generate a comment indicating this step was skipped
                step_script = f"{step_data_comment}\n    # Step {step.step_index + 1}: No valid actions found (likely empty action data)"
                
            else:
                # Use original step data to preserve model_output structure
                step_data = [original_step_data]
                
                # Use async converter to generate script for this step
                generated_script = await self.converter.convert_async(
                    step_data,
                    target_url=self._target_url,
                    context_hints=self._context_hints
                )
                
                # Combine the step data comment with the generated script
                step_script = f"{step_data_comment}\n{generated_script}"
            
            # Update script sections (this needs to be thread-safe)
            await self._update_script_sections_async(step, step_script)
            
            # Update current script
            await self._update_current_script_async()
            
            process_end_time = time.time()
            process_duration = process_end_time - process_start_time
            logger.info(f"✅ Step {step.step_index + 1} processed in {process_duration:.2f}s")
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                metadata={
                    'step_processed': True,
                    'step_index': step.step_index,
                    'process_time': process_duration
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process step {step.step_index}: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Step processing failed: {str(e)}"]
            )
    
    async def _regenerate_script_async(self):
        """Regenerate the complete script from current steps asynchronously."""
        if self._steps:
            try:
                # Check if final analysis is enabled (performance optimization)
                if self.config.processing.enable_final_script_analysis:
                    logger.info("🔍 Performing final script analysis (enable_final_script_analysis=True)")
                    # Use the async converter to generate script from all steps with AI analysis
                    total_actions = sum(len(step.actions) for step in self._steps)
                    parsed_data = ParsedAutomationData(steps=self._steps.copy(), total_actions=total_actions)
                    self._current_script = await self.converter.convert_async(
                        parsed_data,
                        target_url=self._target_url,
                        context_hints=self._context_hints
                    )
                else:
                    logger.info("⚡ Skipping final script analysis for performance (enable_final_script_analysis=False)")
                    # Just combine the individual step scripts without additional AI analysis
                    await self._combine_step_scripts_async()
            except Exception as e:
                logger.warning(f"Async script regeneration failed: {e}")
                # Fall back to previous script
    
    async def _update_script_sections_async(self, step: ParsedStep, step_script: str):
        """Update script sections with new step content asynchronously."""
        # For now, just add to test body
        # This could be enhanced to parse the step_script and extract different sections
        # Use CommentManager for language-appropriate comments
        comment_manager = CommentManager(self.config.output.language)
        step_comment = comment_manager.single_line(f"Step {step.step_index + 1}", "    ")
        self._script_sections['test_body'].append(step_comment)
        self._script_sections['test_body'].append(step_script)
    
    async def _update_current_script_async(self):
        """Update the current script from sections asynchronously."""
        script_lines = []
        script_lines.extend(self._script_sections['imports'])
        script_lines.extend(self._script_sections['setup'])
        script_lines.extend(self._script_sections['test_body'])
        script_lines.extend(self._script_sections['cleanup'])
        
        self._current_script = "\n".join(script_lines)
    
    async def _combine_step_scripts_async(self):
        """Combine step scripts without additional AI analysis for performance."""
        # Generate a simple combined script from individual step results
        script_parts = []
        
        # Add header
        script_parts.append("# Generated test script using DebuggAI's browse-to-test open source project")
        script_parts.append("# visit us at https://debugg.ai for more information")
        script_parts.append("# For docs, see https://github.com/debugg-ai/browse-to-test")
        script_parts.append("# To submit an issue or request a feature, please visit https://github.com/debugg-ai/browse-to-test/issues")
        script_parts.append("")
        script_parts.append(f"# Framework: {self.config.output.framework}")
        script_parts.append(f"# Language: {self.config.output.language}")
        script_parts.append("# This script was automatically generated from sequential browser automation steps")
        script_parts.append("")
        
        # Add imports based on framework
        if self.config.output.framework == "playwright":
            if self.config.output.language == "python":
                script_parts.append("from playwright.sync_api import sync_playwright, expect")
                script_parts.append("import pytest")
            elif self.config.output.language == "typescript":
                script_parts.append("import { test, expect } from '@playwright/test';")
        elif self.config.output.framework == "selenium":
            if self.config.output.language == "python":
                script_parts.append("from selenium import webdriver")
                script_parts.append("from selenium.webdriver.common.by import By")
                script_parts.append("import pytest")
        
        script_parts.append("")
        
        # Add test function
        if self.config.output.language == "python":
            script_parts.append("def test_automated_workflow():")
            script_parts.append('    """Generated test for automated browser workflow."""')
        elif self.config.output.language == "typescript":
            script_parts.append("test('automated workflow', async ({ page }) => {")
        
        script_parts.append("")
        
        # Add basic setup
        if self.config.output.framework == "playwright" and self.config.output.language == "python":
            script_parts.append("    with sync_playwright() as p:")
            script_parts.append("        browser = p.chromium.launch()")
            script_parts.append("        page = browser.new_page()")
            script_parts.append("")
        
        # Add step actions (simplified, no AI analysis)
        for i, step in enumerate(self._steps):
            script_parts.append(f"        # Step {i + 1}")
            for action in step.actions:
                if action.action_type == "go_to_url":
                    url = action.parameters.get("url", "https://example.com")
                    script_parts.append(f'        page.goto("{url}")')
                elif action.action_type == "click_element":
                    script_parts.append(f'        page.click("button")  # TODO: Update selector')
                elif action.action_type == "input_text":
                    text = action.parameters.get("text", "example text")
                    script_parts.append(f'        page.fill("input", "{text}")  # TODO: Update selector')
                elif action.action_type == "wait":
                    seconds = action.parameters.get("seconds", 1)
                    script_parts.append(f'        page.wait_for_timeout({seconds * 1000})')
                elif action.action_type == "scroll":
                    script_parts.append('        page.mouse.wheel(0, 500)')
                elif action.action_type == "done":
                    script_parts.append('        # Test completed')
            script_parts.append("")
        
        # Add cleanup
        if self.config.output.framework == "playwright" and self.config.output.language == "python":
            script_parts.append("        browser.close()")
        elif self.config.output.language == "typescript":
            script_parts.append("});")
        
        self._current_script = "\n".join(script_parts)
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a queued task."""
        if task_id in self._queued_tasks:
            task = self._queued_tasks[task_id]
            return task.status.value if hasattr(task, 'status') else "unknown"
        return None
    
    def get_pending_tasks(self) -> List[str]:
        """Get list of pending task IDs."""
        return [task_id for task_id, task in self._queued_tasks.items() 
                if hasattr(task, 'status') and task.status.value in ['pending', 'running']]
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the current queue."""
        return {
            'total_tasks': len(self._queued_tasks),
            'total_steps': len(self._steps),
            'is_active': self._is_active,
            'pending_tasks': len(self.get_pending_tasks())
        }
    
    async def analyze_script_quality_async(self, timeout: Optional[float] = 120) -> SessionResult:
        """
        Perform optional AI-powered quality analysis of the generated script.
        
        This method provides the comprehensive script analysis that is disabled by default
        for performance. Use this when you want detailed feedback on script quality,
        optimization suggestions, and grading.
        
        Args:
            timeout: Maximum time to wait for analysis completion
            
        Returns:
            SessionResult with analysis metadata including quality score and recommendations
        """
        if not self._steps:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["No steps available for analysis"]
            )
        
        analysis_start_time = time.time()
        logger.info(f"🔍 Starting optional script quality analysis - Script length: {len(self._current_script):,} chars")
        
        try:
            # Temporarily enable final script analysis for this specific analysis
            original_setting = self.config.processing.enable_final_script_analysis
            self.config.processing.enable_final_script_analysis = True
            
            # Perform comprehensive AI analysis of the current script and automation data
            total_actions = sum(len(step.actions) for step in self._steps)
            parsed_data = ParsedAutomationData(steps=self._steps.copy(), total_actions=total_actions)
            
            # Use async converter with comprehensive analysis enabled
            analyzed_script = await asyncio.wait_for(
                self.converter.convert_async(
                    parsed_data,
                    target_url=self._target_url,
                    context_hints=self._context_hints
                ),
                timeout=timeout
            )
            
            # Restore original setting
            self.config.processing.enable_final_script_analysis = original_setting
            
            analysis_end_time = time.time()
            analysis_duration = analysis_end_time - analysis_start_time
            
            logger.info(f"✅ Script quality analysis completed in {analysis_duration:.2f}s - "
                       f"Analyzed script: {len(analyzed_script):,} chars")
            
            # Compare original vs analyzed script for insights
            original_lines = len(self._current_script.split('\n'))
            analyzed_lines = len(analyzed_script.split('\n'))
            
            return SessionResult(
                success=True,
                current_script=analyzed_script,  # Return the analyzed/optimized script
                step_count=len(self._steps),
                metadata={
                    'quality_analysis_completed': True,
                    'analysis_duration': analysis_duration,
                    'original_script_chars': len(self._current_script),
                    'analyzed_script_chars': len(analyzed_script),
                    'original_script_lines': original_lines,
                    'analyzed_script_lines': analyzed_lines,
                    'improvement_detected': len(analyzed_script) != len(self._current_script),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'total_steps_analyzed': len(self._steps),
                    'total_actions_analyzed': total_actions
                }
            )
            
        except asyncio.TimeoutError:
            # Restore original setting on timeout
            self.config.processing.enable_final_script_analysis = original_setting
            analysis_end_time = time.time()
            analysis_duration = analysis_end_time - analysis_start_time
            
            logger.warning(f"⏰ Script quality analysis timed out after {analysis_duration:.2f}s")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Quality analysis timed out after {timeout}s"],
                metadata={
                    'quality_analysis_timeout': True,
                    'analysis_duration': analysis_duration
                }
            )
            
        except Exception as e:
            # Restore original setting on error
            self.config.processing.enable_final_script_analysis = original_setting
            analysis_end_time = time.time()
            analysis_duration = analysis_end_time - analysis_start_time
            
            logger.error(f"❌ Script quality analysis failed after {analysis_duration:.2f}s: {e}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Quality analysis failed: {str(e)}"],
                metadata={
                    'quality_analysis_failed': True,
                    'analysis_duration': analysis_duration,
                    'error_message': str(e)
                }
            )
    
    def _generate_initial_setup(self):
        """Generate initial script setup (imports, etc.)."""
        # For now, we'll generate a minimal setup
        # This could be enhanced to pre-generate imports and setup based on framework
        if self.config.output.framework == "playwright":
            self._script_sections['imports'] = [
                "from playwright.sync_api import sync_playwright",
                "import pytest",
                ""
            ]
        elif self.config.output.framework == "selenium":
            self._script_sections['imports'] = [
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "import pytest",
                ""
            ]
        
        self._update_current_script()
    
    def _update_current_script(self):
        """Update the current script from sections."""
        script_lines = []
        script_lines.extend(self._script_sections['imports'])
        script_lines.extend(self._script_sections['setup'])
        script_lines.extend(self._script_sections['test_body'])
        script_lines.extend(self._script_sections['cleanup'])
        
        self._current_script = "\n".join(script_lines) 