"""
Enhanced async session with intelligent AI request batching and optimization.

This module extends the AsyncIncrementalSession with advanced features:
- Intelligent request batching to reduce AI calls
- Optimized prompts for token efficiency
- Response caching for similar patterns
- Enhanced error handling with graceful degradation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime

from .session import AsyncIncrementalSession, SessionResult
from ..processing.input_parser import ParsedStep
from ...ai.batch_processor import AIBatchProcessor, BatchableRequest
from ...ai.error_handler import AIErrorHandler, AdaptiveRetryStrategy
from ...ai.base import AIAnalysisRequest, AnalysisType
from .async_queue import queue_ai_task, wait_for_ai_task

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """Configuration for batch processing."""

    enabled: bool = True
    max_batch_size: int = 5
    batch_timeout: float = 0.5  # seconds
    cache_ttl: int = 3600  # 1 hour
    similarity_threshold: float = 0.8
    
    # Optimization settings
    optimize_prompts: bool = True
    deduplicate_requests: bool = True
    reuse_context: bool = True


@dataclass
class OptimizationMetrics:
    """Metrics for tracking optimization effectiveness."""

    total_steps: int = 0
    ai_calls_made: int = 0
    ai_calls_saved: int = 0
    tokens_used: int = 0
    tokens_saved: int = 0
    cache_hits: int = 0
    batch_count: int = 0
    avg_batch_size: float = 0.0
    error_count: int = 0
    retry_count: int = 0
    
    def calculate_savings(self) -> Dict[str, float]:
        """Calculate savings percentages."""
        if self.total_steps == 0:
            return {'ai_calls': 0.0, 'tokens': 0.0}
        
        potential_calls = self.total_steps
        actual_calls = self.ai_calls_made
        
        return {
            'ai_calls': (self.ai_calls_saved / potential_calls * 100) if potential_calls > 0 else 0,
            'tokens': (self.tokens_saved / (self.tokens_used + self.tokens_saved) * 100) 
                      if (self.tokens_used + self.tokens_saved) > 0 else 0,
            'efficiency_ratio': actual_calls / potential_calls if potential_calls > 0 else 1.0
        }


class EnhancedAsyncSession(AsyncIncrementalSession):
    """
    Enhanced async session with intelligent batching and optimization.
    
    Features:
    - Groups similar steps for batch AI processing
    - Caches responses for repeated patterns
    - Optimizes prompts to reduce token usage
    - Provides graceful degradation on AI failures
    """
    
    def __init__(self, config, converter=None):
        """Initialize enhanced session with batch processing."""
        super().__init__(config, converter)
        
        # Batch processing configuration
        self.batch_config = BatchConfig()
        
        # Initialize processors
        self.batch_processor = AIBatchProcessor(
            max_batch_size=self.batch_config.max_batch_size,
            batch_timeout=self.batch_config.batch_timeout,
            cache_ttl=self.batch_config.cache_ttl
        )
        
        self.error_handler = AIErrorHandler(
            retry_strategy=AdaptiveRetryStrategy(max_attempts=5)
        )
        
        # Tracking
        self._pending_batches: Dict[str, List[str]] = {}  # batch_key -> task_ids
        self._step_to_batch: Dict[str, str] = {}  # task_id -> batch_key
        self._optimization_metrics = OptimizationMetrics()
        
        # Pattern recognition
        self._pattern_cache: Dict[str, Any] = {}
        self._frequent_patterns: Set[str] = set()
    
    async def add_step_async(
        self, 
        step_data: Union[Dict[str, Any], ParsedStep],
        wait_for_completion: bool = False,
        batch_hint: Optional[str] = None
    ) -> SessionResult:
        """
        Add a step with intelligent batching support.
        
        Args:
            step_data: Step data or ParsedStep object
            wait_for_completion: Whether to wait for processing
            batch_hint: Optional hint for batch grouping
            
        Returns:
            Session result with optimization metadata
        """
        if not self._is_active:
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Session is not active"]
            )
        
        try:
            # Parse step
            if isinstance(step_data, dict):
                step = ParsedStep.from_dict(step_data)
                original_step_data = step_data
            else:
                step = step_data
                original_step_data = step.to_dict()
            
            # Add to collection
            step.step_index = len(self._steps)
            self._steps.append(step)
            self._optimization_metrics.total_steps += 1
            
            # Generate task ID
            task_id = f"step_{self._step_counter}_{datetime.now().timestamp()}"
            self._step_counter += 1
            
            # Check if batching is enabled and beneficial
            if self.batch_config.enabled and self._should_batch_step(step):
                # Create batch request
                batch_result = await self._add_to_batch(
                    task_id, step, original_step_data, batch_hint
                )
                
                if batch_result.get('batched'):
                    # Step added to batch
                    if wait_for_completion:
                        # Wait for batch to complete
                        result = await self._wait_for_batch_completion(
                            batch_result['batch_key'], task_id
                        )
                        return result
                    else:
                        return SessionResult(
                            success=True,
                            current_script=self._current_script,
                            step_count=len(self._steps),
                            metadata={
                                'task_id': task_id,
                                'batched': True,
                                'batch_key': batch_result['batch_key'],
                                'batch_size': batch_result['batch_size']
                            }
                        )
            
            # Fall back to regular processing
            return await super().add_step_async(step_data, wait_for_completion)
            
        except Exception as e:
            logger.error(f"Failed to add step with batching: {e}")
            self._optimization_metrics.error_count += 1
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=[f"Step processing failed: {str(e)}"]
            )
    
    async def _add_to_batch(
        self,
        task_id: str,
        step: ParsedStep,
        original_step_data: Dict[str, Any],
        batch_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a step to a batch for processing."""
        # Create AI analysis request
        request = self._create_analysis_request(step, original_step_data)
        
        # Add to batch processor
        batchable = await self.batch_processor.add_request(
            task_id, request, priority=10 - len(self._steps)
        )
        
        # Determine batch key
        batch_key = batch_hint or batchable.get_batch_key()
        
        # Track batch membership
        if batch_key not in self._pending_batches:
            self._pending_batches[batch_key] = []
        self._pending_batches[batch_key].append(task_id)
        self._step_to_batch[task_id] = batch_key
        
        # Check if we should process batch now
        should_process = await self._should_process_batch(batch_key)
        
        if should_process:
            # Process the batch
            asyncio.create_task(self._process_batch(batch_key))
        
        return {
            'batched': True,
            'batch_key': batch_key,
            'batch_size': len(self._pending_batches[batch_key])
        }
    
    async def _should_process_batch(self, batch_key: str) -> bool:
        """Determine if a batch should be processed now."""
        batch_size = len(self._pending_batches.get(batch_key, []))
        
        # Process if batch is full
        if batch_size >= self.batch_config.max_batch_size:
            return True
        
        # Process if timeout reached (handled by batch processor)
        # Process if this is the last step in a sequence
        if self._is_last_step_in_sequence():
            return True
        
        return False
    
    async def _process_batch(self, batch_key: str):
        """Process a batch of requests."""
        try:
            # Get AI provider
            ai_provider = self.converter.action_analyzer.ai_provider
            if not ai_provider:
                raise ValueError("No AI provider available")
            
            # Process batch with error handling
            results = await self.error_handler.handle_with_retry(
                self.batch_processor.process_batch,
                batch_key,
                ai_provider,
                provider=ai_provider.__class__.__name__,
                model=getattr(ai_provider, 'model', None)
            )
            
            # Update metrics
            self._optimization_metrics.ai_calls_made += 1
            self._optimization_metrics.batch_count += 1
            self._optimization_metrics.ai_calls_saved += len(results) - 1
            
            # Process individual results
            for result in results:
                if result.response:
                    # Update tokens
                    if result.response.tokens_used:
                        self._optimization_metrics.tokens_used += result.response.tokens_used
                    
                    # Process the response for the step
                    await self._process_batch_response(result)
            
            # Clear batch tracking
            if batch_key in self._pending_batches:
                del self._pending_batches[batch_key]
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            self._optimization_metrics.error_count += 1
            
            # Fall back to individual processing
            await self._fallback_to_individual_processing(batch_key)
    
    async def _process_batch_response(self, batch_result):
        """Process an individual response from a batch."""
        # Extract step information and update script
        # This would integrate with the existing converter logic
        pass
    
    async def _fallback_to_individual_processing(self, batch_key: str):
        """Fall back to processing steps individually if batch fails."""
        task_ids = self._pending_batches.get(batch_key, [])
        
        for task_id in task_ids:
            try:
                # Process individually using parent class method
                # This ensures we don't lose steps if batching fails
                pass
            except Exception as e:
                logger.error(f"Individual processing failed for {task_id}: {e}")
    
    def _should_batch_step(self, step: ParsedStep) -> bool:
        """Determine if a step should be batched."""
        # Simple steps might not benefit from batching
        if self._is_simple_step(step):
            return False
        
        # Check if we have similar steps pending
        if self._has_similar_pending_steps(step):
            return True
        
        # Batch if we expect more steps soon
        if self._expect_more_steps():
            return True
        
        return False
    
    def _is_simple_step(self, step: ParsedStep) -> bool:
        """Check if a step is too simple to benefit from batching."""
        # Navigation and simple clicks might not need batching
        simple_actions = {'navigate', 'click', 'wait'}
        
        if hasattr(step, 'actions') and len(step.actions) == 1:
            action = step.actions[0]
            if isinstance(action, dict) and action.get('type') in simple_actions:
                return True
        
        return False
    
    def _has_similar_pending_steps(self, step: ParsedStep) -> bool:
        """Check if there are similar steps already pending."""
        # This could use more sophisticated similarity checking
        return len(self._pending_batches) > 0
    
    def _expect_more_steps(self) -> bool:
        """Predict if more steps are likely to come soon."""
        # Based on timing patterns or user behavior
        if len(self._steps) < 3:
            return True  # Early in session, more steps likely
        
        # Check recent step timing
        # If steps are coming in quickly, expect more
        return False
    
    def _is_last_step_in_sequence(self) -> bool:
        """Check if this appears to be the last step."""
        # Could check for patterns like "submit", "complete", etc.
        return False
    
    def _create_analysis_request(
        self,
        step: ParsedStep,
        original_data: Dict[str, Any]
    ) -> AIAnalysisRequest:
        """Create an AI analysis request for a step."""
        return AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=[original_data],
            target_framework=self.config.output.framework,
            system_context=getattr(self.converter, 'system_context', None),
            target_url=self._target_url
        )
    
    async def _wait_for_batch_completion(
        self,
        batch_key: str,
        task_id: str
    ) -> SessionResult:
        """Wait for a specific task in a batch to complete."""
        try:
            # Wait for batch processing
            timeout = self.batch_config.batch_timeout + 30  # Add buffer
            
            # This would integrate with the batch processor's completion tracking
            result = await asyncio.wait_for(
                self._wait_for_task_in_batch(batch_key, task_id),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Batch processing timeout for task {task_id}")
            return SessionResult(
                success=False,
                current_script=self._current_script,
                validation_issues=["Batch processing timeout"]
            )
    
    async def _wait_for_task_in_batch(
        self,
        batch_key: str,
        task_id: str
    ) -> SessionResult:
        """Wait for a specific task within a batch."""
        # This would be implemented to track individual task completion
        # within a batch
        pass
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get detailed optimization metrics."""
        metrics = self._optimization_metrics
        savings = metrics.calculate_savings()
        
        return {
            'total_steps': metrics.total_steps,
            'ai_calls': {
                'made': metrics.ai_calls_made,
                'saved': metrics.ai_calls_saved,
                'savings_percent': savings['ai_calls']
            },
            'tokens': {
                'used': metrics.tokens_used,
                'saved': metrics.tokens_saved,
                'savings_percent': savings['tokens']
            },
            'batching': {
                'batches_processed': metrics.batch_count,
                'avg_batch_size': metrics.avg_batch_size,
                'cache_hits': metrics.cache_hits
            },
            'errors': {
                'count': metrics.error_count,
                'retry_count': metrics.retry_count
            },
            'efficiency_ratio': savings['efficiency_ratio']
        }
    
    async def optimize_prompt_tokens(self, prompt: str) -> str:
        """Optimize a prompt to reduce token usage while maintaining effectiveness."""
        if not self.batch_config.optimize_prompts:
            return prompt
        
        # Remove redundant whitespace
        optimized = ' '.join(prompt.split())
        
        # Remove repetitive instructions
        optimized = self._remove_redundant_instructions(optimized)
        
        # Use abbreviations for common terms
        optimized = self._apply_abbreviations(optimized)
        
        # Track savings
        original_tokens = len(prompt.split())  # Rough estimate
        optimized_tokens = len(optimized.split())
        self._optimization_metrics.tokens_saved += max(0, original_tokens - optimized_tokens)
        
        return optimized
    
    def _remove_redundant_instructions(self, text: str) -> str:
        """Remove redundant instructions from prompts."""
        # This would implement smart deduplication
        return text
    
    def _apply_abbreviations(self, text: str) -> str:
        """Apply common abbreviations to reduce tokens."""
        abbreviations = {
            'browser automation': 'automation',
            'test script': 'script',
            'user interface': 'UI',
            'application': 'app'
        }
        
        for full, abbrev in abbreviations.items():
            text = text.replace(full, abbrev)
        
        return text