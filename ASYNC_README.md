# Async Support in Browse-to-Test

Browse-to-Test now supports asynchronous processing to solve performance issues with long-blocking AI calls. This allows you to:

- **Queue multiple script generation tasks** without blocking other processing
- **Continue other work** while AI calls are processed in the background  
- **Maintain sequential AI calls** (to preserve conversation context) while enabling parallel non-AI processing
- **Monitor and control** async task execution

## Why Async?

The original library had blocking AI calls that could significantly slow down applications, especially when generating multiple scripts or processing many automation steps. The async version solves this by:

1. **Non-blocking AI calls**: AI requests are queued and processed asynchronously
2. **Sequential AI processing**: AI calls remain sequential to maintain context, but don't block your application
3. **Parallel non-AI work**: Parsing, validation, and other processing can happen in parallel
4. **Better resource utilization**: Your application can continue other work while waiting for AI responses

## Quick Start

### Simple Async Conversion

```python
import browse_to_test as btt
import asyncio

async def main():
    # Instead of this (blocking):
    # script = btt.convert(automation_data, framework="playwright", ai_provider="openai")
    
    # Use this (non-blocking):
    script = await btt.convert_async(automation_data, framework="playwright", ai_provider="openai")
    print(script)

asyncio.run(main())
```

### Async Incremental Session

```python
import browse_to_test as btt
import asyncio

async def main():
    config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
    session = btt.AsyncIncrementalSession(config)
    
    await session.start(target_url="https://example.com")
    
    # Queue multiple steps without waiting
    for step_data in automation_steps:
        await session.add_step_async(step_data, wait_for_completion=False)
    
    # Do other work while AI processes in background
    await do_other_important_work()
    
    # Get final result when ready
    result = await session.wait_for_all_tasks()
    final_script = result.current_script

asyncio.run(main())
```

## API Reference

### Async Functions

#### `convert_async(automation_data, framework="playwright", ai_provider="openai", language="python", **kwargs)`

Async version of the main `convert()` function.

- **Returns**: `str` - Generated test script
- **Benefits**: Non-blocking, can be used with `asyncio.gather()` for parallel processing

#### `AsyncIncrementalSession(config)`

Async version of `IncrementalSession` for step-by-step script building.

**Key Methods:**

- `await session.start(target_url, context_hints)` - Initialize session
- `await session.add_step_async(step_data, wait_for_completion=False)` - Queue a step
- `await session.wait_for_task(task_id, timeout=None)` - Wait for specific task
- `await session.wait_for_all_tasks(timeout=None)` - Wait for all queued tasks
- `await session.finalize_async(wait_for_pending=True)` - Finalize session
- `session.get_queue_stats()` - Get queue statistics

### Async Queue Management

The library uses an internal `AsyncQueueManager` to handle AI call sequencing:

- **Sequential AI calls**: Ensures AI requests maintain context
- **Priority handling**: Higher priority tasks processed first
- **Error handling**: Failed tasks are tracked and can be retried
- **Statistics**: Monitor queue performance and task completion

## Usage Patterns

### Pattern 1: Parallel Script Generation

Generate multiple scripts in parallel while maintaining AI call sequencing:

```python
async def generate_multiple_scripts():
    tasks = []
    
    # Start multiple conversions
    for dataset in automation_datasets:
        task = asyncio.create_task(
            btt.convert_async(dataset, framework="playwright", ai_provider="openai")
        )
        tasks.append(task)
    
    # Do other work while they process
    await process_other_data()
    
    # Collect results
    scripts = await asyncio.gather(*tasks)
    return scripts
```

### Pattern 2: Incremental with Background Processing

Build scripts incrementally while doing other work:

```python
async def incremental_with_background_work():
    session = btt.AsyncIncrementalSession(config)
    await session.start()
    
    # Queue all steps immediately
    task_ids = []
    for step in steps:
        result = await session.add_step_async(step, wait_for_completion=False)
        task_ids.append(result.metadata['task_id'])
    
    # Monitor progress while doing other work
    while session.get_queue_stats()['pending_tasks'] > 0:
        await asyncio.sleep(1)
        await do_background_processing()
        print(f"Queue stats: {session.get_queue_stats()}")
    
    final_result = await session.wait_for_all_tasks()
    return final_result.current_script
```

### Pattern 3: Task Monitoring and Control

Monitor individual tasks and handle completion as they finish:

```python
async def monitor_tasks():
    session = btt.AsyncIncrementalSession(config)
    await session.start()
    
    # Queue tasks
    task_ids = []
    for step in steps:
        result = await session.add_step_async(step, wait_for_completion=False)
        task_ids.append(result.metadata['task_id'])
    
    # Process completed tasks as they finish
    completed = []
    while len(completed) < len(task_ids):
        for task_id in task_ids:
            if task_id not in completed:
                status = session.get_task_status(task_id)
                if status == 'completed':
                    result = await session.wait_for_task(task_id)
                    await handle_completed_task(task_id, result)
                    completed.append(task_id)
                elif status == 'failed':
                    await handle_failed_task(task_id)
                    completed.append(task_id)
        
        await asyncio.sleep(0.1)  # Small delay
```

## Performance Benefits

### Before (Blocking)

