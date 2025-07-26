#!/usr/bin/env python3
"""
Simplified incremental session for live test script generation.

This module provides a clean interface for incremental test generation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import json
from dataclasses import dataclass, field
from datetime import datetime

from ..configuration.config import Config
from ..configuration.comment_manager import CommentManager
from .converter import E2eTestConverter
from ..processing.input_parser import ParsedStep
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
                # Use the converter to generate script from all steps
                self._current_script = self.converter.convert(
                    self._steps,
                    target_url=self._target_url,
                    context_hints=self._context_hints
                )
            except Exception as e:
                logger.warning(f"Script regeneration failed: {e}")
                # Fall back to previous script
    
    def _update_current_script(self):
        """Update current script from sections."""
        all_lines = []
        for section in ['imports', 'setup', 'steps', 'teardown']:
            all_lines.extend(self._script_sections[section])
        
        self._current_script = '\n'.join(all_lines) 


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
        
        try:
            # Parse step if needed
            if isinstance(step_data, dict):
                step = ParsedStep.from_dict(step_data)
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
                result = await wait_for_ai_task(task_id)
                return result
            else:
                # Return immediately with task information
                return SessionResult(
                    success=True,
                    current_script=self._current_script,
                    step_count=len(self._steps),
                    metadata={
                        'task_id': task_id,
                        'step_queued': True,
                        'step_index': step.step_index
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
        try:
            # Use original step data to preserve model_output structure
            step_data = [original_step_data]
            
            # Use async converter to generate script for this step
            step_script = await self.converter.convert_async(
                step_data,
                target_url=self._target_url,
                context_hints=self._context_hints
            )
            
            # Update script sections (this needs to be thread-safe)
            await self._update_script_sections_async(step, step_script)
            
            # Update current script
            await self._update_current_script_async()
            
            return SessionResult(
                success=True,
                current_script=self._current_script,
                step_count=len(self._steps),
                metadata={
                    'step_processed': True,
                    'step_index': step.step_index
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
                # Use the async converter to generate script from all steps
                all_steps_data = [step.to_dict() for step in self._steps]
                self._current_script = await self.converter.convert_async(
                    all_steps_data,
                    target_url=self._target_url,
                    context_hints=self._context_hints
                )
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