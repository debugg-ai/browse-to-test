#!/usr/bin/env python3
"""
Async Usage Example for Browse-to-Test

This example demonstrates how to use the async API for better performance,
especially when generating multiple test scripts or working with complex
automation data that requires AI analysis.

Key features demonstrated:
- convert_async() function for non-blocking operations
- Parallel processing of multiple conversions
- Error handling and timeout management
- Performance comparison with sync version

Requirements:
- Set OPENAI_API_KEY environment variable
- Python 3.7+ for async/await support
"""

import asyncio
import time
import os
from pathlib import Path
import browse_to_test as btt

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_sample_automation_data():
    """Create sample browser automation data."""
    return [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://app.example.com"}}]
            },
            "state": {
                "url": "https://app.example.com",
                "title": "Example App - Dashboard",
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "step_end_time": 1640995202.0,
                "step_number": 1
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://app.example.com/users",
                "title": "User Management",
                "interacted_element": [{
                    "xpath": "//button[contains(@class, 'create-user-btn')]",
                    "css_selector": ".create-user-btn",
                    "highlight_index": 0,
                    "attributes": {
                        "class": "btn btn-primary create-user-btn",
                        "type": "button"
                    },
                    "text_content": "Create New User"
                }]
            },
            "metadata": {
                "step_start_time": 1640995202.0,
                "step_end_time": 1640995204.0,
                "step_number": 2
            }
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "John Doe"}}]
            },
            "state": {
                "url": "https://app.example.com/users/new",
                "title": "Create User",
                "interacted_element": [{
                    "xpath": "//input[@name='fullName']",
                    "css_selector": "input[name='fullName']",
                    "highlight_index": 0,
                    "attributes": {
                        "name": "fullName",
                        "type": "text",
                        "placeholder": "Enter full name",
                        "required": "true"
                    }
                }]
            },
            "metadata": {
                "step_start_time": 1640995204.0,
                "step_end_time": 1640995206.0,
                "step_number": 3
            }
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "john.doe@company.com"}}]
            },
            "state": {
                "url": "https://app.example.com/users/new",
                "title": "Create User",
                "interacted_element": [{
                    "xpath": "//input[@name='email']",
                    "css_selector": "input[name='email']",
                    "highlight_index": 0,
                    "attributes": {
                        "name": "email",
                        "type": "email",
                        "placeholder": "Enter email address",
                        "required": "true"
                    }
                }]
            },
            "metadata": {
                "step_start_time": 1640995206.0,
                "step_end_time": 1640995208.0,
                "step_number": 4
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://app.example.com/users",
                "title": "User Management",
                "interacted_element": [{
                    "xpath": "//button[@type='submit']",
                    "css_selector": "button[type='submit']",
                    "highlight_index": 0,
                    "attributes": {
                        "type": "submit",
                        "class": "btn btn-success",
                        "form": "create-user-form"
                    },
                    "text_content": "Create User"
                }]
            },
            "metadata": {
                "step_start_time": 1640995208.0,
                "step_end_time": 1640995210.0,
                "step_number": 5
            }
        }
    ]


async def example_1_simple_async():
    """Example 1: Basic async conversion."""
    print("=== Example 1: Simple Async Conversion ===")
    
    automation_data = create_sample_automation_data()
    
    try:
        start_time = time.time()
        
        # Use convert_async for non-blocking operation
        script = await btt.convert_async(
            automation_data=automation_data,
            framework="playwright",
            ai_provider="openai",
            language="python"
        )
        
        execution_time = time.time() - start_time
        
        # Save the script
        output_file = OUTPUT_DIR / "async_playwright_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated async test: {output_file}")
        print(f"  Execution time: {execution_time:.2f} seconds")
        print(f"  Script length: {len(script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Error: {e}")


