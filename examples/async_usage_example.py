#!/usr/bin/env python3
"""
Async Usage Example for Browse-to-Test

This example demonstrates how to use the async API to queue multiple script 
generation tasks without blocking other processing. The AI calls will be 
sequential (to maintain context) while allowing other work to continue in parallel.
"""

import asyncio
import time
import browse_to_test as btt
from typing import List, Dict, Any


# Sample automation data for testing
SAMPLE_AUTOMATION_STEPS = [
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
    },
    {
        "model_output": {
            "action": [
                {"type": {"selector": "#password", "text": "password123"}}
            ]
        },
        "timing_info": {"elapsed_time": 0.2}
    },
    {
        "model_output": {
            "action": [
                {"click": {"selector": "#submit", "text": "Submit"}}
            ]
        },
        "timing_info": {"elapsed_time": 0.1}
    }
]


async def simple_async_conversion_example():
    """
    Example 1: Simple async conversion
    
    This shows how to use the async convert function instead of the blocking one.
    """
    print("=== Simple Async Conversion Example ===")
    
    start_time = time.time()
    
    # Use the async convert function - AI calls will be queued
    script = await btt.convert_async(
        SAMPLE_AUTOMATION_STEPS,
        framework="playwright",
        ai_provider="openai",  # Make sure you have OPENAI_API_KEY set
        language="python"
    )
    
    end_time = time.time()
    
    print(f"Generated script in {end_time - start_time:.2f} seconds")
    print(f"Script length: {len(script)} characters")
    print("Script preview:")
    print(script[:200] + "..." if len(script) > 200 else script)
    print()


async def parallel_processing_example():
    """
    Example 2: Parallel processing with async queue
    
    This shows how you can start multiple script generations and do other work
    while they're processing in the background.
    """
    print("=== Parallel Processing Example ===")
    
    # Start multiple async conversions (they'll be queued sequentially for AI calls)
    tasks = []
    for i in range(3):
        print(f"Queueing conversion task {i+1}...")
        task = asyncio.create_task(
            btt.convert_async(
                SAMPLE_AUTOMATION_STEPS[:i+2],  # Different data for each task
                framework="playwright",
                ai_provider="openai"
            )
        )
        tasks.append(task)
    
    # Do other work while tasks are processing
    print("Doing other work while AI calls are queued...")
    for i in range(5):
        await asyncio.sleep(0.5)  # Simulate other processing
        print(f"  Other work step {i+1}/5 completed")
    
    # Wait for all tasks to complete
    print("Waiting for all conversion tasks to complete...")
    results = await asyncio.gather(*tasks)
    
    print(f"All tasks completed! Generated {len(results)} scripts")
    for i, script in enumerate(results):
        print(f"Script {i+1}: {len(script)} characters")
    print()


async def incremental_session_example():
    """
    Example 3: Async Incremental Session
    
    This shows how to use AsyncIncrementalSession to queue multiple steps
    without waiting, then retrieve the complete script when ready.
    """
    print("=== Async Incremental Session Example ===")
    
    # Create async session
    config = btt.ConfigBuilder() \
        .framework("playwright") \
        .ai_provider("openai") \
        .language("python") \
        .build()
    
    session = btt.AsyncIncrementalSession(config)
    
    # Start the session
    result = await session.start(target_url="https://example.com")
    print(f"Session started: {result.success}")
    
    # Queue multiple steps without waiting for completion
    task_ids = []
    for i, step_data in enumerate(SAMPLE_AUTOMATION_STEPS):
        print(f"Queueing step {i+1}...")
        result = await session.add_step_async(step_data, wait_for_completion=False)
        if result.success and 'task_id' in result.metadata:
            task_ids.append(result.metadata['task_id'])
            print(f"  Step {i+1} queued with task ID: {result.metadata['task_id']}")
    
    # Do other work while steps are processing
    print("\nDoing other work while steps are processing...")
    for i in range(3):
        await asyncio.sleep(1)
        stats = session.get_queue_stats()
        print(f"  Queue stats: {stats['pending_tasks']} pending, {stats['total_tasks']} total")
    
    # Wait for all tasks to complete
    print("\nWaiting for all tasks to complete...")
    final_result = await session.wait_for_all_tasks(timeout=60)
    
    if final_result.success:
        print(f"All steps completed! Final script has {len(final_result.current_script)} characters")
        print("Final script preview:")
        preview = final_result.current_script[:300] + "..." if len(final_result.current_script) > 300 else final_result.current_script
        print(preview)
    else:
        print(f"Session failed: {final_result.validation_issues}")
    
    # Finalize the session
    await session.finalize_async()
    print("Session finalized")
    print()


