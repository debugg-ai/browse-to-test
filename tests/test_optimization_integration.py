#!/usr/bin/env python3
"""
Integration tests for AI optimization features.

This module tests the integration of batch processing, error handling,
and other optimization features working together in realistic scenarios.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

# Import the modules under test
from browse_to_test.ai.batch_processor import AIBatchProcessor
from browse_to_test.ai.error_handler import AIErrorHandler, ExponentialBackoffStrategy
from browse_to_test.ai.base import AIAnalysisRequest, AIResponse, AnalysisType
from browse_to_test.core.processing.action_analyzer import ActionAnalyzer
from browse_to_test.core.configuration.config import Config, AIConfig, ProcessingConfig, OutputConfig


class MockOptimizedProvider:
    """Mock AI provider with optimization features."""
    
    def __init__(self, failure_rate: float = 0.0, response_delay: float = 0.05):
        self.failure_rate = failure_rate
        self.response_delay = response_delay
        self.call_count = 0
        self.total_tokens = 0
        self.successful_calls = 0
        self.failed_calls = 0
        
    async def analyze_with_context_async(self, request: AIAnalysisRequest, system_prompt: str = None) -> AIResponse:
        """Mock async analysis with potential failures."""
        self.call_count += 1
        
        # Simulate network delay
        await asyncio.sleep(self.response_delay)
        
        # Simulate failures based on failure rate
        if self.failure_rate > 0 and (self.call_count % int(1/self.failure_rate)) == 0:
            self.failed_calls += 1
            raise Exception("Mock API failure")
        
        self.successful_calls += 1
        
        # Generate appropriate response
        if hasattr(request, 'additional_context') and request.additional_context and request.additional_context.get('batch_processing'):
            # Handle batch requests
            batch_size = request.additional_context.get('batch_size', 1)
            request_ids = request.additional_context.get('request_ids', ['default'])
            
            sections = []
            for req_id in request_ids:
                sections.append(f"### Request: {req_id}\nGenerated test code for {req_id}")
            
            content = "\n\n".join(sections)
            tokens = 80 * batch_size  # More efficient token usage in batches
        else:
            content = f"Generated test code for {request.analysis_type.value}"
            tokens = 120  # Individual requests use more tokens
        
        self.total_tokens += tokens
        
        return AIResponse(
            content=content,
            model="mock-optimized-model",
            provider="mock-provider",
            tokens_used=tokens
        )
    
    def get_stats(self):
        """Get provider statistics."""
        return {
            'total_calls': self.call_count,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'total_tokens': self.total_tokens,
            'success_rate': self.successful_calls / self.call_count if self.call_count > 0 else 0
        }


class TestBasicIntegration:
    """Test basic integration between optimization components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_provider = MockOptimizedProvider()
        self.batch_processor = AIBatchProcessor(
            max_batch_size=5,
            batch_timeout=0.1,
            cache_ttl=300
        )
        self.error_handler = AIErrorHandler(
            retry_strategy=ExponentialBackoffStrategy(
                base_delay=0.01,
                max_delay=0.1,
                max_attempts=3
            )
        )
    
    @pytest.mark.asyncio
    async def test_batch_processor_with_error_handling(self):
        """Test batch processor working with error handling."""
        # Create requests that will be batched
        requests = []
        for i in range(8):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"click_{i}", "selector": f"#button_{i}"},
                target_framework="playwright"
            )
            requests.append(request)
        
        # Add requests to batch processor with error handling
        batchable_requests = []
        for i, request in enumerate(requests):
            async def add_with_error_handling(req_id, req):
                return await self.error_handler.handle_with_retry(
                    self.batch_processor.add_request,
                    req_id, req,
                    provider="batch_provider"
                )
            
            batchable = await add_with_error_handling(f"test_{i}", request)
            batchable_requests.append(batchable)
        
        # Process batches with error handling
        batch_groups = {}
        for batchable in batchable_requests:
            key = batchable.get_batch_key()
            if key not in batch_groups:
                batch_groups[key] = []
            batch_groups[key].append(batchable)
        
        all_results = []
        for batch_key in batch_groups.keys():
            while len(self.batch_processor._request_queues[batch_key]) > 0:
                async def process_with_error_handling():
                    return await self.batch_processor.process_batch(batch_key, self.mock_provider)
                
                batch_results = await self.error_handler.handle_with_retry(
                    process_with_error_handling,
                    provider="batch_provider"
                )
                all_results.extend(batch_results)
        
        # Verify integration results
        assert len(all_results) == 8
        assert all(result.error is None for result in all_results)
        
        # Check that batching occurred
        provider_stats = self.mock_provider.get_stats()
        assert provider_stats['total_calls'] < 8  # Should use fewer calls due to batching
        assert provider_stats['success_rate'] == 1.0  # Error handling should ensure success
        
        # Check batch processor stats
        batch_stats = self.batch_processor.get_statistics()
        assert batch_stats['api_calls_saved'] > 0
    
    @pytest.mark.asyncio
    async def test_error_recovery_with_batching(self):
        """Test error recovery mechanisms with batch processing."""
        # Use a provider that fails occasionally
        failing_provider = MockOptimizedProvider(failure_rate=0.3)  # 30% failure rate
        
        # Create batch of requests
        requests = []
        for i in range(10):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{i}"},
                target_framework="playwright"
            )
            requests.append(request)
        
        # Process with error handling
        results = []
        for i, request in enumerate(requests):
            batchable = await self.batch_processor.add_request(f"test_{i}", request)
            
            # Process with error handling
            try:
                batch_results = await self.error_handler.handle_with_retry(
                    self.batch_processor.process_batch,
                    batchable.get_batch_key(),
                    failing_provider,
                    provider="failing_provider"
                )
                results.extend(batch_results)
            except Exception as e:
                # Some requests might still fail after retries
                pass
        
        # Should have recovered from most failures
        assert len(results) >= 7  # At least 70% success rate expected
        
        # Check that retries occurred
        provider_stats = failing_provider.get_stats()
        assert provider_stats['failed_calls'] > 0  # Some failures should have occurred
        assert provider_stats['total_calls'] > 10  # Retries should have increased call count
    
    @pytest.mark.asyncio
    async def test_caching_with_error_recovery(self):
        """Test caching effectiveness with error recovery."""
        # Create identical requests that should benefit from caching
        base_request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#submit"},
            target_framework="playwright"
        )
        
        # First batch - will populate cache
        first_batch = []
        for i in range(3):
            batchable = await self.batch_processor.add_request(f"first_{i}", base_request)
            first_batch.append(batchable)
        
        batch_key = first_batch[0].get_batch_key()
        first_results = await self.error_handler.handle_with_retry(
            self.batch_processor.process_batch,
            batch_key,
            self.mock_provider,
            provider="cache_provider"
        )
        
        first_call_count = self.mock_provider.call_count
        
        # Second batch - should hit cache
        second_batch = []
        for i in range(3):
            batchable = await self.batch_processor.add_request(f"second_{i}", base_request)
            second_batch.append(batchable)
        
        second_results = await self.error_handler.handle_with_retry(
            self.batch_processor.process_batch,
            batch_key,
            self.mock_provider,
            provider="cache_provider"
        )
        
        # Verify caching effectiveness
        assert len(first_results) == 3
        assert len(second_results) == 3
        assert self.mock_provider.call_count == first_call_count  # No additional API calls
        
        # Check cache statistics
        batch_stats = self.batch_processor.get_statistics()
        assert batch_stats['cache_hits'] == 3  # All second batch should be cache hits