async def example_2_parallel_conversions():
    """Example 2: Generate multiple tests in parallel."""
    print("\n=== Example 2: Parallel Conversions ===")
    
    automation_data = create_sample_automation_data()
    
    # Define multiple conversion tasks
    conversion_tasks = [
        {
            "name": "playwright_python",
            "framework": "playwright",
            "language": "python"
        },
        {
            "name": "playwright_typescript", 
            "framework": "playwright",
            "language": "typescript"
        },
        {
            "name": "selenium_python",
            "framework": "selenium", 
            "language": "python"
        }
    ]
    
    try:
        start_time = time.time()
        
        # Create async tasks for parallel execution
        tasks = []
        for config in conversion_tasks:
            task = btt.convert_async(
                automation_data=automation_data,
                framework=config["framework"],
                ai_provider="openai",
                language=config["language"],
                include_assertions=True,
                include_error_handling=True
            )
            tasks.append((config["name"], task))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        # Process results
        successful_conversions = 0
        for i, ((name, _), result) in enumerate(zip(tasks, results)):
            if isinstance(result, Exception):
                print(f"✗ {name}: {result}")
            else:
                config = conversion_tasks[i]
                extension = ".ts" if config["language"] == "typescript" else ".py"
                output_file = OUTPUT_DIR / f"parallel_{name}{extension}"
                
                with open(output_file, 'w') as f:
                    f.write(result)
                
                print(f"✓ {name}: {output_file}")
                successful_conversions += 1
        
        print(f"\n📊 Parallel execution completed:")
        print(f"  Total time: {execution_time:.2f} seconds")
        print(f"  Successful: {successful_conversions}/{len(conversion_tasks)}")
        print(f"  Average time per conversion: {execution_time/len(conversion_tasks):.2f} seconds")
        
    except Exception as e:
        print(f"✗ Parallel conversion failed: {e}")


