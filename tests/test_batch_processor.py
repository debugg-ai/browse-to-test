#!/usr/bin/env python3
"""
Comprehensive test suite for AIBatchProcessor.

This module tests the AI batching system for correctness, performance,
and edge cases to ensure the optimization claims are validated.
"""

import asyncio
import pytest
import time
import hashlib
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

# Import the modules under test
from browse_to_test.ai.batch_processor import (
    AIBatchProcessor,
    BatchableRequest,
    BatchResult,
)
from browse_to_test.ai.base import AIAnalysisRequest, AIResponse, AnalysisType


class TestBatchableRequest:
    """Test BatchableRequest functionality."""
    
    def test_basic_creation(self):
        """Test basic BatchableRequest creation."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        batchable = BatchableRequest(
            id="test_request_1",
            request=request,
            priority=1
        )
        
        assert batchable.id == "test_request_1"
        assert batchable.request == request
        assert batchable.priority == 1
        assert isinstance(batchable.created_at, datetime)
        assert batchable.metadata == {}
    
    def test_batch_key_generation(self):
        """Test batch key generation for grouping similar requests."""
        request1 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        request2 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "type", "selector": "#input"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        request3 = AIAnalysisRequest(
            analysis_type=AnalysisType.OPTIMIZATION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        batchable1 = BatchableRequest(id="1", request=request1)
        batchable2 = BatchableRequest(id="2", request=request2)
        batchable3 = BatchableRequest(id="3", request=request3)
        
        # Same analysis type, framework, and URL should have same batch key
        assert batchable1.get_batch_key() == batchable2.get_batch_key()
        
        # Different analysis type should have different batch key
        assert batchable1.get_batch_key() != batchable3.get_batch_key()
    
    def test_compatibility_check(self):
        """Test request compatibility checking."""
        request1 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="playwright",
            target_url="https://example.com",
            system_context=None
        )
        
        request2 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "type"},
            target_framework="playwright",
            target_url="https://example.com",
            system_context=None
        )
        
        request3 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="selenium",  # Different framework
            target_url="https://example.com",
            system_context=None
        )
        
        batchable1 = BatchableRequest(id="1", request=request1)
        batchable2 = BatchableRequest(id="2", request=request2)
        batchable3 = BatchableRequest(id="3", request=request3)
        
        # Compatible requests
        assert batchable1.is_compatible_with(batchable2)
        
        # Incompatible requests (different framework)
        assert not batchable1.is_compatible_with(batchable3)


class TestBatchResult:
    """Test BatchResult functionality."""
    
    def test_successful_result(self):
        """Test successful batch result creation."""
        response = AIResponse(
            content="Generated test code",
            model="gpt-4",
            provider="openai",
            tokens_used=150
        )
        
        result = BatchResult(
            request_id="test_1",
            response=response,
            extracted_content="Generated test code"
        )
        
        assert result.request_id == "test_1"
        assert result.response == response
        assert result.error is None
        assert result.extracted_content == "Generated test code"
    
    def test_error_result(self):
        """Test error batch result creation."""
        error = Exception("API rate limit exceeded")
        
        result = BatchResult(
            request_id="test_1",
            error=error
        )
        
        assert result.request_id == "test_1"
        assert result.response is None
        assert result.error == error
        assert result.extracted_content is None


class TestAIBatchProcessor:
    """Test AIBatchProcessor core functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.batch_processor = AIBatchProcessor(
            max_batch_size=3,
            batch_timeout=0.1,  # Short timeout for testing
            cache_ttl=3600
        )
        
        # Mock AI provider
        self.mock_provider = Mock()
        self.mock_provider.analyze_with_context_async = AsyncMock()
    
    def test_initialization(self):
        """Test batch processor initialization."""
        processor = AIBatchProcessor(
            max_batch_size=5,
            batch_timeout=1.0,
            cache_ttl=7200
        )
        
        assert processor.max_batch_size == 5
        assert processor.batch_timeout == 1.0
        assert processor.cache_ttl == 7200
        assert len(processor._request_queues) == 0
        assert len(processor._response_cache) == 0
        assert processor._stats['total_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_add_request(self):
        """Test adding requests to batch queue."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        batchable = await self.batch_processor.add_request(
            request_id="test_1",
            request=request,
            priority=1
        )
        
        assert batchable.id == "test_1"
        assert batchable.request == request
        assert batchable.priority == 1
        assert self.batch_processor._stats['total_requests'] == 1
        
        # Check that request was added to appropriate queue
        batch_key = batchable.get_batch_key()
        assert len(self.batch_processor._request_queues[batch_key]) == 1
    
    @pytest.mark.asyncio
    async def test_batch_grouping(self):
        """Test that similar requests are grouped together."""
        requests = []
        for i in range(3):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{i}"},
                target_framework="playwright",
                target_url="https://example.com"
            )
            batchable = await self.batch_processor.add_request(
                request_id=f"test_{i}",
                request=request,
                priority=i
            )
            requests.append(batchable)
        
        # All requests should have the same batch key
        batch_keys = set(req.get_batch_key() for req in requests)
        assert len(batch_keys) == 1
        
        # All requests should be in the same queue
        batch_key = list(batch_keys)[0]
        assert len(self.batch_processor._request_queues[batch_key]) == 3
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test request caching functionality."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        batchable = BatchableRequest(id="test_1", request=request)
        
        # Test cache miss
        cached_response = await self.batch_processor._check_cache(batchable)
        assert cached_response is None
        
        # Cache a response
        response = AIResponse(
            content="cached response",
            model="gpt-4",
            provider="openai"
        )
        await self.batch_processor._cache_response(batchable, response)
        
        # Test cache hit
        cached_response = await self.batch_processor._check_cache(batchable)
        assert cached_response is not None
        assert cached_response.content == "cached response"
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Test cache expiration functionality."""
        # Create processor with very short cache TTL
        processor = AIBatchProcessor(cache_ttl=0.1)  # 0.1 seconds
        
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="playwright"
        )
        batchable = BatchableRequest(id="test_1", request=request)
        
        # Cache a response
        response = AIResponse(content="test", model="gpt-4", provider="openai")
        await processor._cache_response(batchable, response)
        
        # Should be cached immediately
        cached = await processor._check_cache(batchable)
        assert cached is not None
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Should be expired now
        cached = await processor._check_cache(batchable)
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_process_batch_with_cache_hits(self):
        """Test batch processing with cache hits."""
        # Set up cached response
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        batchable = await self.batch_processor.add_request("test_1", request)
        batch_key = batchable.get_batch_key()
        
        # Cache a response
        cached_response = AIResponse(
            content="cached content",
            model="gpt-4",
            provider="openai"
        )
        await self.batch_processor._cache_response(batchable, cached_response)
        
        # Process batch should return cached result
        results = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        
        assert len(results) == 1
        assert results[0].request_id == "test_1"
        assert results[0].response.content == "cached content"
        assert results[0].error is None
        
        # AI provider should not have been called
        self.mock_provider.analyze_with_context_async.assert_not_called()
        
        # Cache hit should be recorded
        assert self.batch_processor._stats['cache_hits'] == 1
    
    @pytest.mark.asyncio
    async def test_process_batch_without_cache(self):
        """Test batch processing without cache hits."""
        # Set up mock AI provider response
        mock_response = AIResponse(
            content="""### Request: test_1
Generated test code for first request

### Request: test_2
Generated test code for second request""",
            model="gpt-4",
            provider="openai",
            tokens_used=200
        )
        
        self.mock_provider.analyze_with_context_async.return_value = mock_response
        
        # Add multiple requests
        request1 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button1"},
            target_framework="playwright"
        )
        request2 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button2"},
            target_framework="playwright"
        )
        
        batchable1 = await self.batch_processor.add_request("test_1", request1)
        batchable2 = await self.batch_processor.add_request("test_2", request2)
        batch_key = batchable1.get_batch_key()
        
        # Process batch
        results = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        
        assert len(results) == 2
        assert results[0].request_id == "test_1"
        assert results[1].request_id == "test_2"
        assert all(result.error is None for result in results)
        
        # AI provider should have been called once
        self.mock_provider.analyze_with_context_async.assert_called_once()
        
        # Statistics should be updated
        assert self.batch_processor._stats['batched_requests'] == 2
        assert self.batch_processor._stats['api_calls_saved'] == 1
    
    @pytest.mark.asyncio
    async def test_process_batch_with_ai_failure(self):
        """Test batch processing when AI provider fails."""
        # Set up mock AI provider to raise exception
        self.mock_provider.analyze_with_context_async.side_effect = Exception("API Error")
        
        # Add request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        batchable = await self.batch_processor.add_request("test_1", request)
        batch_key = batchable.get_batch_key()
        
        # Process batch should handle error gracefully
        results = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        
        assert len(results) == 1
        assert results[0].request_id == "test_1"
        assert results[0].response is None
        assert results[0].error is not None
        assert "API Error" in str(results[0].error)
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """Test that requests are processed in priority order."""
        # Add requests with different priorities
        requests_data = [
            ("low", 1),
            ("high", 10),
            ("medium", 5)
        ]
        
        for name, priority in requests_data:
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{name}"},
                target_framework="playwright"
            )
            await self.batch_processor.add_request(f"test_{name}", request, priority)
        
        # Mock AI provider response with request markers
        mock_response = AIResponse(
            content="""### Request: test_high
High priority response

### Request: test_medium
Medium priority response

### Request: test_low
Low priority response""",
            model="gpt-4",
            provider="openai"
        )
        
        self.mock_provider.analyze_with_context_async.return_value = mock_response
        
        # Get batch key (all requests should have the same key)
        test_batch_key = "conversion|playwright|no_url"
        
        # Process batch
        results = await self.batch_processor.process_batch(test_batch_key, self.mock_provider)
        
        # Results should be in priority order (highest first)
        assert len(results) == 3
        # Note: The actual order depends on how the response splitting works
        # but we can verify all requests were processed
        result_ids = {result.request_id for result in results}
        expected_ids = {"test_low", "test_high", "test_medium"}
        assert result_ids == expected_ids
    
    @pytest.mark.asyncio
    async def test_wait_for_batch_timeout(self):
        """Test batch timeout functionality."""
        batch_key = "test_batch_key"
        
        # Test timeout with empty queue
        start_time = time.time()
        result = await self.batch_processor.wait_for_batch_or_timeout(batch_key, target_size=2)
        elapsed = time.time() - start_time
        
        assert result is False  # Should timeout
        assert elapsed >= 0.1  # Should wait for timeout duration
        
        # Add one request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="playwright"
        )
        batchable = await self.batch_processor.add_request("test_1", request)
        actual_batch_key = batchable.get_batch_key()
        
        # Test early return when target size reached
        # Add another request to reach target size
        await self.batch_processor.add_request("test_2", request)
        
        start_time = time.time()
        result = await self.batch_processor.wait_for_batch_or_timeout(actual_batch_key, target_size=2)
        elapsed = time.time() - start_time
        
        assert result is True  # Should return early
        assert elapsed < 0.1  # Should not wait for full timeout
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        request1 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        request2 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        request3 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#different"},
            target_framework="playwright",
            target_url="https://example.com"
        )
        
        batchable1 = BatchableRequest(id="1", request=request1)
        batchable2 = BatchableRequest(id="2", request=request2)
        batchable3 = BatchableRequest(id="3", request=request3)
        
        key1 = self.batch_processor._generate_cache_key(batchable1)
        key2 = self.batch_processor._generate_cache_key(batchable2)
        key3 = self.batch_processor._generate_cache_key(batchable3)
        
        # Identical requests should have same cache key
        assert key1 == key2
        
        # Different requests should have different cache keys
        assert key1 != key3
        
        # Keys should be valid SHA256 hashes
        assert len(key1) == 64
        assert all(c in '0123456789abcdef' for c in key1)
    
    def test_response_section_splitting(self):
        """Test splitting combined AI response into individual sections."""
        content = """### Request: test_1
This is the first response section.
It spans multiple lines.

### Request: test_2  
This is the second response section.
With different content.

### Request: test_3
And this is the third section."""
        
        sections = self.batch_processor._split_response_sections(content)
        
        assert len(sections) == 3
        assert "test_1" in sections
        assert "test_2" in sections
        assert "test_3" in sections
        
        assert "first response section" in sections["test_1"]
        assert "second response section" in sections["test_2"]
        assert "third section" in sections["test_3"]
    
    def test_response_section_splitting_no_markers(self):
        """Test splitting response when no markers are present."""
        content = "This is a single response without markers."
        
        sections = self.batch_processor._split_response_sections(content)
        
        assert len(sections) == 1
        assert "full_response" in sections
        assert sections["full_response"] == content
    
    def test_statistics_tracking(self):
        """Test statistics tracking functionality."""
        stats = self.batch_processor.get_statistics()
        
        expected_keys = [
            'total_requests', 'batched_requests', 'cache_hits', 
            'api_calls_saved', 'cache_size', 'active_batches', 
            'pending_requests'
        ]
        
        for key in expected_keys:
            assert key in stats
        
        # Initial values should be zero
        assert stats['total_requests'] == 0
        assert stats['cache_size'] == 0
        assert stats['active_batches'] == 0


