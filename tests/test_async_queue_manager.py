"""
Focused tests for AsyncQueueManager.

Tests the async queue manager in isolation to ensure:
- Sequential task execution
- Priority handling  
- Error handling and recovery
- Statistics and monitoring
- Resource cleanup
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
import time
from typing import List
import functools

from browse_to_test.core.orchestration.async_queue import (
    AsyncQueueManager, QueuedTask, TaskStatus, 
    get_global_queue_manager, queue_ai_task, wait_for_ai_task
)


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
                    # Try to clean up any global queue manager
                    from browse_to_test.core.orchestration.async_queue import reset_global_queue_manager
                    await reset_global_queue_manager()
                except:
                    pass
                pytest.fail(f"Test {func.__name__} timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator


class TestAsyncQueueManagerCore:
    """Test core AsyncQueueManager functionality."""
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_queue_manager_lifecycle(self):
        """Test queue manager start/stop lifecycle."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=2)
        
        # Initially not running
        assert not manager._is_running
        assert len(manager._workers) == 0
        
        try:
            # Start the manager
            await manager.start()
            assert manager._is_running
            assert len(manager._workers) == 2  # Should have 2 workers
            
        finally:
            # Stop the manager
            await manager.stop()
            assert not manager._is_running
            assert len(manager._workers) == 0
            
            # Should be safe to stop again
            await manager.stop()
            assert not manager._is_running
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_single_task_execution(self):
        """Test execution of a single task."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            result_value = None
            
            async def simple_task(value):
                nonlocal result_value
                await asyncio.sleep(0.1)
                result_value = value * 2
                return result_value
            
            # Queue and execute task
            task = await manager.queue_task("test_task", simple_task, 5)
            
            assert task.id == "test_task"
            assert task.status == TaskStatus.PENDING
            
            # Wait for completion
            result = await manager.wait_for_task("test_task")
            
            assert result == 10
            assert result_value == 10
            assert task.status == TaskStatus.COMPLETED
            assert task.result == 10
            assert task.error is None
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_multiple_tasks_sequential_execution(self):
        """Test that tasks execute sequentially when max_concurrent_ai_calls=1."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=1)
        await manager.start()
        
        try:
            execution_order = []
            
            async def tracked_task(task_id, duration=0.1):
                execution_order.append(f"start_{task_id}")
                await asyncio.sleep(duration)
                execution_order.append(f"end_{task_id}")
                return task_id
            
            # Queue multiple tasks
            tasks = []
            for i in range(3):
                task = await manager.queue_task(f"task_{i}", tracked_task, i, 0.1)
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*[
                manager.wait_for_task(task.id) for task in tasks
            ])
            
            # Verify sequential execution (no overlap)
            expected_order = [
                "start_0", "end_0", 
                "start_1", "end_1", 
                "start_2", "end_2"
            ]
            assert execution_order == expected_order
            
            # Verify results
            assert results == [0, 1, 2]
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_task_priority_ordering(self):
        """Test that higher priority tasks execute first."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=1)
        await manager.start()
        
        try:
            execution_order = []
            
            async def priority_task(task_id):
                execution_order.append(task_id)
                await asyncio.sleep(0.05)
                return task_id
            
            # Queue tasks with different priorities (higher number = higher priority)
            await manager.queue_task("low", priority_task, "low", priority=1)
            await manager.queue_task("high", priority_task, "high", priority=10)  
            await manager.queue_task("medium", priority_task, "medium", priority=5)
            
            # Wait for all to complete
            await manager.wait_for_all_tasks()
            
            # Should execute in priority order: high (10), medium (5), low (1)
            assert execution_order == ["high", "medium", "low"]
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_task_failure_handling(self):
        """Test handling of task failures."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def failing_task(should_fail=True):
                await asyncio.sleep(0.1)
                if should_fail:
                    raise ValueError("Intentional failure")
                return "success"
            
            # Queue both failing and successful tasks
            failing_task_obj = await manager.queue_task("failing", failing_task, True)
            success_task_obj = await manager.queue_task("success", failing_task, False)
            
            # Wait for failing task
            with pytest.raises(ValueError, match="Intentional failure"):
                await manager.wait_for_task("failing")
            
            # Verify failing task state
            assert failing_task_obj.status == TaskStatus.FAILED
            assert isinstance(failing_task_obj.error, ValueError)
            assert failing_task_obj.result is None
            
            # Wait for successful task
            result = await manager.wait_for_task("success")
            assert result == "success"
            assert success_task_obj.status == TaskStatus.COMPLETED
            assert success_task_obj.error is None
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_task_timeout_handling(self):
        """Test timeout handling for individual tasks."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def slow_task():
                await asyncio.sleep(1.0)  # 1 second
                return "done"
            
            # Queue slow task
            await manager.queue_task("slow", slow_task)
            
            # Wait with short timeout
            with pytest.raises(asyncio.TimeoutError):
                await manager.wait_for_task("slow", timeout=0.2)
            
            # Task should still be running
            task = manager._tasks["slow"]
            assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
            
            # Wait longer for completion
            result = await manager.wait_for_task("slow", timeout=2.0)
            assert result == "done"
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_duplicate_task_id_handling(self):
        """Test handling of duplicate task IDs."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def dummy_task():
                return "result"
            
            # Queue first task
            task1 = await manager.queue_task("duplicate_id", dummy_task)
            
            # Try to queue with same ID
            with pytest.raises(ValueError, match="Task with ID 'duplicate_id' already exists"):
                await manager.queue_task("duplicate_id", dummy_task)
            
            # First task should still work
            result = await manager.wait_for_task("duplicate_id")
            assert result == "result"
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(10)
    async def test_wait_for_nonexistent_task(self):
        """Test waiting for a task that doesn't exist."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            with pytest.raises(KeyError, match="Task 'nonexistent' not found"):
                await manager.wait_for_task("nonexistent")
        finally:
            await manager.stop()


class TestAsyncQueueManagerStatistics:
    """Test queue statistics and monitoring."""
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_queue_statistics(self):
        """Test queue statistics tracking."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            # Initial stats
            stats = manager.get_queue_stats()
            assert stats['total_queued'] == 0
            assert stats['total_completed'] == 0
            assert stats['total_failed'] == 0
            assert stats['pending_tasks'] == 0
            assert stats['running_tasks'] == 0
            assert stats['queue_size'] == 0
            assert stats['total_tasks'] == 0
            
            # Add some tasks
            async def test_task(duration):
                await asyncio.sleep(duration)
                return "done"
            
            tasks = []
            for i in range(3):
                task = await manager.queue_task(f"task_{i}", test_task, 0.1)
                tasks.append(task)
            
            # Check stats after queueing
            stats = manager.get_queue_stats()
            assert stats['total_queued'] == 3
            assert stats['total_tasks'] == 3
            assert stats['pending_tasks'] + stats['running_tasks'] <= 3
            
            # Wait for completion
            await manager.wait_for_all_tasks()
            
            # Check final stats
            final_stats = manager.get_queue_stats()
            assert final_stats['total_completed'] == 3
            assert final_stats['total_failed'] == 0
            assert final_stats['pending_tasks'] == 0
            assert final_stats['running_tasks'] == 0
            assert final_stats['avg_processing_time'] > 0
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_processing_time_tracking(self):
        """Test that processing times are tracked correctly."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def timed_task(duration):
                await asyncio.sleep(duration)
                return "done"
            
            # Queue tasks with known durations
            durations = [0.1, 0.2, 0.15]
            for i, duration in enumerate(durations):
                await manager.queue_task(f"task_{i}", timed_task, duration)
            
            # Wait for completion
            await manager.wait_for_all_tasks()
            
            # Check timing stats
            stats = manager.get_queue_stats()
            assert stats['avg_processing_time'] > 0
            # Average should be roughly in the middle of our durations
            assert 0.1 <= stats['avg_processing_time'] <= 0.25
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_mixed_success_failure_stats(self):
        """Test statistics with mixed successful and failed tasks."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def conditional_task(should_fail):
                await asyncio.sleep(0.05)
                if should_fail:
                    raise ValueError("Task failed")
                return "success"
            
            # Queue mix of successful and failing tasks
            success_tasks = []
            fail_tasks = []
            
            for i in range(3):
                success_task = await manager.queue_task(f"success_{i}", conditional_task, False)
                success_tasks.append(success_task)
                
                fail_task = await manager.queue_task(f"fail_{i}", conditional_task, True)
                fail_tasks.append(fail_task)
            
            # Wait for all (ignoring failures)
            for task in success_tasks:
                result = await manager.wait_for_task(task.id)
                assert result == "success"
            
            for task in fail_tasks:
                with pytest.raises(ValueError):
                    await manager.wait_for_task(task.id)
            
            # Check final statistics
            stats = manager.get_queue_stats()
            assert stats['total_completed'] == 3
            assert stats['total_failed'] == 3
            assert stats['total_queued'] == 6
            
        finally:
            await manager.stop()


