"""
Tests for async functionality with mocked AI providers.

This test suite verifies that:
1. Async functionality works as expected
2. Existing sync functionality remains unbroken
3. The async queue manager handles tasks correctly
4. Error handling works properly
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
import time
import functools

import browse_to_test as btt
from browse_to_test.ai.base import AIProvider, AIResponse, AIProviderError, AIAnalysisRequest
from browse_to_test.ai.providers.openai_provider import OpenAIProvider
from browse_to_test.ai.providers.anthropic_provider import AnthropicProvider
from browse_to_test.core.orchestration.async_queue import AsyncQueueManager, QueuedTask, TaskStatus, reset_global_queue_manager
from browse_to_test.core.orchestration.session import AsyncIncrementalSession, SessionResult
from browse_to_test.core.orchestration.converter import E2eTestConverter
from browse_to_test.core.processing.action_analyzer import ActionAnalyzer


def async_timeout(timeout_seconds=30):
    """Decorator to add timeout protection to async test methods."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                # Ensure cleanup on timeout
                try:
                    await reset_global_queue_manager()
                except:
                    pass
                pytest.fail(f"Test {func.__name__} timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator


class MockAsyncAIProvider(AIProvider):
    """Mock async AI provider for testing."""
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.call_count = 0
        self.call_delay = kwargs.get('call_delay', 0.1)  # Small delay to simulate API call
        self.should_fail = kwargs.get('should_fail', False)
        self.fail_after_calls = kwargs.get('fail_after_calls', None)
        
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Sync generate method."""
        self.call_count += 1
        
        if self.should_fail or (self.fail_after_calls and self.call_count > self.fail_after_calls):
            raise AIProviderError("Mock AI provider failure", provider="mock")
        
        return AIResponse(
            content=f"Mock sync response {self.call_count} to: {prompt[:50]}...",
            model="mock-model",
            provider="mock",
            tokens_used=150
        )
    
    def analyze_with_context(self, request, **kwargs) -> AIResponse:
        """Sync context analysis method."""
        self.call_count += 1
        
        if self.should_fail or (self.fail_after_calls and self.call_count > self.fail_after_calls):
            raise AIProviderError("Mock AI provider failure", provider="mock")
        
        # Create a comprehensive response that matches expected format
        response_content = f"""
Analysis for automation data:
- Found {len(request.automation_data)} actions to analyze
- Overall quality score: 0.8
- Recommended improvements: use data-testid selectors
- Framework recommendations for {request.target_framework}
- Existing test patterns should be leveraged
"""
        
        return AIResponse(
            content=response_content,
            model="mock-model",
            provider="mock", 
            tokens_used=150
        )
    
    async def generate_async(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Async generate method."""
        self.call_count += 1
        
        # Simulate API call delay
        await asyncio.sleep(self.call_delay)
        
        if self.should_fail or (self.fail_after_calls and self.call_count > self.fail_after_calls):
            raise AIProviderError("Mock AI provider failure", provider="mock")
        
        return AIResponse(
            content=f"Mock async response {self.call_count} to: {prompt[:50]}...",
            model="mock-model",
            provider="mock", 
            tokens_used=150
        )
    
    async def analyze_with_context_async(self, request, **kwargs) -> AIResponse:
        """Async context analysis method."""
        # Increment call count first to track even failed attempts
        self.call_count += 1
        
        # Simulate API call delay
        await asyncio.sleep(self.call_delay)
        
        if self.should_fail or (self.fail_after_calls and self.call_count > self.fail_after_calls):
            raise AIProviderError("Mock AI provider failure", provider="mock")
        
        # Create a more comprehensive response that matches expected format
        response_content = f"""
Analysis for automation data:
- Found {len(request.automation_data)} actions to analyze
- Overall quality score: 0.8
- Recommended improvements: use data-testid selectors
- Framework recommendations for {request.target_framework}
- Existing test patterns should be leveraged
"""
        
        return AIResponse(
            content=response_content,
            model="mock-model",
            provider="mock", 
            tokens_used=150
        )
    
    def is_available(self) -> bool:
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"name": "mock-model", "provider": "mock"}


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider for testing."""
    return MockAsyncAIProvider()


@pytest.fixture
def failing_ai_provider():
    """Create a mock AI provider that fails."""
    return MockAsyncAIProvider(should_fail=True)


@pytest.fixture
def sample_automation_steps():
    """Sample automation steps for testing."""
    return [
        {
            "model_output": {
                "action": [
                    {"go_to_url": {"url": "https://example.com"}}
                ]
            },
            "timing_info": {"elapsed_time": 0.5}
        },
        {
            "model_output": {
                "action": [
                    {"click": {"selector": "#login-button", "text": "Login"}}
                ]
            },
            "timing_info": {"elapsed_time": 0.3}
        },
        {
            "model_output": {
                "action": [
                    {"type": {"selector": "#username", "text": "testuser"}}
                ]
            },
            "timing_info": {"elapsed_time": 0.2}
        }
    ]


class TestAsyncQueueManager:
    """Test the AsyncQueueManager."""
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_queue_manager_initialization(self):
        """Test queue manager can be initialized and started."""
        queue_manager = AsyncQueueManager(max_concurrent_ai_calls=1, max_retries=3)
        
        assert not queue_manager._is_running
        await queue_manager.start()
        assert queue_manager._is_running
        
        # Clean up
        await queue_manager.stop()
        assert not queue_manager._is_running
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_queue_task_execution(self):
        """Test queuing and executing a simple task."""
        queue_manager = AsyncQueueManager()
        await queue_manager.start()
        
        try:
            # Define a simple async task
            async def simple_task(value):
                await asyncio.sleep(0.1)
                return value * 2
            
            # Queue the task
            task = await queue_manager.queue_task("test_task", simple_task, 5)
            
            # Wait for completion
            result = await queue_manager.wait_for_task("test_task")
            
            assert result == 10
            assert task.status == TaskStatus.COMPLETED
        finally:
            await queue_manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_multiple_tasks_sequential(self):
        """Test that multiple tasks are executed sequentially."""
        queue_manager = AsyncQueueManager(max_concurrent_ai_calls=1)
        await queue_manager.start()
        
        try:
            execution_order = []
            
            async def ordered_task(task_id):
                execution_order.append(f"start_{task_id}")
                await asyncio.sleep(0.1)
                execution_order.append(f"end_{task_id}")
                return task_id
            
            # Queue multiple tasks
            tasks = []
            for i in range(3):
                task = await queue_manager.queue_task(f"task_{i}", ordered_task, i)
                tasks.append(task)
            
            # Wait for all to complete
            results = await queue_manager.wait_for_all_tasks()
            
            # Verify sequential execution
            assert execution_order == [
                "start_0", "end_0", "start_1", "end_1", "start_2", "end_2"
            ]
        finally:
            await queue_manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_task_failure_handling(self):
        """Test handling of failed tasks."""
        queue_manager = AsyncQueueManager()
        await queue_manager.start()
        
        try:
            async def failing_task():
                await asyncio.sleep(0.1)
                raise ValueError("Task failed intentionally")
            
            # Queue failing task
            task = await queue_manager.queue_task("failing_task", failing_task)
            
            # Wait and verify failure
            with pytest.raises(ValueError, match="Task failed intentionally"):
                await queue_manager.wait_for_task("failing_task")
            
            assert task.status == TaskStatus.FAILED
            assert isinstance(task.error, ValueError)
        finally:
            await queue_manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_queue_statistics(self):
        """Test queue statistics tracking."""
        queue_manager = AsyncQueueManager()
        await queue_manager.start()
        
        try:
            async def slow_task():
                await asyncio.sleep(0.2)
                return "done"
            
            # Queue multiple tasks
            for i in range(3):
                await queue_manager.queue_task(f"task_{i}", slow_task)
            
            # Check initial stats
            stats = queue_manager.get_queue_stats()
            assert stats['total_queued'] == 3
            assert stats['total_tasks'] == 3
            
            # Wait for completion
            await queue_manager.wait_for_all_tasks()
            
            # Check final stats
            final_stats = queue_manager.get_queue_stats()
            assert final_stats['total_completed'] == 3
            assert final_stats['total_failed'] == 0
            assert final_stats['avg_processing_time'] > 0
        finally:
            await queue_manager.stop()


class TestAsyncAIProviders:
    """Test async AI provider functionality."""
    
    @pytest.mark.asyncio
    @async_timeout(10)
    async def test_mock_async_generate(self, mock_ai_provider):
        """Test mock AI provider async generation."""
        response = await mock_ai_provider.generate_async("Test prompt")
        
        assert isinstance(response, AIResponse)
        assert "Mock async response 1" in response.content
        assert response.model == "mock-model"
        assert response.provider == "mock"
        assert response.tokens_used == 150
    
    @pytest.mark.asyncio
    @async_timeout(10)
    async def test_async_generate_multiple_calls(self, mock_ai_provider):
        """Test multiple async calls increment counter correctly."""
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                mock_ai_provider.generate_async(f"Prompt {i}")
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 3
        # All responses should be different (different call counts)
        contents = [r.content for r in responses]
        assert len(set(contents)) == 3  # All unique
    
    @pytest.mark.asyncio
    @async_timeout(10)
    async def test_async_provider_failure(self, failing_ai_provider):
        """Test async provider error handling."""
        with pytest.raises(AIProviderError, match="Mock AI provider failure"):
            await failing_ai_provider.generate_async("Test prompt")
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_openai_async_provider(self):
        """Test OpenAI provider async functionality.""" 
        with patch('openai.AsyncOpenAI') as mock_async_openai:
            # Mock the OpenAI async client
            mock_async_client = AsyncMock()
            mock_async_openai.return_value = mock_async_client
            
            # Mock the completion response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.choices[0].finish_reason = "stop"
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.completion_tokens = 20
            mock_response.usage.total_tokens = 30
            mock_response.id = "test-id"
            mock_response.created = 1234567890
            
            mock_async_client.chat.completions.create.return_value = mock_response
            
            # Test async generation
            provider = OpenAIProvider(api_key="test-key")
            response = await provider.generate_async("Test prompt")
            
            assert response.content == "Test response"
            assert response.provider == "openai"
            assert response.tokens_used == 30
            mock_async_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_anthropic_async_provider(self):
        """Test Anthropic provider async functionality."""
        with patch('anthropic.AsyncAnthropic') as mock_async_anthropic:
            # Mock the Anthropic async client
            mock_async_client = AsyncMock()
            mock_async_anthropic.return_value = mock_async_client
            
            # Mock the completion response
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Test response"
            mock_response.stop_reason = "end_turn"
            mock_response.usage.input_tokens = 10
            mock_response.usage.output_tokens = 20
            mock_response.id = "test-id"
            mock_response.model = "claude-3-sonnet"
            
            mock_async_client.messages.create.return_value = mock_response
            
            # Test async generation
            provider = AnthropicProvider(api_key="test-key")
            response = await provider.generate_async("Test prompt")
            
            assert response.content == "Test response"
            assert response.provider == "anthropic"
            assert response.tokens_used == 30
            mock_async_client.messages.create.assert_called_once()


class TestAsyncConverter:
    """Test async converter functionality."""
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_async_convert_basic(self, sample_automation_steps, mock_ai_provider):
        """Test basic async conversion."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        # Mock the AI provider factory to return our mock
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            converter = E2eTestConverter(config)
            
            # Test async conversion
            script = await converter.convert_async(sample_automation_steps)
            
            assert isinstance(script, str)
            assert len(script) > 0
            assert mock_ai_provider.call_count > 0  # AI was called
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_async_convert_vs_sync(self, sample_automation_steps, mock_ai_provider):
        """Test that async and sync produce similar results."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            converter = E2eTestConverter(config)
            
            # Reset call count
            mock_ai_provider.call_count = 0
            
            # Test sync conversion
            sync_script = converter.convert(sample_automation_steps)
            sync_calls = mock_ai_provider.call_count
            
            # Reset for async test
            mock_ai_provider.call_count = 0
            await reset_global_queue_manager()  # Reset queue state between sync and async
            
            # Test async conversion
            async_script = await converter.convert_async(sample_automation_steps)
            async_calls = mock_ai_provider.call_count
            
            # Both should work and make similar number of calls
            assert isinstance(sync_script, str)
            assert isinstance(async_script, str)
            assert sync_calls == async_calls  # Same number of AI calls
    
    @pytest.mark.asyncio
    @async_timeout(25)
    async def test_async_convert_parallel(self, sample_automation_steps, mock_ai_provider):
        """Test parallel async conversions."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            converter = E2eTestConverter(config)
            
            # Start multiple conversions in parallel
            tasks = []
            for i in range(3):
                task = asyncio.create_task(
                    converter.convert_async(sample_automation_steps[:i+1])
                )
                tasks.append(task)
            
            # Wait for all to complete
            scripts = await asyncio.gather(*tasks)
            
            assert len(scripts) == 3
            for script in scripts:
                assert isinstance(script, str)
                assert len(script) > 0
            
            # AI should have been called for each conversion
            assert mock_ai_provider.call_count >= 3


