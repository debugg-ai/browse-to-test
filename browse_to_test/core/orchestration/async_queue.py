"""
Async queue manager for sequential AI processing while allowing parallel non-AI work.
"""

import asyncio
import logging
from typing import Callable, Any, Dict, List, Optional, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of tasks in the queue."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedTask:
    """A task in the async queue."""
    id: str
    callable_func: Callable[..., Awaitable[Any]]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0  # Higher priority = executed first
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completion_event: asyncio.Event = field(default_factory=asyncio.Event)

    def __lt__(self, other):
        """Compare tasks for priority queue ordering - higher priority comes first."""
        return self.priority > other.priority


class AsyncQueueManager:
    """
    Manages async task queue for sequential AI calls while allowing parallel non-AI work.
    
    This ensures AI calls are sequential (to maintain conversation context) while allowing
    other processing to continue in parallel.
    """
    
    def __init__(self, max_concurrent_ai_calls: int = 3, max_retries: int = 3):
        """
        Initialize the async queue manager.
        
        Args:
            max_concurrent_ai_calls: Maximum concurrent AI calls (usually 1 for sequential)
            max_retries: Maximum number of retries for failed tasks
        """
        self.max_concurrent_ai_calls = max_concurrent_ai_calls
        self.max_retries = max_retries
        
        # Task management
        self._tasks: Dict[str, QueuedTask] = {}
        self._queue = asyncio.PriorityQueue()  # Use priority queue instead of regular queue
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: List[str] = []
        self._failed_tasks: List[str] = []
        
        # Worker management
        self._workers: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        self._is_running = False
        
        # Statistics
        self._stats = {
            'total_queued': 0,
            'total_completed': 0,
            'total_failed': 0,
            'avg_processing_time': 0.0
        }
    
    async def start(self):
        """Start the queue processing workers."""
        if self._is_running:
            return
        
        self._is_running = True
        self._shutdown_event.clear()
        
        # Start worker tasks
        for i in range(self.max_concurrent_ai_calls):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info(f"Started AsyncQueueManager with {self.max_concurrent_ai_calls} workers")
    
    async def stop(self, timeout: float = 10.0):
        """Stop the queue processing workers."""
        if not self._is_running:
            return
        
        logger.info("Stopping AsyncQueueManager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for workers to complete with timeout, handling closed event loops
        try:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._workers, return_exceptions=True),
                    timeout=timeout
                )
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    # Event loop is closed, can't properly clean up workers
                    logger.warning("Event loop closed during stop, skipping worker cleanup")
                else:
                    raise
        except asyncio.TimeoutError:
            logger.warning("Some workers didn't stop gracefully, cancelling...")
            try:
                for worker in self._workers:
                    worker.cancel()
            except RuntimeError as e:
                if "Event loop is closed" not in str(e):
                    raise
        
        self._workers.clear()
        self._is_running = False
        logger.info("AsyncQueueManager stopped")

    async def queue_task(
        self,
        task_id: str,
        callable_func: Callable[..., Awaitable[Any]],
        *args,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> QueuedTask:
        """
        Queue a task for async execution.
        
        Args:
            task_id: Unique identifier for the task
            callable_func: Async function to execute
            *args: Positional arguments for the function
            priority: Task priority (higher = executed first)
            metadata: Optional metadata for the task
            **kwargs: Keyword arguments for the function
        
        Returns:
            QueuedTask object that can be awaited
        """
        if not self._is_running:
            await self.start()
        
        if task_id in self._tasks:
            raise ValueError(f"Task with ID '{task_id}' already exists")
        
        task = QueuedTask(
            id=task_id,
            callable_func=callable_func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            metadata=metadata or {}
        )
        
        self._tasks[task_id] = task
        await self._queue.put(task)  # Priority queue will order tasks automatically
        self._stats['total_queued'] += 1
        
        logger.debug(f"Queued task: {task_id} (priority: {priority})")
        return task
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for a specific task to complete and return its result.
        
        Args:
            task_id: ID of the task to wait for
            timeout: Maximum time to wait (None for no timeout)
        
        Returns:
            Task result
        
        Raises:
            KeyError: If task doesn't exist
            asyncio.TimeoutError: If timeout is reached
            Exception: If task failed
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' not found")
        
        task = self._tasks[task_id]
        
        # If already completed, return immediately
        if task.status == TaskStatus.COMPLETED:
            return task.result
        elif task.status == TaskStatus.FAILED:
            raise task.error or Exception(f"Task {task_id} failed")
        
        # Wait for completion using event instead of busy waiting
        try:
            if timeout:
                await asyncio.wait_for(task.completion_event.wait(), timeout=timeout)
            else:
                await task.completion_event.wait()
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
        
        if task.status == TaskStatus.COMPLETED:
            return task.result
        elif task.status == TaskStatus.FAILED:
            raise task.error or Exception(f"Task {task_id} failed")
        else:
            raise Exception(f"Task {task_id} in unexpected status: {task.status}")
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for all currently queued tasks to complete.
        
        Args:
            timeout: Maximum time to wait (None for no timeout)
        
        Returns:
            Dictionary mapping task IDs to their results
        """
        task_ids = list(self._tasks.keys())
        results = {}
        
        for task_id in task_ids:
            try:
                results[task_id] = await self.wait_for_task(task_id, timeout)
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                results[task_id] = e
        
        return results
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        task = self._tasks.get(task_id)
        return task.status if task else None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        pending_count = sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING)
        running_count = sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING)
        
        return {
            **self._stats,
            'pending_tasks': pending_count,
            'running_tasks': running_count,
            'queue_size': self._queue.qsize(),
            'total_tasks': len(self._tasks)
        }
    
    async def _worker(self, worker_name: str):
        """Worker coroutine that processes tasks from the queue."""
        logger.debug(f"Worker {worker_name} started")
        
        while not self._shutdown_event.is_set():
            try:
                # Get next task with timeout to allow periodic shutdown checks
                try:
                    task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the task
                await self._execute_task(task, worker_name)
                
            except Exception as e:
                logger.error(f"Worker {worker_name} encountered error: {e}")
        
        logger.debug(f"Worker {worker_name} stopped")
    
    async def _execute_task(self, task: QueuedTask, worker_name: str):
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        # Add to running tasks
        async_task = asyncio.create_task(task.callable_func(*task.args, **task.kwargs))
        self._running_tasks[task.id] = async_task
        
        logger.debug(f"Worker {worker_name} executing task: {task.id}")
        
        try:
            # Execute the task
            result = await async_task
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            self._completed_tasks.append(task.id)
            self._stats['total_completed'] += 1
            
            # Update average processing time
            processing_time = (task.completed_at - task.started_at).total_seconds()
            current_avg = self._stats['avg_processing_time']
            total_completed = self._stats['total_completed']
            self._stats['avg_processing_time'] = (current_avg * (total_completed - 1) + processing_time) / total_completed
            
            logger.debug(f"Task {task.id} completed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            # Mark as failed
            task.status = TaskStatus.FAILED
            task.error = e
            task.completed_at = datetime.now()
            self._failed_tasks.append(task.id)
            self._stats['total_failed'] += 1
            
            logger.error(f"Task {task.id} failed: {e}")
            
        finally:
            # Remove from running tasks and signal completion
            self._running_tasks.pop(task.id, None)
            task.completion_event.set()  # Signal completion to waiters


# Global queue manager instance
_global_queue_manager: Optional[AsyncQueueManager] = None


async def get_global_queue_manager() -> AsyncQueueManager:
    """Get the global async queue manager instance."""
    global _global_queue_manager
    
    if _global_queue_manager is None or not _global_queue_manager._is_running:
        if _global_queue_manager is not None:
            # Clean up old non-running instance
            _global_queue_manager = None
        _global_queue_manager = AsyncQueueManager()
        await _global_queue_manager.start()
    
    return _global_queue_manager


async def reset_global_queue_manager():
    """Reset the global queue manager (useful for testing)."""
    global _global_queue_manager
    
    if _global_queue_manager is not None:
        # Stop the current queue manager properly, handling closed event loops
        try:
            await _global_queue_manager.stop()
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                # Event loop is closed, just reset without proper cleanup
                pass
            else:
                raise
        _global_queue_manager = None


async def queue_ai_task(
    task_id: str,
    callable_func: Callable[..., Awaitable[Any]],
    *args,
    priority: int = 0,
    **kwargs
) -> QueuedTask:
    """
    Convenience function to queue an AI task using the global queue manager.
    
    Args:
        task_id: Unique identifier for the task
        callable_func: Async function to execute
        *args: Positional arguments for the function
        priority: Task priority (higher = executed first)
        **kwargs: Keyword arguments for the function
    
    Returns:
        QueuedTask object that can be awaited
    """
    queue_manager = await get_global_queue_manager()
    return await queue_manager.queue_task(task_id, callable_func, *args, priority=priority, **kwargs)


async def wait_for_ai_task(task_id: str, timeout: Optional[float] = None) -> Any:
    """
    Convenience function to wait for an AI task using the global queue manager.
    
    Args:
        task_id: ID of the task to wait for
        timeout: Maximum time to wait (None for no timeout)
    
    Returns:
        Task result
    """
    queue_manager = await get_global_queue_manager()
    return await queue_manager.wait_for_task(task_id, timeout) 