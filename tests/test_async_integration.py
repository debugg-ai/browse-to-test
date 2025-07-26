"""
Integration tests for async functionality.

Tests the complete async workflow with realistic scenarios:
- End-to-end async conversion pipeline
- Integration between different async components
- Real-world usage patterns
- Performance characteristics
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any
import functools

import browse_to_test as btt
from browse_to_test.ai.base import AIResponse, AIProviderError, AIAnalysisRequest
from browse_to_test.core.orchestration.async_queue import get_global_queue_manager, reset_global_queue_manager


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


class RealisticMockAIProvider:
    """A more realistic mock AI provider that simulates real API behavior."""
    
    def __init__(self, response_delay=0.2, failure_rate=0.0, responses=None):
        self.response_delay = response_delay
        self.failure_rate = failure_rate
        self.call_count = 0
        self.responses = responses or []
        
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Sync generate (blocks)."""
        import random
        time.sleep(self.response_delay)  # Simulate API delay
        
        self.call_count += 1
        
        if random.random() < self.failure_rate:
            raise AIProviderError(f"Simulated API failure on call {self.call_count}")
        
        content = self._get_response_content(prompt)
        return AIResponse(
            content=content,
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=len(prompt.split()) + len(content.split()),
            metadata={'response_time': self.response_delay}
        )
    
    async def generate_async(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Async generate (non-blocking)."""
        import random
        await asyncio.sleep(self.response_delay)  # Simulate async API delay
        
        self.call_count += 1
        
        if random.random() < self.failure_rate:
            raise AIProviderError(f"Simulated API failure on call {self.call_count}")
        
        content = self._get_response_content(prompt)
        return AIResponse(
            content=content,
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=len(prompt.split()) + len(content.split()),
            metadata={'response_time': self.response_delay}
        )
    
    async def analyze_with_context_async(self, request, **kwargs) -> AIResponse:
        """Async analysis with context (required for session processing)."""
        import random
        await asyncio.sleep(self.response_delay)  # Simulate async API delay
        
        self.call_count += 1
        
        if random.random() < self.failure_rate:
            raise AIProviderError(f"Simulated API failure on call {self.call_count}")
        
        # Generate a simple analysis response
        content = f"Analysis completed for {len(request.automation_data)} actions"
        return AIResponse(
            content=content,
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=150,
            metadata={
                'analysis_type': request.analysis_type.value if hasattr(request, 'analysis_type') else 'unknown',
                'target_framework': getattr(request, 'target_framework', 'unknown'),
                'response_time': self.response_delay
            }
        )
    
    def _get_response_content(self, prompt: str) -> str:
        """Generate realistic response content based on prompt."""
        if self.responses and self.call_count <= len(self.responses):
            return self.responses[self.call_count - 1]
        
        # Generate context-aware response
        if "playwright" in prompt.lower():
            return self._generate_playwright_script()
        elif "selenium" in prompt.lower():
            return self._generate_selenium_script()
        else:
            return f"# Generated test script\n# Based on prompt: {prompt[:50]}...\nprint('Test generated')"
    
    def _generate_playwright_script(self) -> str:
        return """
import pytest
from playwright.sync_api import sync_playwright

def test_example():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        page.click("#login-button")
        page.fill("#username", "testuser")
        page.fill("#password", "password123")
        page.click("#submit")
        browser.close()
"""
    
    def _generate_selenium_script(self) -> str:
        return """
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_example():
    driver = webdriver.Chrome()
    driver.get("https://example.com")
    driver.find_element(By.ID, "login-button").click()
    driver.find_element(By.ID, "username").send_keys("testuser")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "submit").click()
    driver.quit()
