#!/usr/bin/env python3
"""
Simplified incremental session for live test script generation.

This module provides a clean interface for incremental test generation.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime

from ..configuration.config import Config
from .converter import E2eTestConverter


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