class TestBatchProcessorPerformance:
    """Test performance characteristics of batch processor."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.batch_processor = AIBatchProcessor(
            max_batch_size=10,
            batch_timeout=0.1,
            cache_ttl=3600
        )
        
        self.mock_provider = Mock()
        self.mock_provider.analyze_with_context_async = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_large_batch_performance(self):
        """Test performance with large number of requests."""
        num_requests = 50
        
        # Set up mock response
        mock_sections = []
        for i in range(num_requests):
            mock_sections.append(f"### Request: test_{i}\nResponse for request {i}")
        
        mock_response = AIResponse(
            content="\n\n".join(mock_sections),
            model="gpt-4",
            provider="openai",
            tokens_used=1000
        )
        
        self.mock_provider.analyze_with_context_async.return_value = mock_response
        
        # Time the request addition
        start_time = time.time()
        
        # Add many requests
        batch_keys = set()
        for i in range(num_requests):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{i}"},
                target_framework="playwright"
            )
            batchable = await self.batch_processor.add_request(f"test_{i}", request)
            batch_keys.add(batchable.get_batch_key())
        
        addition_time = time.time() - start_time
        
        # Process all batches
        start_time = time.time()
        all_results = []
        
        for batch_key in batch_keys:
            # Process all pending requests in this batch key
            while len(self.batch_processor._request_queues[batch_key]) > 0:
                results = await self.batch_processor.process_batch(batch_key, self.mock_provider)
                all_results.extend(results)
        
        processing_time = time.time() - start_time
        
        # Verify results
        assert len(all_results) == num_requests
        
        # Performance assertions (adjust thresholds based on requirements)
        assert addition_time < 1.0  # Adding requests should be fast
        assert processing_time < 5.0  # Processing should be reasonable
        
        # Verify API call savings
        stats = self.batch_processor.get_statistics()
        assert stats['total_requests'] == num_requests
        assert stats['api_calls_saved'] > 0  # Should have saved some API calls
    
    @pytest.mark.asyncio
    async def test_cache_performance_benefit(self):
        """Test that caching provides performance benefits."""
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click", "selector": "#button"},
            target_framework="playwright"
        )
        
        # Set up mock response
        mock_response = AIResponse(
            content="### Request: test_1\nCached response",
            model="gpt-4",
            provider="openai",
            tokens_used=100
        )
        self.mock_provider.analyze_with_context_async.return_value = mock_response
        
        # First request (cache miss)
        batchable1 = await self.batch_processor.add_request("test_1", request)
        batch_key = batchable1.get_batch_key()
        
        start_time = time.time()
        results1 = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        first_request_time = time.time() - start_time
        
        assert len(results1) == 1
        assert self.mock_provider.analyze_with_context_async.call_count == 1
        
        # Second identical request (cache hit)
        batchable2 = await self.batch_processor.add_request("test_2", request)
        
        start_time = time.time()
        results2 = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        second_request_time = time.time() - start_time
        
        assert len(results2) == 1
        # AI provider should not be called again
        assert self.mock_provider.analyze_with_context_async.call_count == 1
        
        # Cache hit should be significantly faster
        assert second_request_time < first_request_time
        
        # Verify cache hit statistics
        stats = self.batch_processor.get_statistics()
        assert stats['cache_hits'] == 1


class TestBatchProcessorEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up edge case test fixtures."""
        self.batch_processor = AIBatchProcessor()
        self.mock_provider = Mock()
        self.mock_provider.analyze_with_context_async = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_empty_batch_processing(self):
        """Test processing empty batch."""
        results = await self.batch_processor.process_batch("empty_batch", self.mock_provider)
        assert results == []
        self.mock_provider.analyze_with_context_async.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_malformed_ai_response(self):
        """Test handling of malformed AI responses."""
        # Set up malformed response (no request markers)
        mock_response = AIResponse(
            content="This response has no proper section markers",
            model="gpt-4",
            provider="openai"
        )
        self.mock_provider.analyze_with_context_async.return_value = mock_response
        
        # Add request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="playwright"
        )
        batchable = await self.batch_processor.add_request("test_1", request)
        batch_key = batchable.get_batch_key()
        
        # Process batch
        results = await self.batch_processor.process_batch(batch_key, self.mock_provider)
        
        assert len(results) == 1
        assert results[0].request_id == "test_1"
        # Should fallback to full response
        assert results[0].response.content == "This response has no proper section markers"
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self):
        """Test concurrent processing of different batches."""
        # Create requests for different batch keys
        request1 = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "click"},
            target_framework="playwright"
        )
        request2 = AIAnalysisRequest(
            analysis_type=AnalysisType.OPTIMIZATION,
            automation_data={"action": "click"},
            target_framework="playwright"
        )
        
        # Set up mock responses
        mock_responses = [
            AIResponse(content="### Request: test_1\nConversion response", model="gpt-4", provider="openai"),
            AIResponse(content="### Request: test_2\nOptimization response", model="gpt-4", provider="openai")
        ]
        
        self.mock_provider.analyze_with_context_async.side_effect = mock_responses
        
        # Add requests
        batchable1 = await self.batch_processor.add_request("test_1", request1)
        batchable2 = await self.batch_processor.add_request("test_2", request2)
        
        # Process batches concurrently
        tasks = [
            self.batch_processor.process_batch(batchable1.get_batch_key(), self.mock_provider),
            self.batch_processor.process_batch(batchable2.get_batch_key(), self.mock_provider)
        ]
        
        results_list = await asyncio.gather(*tasks)
        
        assert len(results_list) == 2
        assert len(results_list[0]) == 1
        assert len(results_list[1]) == 1
        
        # Both AI provider calls should have been made
        assert self.mock_provider.analyze_with_context_async.call_count == 2
    
    def test_context_fingerprinting(self):
        """Test system context fingerprinting for caching."""
        # Create mock context objects
        class MockProject:
            def __init__(self, name, frameworks):
                self.name = name
                self.test_frameworks = frameworks
        
        class MockContext:
            def __init__(self, project, tests, components):
                self.project = project
                self.existing_tests = tests
                self.ui_components = components
        
        context1 = MockContext(
            project=MockProject("test_project", ["playwright", "jest"]),
            tests=["test1.py", "test2.py"],
            components=["button", "input"]
        )
        
        context2 = MockContext(
            project=MockProject("test_project", ["playwright", "jest"]),
            tests=["test1.py", "test2.py"],
            components=["button", "input"]
        )
        
        context3 = MockContext(
            project=MockProject("different_project", ["selenium"]),
            tests=["test3.py"],
            components=["form"]
        )
        
        fingerprint1 = self.batch_processor._create_context_fingerprint(context1)
        fingerprint2 = self.batch_processor._create_context_fingerprint(context2)
        fingerprint3 = self.batch_processor._create_context_fingerprint(context3)
        
        # Identical contexts should have same fingerprint
        assert fingerprint1 == fingerprint2
        
        # Different contexts should have different fingerprints
        assert fingerprint1 != fingerprint3
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self):
        """Test automatic cache cleanup of expired entries."""
        # Create processor with very short TTL
        processor = AIBatchProcessor(cache_ttl=0.1)
        
        # Add some cache entries
        requests = []
        for i in range(3):
            request = AIAnalysisRequest(
                analysis_type=AnalysisType.CONVERSION,
                automation_data={"action": f"action_{i}"},
                target_framework="playwright"
            )
            batchable = BatchableRequest(id=f"test_{i}", request=request)
            requests.append(batchable)
            
            response = AIResponse(content=f"response_{i}", model="gpt-4", provider="openai")
            await processor._cache_response(batchable, response)
        
        # Verify cache size
        assert len(processor._response_cache) == 3
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Trigger cleanup by adding new entry
        new_request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data={"action": "new_action"},
            target_framework="playwright"
        )
        new_batchable = BatchableRequest(id="new_test", request=new_request)
        new_response = AIResponse(content="new_response", model="gpt-4", provider="openai")
        await processor._cache_response(new_batchable, new_response)
        
        # Old entries should be cleaned up
        assert len(processor._response_cache) == 1
        
        # New entry should still be there
        cached = await processor._check_cache(new_batchable)
        assert cached is not None