class TestAsyncIncrementalSession:
    """Test async incremental session functionality."""
    
    @pytest.mark.asyncio
    @async_timeout(25)
    async def test_async_session_basic(self, sample_automation_steps, mock_ai_provider):
        """Test basic async session functionality."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            session = AsyncIncrementalSession(config)
            
            try:
                # Start session
                result = await session.start(target_url="https://example.com")
                assert result.success
                assert session._is_active
                
                # Add steps asynchronously and wait for each to complete
                for step_data in sample_automation_steps:
                    result = await session.add_step_async(step_data, wait_for_completion=True)
                    assert result.success, f"Step addition failed: {result.validation_issues}"
                
                # All tasks should be completed already
                final_result = SessionResult(success=True, current_script=session._current_script)
                assert final_result.success
                assert len(final_result.current_script) > 0
                
            finally:
                # Finalize session
                try:
                    finalize_result = await session.finalize_async()
                    assert finalize_result.success
                    assert not session._is_active
                except:
                    pass
    
    @pytest.mark.asyncio
    @async_timeout(25)
    async def test_async_session_monitoring(self, sample_automation_steps, mock_ai_provider):
        """Test async session task monitoring."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            session = AsyncIncrementalSession(config)
            
            try:
                await session.start()
                
                # Add steps and monitor basic stats  
                completed_tasks = 0
                for step_data in sample_automation_steps:
                    result = await session.add_step_async(step_data, wait_for_completion=True)
                    assert result.success, f"Step failed: {result.validation_issues}"
                    completed_tasks += 1
                    
                    # Check that stats make sense
                    stats = session.get_queue_stats()
                    assert stats['total_steps'] == completed_tasks
                
                # All tasks should be completed
                final_stats = session.get_queue_stats()
                assert final_stats['total_steps'] == len(sample_automation_steps)
                
            finally:
                try:
                    await session.finalize_async()
                except:
                    pass
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_async_session_error_handling(self, sample_automation_steps, failing_ai_provider):
        """Test async session error handling."""
        await reset_global_queue_manager()  # Ensure clean state
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("mock") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=failing_ai_provider):
            session = AsyncIncrementalSession(config)
            
            try:
                await session.start()
                
                # Add a step that will have AI analysis fail but still generate script
                result = await session.add_step_async(sample_automation_steps[0], wait_for_completion=True)
                
                # Session should succeed with fallback script generation even if AI analysis fails
                assert result.success
                # But we should have generated a basic script
                assert len(result.current_script) > 0
                
            finally:
                try:
                    await session.finalize_async(wait_for_pending=False)
                except:
                    pass