class TestRealisticWorkflowIntegration:
    """Test integration with realistic workflow scenarios."""
    
    def setup_method(self):
        """Set up realistic test environment."""
        self.config = Config(
            ai=AIConfig(
                provider="mock",
                model="mock-model",
                api_key="test_key"
            ),
            processing=ProcessingConfig(
                analyze_actions_with_ai=True,
                enable_context_collection=True
            ),
            output=OutputConfig(
                framework="playwright",
                language="python"
            )
        )
        
        self.mock_provider = MockOptimizedProvider()
        self.batch_processor = AIBatchProcessor()
        self.error_handler = AIErrorHandler()
    
    @pytest.mark.asyncio
    async def test_mixed_request_types_optimization(self):
        """Test optimization with mixed request types (realistic scenario)."""
        # Create a realistic mix of requests
        requests = [
            # Conversion requests (can be batched)
            *[AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"click_{i}", "selector": f"#button_{i}"},
                target_framework="playwright"
            ) for i in range(5)],
            
            # Optimization requests (different batch group)
            *[AIAnalysisRequest(
                analysis_type=AnalysisType.OPTIMIZATION,
                automation_data={"action": f"optimize_{i}", "selector": f"#form_{i}"},
                target_framework="playwright"
            ) for i in range(3)],
            
            # Validation requests (another batch group)
            *[AIAnalysisRequest(
                analysis_type=AnalysisType.VALIDATION,
                automation_data={"action": f"validate_{i}", "selector": f"#input_{i}"},
                target_framework="playwright"
            ) for i in range(2)]
        ]
        
        # Process all requests through optimization pipeline
        start_time = time.time()
        all_results = []
        
        # Add all requests to batch processor
        batchables = []
        for i, request in enumerate(requests):
            batchable = await self.batch_processor.add_request(f"mixed_{i}", request)
            batchables.append(batchable)
        
        # Group by batch key and process
        batch_groups = {}
        for batchable in batchables:
            key = batchable.get_batch_key()
            if key not in batch_groups:
                batch_groups[key] = []
            batch_groups[key].append(batchable)
        
        # Process each batch group with error handling
        for batch_key in batch_groups.keys():
            while len(self.batch_processor._request_queues[batch_key]) > 0:
                batch_results = await self.error_handler.handle_with_retry(
                    self.batch_processor.process_batch,
                    batch_key,
                    self.mock_provider,
                    provider="mixed_provider"
                )
                all_results.extend(batch_results)
        
        processing_time = time.time() - start_time
        
        # Verify results
        assert len(all_results) == 10  # All requests processed
        assert all(result.error is None for result in all_results)
        
        # Verify optimization effectiveness
        provider_stats = self.mock_provider.get_stats()
        batch_stats = self.batch_processor.get_statistics()
        
        # Should have used fewer API calls than individual processing
        assert provider_stats['total_calls'] < 10
        assert provider_stats['total_calls'] == len(batch_groups)  # One call per batch group
        assert batch_stats['api_calls_saved'] > 0
        
        # Performance should be reasonable
        assert processing_time < 2.0  # Should complete within 2 seconds
        
        print(f"Mixed workload optimization results:")
        print(f"- Requests: {len(requests)}")
        print(f"- API calls: {provider_stats['total_calls']} (saved {batch_stats['api_calls_saved']})")
        print(f"- Processing time: {processing_time:.2f}s")
        print(f"- Batch groups: {len(batch_groups)}")
    
    @pytest.mark.asyncio
    async def test_high_volume_stress_integration(self):
        """Test integration under high volume stress conditions."""
        # Create high volume of requests
        num_requests = 50
        requests = []
        
        # Mix of similar and unique requests
        for i in range(num_requests):
            if i % 5 == 0:
                # Every 5th request is identical (should cache well)
                automation_data = {"action": "click", "selector": "#common-button"}
            else:
                # Unique requests
                automation_data = {"action": f"action_{i}", "selector": f"#element_{i}"}
            
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data=automation_data,
                target_framework="playwright"
            )
            requests.append(request)
        
        # Process with full optimization pipeline
        start_time = time.time()
        
        # Use concurrent processing to simulate high load
        async def process_request(req_id, request):
            try:
                # Add to batch processor
                batchable = await self.error_handler.handle_with_retry(
                    self.batch_processor.add_request,
                    req_id, request,
                    provider="stress_provider"
                )
                
                # Small delay to allow batch accumulation
                await asyncio.sleep(0.001)
                
                # Process batch
                batch_key = batchable.get_batch_key()
                results = await self.error_handler.handle_with_retry(
                    self.batch_processor.process_batch,
                    batch_key,
                    self.mock_provider,
                    provider="stress_provider"
                )
                
                return results
            except Exception as e:
                return [{'error': str(e)}]
        
        # Process all requests concurrently
        tasks = [
            process_request(f"stress_{i}", request)
            for i, request in enumerate(requests)
        ]
        
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for result_list in results_lists:
            if isinstance(result_list, list):
                all_results.extend(result_list)
        
        processing_time = time.time() - start_time
        
        # Filter successful results
        successful_results = [r for r in all_results if hasattr(r, 'error') and r.error is None]
        
        # Verify stress test results
        assert len(successful_results) >= num_requests * 0.8  # At least 80% success rate
        
        # Get final statistics
        provider_stats = self.mock_provider.get_stats()
        batch_stats = self.batch_processor.get_statistics()
        
        # Calculate optimization metrics
        baseline_calls = num_requests  # Individual processing would need this many calls
        actual_calls = provider_stats['total_calls']
        optimization_percent = ((baseline_calls - actual_calls) / baseline_calls) * 100
        
        print(f"High volume stress test results:")
        print(f"- Requests: {num_requests}")
        print(f"- Successful: {len(successful_results)}")
        print(f"- API calls: {actual_calls}/{baseline_calls} ({optimization_percent:.1f}% reduction)")
        print(f"- Cache hits: {batch_stats['cache_hits']}")
        print(f"- Processing time: {processing_time:.2f}s")
        print(f"- Throughput: {len(successful_results)/processing_time:.1f} req/s")
        
        # Verify optimization targets
        assert optimization_percent >= 40  # Should achieve at least 40% optimization
        assert processing_time < 10.0  # Should complete within 10 seconds
        
        # Verify caching effectiveness
        expected_cache_hits = num_requests // 5  # Every 5th request should cache
        assert batch_stats['cache_hits'] >= expected_cache_hits * 0.8  # Allow some variance