class TestGlobalQueueManagerFunctions:
    """Test global queue manager convenience functions."""
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_global_queue_manager_singleton(self):
        """Test that global queue manager is a singleton."""
        manager1 = await get_global_queue_manager()
        manager2 = await get_global_queue_manager()
        
        try:
            # Should be the same instance
            assert manager1 is manager2
            assert manager1._is_running
        finally:
            # Clean up
            await manager1.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_queue_ai_task_convenience(self):
        """Test the queue_ai_task convenience function."""
        async def test_task(value):
            await asyncio.sleep(0.1)
            return value * 2
        
        try:
            # Use convenience function
            task = await queue_ai_task("test_task", test_task, 5, priority=3)
            
            assert task.id == "test_task"
            assert task.priority == 3
            
            # Wait using convenience function
            result = await wait_for_ai_task("test_task")
            assert result == 10
            
        finally:
            # Clean up global manager
            global_manager = await get_global_queue_manager()
            await global_manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_multiple_convenience_tasks(self):
        """Test multiple tasks using convenience functions."""
        async def multiply_task(value, multiplier):
            await asyncio.sleep(0.05)
            return value * multiplier
        
        try:
            # Queue multiple tasks
            task_ids = []
            for i in range(3):
                task = await queue_ai_task(f"task_{i}", multiply_task, i, 2)
                task_ids.append(task.id)
            
            # Wait for all
            results = []
            for task_id in task_ids:
                result = await wait_for_ai_task(task_id)
                results.append(result)
            
            assert results == [0, 2, 4]  # [0*2, 1*2, 2*2]
            
        finally:
            # Clean up
            global_manager = await get_global_queue_manager()
            await global_manager.stop()


