#!/usr/bin/env python3
"""
Simplified test converter that unifies batch and incremental processing.

This module provides a clean, simple interface for converting automation data
to test scripts, replacing the complex orchestrator classes.
"""

import asyncio
import logging
from typing import Union, List, Dict, Optional, Any
from pathlib import Path

from ..configuration.config import Config
from ..processing.input_parser import InputParser
from ..processing.action_analyzer import ActionAnalyzer
from ..processing.context_collector import ContextCollector
from ...output_langs import LanguageManager
from ...ai.factory import AIProviderFactory
from ...plugins.registry import PluginRegistry
from .async_queue import queue_ai_task, wait_for_ai_task


logger = logging.getLogger(__name__)


class E2eTestConverter:
    """
    Simplified test converter with a clean API.
    
    This class replaces the complex orchestrator classes with a simple,
    unified interface that handles both batch and incremental processing.
    
    Example:
        >>> config = ConfigBuilder().framework("playwright").build()
        >>> converter = E2eTestConverter(config)
        >>> script = converter.convert(automation_data)
    """
    
    def __init__(self, config: Config):
        """
        Initialize the converter with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize core components
        self.input_parser = InputParser(config)
        self.plugin_registry = PluginRegistry()
        
        # Initialize AI provider if enabled
        self.ai_provider = None
        if config.processing.analyze_actions_with_ai:
            try:
                factory = AIProviderFactory()
                self.ai_provider = factory.create_provider(config.ai)
            except Exception as e:
                if config.debug:
                    logger.warning(f"Failed to initialize AI provider: {e}")
                    
        # Initialize action analyzer
        self.action_analyzer = ActionAnalyzer(self.ai_provider, config)
        
        # Initialize context collector if enabled
        self.context_collector = None
        if config.processing.collect_system_context:
            self.context_collector = ContextCollector(config, config.project_root)
        
        # Initialize language manager if enabled
        self.language_manager = None
        if config.output.shared_setup.enabled:
            output_dir = Path(config.output.shared_setup.setup_dir)
            self.language_manager = LanguageManager(
                language=config.output.language,
                framework=config.output.framework,
                output_dir=output_dir
            )
    
    def convert(
        self, 
        automation_data: Union[List[Dict], str, Path],
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert automation data to test script.
        
        Args:
            automation_data: Browser automation data (list of steps, file path, or JSON string)
            target_url: Target URL being tested (optional)
            context_hints: Additional context hints (optional)
            
        Returns:
            Generated test script as string
            
        Raises:
            ValueError: If automation data is invalid
            RuntimeError: If conversion fails
        """
        try:
            # Parse input data
            parsed_data = self.input_parser.parse(automation_data)
            
            # Collect system context if enabled
            system_context = None
            if self.context_collector:
                try:
                    system_context = self.context_collector.collect_context(
                        target_url=target_url
                    )
                except Exception as e:
                    if self.config.debug:
                        logger.warning(f"Context collection failed: {e}")
            
            # Analyze actions with AI if enabled
            analysis_result = None
            if self.ai_provider and self.config.processing.analyze_actions_with_ai:
                try:
                    analysis_result = self.action_analyzer.analyze_comprehensive(
                        parsed_data,
                        system_context=system_context,
                        target_url=target_url
                    )
                except Exception as e:
                    if self.config.debug:
                        logger.warning(f"AI analysis failed: {e}")
            
            # Create plugin and generate script
            plugin = self.plugin_registry.create_plugin(self.config.output)
            
            # Pass context to the plugin using the expected interface
            script_result = plugin.generate_test_script(
                parsed_data=parsed_data,
                analysis_results=analysis_result,  # Note: plural 'results' to match plugin interface
                system_context=system_context,
                context_hints=context_hints
            )
            
            # Extract script content from result
            script = script_result.content if hasattr(script_result, 'content') else str(script_result)
            
            if self.config.debug:
                logger.info(f"Successfully generated {len(script)} characters of test script")
            
            return script
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            if self.config.debug:
                raise
            else:
                raise RuntimeError(f"Failed to convert automation data: {str(e)}")
    
    async def convert_async(
        self, 
        automation_data: Union[List[Dict], str, Path],
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert automation data to test script asynchronously.
        
        Args:
            automation_data: Browser automation data (list of steps, file path, or JSON string)
            target_url: Target URL being tested (optional)
            context_hints: Additional context hints (optional)
            
        Returns:
            Generated test script as string
            
        Raises:
            ValueError: If automation data is invalid
            RuntimeError: If conversion fails
        """
        try:
            # Parse input data (sync, typically fast)
            parsed_data = self.input_parser.parse(automation_data)
            
            # Collect system context if enabled (sync, typically fast)
            system_context = None
            if self.context_collector:
                try:
                    system_context = self.context_collector.collect_context(
                        target_url=target_url
                    )
                except Exception as e:
                    if self.config.debug:
                        logger.warning(f"Context collection failed: {e}")
            
            # Analyze actions with AI if enabled (async)
            analysis_result = None
            if self.ai_provider and self.config.processing.analyze_actions_with_ai:
                try:
                    # Queue the analysis task with unique ID to avoid conflicts in parallel execution
                    import time
                    task_id = f"conversion_analysis_{hash(str(automation_data))}_{int(time.time() * 1000000)}"
                    analysis_task = await queue_ai_task(
                        task_id,
                        self.action_analyzer.analyze_comprehensive_async,
                        parsed_data,
                        system_context,
                        target_url,
                        priority=3  # High priority for conversion analysis
                    )
                    
                    # Get the analysis result
                    analysis_result = await wait_for_ai_task(task_id)
                    
                except Exception as e:
                    if self.config.debug:
                        logger.warning(f"AI analysis failed: {e}")
            
            # Create plugin and generate script (sync, typically fast)
            plugin = self.plugin_registry.create_plugin(self.config.output)
            
            # Pass context to the plugin using the expected interface
            script_result = plugin.generate_test_script(
                parsed_data=parsed_data,
                analysis_results=analysis_result,  # Note: plural 'results' to match plugin interface
                system_context=system_context,
                context_hints=context_hints
            )
            
            # Extract script content from result
            script = script_result.content if hasattr(script_result, 'content') else str(script_result)
            
            if self.config.debug:
                logger.info(f"Successfully generated {len(script)} characters of test script")
            
            return script
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            if self.config.debug:
                raise
            else:
                raise RuntimeError(f"Failed to convert automation data: {str(e)}")
    
    def validate_data(self, automation_data: Union[List[Dict], str, Path]) -> List[str]:
        """
        Validate automation data without converting.
        
        Args:
            automation_data: Data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            parsed_data = self.input_parser.parse(automation_data)
            return self.input_parser.validate(parsed_data)
        except Exception as e:
            return [f"Parsing failed: {str(e)}"]
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported frameworks."""
        return self.plugin_registry.list_available_plugins()
    
    def get_supported_ai_providers(self) -> List[str]:
        """Get list of supported AI providers."""
        factory = AIProviderFactory()
        return factory.list_available_providers() 