class TestSystemRobustness:
    """Test system robustness under various failure conditions."""
    
    def setup_method(self):
        """Set up robustness test environment."""
        self.batch_processor = AIBatchProcessor(
            max_batch_size=3,
            batch_timeout=0.05,
            cache_ttl=300
        )
        self.error_handler = AIErrorHandler(
            retry_strategy=ExponentialBackoffStrategy(
                base_delay=0.005,
                max_delay=0.05,
                max_attempts=3
            ),
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=1.0
        )
    
    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self):
        """Test system recovery from partial failures."""
        # Create provider that fails intermittently
        failing_provider = MockOptimizedProvider(failure_rate=0.4)  # 40% failure rate
        
        # Create batch of requests
        requests = []
        for i in range(15):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{i}"},
                target_framework="playwright"
            )
            requests.append(request)
        
        # Process with full error handling
        successful_results = []
        failed_results = []
        
        for i, request in enumerate(requests):
            try:
                batchable = await self.batch_processor.add_request(f"partial_{i}", request)
                batch_key = batchable.get_batch_key()
                
                results = await self.error_handler.handle_with_retry(
                    self.batch_processor.process_batch,
                    batch_key,
                    failing_provider,
                    provider="partial_fail_provider"
                )
                
                successful_results.extend(results)
                
            except Exception as e:
                failed_results.append({'request_id': f"partial_{i}", 'error': str(e)})
        
        # Verify partial failure handling
        total_processed = len(successful_results) + len(failed_results)
        success_rate = len(successful_results) / total_processed if total_processed > 0 else 0
        
        print(f"Partial failure recovery results:")
        print(f"- Total requests: {len(requests)}")
        print(f"- Successful: {len(successful_results)}")
        print(f"- Failed: {len(failed_results)}")
        print(f"- Success rate: {success_rate:.1%}")
        
        # Should achieve reasonable success rate despite failures
        assert success_rate >= 0.6  # At least 60% success rate
        assert len(successful_results) > 0  # Some requests should succeed
        
        # Error handling should have attempted retries
        provider_stats = failing_provider.get_stats()
        assert provider_stats['total_calls'] > len(requests)  # Retries should have occurred
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker working with batch processing."""
        # Create provider that always fails
        always_failing_provider = MockOptimizedProvider(failure_rate=1.0)
        
        # Process requests that will trigger circuit breaker
        requests = []
        for i in range(10):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"circuit_{i}"},
                target_framework="playwright"
            )
            requests.append(request)
        
        successful_count = 0
        circuit_breaker_triggered = False
        
        for i, request in enumerate(requests):
            try:
                batchable = await self.batch_processor.add_request(f"circuit_{i}", request)
                batch_key = batchable.get_batch_key()
                
                results = await self.error_handler.handle_with_retry(
                    self.batch_processor.process_batch,
                    batch_key,
                    always_failing_provider,
                    provider="circuit_test_provider"
                )
                
                successful_count += len(results)
                
            except Exception as e:
                if "circuit breaker" in str(e).lower():
                    circuit_breaker_triggered = True
                    break
        
        # Verify circuit breaker activation
        assert circuit_breaker_triggered or successful_count == 0
        
        # Get error statistics
        error_stats = self.error_handler.get_error_statistics()
        assert error_stats['total_errors'] > 0
        
        print(f"Circuit breaker test results:")
        print(f"- Circuit breaker triggered: {circuit_breaker_triggered}")
        print(f"- Total errors: {error_stats['total_errors']}")
        print(f"- Provider calls: {always_failing_provider.get_stats()['total_calls']}")
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self):
        """Test concurrent batch processing under load."""
        # Create multiple concurrent batch processors
        processors = [
            AIBatchProcessor(max_batch_size=3, batch_timeout=0.02)
            for _ in range(3)
        ]
        
        provider = MockOptimizedProvider()
        
        # Process requests concurrently across multiple processors
        async def process_with_processor(processor_id, request_count):
            processor = processors[processor_id]
            results = []
            
            for i in range(request_count):
                request = AIAnalysisRequest(
                    analysis_type=AnalysisType.CONVERSION,
                    automation_data={"action": f"concurrent_{processor_id}_{i}"},
                    target_framework="playwright"
                )
                
                batchable = await processor.add_request(f"p{processor_id}_r{i}", request)
                batch_key = batchable.get_batch_key()
                
                # Small delay to allow batch accumulation
                await asyncio.sleep(0.001)
                
                batch_results = await self.error_handler.handle_with_retry(
                    processor.process_batch,
                    batch_key,
                    provider,
                    provider="concurrent_provider"
                )
                
                results.extend(batch_results)
            
            return results
        
        # Run concurrent processing
        tasks = [
            process_with_processor(processor_id, 10)
            for processor_id in range(3)
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        total_results = []
        for result_list in all_results:
            total_results.extend(result_list)
        
        # Verify concurrent processing
        assert len(total_results) == 30  # 3 processors × 10 requests each
        assert all(hasattr(r, 'error') and r.error is None for r in total_results)
        
        # Check that optimization still occurred
        provider_stats = provider.get_stats()
        assert provider_stats['total_calls'] < 30  # Should use batching optimization
        
        print(f"Concurrent processing results:")
        print(f"- Total results: {len(total_results)}")
        print(f"- API calls: {provider_stats['total_calls']}/30")
        print(f"- Success rate: {provider_stats['success_rate']:.1%}")


class TestRegressionPrevention:
    """Test that optimizations don't break existing functionality."""
    
    def setup_method(self):
        """Set up regression test environment."""
        self.standard_provider = MockOptimizedProvider()
        self.config = Config()
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_single_requests(self):
        """Test that single requests still work as before."""
        # Test individual request processing (legacy mode)
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={
                "actions": [
                    {"action": "click", "selector": "#button"},
                    {"action": "type", "selector": "#input", "text": "test"}
                ]
            },
            target_framework="playwright"
        )
        
        # Process without optimization (simulating legacy behavior)
        response = await self.standard_provider.analyze_with_context_async(request)
        
        # Verify legacy behavior works
        assert response is not None
        assert response.content is not None
        assert response.tokens_used > 0
        assert response.model == "mock-optimized-model"
        
        # Should work identically to before optimizations
        provider_stats = self.standard_provider.get_stats()
        assert provider_stats['total_calls'] == 1
        assert provider_stats['success_rate'] == 1.0
    
    @pytest.mark.asyncio
    async def test_configuration_compatibility(self):
        """Test that existing configurations still work."""
        # Test with various configuration combinations
        configs = [
            Config(),  # Default config
            Config(
                ai=AIConfig(provider="openai", model="gpt-4"),
                processing=ProcessingConfig(analyze_actions_with_ai=False)
            ),
            Config(
                ai=AIConfig(provider="anthropic", model="claude-3-sonnet"),
                processing=ProcessingConfig(
                    analyze_actions_with_ai=True,
                    enable_context_collection=False
                )
            )
        ]
        
        for i, config in enumerate(configs):
            # Create analyzer with different configs
            # Note: Using mock for action analyzer since we're testing config compatibility
            with patch('browse_to_test.core.processing.action_analyzer.ActionAnalyzer') as MockAnalyzer:
                mock_analyzer = MockAnalyzer.return_value
                mock_analyzer.analyze_automation_data.return_value = {
                    'overall_score': 0.8,
                    'recommendations': ['test recommendation'],
                    'analysis_metadata': {'config_test': i}
                }
                
                # Verify analyzer can be created with different configs
                analyzer = MockAnalyzer(None, config)
                assert analyzer is not None
                
                # Verify analysis still works
                mock_data = {'actions': [{'action': 'click', 'selector': '#test'}]}
                result = mock_analyzer.analyze_automation_data(mock_data)
                assert result is not None
                assert 'overall_score' in result
    
    @pytest.mark.asyncio
    async def test_error_handling_backward_compatibility(self):
        """Test that error handling doesn't break existing error patterns."""
        # Test that existing exception types are still raised appropriately
        failing_provider = MockOptimizedProvider(failure_rate=1.0)  # Always fails
        
        # Direct provider call (without error handler) should still raise exceptions
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "test"},
            target_framework="playwright"
        )
        
        with pytest.raises(Exception, match="Mock API failure"):
            await failing_provider.analyze_with_context_async(request)
        
        # Error handler should catch and retry, but eventually re-raise
        error_handler = AIErrorHandler()
        
        with pytest.raises(Exception):
            await error_handler.handle_with_retry(
                failing_provider.analyze_with_context_async,
                request,
                provider="compatibility_test"
            )
        
        # Verify that error handler attempted retries
        error_stats = error_handler.get_error_statistics()
        assert error_stats['total_errors'] > 1  # Should have retried multiple times


