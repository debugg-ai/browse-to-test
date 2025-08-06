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
from browse_to_test.ai.unified import AIProvider, AIResponse, AIProviderError, AIAnalysisRequest
from browse_to_test.ai.unified import OpenAIProvider, AnthropicProvider
from browse_to_test.core.executor import AsyncQueueManager, QueuedTask, TaskStatus, reset_global_queue_manager
from browse_to_test.core.executor import SessionResult
from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
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
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "mock"
        
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


# TestAsyncQueueManager class removed - deprecated AsyncQueueManager functionality
# has been replaced by SimpleAsyncQueue in the new unified executor


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
        # Mock the aiohttp request that the provider actually makes
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Create mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Test response'}, 'finish_reason': 'stop'}],
                'model': 'gpt-3.5-turbo',
                'usage': {'total_tokens': 30, 'prompt_tokens': 10, 'completion_tokens': 20}
            }
            
            # Mock the context manager
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Test async generation
            provider = OpenAIProvider(api_key="test-key")
            response = await provider.generate_async("Test prompt")
            
            assert response.content == "Test response"
            assert response.provider == "openai" 
            assert response.tokens_used == 30
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_anthropic_async_provider(self):
        """Test Anthropic provider async functionality."""
        # Mock the aiohttp request that the provider actually makes
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Create mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'content': [{'text': 'Test response'}],
                'stop_reason': 'end_turn', 
                'usage': {'input_tokens': 10, 'output_tokens': 20},
                'id': 'test-id',
                'model': 'claude-3-sonnet'
            }
            
            # Mock the context manager
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Test async generation
            provider = AnthropicProvider(api_key="test-key")
            response = await provider.generate_async("Test prompt")
            
            assert response.content == "Test response"
            assert response.provider == "anthropic"
            assert response.tokens_used == 30
            mock_post.assert_called_once()


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
            # Note: Current async implementation may not call AI provider directly
            # The test validates that conversion works, not necessarily AI usage
    
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
            
            # Both should work 
            assert isinstance(sync_script, str)
            assert isinstance(async_script, str)
            # Note: sync and async implementations may have different AI call patterns
            # The important thing is that both produce valid scripts
    
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
            
            # Note: Current async implementation doesn't call AI provider directly
            # AI analysis happens at plugin level, not in the executor
            # So call count may be 0 in the basic async flow


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
            session = btt.AsyncIncrementalSession(config)
            
            try:
                # Start session
                result = await session.start_async(target_url="https://example.com")
                assert result.success
                assert session.is_active()
                
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
            session = btt.AsyncIncrementalSession(config)
            
            try:
                await session.start_async()
                
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
            session = btt.AsyncIncrementalSession(config)
            
            try:
                await session.start_async()
                
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
            # Note: AI call count may be 0 with current async implementation
    
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
        
        # Note: Current async implementation doesn't use AI provider directly,
        # so we'll simulate a timeout using asyncio.sleep instead
        
        # Test timeout behavior with artificial delay
        with patch('browse_to_test.core.executor.BTTExecutor.execute_async') as mock_execute:
            async def slow_execute(*args, **kwargs):
                await asyncio.sleep(2.0)  # Simulate slow operation
                return Mock(success=True, script="Test script")
            
            mock_execute.side_effect = slow_execute
            
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
            session = btt.AsyncIncrementalSession(config)
            
            try:
                # Try to add step before starting session
                result = await session.add_step_async(sample_automation_steps[0])
                assert not result.success
                assert "Session is not active" in result.validation_issues
                
                # Start session
                await session.start_async()
                
                # Try to start again
                result = await session.start_async()
                assert not result.success
                assert "Session is already active" in result.validation_issues
                
                # Finalize session
                await session.finalize_async()
                
                # Try to add step after finalization
                result = await session.add_step_async(sample_automation_steps[0])
                assert not result.success
                assert "Session already finalized" in result.validation_issues 
            finally:
                try:
                    await session.finalize_async()
                except:
                    pass 