class TestAsyncQueueManagerResourceManagement:
    """Test resource management and cleanup."""
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_worker_cleanup_on_stop(self):
        """Test that workers are properly cleaned up on stop."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=3)
        await manager.start()
        
        try:
            # Verify workers are running
            assert len(manager._workers) == 3
            for worker in manager._workers:
                assert not worker.done()
            
        finally:
            # Stop the manager
            await manager.stop(timeout=1.0)
            
            # Verify workers are cleaned up
            assert len(manager._workers) == 0
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_forced_shutdown_with_running_tasks(self):
        """Test forced shutdown when tasks are still running."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def long_running_task():
                try:
                    await asyncio.sleep(10)  # Very long task
                    return "completed"
                except asyncio.CancelledError:
                    return "cancelled"
            
            # Queue a long-running task
            await manager.queue_task("long_task", long_running_task)
            
            # Give it a moment to start
            await asyncio.sleep(0.1)
            
        finally:
            # Force shutdown with short timeout
            start_time = time.time()
            await manager.stop(timeout=0.5)
            stop_time = time.time()
            
            # Should stop quickly due to timeout and cancellation
            assert stop_time - start_time < 1.0
            assert not manager._is_running
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_memory_cleanup_after_completion(self):
        """Test that completed tasks don't accumulate indefinitely."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def quick_task(task_id):
                return f"result_{task_id}"
            
            # Queue and complete many tasks
            for i in range(10):
                await manager.queue_task(f"task_{i}", quick_task, i)
                await manager.wait_for_task(f"task_{i}")
            
            # All tasks should be in the tasks dict
            assert len(manager._tasks) == 10
            
            # But running tasks should be empty
            assert len(manager._running_tasks) == 0
            
            # Queue should be empty
            assert manager._queue.qsize() == 0
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(15)
    async def test_exception_in_worker_recovery(self):
        """Test that workers can recover from unexpected exceptions."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=1)
        await manager.start()
        
        try:
            # Create a task that will cause an exception in the worker
            async def problematic_task():
                # This should not crash the worker
                raise RuntimeError("Unexpected worker exception")
            
            async def normal_task():
                return "normal_result"
            
            # Queue problematic task
            await manager.queue_task("problematic", problematic_task)
            
            # Wait for it to fail
            with pytest.raises(RuntimeError):
                await manager.wait_for_task("problematic")
            
            # Queue normal task - worker should still be functional
            await manager.queue_task("normal", normal_task)
            result = await manager.wait_for_task("normal")
            
            assert result == "normal_result"
            
        finally:
            await manager.stop()