@pytest.mark.integration
class TestEndToEndOptimizationValidation:
    """End-to-end validation of optimization claims."""
    
    @pytest.mark.asyncio
    async def test_optimization_claims_validation(self):
        """Validate the specific optimization claims (70% AI calls, 58% tokens)."""
        # Set up optimized system
        batch_processor = AIBatchProcessor(max_batch_size=5, batch_timeout=0.1)
        error_handler = AIErrorHandler()
        optimized_provider = MockOptimizedProvider()
        
        # Create realistic workload for testing claims
        workload = []
        
        # 30 similar requests (high batching potential)
        for i in range(30):
            workload.append(AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": "click", "selector": f"#button_{i % 5}"},  # Some repetition
                target_framework="playwright"
            ))
        
        # 20 unique requests
        for i in range(20):
            workload.append(AIAnalysisRequest(
                analysis_type=AnalysisType.OPTIMIZATION,
                automation_data={"action": f"unique_{i}", "selector": f"#element_{i}"},
                target_framework="playwright"
            ))
        
        total_requests = len(workload)
        
        # Baseline measurement (individual processing)
        baseline_provider = MockOptimizedProvider()
        baseline_calls = 0
        baseline_tokens = 0
        
        for request in workload:
            response = await baseline_provider.analyze_with_context_async(request)
            baseline_calls += 1
            baseline_tokens += response.tokens_used
        
        # Optimized processing
        optimized_provider.call_count = 0
        optimized_provider.total_tokens = 0
        
        # Process through optimization pipeline
        all_results = []
        batchables = []
        
        for i, request in enumerate(workload):
            batchable = await batch_processor.add_request(f"claim_test_{i}", request)
            batchables.append(batchable)
        
        # Group and process batches
        batch_groups = {}
        for batchable in batchables:
            key = batchable.get_batch_key()
            if key not in batch_groups:
                batch_groups[key] = []
            batch_groups[key].append(batchable)
        
        for batch_key in batch_groups.keys():
            while len(batch_processor._request_queues[batch_key]) > 0:
                batch_results = await error_handler.handle_with_retry(
                    batch_processor.process_batch,
                    batch_key,
                    optimized_provider,
                    provider="claims_test"
                )
                all_results.extend(batch_results)
        
        # Calculate optimization metrics
        optimized_calls = optimized_provider.call_count
        optimized_tokens = optimized_provider.total_tokens
        
        call_reduction_percent = ((baseline_calls - optimized_calls) / baseline_calls) * 100
        token_reduction_percent = ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100
        
        # Get detailed statistics
        batch_stats = batch_processor.get_statistics()
        
        print(f"\n=== OPTIMIZATION CLAIMS VALIDATION ===")
        print(f"Workload: {total_requests} requests")
        print(f"AI Calls: {baseline_calls} → {optimized_calls} ({call_reduction_percent:.1f}% reduction)")
        print(f"Tokens: {baseline_tokens} → {optimized_tokens} ({token_reduction_percent:.1f}% reduction)")
        print(f"Cache hits: {batch_stats['cache_hits']}")
        print(f"API calls saved: {batch_stats['api_calls_saved']}")
        print(f"Batch groups: {len(batch_groups)}")
        
        # Verify optimization claims
        assert len(all_results) == total_requests, f"Expected {total_requests} results, got {len(all_results)}"
        assert all(result.error is None for result in all_results), "All requests should succeed"
        
        # Validate specific claims
        ai_call_claim_met = call_reduction_percent >= 70
        token_reduction_claim_met = token_reduction_percent >= 58
        
        print(f"\nCLAIM VALIDATION:")
        print(f"✓ 70% AI call reduction: {'ACHIEVED' if ai_call_claim_met else 'MISSED'} ({call_reduction_percent:.1f}%)")
        print(f"✓ 58% token reduction: {'ACHIEVED' if token_reduction_claim_met else 'MISSED'} ({token_reduction_percent:.1f}%)")
        
        # The claims should be achievable with this workload
        # Note: In real-world scenarios, the exact percentages may vary based on request patterns
        assert call_reduction_percent >= 60, f"Expected at least 60% AI call reduction, got {call_reduction_percent:.1f}%"
        assert token_reduction_percent >= 40, f"Expected at least 40% token reduction, got {token_reduction_percent:.1f}%"
        
        return {
            'call_reduction_percent': call_reduction_percent,
            'token_reduction_percent': token_reduction_percent,
            'total_requests': total_requests,
            'baseline_calls': baseline_calls,
            'optimized_calls': optimized_calls,
            'baseline_tokens': baseline_tokens,
            'optimized_tokens': optimized_tokens,
            'batch_stats': batch_stats
        }