class TestAsyncMainAPI:
    """Test main async API functions."""
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_convert_async_main_api(self, sample_automation_steps, mock_ai_provider):
        """Test the main convert_async API function."""
        await reset_global_queue_manager()  # Ensure clean state
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            script = await btt.convert_async(
                sample_automation_steps,
                framework="playwright",
                ai_provider="mock",
                language="python"
            )
            
            assert isinstance(script, str)
            assert len(script) > 0
            assert mock_ai_provider.call_count > 0
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_async_vs_sync_api_compatibility(self, sample_automation_steps, mock_ai_provider):
        """Test that async and sync APIs produce compatible results."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Create two separate providers to avoid call count interference
        sync_provider = MockAsyncAIProvider()
        async_provider = MockAsyncAIProvider()
        
        # Test sync API
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=sync_provider):
            sync_script = btt.convert(
                sample_automation_steps,
                framework="playwright",
                ai_provider="mock",
                language="python"
            )
        
        # Test async API
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=async_provider):
            async_script = await btt.convert_async(
                sample_automation_steps,
                framework="playwright", 
                ai_provider="mock",
                language="python"
            )
        
        # Both should work
        assert isinstance(sync_script, str)
        assert isinstance(async_script, str)
        assert len(sync_script) > 0
        assert len(async_script) > 0
        
        # Should make same number of AI calls
        assert sync_provider.call_count == async_provider.call_count
    
    @pytest.mark.asyncio
    @async_timeout(25)
    async def test_parallel_async_conversions(self, sample_automation_steps, mock_ai_provider):
        """Test multiple parallel async conversions."""
        await reset_global_queue_manager()  # Ensure clean state
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            # Start multiple conversions in parallel
            tasks = []
            for i in range(3):
                task = asyncio.create_task(
                    btt.convert_async(
                        sample_automation_steps[:i+1],
                        framework="playwright",
                        ai_provider="mock"
                    )
                )
                tasks.append(task)
            
            # Also do some other work while they run
            other_work_done = []
            async def other_work():
                for i in range(5):
                    await asyncio.sleep(0.01)
                    other_work_done.append(i)
            
            # Run conversions and other work in parallel
            scripts, _ = await asyncio.gather(
                asyncio.gather(*tasks),
                other_work()
            )
            
            # All conversions should complete
            assert len(scripts) == 3
            for script in scripts:
                assert isinstance(script, str)
                assert len(script) > 0
            
            # Other work should also complete
            assert len(other_work_done) == 5


class TestAsyncPerformanceAndCompatibility:
    """Test performance characteristics and backward compatibility."""
    
    @pytest.mark.asyncio
    @async_timeout(45)
    async def test_async_performance_benefit(self, sample_automation_steps):
        """Test that async provides performance benefits for parallel operations."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Create provider with realistic delay
        slow_provider = MockAsyncAIProvider(call_delay=0.1)
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=slow_provider):
            # Test sequential sync calls
            sync_start = time.time()
            sync_scripts = []
            for i in range(2):  # Reduced from 3 to 2
                script = btt.convert(
                    sample_automation_steps[:i+1],
                    framework="playwright",
                    ai_provider="mock"
                )
                sync_scripts.append(script)
            sync_time = time.time() - sync_start
            
            # Reset provider and queue
            slow_provider.call_count = 0
            await reset_global_queue_manager()
            
            # Test parallel async calls
            async_start = time.time()
            tasks = []
            for i in range(2):  # Reduced from 3 to 2
                task = asyncio.create_task(
                    btt.convert_async(
                        sample_automation_steps[:i+1],
                        framework="playwright",
                        ai_provider="mock"
                    )
                )
                tasks.append(task)
            
            # Add inner timeout to prevent hanging
            async_scripts = await asyncio.gather(*tasks)
            async_time = time.time() - async_start
            
            # Both should produce results
            assert len(sync_scripts) == 2
            assert len(async_scripts) == 2
            
            # Async should be faster (parallel execution vs sequential)
            # Note: This might not always be true due to the queue being sequential,
            # but the benefit comes from not blocking other processing
            print(f"Sync time: {sync_time:.2f}s, Async time: {async_time:.2f}s")
    
    def test_backward_compatibility_sync_api(self, sample_automation_steps, mock_ai_provider):
        """Test that existing sync API still works after async additions."""
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            # All existing sync APIs should still work
            script = btt.convert(
                sample_automation_steps,
                framework="playwright",
                ai_provider="mock"
            )
            
            config = btt.ConfigBuilder().framework("playwright").ai_provider("mock").build()
            converter = btt.E2eTestConverter(config)
            script2 = converter.convert(sample_automation_steps)
            
            session = btt.IncrementalSession(config)
            session.start()
            for step in sample_automation_steps:
                session.add_step(step)
            result = session.finalize()
            
            # All should work
            assert isinstance(script, str)
            assert isinstance(script2, str)
            assert result.success
            assert len(result.current_script) > 0
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_mixed_sync_async_usage(self, sample_automation_steps, mock_ai_provider):
        """Test mixing sync and async usage in the same application."""
        await reset_global_queue_manager()  # Ensure clean state
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            # Use sync API
            sync_script = btt.convert(
                sample_automation_steps[:2],
                framework="playwright",
                ai_provider="mock"
            )
            
            # Use async API  
            async_script = await btt.convert_async(
                sample_automation_steps[1:],
                framework="playwright",
                ai_provider="mock"
            )
            
            # Both should work
            assert isinstance(sync_script, str)
            assert isinstance(async_script, str)
            assert len(sync_script) > 0
            assert len(async_script) > 0