async def example_3_with_timeout_and_retry():
    """Example 3: Robust async conversion with timeout and error handling."""
    print("\n=== Example 3: With Timeout and Error Handling ===")
    
    automation_data = create_sample_automation_data()
    
    async def robust_convert(name, **kwargs):
        """Convert with timeout and retry logic."""
        max_retries = 2
        timeout_seconds = 30
        
        for attempt in range(max_retries + 1):
            try:
                print(f"  {name}: Attempt {attempt + 1}")
                
                # Convert with timeout
                script = await asyncio.wait_for(
                    btt.convert_async(automation_data=automation_data, **kwargs),
                    timeout=timeout_seconds
                )
                
                return script
                
            except asyncio.TimeoutError:
                print(f"  {name}: Timeout after {timeout_seconds}s (attempt {attempt + 1})")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(1)  # Brief delay before retry
                
            except Exception as e:
                print(f"  {name}: Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(1)
    
    conversions = [
        ("robust_playwright", {
            "framework": "playwright",
            "ai_provider": "openai",
            "language": "python",
            "include_assertions": True,
            "include_error_handling": True,
            "include_logging": True
        }),
        ("robust_selenium", {
            "framework": "selenium",
            "ai_provider": "openai", 
            "language": "python",
            "include_assertions": True,
            "include_error_handling": True
        })
    ]
    
    try:
        start_time = time.time()
        
        # Execute robust conversions
        for name, config in conversions:
            try:
                script = await robust_convert(name, **config)
                
                output_file = OUTPUT_DIR / f"{name}_test.py"
                with open(output_file, 'w') as f:
                    f.write(script)
                
                print(f"✓ {name}: {output_file}")
                
            except Exception as e:
                print(f"✗ {name}: Final error: {e}")
        
        execution_time = time.time() - start_time
        print(f"\n📊 Robust conversion completed in {execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"✗ Robust conversion failed: {e}")


async def example_4_performance_comparison():
    """Example 4: Compare sync vs async performance."""
    print("\n=== Example 4: Performance Comparison ===")
    
    automation_data = create_sample_automation_data()
    
    # Test configuration
    config = {
        "framework": "playwright",
        "ai_provider": "openai",
        "language": "python",
        "include_assertions": True
    }
    
    print("Running performance comparison...")
    
    try:
        # Sync version
        print("  Testing synchronous conversion...")
        sync_start = time.time()
        sync_script = btt.convert(automation_data=automation_data, **config)
        sync_time = time.time() - sync_start
        
        # Async version  
        print("  Testing asynchronous conversion...")
        async_start = time.time()
        async_script = await btt.convert_async(automation_data=automation_data, **config)
        async_time = time.time() - async_start
        
        # Save both scripts
        with open(OUTPUT_DIR / "sync_performance_test.py", 'w') as f:
            f.write(sync_script)
        with open(OUTPUT_DIR / "async_performance_test.py", 'w') as f:
            f.write(async_script)
        
        # Results
        print(f"\n📊 Performance Results:")
        print(f"  Synchronous:  {sync_time:.2f} seconds")
        print(f"  Asynchronous: {async_time:.2f} seconds")
        
        if async_time < sync_time:
            improvement = ((sync_time - async_time) / sync_time) * 100
            print(f"  Async is {improvement:.1f}% faster")
        else:
            slowdown = ((async_time - sync_time) / sync_time) * 100
            print(f"  Async is {slowdown:.1f}% slower (overhead for single conversion)")
        
        print(f"  Scripts identical: {sync_script == async_script}")
        
    except Exception as e:
        print(f"✗ Performance comparison failed: {e}")


async def example_5_quality_analysis():
    """Example 5: Async script quality analysis."""
    print("\n=== Example 5: Script Quality Analysis ===")
    
    automation_data = create_sample_automation_data()
    
    try:
        # Generate a script
        print("  Generating test script...")
        script = await btt.convert_async(
            automation_data=automation_data,
            framework="playwright",
            ai_provider="openai",
            language="python"
        )
        
        # Perform quality analysis
        print("  Analyzing script quality...")
        qa_result = await btt.perform_script_qa_async(
            script=script,
            automation_data=automation_data,
            framework="playwright",
            ai_provider="openai"
        )
        
        # Show results
        print(f"\n📊 Quality Analysis Results:")
        print(f"  Quality Score: {qa_result['quality_score']}/100")
        print(f"  Original Script: {qa_result['analysis_metadata']['original_script_lines']} lines")
        print(f"  Optimized Script: {qa_result['analysis_metadata']['analyzed_script_lines']} lines")
        
        if qa_result['improvements']:
            print(f"  Suggested Improvements:")
            for improvement in qa_result['improvements']:
                print(f"    • {improvement}")
        
        # Save both versions
        with open(OUTPUT_DIR / "original_quality_test.py", 'w') as f:
            f.write(script)
        with open(OUTPUT_DIR / "optimized_quality_test.py", 'w') as f:
            f.write(qa_result['optimized_script'])
        
        print(f"  Saved original and optimized versions to output/")
        
    except Exception as e:
        print(f"✗ Quality analysis failed: {e}")


async def main():
    """Run all async examples."""
    print("Browse-to-Test Async Usage Examples")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Warning: OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Examples will fail without it.\n")
        return
    
    try:
        # Run examples sequentially for better output readability
        await example_1_simple_async()
        await example_2_parallel_conversions()
        await example_3_with_timeout_and_retry()
        await example_4_performance_comparison()
        await example_5_quality_analysis()
        
        # Show generated files
        print(f"\n📁 Generated files in {OUTPUT_DIR.relative_to(Path.cwd())}:")
        output_files = list(OUTPUT_DIR.glob("*.py")) + list(OUTPUT_DIR.glob("*.ts"))
        for file_path in sorted(output_files):
            if file_path.name.startswith(('async_', 'parallel_', 'robust_', 'sync_', 'original_', 'optimized_')):
                size = file_path.stat().st_size
                print(f"   • {file_path.name} ({size:,} bytes)")
        
        print("\n✓ All async examples completed successfully!")
        print("\nKey benefits of async API:")
        print("- Non-blocking operations for better responsiveness")
        print("- Parallel processing of multiple conversions")
        print("- Better resource utilization with concurrent AI calls")
        print("- Timeout and retry capabilities")
        
    except Exception as e:
        print(f"\n✗ Async examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())