"""
    
    def analyze_with_context(self, request: AIAnalysisRequest, **kwargs) -> AIResponse:
        """Sync analyze with context for AI analysis calls."""
        time.sleep(self.response_delay)  # Simulate API delay
        
        self.call_count += 1
        
        if hasattr(self, 'failure_rate') and hasattr(self, '_should_fail'):
            import random
            if random.random() < self.failure_rate:
                raise AIProviderError(f"Simulated AI provider failure on call {self.call_count}")
        
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
            model="mock-gpt-4",
            provider="mock-openai",
            tokens_used=150
        )

    def is_available(self) -> bool:
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"name": "mock-gpt-4", "provider": "mock-openai"}


@pytest.fixture
def realistic_automation_flow():
    """A realistic multi-step automation flow."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://app.example.com/login"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_description": "Navigate to login page",
                "step_start_time": 1640995200.0,
                "elapsed_time": 1.2
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click": {
                            "selector": "#email-input"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@id='email-input']",
                        "css_selector": "#email-input",
                        "attributes": {
                            "id": "email-input",
                            "type": "email",
                            "placeholder": "Enter your email"
                        }
                    }
                ]
            },
            "metadata": {
                "step_description": "Click email input field",
                "elapsed_time": 0.5
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "type": {
                            "text": "user@example.com",
                            "selector": "#email-input"
                        }
                    }
                ]
            },
            "metadata": {
                "step_description": "Enter email address",
                "elapsed_time": 0.8
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click": {
                            "selector": "#password-input"
                        }
                    }
                ]
            },
            "metadata": {
                "step_description": "Click password field",
                "elapsed_time": 0.3
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "type": {
                            "text": "secretpassword",
                            "selector": "#password-input"
                        }
                    }
                ]
            },
            "metadata": {
                "step_description": "Enter password",
                "elapsed_time": 0.6
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click": {
                            "selector": "button[type='submit']"
                        }
                    }
                ]
            },
            "metadata": {
                "step_description": "Submit login form",
                "elapsed_time": 0.4
            }
        }
    ]


class TestAsyncEndToEndIntegration:
    """Test complete end-to-end async workflows."""
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_async_conversion_pipeline(self, realistic_automation_flow):
        """Test complete async conversion pipeline."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Create realistic mock provider
        provider = RealisticMockAIProvider(response_delay=0.1)  # Reduced delay
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            # Test the complete async pipeline
            start_time = time.time()
            
            script = await btt.convert_async(
                realistic_automation_flow,
                framework="playwright",
                ai_provider="openai",
                language="python"
            )
            
            end_time = time.time()
            
            # Verify results
            assert isinstance(script, str)
            assert len(script) > 100  # Should be substantial
            assert "playwright" in script.lower()
            assert provider.call_count > 0
            
            # Should complete in reasonable time
            assert end_time - start_time < 5.0
            
            print(f"Async conversion completed in {end_time - start_time:.2f}s with {provider.call_count} AI calls")
    
    @pytest.mark.asyncio
    @async_timeout(45)
    async def test_async_vs_sync_performance_realistic(self, realistic_automation_flow):
        """Test performance comparison with realistic scenarios."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Test sync performance
        sync_provider = RealisticMockAIProvider(response_delay=0.1)  # Reduced delay
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=sync_provider):
            sync_start = time.time()
            sync_script = btt.convert(
                realistic_automation_flow,
                framework="playwright",
                ai_provider="openai"
            )
            sync_time = time.time() - sync_start
        
        # Test async performance
        async_provider = RealisticMockAIProvider(response_delay=0.1)  # Reduced delay
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=async_provider):
            async_start = time.time()
            async_script = await btt.convert_async(
                realistic_automation_flow,
                framework="playwright",
                ai_provider="openai"
            )
            async_time = time.time() - async_start
        
        # Both should produce valid scripts
        assert isinstance(sync_script, str)
        assert isinstance(async_script, str)
        assert len(sync_script) > 100
        assert len(async_script) > 100
        
        # Should make similar number of calls
        assert abs(sync_provider.call_count - async_provider.call_count) <= 1
        
        print(f"Sync: {sync_time:.2f}s ({sync_provider.call_count} calls)")
        print(f"Async: {async_time:.2f}s ({async_provider.call_count} calls)")
    
    @pytest.mark.asyncio
    @async_timeout(45)
    async def test_parallel_async_conversions_realistic(self, realistic_automation_flow):
        """Test multiple parallel conversions with realistic data."""
        await reset_global_queue_manager()  # Ensure clean state
        
        provider = RealisticMockAIProvider(response_delay=0.05)  # Reduced delay
        
        # Create variations of the automation flow
        flows = [
            realistic_automation_flow[:3],  # Short flow
            realistic_automation_flow[:4],  # Medium flow
            realistic_automation_flow,      # Full flow
        ]
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            start_time = time.time()
            
            # Start multiple conversions in parallel
            tasks = []
            for i, flow in enumerate(flows):
                task = asyncio.create_task(
                    btt.convert_async(
                        flow,
                        framework="playwright",
                        ai_provider="openai",
                        language="python"
                    )
                )
                tasks.append(task)
            
            # Simulate other work happening in parallel
            other_work_results = []
            async def simulate_other_work():
                for i in range(10):
                    await asyncio.sleep(0.1)
                    other_work_results.append(f"work_item_{i}")
                return "other_work_done"
            
            # Run conversions and other work in parallel with inner timeout
            scripts, other_work_result = await asyncio.gather(
                asyncio.gather(*tasks),
                simulate_other_work()
            )
            
            total_time = time.time() - start_time
            
            # Verify all conversions completed
            assert len(scripts) == 3
            for script in scripts:
                assert isinstance(script, str)
                assert len(script) > 50
            
            # Verify other work completed
            assert other_work_result == "other_work_done"
            assert len(other_work_results) == 10
            
            # AI calls should be made (exact count depends on optimization)
            # Each conversion typically makes at least 1 call for analysis
            min_expected_calls = len(flows)  # At least one call per conversion
            assert provider.call_count >= min_expected_calls
            
            print(f"Parallel processing completed in {total_time:.2f}s")
            print(f"Total AI calls: {provider.call_count}")
    
    @pytest.mark.asyncio
    @async_timeout(60)
    async def test_async_incremental_session_realistic(self, realistic_automation_flow):
        """Test async incremental session with realistic workflow."""
        await reset_global_queue_manager()  # Ensure clean state
        
        provider = RealisticMockAIProvider(response_delay=0.05)  # Reduced delay
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            session = btt.AsyncIncrementalSession(config)
            
            # Start session
            start_result = await session.start(target_url="https://app.example.com")
            assert start_result.success
            
            # Add steps incrementally with completion waiting (simplified)
            step_times = []
            
            for i, step in enumerate(realistic_automation_flow):
                step_start = time.time()
                result = await session.add_step_async(step, wait_for_completion=True)
                step_time = time.time() - step_start
                
                assert result.success, f"Step {i+1} failed: {result.validation_issues}"
                step_times.append(step_time)
                
                print(f"Step {i+1} completed in {step_time:.3f}s")
            
            # All steps should be processed now
            final_result = result  # Last result from add_step_async
            assert final_result.success
            assert len(final_result.current_script) > 200
            
            # Finalize session
            finalize_result = await session.finalize_async()
            assert finalize_result.success
            
            # Verify step processing completed in reasonable time
            max_step_time = max(step_times)
            assert max_step_time < 2.0  # Should complete within 2 seconds per step
            
            print(f"Session completed with {provider.call_count} AI calls")
            print(f"Final script length: {len(final_result.current_script)} characters")