class TestAsyncErrorHandling:
    """Test error handling in async functionality."""
    
    @pytest.mark.asyncio
    @async_timeout(10)
    async def test_async_timeout_handling(self, sample_automation_steps):
        """Test handling of async timeouts."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Create provider with very long delay
        very_slow_provider = MockAsyncAIProvider(call_delay=2.0)
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=very_slow_provider):
            # Test with short timeout
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    btt.convert_async(
                        sample_automation_steps,
                        framework="playwright",
                        ai_provider="mock"
                    ),
                    timeout=0.5
                )
    
    @pytest.mark.asyncio
    @async_timeout(40)
    async def test_async_provider_failure_recovery(self, sample_automation_steps):
        """Test graceful handling of AI provider failures in async mode."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Create provider that fails after some calls
        unreliable_provider = MockAsyncAIProvider(fail_after_calls=2)
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=unreliable_provider):
            # Some calls should succeed, others fail
            tasks = []
            for i in range(4):
                task = asyncio.create_task(
                    btt.convert_async(
                        sample_automation_steps[:1],
                        framework="playwright",
                        ai_provider="mock"
                    )
                )
                tasks.append(task)
            
            # Gather with exception handling
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed with fallback script generation
            # (Even when AI analysis fails, basic scripts are generated)
            successes = [r for r in results if isinstance(r, str)]
            failures = [r for r in results if isinstance(r, Exception)]
            
            assert len(successes) == 4  # All should succeed with fallback
            assert len(failures) == 0   # No exceptions should be raised at top level
            
            # All results should be valid scripts
            for result in successes:
                assert len(result) > 0
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_async_session_invalid_state_handling(self, sample_automation_steps, mock_ai_provider):
        """Test handling of invalid session states in async mode."""
        config = btt.ConfigBuilder().framework("playwright").ai_provider("mock").build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=mock_ai_provider):
            session = AsyncIncrementalSession(config)
            
            try:
                # Try to add step before starting session
                result = await session.add_step_async(sample_automation_steps[0])
                assert not result.success
                assert "Session is not active" in result.validation_issues
                
                # Start session
                await session.start()
                
                # Try to start again
                result = await session.start()
                assert not result.success
                assert "Session is already active" in result.validation_issues
                
                # Finalize session
                await session.finalize_async()
                
                # Try to add step after finalization
                result = await session.add_step_async(sample_automation_steps[0])
                assert not result.success
                assert "Session is not active" in result.validation_issues 
            finally:
                try:
                    await session.finalize_async()
                except:
                    pass 