class TestAsyncQueueManagerConcurrency:
    """Test concurrency scenarios and edge cases."""
    
    @pytest.mark.asyncio
    @async_timeout(20)
    async def test_concurrent_queue_operations(self):
        """Test concurrent queueing and waiting operations."""
        manager = AsyncQueueManager()
        await manager.start()
        
        try:
            async def test_task(task_id, duration):
                await asyncio.sleep(duration)
                return f"result_{task_id}"
            
            # Concurrently queue multiple tasks
            queue_tasks = []
            for i in range(5):
                queue_task = asyncio.create_task(
                    manager.queue_task(f"task_{i}", test_task, i, 0.1)
                )
                queue_tasks.append(queue_task)
            
            # Wait for all queueing to complete
            queued_tasks = await asyncio.gather(*queue_tasks)
            
            # Concurrently wait for all tasks
            wait_tasks = []
            for task in queued_tasks:
                wait_task = asyncio.create_task(
                    manager.wait_for_task(task.id)
                )
                wait_tasks.append(wait_task)
            
            # All should complete successfully
            results = await asyncio.gather(*wait_tasks)
            
            expected_results = [f"result_{i}" for i in range(5)]
            assert results == expected_results
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    @async_timeout(25)
    async def test_queue_while_processing(self):
        """Test queueing new tasks while others are processing."""
        manager = AsyncQueueManager(max_concurrent_ai_calls=1)
        await manager.start()
        
        try:
            processing_started = asyncio.Event()
            
            async def blocking_task():
                processing_started.set()
                await asyncio.sleep(0.3)
                return "blocking_done"
            
            async def quick_task(task_id):
                await asyncio.sleep(0.05)
                return f"quick_{task_id}"
            
            # Start a blocking task
            await manager.queue_task("blocking", blocking_task)
            
            # Wait for it to start processing
            await processing_started.wait()
            
            # Queue more tasks while blocking task is running
            for i in range(3):
                await manager.queue_task(f"quick_{i}", quick_task, i)
            
            # All should complete in order
            results = []
            for task_id in ["blocking", "quick_0", "quick_1", "quick_2"]:
                result = await manager.wait_for_task(task_id)
                results.append(result)
            
            expected = ["blocking_done", "quick_0", "quick_1", "quick_2"]
            assert results == expected
            
        finally:
            await manager.stop() 