```python
# This blocks for the entire duration of AI calls
total_time = 0
for step in steps:
    start = time.time()
    script = btt.convert(step, ...)  # Blocks for ~2-5 seconds
    total_time += time.time() - start
    
    # Can't do other work here
    
# Total time: 5 steps × 3 seconds = 15 seconds of blocking
```

### After (Async)

```python
# This allows other work while AI calls are queued
tasks = []
for step in steps:
    task = asyncio.create_task(btt.convert_async(step, ...))
    tasks.append(task)

# Do other work immediately while AI calls are processing
await do_other_critical_work()  # This runs in parallel!

# Collect results when ready
scripts = await asyncio.gather(*tasks)

# Total blocking time: Only when you actually need the results
```

## Configuration

### AI Provider Configuration

Both OpenAI and Anthropic providers support async operations:

```python
config = btt.ConfigBuilder() \
    .ai_provider("openai") \
    .ai_config({
        "model": "gpt-4",
        "temperature": 0.1,
        "timeout": 30,
        "retry_attempts": 3
    }) \
    .build()
```

### Queue Configuration

The async queue manager can be configured for different use cases:

```python
from browse_to_test.core.orchestration.async_queue import AsyncQueueManager

# Create custom queue manager
queue_manager = AsyncQueueManager(
    max_concurrent_ai_calls=1,  # Keep sequential for context
    max_retries=3
)

await queue_manager.start()
```

## Error Handling

### Async Error Patterns

```python
async def robust_async_conversion():
    try:
        script = await btt.convert_async(data, framework="playwright", ai_provider="openai")
        return script
    except asyncio.TimeoutError:
        print("AI call timed out")
        return None
    except Exception as e:
        print(f"Conversion failed: {e}")
        return None

# Handle multiple tasks with error tolerance
async def convert_with_error_handling():
    tasks = [
        btt.convert_async(dataset, framework="playwright", ai_provider="openai")
        for dataset in datasets
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    scripts = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Dataset {i} failed: {result}")
        else:
            scripts.append(result)
    
    return scripts
```

## Migration Guide

### From Sync to Async

1. **Simple conversion**:
   ```python
   # Before
   script = btt.convert(data, ...)
   
   # After  
   script = await btt.convert_async(data, ...)
   ```

2. **Incremental sessions**:
   ```python
   # Before
   session = btt.IncrementalSession(config)
   session.start()
   for step in steps:
       session.add_step(step)
   script = session.finalize()
   
   # After
   session = btt.AsyncIncrementalSession(config)
   await session.start()
   for step in steps:
       await session.add_step_async(step, wait_for_completion=False)
   result = await session.wait_for_all_tasks()
   script = result.current_script
   ```

3. **Add async event loop**:
   ```python
   # Wrap your existing code in async function
   async def main():
       # Your async code here
       pass
   
   # Run it
   import asyncio
   asyncio.run(main())
   ```

## Best Practices

### 1. Use Async for Multiple Operations

Async is most beneficial when you have multiple script generations or steps:

```python
# Good: Multiple operations benefit from async
async def process_multiple_datasets():
    tasks = [btt.convert_async(data, ...) for data in datasets]
    return await asyncio.gather(*tasks)

# Less beneficial: Single operation
async def process_single_dataset():
    return await btt.convert_async(data, ...)  # Similar to sync performance
```

### 2. Don't Block the Event Loop

Avoid blocking operations in async code:

```python
# Bad: Blocking operation in async function
async def bad_example():
    script = await btt.convert_async(data, ...)
    time.sleep(5)  # Blocks the entire event loop!
    return script

# Good: Use async sleep
async def good_example():
    script = await btt.convert_async(data, ...)
    await asyncio.sleep(5)  # Non-blocking
    return script
```

### 3. Handle Timeouts

Set appropriate timeouts for AI operations:

```python
async def with_timeout():
    try:
        script = await asyncio.wait_for(
            btt.convert_async(data, ...),
            timeout=60.0  # 60 second timeout
        )
        return script
    except asyncio.TimeoutError:
        print("AI call timed out")
        return None
```

### 4. Monitor Queue Statistics

Keep track of queue performance:

```python
async def monitor_session():
    session = btt.AsyncIncrementalSession(config)
    
    # Queue tasks
    for step in steps:
        await session.add_step_async(step, wait_for_completion=False)
    
    # Monitor progress
    while True:
        stats = session.get_queue_stats()
        if stats['pending_tasks'] == 0:
            break
        
        print(f"Progress: {stats['total_tasks'] - stats['pending_tasks']}/{stats['total_tasks']}")
        await asyncio.sleep(1)
```

## Requirements

Add these dependencies to your `requirements.txt`:

```txt
# Core async support
aiohttp>=3.8.0
asyncio-throttle>=1.0.0

# AI providers with async support
openai>=1.0.0
anthropic>=0.20.0

# Testing async code
pytest-asyncio>=0.20.0
```

## Examples

See `examples/async_usage_example.py` for comprehensive examples demonstrating:

- Simple async conversion
- Parallel processing with async queue
- Async incremental sessions
- Queue monitoring and task management
- Performance comparisons

Run the examples:

```bash
cd examples
python async_usage_example.py
```

Make sure to set your AI provider API key:

```bash
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"
``` 