async def monitoring_queue_example():
    """
    Example 4: Monitoring async queue progress
    
    This shows how to monitor the progress of async tasks and handle them
    individually as they complete.
    """
    print("=== Monitoring Queue Example ===")
    
    # Create session
    config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
    session = btt.AsyncIncrementalSession(config)
    
    await session.start(target_url="https://example.com")
    
    # Queue all steps
    task_ids = []
    for i, step_data in enumerate(SAMPLE_AUTOMATION_STEPS[:3]):  # Use fewer steps for demo
        result = await session.add_step_async(step_data, wait_for_completion=False)
        if result.success and 'task_id' in result.metadata:
            task_ids.append(result.metadata['task_id'])
    
    print(f"Queued {len(task_ids)} tasks")
    
    # Monitor progress
    completed_tasks = []
    while len(completed_tasks) < len(task_ids):
        for task_id in task_ids:
            if task_id not in completed_tasks:
                status = session.get_task_status(task_id)
                if status == 'completed':
                    completed_tasks.append(task_id)
                    print(f"Task {task_id} completed ({len(completed_tasks)}/{len(task_ids)})")
                elif status == 'failed':
                    completed_tasks.append(task_id)
                    print(f"Task {task_id} failed ({len(completed_tasks)}/{len(task_ids)})")
        
        if len(completed_tasks) < len(task_ids):
            await asyncio.sleep(0.5)  # Check every 500ms
    
    print("All tasks finished!")
    
    # Get final result
    final_result = await session.wait_for_all_tasks()
    print(f"Final script: {len(final_result.current_script)} characters")
    
    await session.finalize_async()
    print()


async def performance_comparison():
    """
    Example 5: Performance comparison between sync and async
    
    This demonstrates the performance benefits of async processing.
    """
    print("=== Performance Comparison ===")
    
    # Test data
    test_steps = SAMPLE_AUTOMATION_STEPS[:3]
    
    # Sync version timing
    print("Testing sync version...")
    sync_start = time.time()
    sync_script = btt.convert(test_steps, framework="playwright", ai_provider="openai")
    sync_end = time.time()
    sync_time = sync_end - sync_start
    
    print(f"Sync conversion: {sync_time:.2f} seconds")
    
    # Async version timing
    print("Testing async version...")
    async_start = time.time()
    async_script = await btt.convert_async(test_steps, framework="playwright", ai_provider="openai")
    async_end = time.time()
    async_time = async_end - async_start
    
    print(f"Async conversion: {async_time:.2f} seconds")
    
    # The async version should have similar timing for a single call,
    # but the benefit comes when doing multiple operations in parallel
    print(f"Scripts are equivalent: {len(sync_script) == len(async_script)}")
    print()


async def main():
    """Main function to run all examples."""
    print("Browse-to-Test Async Usage Examples")
    print("=====================================")
    print()
    
    # Check if we have an OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
        print("Some examples may fail. Please set your OpenAI API key.")
        print("You can also modify the examples to use 'anthropic' provider with ANTHROPIC_API_KEY.")
        print()
    
    try:
        # Run examples
        await simple_async_conversion_example()
        await parallel_processing_example()
        await incremental_session_example()
        await monitoring_queue_example()
        await performance_comparison()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")
        print("This might be due to missing API keys or network issues.")


if __name__ == "__main__":
    # Run the async examples
    asyncio.run(main()) 