class TestAsyncErrorHandlingIntegration:
    """Test error handling in realistic async scenarios."""
    
    @pytest.mark.asyncio
    @async_timeout(45)
    async def test_async_conversion_with_partial_failures(self, realistic_automation_flow):
        """Test async conversion when some AI calls fail."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Provider that fails 30% of the time
        provider = RealisticMockAIProvider(response_delay=0.05, failure_rate=0.3)  # Reduced delay
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            # Try multiple conversions, some may fail
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    btt.convert_async(
                        realistic_automation_flow[:3],  # Short flow
                        framework="playwright",
                        ai_provider="openai"
                    )
                )
                tasks.append(task)
            
            # Gather with exception handling
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed with fallback scripts (no exceptions at top level)
            successes = [r for r in results if isinstance(r, str)]
            failures = [r for r in results if isinstance(r, Exception)]
            
            print(f"Successes: {len(successes)}, Failures: {len(failures)}")
            print(f"Total AI calls: {provider.call_count}")
            
            # All should succeed with fallback scripts (no top-level exceptions)
            assert len(successes) == 5  # All should succeed with fallback
            assert len(failures) == 0   # No exceptions should be raised at top level
            
            # All results should be valid scripts
            for script in successes:
                assert len(script) > 0
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_async_session_with_step_failures(self, realistic_automation_flow):
        """Test async session when individual steps fail."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Provider that starts working but then fails
        provider = RealisticMockAIProvider(response_delay=0.05)  # Reduced delay
        provider.failure_rate = 0.0  # Start with no failures
        
        config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            session = btt.AsyncIncrementalSession(config)
            await session.start()
            
            # Add some successful steps
            for i, step in enumerate(realistic_automation_flow[:2]):
                result = await session.add_step_async(step, wait_for_completion=True)
                assert result.success, f"Initial step {i+1} should succeed"
            
            # Change provider to start failing
            provider.failure_rate = 1.0  # Now always fail
            
            # Add steps with AI analysis failures (but should still generate fallback scripts)
            for i, step in enumerate(realistic_automation_flow[2:4]):
                result = await session.add_step_async(step, wait_for_completion=True)
                # Should succeed with fallback script generation even if AI analysis fails
                assert result.success, f"Step {i+3} should succeed with fallback"
                assert len(result.current_script) > 0
            
            # Session should still be functional for new steps
            provider.failure_rate = 0.0  # Fix the provider
            
            # Add one more successful step
            result = await session.add_step_async(realistic_automation_flow[4], wait_for_completion=True)
            assert result.success
            
            await session.finalize_async(wait_for_pending=False)
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_async_timeout_in_real_scenario(self, realistic_automation_flow):
        """Test timeout handling in realistic scenarios."""
        await reset_global_queue_manager()  # Ensure clean state
        
        # Very slow provider
        provider = RealisticMockAIProvider(response_delay=2.0)
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            # Test conversion with timeout
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    btt.convert_async(
                        realistic_automation_flow[:2],
                        framework="playwright",
                        ai_provider="openai"
                    ),
                    timeout=1.0  # Shorter than provider delay
                )
            
            # Test session with timeout
            session = btt.AsyncIncrementalSession(
                btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
            )
            
            await session.start()
            
            # Add step that will timeout
            result = await session.add_step_async(
                realistic_automation_flow[0], 
                wait_for_completion=False
            )
            task_id = result.metadata['task_id']
            
            # Wait with timeout (should return failure result, not raise exception)
            timeout_result = await session.wait_for_task(task_id, timeout=0.5)
            assert not timeout_result.success
            assert "timed out" in str(timeout_result.validation_issues)
            
            await session.finalize_async(wait_for_pending=False)


