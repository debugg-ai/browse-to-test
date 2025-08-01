#!/usr/bin/env python3
"""
Demo script showcasing AI orchestration optimizations in Browse-to-Test.

This script demonstrates:
1. Intelligent AI request batching
2. Optimized prompts for token efficiency
3. Response caching for similar patterns
4. Enhanced error handling with graceful degradation
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from browse_to_test import ConfigBuilder
from browse_to_test.core.orchestration.enhanced_session import EnhancedAsyncSession
from browse_to_test.ai.prompt_optimizer import PromptOptimizer, PromptTemplate
from browse_to_test.ai.error_handler import AIErrorHandler, AdaptiveRetryStrategy


async def demonstrate_batching():
    """Demonstrate intelligent AI request batching."""
    print("\n=== AI Request Batching Demo ===\n")
    
    # Create enhanced session with batching enabled
    config = ConfigBuilder() \
        .framework("playwright") \
        .use_ai(True) \
        .build()
    
    session = EnhancedAsyncSession(config)
    
    # Start session
    result = await session.start("https://example.com")
    print(f"Session started: {result.success}")
    
    # Add multiple steps rapidly (will be batched)
    steps = [
        {
            "model_output": {
                "action": [{"click_element": {"selector": "#login"}}]
            },
            "state": {"interacted_element": [{"selector": "#login", "tag": "button"}]}
        },
        {
            "model_output": {
                "action": [{"input_text": {"selector": "#username", "text": "user@example.com"}}]
            },
            "state": {"interacted_element": [{"selector": "#username", "tag": "input"}]}
        },
        {
            "model_output": {
                "action": [{"input_text": {"selector": "#password", "text": "password123"}}]
            },
            "state": {"interacted_element": [{"selector": "#password", "tag": "input"}]}
        },
        {
            "model_output": {
                "action": [{"click_element": {"selector": "#submit"}}]
            },
            "state": {"interacted_element": [{"selector": "#submit", "tag": "button"}]}
        }
    ]
    
    # Add steps without waiting (allows batching)
    print("Adding steps for batch processing...")
    task_ids = []
    
    for i, step in enumerate(steps):
        result = await session.add_step_async(step, wait_for_completion=False)
        if result.metadata.get('batched'):
            print(f"Step {i+1} added to batch {result.metadata['batch_key']}")
        task_ids.append(result.metadata.get('task_id'))
    
    # Wait for all processing to complete
    print("\nWaiting for batch processing to complete...")
    await asyncio.sleep(2)  # Give time for batching
    
    # Get optimization metrics
    metrics = session.get_optimization_metrics()
    print("\nOptimization Metrics:")
    print(f"- Total steps: {metrics['total_steps']}")
    print(f"- AI calls made: {metrics['ai_calls']['made']}")
    print(f"- AI calls saved: {metrics['ai_calls']['saved']} ({metrics['ai_calls']['savings_percent']:.1f}%)")
    print(f"- Efficiency ratio: {metrics['efficiency_ratio']:.2f}")
    
    return session


def demonstrate_prompt_optimization():
    """Demonstrate prompt optimization for token efficiency."""
    print("\n=== Prompt Optimization Demo ===\n")
    
    optimizer = PromptOptimizer()
    
    # Original verbose prompt
    original_prompt = """
    Please analyze the following browser automation data and provide comprehensive 
    recommendations for converting it to Playwright test code. It is important that 
    you consider best practices and make sure to include proper error handling.
    
    In order to create a reliable test script, you should consider the following:
    - Use appropriate selectors that are stable and reliable
    - Implement proper wait strategies to handle dynamic content
    - Add assertions to validate the expected behavior
    - Include error handling for potential failures
    
    Automation Data:
    - Click on element with selector '#login-button'
    - Fill in text 'user@example.com' in element with selector '#email-input'
    - Click on element with selector '#submit-button'
    
    Please provide:
    1. Detailed action analysis and comprehensive recommendations
    2. Selector optimization suggestions with best practices
    3. Potential issues or improvements that should be considered
    4. Framework-specific best practices for Playwright
    """
    
    # Optimize the prompt
    optimized = optimizer.optimize_prompt(
        PromptTemplate.CONVERSION_COMPACT,
        {
            'framework': 'Playwright',
            'actions': "click('#login-button'), fill('#email-input', 'user@example.com'), click('#submit-button')"
        }
    )
    
    print("Original prompt length:", len(original_prompt))
    print("Original estimated tokens:", optimizer.estimate_tokens(original_prompt))
    print("\nOptimized prompt length:", len(optimized))
    print("Optimized estimated tokens:", optimizer.estimate_tokens(optimized))
    print(f"\nToken reduction: {(1 - optimizer.estimate_tokens(optimized) / optimizer.estimate_tokens(original_prompt)) * 100:.1f}%")
    
    print("\n--- Optimized Prompt ---")
    print(optimized)


async def demonstrate_error_handling():
    """Demonstrate enhanced error handling with graceful degradation."""
    print("\n=== Enhanced Error Handling Demo ===\n")
    
    # Create error handler with adaptive strategy
    error_handler = AIErrorHandler(
        retry_strategy=AdaptiveRetryStrategy(max_attempts=5)
    )
    
    # Simulate various error scenarios
    async def simulate_api_call(scenario: str):
        """Simulate API call with different error scenarios."""
        if scenario == "rate_limit":
            raise Exception("Rate limit exceeded")
        elif scenario == "timeout":
            raise asyncio.TimeoutError("Request timeout")
        elif scenario == "success_after_retry":
            # Succeed on 3rd attempt
            if not hasattr(simulate_api_call, 'attempts'):
                simulate_api_call.attempts = 0
            simulate_api_call.attempts += 1
            if simulate_api_call.attempts < 3:
                raise Exception("Temporary API error")
            return {"result": "success"}
        return {"result": "immediate_success"}
    
    # Test different scenarios
    scenarios = ["success_after_retry", "rate_limit", "timeout"]
    
    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario}")
        simulate_api_call.attempts = 0  # Reset attempts
        
        try:
            start_time = time.time()
            result = await error_handler.handle_with_retry(
                simulate_api_call,
                scenario,
                provider="demo_provider",
                model="demo_model"
            )
            elapsed = time.time() - start_time
            print(f"✓ Success after {elapsed:.2f}s: {result}")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"✗ Failed after {elapsed:.2f}s: {e}")
    
    # Show error statistics
    stats = error_handler.get_error_statistics()
    print("\n--- Error Statistics ---")
    print(json.dumps(stats, indent=2))


async def demonstrate_caching():
    """Demonstrate response caching for similar patterns."""
    print("\n=== Response Caching Demo ===\n")
    
    # Create config with caching enabled
    config = ConfigBuilder() \
        .framework("playwright") \
        .use_ai(True) \
        .build()
    
    session = EnhancedAsyncSession(config)
    await session.start("https://example.com")
    
    # Add similar steps that should benefit from caching
    similar_steps = [
        {
            "model_output": {
                "action": [{"click_element": {"selector": ".btn-primary"}}]
            },
            "state": {"interacted_element": [{"selector": ".btn-primary", "tag": "button"}]}
        },
        {
            "model_output": {
                "action": [{"click_element": {"selector": ".btn-primary"}}]  # Same action
            },
            "state": {"interacted_element": [{"selector": ".btn-primary", "tag": "button"}]}
        },
        {
            "model_output": {
                "action": [{"click_element": {"selector": ".btn-secondary"}}]  # Different
            },
            "state": {"interacted_element": [{"selector": ".btn-secondary", "tag": "button"}]}
        }
    ]
    
    print("Processing similar steps...")
    
    for i, step in enumerate(similar_steps):
        start_time = time.time()
        result = await session.add_step_async(step, wait_for_completion=True)
        elapsed = time.time() - start_time
        
        print(f"Step {i+1} processed in {elapsed:.3f}s")
        
        # Check if it was cached
        if i == 1:  # Second step should be cached
            print("  → Should have been served from cache (faster)")
    
    # Show cache statistics
    cache_stats = session.batch_processor.get_statistics()
    print("\n--- Cache Statistics ---")
    print(f"Cache hits: {cache_stats['cache_hits']}")
    print(f"Cache size: {cache_stats['cache_size']}")
    print(f"API calls saved: {cache_stats['api_calls_saved']}")


async def main():
    """Run all demonstrations."""
    print("Browse-to-Test AI Orchestration Optimizations Demo")
    print("=" * 50)
    
    # Run demonstrations
    try:
        # 1. Batching demo
        session = await demonstrate_batching()
        
        # 2. Prompt optimization demo
        demonstrate_prompt_optimization()
        
        # 3. Error handling demo
        await demonstrate_error_handling()
        
        # 4. Caching demo
        await demonstrate_caching()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())