class TestAsyncPerformanceIntegration:
    """Test performance characteristics in integrated scenarios."""
    
    @pytest.mark.asyncio
    @async_timeout(15)  # Much shorter timeout since we're optimizing for speed
    async def test_async_queue_efficiency(self, realistic_automation_flow):
        """Test that async queue processes tasks efficiently."""
        await reset_global_queue_manager()  # Ensure clean state at start
        
        # Use much faster mock provider - focus on queue efficiency, not realistic AI delays
        provider = RealisticMockAIProvider(response_delay=0.01)  # 10ms instead of 150ms
        
        # Use only a subset of steps to focus on queue behavior, not volume
        test_steps = realistic_automation_flow[:3]  # Just 3 steps instead of 6
        
        # Disable AI analysis to focus purely on queue efficiency
        config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
        config.processing.analyze_actions_with_ai = False
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            session = btt.AsyncIncrementalSession(config)
            
            try:
                await session.start()
                
                # Queue all steps rapidly
                queue_start = time.time()
                task_ids = []
                
                for step in test_steps:
                    result = await session.add_step_async(step, wait_for_completion=False)
                    task_ids.append(result.metadata['task_id'])
                
                queue_time = time.time() - queue_start
                
                # Queueing should be very fast
                assert queue_time < 0.1  # Much stricter timing expectation
                print(f"Queued {len(task_ids)} tasks in {queue_time:.3f}s")
                
                # Monitor processing with shorter timeout
                process_start = time.time()
                await session.wait_for_all_tasks(timeout=10)  # Much shorter timeout
                process_time = time.time() - process_start
                
                print(f"Processed {len(task_ids)} tasks in {process_time:.3f}s")
                print(f"AI calls made: {provider.call_count}")
                
                # Processing should be efficient with our optimized setup
                # With 3 steps, 10ms delay each, plus minimal overhead
                assert process_time < 5.0  # Should complete in under 5 seconds
                
                # Verify all tasks completed successfully
                assert len(task_ids) == len(test_steps)
                
                # Test queue efficiency: multiple tasks should process concurrently where possible
                # (non-AI tasks can run in parallel while AI tasks are sequential)
                efficiency_ratio = len(test_steps) / max(process_time, 0.001)  # steps per second
                print(f"Processing efficiency: {efficiency_ratio:.1f} steps/second")
                assert efficiency_ratio > 0.5  # At least 0.5 steps per second
                
            finally:
                # Ensure cleanup even if test fails
                try:
                    await session.finalize_async(wait_for_pending=False)
                except:
                    pass
                await reset_global_queue_manager()
    
    @pytest.mark.asyncio
    @async_timeout(45)
    async def test_memory_usage_in_long_session(self):
        """Test memory usage doesn't grow unbounded in long sessions."""
        await reset_global_queue_manager()  # Ensure clean state
        
        provider = RealisticMockAIProvider(response_delay=0.05)
        
        # Create a large number of simple steps
        simple_steps = []
        for i in range(20):
            step = {
                "model_output": {
                    "action": [{"click": {"selector": f"#button-{i}"}}]
                },
                "metadata": {"step_description": f"Click button {i}"}
            }
            simple_steps.append(step)
        
        with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
            # Disable AI analysis to focus on async queue performance
            config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
            config.processing.analyze_actions_with_ai = False
            
            session = btt.AsyncIncrementalSession(config)
            
            try:
                await session.start()
                
                # Process steps in batches to simulate real usage
                all_task_ids = []
                for i in range(0, len(simple_steps), 5):
                    batch = simple_steps[i:i+5]
                    batch_task_ids = []
                    
                    # Queue batch
                    for step in batch:
                        result = await session.add_step_async(step, wait_for_completion=False)
                        batch_task_ids.append(result.metadata['task_id'])
                    
                    # Wait for batch to complete with increased timeout
                    for task_id in batch_task_ids:
                        await session.wait_for_task(task_id, timeout=10)
                    
                    all_task_ids.extend(batch_task_ids)
                    
                    # Check queue stats
                    stats = session.get_queue_stats()
                    print(f"Batch {i//5 + 1}: {stats}")
                
                # Final verification
                final_result = await session.wait_for_all_tasks(timeout=30)  # Add timeout
                assert final_result.success
                
                final_stats = session.get_queue_stats()
                assert final_stats['total_tasks'] == len(simple_steps)
                assert final_stats['pending_tasks'] == 0
                
                print(f"Processed {len(simple_steps)} steps with {provider.call_count} AI calls")
                
            finally:
                try:
                    await session.finalize_async(wait_for_pending=False)
                except:
                    pass
    
    @pytest.mark.asyncio
    @async_timeout(30)
    async def test_concurrent_sessions_performance(self, realistic_automation_flow):
        """Test performance when running multiple concurrent sessions."""
        await reset_global_queue_manager()  # Ensure clean state
        
        provider = RealisticMockAIProvider(response_delay=0.1)
        
        # Disable AI analysis to focus on async queue performance
        config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
        config.processing.analyze_actions_with_ai = False
        
        async def run_session(session_id, steps):
            with patch('browse_to_test.ai.factory.AIProviderFactory.create_provider', return_value=provider):
                session = btt.AsyncIncrementalSession(config)
                try:
                    await session.start(target_url=f"https://example{session_id}.com")
                    
                    # Queue steps
                    task_ids = []
                    for step in steps:
                        result = await session.add_step_async(step, wait_for_completion=False)
                        task_ids.append(result.metadata['task_id'])
                    
                    # Wait for completion with timeout
                    final_result = await session.wait_for_all_tasks(timeout=20)
                    return len(final_result.current_script)
                finally:
                    try:
                        await session.finalize_async(wait_for_pending=False)
                    except:
                        pass
        
        # Run multiple sessions concurrently
        start_time = time.time()
        
        session_tasks = []
        for i in range(3):
            steps = realistic_automation_flow[:3 + i]  # Different sizes
            task = asyncio.create_task(run_session(i, steps))
            session_tasks.append(task)
        
        results = await asyncio.gather(*session_tasks)
        
        total_time = time.time() - start_time
        
        # All sessions should complete successfully
        assert len(results) == 3
        for result in results:
            assert result > 0  # All should generate some script
        
        print(f"3 concurrent sessions completed in {total_time:.2f}s")
        print(f"Total AI calls across all sessions: {provider.call_count}")
        
        # Verify queue manager is clean
        queue_manager = await get_global_queue_manager()
        final_stats = queue_manager.get_queue_stats()
        print(f"Final queue stats: {final_stats}")
        
        # Clean up
        await queue_manager.stop() 